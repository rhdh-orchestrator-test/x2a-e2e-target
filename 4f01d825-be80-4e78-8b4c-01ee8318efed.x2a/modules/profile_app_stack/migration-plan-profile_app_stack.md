---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack module that sets up a complete WSGI application environment with PostgreSQL database, systemd service management, and monitoring. Deploys applications from Git repositories with virtual environments, configures database connections, and provides health checking and log rotation.

## Service Type and Instances

**Service Type**: Python Web Application Stack

**Configured Instances**:
- **myapp**: Python WSGI application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: Gunicorn WSGI server with 4 workers, sync worker class, PostgreSQL backend

## File Structure

```
site-modules/profile_app_stack/manifests/init.pp
site-modules/profile_app_stack/manifests/python.pp
site-modules/profile_app_stack/manifests/database.pp
site-modules/profile_app_stack/manifests/app.pp
site-modules/profile_app_stack/manifests/service.pp
site-modules/profile_app_stack/manifests/monitoring.pp
site-modules/profile_postgresql/manifests/init.pp
site-modules/profile_postgresql/manifests/repo.pp
site-modules/profile_postgresql/manifests/install.pp
site-modules/profile_postgresql/manifests/service.pp
site-modules/role/manifests/app_stack.pp
site-modules/profile/manifests/app/stack.pp
site-modules/profile_app_stack/templates/logrotate.conf.erb
site-modules/profile_app_stack/templates/app.env.erb
site-modules/profile_app_stack/templates/app.service.epp
site-modules/profile_app_stack/data/common.yaml
site-modules/profile_app_stack/data/environment/production.yaml
site-modules/profile_app_stack/data/environment/staging.yaml
site-modules/profile_postgresql/data/common.yaml
site-modules/profile_postgresql/data/os/Debian.yaml
migration-dependencies/apt/manifests/init.pp
migration-dependencies/apt/manifests/source.pp
migration-dependencies/apt/manifests/setting.pp
migration-dependencies/apt/manifests/update.pp
migration-dependencies/apt/manifests/keyring.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::app_stack** (`site-modules/role/manifests/app_stack.pp`):
   - Entry point role class that validates kernel compatibility
   - Conditional check: if facts['kernel'] == 'Linux' (TRUE)
   - `include profile::app::stack`

2. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Profile wrapper class that includes the main application stack
   - Uses facts['environment'] for environment-specific configuration
   - `include profile_app_stack`

3. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera lookups: app_name=myapp, app_repo=https://github.com/company/myapp.git, app_revision=main, app_port=8000, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, db_host=localhost, db_port=5432, db_name=myapp_db, db_user=myapp_user, db_password=[ENCRYPTED], worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info, secret_key=[ENCRYPTED]
   - Builds database URL: `postgresql://myapp_user:[ENCRYPTED]@localhost:5432/myapp_db`
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
   - `package 'git'` → ensure: `present`
   - `group 'myapp'` → ensure: `present`, gid: `1001`
   - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp`, shell: `/bin/bash`, managehome: `true`
   - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp'` (template `logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_dir=/var/log/myapp, log_rotate_count=30, log_max_size=100M, app_name=myapp

5. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Conditional: if db_host == 'localhost' (TRUE):
     - Includes dependency module: `profile_postgresql`
       - **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
         - `contain profile_postgresql::repo`
         - `contain profile_postgresql::install`
         - `contain profile_postgresql::service`
         - Sets ordering: `profile_postgresql::repo -> profile_postgresql::install -> profile_postgresql::service`
       - **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
         - Includes dependency module: `apt`
           - **apt** (`migration-dependencies/apt/manifests/init.pp`):
             - Conditional: if os.family != 'Debian' (FALSE - no action)
             - `contain apt::update`
             - **apt::update** (`migration-dependencies/apt/manifests/update.pp`):
               - `exec 'apt_update'` → command: `/usr/bin/apt-get update`, refreshonly: `true`
             - `file '/etc/apt/sources.list'` → ensure: `file`, owner: `root`, group: `root`, mode: `0644`
             - `file '/etc/apt/sources.list.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
             - `file '/etc/apt/preferences'` → ensure: `file`, owner: `root`, group: `root`, mode: `0644`
             - `file '/etc/apt/preferences.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
             - `file '/etc/apt/apt.conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
             - Iterations: `$keyrings.each` — Loop runs 0 times (no keyrings configured)
             - `package 'gnupg'` → ensure: `present`
         - **apt::source 'pgdg'** (`migration-dependencies/apt/manifests/source.pp`):
           - **apt::setting 'list-pgdg'** (`migration-dependencies/apt/manifests/setting.pp`):
             - `file '/etc/apt/sources.list.d/pgdg.list'` → ensure: `file`, owner: `root`, group: `root`, mode: `0644`, content: `deb https://apt.postgresql.org/pub/repos/apt/ jammy-pgdg main`, notify: `Exec[apt_update]`
       - **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
         - `package 'postgresql-15'` → ensure: `present`
         - `package 'postgresql-client-15'` → ensure: `present`
         - `package 'postgresql-contrib-15'` → ensure: `present`
         - `package 'libpq-dev'` → ensure: `present`
       - **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
         - `service 'postgresql'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
     - `exec 'create_db_user'` → command: `sudo -u postgres createuser -d -r -s myapp_user`, unless: `sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp_user'" | grep -q 1`
     - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp_user myapp_db`, unless: `sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw myapp_db`, require: `Exec[create_db_user]`
     - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp_user;"`, require: `Exec[create_database]`
   - `file '/usr/local/bin/db-backup.sh'` → ensure: `file`, owner: `root`, group: `root`, mode: `0755`, content: database backup script
   - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `0`

6. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
   - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp'` → ensure: `present`, provider: `git`, source: `https://github.com/company/myapp.git`, revision: `main`, user: `myapp`, owner: `myapp`, group: `myapp`
   - `exec 'create_app_venv'` → command: `python3 -m venv /opt/myapp/venv`, user: `myapp`, cwd: `/opt/myapp`, creates: `/opt/myapp/venv/bin/python`, require: `Vcsrepo[/opt/myapp]`
   - `exec 'install_requirements'` → command: `/opt/myapp/venv/bin/pip install -r requirements.txt`, user: `myapp`, cwd: `/opt/myapp`, require: `Exec[create_app_venv]`, subscribe: `Vcsrepo[/opt/myapp]`
   - Conditional: if !empty(pip_packages) (FALSE - pip_packages is empty array)
   - `file '/opt/myapp/.env'` (template `app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
     - Passes: db_url=postgresql://myapp_user:[ENCRYPTED]@localhost:5432/myapp_db, app_name=myapp, app_port=8000, secret_key=[ENCRYPTED], log_level=info, log_dir=/var/log/myapp, worker_count=4, facts['environment']=production, debug_mode=false
   - `file '/usr/local/bin/app-healthcheck.sh'` → ensure: `file`, owner: `root`, group: `root`, mode: `0755`, content: health check script
   - `exec 'run_db_migrations'` → command: `/opt/myapp/venv/bin/python manage.py migrate`, user: `myapp`, cwd: `/opt/myapp`, require: `File[/opt/myapp/.env]`, subscribe: `Vcsrepo[/opt/myapp]`

7. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
   - `file '/etc/systemd/system/myapp.service'` (template `app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: app_name=myapp, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, app_port=8000, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info, timeout_stop_sec=35
   - `exec 'systemd_daemon_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`, subscribe: `File[/etc/systemd/system/myapp.service]`
   - `service 'myapp'` → ensure: `running`, enable: `true`, require: `Exec[systemd_daemon_reload]`, subscribe: `File[/etc/systemd/system/myapp.service]`

8. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual resource)
   - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual resource)
   - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual resource)
   - `@cron 'push_app_metrics'` → command: `/usr/local/bin/push-metrics.sh`, user: `myapp`, minute: `*/5` (virtual resource)
   - Conditional: if facts['environment'] == 'production' (TRUE):
     - `<<| package |>>` → realizes all virtual package resources (prometheus-node-exporter, prometheus-pushgateway)
     - `<<| service |>>` → realizes all virtual service resources (prometheus-node-exporter)
     - `<<| cron |>>` → realizes all virtual cron resources (push_app_metrics)
   - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `root`, minute: `*/2`

