---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: `profile_app_stack` deploys the `test-app` Python/Gunicorn application from `file:///tmp/test-app-repo`, creates the `appuser` runtime account and application directories, configures PostgreSQL access and local database initialization when applicable, installs the Python runtime and application dependencies, renders the application environment and systemd unit, runs migrations, configures log rotation, and schedules health-check and database-backup jobs. The effective repository configuration uses `test-app` on port `8000`, with environment-specific revisions, worker counts, request limits, log levels, database hosts, and secrets. Production and staging values override repository common values where defined; repository common values override module defaults for remaining settings.

## Service Type and Instances

**Service Type**: Python web application managed by systemd and Gunicorn, with PostgreSQL connectivity and Prometheus-related monitoring resources.

**Configured Instances**:

- **myapp-api**: Python/Gunicorn application service represented by the effective `test-app` repository configuration
  - Application repository: `file:///tmp/test-app-repo`
  - Revision:
    - Default: `master`
    - Production: `v2.4.1`
    - Staging: `main`
  - Application directory: `/opt/test-app`
  - Runtime user/group: `appuser` / `appuser`
  - Port: `8000`
  - Database:
    - Default and staging host: `localhost`
    - Production host: `db-primary.prod.internal`
    - Port: `5432`
    - Database: `testdb`
    - User: `testuser`
  - Worker count:
    - Default: `2`
    - Production: `8`
    - Staging: `1`
  - Worker class: `sync`
  - Maximum requests:
    - Default: `1000`
    - Production: `5000`
    - Staging: `100`
  - Graceful timeout: `30` seconds
  - Log directory: `/var/log/test-app`
  - Log level:
    - Default: `info`
    - Production: `warning`
    - Staging: `debug`
  - Systemd unit: `/etc/systemd/system/test-app.service`
  - Environment file: `/opt/test-app/.env`

## File Structure

```text
site-modules/
├── profile/
│   └── manifests/
│       └── app/
│           └── stack.pp
├── profile_app_stack/
│   ├── manifests/
│   │   ├── init.pp
│   │   ├── python.pp
│   │   ├── database.pp
│   │   ├── app.pp
│   │   ├── service.pp
│   │   └── monitoring.pp
│   ├── templates/
│   │   ├── logrotate.conf.erb
│   │   ├── app.env.erb
│   │   └── app.service.epp
│   ├── data/
│   │   ├── common.yaml
│   │   └── environment/
│   │       ├── production.yaml
│   │       └── staging.yaml
│   ├── hiera.yaml
│   └── metadata.json
└── role/
    └── manifests/
        └── app_server.pp

data/
├── common.yaml
└── environment/
    ├── production.yaml
    └── staging.yaml
```

## Module Explanation

The module performs operations in this order:

1. **`role::app_server`** (`site-modules/role/manifests/app_server.pp`):
   - Entry point for the broader application server stack.
   - Includes `profile::base::base`, `profile::loadbalancer::haproxy`, `profile::app::stack`, and `profile::cache::redis`.
   - Reads the `environment` Puppet fact.
   - Only `profile::app::stack` and its application-stack dependencies are analyzed in this plan.

2. **`profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`):
   - Includes `profile_app_stack`.
   - Reads the `environment` Puppet fact.
   - Serves as the control-repository wrapper around the application-stack module.

