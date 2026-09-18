---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: Python web application stack with PostgreSQL database, systemd service management, log rotation, and monitoring. Deploys a Python app from Git repository with virtual environment, database setup, and health checks.

## Service Type and Instances

**Service Type**: Python Web Application Stack

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: Gunicorn WSGI server, 4 workers, sync worker class, 1000 max requests

## File Structure

```
site-modules/profile_app_stack/
├── manifests/
│   ├── init.pp
│   ├── python.pp
│   ├── database.pp
│   ├── app.pp
│   ├── service.pp
│   └── monitoring.pp
├── templates/
│   ├── logrotate.conf.erb
│   ├── app.env.erb
│   └── app.service.epp
└── data/
    ├── common.yaml
    └── environment/
        ├── production.yaml
        └── staging.yaml

site-modules/profile_postgresql/
├── manifests/
│   ├── init.pp
│   ├── repo.pp
│   ├── install.pp
│   └── service.pp
└── data/
    └── os/
        └── Debian.yaml

site-modules/role/
└── manifests/
    └── app_server.pp

site-modules/profile/
└── manifests/
    └── base/
        └── base.pp
    └── app/
        └── stack.pp

migration-dependencies/apt/
├── manifests/
│   ├── init.pp
│   ├── update.pp
│   ├── setting.pp
│   ├── keyring.pp
│   └── source.pp
└── templates/
    └── sources.list.erb

./data/
└── common.yaml
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point role class
   - `include profile::base::base`
   - `include profile::app::stack`

2. **profile::base::base** (`site-modules/profile/manifests/base/base.pp`):
   - Base system configuration
   - Common packages and settings

3. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Application stack wrapper
   - `include profile_app_stack`

4. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera lookups: app_name=myapp, app_repo=https://github.com/company/myapp.git, app_revision=main, app_port=8000, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, db_host=localhost, db_port=5432, db_name=myapp_db, db_user=myapp_user, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info
   - Builds database URL using custom function: `profile_app_stack::app_db_url()`
   - `contain profile_app_stack::python`
   - `contain profile_app_stack::database`
   - `contain profile_app_stack::app`
   - `contain profile_app_stack::service`
   - `contain profile_app_stack::monitoring`
   - Sets ordering: `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`

5. **profile_app_stack::python** (`site-modules/profile_app_stack/manifests/python.pp`):
   - `package 'python3.11'` → ensure: `installed`
   - `package 'python3.11-pip'` → ensure: `installed`
   - `package 'python3.11-venv'` → ensure: `installed`
   - `package 'python3.11-dev'` → ensure: `installed`
   - `package 'git'` → ensure: `installed`
   - `package 'build-essential'` → ensure: `installed`
   - `group 'myapp'` → ensure: `present`, system: `true`
   - `user 'myapp'` → ensure: `present`, gid: `myapp`, home: `/opt/myapp`, shell: `/bin/bash`, system: `true`, managehome: `false`
   - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp'` (template `templates/logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`

6. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - **Conditional**: if db_host == 'localhost' (true):
     - Includes dependency module: `profile_postgresql`
       - **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
         - Includes dependency module: `apt` (from `migration-dependencies/apt`)
           - **apt** (`migration-dependencies/apt/manifests/init.pp`):
             - `fail 'This module only works on Debian or derivatives like Ubuntu'` if not Debian family
             - `apt::update` → manages apt cache updates with frequency logic
             - `file '/etc/apt/sources.list'` → purge management
             - `file '/etc/apt/sources.list.d'` → purge management
             - `file '/etc/apt/preferences'` → purge management
             - `file '/etc/apt/preferences.d'` → purge management
             - `file '/etc/apt/apt.conf.d'` → purge management
             - `stdlib::ensure_packages 'gnupg'` → ensure: `present`
           - **apt::update** (`migration-dependencies/apt/manifests/update.pp`):
             - Complex frequency logic based on `$facts['apt_update_last_success']`
             - `exec 'apt_update'` with conditional execution
           - **apt::setting** (`migration-dependencies/apt/manifests/setting.pp`):
             - Defined type for APT configuration settings
           - **apt::keyring** (`migration-dependencies/apt/manifests/keyring.pp`):
             - Defined type with loops for GPG key management
           - **apt::source** (`migration-dependencies/apt/manifests/source.pp`):
             - Defined type for repository sources
         - **apt::source 'pgdg'** → location: `http://apt.postgresql.org/pub/repos/apt/`, release: `jammy-pgdg`, repos: `main`, key: PostgreSQL signing key
       - **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
         - `package 'postgresql-15'` → ensure: `installed`
         - `package 'postgresql-client-15'` → ensure: `installed`
         - `package 'postgresql-contrib-15'` → ensure: `installed`
         - `package 'libpq-dev'` → ensure: `installed`
       - **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
         - `service 'postgresql'` → ensure: `running`, enable: `true`
     - `exec 'create_db_user'` → creates PostgreSQL user myapp_user
     - `exec 'create_database'` → creates database myapp_db
     - `exec 'grant_db_privileges'` → grants ALL privileges on myapp_db to myapp_user
   - `file '/usr/local/bin/db-backup.sh'` → database backup script
   - `cron 'database_backup'` → daily database backup at 2:00 AM

7. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
   - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp'` → provider: `git`, source: `https://github.com/company/myapp.git`, revision: `main`, user: `myapp`
   - `exec 'create_app_venv'` → creates Python virtual environment at `/opt/myapp/venv`
   - `exec 'install_requirements'` → installs Python packages from requirements.txt
   - `file '/opt/myapp/.env'` (template `templates/app.env.erb`) → mode: `0644`, owner: `myapp`, group: `myapp`
   - `file '/usr/local/bin/app-healthcheck.sh'` → health check script
   - `exec 'run_db_migrations'` → runs database migrations

8. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
   - `file '/etc/systemd/system/myapp.service'` (template `templates/app.service.epp`) → mode: `0644`, owner: `root`, group: `root`
   - `exec 'systemd_daemon_reload'` → reloads systemd configuration
   - `service 'myapp'` → ensure: `running`, enable: `true`
   - **notifies**: `file[.env] ~> service[myapp]` (restart on config change)

9. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - `@package 'prometheus-node-exporter'` → virtual resource
   - `@service 'prometheus-node-exporter'` → virtual resource
   - `@package 'prometheus-pushgateway'` → virtual resource
   - `@cron 'push_app_metrics'` → virtual resource
   - **Conditional**: if facts['environment'] == 'production':
     - `<<| package |>>` → realizes all virtual package resources
     - `<<| service |>>` → realizes all virtual service resources
     - `<<| cron |>>` → realizes all virtual cron resources
   - `cron 'app_health_check'` → runs health check every 5 minutes

## Variables

**Variable Flow Summary**: 29 variables across 5 Hiera levels

### Variable Definitions

**common.yaml (./data/common.yaml)** → Migration note: Base defaults for all nodes
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
- `profile_app_stack::db_password`: `***encrypted***` (type: string)
- `profile_app_stack::worker_count`: `4` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_postgresql::version`: `15` (type: string)

**common.yaml (site-modules/profile_app_stack/data/common.yaml)** → Migration note: Module-level defaults
- `profile_app_stack::python_version`: `python3.11` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

**production.yaml (site-modules/profile_app_stack/data/environment/production.yaml)** → Migration note: Production environment overrides
- `profile_app_stack::secret_key`: `***encrypted***` (type: string)

**staging.yaml (site-modules/profile_app_stack/data/environment/staging.yaml)** → Migration note: Staging environment overrides
- `profile_app_stack::secret_key`: `***encrypted***` (type: string)

**Debian.yaml (site-modules/profile_postgresql/data/os/Debian.yaml)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_postgresql::package_names`: `['postgresql-15', 'postgresql-client-15', 'postgresql-contrib-15']` (type: array)
- `profile_postgresql::service_name`: `postgresql` (type: string)
- `profile_postgresql::repo_key_id`: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8` (type: string)
- `profile_postgresql::repo_key_source`: `https://www.postgresql.org/media/keys/ACCC4CF8.asc` (type: string)
- `profile_postgresql::repo_location`: `http://apt.postgresql.org/pub/repos/apt/` (type: string)
- `profile_postgresql::repo_release`: `jammy-pgdg` (type: string)

### Variable Migration Summary

- **Common defaults**: 19 variables from environment-level common.yaml (base configuration for all nodes)
- **Module-specific variables**: 4 variables from module-level common.yaml
- **Environment-specific variables**: 2 variables that vary by deployment environment (production, staging)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Encrypted variables**: 3 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple levels:
- **profile_app_stack::secret_key**: defined at production and staging levels, merge strategy: first
- **All profile_app_stack variables**: defined at environment and module levels, merge strategy: first (environment takes precedence)

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- Environment-level variables override module-level defaults
- OS-specific variables loaded conditionally based on `$facts['os']['family']`

## Custom Types and Providers

**Custom Functions**:
- `profile_app_stack::app_db_url()` - Constructs database connection URL from individual parameters

## Dependencies

**External module dependencies**:
- puppetlabs-vcsrepo (version: 6.1.0) - Git repository management
- puppetlabs-apt (version: 9.4.0) - APT repository management
- puppetlabs-stdlib (version: 9.7.0) - Standard library functions

**System package dependencies**:
- python3.11, python3.11-pip, python3.11-venv, python3.11-dev
- git, build-essential
- postgresql-15, postgresql-client-15, postgresql-contrib-15, libpq-dev
- gnupg (for APT key management)
- prometheus-node-exporter, prometheus-pushgateway (monitoring)

**Service dependencies**:
- PostgreSQL service must be running before application service
- APT repository setup before PostgreSQL installation
- Python environment setup before application deployment

## Puppet Facts Used

- `$facts['kernel']` - Operating system kernel type (Linux)
- `$facts['os']['family']` - OS family (Debian) - used for OS-specific configuration
- `$facts['os']['name']` - OS name (Ubuntu/Debian) - used in apt module logic
- `$facts['environment']` - Puppet environment (production/staging) - controls monitoring deployment
- `$facts['apt_update_last_success']` - Last successful APT update timestamp - used in apt update frequency logic

## Template Conversion Notes

**logrotate.conf.erb**:
- Variables: log_dir, log_rotate_count, log_max_size, app_name
- Simple variable substitution, no complex logic

**app.env.erb**:
- Variables: db_url, app_name, app_port, secret_key, log_level, log_dir, worker_count, facts['environment']
- Conditional logic: Different DEBUG/ALLOWED_HOSTS/CORS_ORIGINS settings for production vs non-production environments
- Environment-based configuration switching

**app.service.epp**:
- Variables: app_name, app_dir, app_user, app_group, app_port, worker_count, worker_class, max_requests, graceful_timeout, log_dir, log_level
- Mathematical expression: graceful_timeout + 5 for TimeoutStopSec calculation
- Complex Gunicorn command line construction with multiple parameters

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Virtual Resources**:
- `@package 'prometheus-node-exporter'` - Virtual monitoring package, exported for conditional realization
- `@service 'prometheus-node-exporter'` - Virtual monitoring service, exported for conditional realization
- `@package 'prometheus-pushgateway'` - Virtual metrics gateway package, exported for conditional realization
- `@cron 'push_app_metrics'` - Virtual metrics push job, exported for conditional realization

**Resource Collectors**:
- `<<| package |>>` - Realizes ALL virtual packages (no search expression), migration notes: requires inventory of all virtual packages across infrastructure
- `<<| service |>>` - Realizes ALL virtual services (no search expression), migration notes: requires inventory of all virtual services across infrastructure
- `<<| cron |>>` - Realizes ALL virtual cron jobs (no search expression), migration notes: requires inventory of all virtual cron jobs across infrastructure

**Migration Notes**: The collector pattern uses no search expressions, meaning it will realize every virtual resource of that type from any class. This requires careful inventory of all virtual resources across the entire Puppet codebase to understand what gets deployed in production.

## Checks for the Migration

**Files to verify**:
- `/opt/myapp` (application directory)
- `/opt/myapp/.env` (environment configuration)
- `/opt/myapp/venv` (Python virtual environment)
- `/etc/systemd/system/myapp.service` (systemd unit file)
- `/etc/logrotate.d/myapp` (log rotation configuration)
- `/var/log/myapp` (log directory)
- `/usr/local/bin/db-backup.sh` (backup script)
- `/usr/local/bin/app-healthcheck.sh` (health check script)

**Service endpoints to check**:
- Port 8000 (myapp HTTP endpoint)
- Port 5432 (PostgreSQL database)

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
curl http://localhost:8000/health
su - myapp -c '/opt/myapp/venv/bin/python -c "import app"'
psql -h localhost -U myapp_user -d myapp_db -c '\dt'

# Configuration validation commands
python3.11 --version
/opt/myapp/venv/bin/pip list
systemd-analyze verify /etc/systemd/system/myapp.service

# Network/connectivity checks
netstat -tlnp | grep :8000
netstat -tlnp | grep :5432
```