## Variables

**Variable Flow Summary**: 29 variables across 4 Hiera levels

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
- `profile_app_stack::db_password`: `[ENCRYPTED]` (type: string)
- `profile_app_stack::worker_count`: `4` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `[ENCRYPTED]` (type: string)
- `profile_app_stack::python_version`: `3.11` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `30` (type: integer)
- `profile_postgresql::version`: `15` (type: string)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_postgresql::package_names`: `['postgresql-15', 'postgresql-client-15', 'postgresql-contrib-15']` (type: array)
- `profile_postgresql::service_name`: `postgresql` (type: string)
- `profile_postgresql::repo_location`: `https://apt.postgresql.org/pub/repos/apt/` (type: string)
- `profile_postgresql::repo_release`: `jammy-pgdg` (type: string)
- `profile_postgresql::repo_key_id`: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8` (type: string)
- `profile_postgresql::repo_key_source`: `https://www.postgresql.org/media/keys/ACCC4CF8.asc` (type: string)

### Variable Migration Summary

- **Common defaults**: 24 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 0 variables (overridden by root-level configuration)
- **Host-specific variables**: 0 variables
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_name**: defined at root-level and module-level, merge strategy: first
- **profile_app_stack::app_repo**: defined at root-level and module-level, merge strategy: first
- **profile_app_stack::app_revision**: defined at root-level, module-level, and environment-level, merge strategy: first
- **profile_app_stack::worker_count**: defined at root-level, module-level, and environment-level, merge strategy: first
- **profile_app_stack::secret_key**: defined at root-level, module-level, and environment-level, merge strategy: first
- **profile_postgresql::version**: defined at root-level and module-level, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- Root-level configuration takes precedence over module and environment defaults

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (forge, version: 9.7.0)
- puppetlabs-vcsrepo (forge, version: 6.1.0)
- puppetlabs-apt (forge, version: 9.4.0)

