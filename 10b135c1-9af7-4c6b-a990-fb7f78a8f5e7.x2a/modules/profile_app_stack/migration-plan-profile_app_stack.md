---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack module that deploys a complete WSGI application with PostgreSQL database, systemd service management, monitoring, and log rotation. Manages the full lifecycle from Python environment setup through database provisioning, application deployment, and service orchestration with strict dependency ordering.

## Service Type and Instances

**Service Type**: Python Web Application Stack (WSGI/Gunicorn)

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: 4 workers, sync worker class, 1000 max requests, 30s graceful timeout

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
site-modules/role/manifests/app_server.pp
site-modules/profile/manifests/app/stack.pp
site-modules/profile_app_stack/templates/logrotate.conf.erb
site-modules/profile_app_stack/templates/app.env.erb
site-modules/profile_app_stack/templates/app.service.epp
site-modules/profile_app_stack/data/common.yaml
site-modules/profile_app_stack/data/environment/production.yaml
site-modules/profile_app_stack/data/environment/staging.yaml
migration-dependencies/apt/manifests/init.pp
migration-dependencies/apt/manifests/source.pp
migration-dependencies/apt/manifests/setting.pp
migration-dependencies/apt/manifests/update.pp
migration-dependencies/apt/manifests/keyring.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes profile::app::stack
   - Sets up the complete application server role

2. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Wrapper class that includes profile_app_stack
   - Uses `fact('environment')` for environment-specific configuration

3. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera lookups: app_name=myapp, app_repo=https://github.com/company/myapp.git, app_revision=main, app_port=8000, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, db_host=localhost, db_port=5432, db_name=myapp_db, db_user=myapp_user, db_password=encrypted, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info, secret_key=encrypted
   - Builds database URL using custom function: `postgresql://myapp_user:encrypted@localhost:5432/myapp_db`
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
   - `package 'libpq-dev'` → ensure: `present`
   - `group 'myapp'` → ensure: `present`, gid: `1001`
   - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp`, shell: `/bin/bash`, managehome: `true`
   - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp'` (template `site-modules/profile_app_stack/templates/logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_dir=/var/log/myapp, log_rotate_count=7, log_max_size=100M, app_name=myapp

5. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - **Conditional**: if db_host == 'localhost' (TRUE):
     - `contain profile_postgresql`
       - **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
         - `contain profile_postgresql::repo`
         - `contain profile_postgresql::install`
         - `contain profile_postgresql::service`
         - Sets ordering: `profile_postgresql::repo -> profile_postgresql::install -> profile_postgresql::service`
       - **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
         - `contain apt`
           - **apt** (`migration-dependencies/apt/manifests/init.pp`):
             - Validates OS family is Debian
             - `contain apt::update`
             - Manages APT configuration files and directories
             - `apt::source 'pgdg'` → location: `http://apt.postgresql.org/pub/repos/apt/`, release: `jammy-pgdg`, repos: `main`, key: PostgreSQL signing key
       - **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
         - `package 'postgresql-14'` → ensure: `present`
         - `package 'postgresql-client-14'` → ensure: `present`
         - `package 'postgresql-contrib-14'` → ensure: `present`
         - `package 'libpq-dev'` → ensure: `present`
       - **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
         - `service 'postgresql'` → ensure: `running`, enable: `true`
     - `exec 'create_db_user'` → command: `sudo -u postgres createuser -d -r -s myapp_user`, creates: `/var/lib/postgresql/.myapp_user_created`
     - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp_user myapp_db`, creates: `/var/lib/postgresql/.myapp_db_created`
     - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp_user;"`, refreshonly: `true`
   - `file '/usr/local/bin/db-backup.sh'` → owner: `root`, group: `root`, mode: `0755`, content: database backup script
   - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `0`

6. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
   - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp'` → ensure: `present`, provider: `git`, source: `https://github.com/company/myapp.git`, revision: `main`, user: `myapp`
   - `exec 'create_app_venv'` → command: `python3 -m venv /opt/myapp/venv`, user: `myapp`, creates: `/opt/myapp/venv/bin/python`
   - `exec 'install_requirements'` → command: `/opt/myapp/venv/bin/pip install -r /opt/myapp/requirements.txt`, user: `myapp`, refreshonly: `true`
   - `file '/opt/myapp/.env'` (template `site-modules/profile_app_stack/templates/app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
     - Passes: db_url=postgresql://myapp_user:encrypted@localhost:5432/myapp_db, app_name=myapp, app_port=8000, secret_key=encrypted, log_level=info, log_dir=/var/log/myapp, worker_count=4, facts['environment']=production
   - `file '/usr/local/bin/app-healthcheck.sh'` → owner: `root`, group: `root`, mode: `0755`, content: health check script
   - `exec 'run_db_migrations'` → command: `/opt/myapp/venv/bin/python /opt/myapp/manage.py migrate`, user: `myapp`, refreshonly: `true`

7. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
   - `file '/etc/systemd/system/myapp.service'` (template `site-modules/profile_app_stack/templates/app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: app_name=myapp, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, app_port=8000, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info
   - `exec 'systemd_daemon_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'myapp'` → ensure: `running`, enable: `true`, hasrestart: `true`, hasstatus: `true`
   - **notifies**: `file[myapp.service] ~> exec[systemd_daemon_reload] ~> service[myapp]`

8. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual)
   - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual)
   - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual)
   - `@cron 'push_app_metrics'` → command: `/usr/local/bin/push-metrics.sh`, user: `myapp`, minute: `*/5` (virtual)
   - **Conditional**: if facts['environment'] == 'production' (TRUE):
     - Realizes all virtual monitoring resources via collectors: `<<| tag == 'monitoring' |>>`
   - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `root`, minute: `*/2`

