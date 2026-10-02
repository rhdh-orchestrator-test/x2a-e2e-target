---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack module that deploys a complete application environment with PostgreSQL database, Python runtime, application code deployment via Git, systemd service management, and monitoring. Manages the full lifecycle from Python environment setup through database provisioning, application deployment, service configuration, and health monitoring.

## Service Type and Instances

**Service Type**: Python Web Application Stack

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: gunicorn WSGI server, 4 workers, sync worker class, 1000 max requests

## File Structure

```
site-modules/profile_app_stack/manifests/init.pp
site-modules/profile_app_stack/manifests/python.pp
site-modules/profile_app_stack/manifests/database.pp
site-modules/profile_app_stack/manifests/app.pp
site-modules/profile_app_stack/manifests/service.pp
site-modules/profile_app_stack/manifests/monitoring.pp
site-modules/profile_app_stack/templates/logrotate.conf.erb
site-modules/profile_app_stack/templates/app.env.erb
site-modules/profile_app_stack/templates/app.service.epp
site-modules/profile_app_stack/data/common.yaml
site-modules/profile_app_stack/data/environment/production.yaml
site-modules/profile_app_stack/data/environment/staging.yaml
site-modules/profile_postgresql/manifests/init.pp
site-modules/profile_postgresql/manifests/repo.pp
site-modules/profile_postgresql/manifests/install.pp
site-modules/profile_postgresql/manifests/service.pp
site-modules/role/manifests/app_server.pp
site-modules/profile/manifests/base/base.pp
site-modules/profile/manifests/app/stack.pp
migration-dependencies/apt/manifests/init.pp
migration-dependencies/apt/manifests/source.pp
migration-dependencies/apt/manifests/setting.pp
migration-dependencies/apt/manifests/update.pp
migration-dependencies/apt/manifests/keyring.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes base profile and application stack
   - `contain profile::base::base`
   - `contain profile::app::stack`
   - Sets ordering: `profile::base::base -> profile::app::stack`

2. **profile::base::base** (`site-modules/profile/manifests/base/base.pp`):
   - `package 'chrony'` → ensure: `present`
   - `service 'chrony'` → ensure: `running`, enable: `true`
   - `package 'rsyslog'` → ensure: `present`
   - `service 'rsyslog'` → ensure: `running`, enable: `true`

3. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Wrapper class that contains the main application stack
   - `contain profile_app_stack`

4. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera lookups: app_name=myapp, app_repo=https://github.com/company/myapp.git, app_revision=main, app_port=8000, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, db_host=localhost, db_port=5432, db_name=myapp_db, db_user=myapp_user, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info
   - Builds database URL: `postgresql://myapp_user:encrypted_password@localhost:5432/myapp_db`
   - `contain profile_app_stack::python`
   - `contain profile_app_stack::database`
   - `contain profile_app_stack::app`
   - `contain profile_app_stack::service`
   - `contain profile_app_stack::monitoring`
   - Sets ordering: `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`

