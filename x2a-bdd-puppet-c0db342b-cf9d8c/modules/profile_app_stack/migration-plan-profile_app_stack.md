---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: `profile_app_stack` provisions a Python application from a VCS repository, creates its runtime account and directories, prepares a Python virtual environment, installs dependencies, renders environment and systemd configuration, optionally provisions a local PostgreSQL database, runs migrations, configures database backups and health checks, and enables production Prometheus monitoring. The execution order is `role::app_stack` → `profile::app::stack` → `profile_app_stack::python` → `profile_app_stack::database` → `profile_app_stack::app` → `profile_app_stack::service` → `profile_app_stack::monitoring`. Hiera values, hierarchy, dependency versions, and several command details require verification against the actual source files before migration.

## Service Type and Instances

**Service Type**: Python application service with PostgreSQL, systemd, cron, and Prometheus monitoring integration.

**Configured Instances**:

- **Application service**
  - Name: `profile_app_stack::app_name`; value requires Hiera verification.
  - Repository: `profile_app_stack::app_repo`; value requires Hiera verification.
  - Revision: reported as `master`; verify against Hiera.
  - Application directory: `profile_app_stack::app_dir`; value requires Hiera verification.
  - Port: `profile_app_stack::app_port`; value requires Hiera verification.
  - User/group: `profile_app_stack::app_user` and `profile_app_stack::app_group`; values require Hiera verification.
  - Workers: reported as `2`; verify against Hiera.
  - Worker class: `profile_app_stack::worker_class`; value requires Hiera verification.
  - Maximum requests: reported as `1000`; verify against Hiera.
  - Graceful timeout: `profile_app_stack::graceful_timeout`; value requires Hiera verification.
  - Log directory: `profile_app_stack::log_dir`; value requires Hiera verification.
  - Log level: reported as `info`; verify against Hiera.

- **Database**
  - Host: reported as `localhost`; verify against Hiera.
  - Port: reported as `5432`; verify against Hiera.
  - Database name: `profile_app_stack::db_name`; value requires Hiera verification.
  - Database user: `profile_app_stack::db_user`; value requires Hiera verification.
  - Password: reported plaintext value `test-db-password`; migrate to Ansible Vault or an external secret manager.
  - Local-database branch: enabled when `db_host == 'localhost'`.
  - Provisioning resources: `Class['profile_postgresql']`, `Exec[create_db_user]`, `Exec[create_database]`, and `Exec[grant_db_privileges]`.

- **Database backup**
  - Script: `/usr/local/bin/db-backup.sh`.
  - Cron resource: `database_backup`.
  - Schedule, destination, retention, credentials, and command require source verification.

- **Application health check**
  - Script: `/usr/local/bin/app-healthcheck.sh`.
  - Cron resource: `app_health_check`.
  - Created outside the production conditional and therefore expected in all environments unless additional logic exists.

- **Production monitoring**
  - Package: `prometheus-node-exporter`.
  - Service: `prometheus-node-exporter`.
  - Package: `prometheus-pushgateway`.
  - Cron resource: `push_app_metrics`.
  - These resources are created only when `$facts['environment'] == 'production'`.

## File Structure

```text
site-modules/
├── role/
│   └── manifests/
│       └── app_stack.pp
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
    └── data/
        ├── common.yaml
        └── environment/
            ├── production.yaml
            └── staging.yaml

data/
├── common.yaml
└── environment/
    ├── production.yaml
    └── staging.yaml

profile_app_stack/
├── logrotate.conf.erb
├── app.env.erb
└── app.service.epp
```