## Variables

**Variable Flow Summary**: 21 variables across 3 Hiera levels

### Variable Definitions

**site-modules/profile_app_stack/data/common.yaml (module defaults)** → Migration note: Base defaults for all nodes
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
- `profile_app_stack::db_password`: `ENC[PKCS7,encrypted_password]` (type: string)
- `profile_app_stack::worker_count`: `4` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_secret]` (type: string)

**site-modules/profile_app_stack/data/environment/production.yaml (production overrides)** → Migration note: Production-specific variables, loaded when environment=production
- `profile_app_stack::app_revision`: `v1.2.3` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `2000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::db_host`: `db.prod.internal` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_prod_secret]` (type: string)

**site-modules/profile_app_stack/data/environment/staging.yaml (staging overrides)** → Migration note: Staging-specific variables, loaded when environment=staging
- `profile_app_stack::app_revision`: `staging` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::max_requests`: `500` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `db.staging.internal` (type: string)
- `profile_app_stack::secret_key`: `staging-secret-key` (type: string)

### Variable Migration Summary

- **Common defaults**: 21 variables from module common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables
- **Environment-specific variables**: 7 variables for production, 6 variables for staging
- **Host-specific variables**: 0 variables
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_revision**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::worker_count**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::max_requests**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::log_level**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::db_host**: defined at common, production, staging, merge strategy: first
- **profile_app_stack::secret_key**: defined at common, production, staging, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (9.7.0)
- puppetlabs-vcsrepo (6.1.0)
- puppetlabs-apt (9.4.0)

**System package dependencies**:
- python3, python3-pip, python3-venv, python3-dev
- build-essential, libpq-dev
- postgresql-14, postgresql-client-14, postgresql-contrib-14
- prometheus-node-exporter, prometheus-pushgateway

**Service dependencies**:
- PostgreSQL service must be running before application starts
- Systemd daemon-reload required after service file changes
- Application service restart triggered by configuration changes

## Puppet Facts Used

- `$facts['os']['family']`: OS family detection for APT module compatibility
- `$facts['os']['name']`: OS name for package management decisions
- `$facts['environment']`: Environment detection for conditional monitoring and application configuration
- `$facts['apt_update_last_success']`: APT update timestamp tracking
- `fact('environment')`: Environment detection in profile::app::stack wrapper class

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution for log directory, rotation count, max size, and app name.

**app.env.erb**: Contains 1 conditional logic block for environment-specific settings (DEBUG, ALLOWED_HOSTS, CORS_ORIGINS). Uses facts['environment'] to determine production vs non-production configuration with if/else branching.

**app.service.epp**: EPP template with parameter validation and 1 logic block. Complex systemd unit file with security hardening, resource limits, and logging configuration. Uses arithmetic expression for timeout calculation (graceful_timeout + 5).

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Virtual Resources**: 4 monitoring-related virtual resources (@package prometheus-node-exporter, @service prometheus-node-exporter, @package prometheus-pushgateway, @cron push_app_metrics) that are conditionally realized in production environments.

**Resource Collectors**: Uses `<<| tag == 'monitoring' |>>` collectors to realize virtual monitoring resources when facts['environment'] == 'production'. Migration notes: Requires cross-node resource sharing for monitoring infrastructure coordination.

## Checks for the Migration

**Files to verify**:
- `/opt/myapp` (application directory)
- `/opt/myapp/.env` (environment configuration)
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

# Instance-specific checks
curl -f http://localhost:8000/health
sudo -u postgres psql -c "\l"

# Configuration validation commands
python3 /opt/myapp/manage.py check
/opt/myapp/venv/bin/python -c "import django; print('Django OK')"

# Network/connectivity checks
nc -zv localhost 8000
nc -zv localhost 5432
```