3. **`profile_app_stack`** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Resolves application, database, service, logging, and secret parameters through Hiera.
   - Builds the database URL in the following form:
     `postgresql://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>`.
   - References the following implementation classes:
     - `profile_app_stack::python`
     - `profile_app_stack::database`
     - `profile_app_stack::app`
     - `profile_app_stack::service`
     - `profile_app_stack::monitoring`
   - Enforces the relationship:
     `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`.
   - The application-to-service `~>` relationship causes application changes to notify the service phase. The Ansible implementation should use handlers for systemd reload and service restart or reload.
   - A reference to `profile_app_stack::app_db_url` is not confirmed by the supplied execution tree. Source review is required before migration; if the implementation exists, reproduce its database-URL behavior exactly.

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Installs the package collection represented by `$python_packages`; the exact expansion is not exposed by the supplied execution tree and must be confirmed from the original class.
   - Ensures the `appuser` group exists.
   - Ensures the `appuser` user exists.
   - Creates `/var/log/test-app` owned by `appuser:appuser`.
   - Renders `/etc/logrotate.d/test-app` from `site-modules/profile_app_stack/templates/logrotate.conf.erb`.
   - Known Python runtime:
     - `python3`
   - Known module-default pip packages:
     - `uvicorn`
     - `gunicorn`
     - `psycopg2-binary`
   - Under the effective repository configuration, `pip_packages` is overridden to `[]`; therefore the conditional pip-installation branch executes zero times.

   **Iterations**:
   - No `.each` loops are exposed in the supplied execution tree.
   - The known pip package list is `uvicorn`, `gunicorn`, and `psycopg2-binary`, but it is not installed by the conditional branch when the effective repository value is `[]`.

   **Logrotate template**:
   - Source: `site-modules/profile_app_stack/templates/logrotate.conf.erb`
   - Destination: `/etc/logrotate.d/test-app`
   - Render count: once
   - Variables:
     - `log_dir`: `/var/log/test-app`
     - `log_rotate_count`: `7`
     - `log_max_size`: `100M`
     - `app_name`: `test-app`
   - Behavior:
     - Rotates `/var/log/test-app/*.log` daily.
     - Retains seven rotations.
     - Compresses rotated logs with delayed compression.
     - Uses `maxsize 100M`.
     - Reloads `test-app` after rotation.

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Resolves the database host and branches on whether it equals `localhost`.
   - For the default and staging configurations, `db_host` is `localhost` and local PostgreSQL setup is enabled.
   - For production, `db_host` is `db-primary.prod.internal` and local PostgreSQL setup is not enabled.
   - Includes `profile_postgresql` when the database host is local.
   - Creates the local database user `testuser`.
   - Creates the local database `testdb`.
   - Grants database privileges to `testuser`.
   - The exact Puppet shell commands, idempotence tests, execution users, and refresh relationships are not exposed. Replace them with:
     - `community.postgresql.postgresql_user`
     - `community.postgresql.postgresql_db`
     - `community.postgresql.postgresql_privs`
   - Creates `/usr/local/bin/db-backup.sh`.
   - Schedules the `database_backup` cron job.
   - The backup script content, ownership, mode, schedule, and command line require source verification.

6. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`):
   - Creates `/opt/test-app`.
   - Checks out `file:///tmp/test-app-repo` into `/opt/test-app`.
   - Uses revision `master` by default, `v2.4.1` in production, and `main` in staging.
   - Creates `/opt/test-app/venv`.
   - Installs application requirements.
   - Evaluates `if !empty($pip_packages)`.
   - With the effective repository value `pip_packages: []`, the pip-package installation branch executes zero times.
   - Renders `/opt/test-app/.env` from `site-modules/profile_app_stack/templates/app.env.erb`.
   - Creates `/usr/local/bin/app-healthcheck.sh`.
   - Runs application database migrations.
   - The exact commands, environment, ownership, modes, and notification attributes for the executable resources require source verification.

   **Iterations**:
   - No `.each` loops are exposed in the supplied execution tree.
   - The conditional pip-installation loop expands to zero items under the effective repository configuration.

   **Application environment template**:
   - Source: `site-modules/profile_app_stack/templates/app.env.erb`
   - Destination: `/opt/test-app/.env`
   - Render count: once
   - Variables:
     - `db_url`
     - `app_name`
     - `app_port`
     - `secret_key`
     - `log_level`
     - `log_dir`
     - `worker_count`
     - Puppet `environment` fact
   - Default effective values:
     - `DATABASE_URL`: `postgresql://testuser:<secret>@localhost:5432/testdb`
     - `APP_NAME`: `test-app`
     - `APP_PORT`: `8000`
     - `SECRET_KEY`: current repository value is `test-secret-key`; replace with a Vault-managed value
     - `LOG_LEVEL`: `info`
     - `LOG_DIR`: `/var/log/test-app`
     - `WORKERS`: `2`
   - Staging effective values:
     - `DATABASE_URL`: `postgresql://testuser:<secret>@localhost:5432/testdb`
     - `LOG_LEVEL`: `debug`
     - `WORKERS`: `1`
     - `SECRET_KEY`: currently `staging-not-secret-at-all`; replace with a Vault-managed value
   - Production effective values:
     - `DATABASE_URL`: `postgresql://testuser:<secret>@db-primary.prod.internal:5432/testdb`
     - `LOG_LEVEL`: `warning`
     - `WORKERS`: `8`
     - `SECRET_KEY`: encrypted Hiera value
   - For production:
     - `DEBUG=false`
     - `ALLOWED_HOSTS=*`
     - `CORS_ORIGINS=https://app.example.com,https://admin.example.com`
   - For non-production environments:
     - `DEBUG=true`
     - `ALLOWED_HOSTS=*`
     - `CORS_ORIGINS=*`
   - The Ansible template must preserve this environment conditional.
   - Render the file with restrictive permissions, preferably mode `0600`.
   - The values `<vault-secret>` used in migration examples are proposed post-migration Vault placeholders, not necessarily the current Puppet-rendered values.

7. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`):
   - Renders `/etc/systemd/system/test-app.service` from `site-modules/profile_app_stack/templates/app.service.epp`.
   - Reloads systemd unit definitions.
   - Ensures `test-app` is running.
   - Enables `test-app` at boot.
   - Uses `app.service.epp` once with:
     - `app_name`: `test-app`
     - `app_dir`: `/opt/test-app`
     - `app_user`: `appuser`
     - `app_group`: `appuser`
     - `app_port`: `8000`
     - `worker_count`: `2` default, `8` production, `1` staging
     - `worker_class`: `sync`
     - `max_requests`: `1000` default, `5000` production, `100` staging
     - `graceful_timeout`: `30`
     - `log_dir`: `/var/log/test-app`
     - `log_level`: `info` default, `warning` production, `debug` staging
   - Computes `TimeoutStopSec` as `graceful_timeout + 5`, resulting in `35`.
   - Renders:
     - Description: `test-app Application Server`
     - Documentation: `https://wiki.internal.example.com/apps/test-app`
     - After: `network.target postgresql.service`
     - Wants: `postgresql.service`
     - Type: `notify`
     - User/group: `appuser` / `appuser`
     - Working directory: `/opt/test-app`
     - Environment file: `/opt/test-app/.env`
     - Gunicorn executable: `/opt/test-app/venv/bin/gunicorn`
     - Application target: `app.main:app`
     - Bind address: `0.0.0.0:8000`
     - Worker class: `sync`
     - Maximum request jitter: `50`
     - Access log: `/var/log/test-app/access.log`
     - Error log: `/var/log/test-app/error.log`
     - ExecReload: `/bin/kill -s HUP $MAINPID`
     - Kill mode: `mixed`
     - Restart policy: `on-failure`
     - Restart delay: `5`
     - Standard output: `/var/log/test-app/stdout.log`
     - Standard error: `/var/log/test-app/stderr.log`
     - Security settings: `NoNewPrivileges=true`, `ProtectSystem=strict`, `ProtectHome=true`, `ReadWritePaths=/opt/test-app /var/log/test-app`, and `PrivateTmp=true`
     - Installation target: `multi-user.target`
   - The Ansible implementation must use `ansible.builtin.template`, notify a systemd daemon-reload handler, and ensure the service is enabled and started with `ansible.builtin.systemd_service`.

8. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Declares virtual resources:
     - `@package[prometheus-node-exporter]`
     - `@service[prometheus-node-exporter]`
     - `@package[prometheus-pushgateway]`
     - `@cron[push_app_metrics]`
   - Declares the same four virtual resources inside the production conditional where `facts['environment'] == 'production'`.
   - No `realize(...)` operation or `<<| |>>` collector is shown. These resources are declarations only unless realized externally.
   - Schedules the `app_health_check` cron job.
   - Reads the `environment` Puppet fact.
   - The health-check command and schedule require source verification.

## Variables

**Variable Flow Summary**: 24 application-stack parameters are defined in `profile_app_stack`. Module common data defines 21 variables, module production data defines 7, module staging data defines 6, and repository common data defines 21. The effective hierarchy gives environment-specific values precedence over repository common values, while repository common values override module defaults for parameters not overridden by environment data.

### Hiera to Ansible Mapping

- `site-modules/profile_app_stack/hiera.yaml`
  - Defines the module hierarchy:
    1. `environment/%{::environment}.yaml`
    2. `common.yaml`
- `site-modules/profile_app_stack/data/common.yaml`
  - Maps to Ansible role defaults or fallback role variables.
- `site-modules/profile_app_stack/data/environment/production.yaml`
  - Maps to `group_vars/production.yml` or production role variables.
