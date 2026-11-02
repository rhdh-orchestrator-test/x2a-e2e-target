---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: `profile_app_stack` deploys the `test-app` Python application as a systemd service. It creates the application account and log directory, installs Python packages, checks out the application repository, creates a virtual environment, installs requirements and optional packages, renders environment, systemd, and logrotate configuration, runs database migrations, configures local PostgreSQL resources and backups, and installs health-check and monitoring cron jobs. The Prometheus node exporter, Pushgateway, and metrics cron are production-only; the application health-check cron is unconditional. Effective Hiera values, dependency versions, credentials, and several resource implementation details require verification from the original Puppet and Hiera sources before migration.

## Service Type and Instances

**Service Type**: Python application managed by systemd, with optional local PostgreSQL, scheduled backups, health checks, and production monitoring.

**Configured Instances**:

- **`test-app`**: Python application service
  - Application repository: `file:///tmp/test-app-repo`
  - Revision: `master`
  - Application user: `appuser`
  - Application database: `testdb`
  - Database user: `testuser`
  - Database host: `localhost`
  - Database port: `5432`
  - Worker class: `sync`
  - Worker count: `2`
  - Maximum requests: `1000`
  - Log level: `info`
  - Application port: effective value not included in the supplied analysis
  - Application directory: effective path not included in the supplied analysis
  - Log directory: effective path not included in the supplied analysis
  - Database password: `test-db-password` — sensitive; source and precedence require verification
  - Application secret key: `test-secret-key` — sensitive; source and precedence require verification

## File Structure

The following is the complete directory listing supplied for the analyzed execution tree. The broader analysis reportedly covered 97 files, but the remaining files were not enumerated and are not represented below.

```text
site-modules/role/manifests/app_server.pp
site-modules/profile/manifests/app/stack.pp
site-modules/profile_app_stack/manifests/init.pp
site-modules/profile_app_stack/manifests/python.pp
site-modules/profile_app_stack/manifests/database.pp
site-modules/profile_app_stack/manifests/app.pp
site-modules/profile_app_stack/manifests/service.pp
site-modules/profile_app_stack/manifests/monitoring.pp

profile_app_stack/logrotate.conf.erb
profile_app_stack/app.env.erb
profile_app_stack/app.service.epp

data/common.yaml
site-modules/profile_app_stack/data/common.yaml
site-modules/profile_app_stack/data/environment/production.yaml
site-modules/profile_app_stack/data/environment/staging.yaml
```

## Module Explanation

The module is reached through this control-repository chain:

1. **`role::app_server`** (`site-modules/role/manifests/app_server.pp`):
   - Includes `profile::base::base`.
   - Includes `profile::loadbalancer::haproxy`.
   - Includes `profile::app::stack`.
   - Includes `profile::cache::redis`.
   - Reads `fact('environment')`.
   - Only the `profile::app::stack` branch is expanded in this plan. The base, HAProxy, and Redis profiles require separate migration analysis.

2. **`profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`):
   - Includes `profile_app_stack`.
   - Reads `fact('environment')`.

3. **`profile_app_stack`** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Includes `profile_app_stack::python`.
   - Includes `profile_app_stack::database`.
   - Includes `profile_app_stack::app`.
   - Includes `profile_app_stack::service`.
   - Includes `profile_app_stack::monitoring`.
   - Establishes the resource ordering:
     `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`.
   - Application changes notify the service class, requiring a service refresh or restart when applicable.
   - No `.each` loops were identified in the supplied execution tree.

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Installs the package collection represented by `$python_packages`; exact package names require source inspection.
   - Uses `profile_app_stack::python_version`; the effective value requires Hiera verification.
   - Creates the application group, whose title is derived from `profile_app_stack::app_group`.
   - Creates the `appuser` application user.
   - Creates the effective log directory.
   - Renders `/etc/logrotate.d/test-app` from `profile_app_stack/logrotate.conf.erb`.
   - The logrotate template renders once and uses four variables. The related values include `log_dir`, `log_max_size`, and `log_rotate_count`; the fourth variable requires source inspection.

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Evaluates the local-database condition `db_host == 'localhost'`.
   - The effective host is reported as `localhost`; this value and the resulting branch require Hiera verification.
   - Includes `profile_postgresql`, which is external to the analyzed module.
   - Declares `exec[create_db_user]` for database user `testuser`.
   - Declares `exec[create_database]` for database `testdb`.
   - Declares `exec[grant_db_privileges]` for privileges on `testdb` for `testuser`.
   - Declares `file[/usr/local/bin/db-backup.sh]` for the database backup script.
   - Declares `cron[database_backup]` for the database backup job.
   - Commands, guards, refresh behavior, schedules, ownership, modes, and script contents require source inspection.

6. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`):
   - Creates the effective application directory.
   - Checks out `file:///tmp/test-app-repo` into the effective application directory using revision `master`.
   - Uses the external `vcsrepo` resource type.
   - Creates the application Python virtual environment with `exec[create_app_venv]`.
   - Installs repository requirements with `exec[install_requirements]`.
   - Conditionally installs `profile_app_stack::pip_packages` when the list is nonempty.
   - No `.each` loop was identified; the optional package branch executes zero or one installation operation based on whether the list is empty.
   - Renders `<effective app_dir>/.env` from `profile_app_stack/app.env.erb`.
   - The environment template renders once and contains eight variables plus one Ruby logic block. The condition and rendered branches require source inspection.
   - Declares `file[/usr/local/bin/app-healthcheck.sh]`.
   - Runs database migrations with `exec[run_db_migrations]`.
   - Exact commands, paths, guards, working directories, users, file ownership, modes, and script contents require source inspection.

7. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`):
   - Renders `/etc/systemd/system/test-app.service` from `profile_app_stack/app.service.epp`.
   - The service template renders once and contains twelve variables plus one Ruby logic block. The condition and rendered branches require source inspection.
   - Declares `exec[systemd_daemon_reload]` after the unit file changes.
   - Manages `service[test-app]`.
   - Uses the effective application name `test-app`, application user `appuser`, revision `master`, worker class `sync`, worker count `2`, maximum requests `1000`, and log level `info`.
   - Application port, application directory, Python version, and graceful timeout require value verification.
   - The application class notifies this service class through the class-level `~>` relationship.
   - Exact `ExecStart`, environment, restart policy, enablement, status provider, ownership, and mode require source inspection.

8. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Declares virtual resources:
     - `@package[prometheus-node-exporter]`
     - `@service[prometheus-node-exporter]`
     - `@package[prometheus-pushgateway]`
     - `@cron[push_app_metrics]`
   - Realizes the node exporter, Pushgateway, and `push_app_metrics` cron resources only when `$facts['environment'] == 'production'`.
   - Declares `cron[app_health_check]` unconditionally, outside the production conditional.
   - The virtual resources are ordinary Puppet virtual resources, not PuppetDB-exported resources. Implement them as conditionally applied Ansible tasks.
   - Exact schedules, commands, users, and environments require source inspection.

## Variables

**Variable Flow Summary**: 22 module-default variables, 21 control-repository common variables, 7 production environment values, and 6 staging environment values are reported across four Hiera files. The supplied execution-tree analysis does not independently verify these inventories, values, types, or precedence. The reported lookup behavior is first/highest-priority lookup for scalar values rather than hash or deep merging.

### Variable Definitions

**`data/common.yaml` (control-repository common values)** → Migration note: Reported effective common values for all application-stack nodes; verify against the source Hiera data before migration.

- `profile_app_stack::app_name`: `test-app` (type: string) → `app_stack_app_name`
- `profile_app_stack::app_repo`: `file:///tmp/test-app-repo` (type: string) → `app_stack_app_repo`
- `profile_app_stack::app_revision`: `master` (type: string) → `app_stack_app_revision`
- `profile_app_stack::app_port`: effective value not supplied (type: integer, requires verification) → `app_stack_app_port`
- `profile_app_stack::app_dir`: effective value not supplied (type: string, requires verification) → `app_stack_app_dir`
- `profile_app_stack::app_user`: `appuser` (type: string) → `app_stack_app_user`
- `profile_app_stack::app_group`: effective value not separately supplied (type: string, requires verification) → `app_stack_app_group`
- `profile_app_stack::db_host`: `localhost` (type: string) → `app_stack_db_host`
- `profile_app_stack::db_port`: `5432` (type: integer) → `app_stack_db_port`
- `profile_app_stack::db_name`: `testdb` (type: string) → `app_stack_db_name`
- `profile_app_stack::db_user`: `testuser` (type: string) → `app_stack_db_user`
- `profile_app_stack::db_password`: `test-db-password` (type: string, sensitive) → `app_stack_db_password`
- `profile_app_stack::worker_count`: `2` (type: integer) → `app_stack_worker_count`
- `profile_app_stack::worker_class`: `sync` (type: string) → `app_stack_worker_class`
- `profile_app_stack::max_requests`: `1000` (type: integer) → `app_stack_max_requests`
- `profile_app_stack::graceful_timeout`: effective value not supplied (type: integer, requires verification) → `app_stack_graceful_timeout`
- `profile_app_stack::log_dir`: effective value not supplied (type: string, requires verification) → `app_stack_log_dir`
- `profile_app_stack::log_level`: `info` (type: string) → `app_stack_log_level`
- `profile_app_stack::secret_key`: `test-secret-key` (type: string, sensitive) → `app_stack_secret_key`
- `profile_app_stack::python_version`: effective value not supplied (type: string, requires verification) → `app_stack_python_version`
- `profile_app_stack::pip_packages`: effective contents not supplied (type: array, requires verification) → `app_stack_pip_packages`

