---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: `profile_app_stack` deploys the `test-app` Python/Gunicorn application, including Python packages, a system user, Git checkout, virtualenv, environment file, log rotation, database configuration, backups, migrations, health checks, systemd service management, and optional production Prometheus monitoring. The role also conditionally manages Chrony and rsyslog on Linux. Common application values are overridden by production and staging Hiera data. Database passwords, application secret keys, generated database URLs, and any other credential-bearing values must be migrated to Ansible Vault or an external secret provider.

## Service Type and Instances

**Service Type**: Python web application / Gunicorn application server with optional local PostgreSQL and production Prometheus monitoring.

**Configured Instances**:

- **`test-app`**: Python/Gunicorn application server
  - Repository: `file:///tmp/test-app-repo`
  - Revision: `master` in common and staging; `v2.4.1` in production
  - Location/Path: `/opt/test-app`
  - User/group: `appuser` / `appuser`
  - Port/Socket: `0.0.0.0:8000`
  - Database host: `localhost` in common and staging; `db-primary.prod.internal` in production
  - Database port: `5432`
  - Database: `testdb`
  - Database user: `testuser`
  - Worker count: `2` common, `1` staging, `8` production
  - Worker class: `sync`
  - Maximum requests: `1000` common, `100` staging, `5000` production
  - Graceful timeout: `30` seconds
  - Log directory: `/var/log/test-app`
  - Log level: `info` common, `debug` staging, `warning` production
  - Service unit: `/etc/systemd/system/test-app.service`
  - Health endpoint: `http://localhost:8000/health`

- **`postgresql-local`**: Optional local PostgreSQL instance for common and staging
  - Activation: `db_host == localhost`
  - Port/Socket: PostgreSQL port `5432`
  - Database: `testdb`
  - Database user: `testuser`
  - Production behavior: not created; production uses `db-primary.prod.internal`

- **`prometheus-node-exporter`**: Production-only node metrics service
  - Activation: Puppet environment is `production`
  - Service: enabled and running

- **`prometheus-pushgateway`**: Production-only metrics destination
  - Activation: Puppet environment is `production`
  - Metrics schedule: every five minutes

## File Structure

```text
### Manifests

- site-modules/role/manifests/app_stack.pp
- site-modules/profile/manifests/base/base.pp
- site-modules/profile/manifests/app/stack.pp
- site-modules/profile_app_stack/manifests/init.pp
- site-modules/profile_app_stack/manifests/python.pp
- site-modules/profile_app_stack/manifests/database.pp
- site-modules/profile_app_stack/manifests/app.pp
- site-modules/profile_app_stack/manifests/service.pp
- site-modules/profile_app_stack/manifests/monitoring.pp
- site-modules/profile_postgresql/manifests/init.pp
- site-modules/profile_postgresql/manifests/repo.pp
- site-modules/profile_postgresql/manifests/install.pp
- site-modules/profile_postgresql/manifests/service.pp
- migration-dependencies/apt/manifests/init.pp
- migration-dependencies/apt/manifests/keyring.pp
- migration-dependencies/apt/manifests/pin.pp
- migration-dependencies/apt/manifests/setting.pp
- migration-dependencies/apt/manifests/source.pp
- migration-dependencies/apt/manifests/update.pp

### Templates

- site-modules/profile_app_stack/templates/logrotate.conf.erb
- site-modules/profile_app_stack/templates/app.env.erb
- site-modules/profile_app_stack/templates/app.service.epp

### Hiera data

- data/common.yaml
- data/environment/production.yaml
- data/environment/staging.yaml
- site-modules/profile_app_stack/data/common.yaml
- site-modules/profile_app_stack/data/environment/production.yaml
- site-modules/profile_app_stack/data/environment/staging.yaml

### Referenced source files not present in the supplied directory listing

- puppet:///modules/profile_app_stack/backup.sh
- puppet:///modules/profile_app_stack/healthcheck.sh
```

## Module Explanation

The module performs operations in this order:

1. **`role::app_stack`** (`site-modules/role/manifests/app_stack.pp`):
   - Runs Linux-only logic when `facts['kernel'].downcase == 'linux'`.
   - Contains an `exec[None]` whose command was not exposed; inspect the original role manifest before migration.
   - Includes `profile::base::base`.
   - Includes `profile::app::stack`.
   - Enforces `Class['::profile::base::base'] -> Class['::profile::app::stack']`.