- `site-modules/profile_app_stack/data/environment/staging.yaml`
  - Maps to `group_vars/staging.yml` or staging role variables.
- `data/common.yaml`
  - Maps to repository-level `group_vars/all.yml` or higher-priority application-stack defaults.
- `data/environment/production.yaml`
  - Maps to repository production group variables; currently contains no `profile_app_stack` values.
- `data/environment/staging.yaml`
  - Maps to repository staging group variables; currently contains no `profile_app_stack` values.

**Combined effective precedence**:

1. Environment-specific module values.
2. Environment-specific repository values, if added.
3. Repository common values.
4. Module common defaults.

This ordering ensures production and staging values override repository common values where defined, while repository common values override module defaults for remaining parameters.

### Variable Definitions

#### `site-modules/profile_app_stack/data/common.yaml` — module defaults

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
- `profile_app_stack::db_password`: encrypted `ENC[...]` value (type: string)
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
- `profile_app_stack::secret_key`: encrypted `ENC[...]` value (type: string)

#### `site-modules/profile_app_stack/data/environment/staging.yaml` — staging overrides

- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::worker_count`: `1` (type: integer)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging-not-secret-at-all` (type: string; must be replaced with a Vault-managed secret)

#### `data/common.yaml` — repository common overrides

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
- `profile_app_stack::db_password`: `test-db-password` (type: string; plaintext and must not be migrated as plaintext)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/test-app` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::secret_key`: `test-secret-key` (type: string; plaintext and must not be migrated as plaintext)
- `profile_app_stack::python_version`: `python3` (type: string)
- `profile_app_stack::pip_packages`: `[]` (type: array)

#### `data/environment/production.yaml`

- No `profile_app_stack` variables are defined.

#### `data/environment/staging.yaml`

- No `profile_app_stack` variables are defined.

### Effective Values

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
- `db_password`: current repository value is plaintext; replace with Vault-managed data
- `worker_count`: `2`
- `worker_class`: `sync`
- `max_requests`: `1000`
- `graceful_timeout`: `30`
- `log_dir`: `/var/log/test-app`
- `log_level`: `info`
- `secret_key`: current repository value is plaintext; replace with Vault-managed data
- `python_version`: `python3`
- `pip_packages`: `[]`
- `log_max_size`: `100M`
- `log_rotate_count`: `7`

#### Production

Uses the default values except:

- `app_revision`: `v2.4.1`
- `worker_count`: `8`
- `max_requests`: `5000`
- `log_level`: `warning`
- `db_host`: `db-primary.prod.internal`
- `db_port`: `5432`
- `secret_key`: encrypted production value

#### Staging

Uses the default values except:

- `app_revision`: `main`
- `worker_count`: `1`
- `max_requests`: `100`
- `log_level`: `debug`
- `db_host`: `localhost`
- `secret_key`: currently `staging-not-secret-at-all`; replace with a Vault-managed value

### Variable Migration Summary

- **Common module defaults**: 21 variables from `site-modules/profile_app_stack/data/common.yaml`, plus the module’s logging defaults.
- **Repository common overrides**: 21 variables from `data/common.yaml`.
- **Production overrides**: 7 variables from `site-modules/profile_app_stack/data/environment/production.yaml`.
- **Staging overrides**: 6 variables from `site-modules/profile_app_stack/data/environment/staging.yaml`.
- **Environment-specific repository overrides**: 0 currently defined.
- **Encrypted or secret variables**: 2 direct module secrets:
  - `profile_app_stack::db_password`
  - `profile_app_stack::secret_key`
- **Plaintext secrets requiring remediation**:
  - `data/common.yaml` database password
  - `data/common.yaml` secret key
  - `site-modules/profile_app_stack/data/environment/staging.yaml` secret key

### Cross-Level Overrides