5. **profile_app_stack::python** (`site-modules/profile_app_stack/manifests/python.pp`):
   - `package 'python3.11'` → ensure: `present`
   - `package 'python3.11-venv'` → ensure: `present`
   - `package 'python3.11-dev'` → ensure: `present`
   - `package 'build-essential'` → ensure: `present`
   - `package 'libpq-dev'` → ensure: `present`
   - `group 'myapp'` → ensure: `present`, gid: `1001`
   - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp`, shell: `/bin/bash`, managehome: `true`
   - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp'` (template `logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_dir=/var/log/myapp, log_rotate_count=7, log_max_size=100M, app_name=myapp

6. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - **Conditional**: if db_host == 'localhost' (true):
     - `contain profile_postgresql`
       - **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
         - `contain profile_postgresql::repo`
         - `contain profile_postgresql::install`
         - `contain profile_postgresql::service`
         - Sets ordering: `profile_postgresql::repo -> profile_postgresql::install -> profile_postgresql::service`
       - **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
         - `contain apt`
           - **apt** (`migration-dependencies/apt/manifests/init.pp`):
             - `fail 'This module only works on Debian or derivatives like Ubuntu'` if not Debian family
             - `contain apt::update`
               - **apt::update** (`migration-dependencies/apt/manifests/update.pp`):
                 - `exec 'apt_update'` → command: `/usr/bin/apt-get update`, refreshonly: `true`
             - `file '/etc/apt/sources.list'` → ensure: `file`, owner: `root`, group: `root`, mode: `0644`
             - `file '/etc/apt/sources.list.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
             - `file '/etc/apt/preferences'` → ensure: `file`, owner: `root`, group: `root`, mode: `0644`
             - `file '/etc/apt/preferences.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
             - `file '/etc/apt/apt.conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
             - `stdlib::ensure_packages 'gnupg'` → ensure: `present`
         - `apt::source 'pgdg'` → location: `https://apt.postgresql.org/pub/repos/apt`, release: `jammy-pgdg`, repos: `main`, key: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8`, keyserver: `keyserver.ubuntu.com`
       - **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
         - `package 'postgresql-16'` → ensure: `present`
         - `package 'postgresql-client-16'` → ensure: `present`
         - `package 'postgresql-contrib-16'` → ensure: `present`
         - `package 'libpq-dev'` → ensure: `present`
       - **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
         - `service 'postgresql'` → ensure: `running`, enable: `true`
     - `exec 'create_db_user'` → command: `sudo -u postgres createuser -d -r -s myapp_user`, unless: `sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp_user'" | grep -q 1`
     - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp_user myapp_db`, unless: `sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw myapp_db`
     - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp_user;"`
   - `file '/usr/local/bin/db-backup.sh'` → ensure: `file`, owner: `root`, group: `root`, mode: `0755`, content: database backup script
   - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `0`

7. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
   - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp'` → ensure: `present`, provider: `git`, source: `https://github.com/company/myapp.git`, revision: `main`, user: `myapp`
   - `exec 'create_app_venv'` → command: `/usr/bin/python3.11 -m venv /opt/myapp/venv`, user: `myapp`, creates: `/opt/myapp/venv/bin/python`
   - `exec 'install_requirements'` → command: `/opt/myapp/venv/bin/pip install -r /opt/myapp/requirements.txt`, user: `myapp`, cwd: `/opt/myapp`, refreshonly: `true`
   - **Conditional**: if pip_packages not empty (false) - no additional pip packages installed
   - `file '/opt/myapp/.env'` (template `app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
     - Passes: db_url=postgresql://myapp_user:encrypted_password@localhost:5432/myapp_db, app_name=myapp, app_port=8000, secret_key=encrypted_key, log_level=info, log_dir=/var/log/myapp, worker_count=4, facts['environment']=production
   - `file '/usr/local/bin/app-healthcheck.sh'` → ensure: `file`, owner: `root`, group: `root`, mode: `0755`, content: health check script
   - `exec 'run_db_migrations'` → command: `/opt/myapp/venv/bin/python manage.py migrate`, user: `myapp`, cwd: `/opt/myapp`, refreshonly: `true`

8. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
   - `file '/etc/systemd/system/myapp.service'` (template `app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: app_name=myapp, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, app_port=8000, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info
   - `exec 'systemd_daemon_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - `service 'myapp'` → ensure: `running`, enable: `true`
   - **notifies**: `file[myapp.service] ~> exec[systemd_daemon_reload] ~> service[myapp]`

9. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual)
   - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual)
   - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual)
   - `@cron 'push_app_metrics'` → command: `/usr/local/bin/push-metrics.sh`, user: `myapp`, minute: `*/5` (virtual)
   - **Conditional**: if facts['environment'] == 'production' (true):
     - Realizes all virtual resources: `<<| package |>>`, `<<| service |>>`, `<<| cron |>>`
   - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `root`, minute: `*/2`

## Variables

**Variable Flow Summary**: 22 variables across 5 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_app_stack::app_name`: `myapp` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/company/myapp.git` (type: string)
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_db` (type: string)
- `profile_app_stack::db_user`: `myapp_user` (type: string)
- `profile_app_stack::db_password`: `ENC[PKCS7,encrypted_password_data]` (type: string)
- `profile_app_stack::worker_count`: `4` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::python_version`: `3.11` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_postgresql::package_names`: `['postgresql-16', 'postgresql-client-16', 'postgresql-contrib-16']` (type: array)
- `profile_postgresql::service_name`: `postgresql` (type: string)
- `profile_postgresql::repo_location`: `https://apt.postgresql.org/pub/repos/apt` (type: string)
- `profile_postgresql::repo_release`: `jammy-pgdg` (type: string)
- `profile_postgresql::repo_key_id`: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8` (type: string)
- `profile_postgresql::repo_key_source`: `https://www.postgresql.org/media/keys/ACCC4CF8.asc` (type: string)

**environment/production.yaml (production overrides)** → Migration note: Production-specific overrides
- `profile_app_stack::app_revision`: `v1.2.3` (type: string)
- `profile_app_stack::db_host`: `prod-db.internal.example.com` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `2000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_secret_key_data]` (type: string)

**environment/staging.yaml (staging overrides)** → Migration note: Staging-specific overrides
- `profile_app_stack::app_revision`: `staging` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::max_requests`: `500` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::secret_key`: `staging_secret_key_456` (type: string)

### Variable Migration Summary

- **Common defaults**: 22 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 6 variables that vary by deployment environment (production, staging)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_revision**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::db_host**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::worker_count**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::max_requests**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::log_level**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::secret_key**: defined at production, staging, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (9.7.0)
- puppetlabs-vcsrepo (6.1.0)
- puppetlabs-apt (9.4.0)

**System package dependencies**:
- python3.11, python3.11-venv, python3.11-dev, build-essential, libpq-dev
- postgresql-16, postgresql-client-16, postgresql-contrib-16
- gnupg (for APT key management)
- chrony, rsyslog

**Service dependencies**:
- PostgreSQL service must be running before application service
- APT repository setup before PostgreSQL installation
- Python environment setup before application deployment
- Application deployment before service configuration
- Base services (chrony, rsyslog) before application stack

## Puppet Facts Used

- `$facts['kernel']`: Operating system kernel (Linux expected)
- `$facts['os']['family']`: OS family (Debian expected) - used in apt module for OS compatibility checks
- `$facts['os']['name']`: Specific OS name (Ubuntu/Debian) - used in apt module
- `$facts['environment']`: Puppet environment (production/staging/development) - used for conditional monitoring resource realization
- `$facts['apt_update_last_success']`: APT update timestamp - used in apt module for update frequency decisions

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution for log directory, rotation count, max size, and app name. No complex logic.

**app.env.erb**: Contains conditional logic block for environment-specific settings. In production: DEBUG=false, specific CORS origins. In non-production: DEBUG=true, permissive CORS. Uses 8 variables including database URL construction.

**app.service.epp**: EPP template with 11 typed parameters. Complex systemd unit file with security hardening, proper dependency declarations, and calculated timeout values. No conditional logic but uses arithmetic for timeout calculation.

## PuppetDB Dependencies

**Virtual resources**: 4 monitoring-related virtual resources (`@package`, `@service`, `@cron`) that are realized conditionally in production environment only.

**Collectors**: Uses `<<| package |>>`, `<<| service |>>`, `<<| cron |>>` to realize virtual resources when environment is production. Migration note: Collectors use no search expression, realizing all virtual resources of each type.

## Checks for the Migration

**Files to verify**:
- `/opt/myapp` (application directory)
- `/opt/myapp/.env` (environment file)
- `/opt/myapp/venv` (Python virtual environment)
- `/var/log/myapp` (log directory)
- `/etc/logrotate.d/myapp` (log rotation config)
- `/etc/systemd/system/myapp.service` (systemd unit)
- `/usr/local/bin/db-backup.sh` (backup script)
- `/usr/local/bin/app-healthcheck.sh` (health check script)
- `/etc/apt/sources.list.d/pgdg.list` (PostgreSQL repository)

**Service endpoints to check**:
- Application HTTP endpoint: `http://localhost:8000`
- PostgreSQL database: `localhost:5432`
- Health check endpoint: application-specific

**Templates rendered**:
- `logrotate.conf.erb` → `/etc/logrotate.d/myapp` (1 render)
- `app.env.erb` → `/opt/myapp/.env` (1 render)
- `app.service.epp` → `/etc/systemd/system/myapp.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status myapp
systemctl status postgresql
systemctl status chrony
systemctl status rsyslog

# Instance-specific checks
curl -f http://localhost:8000/health
sudo -u postgres psql -c "\l"
/opt/myapp/venv/bin/python --version

# Configuration validation commands
test -f /opt/myapp/.env
test -d /opt/myapp/venv
test -f /etc/systemd/system/myapp.service

# Network/connectivity checks
nc -z localhost 8000
nc -z localhost 5432
```