---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: Python web application stack with PostgreSQL database, systemd service management, monitoring, and environment-specific configuration. Deploys from Git repository with virtual environment, database setup, log rotation, and health monitoring.

## Service Type and Instances

**Service Type**: Python Web Application Stack

**Configured Instances**:
- **myapp-api**: FastAPI/Django application server
  - Location/Path: `/opt/myapp-api`
  - Port/Socket: `8000`
  - Key Config: Gunicorn with Uvicorn workers, PostgreSQL backend, systemd service

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

site-modules/profile/manifests/app/stack.pp
```

## Module Explanation

The module performs operations in this order:

1. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Wrapper class that includes `profile_app_stack`
   - Provides standardized entry point for application stack deployment

2. **profile_app_stack** (`manifests/init.pp`):
   - Sets class parameters from Hiera lookups
   - Builds database URL using custom function `profile_app_stack::app_db_url`
   - `contain profile_app_stack::python`
   - `contain profile_app_stack::database`
   - `contain profile_app_stack::app`
   - `contain profile_app_stack::service`
   - `contain profile_app_stack::monitoring`
   - Sets ordering: `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`

3. **profile_app_stack::python** (`manifests/python.pp`):
   - `package 'python3'` → ensure: `present`
   - `package 'python3-pip'` → ensure: `present`
   - `package 'python3-venv'` → ensure: `present`
   - `package 'python3-dev'` → ensure: `present`
   - `package 'build-essential'` → ensure: `present`
   - `package 'libpq-dev'` → ensure: `present`
   - `group 'myapp'` → ensure: `present`, gid: `1001`
   - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp-api`, shell: `/bin/bash`
   - `file '/var/log/myapp-api'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp-api'` (template `logrotate.conf.erb`) → mode: `0644`
     - Passes: log_dir=`/var/log/myapp-api`, log_rotate_count=`7`, log_max_size=`100M`, app_name=`myapp-api`

4. **profile_app_stack::database** (`manifests/database.pp`):
   - **Conditional**: if db_host == `localhost`
     - `contain profile_postgresql` (includes repo setup, installation, and service management)
     - `exec 'create_db_user'` → creates database user `myapp_app`
     - `exec 'create_database'` → creates database `myapp_db`
     - `exec 'grant_db_privileges'` → grants ALL privileges to user
   - `file '/usr/local/bin/db-backup.sh'` → mode: `0755`, owner: `root`
   - `cron 'database_backup'` → hour: `2`, minute: `0`, command: `/usr/local/bin/db-backup.sh`

5. **profile_app_stack::app** (`manifests/app.pp`):
   - `file '/opt/myapp-api'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp-api'` → ensure: `present`, provider: `git`, source: `https://github.com/example-org/myapp-api.git`, revision: `main` (staging) / `v2.4.1` (production)
   - `exec 'create_app_venv'` → creates Python virtual environment at `/opt/myapp-api/venv`
   - `exec 'install_requirements'` → installs from `requirements.txt`
   - **Conditional**: if pip_packages not empty
     - Installs additional packages: `uvicorn`, `gunicorn`, `psycopg2-binary`
   - `file '/opt/myapp-api/.env'` (template `app.env.erb`) → mode: `0600`, owner: `myapp`, group: `myapp`
     - Passes: db_url, app_name=`myapp-api`, app_port=`8000`, secret_key, log_level, log_dir=`/var/log/myapp-api`, worker_count, facts['environment']
   - `file '/usr/local/bin/app-healthcheck.sh'` → mode: `0755`, owner: `root`
   - `exec 'run_db_migrations'` → runs database migrations

6. **profile_app_stack::service** (`manifests/service.pp`):
   - `file '/etc/systemd/system/myapp-api.service'` (template `app.service.epp`) → mode: `0644`
     - Passes: app_name=`myapp-api`, app_dir=`/opt/myapp-api`, app_user=`myapp`, app_group=`myapp`, app_port=`8000`, worker_count, worker_class=`uvicorn.workers.UvicornWorker`, max_requests, graceful_timeout=`30`, log_dir=`/var/log/myapp-api`, log_level
   - `exec 'systemd_daemon_reload'` → reloads systemd configuration
   - `service 'myapp-api'` → ensure: `running`, enable: `true`
   - **notifies**: `file[myapp-api.service] ~> exec[systemd_daemon_reload] ~> service[myapp-api]`

