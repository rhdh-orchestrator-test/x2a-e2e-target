---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: `profile_app_stack` deploys the `test-app` Python application from a Git repository, creates its system account and virtual environment, installs dependencies, optionally provisions local PostgreSQL, writes application and systemd configuration, schedules backups and health checks, and realizes Prometheus resources in production. Preserve the execution order `python → database → app ~> service → monitoring`. The Ansible migration must obtain and analyze the missing backup and health-check scripts, verify the unresolved `app_db_url` implementation, and confirm Hiera precedence and resource expansion before implementation is finalized.

## Service Type and Instances

**Service Type**: Python web application managed by systemd, with optional local PostgreSQL and production-only Prometheus monitoring.

**Configured Instances**:

- **test-app**
  - Purpose: Python web application service
  - Location/Path: `/opt/test-app`
  - User/Group: `appuser` / `appuser`
  - Port/Socket: TCP `8000`
  - Repository: `file:///tmp/test-app-repo`
  - Revision: `master`
  - Workers: `2`
  - Worker class: `sync`
  - Max requests: `1000`
  - Graceful timeout: `30`
  - Log directory: `/var/log/test-app`
  - Log level: `info`
  - Health endpoint: `http://localhost:8000/health`

- **testdb**
  - Purpose: Application PostgreSQL database
  - Host: `localhost`
  - Port/Socket: TCP `5432`
  - Database: `testdb`
  - User: `testuser`
  - Password: sensitive effective value `test-db-password`; store in Ansible Vault
  - Provisioning: Local PostgreSQL is enabled because the effective `db_host` is `localhost`

- **prometheus-node-exporter**
  - Purpose: Production host metrics
  - Package: `prometheus-node-exporter`
  - Service: Enabled and running
  - Activation: Production only

- **prometheus-pushgateway**
  - Purpose: Production application metrics delivery
  - Package: `prometheus-pushgateway`
  - Metrics job: `/usr/local/bin/app-healthcheck.sh --push-metrics`
  - User: `appuser`
  - Schedule: Every 5 minutes
  - Activation: Production only

- **app_health_check**
  - Purpose: Application health monitoring
  - Command: `/usr/local/bin/app-healthcheck.sh http://localhost:8000/health`
  - User: `root`
  - Schedule: Every 2 minutes
  - Activation: All environments

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
site-modules/
├── role/
│   └── manifests/
│       └── app_server.pp
├── profile/
│   └── manifests/
│       └── app/
│           └── stack.pp
└── profile_app_stack/
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
    ├── hiera.yaml
    └── data/
        ├── common.yaml
        └── environment/
            ├── production.yaml
            └── staging.yaml

data/
└── common.yaml