**`site-modules/profile_app_stack/data/common.yaml` (module defaults)** → Migration note: Base module defaults; reported to be overridden by higher-priority control-repository common data.

- `profile_app_stack::app_name` (type and value require source verification) → `app_stack_app_name`
- `profile_app_stack::app_repo` (type and value require source verification) → `app_stack_app_repo`
- `profile_app_stack::app_revision` (type and value require source verification) → `app_stack_app_revision`
- `profile_app_stack::app_port` (type and value require source verification) → `app_stack_app_port`
- `profile_app_stack::app_dir` (type and value require source verification) → `app_stack_app_dir`
- `profile_app_stack::app_user` (type and value require source verification) → `app_stack_app_user`
- `profile_app_stack::app_group` (type and value require source verification) → `app_stack_app_group`
- `profile_app_stack::db_host` (type and value require source verification) → `app_stack_db_host`
- `profile_app_stack::db_port` (type and value require source verification) → `app_stack_db_port`
- `profile_app_stack::db_name` (type and value require source verification) → `app_stack_db_name`
- `profile_app_stack::db_user` (type and value require source verification) → `app_stack_db_user`
- `profile_app_stack::db_password` (type and value require source verification; reported as encrypted) → `app_stack_db_password`
- `profile_app_stack::worker_count` (type and value require source verification) → `app_stack_worker_count`
- `profile_app_stack::worker_class` (type and value require source verification) → `app_stack_worker_class`
- `profile_app_stack::max_requests` (type and value require source verification) → `app_stack_max_requests`
- `profile_app_stack::graceful_timeout` (type and value require source verification) → `app_stack_graceful_timeout`
- `profile_app_stack::log_dir` (type and value require source verification) → `app_stack_log_dir`
- `profile_app_stack::log_level` (type and value require source verification) → `app_stack_log_level`
- `profile_app_stack::python_version` (type and value require source verification) → `app_stack_python_version`
- `profile_app_stack::pip_packages` (type and value require source verification) → `app_stack_pip_packages`
- `profile_app_stack::log_max_size` (type and value require source verification) → `app_stack_log_max_size`
- `profile_app_stack::log_rotate_count` (type and value require source verification) → `app_stack_log_rotate_count`

**`site-modules/profile_app_stack/data/environment/production.yaml` (production values)** → Migration note: Production-specific values; verify precedence and explicitly define desired values in Ansible production group variables.

- `profile_app_stack::app_revision`: `v2.4.1` (type: string) → `app_stack_app_revision`
- `profile_app_stack::worker_count`: `8` (type: integer) → `app_stack_worker_count`
- `profile_app_stack::max_requests`: `5000` (type: integer) → `app_stack_max_requests`
- `profile_app_stack::log_level`: `warning` (type: string) → `app_stack_log_level`
- `profile_app_stack::db_host`: `db-primary.prod.internal` (type: string) → `app_stack_db_host`
- `profile_app_stack::db_port`: `5432` (type: integer) → `app_stack_db_port`
- `profile_app_stack::secret_key`: encrypted value (type: sensitive string) → `app_stack_secret_key`

**`site-modules/profile_app_stack/data/environment/staging.yaml` (staging values)** → Migration note: Staging-specific values; verify precedence and define desired values in Ansible staging group variables.

- `profile_app_stack::app_revision`: `main` (type: string) → `app_stack_app_revision`
- `profile_app_stack::worker_count`: `1` (type: integer) → `app_stack_worker_count`
- `profile_app_stack::max_requests`: `100` (type: integer) → `app_stack_max_requests`
- `profile_app_stack::log_level`: `debug` (type: string) → `app_stack_log_level`
- `profile_app_stack::db_host`: `localhost` (type: string) → `app_stack_db_host`
- `profile_app_stack::secret_key`: `staging-not-secret-at-all` (type: string, sensitive) → `app_stack_secret_key`

### Variable Migration Summary

