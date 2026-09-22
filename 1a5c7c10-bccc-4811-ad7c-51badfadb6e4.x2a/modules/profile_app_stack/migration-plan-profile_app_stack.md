---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack module that sets up a complete deployment pipeline including Python runtime, PostgreSQL database (conditionally local), application deployment from Git, systemd service configuration, and monitoring. The module orchestrates 6 classes in strict dependency order with encrypted credentials and environment-specific overrides.

## Service Type and Instances

**Service Type**: Python Web Application Stack

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: Gunicorn WSGI server with 4 workers, sync worker class, 1000 max requests

## File Structure

**Manifests**:
- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/python.pp`
- `site-modules/profile_app_stack/manifests/database.pp`
- `site-modules/profile_app_stack/manifests/app.pp`
- `site-modules/profile_app_stack/manifests/service.pp`
- `site-modules/profile_app_stack/manifests/monitoring.pp`
- `site-modules/profile_postgresql/manifests/init.pp`
- `site-modules/profile_postgresql/manifests/repo.pp`
- `site-modules/profile_postgresql/manifests/install.pp`
- `site-modules/profile_postgresql/manifests/service.pp`
- `site-modules/role/manifests/app_server.pp`
- `site-modules/profile/manifests/app/stack.pp`

**Templates**:
- `site-modules/profile_app_stack/templates/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/app.env.erb`
- `site-modules/profile_app_stack/templates/app.service.epp`

**Data Files**:
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `site-modules/profile_postgresql/data/common.yaml`
- `site-modules/profile_postgresql/data/os/Debian.yaml`

**Dependencies**:
- `migration-dependencies/apt/manifests/init.pp`
- `migration-dependencies/apt/manifests/update.pp`
- `migration-dependencies/apt/manifests/setting.pp`
- `migration-dependencies/apt/manifests/source.pp`
- `migration-dependencies/apt/manifests/keyring.pp`

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point role class that includes profile::app::stack
   - Sets up complete application server configuration

2. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Wrapper profile that includes profile_app_stack
   - Provides abstraction layer for application stack components

3. **profile_app_stack** (`manifests/init.pp`):
   - Sets class parameters from Hiera lookups: app_name=myapp, app_repo=https://github.com/company/myapp.git, app_revision=main, app_port=8000, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, db_host=localhost, db_port=5432, db_name=myapp_db, db_user=myapp_user, db_password=[ENCRYPTED], worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info, secret_key=[ENCRYPTED]
   - Builds database URL: `postgresql://myapp_user:[ENCRYPTED]@localhost:5432/myapp_db`
   - `contain profile_app_stack::python`
   - `contain profile_app_stack::database`
   - `contain profile_app_stack::app`
   - `contain profile_app_stack::service`
   - `contain profile_app_stack::monitoring`
   - Sets ordering: `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`