- `app_name`: module common and repository common; first-value behavior, with repository common effective.
- `app_repo`: module common and repository common; first-value behavior, with repository common effective.
- `app_revision`: module common, module environment, and repository common; environment-specific value wins.
- `app_port`: module common and repository common; repository common effective.
- `app_dir`: module common and repository common; repository common effective.
- `app_user`: module common and repository common; repository common effective.
- `app_group`: module common and repository common; repository common effective.
- `db_host`: module common, module environment, and repository common; environment-specific value wins.
- `db_port`: module common, module production, and repository common; effective value is `5432`.
- `db_name`: module common and repository common; repository common effective.
- `db_user`: module common and repository common; repository common effective.
- `db_password`: module common and repository common; replace both with one Vault-managed value.
- `worker_count`: module common, module environment, and repository common; environment-specific value wins.
- `worker_class`: module common and repository common; repository common effective.
- `max_requests`: module common, module environment, and repository common; environment-specific value wins.
- `graceful_timeout`: module common and repository common; repository common effective.
- `log_dir`: module common and repository common; repository common effective.
- `log_level`: module common, module environment, and repository common; environment-specific value wins.
- `python_version`: module common and repository common; repository common effective.
- `pip_packages`: module common and repository common; the complete array is replaced by `[]`, not merged.
- `secret_key`: module environment and repository common; environment-specific value wins where defined.

### Merge Strategy Notes

- Scalar values use first-value behavior.
- `pip_packages` uses replacement semantics; arrays are not merged.
- No hash or deep merge behavior is indicated for these variables.
- In Ansible, represent the effective precedence explicitly through role defaults, repository group variables, environment group variables, and Vault variables.

## Custom Types and Providers

No custom types, providers, facts, or functions were detected.

The `profile_app_stack::app_db_url` behavior is not confirmed by the supplied execution tree. Review the original source before implementation and reproduce it only if the source confirms that it is used.

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
- Metadata-declared compatible ranges:
  - `puppetlabs-stdlib`: `>= 9.0.0 < 10.0.0`
  - `puppetlabs-vcsrepo`: `>= 6.0.0 < 7.0.0`

**System package dependencies**:

- `python3`
- Exact `$python_packages` expansion: requires source verification.
- Known module-default pip packages:
  - `uvicorn`
  - `gunicorn`
  - `psycopg2-binary`
- Effective repository configuration sets `pip_packages` to `[]`, so no conditional pip package installation occurs.
- `prometheus-node-exporter` and `prometheus-pushgateway` are declared virtually and are not shown as realized.

**Service dependencies**:

- `profile_app_stack::python` precedes `profile_app_stack::database`.
- `profile_app_stack::database` precedes `profile_app_stack::app`.
- `profile_app_stack::app` notifies `profile_app_stack::service`.
- `profile_app_stack::service` precedes `profile_app_stack::monitoring`.
- `test-app.service` starts after `network.target` and `postgresql.service`.
- `test-app.service` wants `postgresql.service`.

## Puppet Facts Used

- `$facts['environment']`
  - Selects environment-specific Hiera data.
  - Controls production versus non-production `.env` rendering.
  - Controls production virtual monitoring declarations.
- `fact('environment')`
  - Used by `profile::app::stack` and `role::app_server`.
  - Map to an Ansible inventory group or explicit variable such as `deployment_environment`.

## Template Conversion Notes

### `site-modules/profile_app_stack/templates/logrotate.conf.erb`

- Convert to an Ansible-managed logrotate template.
- Variables:
  - `log_dir`
  - `log_rotate_count`
  - `log_max_size`
  - `app_name`
- Preserve the `postrotate` command:
  `systemctl reload test-app 2>/dev/null || true`.

### `site-modules/profile_app_stack/templates/app.env.erb`

- Convert to an Ansible Jinja2 template.
- Preserve database URL construction and all application variables.
- Preserve the production conditional:
  - Production: `DEBUG=false` and restricted CORS origins.
  - Other environments: `DEBUG=true` and wildcard CORS origins.
- Retrieve `db_password` and `secret_key` from Ansible Vault or an external secret provider.
- Render `/opt/test-app/.env` with restrictive permissions, preferably `0600`.
- Do not migrate current plaintext database or signing-key values as plaintext.
- Treat `<vault-secret>` in examples as a proposed post-migration placeholder, not as a current effective Puppet value.

### `site-modules/profile_app_stack/templates/app.service.epp`

- Convert the typed EPP parameters to Jinja2 variables.
- Preserve all service directives and security settings.
- Preserve the arithmetic expression:
  `TimeoutStopSec = graceful_timeout + 5`.
- Use a template handler for `systemctl daemon-reload`.
- Notify a service restart or reload according to the original application-change behavior.

## PuppetDB Dependencies

**Context**: The application stack does not directly use PuppetDB for exported application resources or resource collection.

