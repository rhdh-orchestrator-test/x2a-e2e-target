---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: `profile_app_stack` deploys the `test-app` Python application from Git, creates the `appuser` identity and virtual environment, installs system and application dependencies, optionally provisions a local PostgreSQL database, renders environment, systemd, and log-rotation configuration, runs conditional database migrations, manages backups and health checks, and enables Prometheus monitoring only in production. The effective control-repository defaults use `/opt/test-app`, port `8000`, PostgreSQL database `testdb`, two synchronous workers, and `/var/log/test-app`. Production overrides the Git revision, worker count, request limit, log level, database host, and secret; staging overrides the revision, worker count, request limit, log level, and secret.

## Service Type and Instances

**Service Type**: Python web application managed by systemd, with optional local PostgreSQL provisioning and Prometheus monitoring.

**Configured Instances**:

- **`test-app`**
  - Purpose: Default application instance.
  - Repository: `file:///tmp/test-app-repo`
  - Revision: `master`
  - Location/Path: `/opt/test-app`
  - User/Group: `appuser:appuser`
  - HTTP Port: `8000`
  - Database: `testdb`
  - Database Host/Port: `localhost:5432`
  - Database User: `testuser`
  - Workers: `2`
  - Worker Class: `sync`
  - Maximum Requests: `1000`
  - Graceful Timeout: `30`
  - Log Directory: `/var/log/test-app`
  - Log Level: `info`
  - Service Unit: `/etc/systemd/system/test-app.service`

- **`test-app` production configuration**
  - Revision: `v2.4.1`
  - Workers: `8`
  - Maximum Requests: `5000`
  - Log Level: `warning`
  - Database Host/Port: `db-primary.prod.internal:5432`
  - Secret Key: Hiera-eyaml encrypted value
  - Monitoring: Prometheus node exporter and pushgateway are realized.
  - Database mode: Remote database; local PostgreSQL provisioning is not active.

- **`test-app` staging configuration**
  - Revision: `main`
  - Workers: `1`
  - Maximum Requests: `100`
  - Log Level: `debug`
  - Database Host/Port: `localhost:5432`
  - Secret Key: `staging-not-secret-at-all`; migrate to Ansible Vault.
  - Monitoring: Prometheus virtual resources are not realized.
  - Database mode: Local PostgreSQL provisioning is active.

## File Structure

### Manifests

- `site-modules/role/manifests/app_stack.pp`
- `site-modules/profile/manifests/app/stack.pp`
- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/python.pp`
- `site-modules/profile_app_stack/manifests/database.pp`
- `site-modules/profile_app_stack/manifests/app.pp`
- `site-modules/profile_app_stack/manifests/service.pp`
- `site-modules/profile_app_stack/manifests/monitoring.pp`

### Templates and source files referenced by the execution tree

- `profile_app_stack/logrotate.conf.erb`
- `profile_app_stack/app.env.erb`
- `profile_app_stack/app.service.epp`
- `puppet:///modules/profile_app_stack/backup.sh`
- `puppet:///modules/profile_app_stack/healthcheck.sh`

### Hiera data

- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`

## Module Explanation

The module performs operations in this order:

1. **`role::app_stack`** (`site-modules/role/manifests/app_stack.pp`):
   - Includes `profile::base::base`.
   - Contains `profile::app::stack`.
   - On Linux, sets the executable default `PATH` to `/usr/bin:/bin:/usr/sbin:/sbin`; it does not create a named executable resource.
   - Uses `$facts['kernel']` for the Linux conditional.
   - Orders `Class['::profile::base::base']` before `Class['::profile::app::stack']`.

2. **`profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`):
   - Declares `class { 'profile_app_stack': }`.
   - Defines `environment_name`, defaulting to `fact('environment')`; this parameter is not otherwise used by the supplied execution tree.
   - Delegates application-stack resources to `profile_app_stack`.
   - Uses `fact('environment')`.

3. **`profile_app_stack`** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Resolves application, database, worker, logging, Python, and secret parameters from Hiera.
   - Computes `db_url` with `profile_app_stack::app_db_url(db_user, db_password, db_host, db_port, db_name)`.
   - The function implementation was not supplied. Migration is blocked pending confirmation of its exact URL syntax, escaping, and encoding behavior.
   - Expected logical URL components are user `testuser`, the database password, host `localhost` or the environment-specific host, port `5432`, and database `testdb`.
   - Contains `profile_app_stack::python`, `profile_app_stack::database`, `profile_app_stack::app`, `profile_app_stack::service`, and `profile_app_stack::monitoring`.
   - Orders Python before database, database before application, application changes to notify service, and service before monitoring.
   - Implement the application-to-service notification with Ansible handlers and explicit task ordering.

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `python3-dev`, `git`, and `build-essential`.
   - Creates system group `appuser`.
   - Creates system user `appuser` with group `appuser`, home `/opt/test-app`, shell `/bin/bash`, and `managehome: false`.
   - Creates `/var/log/test-app` owned by `appuser:appuser` with mode `0755`.
   - Renders `/etc/logrotate.d/test-app` from `profile_app_stack/logrotate.conf.erb`, once, owned by `root:root` with mode `0644`.
   - Uses `python_version: python3`, `pip_packages: []`, `log_max_size: 100M`, and `log_rotate_count: 7`.
   - The effective package loop expands to:
     - `python3` → installed
     - `python3-pip` → installed
     - `python3-venv` → installed
     - `python3-dev` → installed
     - `git` → installed
     - `build-essential` → installed

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Activates local PostgreSQL provisioning when `db_host == localhost`.
   - Includes external class `profile_postgresql`; its package, service, and configuration resources require verification in the dependency/profile implementation.
   - Uses PostgreSQL version `15` from `profile_postgresql::version`.
   - Creates PostgreSQL user `testuser`.
   - Creates database `testdb` owned by `testuser`.
   - Grants all privileges on `testdb` to `testuser`.
   - Implements the user, database, and privilege operations with Ansible PostgreSQL modules or `no_log: true` tasks rather than logging passwords in shell commands.
   - Requires the PostgreSQL service before database operations.
   - Deploys `puppet:///modules/profile_app_stack/backup.sh` to `/usr/local/bin/db-backup.sh`, owned by `root:appuser` with mode `0750`.
   - Schedules `/usr/local/bin/db-backup.sh testdb localhost` as root daily at `02:30`.

6. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`):
   - Creates `/opt/test-app` owned by `appuser:appuser` with mode `0755`.
   - Checks out `file:///tmp/test-app-repo` with Git, revision `master` by default, provider `git`, user `appuser`, and ensure `latest`.
   - Requires the `appuser` user and application directory.
   - Creates `/opt/test-app/venv` using `python3 -m venv /opt/test-app/venv`.
   - Uses marker `/opt/test-app/venv/bin/activate`.
   - Installs `/opt/test-app/requirements.txt` into the virtual environment.
   - The effective `pip_packages` loop runs zero times; no `install_pip_*` resources are created.
   - The module-default package names `uvicorn`, `gunicorn`, and `psycopg2-binary` are shadowed by the effective empty list and are not installed.
   - Retain an Ansible loop over `app_stack_pip_packages`, defaulting to `[]`.
   - Renders `/opt/test-app/.env` from `profile_app_stack/app.env.erb`, once, owned by `appuser:appuser` with mode `0600`.
   - Suppresses environment-file output with `no_log: true`.
   - Deploys `puppet:///modules/profile_app_stack/healthcheck.sh` to `/usr/local/bin/app-healthcheck.sh`, owned by `root:root` with mode `0755`.
   - Runs `/opt/test-app/venv/bin/python -m alembic upgrade head` from `/opt/test-app` as `appuser` with `DATABASE_URL` set to the generated `db_url`.
   - Runs migrations only when the checkout changes and `/opt/test-app/migrations/env.py` exists.
   - Requirements installation and environment-file changes notify the service phase.

7. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`):
   - Renders `/etc/systemd/system/test-app.service` from `profile_app_stack/app.service.epp`, once, owned by `root:root` with mode `0644`.
   - Runs `systemctl daemon-reload` when the unit changes.
   - Enables and starts `test-app`.
   - Requires the unit file and daemon reload.
   - Restarts `test-app` when the unit or `/opt/test-app/.env` changes.
   - Ansible implementation uses a template task, a daemon-reload handler, and a restart handler.

8. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Declares virtual package `prometheus-node-exporter`.
   - Declares virtual service `prometheus-node-exporter`, enabled and running, requiring the package.
   - Declares virtual package `prometheus-pushgateway`.
   - Declares virtual cron `push_app_metrics` invoking `/usr/local/bin/app-healthcheck.sh --push-metrics` as `appuser` every five minutes.
   - Realizes all four virtual resources only when `$facts['environment'] == 'production'`.
   - Runs the always-active `app_health_check` cron as root every two minutes:
     - Command: `/usr/local/bin/app-healthcheck.sh http://localhost:8000/health`
   - In Ansible, guard production packages, service, and metric-push cron tasks with `app_stack_environment == 'production'`.

## Variables

**Variable Flow Summary**: 23 distinct application-stack variables flow through control-repository common data, module common data, and environment-specific Hiera levels. Lookup behavior is effectively first-value precedence for explicitly typed lookups. Ansible should represent this with defaults, environment group variables, and encrypted group or host variables.

### Variable Definitions

#### `data/common.yaml` — control-repository common defaults

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
- `profile_app_stack::db_password`: `test-db-password` (type: string; migrate to Ansible Vault)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/test-app` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `test-secret-key` (type: string; migrate to Ansible Vault)
- `profile_app_stack::python_version`: `python3` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)

#### `site-modules/profile_app_stack/data/common.yaml` — module defaults

- `profile_app_stack::app_name`: `myapp-api` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/example-org/myapp-api.git` (type: string)
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp-api` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::python_version`: `python3` (type: string)
- `profile_app_stack::pip_packages`: `['uvicorn', 'gunicorn', 'psycopg2-binary']` (type: array)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_db` (type: string)
- `profile_app_stack::db_user`: `myapp_app` (type: string)
- `profile_app_stack::db_password`: Hiera-eyaml encrypted string (type: string; secret)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `uvicorn.workers.UvicornWorker` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp-api` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

#### `site-modules/profile_app_stack/data/environment/production.yaml` — production overrides

- `profile_app_stack::app_revision`: `v2.4.1` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `5000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::db_host`: `db-primary.prod.internal` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::secret_key`: Hiera-eyaml encrypted string (type: string; secret)

#### `site-modules/profile_app_stack/data/environment/staging.yaml` — staging overrides

- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::worker_count`: `1` (type: integer)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging-not-secret-at-all` (type: string; migrate to Ansible Vault)

#### `data/environment/production.yaml`

- No `profile_app_stack` variables.
- Contains NTP and syslog values outside this module’s lookup flow.

#### `data/environment/staging.yaml`

- No `profile_app_stack` variables.
- Contains syslog values outside this module’s lookup flow.

### Effective environment values

#### Default

- `app_name`: `test-app`
- `app_repo`: `file:///tmp/test-app-repo`
- `app_revision`: `master`
- `app_port`: `8000`
- `app_dir`: `/opt/test-app`
- `app_user`: `appuser`
- `app_group`: `appuser`
- `db_host`: `localhost`
- `db_port`: `5432`
- `db_name`: `testdb`
- `db_user`: `testuser`
- `db_password`: `test-db-password`
- `worker_count`: `2`
- `worker_class`: `sync`
- `max_requests`: `1000`
- `graceful_timeout`: `30`
- `log_dir`: `/var/log/test-app`
- `log_level`: `info`
- `secret_key`: `test-secret-key`
- `python_version`: `python3`
- `pip_packages`: `[]`
- `log_max_size`: `100M`
- `log_rotate_count`: `7`

#### Production

- `app_revision`: `v2.4.1`
- `worker_count`: `8`
- `max_requests`: `5000`
- `log_level`: `warning`
- `db_host`: `db-primary.prod.internal`
- `db_port`: `5432`
- `secret_key`: encrypted production value

#### Staging