The supplied plan identifies the following files:

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
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`

## Module Explanation

The module performs operations in the following order.

1. **`role::app_stack`** (`site-modules/role/manifests/app_stack.pp`)
   - Evaluates `$facts['kernel'].downcase == 'linux'`.
   - On Linux, creates `Exec[None]`; its command and attributes require source verification.
   - On non-Linux systems, the Linux-only resource is not created.
   - References `Class['::profile::base::base']`.
   - References `Class['::profile::app::stack']`.
   - Orders `Class['::profile::base::base']` before `Class['::profile::app::stack']`.

2. **`profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`)
   - Includes `Class['profile_app_stack']`.
   - Provides the profile layer between the role and the application module.

3. **`profile_app_stack`** (`site-modules/profile_app_stack/manifests/init.pp`)
   - Includes `Class['profile_app_stack::python']`.
   - Includes `Class['profile_app_stack::database']`.
   - Includes `Class['profile_app_stack::app']`.
   - Includes `Class['profile_app_stack::service']`.
   - Includes `Class['profile_app_stack::monitoring']`.
   - Orders Python before database.
   - Orders database before application setup.
   - Refreshes the service class when application resources change.
   - Orders the service class before monitoring.
   - No `.each` loops are present in the supplied execution tree.

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`)
   - Manages `package[$python_packages]`; package names and versions require source verification.
   - Creates `group[$profile_app_stack::app_group]`.
   - Creates `user[$profile_app_stack::app_user]`.
   - Creates `file[$profile_app_stack::log_dir]` as a directory.
   - Creates `/etc/logrotate.d/${profile_app_stack::app_name}` as a file.
   - Renders `profile_app_stack/logrotate.conf.erb` once.
   - The logrotate template contains four referenced variables; their names and logic require template extraction.

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`)
   - Evaluates `if $profile_app_stack::db_host == 'localhost'`.
   - When enabled, includes `Class['profile_postgresql']`.
   - Creates `Exec[create_db_user]`; command and credentials handling require source verification.
   - Creates `Exec[create_database]`; command and arguments require source verification.
   - Creates `Exec[grant_db_privileges]`; command and privilege set require source verification.
   - Creates `/usr/local/bin/db-backup.sh`.
   - Creates `Cron[database_backup]`; schedule and command require source verification.
   - Database credentials must not be exposed in shell arguments. Use Ansible Vault, an external secret provider, a protected environment file, or PostgreSQL `.pgpass`.

6. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`)
   - Creates `file[$profile_app_stack::app_dir]` as the application directory.
   - Manages `vcsrepo[$profile_app_stack::app_dir]`.
   - Uses `profile_app_stack::app_repo` as the repository and the reported revision `master`; both require Hiera verification.
   - Creates `Exec[create_app_venv]`.
   - Creates `Exec[install_requirements]`.
   - Evaluates `if !empty($pip_packages)`.
   - The supplied execution tree does not identify a resource inside the `pip_packages` conditional. Treat the conditional as unresolved until the manifest is inspected.
   - Creates `${profile_app_stack::app_dir}/.env`.
   - Renders `profile_app_stack/app.env.erb` once.
   - The environment template contains eight referenced variables and two logic blocks; exact names and logic require template extraction.
   - Creates `/usr/local/bin/app-healthcheck.sh`.
   - Creates `Exec[run_db_migrations]`.
   - Application migrations run after database resources and application source setup.

7. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`)
   - Creates `/etc/systemd/system/${profile_app_stack::app_name}.service`.
   - Renders `profile_app_stack/app.service.epp` once.
   - The service template contains twelve referenced variables and two logic blocks; exact directives require template extraction.
   - Creates `Exec[systemd_daemon_reload]`.
   - Manages `service[$profile_app_stack::app_name]` with `ensure => running`.
   - Application changes refresh the service class according to the manifest’s notification semantics.
   - The unit must be daemon-reloaded after changes and before service activation or restart.

8. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`)
   - Declares virtual resources:
     - `@package[prometheus-node-exporter]`
     - `@service[prometheus-node-exporter]`
     - `@package[prometheus-pushgateway]`
     - `@cron[push_app_metrics]`
   - Evaluates `$facts['environment'] == 'production'`.
   - In production, realizes or creates:
     - `package[prometheus-node-exporter]`
     - `service[prometheus-node-exporter]`
     - `package[prometheus-pushgateway]`
     - `cron[push_app_metrics]`
   - Creates `cron[app_health_check]` outside the production conditional.
   - In staging and other non-production environments, production-only monitoring resources are not created by this conditional.

## Variables

**Variable Flow Summary**: The supplied plan identifies 22 module-common variables, 7 module-production variables, 6 module-staging variables, and 21 repository-common variables. The Hiera files, values, types, and lookup hierarchy were not present in the validated structured analysis; all values below are therefore source claims requiring verification.