- **Exported Resources**:
  - No `@@` exported resources are shown for `profile_app_stack`.
  - Monitoring resources use `@` virtual declarations only:
    - `prometheus-node-exporter` package
    - `prometheus-node-exporter` service
    - `prometheus-pushgateway` package
    - `push_app_metrics` cron job
  - No realization operation is shown. The Ansible migration should not create these resources unless the broader configuration confirms that they are realized externally.

- **Resource Collectors**:
  - No `<<| |>>` collectors are shown in the application-stack execution tree.
  - No cross-node resource discovery is required for the analyzed module.

- **PuppetDB Queries**:
  - Dependency code reports the query `title == "/etc/sysconfig/${service_name}"` in `firewall::linux::redhat`.
  - Dependency code reports the query `title == "/etc/sysconfig/${service_name_v6}"` in `firewall::linux::redhat`.
  - These queries belong to dependency code, not to direct `profile_app_stack` resources.
  - The Ansible application-stack migration does not require a PuppetDB equivalent unless the broader firewall role depends on them.

- **Host Identity Data**:
  - No per-host PuppetDB identity data is used directly.
  - The `environment` fact is the only host-classification input used by this module.

## Checks for the Migration

**Files to verify**:

- `site-modules/profile/manifests/app/stack.pp`
- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/python.pp`
- `site-modules/profile_app_stack/manifests/database.pp`
- `site-modules/profile_app_stack/manifests/app.pp`
- `site-modules/profile_app_stack/manifests/service.pp`
- `site-modules/profile_app_stack/manifests/monitoring.pp`
- `site-modules/role/manifests/app_server.pp`
- `site-modules/profile_app_stack/templates/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/app.env.erb`
- `site-modules/profile_app_stack/templates/app.service.epp`
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`
- `site-modules/profile_app_stack/hiera.yaml`
- `site-modules/profile_app_stack/metadata.json`

**Service endpoints to check**:

- **myapp-api/test-app**: `0.0.0.0:8000`
- **PostgreSQL default**: `localhost:5432`
- **PostgreSQL staging**: `localhost:5432`
- **PostgreSQL production**: `db-primary.prod.internal:5432`
- **Application health check**: endpoint invoked by `/usr/local/bin/app-healthcheck.sh`; exact URI requires source verification.

**Templates rendered**:

- `site-modules/profile_app_stack/templates/logrotate.conf.erb` → `/etc/logrotate.d/test-app` — once
- `site-modules/profile_app_stack/templates/app.env.erb` → `/opt/test-app/.env` — once
- `site-modules/profile_app_stack/templates/app.service.epp` → `/etc/systemd/system/test-app.service` — once

## Pre-flight checks

```bash
# Confirm the Python runtime and the exact original package expansion.
python3 --version
# Verify the original $python_packages value from the Puppet source.

# Confirm the application account and group.
getent passwd appuser
getent group appuser

# Confirm application directory ownership and repository revision.
stat -c '%U:%G %a %n' /opt/test-app
git -C /opt/test-app rev-parse --abbrev-ref HEAD
git -C /opt/test-app rev-parse HEAD

# Confirm the virtual environment and Gunicorn executable.
test -x /opt/test-app/venv/bin/gunicorn

# Confirm the environment file is protected and contains no committed plaintext secrets.
stat -c '%a %U:%G %n' /opt/test-app/.env
grep -E '^(DATABASE_URL|SECRET_KEY)=' /opt/test-app/.env

# Validate the systemd unit.
systemd-analyze verify /etc/systemd/system/test-app.service

# Reload systemd, enable the service, and check status.
systemctl daemon-reload
systemctl enable --now test-app
systemctl status test-app

# Verify the application endpoint for myapp-api/test-app.
ss -ltnp | grep ':8000'

# Review application logs and log directory.
journalctl -u test-app
ls -l /var/log/test-app/

# Check default/staging PostgreSQL connectivity.
pg_isready -h localhost -p 5432 -d testdb -U testuser

# Check production PostgreSQL connectivity.
pg_isready -h db-primary.prod.internal -p 5432 -d testdb -U testuser

# Verify database migrations completed successfully.
# Use the application migration command from the original manifest.

# Verify the database backup schedule and script.
test -x /usr/local/bin/db-backup.sh
crontab -l
/usr/local/bin/db-backup.sh

# Verify the application health-check schedule.
crontab -l

# Validate logrotate syntax for the actual rendered file.
logrotate -d /etc/logrotate.d/test-app
```