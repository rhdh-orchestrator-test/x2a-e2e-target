---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack module that deploys a FastAPI/Django-style application with PostgreSQL database, systemd service management, monitoring, and environment-specific configuration. Handles Python environment setup, database provisioning, application deployment from Git, service configuration, and optional monitoring components.

## Service Type and Instances

**Service Type**: Web Application Stack

**Configured Instances**:
- **myapp-api**: Python web application server
  - Location/Path: `/opt/myapp-api`
  - Port/Socket: `8000` (production), `8000` (staging)
  - Key Config: Gunicorn WSGI server with uvicorn workers, PostgreSQL backend

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
   - Entry point class that contains profile classes
   - `contain profile::app::stack`

2. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Wrapper class that contains the main application stack
   - `contain profile_app_stack`
   - Uses `fact('environment')` for environment-specific logic

3. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera data
   - `contain profile_app_stack::python`
   - `contain profile_app_stack::database`
   - `contain profile_app_stack::app`
   - `contain profile_app_stack::service`
   - `contain profile_app_stack::monitoring`
   - Sets ordering: `Class['profile_app_stack::python'] -> Class['profile_app_stack::database'] -> Class['profile_app_stack::app'] ~> Class['profile_app_stack::service'] -> Class['profile_app_stack::monitoring']`

4. **profile_app_stack::python** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Iterations: `$python_packages.each` — runs 3 times for: **python3**, **python3-pip**, **python3-venv**
     - `package 'python3'` → ensure: `present`
     - `package 'python3-pip'` → ensure: `present`
     - `package 'python3-venv'` → ensure: `present`
   - `group 'myapp'` → ensure: `present`, gid: `1001`
   - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp-api`, shell: `/bin/bash`, managehome: `true`
   - `file '/var/log/myapp-api'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp-api'` (template `templates/logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_dir=/var/log/myapp-api, log_rotate_count=7, log_max_size=100M, app_name=myapp-api

5. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Conditional: `if $profile_app_stack::db_host == 'localhost'` (true in staging, false in production)
     - When true (staging):
       - `contain profile_postgresql`
         - **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
           - `contain profile_postgresql::repo`
           - `contain profile_postgresql::install`
           - `contain profile_postgresql::service`
           - Sets ordering: `Class['profile_postgresql::repo'] -> Class['profile_postgresql::install'] -> Class['profile_postgresql::service']`
         - **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
           - `contain apt` (Note: Complex APT module with circular dependencies and 110+ files)
             - **apt** (`migration-dependencies/apt/manifests/init.pp`):
               - `contain apt::update`
               - Multiple configuration files and settings for APT management
               - Includes apt::setting, apt::keyring, apt::source defined types
               - Complex parameter validation and conditional logic
           - `apt::source 'pgdg'` → location: `http://apt.postgresql.org/pub/repos/apt/`, release: `jammy-pgdg`, repos: `main`, key: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8`
         - **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
           - Iterations: `$profile_postgresql::package_names.each` — runs 3 times for: **postgresql-15**, **postgresql-client-15**, **postgresql-contrib-15**
             - `package 'postgresql-15'` → ensure: `present`
             - `package 'postgresql-client-15'` → ensure: `present`
             - `package 'postgresql-contrib-15'` → ensure: `present`
           - `package 'libpq-dev'` → ensure: `present`
         - **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
           - `service 'postgresql'` → ensure: `running`, enable: `true`
       - `exec 'create_db_user'` → command: `sudo -u postgres createuser myapp_app`, creates: `/var/lib/postgresql/users/myapp_app`
       - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp_app myapp_db`, creates: `/var/lib/postgresql/databases/myapp_db`
       - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp_app;"`
   - `file '/usr/local/bin/db-backup.sh'` → owner: `root`, group: `root`, mode: `0755`, content: database backup script
   - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `0`

6. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
   - `file '/opt/myapp-api'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp-api'` → ensure: `present`, provider: `git`, source: `https://github.com/example-org/myapp-api.git`, revision: `main` (staging) / `v2.4.1` (production), user: `myapp`
   - `exec 'create_app_venv'` → command: `python3 -m venv /opt/myapp-api/venv`, user: `myapp`, creates: `/opt/myapp-api/venv/bin/python`
   - `exec 'install_requirements'` → command: `/opt/myapp-api/venv/bin/pip install -r requirements.txt`, user: `myapp`, cwd: `/opt/myapp-api`
   - Conditional: `if !empty($pip_packages)` (true - has uvicorn, gunicorn, psycopg2-binary)
     - Iterations: `$pip_packages.each` — runs 3 times for: **uvicorn**, **gunicorn**, **psycopg2-binary**
       - `exec 'install_uvicorn'` → command: `/opt/myapp-api/venv/bin/pip install uvicorn`, user: `myapp`
       - `exec 'install_gunicorn'` → command: `/opt/myapp-api/venv/bin/pip install gunicorn`, user: `myapp`
       - `exec 'install_psycopg2-binary'` → command: `/opt/myapp-api/venv/bin/pip install psycopg2-binary`, user: `myapp`
   - `file '/opt/myapp-api/.env'` (template `templates/app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
     - Passes: db_url=postgresql://myapp_app:ENCRYPTED_PASSWORD@localhost:5432/myapp_db, app_name=myapp-api, app_port=8000, secret_key=ENCRYPTED_KEY, log_level=info/warning/debug, log_dir=/var/log/myapp-api, worker_count=2/8/1, facts['environment']
   - `file '/usr/local/bin/app-healthcheck.sh'` → owner: `root`, group: `root`, mode: `0755`, content: health check script
   - `exec 'run_db_migrations'` → command: `/opt/myapp-api/venv/bin/python manage.py migrate`, user: `myapp`, cwd: `/opt/myapp-api`

7. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
   - `file '/etc/systemd/system/myapp-api.service'` (template `templates/app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: app_name=myapp-api, app_dir=/opt/myapp-api, app_user=myapp, app_group=myapp, app_port=8000, worker_count=2/8/1, worker_class=uvicorn.workers.UvicornWorker, max_requests=1000/5000/100, graceful_timeout=30, log_dir=/var/log/myapp-api, log_level=info/warning/debug
   - `exec 'systemd_daemon_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'myapp-api'` → ensure: `running`, enable: `true`, subscribe: `File[/etc/systemd/system/myapp-api.service]`
   - notifies: `file[/opt/myapp-api/.env] ~> service[myapp-api]` (restart on config change)

8. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Virtual resources (using `@` syntax for deferred realization):
     - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual)
     - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual)
     - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual)
     - `@cron 'push_app_metrics'` → command: `/usr/local/bin/push-metrics.sh`, user: `myapp`, minute: `*/5` (virtual)
   - Conditional: `if $facts['environment'] == 'production'` (true in production only)
     - `realize Package['prometheus-node-exporter']`
     - `realize Service['prometheus-node-exporter']`
     - `realize Package['prometheus-pushgateway']`
     - `realize Cron['push_app_metrics']`
   - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `root`, minute: `*/2`

## Variables

**Variable Flow Summary**: 24 variables across 6 Hiera levels

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
- `profile_app_stack::db_password`: `ENC[PKCS7,encrypted_password]` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `uvicorn.workers.UvicornWorker` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp-api` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

**environment/production.yaml (production overrides)** → Migration note: Production-specific variables, loaded conditionally based on environment
- `profile_app_stack::app_revision`: `v2.4.1` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `5000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::db_host`: `db-primary.prod.internal` (type: string)
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_secret]` (type: string)