2. **`profile::base::base`** (`site-modules/profile/manifests/base/base.pp`):
   - Includes `base_utils` when `$manage_utils` is true; implementation was not supplied.
   - Installs and starts `chrony`/`chronyd` when `$manage_ntp` is true and `facts['kernel'] == 'Linux'`.
   - Installs and starts `rsyslog` when `$manage_syslog` is true and `facts['kernel'] == 'Linux'`.
   - Preserve `$manage_utils`, `$manage_ntp`, and `$manage_syslog` as Ansible role booleans.

3. **`profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`):
   - Includes `profile_app_stack`.
   - References `fact('environment')`.
   - Executes the application phases in this order:
     1. `profile_app_stack::python`
     2. `profile_app_stack::database`
     3. `profile_app_stack::app`
     4. `profile_app_stack::service`
     5. `profile_app_stack::monitoring`
   - Enforces Python before database, database before application, application notification to service, and service before monitoring.

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `python3-dev`, `git`, and `build-essential`.
   - Creates system group `appuser`.
   - Creates system user `appuser` with home `/opt/test-app`, shell `/bin/bash`, and `managehome: false`.
   - Creates `/var/log/test-app` owned by `appuser:appuser`, mode `0755`.
   - Deploys `/etc/logrotate.d/test-app` from `site-modules/profile_app_stack/templates/logrotate.conf.erb`.
   - Renders the logrotate template once with `log_dir`, `log_rotate_count`, `log_max_size`, and `app_name`.

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Uses `db_host` to select the database branch.
   - In production, where `db_host` is `db-primary.prod.internal`, does not include `profile_postgresql` and creates no local PostgreSQL resources.
   - In common and staging, where `db_host` is `localhost`, includes `profile_postgresql`.
   - Executes `profile_postgresql::repo`, then `profile_postgresql::install`, then `profile_postgresql::service`.
   - `profile_postgresql::repo` (`site-modules/profile_postgresql/manifests/repo.pp`) includes `apt`, declares `apt::source 'pgdg'`, and evaluates APT update, source, setting, keyring, pin, proxy, and platform conditionals.
   - The exact PostgreSQL APT URL, release, signing key, package names, and service name were not exposed and must be confirmed.
   - `profile_postgresql::install` (`site-modules/profile_postgresql/manifests/install.pp`) installs the profile PostgreSQL package list and `libpq-dev`.
   - `profile_postgresql::service` (`site-modules/profile_postgresql/manifests/service.pp`) manages the profile-specific PostgreSQL service.
   - Creates the `testuser` role, `testdb` database, and database privileges. Replace the Puppet shell commands with Ansible PostgreSQL modules where possible.
   - Creates `/usr/local/bin/db-backup.sh` from the missing `puppet:///modules/profile_app_stack/backup.sh` source, owned by `root:appuser`, mode `0750`.
   - Schedules `/usr/local/bin/db-backup.sh testdb localhost` at 02:30 in common/staging and `/usr/local/bin/db-backup.sh testdb db-primary.prod.internal` at 02:30 in production.
   - Vault the database password and use `no_log: true` for credential-bearing tasks.

6. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`):
   - Creates `/opt/test-app`, owned by `appuser:appuser`, mode `0755`.
   - Checks out `file:///tmp/test-app-repo` using Git and the effective revision: `master` common, `main` staging, and `v2.4.1` production.
   - Creates `/opt/test-app/venv` using `python3 -m venv`.
   - Installs `/opt/test-app/requirements.txt` into the virtualenv.
   - The `$pip_packages.each` loop runs zero times because the effective control-repository value is `[]`; therefore no package-specific loop resources are created.
   - If future data supplies packages, use one Ansible `pip` task per package or a list task. The module-default package names are `uvicorn`, `gunicorn`, and `psycopg2-binary`.
   - Deploys `/opt/test-app/.env` from `site-modules/profile_app_stack/templates/app.env.erb`, once, mode `0600`, owned by `appuser:appuser`.
   - Builds `DATABASE_URL` through the unresolved `profile_app_stack::app_db_url` helper. Confirm its exact URL-encoding behavior before migration.
   - Deploys `/usr/local/bin/app-healthcheck.sh` from the missing `puppet:///modules/profile_app_stack/healthcheck.sh` source, owned by `root:root`, mode `0755`.
   - Runs Alembic migrations when `/opt/test-app/migrations/env.py` exists and the repository revision changes.
   - Migration command: `/opt/test-app/venv/bin/python -m alembic upgrade head`, executed as `appuser` from `/opt/test-app`.

7. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`):
   - Deploys `/etc/systemd/system/test-app.service` from `site-modules/profile_app_stack/templates/app.service.epp`, once, mode `0644`.
   - Reloads systemd with `systemctl daemon-reload` when the unit changes.
   - Enables and starts the `test-app` service.
   - Runs Gunicorn from `/opt/test-app/venv/bin/gunicorn`.
   - Binds to `0.0.0.0:8000`, uses `sync` workers, environment-specific worker counts and maximum requests, `--max-requests-jitter 50`, graceful timeout `30`, and log level from Hiera.
   - Writes access, error, stdout, and stderr logs under `/var/log/test-app`.
   - Uses `After=network.target postgresql.service`, `Wants=postgresql.service`, `NoNewPrivileges=true`, `ProtectSystem=strict`, `ProtectHome=true`, `ReadWritePaths=/opt/test-app /var/log/test-app`, and `PrivateTmp=true`.
   - Restarts on failure with `RestartSec=5` and `TimeoutStopSec=35`.

8. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Defines virtual `prometheus-node-exporter` package and service resources.
   - Defines virtual `prometheus-pushgateway` package resource.
   - Defines the `push_app_metrics` cron resource at every five minutes as `appuser`.
   - Realizes all four virtual resources only when `facts['environment'] == 'production'`.
   - Creates the always-active `app_health_check` cron job at every two minutes as `root`, invoking `/usr/local/bin/app-healthcheck.sh http://localhost:8000/health`.

## Variables

**Variable Flow Summary**: 22 variables are defined at each of the control-repository common and module-common levels, with production and staging overrides. Scalar values use first-value selection rather than deep merging. The effective control-repository common data overrides module-common values for most application settings.

### Variable Definitions

#### `data/common.yaml` — control-repository common level

Migration note: Base defaults for all nodes. Sensitive values must be moved to Ansible Vault or an external secret provider.

- `profile_app_stack::app_name`: `test-app` (type: string)
- `profile_app_stack::app_repo`: `file:///tmp/test-app-repo` (type: string)
- `profile_app_stack::app_revision`: `master` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/test-app` (type: string)
- `profile_app_stack::app_user`: `appuser` (type: string)
- `profile_app_stack::app_group`: `appuser` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `testdb` (type: string)
- `profile_app_stack::db_user`: `testuser` (type: string)
- `profile_app_stack::db_password`: `test-db-password` (type: string; plaintext in supplied data)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/test-app` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `test-secret-key` (type: string; sensitive)
- `profile_app_stack::python_version`: `python3` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)
- `profile_postgresql::version`: `15` (type: integer)

#### `site-modules/profile_app_stack/data/common.yaml` — module common level

