---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack with PostgreSQL database, systemd service management, and Prometheus monitoring. Deploys a Python Flask/Django app via Git, creates virtual environment, configures database, sets up systemd service with gunicorn, and enables monitoring in production environments.

## Service Type and Instances

**Service Type**: Python Web Application Stack

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: gunicorn WSGI server, 4 workers, PostgreSQL backend

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
site-modules/profile_app_stack/templates/app.env.erb
site-modules/profile_app_stack/templates/logrotate.conf.erb
site-modules/profile_app_stack/templates/app.service.epp
site-modules/profile_app_stack/data/common.yaml
site-modules/profile_app_stack/data/environment/production.yaml
site-modules/profile_app_stack/data/environment/staging.yaml
site-modules/profile_postgresql/data/common.yaml
site-modules/profile_postgresql/data/os/Debian.yaml
data/common.yaml
migration-dependencies/apt/manifests/init.pp
migration-dependencies/apt/manifests/update.pp
migration-dependencies/apt/manifests/setting.pp
migration-dependencies/apt/manifests/source.pp
migration-dependencies/apt/manifests/keyring.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::app_stack** (`site-modules/role/manifests/app_stack.pp`):
   - Validates kernel is Linux using `$facts['kernel']`
   - Contains `profile::app::stack`
   - Entry point role class for application stack deployment

2. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Wrapper profile class
   - Uses `$facts['environment']` for environment-specific behavior
   - Contains `profile_app_stack`

3. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera lookups: app_name=myapp, app_repo=https://github.com/company/myapp.git, app_revision=main, app_port=8000, app_dir=/opt/myapp, app_user=myapp, app_group=myapp, db_host=localhost, db_port=5432, db_name=myapp_production, db_user=myapp_user, worker_count=4, worker_class=sync, max_requests=1000, graceful_timeout=30, log_dir=/var/log/myapp, log_level=info
   - Builds database URL: `postgresql://myapp_user:encrypted_password@localhost:5432/myapp_production`
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
   - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp`, shell: `/bin/bash`, managehome: `true`
   - `file '/var/log/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
   - `file '/etc/logrotate.d/myapp'` (template `logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`

5. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - **Conditional**: if db_host == 'localhost' (true):
     - `contain profile_postgresql`
     - `exec 'create_db_user'` → command: `sudo -u postgres createuser -d -r -s myapp_user`, unless: `sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp_user'" | grep -q 1`
     - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp_user myapp_production`, unless: `sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw myapp_production`
     - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_production TO myapp_user;"`, refreshonly: `true`
   - `file '/usr/local/bin/db-backup.sh'` → ensure: `file`, owner: `root`, group: `root`, mode: `0755`
   - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `0`

6. **profile_postgresql** (`site-modules/profile_postgresql/manifests/init.pp`):
   - `contain profile_postgresql::repo`
   - `contain profile_postgresql::install`
   - `contain profile_postgresql::service`
   - Sets ordering: `profile_postgresql::repo -> profile_postgresql::install -> profile_postgresql::service`

7. **profile_postgresql::repo** (`site-modules/profile_postgresql/manifests/repo.pp`):
   - `contain apt`
   - `apt::source 'pgdg'` → location: `https://apt.postgresql.org/pub/repos/apt`, release: `jammy-pgdg`, repos: `main`, key: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8`, keyring: `/etc/apt/keyrings/pgdg.gpg`

8. **apt** (`migration-dependencies/apt/manifests/init.pp`):
   - Validates OS family is Debian
   - `contain apt::update`
   - `file '/etc/apt/sources.list'` → ensure: `file`, owner: `root`, group: `root`, mode: `0644`
   - `file '/etc/apt/sources.list.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
   - `file '/etc/apt/preferences'` → ensure: `file`, owner: `root`, group: `root`, mode: `0644`
   - `file '/etc/apt/preferences.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
   - `file '/etc/apt/apt.conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`, purge: `true`, recurse: `true`
   - `package 'gnupg'` → ensure: `present`

9. **apt::update** (`migration-dependencies/apt/manifests/update.pp`):
   - `exec 'apt_update'` → command: `/usr/bin/apt-get update`, refreshonly: `true`, timeout: `300`, tries: `3`

10. **apt::source** (`migration-dependencies/apt/manifests/source.pp`):
    - Defined type for managing APT sources
    - Creates source files in `/etc/apt/sources.list.d/`
    - Manages GPG keys via `apt::keyring`

11. **apt::keyring** (`migration-dependencies/apt/manifests/keyring.pp`):
    - Defined type for managing GPG keyrings
    - Iterations: pgdg keyring for PostgreSQL repository

12. **profile_postgresql::install** (`site-modules/profile_postgresql/manifests/install.pp`):
    - `package 'postgresql-15'` → ensure: `present`
    - `package 'postgresql-client-15'` → ensure: `present`
    - `package 'postgresql-contrib-15'` → ensure: `present`
    - `package 'libpq-dev'` → ensure: `present`

13. **profile_postgresql::service** (`site-modules/profile_postgresql/manifests/service.pp`):
    - `service 'postgresql'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`

14. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
    - `file '/opt/myapp'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
    - `vcsrepo '/opt/myapp'` → ensure: `present`, provider: `git`, source: `https://github.com/company/myapp.git`, revision: `main`, user: `myapp`
    - `exec 'create_app_venv'` → command: `python3 -m venv /opt/myapp/venv`, user: `myapp`, creates: `/opt/myapp/venv/bin/activate`
    - `exec 'install_requirements'` → command: `/opt/myapp/venv/bin/pip install -r /opt/myapp/requirements.txt`, user: `myapp`, refreshonly: `true`, subscribe: `Vcsrepo[/opt/myapp]`
    - `file '/opt/myapp/.env'` (template `app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
    - `file '/usr/local/bin/app-healthcheck.sh'` → ensure: `file`, owner: `root`, group: `root`, mode: `0755`
    - `exec 'run_db_migrations'` → command: `/opt/myapp/venv/bin/python /opt/myapp/manage.py migrate`, user: `myapp`, refreshonly: `true`, subscribe: `Vcsrepo[/opt/myapp]`

15. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
    - `file '/etc/systemd/system/myapp.service'` (template `app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
    - `exec 'systemd_daemon_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`, subscribe: `File[/etc/systemd/system/myapp.service]`
    - `service 'myapp'` → ensure: `running`, enable: `true`, subscribe: `File[/etc/systemd/system/myapp.service]`

16. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
    - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual)
    - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual)
    - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual)
    - `@cron 'push_app_metrics'` → command: `/usr/local/bin/push-metrics.sh`, user: `myapp`, minute: `*/5` (virtual)
    - **Conditional**: if facts['environment'] == 'production' (true):
      - `realize Package['prometheus-node-exporter']`
      - `realize Service['prometheus-node-exporter']`
      - `realize Package['prometheus-pushgateway']`
      - `realize Cron['push_app_metrics']`
    - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `root`, minute: `*/2`