4. **profile_app_stack::python** (`manifests/python.pp`):
   - Iterations: `$python_packages.each` — runs 4 times for: **python3.11**, **python3.11-venv**, **python3.11-dev**, **build-essential**
     - `package 'python3.11'` → ensure: `present`
     - `package 'python3.11-venv'` → ensure: `present`
     - `package 'python3.11-dev'` → ensure: `present`
     - `package 'build-essential'` → ensure: `present`
   - `group 'myapp'` → ensure: `present`, gid: `1001`
   - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp`, shell: `/bin/bash`, managehome: `true`
   - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp'` (template `logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_dir=/var/log/myapp, log_rotate_count=7, log_max_size=100M, app_name=myapp

5. **profile_app_stack::database** (`manifests/database.pp`):
   - Conditional: if `localhost` == 'localhost' (TRUE)
     - **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
       - `contain profile_postgresql::repo`
       - `contain profile_postgresql::install`
       - `contain profile_postgresql::service`
       - Sets ordering: `profile_postgresql::repo -> profile_postgresql::install -> profile_postgresql::service`
     - **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
       - **apt** (`migration-dependencies/apt/manifests/init.pp`):
         - `fail 'This module only works on Debian or derivatives like Ubuntu'` if not Debian family
         - **apt::update** (`migration-dependencies/apt/manifests/update.pp`):
           - `exec 'apt_update'` → command: `/usr/bin/apt-get update`, refreshonly: `true`
         - **apt::setting** `conf-proxy` → content: proxy configuration, notify_update: `true`
         - **apt::setting** `conf-update-stamp` → content: update stamp configuration
         - `file 'sources.list'` → path: `/etc/apt/sources.list`, purge: `false`
         - `file 'sources.list.d'` → path: `/etc/apt/sources.list.d`, purge: `false`
         - `file 'preferences'` → path: `/etc/apt/preferences`, purge: `false`
         - `file 'preferences.d'` → path: `/etc/apt/preferences.d`, purge: `false`
         - `file 'apt.conf.d'` → path: `/etc/apt/apt.conf.d`, purge: `false`
         - Iterations: `$keyrings.each` — Loop runs 0 times (no keyrings configured)
         - `package 'gnupg'` → ensure: `present` (for Debian/Ubuntu)
       - **apt::source** `pgdg` → location: `https://apt.postgresql.org/pub/repos/apt`, release: `jammy-pgdg`, repos: `main`, key: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8`, keyserver: `keyserver.ubuntu.com`
         - **apt::setting** `list-pgdg` → content: PostgreSQL repository configuration, notify_update: `true`
     - **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
       - Iterations: `$package_names.each` — runs 3 times for: **postgresql-15**, **postgresql-client-15**, **postgresql-contrib-15**
         - `package 'postgresql-15'` → ensure: `present`
         - `package 'postgresql-client-15'` → ensure: `present`
         - `package 'postgresql-contrib-15'` → ensure: `present`
       - `package 'libpq-dev'` → ensure: `present`
     - **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
       - `service 'postgresql'` → ensure: `running`, enable: `true`
     - `exec 'create_db_user'` → command: `sudo -u postgres createuser -d -r -s myapp_user`, unless: `sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp_user'" | grep -q 1`
     - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp_user myapp_db`, unless: `sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw myapp_db`
     - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp_user;"`, refreshonly: `true`
   - `file '/usr/local/bin/db-backup.sh'` → owner: `root`, group: `root`, mode: `0755`, content: database backup script
   - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `0`

6. **profile_app_stack::app** (`manifests/app.pp`):
   - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp'` → ensure: `present`, provider: `git`, source: `https://github.com/company/myapp.git`, revision: `main`, user: `myapp`
   - `exec 'create_app_venv'` → command: `python3.11 -m venv /opt/myapp/venv`, user: `myapp`, creates: `/opt/myapp/venv/bin/activate`
   - `exec 'install_requirements'` → command: `/opt/myapp/venv/bin/pip install -r /opt/myapp/requirements.txt`, user: `myapp`, refreshonly: `true`
   - Conditional: if `!empty($pip_packages)` (pip_packages=['gunicorn', 'psycopg2-binary'] - TRUE)
     - Iterations: `$pip_packages.each` — runs 2 times for: **gunicorn**, **psycopg2-binary**
       - `exec 'install_gunicorn'` → command: `/opt/myapp/venv/bin/pip install gunicorn`, user: `myapp`
       - `exec 'install_psycopg2-binary'` → command: `/opt/myapp/venv/bin/pip install psycopg2-binary`, user: `myapp`
   - `file '/opt/myapp/.env'` (template `app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
     - Passes: db_url=postgresql://myapp_user:[ENCRYPTED]@localhost:5432/myapp_db, app_name=myapp, app_port=8000, secret_key=[ENCRYPTED], log_level=info, log_dir=/var/log/myapp, worker_count=4, facts['environment']=production
   - `file '/usr/local/bin/app-healthcheck.sh'` → owner: `root`, group: `root`, mode: `0755`, content: health check script
   - `exec 'run_db_migrations'` → command: `/opt/myapp/venv/bin/python /opt/myapp/manage.py migrate`, user: `myapp`, refreshonly: `true`

7. **profile_app_stack::service** (`manifests/service.pp`):
   - `file '/etc/systemd/system/myapp.service'` (template `app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: app_name=myapp, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, app_port=8000, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info
   - `exec 'systemd_daemon_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - `service 'myapp'` → ensure: `running`, enable: `true`
   - notifies: `file[myapp.service] ~> exec[systemd_daemon_reload] ~> service[myapp]`

8. **profile_app_stack::monitoring** (`manifests/monitoring.pp`):
   - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual)
   - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual)
   - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual)
   - `@cron 'push_app_metrics'` → command: `/usr/local/bin/push-metrics.sh`, user: `myapp`, minute: `*/5` (virtual)
   - Conditional: if `production` == 'production' (TRUE in production)
     - `<<| Package |>>` → realizes all virtual Package resources
     - `<<| Service |>>` → realizes all virtual Service resources
     - `<<| Cron |>>` → realizes all virtual Cron resources
   - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `root`, minute: `*/2`

## Variables

**Variable Flow Summary**: 35 variables across 5 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_app_stack::app_name`: `myapp` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/company/myapp.git` (type: string)
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::python_version`: `3.11` (type: string)
- `profile_app_stack::pip_packages`: `['gunicorn', 'psycopg2-binary']` (type: array)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_db` (type: string)
- `profile_app_stack::db_user`: `myapp_user` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `500` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `test-secret-key` (type: string)
- `profile_app_stack::db_password`: `[ENCRYPTED]` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)
- `profile_postgresql::version`: `15` (type: string)

**environment/production.yaml (production overrides)** → Migration note: Production-specific variables, loaded for production environment
- `profile_app_stack::app_revision`: `v1.2.3` (type: string)
- `profile_app_stack::db_host`: `db.prod.internal` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `2000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::secret_key`: `[ENCRYPTED]` (type: string)

**environment/staging.yaml (staging overrides)** → Migration note: Staging-specific variables, loaded for staging environment
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::secret_key`: `[ENCRYPTED]` (type: string)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_postgresql::package_names`: `['postgresql-15', 'postgresql-client-15', 'postgresql-contrib-15']` (type: array)
- `profile_postgresql::service_name`: `postgresql` (type: string)
- `profile_postgresql::repo_location`: `https://apt.postgresql.org/pub/repos/apt` (type: string)
- `profile_postgresql::repo_release`: `jammy-pgdg` (type: string)
- `profile_postgresql::repo_key_id`: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8` (type: string)
- `profile_postgresql::repo_key_source`: `https://www.postgresql.org/media/keys/ACCC4CF8.asc` (type: string)

### Variable Migration Summary

- **Common defaults**: 24 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 10 variables that vary by deployment environment (production: 6, staging: 4)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 4 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_revision**: defined at common/environment, merge strategy: first
- **profile_app_stack::worker_count**: defined at common/environment, merge strategy: first
- **profile_app_stack::max_requests**: defined at common/environment, merge strategy: first
- **profile_app_stack::log_level**: defined at common/environment, merge strategy: first
- **profile_app_stack::secret_key**: defined at common/environment, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- No hash or deep merge strategies detected in this module

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (9.7.0)
- puppetlabs-vcsrepo (6.1.0)
- puppetlabs-apt (9.4.0)

**System package dependencies**:
- python3.11, python3.11-venv, python3.11-dev, build-essential
- postgresql-15, postgresql-client-15, postgresql-contrib-15, libpq-dev
- gnupg (for APT key management)
- prometheus-node-exporter, prometheus-pushgateway (monitoring)

**Service dependencies**:
- PostgreSQL service must be running before application service
- APT update must complete before PostgreSQL installation
- Python environment must be ready before application deployment

## Puppet Facts Used

- `$facts['os']['family']`: Operating system family (Debian validation)
- `$facts['os']['name']`: Operating system name (Ubuntu/Debian package selection)
- `$facts['environment']`: Environment name (production/staging configuration)
- `$facts['apt_update_last_success']`: APT update timestamp (update frequency control)

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution for log rotation configuration with log_dir, log_rotate_count, log_max_size, and app_name variables

**app.env.erb**: Contains conditional logic for environment-specific DEBUG and CORS settings based on `$facts['environment']`. Production sets DEBUG=false, staging sets DEBUG=true. Uses variables: db_url, app_name, app_port, secret_key, log_level, log_dir, worker_count

**app.service.epp**: Complex systemd service template with security hardening using EPP syntax. Includes typed parameters for systemd service configuration with variables: app_name, app_dir, app_user, app_group, app_port, worker_count, worker_class, max_requests, graceful_timeout, log_dir, log_level

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries.

**Virtual Resources**: Virtual resources are created with `@` prefix and realized with collectors
- **Exported Resources**: None detected
- **Resource Collectors**: 
  - `<<| Package |>>`: Collects all virtual Package resources, migration notes: realizes monitoring packages only in production environment
  - `<<| Service |>>`: Collects all virtual Service resources, migration notes: realizes monitoring services only in production environment  
  - `<<| Cron |>>`: Collects all virtual Cron resources, migration notes: realizes monitoring cron jobs only in production environment
- **PuppetDB Queries**: None detected
- **Host Identity Data**: Environment-based conditional realization using `$facts['environment']` for production monitoring setup

## Checks for the Migration

**Files to verify**:
- `/etc/logrotate.d/myapp`
- `/opt/myapp/.env`
- `/etc/systemd/system/myapp.service`
- `/usr/local/bin/db-backup.sh`
- `/usr/local/bin/app-healthcheck.sh`
- `/etc/apt/sources.list.d/pgdg.list`
- `/opt/myapp/venv/bin/activate`
- `/var/log/myapp/`

**Service endpoints to check**:
- Application: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Health check endpoint: `http://localhost:8000/health`

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
sudo -u postgres psql -c "\l"
sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='myapp_user'"

# Configuration validation commands
python3.11 --version
/opt/myapp/venv/bin/python --version
/opt/myapp/venv/bin/pip list | grep -E "(gunicorn|psycopg2-binary)"

# Network/connectivity checks
netstat -tlnp | grep :8000
netstat -tlnp | grep :5432
```