### Variable Definitions

#### `site-modules/profile_app_stack/data/common.yaml` — module defaults

Migration note: Intended as the module-wide default layer. File contents and exact values require verification.

- `profile_app_stack::app_name`: value not verified (type: string)
- `profile_app_stack::app_repo`: value not verified (type: string)
- `profile_app_stack::app_revision`: value not verified (type: string)
- `profile_app_stack::app_port`: value not verified (type: integer)
- `profile_app_stack::app_dir`: value not verified (type: string)
- `profile_app_stack::app_user`: value not verified (type: string)
- `profile_app_stack::app_group`: value not verified (type: string)
- `profile_app_stack::db_host`: value not verified (type: string)
- `profile_app_stack::db_port`: value not verified (type: integer)
- `profile_app_stack::db_name`: value not verified (type: string)
- `profile_app_stack::db_user`: value not verified (type: string)
- `profile_app_stack::db_password`: encrypted value reported, not verified (type: sensitive string)
- `profile_app_stack::worker_count`: value not verified (type: integer)
- `profile_app_stack::worker_class`: value not verified (type: string)
- `profile_app_stack::max_requests`: value not verified (type: integer)
- `profile_app_stack::graceful_timeout`: value not verified (type: integer)
- `profile_app_stack::log_dir`: value not verified (type: string)
- `profile_app_stack::log_level`: value not verified (type: string)
- `profile_app_stack::python_version`: value not verified (type: string)
- `profile_app_stack::pip_packages`: value not verified (type: array)
- `profile_app_stack::log_max_size`: value not verified (type: integer)
- `profile_app_stack::log_rotate_count`: value not verified (type: integer)

#### `site-modules/profile_app_stack/data/environment/production.yaml` — production overrides

Migration note: Intended as production-specific data loaded conditionally by environment. File contents and exact values require verification.

- `profile_app_stack::app_revision`: value not verified (type: string)
- `profile_app_stack::worker_count`: value not verified (type: integer)
- `profile_app_stack::max_requests`: value not verified (type: integer)
- `profile_app_stack::log_level`: value not verified (type: string)
- `profile_app_stack::db_host`: value not verified (type: string)
- `profile_app_stack::db_port`: value not verified (type: integer)
- `profile_app_stack::secret_key`: encrypted value reported, not verified (type: sensitive string)

#### `site-modules/profile_app_stack/data/environment/staging.yaml` — staging overrides

Migration note: Intended as staging-specific data loaded conditionally by environment. The detailed supplied list contains six keys, not seven.

- `profile_app_stack::app_revision`: value not verified (type: string)
- `profile_app_stack::worker_count`: value not verified (type: integer)
- `profile_app_stack::max_requests`: value not verified (type: integer)
- `profile_app_stack::log_level`: value not verified (type: string)
- `profile_app_stack::db_host`: value not verified (type: string)
- `profile_app_stack::secret_key`: plaintext value reported, not verified (type: sensitive string)

#### `data/common.yaml` — repository-common data

Migration note: Intended as the repository-level common layer. The supplied plan lists 21 keys. Exact file contents and precedence require verification.

- `profile_app_stack::app_name`: value not verified (type: string)
- `profile_app_stack::app_repo`: value not verified (type: string)
- `profile_app_stack::app_revision`: reported as `master` (type: string; verify)
- `profile_app_stack::app_port`: value not verified (type: integer)
- `profile_app_stack::app_dir`: value not verified (type: string)
- `profile_app_stack::app_user`: value not verified (type: string)
- `profile_app_stack::app_group`: value not verified (type: string)
- `profile_app_stack::db_host`: reported as `localhost` (type: string; verify)
- `profile_app_stack::db_port`: reported as `5432` (type: integer; verify)
- `profile_app_stack::db_name`: value not verified (type: string)
- `profile_app_stack::db_user`: value not verified (type: string)
- `profile_app_stack::db_password`: reported as `test-db-password` (type: sensitive string; replace)
- `profile_app_stack::worker_count`: reported as `2` (type: integer; verify)
- `profile_app_stack::worker_class`: value not verified (type: string)
- `profile_app_stack::max_requests`: reported as `1000` (type: integer; verify)
- `profile_app_stack::graceful_timeout`: value not verified (type: integer)
- `profile_app_stack::log_dir`: value not verified (type: string)
- `profile_app_stack::log_level`: reported as `info` (type: string; verify)
- `profile_app_stack::secret_key`: reported as `test-secret-key` (type: sensitive string; replace)
- `profile_app_stack::python_version`: value not verified (type: string)
- `profile_app_stack::pip_packages`: value not verified (type: array)