**environment/staging.yaml (staging overrides)** → Migration note: Staging-specific variables, loaded conditionally based on environment
- `profile_app_stack::worker_count`: `1` (type: integer)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging-not-secret-at-all` (type: string)

**profile_postgresql/data/common.yaml (PostgreSQL defaults)** → Migration note: PostgreSQL module defaults
- `profile_postgresql::version`: `15` (type: string)

**profile_postgresql/data/os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_postgresql::package_names`: `[postgresql-15, postgresql-client-15, postgresql-contrib-15]` (type: array)
- `profile_postgresql::service_name`: `postgresql` (type: string)
- `profile_postgresql::repo_location`: `http://apt.postgresql.org/pub/repos/apt/` (type: string)
- `profile_postgresql::repo_release`: `jammy-pgdg` (type: string)
- `profile_postgresql::repo_key_id`: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8` (type: string)
- `profile_postgresql::repo_key_source`: `https://www.postgresql.org/media/keys/ACCC4CF8.asc` (type: string)

### Variable Migration Summary

- **Common defaults**: 22 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 11 variables that vary by deployment environment (6 production, 5 staging)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_revision**: defined at module/environment levels, merge strategy: first
- **profile_app_stack::worker_count**: defined at module/environment levels, merge strategy: first
- **profile_app_stack::max_requests**: defined at module/environment levels, merge strategy: first
- **profile_app_stack::log_level**: defined at module/environment levels, merge strategy: first
- **profile_app_stack::db_host**: defined at module/environment levels, merge strategy: first
- **profile_app_stack::secret_key**: defined at environment levels only, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging

## Dependencies

**External module dependencies**:
- puppetlabs-vcsrepo (for Git repository management)
- puppetlabs-apt (for APT repository management)
- puppetlabs-stdlib (for utility functions)

**System package dependencies**:
- python3, python3-pip, python3-venv
- postgresql-15, postgresql-client-15, postgresql-contrib-15, libpq-dev
- prometheus-node-exporter, prometheus-pushgateway (production only)

**Service dependencies**:
- PostgreSQL service must be running before application service
- APT repository setup before PostgreSQL installation
- Python environment setup before application deployment
- Application deployment before service configuration

## Puppet Facts Used

- `$facts['environment']`: Environment name (production/staging) for conditional logic in templates and monitoring
- `fact('environment')`: Environment name used in profile::app::stack wrapper class
- `$facts['os']['family']`: OS family detection in APT module (must be 'Debian')
- `$facts['os']['name']`: OS name detection in APT module for package management

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution for log directory, rotation count, max size, and app name.

**app.env.erb**: Contains conditional logic based on environment fact. In production sets DEBUG=false and specific CORS origins, otherwise sets DEBUG=true and permissive CORS. Uses 8 variables including encrypted database URL and secret key.

**app.service.epp**: Complex systemd unit file with 11 parameters. Includes security hardening directives, proper service dependencies, and calculated timeout values. Uses EPP syntax with typed parameters.

## Checks for the Migration

**Files to verify**:
- `/opt/myapp-api` (application directory)
- `/opt/myapp-api/.env` (environment configuration)
- `/etc/systemd/system/myapp-api.service` (systemd unit)
- `/etc/logrotate.d/myapp-api` (log rotation config)
- `/var/log/myapp-api` (log directory)
- `/usr/local/bin/db-backup.sh` (backup script)
- `/usr/local/bin/app-healthcheck.sh` (health check script)

**Service endpoints to check**:
- Port 8000 (myapp-api HTTP endpoint)
- Port 5432 (PostgreSQL database, staging only)

**Templates rendered**:
- `logrotate.conf.erb` → `/etc/logrotate.d/myapp-api` (1 render)
- `app.env.erb` → `/opt/myapp-api/.env` (1 render)
- `app.service.epp` → `/etc/systemd/system/myapp-api.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status myapp-api
systemctl status postgresql  # staging only

# Instance-specific checks
curl http://localhost:8000/health  # myapp-api health check
sudo -u postgres psql -l  # database connectivity, staging only

# Configuration validation commands
/opt/myapp-api/venv/bin/python --version  # Python environment
test -f /opt/myapp-api/.env && echo "Environment file exists"
test -f /etc/systemd/system/myapp-api.service && echo "Systemd unit exists"

# Network/connectivity checks
netstat -tlnp | grep :8000  # myapp-api port binding
netstat -tlnp | grep :5432  # PostgreSQL port binding, staging only
```