Referenced source files requiring verification:
- puppet:///modules/profile_app_stack/backup.sh
- puppet:///modules/profile_app_stack/healthcheck.sh
```

The two referenced source files were not present in the supplied directory listing. Their contents, arguments, database access, error handling, and metrics behavior must be obtained and analyzed before migration completion.

## Module Explanation

The module performs operations in this order:

1. **`role::app_server`** (`site-modules/role/manifests/app_server.pp`):
   - Includes `profile::base::base`, `profile::loadbalancer::haproxy`, `profile::app::stack`, and `profile::cache::redis`.
   - The base, HAProxy, and Redis profiles are outside this module’s analyzed execution tree.
   - Implement their resources and ordering through separate Ansible roles.

2. **`profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`):
   - Instantiates `profile_app_stack`.
   - Resolves parameters through Hiera.
   - Uses the `environment` fact to select environment-specific data.
   - Delegates application-stack resources to `profile_app_stack`.

3. **`profile_app_stack`** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Resolves the application, database, worker, logging, and secret parameters.
   - Builds `db_url` using `profile_app_stack::app_db_url(testuser, db_password, localhost, 5432, testdb)`.
   - The implementation and URL escaping behavior of `profile_app_stack::app_db_url` were not supplied. Treat this as a migration blocker until the declaring module or implementation is identified.
   - Contains `profile_app_stack::python`, `profile_app_stack::database`, `profile_app_stack::app`, `profile_app_stack::service`, and `profile_app_stack::monitoring`.
   - Enforces:
     - `profile_app_stack::python` before `profile_app_stack::database`
     - `profile_app_stack::database` before `profile_app_stack::app`
     - Application changes notifying `profile_app_stack::service`
     - `profile_app_stack::service` before `profile_app_stack::monitoring`
   - Ansible phase order:
     1. Python runtime and account setup
     2. Database provisioning and backup scheduling
     3. Application checkout, virtualenv, configuration, and migrations
     4. Systemd unit and service management
     5. Monitoring resources and health checks

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Installs the following packages, each with `ensure: installed`:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `python3-dev`
     - `git`
     - `build-essential`
   - Creates system group `appuser`.
   - Creates system user `appuser` with:
     - Group: `appuser`
     - Home: `/opt/test-app`
     - Shell: `/bin/bash`
     - `managehome: false`
   - Creates `/var/log/test-app` as a directory owned by `appuser:appuser`, mode `0755`.
   - Deploys `/etc/logrotate.d/test-app` from `site-modules/profile_app_stack/templates/logrotate.conf.erb`, owned by `root:root`, mode `0644`.
   - Template variables are `app_name`, `log_dir`, `log_max_size`, and `log_rotate_count`.

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Checks whether `db_host == 'localhost'`.
   - When true, includes `profile_postgresql`; its exact resources require separate dependency analysis.
   - Creates PostgreSQL role `testuser` after the PostgreSQL service is available.
   - Creates database `testdb` owned by `testuser` after the role exists.
   - Grants all privileges on `testdb` to `testuser` after database creation.
   - Idempotence checks query PostgreSQL system catalogs.
   - Deploys `/usr/local/bin/db-backup.sh` from `puppet:///modules/profile_app_stack/backup.sh`, owned by `root:appuser`, mode `0750`.
   - Creates the `database_backup` cron job:
     - Command: `/usr/local/bin/db-backup.sh testdb localhost`
     - User: `root`
     - Schedule: `02:30`
   - The database password must not appear in commands, output, diffs, or logs.
   - For a non-localhost database, skip local PostgreSQL provisioning, role creation, database creation, and privilege grants. Retain the backup script and cron only if the backup implementation supports remote database operation.

6. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`):
   - Creates `/opt/test-app` as `appuser:appuser`, mode `0755`.
   - Checks out `file:///tmp/test-app-repo` at revision `master` using Git.
   - Creates `/opt/test-app/venv` with `python3 -m venv`.
   - Installs `/opt/test-app/requirements.txt` with `/opt/test-app/venv/bin/pip`.
   - The requirements installation runs as `appuser` from `/opt/test-app` and notifies service management.
   - The `pip_packages` loop expands to zero resources because the effective value is an empty array:
     - No `install_pip_<package>` resources are created.
   - Deploys `/opt/test-app/.env` from `site-modules/profile_app_stack/templates/app.env.erb`, owned by `appuser:appuser`, mode `0600`, and notifies service management.
   - Deploys `/usr/local/bin/app-healthcheck.sh` from `puppet:///modules/profile_app_stack/healthcheck.sh`, owned by `root:root`, mode `0755`.
   - Runs `/opt/test-app/venv/bin/python -m alembic upgrade head` as `appuser` from `/opt/test-app` when `/opt/test-app/migrations/env.py` exists.
   - Database migrations are refresh-only and triggered by repository changes.
   - The Ansible implementation should use `ansible.builtin.git`, `ansible.builtin.command` or `ansible.builtin.pip`, a protected environment-file template, and a migration handler or task triggered by repository changes.

7. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`):
   - Deploys `/etc/systemd/system/test-app.service` from `site-modules/profile_app_stack/templates/app.service.epp`, owned by `root:root`, mode `0644`.
   - Runs `systemctl daemon-reload` when the unit changes.
   - Enables and starts the `test-app` service.
   - Requires the systemd unit and daemon reload before service startup.
   - Subscribes to `/opt/test-app/.env`.
   - Preserve these notification behaviors:
     - Unit changes trigger daemon reload.
     - `.env` changes trigger application service management.
     - Requirements installation notifies service management.
     - Application-phase changes notify service management through the class-level application-to-service relationship.

8. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Declares virtual resources:
     - Package `prometheus-node-exporter`
     - Service `prometheus-node-exporter`
     - Package `prometheus-pushgateway`
     - Cron `push_app_metrics`
   - Realizes all four resources only when `$facts['environment'] == 'production'`.
   - Production resources:
     - Install and enable `prometheus-node-exporter`.
     - Install `prometheus-pushgateway`.
     - Run `/usr/local/bin/app-healthcheck.sh --push-metrics` as `appuser` every 5 minutes.
   - Always creates `app_health_check` as `root` every 2 minutes against `http://localhost:8000/health`.
   - Virtual Puppet resources are local resources, not PuppetDB resources.