- **Common defaults**: 21 reported control-repository variables from `data/common.yaml`; verify inventory and effective values.
- **Module defaults**: 22 reported variables from `site-modules/profile_app_stack/data/common.yaml`; verify inventory, types, and values.
- **Environment-specific variables**: 7 production variables and 6 staging variables.
- **Host-specific variables**: 0 supplied.
- **OS-specific variables**: 0 supplied.
- **Encrypted variables**: Reported encrypted module-level database password and production secret key; secure-storage requirements require source verification.
- **Ansible mapping**: All listed Puppet keys map to the corresponding `app_stack_*` names shown above.

### Cross-Level Overrides

The following variables are reported at multiple levels:

- `app_revision`: module defaults, production or staging data, and common control-repository data; reported effective value: `master`.
- `worker_count`: module defaults, production or staging data, and common control-repository data; reported effective value: `2`.
- `max_requests`: module defaults, production or staging data, and common control-repository data; reported effective value: `1000`.
- `log_level`: module defaults, production or staging data, and common control-repository data; reported effective value: `info`.
- `db_host`: module defaults, production or staging data, and common control-repository data; reported effective value: `localhost`.
- `db_port`: module defaults, production data, and common control-repository data; reported effective value: `5432`.
- `secret_key`: module/common data plus production and staging values; reported effective value: plaintext `test-secret-key`.
- `db_password`: module-level encrypted value and common control-repository plaintext value; reported effective value: plaintext `test-db-password`.

### Merge Strategy Notes

- Scalar values use first/highest-priority lookup according to the reported behavior.
- Variables using `hash` merge would be shallow-merged; no confirmed hash-merge variables were supplied.
- Variables using `deep` merge would be recursively merged; no confirmed deep-merge variables were supplied.
- `pip_packages` should be explicitly defined in Ansible rather than relying on implicit Puppet merge behavior.

## Credentials and Secret Handling

- `profile_app_stack::db_password`:
  - Reported effective value: plaintext `test-db-password`.
  - Also reported as an encrypted module-level value.
  - Migrate to `app_stack_db_password` in Ansible Vault or an external secret backend.
  - Do not expose it in task output, logs, rendered-file diagnostics, or world-readable files.

- `profile_app_stack::secret_key`:
  - Reported effective value: plaintext `test-secret-key`.
  - Production reportedly contains an encrypted value overridden by the common plaintext value.
  - Migrate to `app_stack_secret_key` in Ansible Vault or an external secret backend.
  - Remove any insecure `changeme` fallback after confirming it in the source.

- External Redis credentials requiring separate profile analysis:
  - Redis `masterauth`
  - Redis `requirepass`
  - Redis Sentinel authentication password
  - Redis TLS private-key file references
  - Redis Sentinel TLS private-key file reference

## Dependencies

**External module dependencies**: The supplied plan reports the following dependencies, but exact versions are not supported by the supplied execution-tree analysis and must be verified from `Puppetfile` or `metadata.json`:

- `puppetlabs-stdlib`
- `puppetlabs-concat`
- `puppetlabs-firewall`
- `puppetlabs-vcsrepo`
- `puppet-redis`
- `puppet-systemd`
- `puppetlabs-inifile`
- `puppetlabs-apt`

The analyzed tree directly exposes the `vcsrepo` resource type. `profile_postgresql`, the base profile, HAProxy profile, and Redis profile are external classes requiring separate analysis.

**System package dependencies**:

- Python package collection represented by `$python_packages`; exact package names require source inspection.
- `prometheus-node-exporter`, production only.
- `prometheus-pushgateway`, production only.
- Python and pip prerequisites for virtual-environment and requirement installation require verification.

**Service dependencies**:

- Python setup precedes database setup.
- Database setup precedes application checkout and configuration.
- Application configuration and migrations precede service configuration.
- Systemd daemon reload follows changes to the unit file.
- Application changes notify `test-app`.
- Monitoring follows the application service class.
- The local PostgreSQL branch is active only if the verified effective database host is `localhost`.

## Puppet Facts Used

- `$facts['environment']`:
  - Determines whether production-only node exporter, Pushgateway, and `push_app_metrics` resources are applied.
  - Resources are applied when the value is `production`.

- `fact('environment')`:
  - Read by `role::app_server`.
  - Read by `profile::app::stack`.
  - No additional behavior tied to these reads is exposed in the supplied analysis.

## Template Conversion Notes

### `profile_app_stack/logrotate.conf.erb`

- Destination: `/etc/logrotate.d/test-app`
- Render count: `1`
- Variables: `4`
- Related values:
  - Application name: `test-app`
  - Log directory: `app_stack_log_dir`
  - Maximum log size: `app_stack_log_max_size`
  - Rotation count: `app_stack_log_rotate_count`