7. **profile_app_stack::monitoring** (`manifests/monitoring.pp`):
   - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual)
   - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual)
   - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual)
   - `@cron 'push_app_metrics'` → minute: `*/5`, command: `/usr/local/bin/push-metrics.sh` (virtual)
   - **Conditional**: if facts['environment'] == `production`
     - Realizes virtual Package, Service, and Cron resources using collectors
   - `cron 'app_health_check'` → minute: `*/2`, command: `/usr/local/bin/app-healthcheck.sh`

## Variables

**Variable Flow Summary**: 22 variables across 3 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_app_stack::app_name`: `myapp-api` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/example-org/myapp-api.git` (type: string)
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp-api` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::python_version`: `python3` (type: string)
- `profile_app_stack::pip_packages`: `[uvicorn, gunicorn, psycopg2-binary]` (type: array)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_db` (type: string)
- `profile_app_stack::db_user`: `myapp_app` (type: string)
- `profile_app_stack::db_password`: `ENC[PKCS7,...]` (type: string, encrypted)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `uvicorn.workers.UvicornWorker` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp-api` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

**environment/production.yaml (production overrides)** → Migration note: Production-specific variables for performance and security
- `profile_app_stack::app_revision`: `v2.4.1` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `5000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::db_host`: `db-primary.prod.internal` (type: string)
- `profile_app_stack::secret_key`: `ENC[PKCS7,...]` (type: string, encrypted)

**environment/staging.yaml (staging overrides)** → Migration note: Staging-specific variables for development and testing
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::worker_count`: `1` (type: integer)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging-not-secret-at-all` (type: string)

### Variable Migration Summary

- **Common defaults**: 22 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables
- **Environment-specific variables**: 6 variables for production, 6 variables for staging
- **Host-specific variables**: 0 variables
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_revision**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::worker_count**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::max_requests**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::log_level**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::db_host**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::secret_key**: defined at environment levels only, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging

## Dependencies

**External module dependencies**:
- `puppetlabs-vcsrepo` (Git repository management)
- `puppetlabs-stdlib` (standard library functions)
- `profile_postgresql` (PostgreSQL server when db_host=localhost)

**System package dependencies**:
- `python3`, `python3-pip`, `python3-venv`, `python3-dev`
- `build-essential`, `libpq-dev`
- `prometheus-node-exporter`, `prometheus-pushgateway` (production only)

**Service dependencies**:
- PostgreSQL service (when local database)
- Network target (systemd dependency)

## Puppet Facts Used

- `$facts['environment']`: Environment name (production/staging) for conditional configuration in templates and monitoring resource realization

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution for log directory, rotation count, max size, and app name.

**app.env.erb**: Contains 1 conditional logic block for environment-specific settings (DEBUG, ALLOWED_HOSTS, CORS_ORIGINS). Uses facts['environment'] to determine production vs non-production configuration.

**app.service.epp**: Complex systemd unit template with 11 variables including calculated timeout values (graceful_timeout + 5). Uses EPP syntax with parameter validation.

## Checks for the Migration

**Files to verify**:
- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/python.pp`
- `site-modules/profile_app_stack/manifests/database.pp`
- `site-modules/profile_app_stack/manifests/app.pp`
- `site-modules/profile_app_stack/manifests/service.pp`
- `site-modules/profile_app_stack/manifests/monitoring.pp`
- `site-modules/profile/manifests/app/stack.pp`
- `/opt/myapp-api/.env`
- `/etc/systemd/system/myapp-api.service`
- `/etc/logrotate.d/myapp-api`
- `/var/log/myapp-api/`
- `/usr/local/bin/db-backup.sh`
- `/usr/local/bin/app-healthcheck.sh`

**Service endpoints to check**:
- `http://localhost:8000` (myapp-api application endpoint)
- PostgreSQL connection on port 5432 (when local)

**Templates rendered**:
- `logrotate.conf.erb` → `/etc/logrotate.d/myapp-api` (1 render)
- `app.env.erb` → `/opt/myapp-api/.env` (1 render)
- `app.service.epp` → `/etc/systemd/system/myapp-api.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status myapp-api

# Instance-specific checks
curl -f http://localhost:8000/health

# Configuration validation commands
sudo -u myapp /opt/myapp-api/venv/bin/python -c "import app"

# Network/connectivity checks
psql -h localhost -U myapp_app -d myapp_db -c "SELECT 1"
```