#### `data/environment/production.yaml`

Migration note: The supplied plan reports no `profile_app_stack` keys in this file. It reportedly contains unrelated NTP and syslog settings; verify before migration.

- No verified `profile_app_stack` variables.

#### `data/environment/staging.yaml`

Migration note: The supplied plan reports no `profile_app_stack` keys in this file. It reportedly contains unrelated syslog settings; verify before migration.

- No verified `profile_app_stack` variables.

### Variable Migration Summary

- **Module-common defaults**: 22 reported variables from `site-modules/profile_app_stack/data/common.yaml`; values require verification.
- **Module production variables**: 7 reported variables from `site-modules/profile_app_stack/data/environment/production.yaml`; values require verification.
- **Module staging variables**: 6 variables listed in the supplied data summary; reconcile against the source file.
- **Repository-common variables**: 21 variables listed in `data/common.yaml`.
- **Repository environment-specific variables**: 0 `profile_app_stack` variables reported in the supplied plan.
- **Encrypted or credential-bearing variables**:
  - `profile_app_stack::db_password`
  - `profile_app_stack::secret_key`
- **Plaintext credentials requiring replacement**:
  - `test-db-password`
  - `test-secret-key`

### Cross-Level Overrides

The supplied plan reports higher-priority repository values overriding module defaults. This precedence requires verification against the actual Hiera configuration.

- `profile_app_stack::app_revision`: module common, module production/staging, and repository common; reported effective value `master`.
- `profile_app_stack::worker_count`: module common, module production/staging, and repository common; reported effective value `2`.
- `profile_app_stack::max_requests`: module common, module production/staging, and repository common; reported effective value `1000`.
- `profile_app_stack::log_level`: module common, module production/staging, and repository common; reported effective value `info`.
- `profile_app_stack::db_host`: module common, module production/staging, and repository common; reported effective value `localhost`.
- `profile_app_stack::db_port`: module common, module production, and repository common; reported effective value `5432`.
- `profile_app_stack::db_password`: module common and repository common; reported repository value `test-db-password`; replace with vaulted data.
- `profile_app_stack::secret_key`: module production, module staging, and repository common; reported repository value `test-secret-key`; replace with environment-specific vaulted data.
- `profile_app_stack::python_version`: module common and repository common; lookup usage requires manifest validation.
- `profile_app_stack::pip_packages`: module common and repository common; lookup usage requires manifest validation.

### Merge Strategy Notes