- `app_revision`: `main`
- `worker_count`: `1`
- `max_requests`: `100`
- `log_level`: `debug`
- `db_host`: `localhost`
- `db_port`: `5432`, inherited from common data
- `secret_key`: `staging-not-secret-at-all`

### Variable Migration Summary

- **Common defaults**: 21 variables from `data/common.yaml`.
- **Module defaults**: 22 variables from `site-modules/profile_app_stack/data/common.yaml`.
- **Distinct variable flow**: 23 variables after accounting for 20 overlapping variables, control-repository-only `secret_key`, and module-only `log_max_size` and `log_rotate_count`.
- **Production-specific variables**: 7 variables.
- **Staging-specific variables**: 6 variables.
- **Encrypted or secret-bearing variables**:
  - `profile_app_stack::db_password`
  - `profile_app_stack::secret_key`
  - PostgreSQL credentials generated from those values
  - Any Redis credentials or TLS material from dependency modules if enabled elsewhere; none are referenced by this execution tree.

### Cross-Level Overrides

- `app_name`: control common and module common; effective value `test-app`.
- `app_repo`: control common and module common; effective value `file:///tmp/test-app-repo`.
- `app_revision`: control common, module common, production, and staging; effective values `master`, `v2.4.1`, and `main`.
- `app_port`: control common and module common; effective value `8000`.
- `app_dir`: control common and module common; effective value `/opt/test-app`.
- `app_user`: control common and module common; effective value `appuser`.
- `app_group`: control common and module common; effective value `appuser`.
- `db_host`: control common, module common, production, and staging; effective values `localhost` or `db-primary.prod.internal`.
- `db_port`: control common, module common, and production; effective value `5432`.
- `db_name`: control common and module common; effective value `testdb`.
- `db_user`: control common and module common; effective value `testuser`.
- `db_password`: control common and module common; effective supplied value `test-db-password`; store only in Ansible Vault.
- `worker_count`: control common, module common, production, and staging; effective values `2`, `8`, and `1`.
- `worker_class`: control common and module common; effective value `sync`.
- `max_requests`: control common, module common, production, and staging; effective values `1000`, `5000`, and `100`.
- `graceful_timeout`: control common and module common; effective value `30`.
- `log_dir`: control common and module common; effective value `/var/log/test-app`.
- `log_level`: control common, module common, production, and staging; effective values `info`, `warning`, and `debug`.
- `secret_key`: control common, production, and staging; use the environment-specific secret where applicable.
- `python_version`: control common and module common; effective value `python3`.
- `pip_packages`: control common and module common; effective value `[]`.
- `log_max_size`: module common only; effective value `100M`.
- `log_rotate_count`: module common only; effective value `7`.

### Merge Strategy Notes

- Explicitly typed lookups use first-value precedence; the first value found wins.
- Ansible defaults should represent module defaults.
- Environment `group_vars` should override defaults for production and staging.
- Encrypted `group_vars` or `host_vars` should contain `db_password` and `secret_key`.
- No `hash` or `deep` merge behavior is used by the documented application variables.

## Custom Types and Providers

- No custom Puppet types or providers were detected in `lib/`.
- `vcsrepo` uses the Git provider.
- The manifest invokes `profile_app_stack::app_db_url`.
- The function source and implementation were not supplied, so its exact return format, URL encoding, reserved-character escaping, quoting, and handling of special database credentials remain pending verification.
- The Ansible migration must implement an equivalent Jinja2 filter or lookup after the function source is located. It must accept:
  - `db_user`
  - `db_password`
  - `db_host`
  - `db_port`
  - `db_name`
- Migration is not complete until the generated URL is compared with Puppet output for ordinary and special-character passwords.

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
- External `profile_postgresql` for local PostgreSQL mode

Only `puppetlabs-vcsrepo` is directly evident in the application execution tree. The other dependencies require verification in the broader profile implementation.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `python3-dev`
- `git`
- `build-essential`
- PostgreSQL packages and service when `db_host == localhost`
- `prometheus-node-exporter` in production
- `prometheus-pushgateway` in production

**Python package dependencies**:

- Requirements from `/opt/test-app/requirements.txt`
- No extra Hiera pip packages in the effective configuration
- `uvicorn`, `gunicorn`, and `psycopg2-binary` are module defaults only and are not installed when `pip_packages: []`

**Service dependencies**:

- Base profile before application profile.
- Python setup before database setup.
- Database setup before application deployment.
- Application changes notify the service phase.
- Service setup before monitoring.
- Local database operations require the PostgreSQL service.
- Virtual environment creation requires the Git checkout.
- Requirements installation requires the Git checkout and virtual environment.
- Systemd service requires the unit file and daemon reload.
- `.env` changes restart the application service.
- Git checkout changes trigger database migrations.

## Puppet Facts Used

- `$facts['kernel']`
  - Provides the operating-system kernel name.
  - Applies executable `PATH` defaults only on Linux.

- `fact('environment')`
  - Provides the Puppet environment name.
  - Supplies the unused `profile::app::stack` parameter `environment_name`.

- `$facts['environment']`
  - Provides the Puppet environment name.
  - Realizes Prometheus virtual resources only when the value is `production`.

Ansible replacements:

- `app_stack_environment: production` or `staging` from inventory/group variables.
- `ansible_facts['kernel']` where kernel-based behavior is still required.

## Template Conversion Notes

### `profile_app_stack/logrotate.conf.erb`

- Render count: `1`.
- Destination: `/etc/logrotate.d/test-app`.
- Variables: `app_name`, `log_dir`, `log_max_size`, and `log_rotate_count`.
- Convert to Jinja2.
- Preserve `/var/log/test-app`, `100M`, and seven retained rotations.
- Ownership and mode: `root:root`, `0644`.

### `profile_app_stack/app.env.erb`

- Render count: `1`.
- Destination: `/opt/test-app/.env`.
- Ownership and mode: `appuser:appuser`, `0600`.
- Variables include generated `db_url`, `app_name`, `app_port`, `secret_key`, `log_level`, `log_dir`, `worker_count`, and application environment/database context.
- Contains three Ruby logic blocks.
- Convert conditionals and expressions to Jinja2 while preserving exact environment-variable names and quoting.
- Render with `no_log: true`.

### `profile_app_stack/app.service.epp`

- Render count: `1`.
- Destination: `/etc/systemd/system/test-app.service`.
- Ownership and mode: `root:root`, `0644`.
- Variables include `app_name`, `app_dir`, `app_user`, `app_group`, `app_port`, `worker_count`, `worker_class`, `max_requests`, `graceful_timeout`, `log_dir`, `log_level`, and one additional invocation/class-context value.
- Contains two logic blocks.
- Convert EPP conditionals to Jinja2.
- Notify `systemctl daemon-reload` when changed.
- Restart `test-app` after daemon reload.

### `puppet:///modules/profile_app_stack/backup.sh`

- Destination: `/usr/local/bin/db-backup.sh`.
- Ownership and mode: `root:appuser`, `0750`.
- Source-file behavior: database backup script invoked with database name and host arguments.
- Invocation: `/usr/local/bin/db-backup.sh testdb localhost`.
- Schedule: root cron, daily at `02:30`.
- Deploy with an Ansible `copy` or `template` task and preserve executable mode.
- Do not expose database credentials in task output; use Vault-backed variables and `no_log: true` if credentials are consumed by the script.
- Validate that the script supports the exact two-argument invocation and writes backups to the expected destination.

### `puppet:///modules/profile_app_stack/healthcheck.sh`

- Destination: `/usr/local/bin/app-healthcheck.sh`.
- Ownership and mode: `root:root`, `0755`.
- HTTP health invocation: `/usr/local/bin/app-healthcheck.sh http://localhost:8000/health`.
- Production metric invocation: `/usr/local/bin/app-healthcheck.sh --push-metrics`.
- Always-active schedule: root cron every two minutes.
- Production-only schedule: `appuser` cron every five minutes.
- Deploy with an Ansible `copy` or `template` task and preserve executable mode.
- Validate HTTP endpoint handling, exit status behavior, and pushgateway metric behavior before migration completion.

## PuppetDB Dependencies