## Variables

**Variable Flow Summary**: 29 variables across 6 Hiera levels

### Variable Definitions

**site-modules/profile_app_stack/data/common.yaml (module defaults)** → Migration note: Base defaults for all nodes
- `profile_app_stack::app_name`: `myapp` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/company/myapp.git` (type: string)
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::python_version`: `3.11` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_dev` (type: string)
- `profile_app_stack::db_user`: `myapp_user` (type: string)
- `profile_app_stack::db_password`: `changeme` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `500` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::log_max_size`: `50M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

**data/common.yaml (environment defaults)** → Migration note: Environment-wide configuration overrides
- `profile_app_stack::app_name`: `myapp` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/company/myapp.git` (type: string)
- `profile_app_stack::app_revision`: `develop` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_production` (type: string)
- `profile_app_stack::db_user`: `myapp_user` (type: string)
- `profile_app_stack::db_password`: `ENC[PKCS7,encrypted_password]` (type: string)
- `profile_app_stack::worker_count`: `4` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_secret]` (type: string)
- `profile_app_stack::python_version`: `3.11` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)
- `profile_postgresql::version`: `15` (type: string)

**site-modules/profile_app_stack/data/environment/production.yaml (production overrides)** → Migration note: Production-specific configuration
- `profile_app_stack::app_revision`: `v1.2.3` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `2000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::db_host`: `db.internal.example.com` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::secret_key`: `ENC[PKCS7,production_secret]` (type: string)

**site-modules/profile_app_stack/data/environment/staging.yaml (staging overrides)** → Migration note: Staging-specific configuration
- `profile_app_stack::app_revision`: `develop` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::max_requests`: `500` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging_secret_key_123` (type: string)

**site-modules/profile_postgresql/data/common.yaml (PostgreSQL defaults)** → Migration note: PostgreSQL module defaults
- `profile_postgresql::version`: `16` (type: string)

**site-modules/profile_postgresql/data/os/Debian.yaml (Debian-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_postgresql::package_names`: `["postgresql-%{lookup('profile_postgresql::version')}", "postgresql-client-%{lookup('profile_postgresql::version')}", "postgresql-contrib-%{lookup('profile_postgresql::version')}"]` (type: array)
- `profile_postgresql::service_name`: `postgresql` (type: string)
- `profile_postgresql::repo_location`: `https://apt.postgresql.org/pub/repos/apt` (type: string)
- `profile_postgresql::repo_release`: `%{facts.os.distro.codename}-pgdg` (type: string)
- `profile_postgresql::repo_key_id`: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8` (type: string)
- `profile_postgresql::repo_key_source`: `https://www.postgresql.org/media/keys/ACCC4CF8.asc` (type: string)

