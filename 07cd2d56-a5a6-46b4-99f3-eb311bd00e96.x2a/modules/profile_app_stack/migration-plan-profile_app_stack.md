---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack that deploys a Django/Flask app with PostgreSQL database, systemd service management, log rotation, and Prometheus monitoring. Configures Python environment, database setup, application deployment from Git, systemd service with gunicorn, and monitoring with virtual resources for production environments.

## Service Type and Instances

**Service Type**: Python Web Application Stack

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: gunicorn with 4 workers, sync worker class, PostgreSQL backend

## File Structure

**Manifests**:
- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/python.pp`
- `site-modules/profile_app_stack/manifests/database.pp`
- `site-modules/profile_app_stack/manifests/app.pp`
- `site-modules/profile_app_stack/manifests/service.pp`
- `site-modules/profile_app_stack/manifests/monitoring.pp`
- `site-modules/profile/manifests/app/stack.pp`
- `site-modules/role/manifests/app_server.pp`

**Templates**:
- `site-modules/profile_app_stack/templates/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/app.env.erb`
- `site-modules/profile_app_stack/templates/app.service.epp`

**Data Files**:
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`

**Dependencies**:
- `site-modules/profile_postgresql/manifests/init.pp`

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes profile::app::stack
   - Uses fact('environment') for environment-based configuration

2. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - `include profile_app_stack`

3. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera lookups
   - Builds database URL: `postgresql://myapp_user:encrypted_password@localhost:5432/myapp_db`
   - `contain profile_app_stack::python`
   - `contain profile_app_stack::database`
   - `contain profile_app_stack::app`
   - `contain profile_app_stack::service`
   - `contain profile_app_stack::monitoring`
   - Sets ordering: `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`

4. **profile_app_stack::python** (`site-modules/profile_app_stack/manifests/python.pp`):
   - `group 'myapp'` → gid: `1001`
   - `user 'myapp'` → uid: `1001`, home: `/opt/myapp`, shell: `/bin/bash`, gid: `1001`
   - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp'` (template `logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_dir=/var/log/myapp, log_rotate_count=7, log_max_size=100M, app_name=myapp

5. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - **Conditional**: `if $profile_app_stack::db_host == 'localhost'` (true for development/staging)
     - `include profile_postgresql`
       - **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
         - `contain profile_postgresql::repo`
         - `contain profile_postgresql::install`
         - `contain profile_postgresql::service`
         - Sets ordering: `profile_postgresql::repo -> profile_postgresql::install -> profile_postgresql::service`
     - `exec 'create_db_user'` → creates PostgreSQL user `myapp_user` with password
     - `exec 'create_database'` → creates database `myapp_db` owned by `myapp_user`
     - `exec 'grant_db_privileges'` → grants ALL privileges on `myapp_db` to `myapp_user`
   - `file '/usr/local/bin/db-backup.sh'` → backup script for database
   - `cron 'database_backup'` → daily backup at 2:00 AM

6. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
   - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `vcsrepo '/opt/myapp'` → source: `https://github.com/company/myapp.git`, revision: `main`, provider: `git`
   - `exec 'create_app_venv'` → creates Python virtual environment at `/opt/myapp/venv`
   - `exec 'install_requirements'` → installs packages from `requirements.txt`
   - `file '/opt/myapp/.env'` (template `app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
     - Passes: db_url=postgresql://myapp_user:encrypted_password@localhost:5432/myapp_db, app_name=myapp, app_port=8000, secret_key=encrypted_key, log_level=info, log_dir=/var/log/myapp, worker_count=4, facts['environment']=production
   - `file '/usr/local/bin/app-healthcheck.sh'` → health check script
   - `exec 'run_db_migrations'` → runs Django/Flask database migrations

7. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
   - `file '/etc/systemd/system/myapp.service'` (template `app.service.epp`) → mode: `0644`
     - Passes: app_name=myapp, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, app_port=8000, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info
   - `exec 'systemd_daemon_reload'` → reloads systemd after service file changes
   - `service 'myapp'` → ensure: `running`, enable: `true`
   - **notifies**: `file[myapp.service] ~> exec[systemd_daemon_reload] ~> service[myapp]`

8. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - `@package 'prometheus-node-exporter'` → virtual resource, ensure: `present`
   - `@service 'prometheus-node-exporter'` → virtual resource, ensure: `running`, enable: `true`
   - `@package 'prometheus-pushgateway'` → virtual resource, ensure: `present`
   - `@cron 'push_app_metrics'` → virtual resource, pushes metrics every 5 minutes
   - **Conditional**: `if $facts['environment'] == 'production'` (true in production)
     - `Package <| title == 'prometheus-node-exporter' |>` → realizes virtual package
     - `Service <| title == 'prometheus-node-exporter' |>` → realizes virtual service
     - `Package <| title == 'prometheus-pushgateway' |>` → realizes virtual package
     - `Cron <| title == 'push_app_metrics' |>` → realizes virtual cron job
   - `cron 'app_health_check'` → runs health check every minute

## Variables

**Variable Flow Summary**: 21 variables across 6 Hiera levels

### Variable Definitions

**data/common.yaml (root defaults)** → Migration note: Base defaults for all nodes
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
- `profile_app_stack::db_password`: `changeme123` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `500` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `dev-secret-key-change-in-production` (type: string)
- `profile_postgresql::version`: `14` (type: string)
- `profile_redis_cluster::redis_password`: `redis123` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `512` (type: integer)

**data/environment/production.yaml (production overrides)** → Migration note: Production-specific variables, loaded for production environment
- `profile_app_stack::app_revision`: `v1.2.3` (type: string)
- `profile_app_stack::worker_count`: `4` (type: integer)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::db_host`: `db.prod.internal` (type: string)
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_secret_key]` (type: string)

**data/environment/staging.yaml (staging overrides)** → Migration note: Staging-specific variables, loaded for staging environment
- `profile_app_stack::app_revision`: `develop` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::max_requests`: `200` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::secret_key`: `staging-secret-key` (type: string)

**site-modules/profile_app_stack/data/common.yaml (module defaults)** → Migration note: Module-level defaults, lowest priority in hierarchy
- `profile_app_stack::app_name`: `webapp` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/example/webapp.git` (type: string)
- `profile_app_stack::app_revision`: `master` (type: string)
- `profile_app_stack::app_port`: `3000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/webapp` (type: string)
- `profile_app_stack::app_user`: `webapp` (type: string)
- `profile_app_stack::app_group`: `webapp` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `webapp_db` (type: string)
- `profile_app_stack::db_user`: `webapp_user` (type: string)
- `profile_app_stack::db_password`: `ENC[PKCS7,encrypted_db_password]` (type: string)
- `profile_app_stack::worker_count`: `1` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/webapp` (type: string)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_postgresql::version`: `13` (type: string)
- `profile_postgresql::package_names`: `{debian: postgresql-13, redhat: postgresql13-server}` (type: hash)
- `profile_postgresql::service_name`: `{debian: postgresql, redhat: postgresql-13}` (type: hash)