## Variables

**Variable Flow Summary**: 23 class and runtime variables across the module Hiera hierarchy and the higher-priority control-repository common data. Exact precedence and effective environment values require verification against the supplied Hiera configuration and data.

### Hiera Hierarchy

`site-modules/profile_app_stack/hiera.yaml` is reported to define:

1. `environment/%{::environment}.yaml`
2. `common.yaml`

The supplied validation notes state that the hierarchy and precedence claims could not be verified from the structured analysis summary. Confirm the Hiera configuration, control-repository lookup integration, precedence, and effective values before implementation.

### Variable Definitions

#### Control-repository common: `data/common.yaml`  
Migration note: Higher-priority control-repository values reported as effective for the supplied test instance; precedence requires verification.

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
- `profile_app_stack::db_password`: `test-db-password` (type: string; sensitive)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/test-app` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `test-secret-key` (type: string; sensitive)
- `profile_app_stack::python_version`: `python3` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array of strings)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

#### Module-local common: `site-modules/profile_app_stack/data/common.yaml`  
Migration note: Module defaults; reported to be overridden by higher-priority data where applicable.

- `profile_app_stack::app_name`: `myapp-api` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/example-org/myapp-api.git` (type: string)
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp-api` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_db` (type: string)
- `profile_app_stack::db_user`: `myapp_app` (type: string)
- `profile_app_stack::db_password`: `ENC[PKCS7,...]` (type: string; sensitive and encrypted)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `uvicorn.workers.UvicornWorker` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp-api` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)
- `profile_app_stack::python_version`: `python3` (type: string)
- `profile_app_stack::pip_packages`: `[uvicorn, gunicorn, psycopg2-binary]` (type: array of strings)

#### Module-local production: `site-modules/profile_app_stack/data/environment/production.yaml`  
Migration note: Production-specific values; precedence over module-local common values requires verification.

- `profile_app_stack::app_revision`: `v2.4.1` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `5000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::db_host`: `db-primary.prod.internal` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::secret_key`: `ENC[PKCS7,...]` (type: string; sensitive and encrypted)

#### Module-local staging: `site-modules/profile_app_stack/data/environment/staging.yaml`  
Migration note: Staging-specific values; precedence over module-local common values requires verification.

- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::worker_count`: `1` (type: integer)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging-not-secret-at-all` (type: string; sensitive despite plaintext storage)

### Variable Migration Summary

- **Control-repository common**: 23 variables, including application, database, runtime, worker, logging, and secret values.
- **Module-local common**: 22 variables providing module defaults.
- **Production-specific**: 7 variables.
- **Staging-specific**: 6 variables.
- **Encrypted or sensitive**: database password, application secret key, and dependency-module credentials.
- **Extra pip package loop instances**: 0.
- **Ansible mapping**:
  - `app_stack_db_password`: Ansible Vault variable for `profile_app_stack::db_password`
  - `app_stack_secret_key`: Ansible Vault variable for `profile_app_stack::secret_key`
  - Application, database, worker, and logging values: ordinary role variables unless sensitive
  - `pip_packages`: Ansible list; do not create package tasks when the effective list is empty
  - `environment`: Ansible inventory/group variable controlling environment-specific configuration and production monitoring

### Cross-Level Overrides

Variables reported as defined at multiple levels include:

- `app_name`: control-repository common overrides module-local common.
- `app_repo`: control-repository common overrides module-local common.
- `app_revision`: control-repository common and environment data override module-local common according to precedence.
- `app_dir`: control-repository common overrides module-local common.
- `app_user`: control-repository common overrides module-local common.
- `app_group`: control-repository common overrides module-local common.
- `db_name`: control-repository common overrides module-local common.
- `db_user`: control-repository common overrides module-local common.
- `db_password`: control-repository common value overrides the encrypted module-local value in the supplied context.
- `worker_class`: control-repository common overrides module-local common.
- `log_dir`: control-repository common overrides module-local common.
- `secret_key`: control-repository common value reportedly overrides module-local production and staging values.
- `app_revision`, `worker_count`, `max_requests`, `log_level`, and `db_host`: environment values override module-local common when no higher-priority value is present.

These claims require verification against the actual Hiera lookup configuration.

### Merge Strategy Notes

