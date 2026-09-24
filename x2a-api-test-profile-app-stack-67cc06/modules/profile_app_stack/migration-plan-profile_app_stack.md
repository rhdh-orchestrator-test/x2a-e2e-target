---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: Python web application stack with PostgreSQL database backend, systemd service management, log rotation, and monitoring. Deploys a Flask/Django-style app with gunicorn WSGI server, creates database user/schema, manages virtual environment with pip dependencies, and sets up health checks with optional Prometheus monitoring in production.

## Service Type and Instances

**Service Type**: Web Application Stack (Python WSGI)

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: gunicorn WSGI server, 4 workers, sync worker class, PostgreSQL backend

## File Structure

**Manifests**:
- `site-modules/role/manifests/app_server.pp`
- `site-modules/profile/manifests/app/stack.pp`
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

**Templates**:
- `site-modules/profile_app_stack/templates/app.env.erb`
- `site-modules/profile_app_stack/templates/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/app.service.epp`

**Data Files**:
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `site-modules/profile_postgresql/data/common.yaml`
- `site-modules/profile_postgresql/data/os/Debian.yaml`

**Dependencies**:
- `migration-dependencies/apt/` (APT repository management)
- `migration-dependencies/vcsrepo/` (Git repository management)

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes profile::app::stack
   - Sets up application server role configuration

2. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Wrapper class that includes profile_app_stack
   - Provides abstraction layer for application stack

3. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera lookups
   - Builds database URL: `postgresql://myapp:ENC[PKCS7,encrypted_password]@localhost:5432/myapp_db`
   - `contain profile_app_stack::python`
   - `contain profile_app_stack::database`
   - `contain profile_app_stack::app`
   - `contain profile_app_stack::service`
   - `contain profile_app_stack::monitoring`
   - Sets ordering: `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`

4. **profile_app_stack::python** (`site-modules/profile_app_stack/manifests/python.pp`):
   - `package 'python3'` → ensure: `present`
   - `package 'python3-pip'` → ensure: `present`
   - `package 'python3-venv'` → ensure: `present`
   - `package 'python3-dev'` → ensure: `present`
   - `package 'build-essential'` → ensure: `present`
   - `group 'myapp'` → ensure: `present`, gid: `1001`
   - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp`, shell: `/bin/bash`
   - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp'` (template `logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_dir='/var/log/myapp', log_rotate_count=30, log_max_size='100M', app_name='myapp'

5. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - **Conditional**: if db_host == 'localhost' (TRUE):
     - **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
       - `contain profile_postgresql::repo`
       - `contain profile_postgresql::install`
       - `contain profile_postgresql::service`
       - Sets ordering: `profile_postgresql::repo -> profile_postgresql::install -> profile_postgresql::service`
     - **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
       - **apt** dependency module setup:
         - `package 'gnupg'` → ensure: `present`
         - `file '/etc/apt/sources.list'` → managed
         - `file '/etc/apt/sources.list.d'` → purge unmanaged files
         - `file '/etc/apt/preferences'` → managed
         - `file '/etc/apt/preferences.d'` → purge unmanaged files
         - `file '/etc/apt/apt.conf.d'` → purge unmanaged files
         - `exec 'apt_update'` → refreshonly: `true`
       - **apt::source 'pgdg'**:
         - `file '/etc/apt/sources.list.d/pgdg.list'` → content: `deb https://apt.postgresql.org/pub/repos/apt jammy-pgdg main`
     - **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
       - `package 'postgresql-15'` → ensure: `present`
       - `package 'postgresql-client-15'` → ensure: `present`
       - `package 'postgresql-contrib-15'` → ensure: `present`
       - `package 'libpq-dev'` → ensure: `present`
     - **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
       - `service 'postgresql'` → ensure: `running`, enable: `true`
     - `exec 'create_db_user'` → command: `sudo -u postgres createuser -d -r -s myapp`, unless: `sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp'" | grep -q 1`
     - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp myapp_db`, unless: `sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw myapp_db`
     - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp;"`
   - `file '/usr/local/bin/db-backup.sh'` → owner: `root`, group: `root`, mode: `0755`
   - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `30`

6. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
   - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp'` → ensure: `present`, provider: `git`, source: `https://github.com/company/myapp.git`, revision: `main`, user: `myapp`
   - `exec 'create_app_venv'` → command: `python3 -m venv /opt/myapp/venv`, user: `myapp`, creates: `/opt/myapp/venv/bin/activate`
   - `exec 'install_requirements'` → command: `/opt/myapp/venv/bin/pip install -r /opt/myapp/requirements.txt`, user: `myapp`, refreshonly: `true`
   - `file '/opt/myapp/.env'` (template `app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
     - Passes: db_url='postgresql://myapp:ENC[PKCS7,encrypted_password]@localhost:5432/myapp_db', app_name='myapp', app_port=8000, secret_key='ENC[PKCS7,encrypted_secret]', log_level='info', log_dir='/var/log/myapp', worker_count=4, facts['environment']='production'
   - `file '/usr/local/bin/app-healthcheck.sh'` → owner: `root`, group: `root`, mode: `0755`
   - `exec 'run_db_migrations'` → command: `/opt/myapp/venv/bin/python /opt/myapp/manage.py migrate`, user: `myapp`, refreshonly: `true`

7. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
   - `file '/etc/systemd/system/myapp.service'` (template `app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: app_name='myapp', app_dir='/opt/myapp', app_user='myapp', app_group='myapp', app_port=8000, worker_count=4, worker_class='sync', max_requests=1000, graceful_timeout=30, log_dir='/var/log/myapp', log_level='info'
   - `exec 'systemd_daemon_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'myapp'` → ensure: `running`, enable: `true`
   - **notifies**: `file[myapp.service] ~> exec[systemd_daemon_reload] ~> service[myapp]`

8. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual)
   - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual)
   - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual)
   - `@cron 'push_app_metrics'` → command: `/usr/local/bin/app-healthcheck.sh | curl -X POST --data-binary @- http://localhost:9091/metrics/job/myapp`, user: `myapp`, minute: `*/5` (virtual)
   - **Conditional**: if facts['environment'] == 'production' (TRUE):
     - **Collector**: realizes all virtual Package resources
     - **Collector**: realizes all virtual Service resources
     - **Collector**: realizes all virtual Cron resources
   - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `myapp`, minute: `*/2`