Migration note: Module defaults used when no higher-priority control-repository value exists.

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
- `profile_app_stack::db_password`: `ENC[PKCS7,...]` (type: encrypted string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `uvicorn.workers.UvicornWorker` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp-api` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

#### `site-modules/profile_app_stack/data/environment/production.yaml` — production level

Migration note: Production-specific overrides. Store encrypted values in Ansible Vault or an external secret provider.

- `profile_app_stack::app_revision`: `v2.4.1` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `5000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::db_host`: `db-primary.prod.internal` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::secret_key`: `ENC[PKCS7,...]` (type: encrypted string)

#### `site-modules/profile_app_stack/data/environment/staging.yaml` — staging level

Migration note: Staging-specific overrides. The plaintext secret must be replaced with a vaulted value.

- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::worker_count`: `1` (type: integer)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging-not-secret-at-all` (type: string; sensitive)

#### `data/environment/production.yaml`

Migration note: No relevant `profile_app_stack` or `profile_postgresql` values were found.

#### `data/environment/staging.yaml`

Migration note: No relevant `profile_app_stack` or `profile_postgresql` values were found.

### Variable Migration Summary

- **Control-repository common defaults**: 22 variables from `data/common.yaml`.
- **Module common defaults**: 22 variables from `site-modules/profile_app_stack/data/common.yaml`.
- **Production-specific variables**: 7 overrides.
- **Staging-specific variables**: 6 overrides.
- **Encrypted variables**: 2 supplied encrypted values: module-common database password and production application secret key.
- **Plaintext sensitive values requiring Vault migration**:
  - Control-repository database password.
  - Control-repository common secret key.
  - Staging secret key.
  - Generated `DATABASE_URL`, which contains the database password.
- **Environment variables**: production and staging values must be represented as inventory or group variables.
- **Host-specific variables**: none supplied.

### Cross-Level Overrides

- `app_name`: module common and control common; effective value `test-app`.
- `app_repo`: module common and control common; effective value `file:///tmp/test-app-repo`.
- `app_revision`: module common, control common, production, and staging; effective production value `v2.4.1`, staging value `main`.
- `app_port`: module common and control common; effective value `8000`.
- `app_dir`: module common and control common; effective value `/opt/test-app`.
- `app_user`: module common and control common; effective value `appuser`.
- `app_group`: module common and control common; effective value `appuser`.
- `db_host`: module common, control common, production, and staging; effective production value `db-primary.prod.internal`, staging value `localhost`.
- `db_port`: module common, control common, and production; effective value `5432`.
- `db_name`: module common and control common; effective value `testdb`.
- `db_user`: module common and control common; effective value `testuser`.
- `db_password`: module common encrypted and control common plaintext; effective control value is `test-db-password`, which must be vaulted.
- `worker_count`: module common, control common, production, and staging; effective values are `8` production, `1` staging, and `2` common.
- `worker_class`: module common and control common; effective value `sync`.
- `max_requests`: module common, control common, production, and staging; effective values are `5000` production, `100` staging, and `1000` common.
- `graceful_timeout`: module common and control common; effective value `30`.
- `log_dir`: module common and control common; effective value `/var/log/test-app`.
- `log_level`: module common, control common, production, and staging; effective values are `warning` production, `debug` staging, and `info` common.
- `secret_key`: control common, production, and staging; environment values override common values.
- `python_version`: module common and control common; effective value `python3`.
- `pip_packages`: module common and control common; effective value `[]`, with no array merge.
- `log_max_size`: module common only; effective value `100M`.
- `log_rotate_count`: module common only; effective value `7`.

### Merge Strategy Notes

- Scalar variables use `first` lookup behavior; the first value found wins.
- `pip_packages` uses complete-value selection and is not merged between Hiera levels.
- No variables were identified as using `hash` or `deep` merge.
- Ansible group and host variable precedence must reproduce the effective production, staging, and common values.

## Custom Types and Providers

No custom Puppet types, providers, facts, or functions were detected in the supplied custom-component analysis.

The manifest references `profile_app_stack::app_db_url`, an unresolved Puppet helper/function reference. Its implementation was not supplied. Before migration, confirm whether it URL-encodes the username, password, host, database name, or other components, especially reserved characters in passwords. The Ansible implementation must reproduce the confirmed behavior exactly and must not expose the resulting URL in logs.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.7.0`
- `puppetlabs-concat` `9.0.2`
- `puppetlabs-firewall` `8.1.3`
- `puppetlabs-vcsrepo` `6.1.0`
- `puppet-redis` `11.0.0`
- `puppet-systemd` `7.1.0`
- `puppetlabs-inifile` `6.1.1`
- `puppetlabs-apt` `9.4.0`

Directly relevant dependencies are `puppetlabs-vcsrepo`, `puppetlabs-apt`, and standard package/service functionality.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `python3-dev`
- `git`
- `build-essential`
- `libpq-dev`
- PostgreSQL packages from `profile_postgresql`; exact names require confirmation.
- `chrony`, conditional.
- `rsyslog`, conditional.
- `prometheus-node-exporter`, production only.
- `prometheus-pushgateway`, production only.
- `gnupg`, conditionally through the APT dependency module on Debian/Ubuntu.

**Service dependencies**:

- Base profile before application profile.
- Python setup before database setup.
- Database setup before application deployment.
- Application changes notify the service phase.
- Systemd unit changes trigger daemon reload.
- The application service requires its unit file and daemon reload.
- Service phase before monitoring.
- The systemd unit declares `After=network.target postgresql.service` and `Wants=postgresql.service`.

## Puppet Facts Used

- `facts['kernel']`: determines Linux-only role logic and Chrony/rsyslog management.
- `facts['os']['family']`: distinguishes Debian-family systems for APT behavior.
- `facts['os']['name']`: controls `gnupg` installation for Debian and Ubuntu.
- `facts['apt_update_last_success']`: determines whether an APT update is due.
- `facts['environment']`: controls production monitoring realization and production versus non-production `.env` values.
- `fact('environment')`: referenced by `profile::app::stack`.

## Template Conversion Notes

### `site-modules/profile_app_stack/templates/logrotate.conf.erb`

- Destination: `/etc/logrotate.d/test-app`
- Render count: once.
- Variables: `log_dir`, `log_rotate_count`, `log_max_size`, and `app_name`.
- No loops or conditional branches.
- Behavior: daily rotation, seven retained files, compression with delayed compression, `100M` maximum size, and post-rotation `systemctl reload test-app 2>/dev/null || true`.

### `site-modules/profile_app_stack/templates/app.env.erb`

- Destination: `/opt/test-app/.env`
- Render count: once.
- Variables: `db_url`, `app_name`, `app_port`, `secret_key`, `log_level`, `log_dir`, `worker_count`, and `facts['environment']`.
- Production values: `DEBUG=false`, `ALLOWED_HOSTS=*`, and `CORS_ORIGINS=https://app.example.com,https://admin.example.com`.
- Non-production values: `DEBUG=true`, `ALLOWED_HOSTS=*`, and `CORS_ORIGINS=*`.
- Preserve mode `0600`.
- Render using protected Ansible variables and `no_log: true`.

### `site-modules/profile_app_stack/templates/app.service.epp`

- Destination: `/etc/systemd/system/test-app.service`
- Render count: once.
- Variables: `app_name`, `app_dir`, `app_user`, `app_group`, `app_port`, `worker_count`, `worker_class`, `max_requests`, `graceful_timeout`, `log_dir`, and `log_level`.
- Logic block 1: computes `TimeoutStopSec` as `graceful_timeout + 5`, resulting in `35`.
- Logic block 2: structured validation identified a second logic block, but its exact expression was not included in the supplied template analysis. Inspect the original EPP template and document the expression before conversion; the Ansible template must preserve it.
- The Ansible template must notify a systemd daemon-reload handler and restart or reload `test-app` when required.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/app_stack.pp`
- `site-modules/profile/manifests/base/base.pp`
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
- `migration-dependencies/apt/manifests/init.pp`
- `migration-dependencies/apt/manifests/keyring.pp`
- `migration-dependencies/apt/manifests/pin.pp`
- `migration-dependencies/apt/manifests/setting.pp`
- `migration-dependencies/apt/manifests/source.pp`
- `migration-dependencies/apt/manifests/update.pp`
- `site-modules/profile_app_stack/templates/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/app.env.erb`
- `site-modules/profile_app_stack/templates/app.service.epp`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `/usr/local/bin/db-backup.sh`
- `/usr/local/bin/app-healthcheck.sh`
- `/opt/test-app/requirements.txt`
- `/opt/test-app/migrations/env.py`, when migrations are present

**Service endpoints to check**:

- `test-app`: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432` in common/staging
- PostgreSQL: `db-primary.prod.internal:5432` in production
- Health endpoint: `http://localhost:8000/health`
- Prometheus metrics push schedule: every five minutes in production

**Templates rendered**:

- `logrotate.conf.erb`: 1 render to `/etc/logrotate.d/test-app`
- `app.env.erb`: 1 render to `/opt/test-app/.env`
- `app.service.epp`: 1 render to `/etc/systemd/system/test-app.service`

## Pre-flight checks:

```bash
# Confirm operating system and Puppet fact equivalents
uname -s
ansible all -m setup -a 'filter=ansible_kernel'
ansible all -m setup -a 'filter=ansible_os_family'
ansible all -m setup -a 'filter=ansible_distribution'
ansible all -m setup -a 'filter=ansible_env'

# Confirm required packages and users
command -v python3
command -v git
id appuser
getent group appuser

# Verify the test-app instance individually
test -d /opt/test-app
test -x /opt/test-app/venv/bin/gunicorn
test -f /opt/test-app/.env
stat -c '%U:%G %a' /opt/test-app /opt/test-app/.env /var/log/test-app
systemctl is-enabled test-app
systemctl is-active test-app
systemctl status test-app --no-pager
curl --fail http://localhost:8000/health

# Validate test-app configuration
systemd-analyze verify /etc/systemd/system/test-app.service
systemctl daemon-reload
test -f /opt/test-app/requirements.txt
test -f /opt/test-app/migrations/env.py || true
/opt/test-app/venv/bin/python -m pip check
/opt/test-app/venv/bin/python -m alembic current

# Verify local PostgreSQL instance in common/staging
systemctl is-enabled postgresql
systemctl is-active postgresql
pg_isready -h localhost -p 5432
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='testuser'"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_catalog.pg_database WHERE datname='testdb'"
sudo -u postgres psql -tAc "SELECT has_database_privilege('testuser', 'testdb', 'CREATE')"

# Verify production database connectivity
pg_isready -h db-primary.prod.internal -p 5432
# Do not print DATABASE_URL or database passwords.

# Verify backup and health-check scripts
test -x /usr/local/bin/db-backup.sh
test -x /usr/local/bin/app-healthcheck.sh
systemctl list-timers --all
crontab -l -u root
crontab -l -u appuser

# Verify log rotation
test -f /etc/logrotate.d/test-app
logrotate -d /etc/logrotate.d/test-app

# Verify production-only monitoring
systemctl is-enabled prometheus-node-exporter
systemctl is-active prometheus-node-exporter
systemctl is-enabled prometheus-pushgateway || true
crontab -l -u appuser | grep 'push-metrics'
```