- Scalar variables use first-match lookup; no hash or deep merge is reported.
- Variables using `hash` merge: none identified.
- Variables using `deep` merge: none identified.
- Variables using `first` or default lookup: all listed scalar variables unless the verified Hiera configuration states otherwise.

## Custom Types and Providers

No custom Puppet types, providers, facts, or functions were confirmed by the supplied custom-code analysis.

`profile_app_stack::app_db_url` is called by `site-modules/profile_app_stack/manifests/init.pp`, but its implementation was not supplied and no custom functions were detected in the analysis summary. Identify its declaring module and exact escaping behavior. If unavailable, migration of database URL construction is blocked. The Ansible equivalent must URL-escape the database password correctly and must not expose it in output.

## Dependencies

**External module dependencies**: The following dependencies were listed but were not supported by the supplied structured summary; retain them as requiring separate analysis:

- `puppetlabs-stdlib` `9.7.0`
- `puppetlabs-concat` `9.0.2`
- `puppetlabs-firewall` `8.1.3`
- `puppetlabs-vcsrepo` `6.1.0`
- `puppet-redis` `11.0.0`
- `puppet-systemd` `7.1.0`
- `puppetlabs-inifile` `6.1.1`
- `puppetlabs-apt` `9.4.0`
- `profile_postgresql`, specifically its PostgreSQL service and package resources
- External base, HAProxy, and Redis profiles included by `role::app_server`

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `python3-dev`
- `git`
- `build-essential`
- PostgreSQL packages when `db_host == localhost`
- `prometheus-node-exporter` in production
- `prometheus-pushgateway` in production

**Service dependencies**:

- Python packages and account setup precede database provisioning.
- PostgreSQL service precedes PostgreSQL role creation.
- PostgreSQL role creation precedes database creation.
- Database creation precedes privilege grants.
- Database provisioning precedes application deployment.
- Git checkout precedes virtualenv creation.
- Virtualenv creation precedes requirements installation.
- Application changes notify systemd service management.
- Systemd unit changes trigger daemon reload.
- Unit installation and daemon reload precede starting `test-app`.
- Monitoring follows service configuration.

## Puppet Facts Used

- `$facts['environment']`
  - Selects the environment-specific Hiera data.
  - Determines whether Prometheus virtual resources are realized.
- `fact('environment')`
  - Passed by `profile::app::stack` as the optional `environment_name` parameter.
  - Is not otherwise used by the supplied wrapper manifest.

## Template Conversion Notes

### `site-modules/profile_app_stack/templates/logrotate.conf.erb`

- Destination: `/etc/logrotate.d/test-app`
- Render count: 1
- Variables: `app_name`, `log_dir`, `log_max_size`, `log_rotate_count`
- Deploy as `root:root`, mode `0644`.
- Convert to an Ansible template without changing log rotation behavior.

### `site-modules/profile_app_stack/templates/app.env.erb`

- Destination: `/opt/test-app/.env`
- Render count: 1
- The template has 8 variables total, not 8 additional variables.
- Variables include:
  - Application name: `test-app`
  - Resolved database URL
  - Secret key
  - Application port: `8000`
  - Log level: `info`
  - Log directory: `/var/log/test-app`
  - Worker count: `2`
  - One additional application setting represented by the supplied template analysis
- Contains 2 logic blocks.
- Inspect the source template and preserve its exact conditional rendering and formatting.
- Deploy as `appuser:appuser`, mode `0600`.
- Use `no_log: true` for tasks that may expose rendered secrets.

### `site-modules/profile_app_stack/templates/app.service.epp`

- Destination: `/etc/systemd/system/test-app.service`
- Render count: 1
- Variables:
  - `app_name`: `test-app`
  - `app_dir`: `/opt/test-app`
  - `app_user`: `appuser`
  - `app_group`: `appuser`
  - `app_port`: `8000`
  - `worker_count`: `2`
  - `worker_class`: `sync`
  - `max_requests`: `1000`
  - `graceful_timeout`: `30`
  - `log_dir`: `/var/log/test-app`
  - `log_level`: `info`
- Contains 2 logic blocks.
- Convert EPP conditionals to Jinja2 without changing generated systemd directives.
- Notify a systemd daemon-reload handler.
- Enable and start `test-app` after the unit is installed and reloaded.

## Credentials and Secret Handling