- No complex Ruby logic was reported.
- Convert to a Jinja2 template after verifying the fourth variable and the exact logrotate directives.

### `profile_app_stack/app.env.erb`

- Destination: `<effective app_stack_app_dir>/.env`
- Render count: `1`
- Variables: `8`
- Reported values:
  - Application name: `test-app`
  - Database host: `localhost`
  - Database port: `5432`
  - Database name: `testdb`
  - Database user: `testuser`
  - Database password: `test-db-password`
  - Application secret key: `test-secret-key`
  - Log level: `info`
- Contains one Ruby logic block.
- The condition and rendered branches are not exposed in the supplied analysis and require source inspection before conversion.
- Use an Ansible Jinja2 template with restrictive ownership and permissions.
- Use `no_log: true` for secret-bearing tasks where task output could expose values.

### `profile_app_stack/app.service.epp`

- Destination: `/etc/systemd/system/test-app.service`
- Render count: `1`
- Variables: `12`
- Reported values:
  - Service name: `test-app`
  - User: `appuser`
  - Worker class: `sync`
  - Worker count: `2`
  - Maximum requests: `1000`
  - Log level: `info`
  - Application port: effective value not supplied
  - Application directory: effective path not supplied
  - Graceful timeout: effective value not supplied
  - Python version: effective value not supplied
- Contains one Ruby logic block.
- The condition and rendered branches require source inspection.
- Deploy with Ansible `template`, then notify a handler that runs `systemctl daemon-reload` and restarts or reloads `test-app` according to the verified Puppet service behavior.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/app_server.pp`
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
- `data/common.yaml`
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `Puppetfile` or `metadata.json`, if present, for dependency verification

**Service endpoints to check**:

- `test-app` on the verified effective application port.
- PostgreSQL at `localhost:5432` when the local-database branch is active.
- Prometheus node exporter endpoint in production; port requires verification.
- Pushgateway endpoint in production; port requires verification.

**Templates rendered**:

- `profile_app_stack/logrotate.conf.erb` — 1 render
- `profile_app_stack/app.env.erb` — 1 render
- `profile_app_stack/app.service.epp` — 1 render

**Pre-flight checks**:

- For **`test-app`**, verify:
  - `app_stack_app_name` is `test-app`.
  - `app_stack_app_repo` is `file:///tmp/test-app-repo`.
  - `app_stack_app_revision` is `master`, unless environment-specific behavior is intentionally restored.
  - `app_stack_app_user` is `appuser`.
  - `app_stack_app_group` is explicitly confirmed.
  - `app_stack_app_dir` is explicitly confirmed.
  - `app_stack_app_port` is explicitly confirmed.
  - `app_stack_log_dir` is explicitly confirmed.
  - `app_stack_python_version`, `app_stack_graceful_timeout`, and `app_stack_pip_packages` are explicitly confirmed.
  - The repository is available at `file:///tmp/test-app-repo`.
  - Python, pip, and required system packages are installed.
  - PostgreSQL is running and accepting connections at `localhost:5432` if the local branch is intended.
  - Database `testdb` and user `testuser` can be created or verified.
  - Database migrations complete successfully.
  - The rendered environment file has restrictive permissions and does not expose secrets through Ansible output.
  - `systemd-analyze verify /etc/systemd/system/test-app.service` succeeds.
  - `systemctl daemon-reload` completes successfully.
  - `systemctl enable --now test-app` succeeds.
  - `systemctl status test-app` reports the expected state.
  - Application logs are written to the verified log directory.
  - The database backup cron and unconditional application health-check cron are installed and runnable.

- Confirm the target environment is represented explicitly in Ansible inventory or group variables.
- Confirm whether production should use:
  - Revision `v2.4.1` instead of `master`.
  - Database host `db-primary.prod.internal` instead of `localhost`.
  - Worker count `8` instead of `2`.
  - Maximum requests `5000` instead of `1000`.
  - Log level `warning` instead of `info`.
- Confirm whether staging should use:
  - Revision `main`.
  - Worker count `1`.
  - Maximum requests `100`.
  - Log level `debug`.
- In production, verify:
  - `systemctl status prometheus-node-exporter`.
  - `systemctl status prometheus-pushgateway`.
  - `push_app_metrics` publishes successfully.
- Confirm that the application health-check cron is configured in every environment, not only production.
- Confirm rendered `.env` and systemd files do not expose secrets through task output, logs, or world-readable permissions.