- No hash or deep-merge behavior was identified.
- The supplied plan describes scalar values as using higher-priority override behavior.
- Treat the merge strategy as `first`/highest-priority value until the actual Hiera configuration confirms otherwise.
- Do not use `hash` or `deep` merging for these variables unless explicitly configured.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.7.0` — version reported in the supplied plan; verify against `Puppetfile`.
- `puppetlabs-concat` `9.0.2` — version reported; verify.
- `puppetlabs-firewall` `8.1.3` — version reported; verify.
- `puppetlabs-vcsrepo` `6.1.0` — provides `vcsrepo`; verify.
- `puppet-redis` `11.0.0` — dependency inventory item reported; relevance to this execution tree requires verification.
- `puppet-systemd` `7.1.0` — version reported; verify.
- `puppetlabs-inifile` `6.1.1` — version reported; verify.
- `puppetlabs-apt` `9.4.0` — version reported; verify.
- `profile_postgresql` — external class used by the local database branch; implementation was not analyzed.

**System package dependencies**:

- Python package list represented by `$python_packages`; exact names and versions require verification.
- `prometheus-node-exporter` in production.
- `prometheus-pushgateway` in production.
- PostgreSQL packages implied by `profile_postgresql`; exact package names require analysis of that class.

**Service dependencies**:

- `Class['::profile::base::base']` before `Class['::profile::app::stack']`.
- `profile_app_stack::python` before `profile_app_stack::database`.
- `profile_app_stack::database` before `profile_app_stack::app`.
- Application changes refresh `profile_app_stack::service`.
- `profile_app_stack::service` before `profile_app_stack::monitoring`.
- Local PostgreSQL provisioning before database migrations.
- Systemd daemon reload after unit rendering and before service activation or restart.

## Puppet Facts Used

- `$facts['kernel']`
  - Identifies the operating-system kernel.
  - Converted to lowercase and compared with `linux`.
  - Controls the Linux-only `Exec[None]` branch.

- `$facts['environment']`
  - Identifies the Puppet environment.
  - Compared exactly with `production`.
  - Controls production Prometheus packages, service, and metrics cron.

## Template Conversion Notes

### `profile_app_stack/logrotate.conf.erb`

- Destination: `/etc/logrotate.d/${app_name}`.
- Render count: 1.
- Referenced variable count: 4.
- Exact variable names, conditionals, rotation frequency, compression, retention, ownership, and post-rotate behavior require extraction from the template.
- Convert ERB syntax to Jinja2 while preserving all rendered behavior.

### `profile_app_stack/app.env.erb`

- Destination: `${app_dir}/.env`.
- Render count: 1.
- Referenced variable count: 8.
- Logic block count: 2.
- Exact variable names and conditional behavior require extraction from the template.
- The supplied plan reports database and application secrets associated with this file, but those references require template verification.
- Store `db_password` and `secret_key` in Ansible Vault or an external secret provider.
- Use restrictive ownership and permissions.
- Preserve behavior for undefined, empty, and false values.

### `profile_app_stack/app.service.epp`

- Destination: `/etc/systemd/system/${app_name}.service`.
- Render count: 1.
- Referenced variable count: 12.
- Logic block count: 2.
- Exact variable names and systemd directives require extraction from the template.
- Preserve the rendered `ExecStart`, working directory, user/group, environment-file reference, restart policy, resource limits, and logging directives.
- Run `systemctl daemon-reload` when the rendered unit changes.
- Restart or reload the application service according to the Puppet refresh behavior.

## PuppetDB Dependencies

The supplied execution tree does not show PuppetDB queries, exported resources, or collectors. A separate dependency scan reported the following items, which must be confirmed independently:

- **Exported resources**:
  - No `@@` exported resources were identified for `profile_app_stack`.
  - The monitoring declarations use virtual resources, but the execution tree shows production resources declared explicitly rather than collected through PuppetDB.

- **Resource collectors**:
  - A separate scan reported the following collectors in `firewall::linux::redhat`:
    - `File <| title == "/etc/sysconfig/${service_name}" |>`
    - `File <| title == "/etc/sysconfig/${service_name_v6}" |>`
  - These collectors are outside the supplied `profile_app_stack` execution tree and require dependency-source verification before migration.

- **PuppetDB queries**:
  - No `puppetdb_query()` calls were identified in the supplied plan.
  - Confirm through a complete dependency scan.

- **Host identity data**:
  - No per-host PuppetDB classification or host identity lookup was identified.
  - The module uses `$facts['kernel']` and `$facts['environment']` for local classification.

- **Virtual resources**:
  - `@package[prometheus-node-exporter]`
  - `@service[prometheus-node-exporter]`
  - `@package[prometheus-pushgateway]`
  - `@cron[push_app_metrics]`
  - In Ansible, implement the production condition explicitly rather than relying on PuppetDB realization.

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
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`

**Service endpoints to check**:

- **Application service**: `profile_app_stack::app_port`; concrete port requires Hiera verification.
- **PostgreSQL database**: reported host `localhost`, port `5432`; verify both values.
- **Prometheus node exporter**: endpoint and port require monitoring configuration verification.
- **Prometheus Pushgateway**: endpoint and port require configuration verification.
- **Application health check**: command, URL, and endpoint require manifest verification.

**Templates rendered**:

- `profile_app_stack/logrotate.conf.erb` — 1 render.
- `profile_app_stack/app.env.erb` — 1 render.
- `profile_app_stack/app.service.epp` — 1 render.