### Variable Migration Summary

- **Common defaults**: 22 variables from module defaults (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 7 variables that vary by deployment environment (production), 5 variables (staging)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_revision**: defined at module/environment/production/staging levels, merge strategy: first
- **profile_app_stack::worker_count**: defined at module/environment/production/staging levels, merge strategy: first
- **profile_app_stack::max_requests**: defined at module/environment/production/staging levels, merge strategy: first
- **profile_app_stack::log_level**: defined at module/environment/production/staging levels, merge strategy: first
- **profile_app_stack::db_host**: defined at module/environment/production/staging levels, merge strategy: first
- **profile_app_stack::db_password**: defined at module/environment levels, merge strategy: first
- **profile_app_stack::secret_key**: defined at environment/production/staging levels, merge strategy: first
- **profile_postgresql::version**: defined at module/environment levels, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Defined Types**:
- **apt::source**: Manages APT repository sources with parameters for location, release, repos, key, keyring
- **apt::keyring**: Manages GPG keyrings for APT repository authentication
- **apt::setting**: Manages APT configuration settings

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (9.7.0)
- puppetlabs-vcsrepo (6.1.0)
- puppetlabs-apt (9.4.0)

**System package dependencies**:
- python3, python3-pip, python3-venv, python3-dev, build-essential
- postgresql-15, postgresql-client-15, postgresql-contrib-15, libpq-dev
- prometheus-node-exporter, prometheus-pushgateway (production only)
- gnupg

**Service dependencies**:
- PostgreSQL service must be running before application starts
- systemd daemon-reload required after service file changes

## Puppet Facts Used

- `$facts['kernel']`: OS kernel type (Linux validation)
- `$facts['os']['family']`: OS family (Debian validation)
- `$facts['os']['name']`: OS name (Ubuntu/Debian package selection)
- `$facts['os']['distro']['codename']`: Ubuntu codename for PostgreSQL repository
- `$facts['environment']`: Environment name (production/staging behavior)
- `$facts['apt_update_last_success']`: Custom fact for APT update status

## Template Conversion Notes

**app.env.erb**: 8 variables, 1 conditional logic block for production vs non-production environment settings (DEBUG, ALLOWED_HOSTS, CORS_ORIGINS). Variables used: db_url, app_name, app_port, secret_key, log_level, log_dir, worker_count, facts['environment']. Ruby logic sets DEBUG=false, ALLOWED_HOSTS=*, CORS_ORIGINS=https://app.example.com,https://admin.example.com for production.

**logrotate.conf.erb**: 4 variables, straightforward substitution for log rotation configuration. Variables used: log_dir, log_rotate_count, log_max_size, app_name.

**app.service.epp**: 11 variables, 1 logic block for timeout calculation (graceful_timeout + 5), complex systemd service configuration with security hardening. Variables used: app_name, app_dir, app_user, app_group, app_port, worker_count, worker_class, max_requests, graceful_timeout, log_dir, log_level.

## Checks for the Migration

**Files to verify**:
- `/opt/myapp/.env` (environment variables)
- `/etc/systemd/system/myapp.service` (systemd unit)
- `/etc/logrotate.d/myapp` (log rotation)
- `/usr/local/bin/db-backup.sh` (backup script)
- `/usr/local/bin/app-healthcheck.sh` (health check script)
- `/etc/apt/sources.list.d/pgdg.list` (PostgreSQL repository)
- `/etc/apt/keyrings/pgdg.gpg` (PostgreSQL GPG keyring)

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
/usr/local/bin/app-healthcheck.sh  # myapp health script

# Configuration validation commands
python3 --version
/opt/myapp/venv/bin/python --version
sudo -u postgres psql -c "\l"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='myapp_user'"

# Network/connectivity checks
netstat -tlnp | grep :8000  # myapp port
netstat -tlnp | grep :5432  # PostgreSQL port
```