- **Application database password**
  - Effective reported value: `test-db-password`.
  - Module-local value: Hiera-eyaml encrypted.
  - Store as an Ansible Vault variable such as `app_stack_db_password`.
  - Do not expose it in PostgreSQL commands, task output, diffs, logs, or generated command lines.

- **Application secret key**
  - Effective reported value: `test-secret-key`.
  - Production module-local value: Hiera-eyaml encrypted.
  - Staging module-local value is plaintext but sensitive.
  - Store all environment-specific values in Ansible Vault.
  - Do not use a `changeme` fallback.

- **Dependency-module credentials**
  - Redis authentication and TLS material are outside this module’s direct execution tree.
  - APT authentication entries may contain repository credentials.
  - Store these in Vault or an external secret backend with restrictive permissions and `no_log`.

## Checks for the Migration

**Files to verify**:

- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/python.pp`
- `site-modules/profile_app_stack/manifests/database.pp`
- `site-modules/profile_app_stack/manifests/app.pp`
- `site-modules/profile_app_stack/manifests/service.pp`
- `site-modules/profile_app_stack/manifests/monitoring.pp`
- `site-modules/profile/manifests/app/stack.pp`
- `site-modules/role/manifests/app_server.pp`
- `site-modules/profile_app_stack/templates/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/app.env.erb`
- `site-modules/profile_app_stack/templates/app.service.epp`
- `site-modules/profile_app_stack/hiera.yaml`
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `data/common.yaml`
- `puppet:///modules/profile_app_stack/backup.sh`
- `puppet:///modules/profile_app_stack/healthcheck.sh`
- The implementation or declaring module for `profile_app_stack::app_db_url`
- `profile_postgresql` resources and dependency metadata
- External dependency metadata and Puppetfile entries

**Service endpoints to check**:

- `test-app`: `http://localhost:8000/health`
- `test-app`: TCP port `8000`
- `testdb`: `localhost:5432` when local PostgreSQL is enabled
- `prometheus-node-exporter`: package and service state in production
- `prometheus-pushgateway`: package state in production

**Templates rendered**:

- `site-modules/profile_app_stack/templates/logrotate.conf.erb` → `/etc/logrotate.d/test-app` — 1 render
- `site-modules/profile_app_stack/templates/app.env.erb` → `/opt/test-app/.env` — 1 render
- `site-modules/profile_app_stack/templates/app.service.epp` → `/etc/systemd/system/test-app.service` — 1 render

**Pre-flight checks**:

```bash
# General and variable resolution
facter environment
# Confirm the actual Hiera hierarchy, precedence, effective values, and sensitive variable sources.

# test-app instance
test -d /tmp/test-app-repo
test -f /tmp/test-app-repo/requirements.txt
test -d /opt/test-app
test -x /opt/test-app/venv/bin/python
test -f /opt/test-app/.env
stat -c '%U:%G %a %n' /opt/test-app/.env
systemctl is-enabled test-app
systemctl is-active test-app
curl --fail http://localhost:8000/health

# testdb instance
pg_isready -h localhost -p 5432
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='testuser'"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_catalog.pg_database WHERE datname='testdb'"
sudo -u postgres psql -tAc "SELECT has_database_privilege('testuser', 'testdb', 'CREATE')"
test -x /usr/local/bin/db-backup.sh
crontab -l -u root | grep -F '/usr/local/bin/db-backup.sh testdb localhost'

# Prometheus node exporter instance, production only
dpkg-query -W prometheus-node-exporter 2>/dev/null || rpm -q prometheus-node-exporter
systemctl is-enabled prometheus-node-exporter
systemctl is-active prometheus-node-exporter

# Prometheus pushgateway instance, production only
dpkg-query -W prometheus-pushgateway 2>/dev/null || rpm -q prometheus-pushgateway
crontab -l -u appuser | grep -F '/usr/local/bin/app-healthcheck.sh --push-metrics'

# app_health_check instance
crontab -l -u root | grep -F '/usr/local/bin/app-healthcheck.sh http://localhost:8000/health'

# Configuration and service validation
systemd-analyze verify /etc/systemd/system/test-app.service
systemctl daemon-reload
systemctl enable --now test-app

# Application migration validation
test -f /opt/test-app/migrations/env.py
# If present, run Alembic migration validation without logging DATABASE_URL or credentials.
```

Migration completion is blocked until the `app_db_url` implementation, Hiera precedence, package/resource expansion, external dependencies, `backup.sh`, and `healthcheck.sh` are verified.