**Instance-specific checks**:

- **Application service**
  - Confirm the resolved application name, repository, revision, directory, user, group, port, worker class, timeout, and log directory.
  - Confirm the repository checkout uses the intended provider and revision.
  - Confirm the virtual environment exists.
  - Confirm requirements installation is idempotent.
  - Confirm `.env` ownership, permissions, and secret rendering.
  - Confirm database migrations complete successfully.
  - Confirm the systemd service is enabled, running, and reachable on the configured application port.

- **PostgreSQL database**
  - Confirm the local-database branch is enabled only when the host is `localhost`.
  - Confirm PostgreSQL package, service, database, and user provisioning.
  - Confirm database privileges for the application user.
  - Confirm connectivity on the configured host and port.
  - Confirm passwords are not exposed in process arguments or logs.

- **Database backup**
  - Confirm `/usr/local/bin/db-backup.sh` exists, is executable, and has restrictive ownership and permissions.
  - Confirm the `database_backup` cron schedule, command, destination, retention, and credentials.
  - Execute a backup test and verify restoration prerequisites.

- **Application health check**
  - Confirm `/usr/local/bin/app-healthcheck.sh` exists and is executable.
  - Confirm the `app_health_check` cron schedule and command.
  - Execute the health check manually and verify failure reporting.

- **Production monitoring**
  - Confirm `prometheus-node-exporter` is installed and running.
  - Confirm `prometheus-pushgateway` is installed.
  - Confirm `push_app_metrics` has the expected schedule and command.
  - Confirm exporter and Pushgateway endpoints.

- **Staging monitoring**
  - Confirm production-only Prometheus packages, service, and `push_app_metrics` are absent.
  - Confirm `app_health_check` remains configured.

## Pre-flight checks

```bash
# Confirm the target operating system
uname -s
test "$(uname -s)" = "Linux"

# Confirm the application account and group after variable resolution
getent passwd "<app_user>"
getent group "<app_group>"

# Confirm the application directory and repository
test -d "<app_dir>"
git -C "<app_dir>" rev-parse --is-inside-work-tree
git -C "<app_dir>" rev-parse --abbrev-ref HEAD

# Confirm the Python runtime and virtual environment
python3 --version
test -x "<app_dir>/venv/bin/python"
"<app_dir>/venv/bin/python" -m pip check

# Confirm application configuration file permissions
stat -c '%U:%G %a %n' "<app_dir>/.env"
test "$(stat -c '%a' "<app_dir>/.env")" = "600"

# Confirm PostgreSQL connectivity
pg_isready -h localhost -p 5432
psql -h localhost -p 5432 -U "<db_user>" -d "<db_name>" -c 'SELECT 1;'

# Confirm database backup script
test -x /usr/local/bin/db-backup.sh
/usr/local/bin/db-backup.sh

# Confirm health-check script
test -x /usr/local/bin/app-healthcheck.sh
/usr/local/bin/app-healthcheck.sh

# Confirm logrotate configuration
logrotate -d "/etc/logrotate.d/<app_name>"

# Confirm systemd unit syntax and reload
systemd-analyze verify "/etc/systemd/system/<app_name>.service"
systemctl daemon-reload

# Confirm the application service instance
systemctl enable --now "<app_name>"
systemctl is-enabled "<app_name>"
systemctl is-active "<app_name>"
systemctl status "<app_name>" --no-pager

# Confirm application endpoint
curl --fail --silent --show-error "http://127.0.0.1:<app_port>/"

# Confirm production monitoring instance
systemctl is-active prometheus-node-exporter
systemctl status prometheus-node-exporter --no-pager
rpm -q prometheus-node-exporter prometheus-pushgateway 2>/dev/null || \
  dpkg-query -W prometheus-node-exporter prometheus-pushgateway

# Confirm cron entries
crontab -l
grep -R "database_backup\|app_health_check\|push_app_metrics" /etc/cron* /var/spool/cron* 2>/dev/null || true

# Confirm no plaintext credentials remain in migrated configuration
grep -R "test-db-password\|test-secret-key" /etc /opt /srv 2>/dev/null || true
```