**System package dependencies**:
- python3, python3-pip, python3-venv, python3-dev, build-essential, git
- postgresql-15, postgresql-client-15, postgresql-contrib-15, libpq-dev
- gnupg, prometheus-node-exporter, prometheus-pushgateway

**Service dependencies**:
- PostgreSQL service must be running before application service
- APT repository updates before PostgreSQL installation
- Python environment setup before application deployment
- Application deployment before service configuration

## Puppet Facts Used

- `$facts['kernel']`: Operating system kernel type (Linux) - used for compatibility validation
- `$facts['os']['family']`: OS family (Debian) - used for conditional package management
- `$facts['os']['name']`: OS name (Ubuntu) - used for repository configuration
- `$facts['environment']`: Puppet environment (production/staging) - used for conditional monitoring and template logic
- `$facts['apt_update_last_success']`: Last successful APT update timestamp

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution for log directory, rotation count, max size, and app name. No complex logic.

**app.env.erb**: Contains conditional logic block for environment-specific settings (DEBUG, ALLOWED_HOSTS, CORS_ORIGINS). Uses facts['environment'] to determine production vs non-production configuration. Variables: db_url, app_name, app_port, secret_key, log_level, log_dir, worker_count, debug_mode.

**app.service.epp**: EPP template with typed parameters. Contains arithmetic expression for TimeoutStopSec calculation (graceful_timeout + 5). Variables: app_name, app_dir, app_user, app_group, app_port, worker_count, worker_class, max_requests, graceful_timeout, log_dir, log_level, timeout_stop_sec.

## Checks for the Migration

**Files to verify**:
- `/etc/logrotate.d/myapp`
- `/opt/myapp/.env`
- `/etc/systemd/system/myapp.service`
- `/etc/apt/sources.list.d/pgdg.list`
- `/usr/local/bin/db-backup.sh`
- `/usr/local/bin/app-healthcheck.sh`
- `/opt/myapp/venv/bin/python`
- `/var/log/myapp`

**Service endpoints to check**:
- Application: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

**Templates rendered**:
- `logrotate.conf.erb` → `/etc/logrotate.d/myapp` (1 render)
- `app.env.erb` → `/opt/myapp/.env` (1 render)
- `app.service.epp` → `/etc/systemd/system/myapp.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status myapp
systemctl status postgresql
systemctl status prometheus-node-exporter

# Instance-specific checks
sudo -u postgres psql -c "\l" | grep myapp_db
curl -f http://localhost:8000/health
/usr/local/bin/app-healthcheck.sh

# Configuration validation commands
python3 -m py_compile /opt/myapp/manage.py
/opt/myapp/venv/bin/python -c "import django; print('Django OK')"
sudo -u myapp /opt/myapp/venv/bin/python /opt/myapp/manage.py check

# Network/connectivity checks
nc -z localhost 5432
nc -z localhost 8000
```