No PuppetDB dependencies were detected in the analyzed execution tree.

- No exported resources using `@@` were found.
- No resource collectors using `<<| |>>` were found.
- No `puppetdb_query()` calls were found.
- No host identity data or cross-node resource sharing patterns were found.
- No PuppetDB replacement is required for this module.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/app_stack.pp`
- `site-modules/profile/manifests/app/stack.pp`
- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/python.pp`
- `site-modules/profile_app_stack/manifests/database.pp`
- `site-modules/profile_app_stack/manifests/app.pp`
- `site-modules/profile_app_stack/manifests/service.pp`
- `site-modules/profile_app_stack/manifests/monitoring.pp`
- `profile_app_stack/logrotate.conf.erb`
- `profile_app_stack/app.env.erb`
- `profile_app_stack/app.service.epp`
- `puppet:///modules/profile_app_stack/backup.sh`
- `puppet:///modules/profile_app_stack/healthcheck.sh`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `profile_postgresql` implementation
- `profile_app_stack::app_db_url` implementation

**Service endpoints to check**:

- `test-app`: HTTP `localhost:8000`
- PostgreSQL local mode: `localhost:5432`
- PostgreSQL production mode: `db-primary.prod.internal:5432`
- Systemd unit: `test-app.service`
- Health endpoint: `http://localhost:8000/health`

**Templates rendered**:

- `profile_app_stack/logrotate.conf.erb`: 1 render
- `profile_app_stack/app.env.erb`: 1 render
- `profile_app_stack/app.service.epp`: 1 render
- `backup.sh`: 1 deployed script
- `healthcheck.sh`: 1 deployed script

## Pre-flight checks

```bash
# Common application checks
getent passwd appuser
getent group appuser
python3 --version
git --version
test -d /opt/test-app
test -d /opt/test-app/venv
test -x /opt/test-app/venv/bin/python
test -f /opt/test-app/requirements.txt
test -f /opt/test-app/.env
stat -c '%U:%G %a %n' /opt/test-app /opt/test-app/.env
systemctl is-enabled test-app
systemctl is-active test-app

# test-app default instance
curl --fail http://localhost:8000/health
systemctl status test-app.service
systemctl cat test-app.service
test -x /usr/local/bin/app-healthcheck.sh
/usr/local/bin/app-healthcheck.sh http://localhost:8000/health
test -f /etc/logrotate.d/test-app
logrotate -d /etc/logrotate.d/test-app
test -x /usr/local/bin/db-backup.sh
/usr/local/bin/db-backup.sh testdb localhost --help || true

# Staging instance
systemctl status test-app.service
curl --fail http://localhost:8000/health
grep -E 'APP_REVISION|WORKER_COUNT|MAX_REQUESTS|LOG_LEVEL' /opt/test-app/.env
test "$(systemctl is-active test-app)" = "active"
test ! -e /etc/systemd/system/prometheus-node-exporter.service || true

# Production instance
getent hosts db-primary.prod.internal
timeout 5 bash -c '</dev/tcp/db-primary.prod.internal/5432'
systemctl status test-app.service
curl --fail http://localhost:8000/health
grep -E 'APP_REVISION|WORKER_COUNT|MAX_REQUESTS|LOG_LEVEL' /opt/test-app/.env
systemctl is-enabled prometheus-node-exporter
systemctl is-active prometheus-node-exporter
systemctl is-enabled prometheus-pushgateway || true
test "$(crontab -u appuser -l 2>/dev/null | grep -c -- '--push-metrics')" -ge 1

# Local PostgreSQL checks for the test-app default and staging configurations
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='testuser'"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_catalog.pg_database WHERE datname='testdb'"
sudo -u postgres psql -tAc "SELECT has_database_privilege('testuser', 'testdb', 'CREATE')"
ss -lnt | grep ':5432'

# Configuration and migration checks
systemctl daemon-reload
systemctl restart test-app
test ! -e /opt/test-app/migrations/env.py || \
  sudo -u appuser /opt/test-app/venv/bin/python -m alembic current
test -x /usr/local/bin/app-healthcheck.sh
test -x /usr/local/bin/db-backup.sh
```