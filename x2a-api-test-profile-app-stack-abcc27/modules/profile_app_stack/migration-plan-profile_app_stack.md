---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack module that sets up a complete WSGI application environment with PostgreSQL database, systemd service management, log rotation, and monitoring. Manages the full lifecycle from Python environment setup through database provisioning, application deployment, service configuration, and health monitoring.

## Service Type and Instances

**Service Type**: Python Web Application Stack (WSGI/Gunicorn)

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: 4 workers, sync worker class, 1000 max requests, 30s graceful timeout

## File Structure

**Manifests**:
- `site-modules/role/manifests/app_stack.pp`
- `site-modules/profile/manifests/base/base.pp`
- `site-modules/profile/manifests/app/stack.pp`
- `site-modules/profile_postgresql/manifests/init.pp`
- `site-modules/profile_postgresql/manifests/repo.pp`
- `site-modules/profile_postgresql/manifests/install.pp`
- `site-modules/profile_postgresql/manifests/service.pp`
- `migration-dependencies/apt/manifests/init.pp`
- `migration-dependencies/apt/manifests/source.pp`
- `migration-dependencies/apt/manifests/setting.pp`
- `migration-dependencies/apt/manifests/update.pp`
- `migration-dependencies/apt/manifests/keyring.pp`

**Templates**:
- `site-modules/profile/templates/app/logrotate.conf.erb`
- `site-modules/profile/templates/app/app.env.erb`
- `site-modules/profile/templates/app/app.service.epp`

**Data Files**:
- `site-modules/profile/data/common.yaml`
- `site-modules/profile/data/environment/production.yaml`
- `site-modules/profile/data/environment/staging.yaml`
- `site-modules/profile/data/os/Debian.yaml`

## Module Explanation

The module performs operations in this order:

1. **role::app_stack** (`site-modules/role/manifests/app_stack.pp`):
   - Entry point role class that includes profile classes
   - `contain profile::base::base`
   - `contain profile::app::stack`
   - Sets ordering: `profile::base::base -> profile::app::stack`

2. **profile::base::base** (`site-modules/profile/manifests/base/base.pp`):
   - Base system configuration and package management
   - `contain apt`
   - Manages system-wide package repositories and updates

3. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Sets class parameters from Hiera lookups: app_name=myapp, app_port=8000, worker_count=4, app_user=myapp, app_group=myapp, app_dir=/opt/myapp, db_host=localhost, db_port=5432, db_name=myapp_dev, db_user=myapp_user, log_dir=/var/log/myapp, log_level=info, worker_class=sync, max_requests=1000, graceful_timeout=30
   - Builds database URL using custom function: `postgresql://myapp_user:encrypted_password@localhost:5432/myapp_dev`
   - **Python Environment Setup**:
     - `package 'python3'` → ensure: `present`
     - `package 'python3-pip'` → ensure: `present`
     - `package 'python3-venv'` → ensure: `present`
     - `package 'python3-dev'` → ensure: `present`
     - `package 'build-essential'` → ensure: `present`
     - `group 'myapp'` → ensure: `present`, gid: `1001`
     - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp`, shell: `/bin/bash`, managehome: `true`
     - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
     - `file '/etc/logrotate.d/myapp'` (template `logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`
   - **Database Setup**:
     - `contain profile_postgresql`
     - `exec 'create_db_user'` → command: `sudo -u postgres createuser -d -r -s myapp_user`, unless: `sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp_user'" | grep -q 1`
     - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp_user myapp_dev`, unless: `sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw myapp_dev`
     - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_dev TO myapp_user;"`
     - `file '/usr/local/bin/db-backup.sh'` → owner: `root`, group: `root`, mode: `0755`
     - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `0`
   - **Application Deployment**:
     - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
     - `vcsrepo '/opt/myapp'` → ensure: `present`, provider: `git`, source: `https://github.com/example/myapp.git`, revision: `main`, user: `myapp`
     - `exec 'create_app_venv'` → command: `python3 -m venv /opt/myapp/venv`, user: `myapp`, creates: `/opt/myapp/venv/bin/activate`
     - `exec 'install_requirements'` → command: `/opt/myapp/venv/bin/pip install -r /opt/myapp/requirements.txt`, user: `myapp`, refreshonly: `true`
     - `file '/opt/myapp/.env'` (template `app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
     - `file '/usr/local/bin/app-healthcheck.sh'` → owner: `root`, group: `root`, mode: `0755`
     - `exec 'run_db_migrations'` → command: `/opt/myapp/venv/bin/python /opt/myapp/manage.py migrate`, user: `myapp`, refreshonly: `true`
   - **Service Configuration**:
     - `file '/etc/systemd/system/myapp.service'` (template `app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
     - `exec 'systemd_daemon_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
     - `service 'myapp'` → ensure: `running`, enable: `true`
   - **Monitoring Setup**:
     - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual)
     - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual)
     - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual)
     - `@cron 'push_app_metrics'` → command: `/usr/local/bin/push-metrics.sh`, user: `myapp`, minute: `*/5` (virtual)
     - `<<| package { tag == 'monitoring' } |>>` (collector for monitoring packages)
     - `<<| service { tag == 'monitoring' } |>>` (collector for monitoring services)
     - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `root`, minute: `*/2`

4. **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
   - `contain profile_postgresql::repo`
   - `contain profile_postgresql::install`
   - `contain profile_postgresql::service`
   - Sets ordering: `profile_postgresql::repo -> profile_postgresql::install -> profile_postgresql::service`

5. **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
   - `contain apt`
   - `apt::source 'pgdg'` → location: `http://apt.postgresql.org/pub/repos/apt`, release: `jammy-pgdg`, repos: `main`, key: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8`

6. **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
   - `package 'postgresql-15'` → ensure: `present`
   - `package 'postgresql-client-15'` → ensure: `present`
   - `package 'postgresql-contrib-15'` → ensure: `present`
   - `package 'libpq-dev'` → ensure: `present`

7. **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
   - `service 'postgresql'` → ensure: `running`, enable: `true`

8. **apt** (`migration-dependencies/apt/manifests/init.pp`):
   - Validates OS family is Debian using case statement
   - `contain apt::update`
   - `file '/etc/apt/sources.list'` → owner: `root`, group: `root`, mode: `0644`
   - `file '/etc/apt/sources.list.d'` → ensure: `directory`, purge: `true`
   - `file '/etc/apt/preferences'` → owner: `root`, group: `root`, mode: `0644`
   - `file '/etc/apt/preferences.d'` → ensure: `directory`, purge: `true`
   - `file '/etc/apt/apt.conf.d'` → ensure: `directory`, purge: `true`
   - `stdlib::ensure_packages 'gnupg'` → ensure: `present`
   - Iterations: Loop through keyrings hash creating apt::keyring resources for each key-value pair

9. **apt::update** (`migration-dependencies/apt/manifests/update.pp`):
   - `exec 'apt_update'` → command: `/usr/bin/apt-get update`, refreshonly: `true`
   - Conditional logic based on `$facts['apt_update_last_success']` for update frequency

10. **apt::keyring** (`migration-dependencies/apt/manifests/keyring.pp`):
    - Manages GPG keyrings for apt repositories
    - `file` resources for keyring management
    - `exec` resources for key import operations

## Variables

**Variable Flow Summary**: 25 variables across 4 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile::app::stack::app_name`: `myapp` (type: string)
- `profile::app::stack::app_port`: `8000` (type: integer)
- `profile::app::stack::worker_count`: `4` (type: integer)
- `profile::app::stack::app_user`: `myapp` (type: string)
- `profile::app::stack::app_group`: `myapp` (type: string)
- `profile::app::stack::app_dir`: `/opt/myapp` (type: string)
- `profile::app::stack::log_dir`: `/var/log/myapp` (type: string)
- `profile::app::stack::log_level`: `info` (type: string)
- `profile::app::stack::worker_class`: `sync` (type: string)
- `profile::app::stack::graceful_timeout`: `30` (type: integer)
- `profile::app::stack::max_requests`: `1000` (type: integer)
- `profile::app::stack::app_repo`: `https://github.com/example/myapp.git` (type: string)
- `profile::app::stack::app_revision`: `main` (type: string)
- `profile::app::stack::db_host`: `localhost` (type: string)
- `profile::app::stack::db_port`: `5432` (type: integer)
- `profile::app::stack::db_name`: `myapp_dev` (type: string)
- `profile::app::stack::db_user`: `myapp_user` (type: string)
- `profile::app::stack::pip_packages`: `[]` (type: array)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_postgresql::package_names`: `['postgresql-15', 'postgresql-client-15', 'postgresql-contrib-15']` (type: array)
- `profile_postgresql::service_name`: `postgresql` (type: string)
- `profile_postgresql::repo_location`: `http://apt.postgresql.org/pub/repos/apt` (type: string)
- `profile_postgresql::repo_release`: `jammy-pgdg` (type: string)
- `profile_postgresql::repo_key_source`: `https://www.postgresql.org/media/keys/ACCC4CF8.asc` (type: string)
- `profile_postgresql::repo_key_id`: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8` (type: string)

**environment/production.yaml (environment-specific)** → Migration note: Production environment overrides
- `profile::app::stack::log_level`: `warning` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Staging environment overrides
- `profile::app::stack::log_level`: `debug` (type: string)

### Variable Migration Summary

- **Common defaults**: 18 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 2 variables that vary by deployment environment (staging, prod)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple levels:
- **profile::app::stack::log_level**: defined at common, staging, and production levels, merge strategy: first
- **profile_postgresql::version**: defined at module and environment levels, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- No hash or deep merge strategies detected in this module

## Dependencies

**External module dependencies**:
- puppetlabs-vcsrepo (version: 6.1.0)
- puppetlabs-stdlib (version: 9.7.0)
- puppetlabs-apt (version: 9.4.0)

**System package dependencies**:
- python3, python3-pip, python3-venv, python3-dev, build-essential
- postgresql-15, postgresql-client-15, postgresql-contrib-15, libpq-dev
- gnupg (for apt key management)
- prometheus-node-exporter, prometheus-pushgateway (monitoring)

**Service dependencies**:
- PostgreSQL service must be running before application starts
- Systemd daemon-reload required after service file changes
- APT update must complete before package installations

## Puppet Facts Used

- `$facts['kernel']`: Operating system kernel type (Linux)
- `$facts['os']['family']`: OS family validation (Debian) - used in apt module case statements
- `$facts['os']['name']`: OS name (Ubuntu) - used for repository configuration
- `$facts['environment']`: Puppet environment (development/staging/production) - controls monitoring resource realization
- `$facts['apt_update_last_success']`: APT update timestamp for frequency control

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution for log directory, rotation count, max size, and app name. No complex logic blocks.

**app.env.erb**: Contains conditional logic block for environment-specific settings (DEBUG, ALLOWED_HOSTS, CORS_ORIGINS). Uses facts['environment'] to determine production vs development configuration. Ruby conditional blocks set different values based on environment.

**app.service.epp**: Complex systemd service template with 11 variables including calculated timeout values (graceful_timeout + 5). Uses EPP syntax with parameter validation and arithmetic operations for timeout calculations.

## Checks for the Migration

**Files to verify**:
- `/etc/logrotate.d/myapp`
- `/opt/myapp/.env`
- `/etc/systemd/system/myapp.service`
- `/usr/local/bin/db-backup.sh`
- `/usr/local/bin/app-healthcheck.sh`
- `/etc/apt/sources.list.d/pgdg.list`
- `/etc/apt/sources.list`
- `/etc/apt/preferences`

**Service endpoints to check**:
- Application: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

**Templates rendered**:
- `logrotate.conf.erb` → `/etc/logrotate.d/myapp` (1 time)
- `app.env.erb` → `/opt/myapp/.env` (1 time)
- `app.service.epp` → `/etc/systemd/system/myapp.service` (1 time)

## Pre-flight checks:
```bash
# Service status commands
systemctl status myapp
systemctl status postgresql
systemctl status prometheus-node-exporter

# Instance-specific checks
curl -f http://localhost:8000/health
/usr/local/bin/app-healthcheck.sh

# Configuration validation commands
sudo -u postgres psql -c "\l"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp_user'"
test -f /opt/myapp/venv/bin/activate
test -f /opt/myapp/.env

# Network/connectivity checks
nc -z localhost 8000
nc -z localhost 5432
```