**site-modules/profile_app_stack/data/environment/production.yaml (module production overrides)** → Migration note: Module-level production overrides
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_production_secret]` (type: string)

### Variable Migration Summary

- **Common defaults**: 22 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 2 variables that vary by operating system family (PostgreSQL packages/service names)
- **Environment-specific variables**: 11 variables that vary by deployment environment (dev, staging, prod)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 3 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_name**: defined at root common, module common, merge strategy: first
- **profile_app_stack::app_repo**: defined at root common, module common, merge strategy: first
- **profile_app_stack::app_revision**: defined at root common, production, staging, module common, merge strategy: first
- **profile_app_stack::worker_count**: defined at root common, production, staging, module common, merge strategy: first
- **profile_app_stack::secret_key**: defined at root common, production, staging, module production, merge strategy: first
- **profile_postgresql::version**: defined at root common, module common, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- Hash variables like `profile_postgresql::package_names` use implicit hash merge for OS-specific values

## Dependencies

**External module dependencies**:
- `puppetlabs-stdlib` (version: 9.7.0)
- `puppetlabs-vcsrepo` (version: 6.1.0) - Git repository management
- `puppet-systemd` (version: 7.1.0) - Systemd service management

**System package dependencies**:
- Python 3 and pip (implicit from python_packages variable)
- PostgreSQL server and client (from profile_postgresql, conditionally included when db_host == 'localhost')
- Git (for vcsrepo)
- Prometheus node exporter and pushgateway (virtual resources)

**Service dependencies**:
- PostgreSQL must be running before application starts
- Application service depends on database setup completion
- Monitoring setup runs after service is configured

## Puppet Facts Used

- `$facts['environment']`: Determines production vs non-production configuration in app.env.erb template and monitoring resource realization
- `fact('environment')`: Used in role::app_server for environment-based configuration

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution for log directory, rotation count, max size, and app name.

**app.env.erb**: Contains environment-specific conditional logic block that sets DEBUG, ALLOWED_HOSTS, and CORS_ORIGINS based on `$facts['environment']`. Uses 8 variables for database connection, application settings, and logging configuration. Logic blocks include environment-specific DEBUG/ALLOWED_HOSTS/CORS_ORIGINS settings.

**app.service.epp**: Complex systemd service template with 11 variables defining gunicorn configuration, security hardening, and service dependencies. Includes calculated timeout values and path configurations. Contains logic blocks for systemd service configuration with gunicorn command.

## Checks for the Migration

**Files to verify**:
- `/opt/myapp/.env` (environment variables)
- `/etc/systemd/system/myapp.service` (systemd unit)
- `/etc/logrotate.d/myapp` (log rotation config)
- `/usr/local/bin/db-backup.sh` (backup script)
- `/usr/local/bin/app-healthcheck.sh` (health check script)
- `/opt/myapp/venv/` (Python virtual environment)

**Service endpoints to check**:
- `http://localhost:8000` (myapp application port)
- PostgreSQL connection on port 5432
- Log files in `/var/log/myapp/`

**Templates rendered**:
- `logrotate.conf.erb` → `/etc/logrotate.d/myapp` (1 render)
- `app.env.erb` → `/opt/myapp/.env` (1 render)
- `app.service.epp` → `/etc/systemd/system/myapp.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status myapp
curl -f http://localhost:8000/health

# Instance-specific checks
sudo -u postgres psql -c "\l" | grep myapp_db
test -d /opt/myapp/venv
test -f /opt/myapp/.env

# Configuration validation commands
python3 --version
git --version
systemctl daemon-reload

# Network/connectivity checks
nc -z localhost 8000
nc -z localhost 5432
```