## Variables

**Variable Flow Summary**: 26 variables across 3 Hiera levels

### Variable Definitions

**site-modules/profile_app_stack/data/common.yaml (module defaults)** → Migration note: Base defaults for all nodes
- `profile_app_stack::python_version`: `3.11` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `30` (type: integer)

**site-modules/profile_app_stack/data/environment/production.yaml (environment-specific)** → Migration note: Production environment variables, loaded conditionally based on environment
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
- `profile_app_stack::db_user`: `myapp` (type: string)
- `profile_app_stack::db_password`: `ENC[PKCS7,encrypted_password]` (type: string)
- `profile_app_stack::worker_count`: `4` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_secret]` (type: string)
- `profile_postgresql::version`: `15` (type: string)

**site-modules/profile_postgresql/data/os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_postgresql::package_names`: `['postgresql-15', 'postgresql-client-15', 'postgresql-contrib-15']` (type: array)
- `profile_postgresql::service_name`: `postgresql` (type: string)
- `profile_postgresql::repo_location`: `https://apt.postgresql.org/pub/repos/apt` (type: string)
- `profile_postgresql::repo_release`: `jammy-pgdg` (type: string)
- `profile_postgresql::repo_key_id`: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8` (type: string)
- `profile_postgresql::repo_key_source`: `https://www.postgresql.org/media/keys/ACCC4CF8.asc` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 20 variables that vary by deployment environment (dev, staging, prod)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

No variables are defined at multiple Hiera levels in this module.

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- No hash or deep merge strategies detected in this module

## Dependencies

**External module dependencies**:
- puppetlabs-vcsrepo (Git repository management)
- puppetlabs-apt (APT repository management)
- puppetlabs-stdlib (standard library functions)

**System package dependencies**:
- python3, python3-pip, python3-venv, python3-dev, build-essential
- postgresql-15, postgresql-client-15, postgresql-contrib-15, libpq-dev
- gnupg (for APT key management)
- prometheus-node-exporter, prometheus-pushgateway (production only)

**Service dependencies**:
- PostgreSQL service must be running before application starts
- APT repository setup before PostgreSQL installation
- Python environment before application deployment
- Application deployment before service configuration

## Puppet Facts Used

- `$facts['os']['family']`: OS family detection (Debian)
- `$facts['os']['name']`: OS name detection (Ubuntu)
- `$facts['environment']`: Environment detection (production/staging) for conditional monitoring and application configuration
- `$facts['apt_update_last_success']`: APT update timestamp tracking

## Template Conversion Notes

**app.env.erb**: 8 variables, 1 conditional block for environment-specific settings (DEBUG, ALLOWED_HOSTS, CORS_ORIGINS based on production vs non-production environment detection)

**logrotate.conf.erb**: 4 variables, straightforward substitution for log rotation configuration

**app.service.epp**: 11 variables, 1 logic block with calculated expression (graceful_timeout + 5 for TimeoutStopSec), systemd service unit with security hardening

## Checks for the Migration

**Files to verify**:
- `/opt/myapp/.env` (application environment variables)
- `/etc/systemd/system/myapp.service` (systemd unit file)
- `/etc/logrotate.d/myapp` (log rotation configuration)
- `/etc/apt/sources.list.d/pgdg.list` (PostgreSQL repository)
- `/usr/local/bin/db-backup.sh` (database backup script)
- `/usr/local/bin/app-healthcheck.sh` (health check script)

**Service endpoints to check**:
- Port 8000 (myapp HTTP endpoint)
- Port 5432 (PostgreSQL database)
- Port 9100 (node-exporter, production only)
- Port 9091 (pushgateway, production only)

**Templates rendered**:
- `app.env.erb` → `/opt/myapp/.env` (1 render)
- `logrotate.conf.erb` → `/etc/logrotate.d/myapp` (1 render)
- `app.service.epp` → `/etc/systemd/system/myapp.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status myapp
systemctl status postgresql
systemctl status prometheus-node-exporter  # production only
systemctl status prometheus-pushgateway     # production only

# Instance-specific checks
curl http://localhost:8000/health  # myapp health check
sudo -u postgres psql -c "\l" | grep myapp_db  # database existence
/opt/myapp/venv/bin/python --version  # virtual environment check

# Configuration validation commands
python3 --version
/opt/myapp/venv/bin/pip list | grep -E "(django|flask|gunicorn)"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp'" | grep -q 1

# Network/connectivity checks
netstat -tlnp | grep :8000  # myapp port
netstat -tlnp | grep :5432  # postgresql port
```