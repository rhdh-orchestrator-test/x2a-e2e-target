---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: `profile_app_stack` deploys a Python application from a VCS repository, creates its runtime user, group, log directory, and logrotate configuration, installs Python dependencies, optionally provisions a local PostgreSQL database, renders application and systemd configuration, runs database migrations, and schedules health-check and backup jobs. Monitoring resources are declared as Puppet virtual resources and are not realized by the supplied execution tree. The Ansible migration must preserve the order of Python setup → database setup → application deployment → systemd service → monitoring, while moving all credentials to Ansible Vault or an external secret manager. Hiera values, exact resource attributes, command contents, and template variable names require source verification.

## Service Type and Instances

**Service Type**: Python application service with optional local PostgreSQL integration and Prometheus-oriented monitoring hooks.

**Configured Instances**:

- **test-app**
  - Purpose: Python application systemd service.
  - Location/Path: `/opt/test-app`
  - Port/Socket: `profile_app_stack::app_port` integer; literal value requires verification.
  - Repository: `file:///tmp/test-app-repo`
  - Revision: `master` in supplied repository/test data; production and staging override this value, pending Hiera verification.
  - User: `appuser`
  - Group: `profile_app_stack::app_group`; literal value requires verification.
  - Python version: `profile_app_stack::python_version`; literal value requires verification.
  - Worker count: `profile_app_stack::worker_count`; declared as an integer, but the supplied summary also associates `sync` with this value. Resolve before migration.
  - Worker class: `profile_app_stack::worker_class`; literal value requires verification.
  - Maximum requests: `profile_app_stack::max_requests`; production and staging override this value, pending Hiera verification.
  - Graceful timeout: `profile_app_stack::graceful_timeout`; literal value requires verification.
  - Log directory: `/var/log/test-app`
  - Log level: `sync` in supplied repository/test data; production and staging override this value, pending Hiera verification.
  - Unit file: `/etc/systemd/system/test-app.service`

- **Database**
  - Purpose: Application PostgreSQL database.
  - Host: `testdb` in supplied repository/test data; production and staging override this value, pending Hiera verification.
  - Port: `profile_app_stack::db_port` integer; literal value requires verification.
  - Database name: `testdb` in supplied repository/test data.
  - Database user: `testuser` in supplied repository/test data.
  - Password: Vault-backed `vault_app_stack_db_password`; do not migrate or reproduce the plaintext source value.
  - Local PostgreSQL mode: enabled only when the effective `db_host` is exactly `localhost`.
  - Backup script: `/usr/local/bin/db-backup.sh`

- **prometheus-node-exporter**
  - Purpose: Prometheus node metrics.
  - Resources: Virtual package and virtual service declarations.
  - Realization: Not realized in the supplied execution tree.

- **prometheus-pushgateway**
  - Purpose: Prometheus push gateway support.
  - Resource: Virtual package declaration.
  - Realization: Not realized in the supplied execution tree.

- **push_app_metrics**
  - Purpose: Application metrics push cron job.
  - Resource: Virtual cron declaration.
  - Realization: Not realized in the supplied execution tree.

- **app_health_check**
  - Purpose: Concrete application health-check cron job.
  - Script: `/usr/local/bin/app-healthcheck.sh`
  - Schedule, user, command arguments, and environment: Require verification.

- **database_backup**
  - Purpose: Concrete database backup cron job in local database mode unless suppressed by an unshown manifest conditional.
  - Script: `/usr/local/bin/db-backup.sh`
  - Schedule, user, command arguments, and environment: Require verification.

## File Structure

```text
### Manifests

- site-modules/role/manifests/app_stack.pp
- site-modules/profile/manifests/app/stack.pp
- site-modules/profile_app_stack/manifests/init.pp
- site-modules/profile_app_stack/manifests/python.pp
- site-modules/profile_app_stack/manifests/database.pp
- site-modules/profile_app_stack/manifests/app.pp
- site-modules/profile_app_stack/manifests/service.pp
- site-modules/profile_app_stack/manifests/monitoring.pp

### Templates

- profile_app_stack/logrotate.conf.erb
- profile_app_stack/app.env.erb
- profile_app_stack/app.service.epp

### Data

- site-modules/profile_app_stack/data/common.yaml
- site-modules/profile_app_stack/data/environment/production.yaml
- site-modules/profile_app_stack/data/environment/staging.yaml
- Repository/control-repo data/common.yaml
- Repository/control-repo data/environment/production.yaml
- Repository/control-repo data/environment/staging.yaml
```

The repository/control-repo environment files contain no confirmed relevant `profile_app_stack::` keys. Their unrelated NTP and syslog values should not be migrated into this role unless source analysis identifies otherwise.

## Module Explanation

The module is invoked through the following execution order.

1. **`role::app_stack`** (`site-modules/role/manifests/app_stack.pp`):
   - Evaluates `$facts['kernel'].downcase == 'linux'`.
   - Runs an unresolved Linux-only `exec[None]`; its command, path, guards, and execution attributes require source verification.
   - Includes `::profile::base::base`.
   - Includes `::profile::app::stack`.
   - Preserves the ordering relationship in which the base profile completes before the application stack profile starts.
   - Ansible equivalent: run the confirmed preparation command only when `ansible_facts['kernel'] | lower == 'linux'`.

2. **`profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`):
   - Includes `profile_app_stack`.
   - Evaluates `fact('environment')` as part of the profile chain.
   - Preserves prerequisites supplied by the external base profile separately in Ansible.

3. **`profile_app_stack`** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Includes `profile_app_stack::python`.
   - Includes `profile_app_stack::database`.
   - Includes `profile_app_stack::app`.
   - Includes `profile_app_stack::service`.
   - Includes `profile_app_stack::monitoring`.
   - Orders Python before database, database before application deployment, application changes before service refresh, and service before monitoring:
     - `profile_app_stack::python` → `profile_app_stack::database`
     - `profile_app_stack::database` → `profile_app_stack::app`
     - `profile_app_stack::app` refresh-notifies `profile_app_stack::service`
     - `profile_app_stack::service` → `profile_app_stack::monitoring`

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Installs the package list derived from `profile_app_stack::python_version`; exact package names require verification.
   - Creates the configured application group.
   - Creates the `appuser` application user.
   - Creates `/var/log/test-app` with resolved application ownership and Puppet-equivalent permissions.
   - Renders `/etc/logrotate.d/test-app` from `profile_app_stack/logrotate.conf.erb`.
   - Renders the logrotate template once with four template inputs; exact variable names and file attributes require verification.

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Evaluates `profile_app_stack::db_host == 'localhost'`.
   - When true, includes `profile_postgresql`.
   - When true, creates the configured database user; supplied repository/test data identifies `testuser`.
   - When true, creates the configured database; supplied repository/test data identifies `testdb`.
   - When true, grants database privileges to `testuser` on `testdb`.
   - Manages `/usr/local/bin/db-backup.sh`.
   - Manages the `database_backup` cron job.
   - Exact commands, guards, ownership, permissions, schedule, and environment require verification.
   - When `db_host` is not `localhost`, local PostgreSQL provisioning and the three database-management `exec` resources are skipped. Backup behavior remains subject to any unshown manifest conditional.
   - Database credentials must be passed through protected Ansible variables without exposing them in output or process listings.

6. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`):
   - Creates or manages `/opt/test-app`.
   - Uses `vcsrepo` to check out `file:///tmp/test-app-repo` into `/opt/test-app`.
   - Checks out `master` for supplied repository/test data; production and staging revisions require Hiera verification.
   - Creates the application virtual environment using the configured Python version.
   - Installs the repository requirements into that virtual environment.
   - Evaluates `if !empty($pip_packages)`.
   - Expands the optional package loop over the actual supplied list: the supplied repository/test list is `[]`, so the loop runs zero times.
   - For any environment with a non-empty `pip_packages` list, installs each resolved package into the virtual environment.
   - Renders `/opt/test-app/.env` from `profile_app_stack/app.env.erb` once.
   - Renders the environment file with eight template inputs and one Ruby logic block; exact names and logic require template-source verification.
   - Uses Vault-backed values for the database password and secret key and renders the file with restrictive permissions and `no_log: true`.
   - Manages `/usr/local/bin/app-healthcheck.sh`.
   - Runs `run_db_migrations` after checkout, virtual-environment creation, requirements installation, and `.env` rendering.
   - Exact virtual-environment paths, commands, guards, script contents, and migration environment require verification.

7. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`):
   - Renders `/etc/systemd/system/test-app.service` from `profile_app_stack/app.service.epp`.
   - Renders the service template once with 11 template inputs and one Ruby logic block; exact names and directives require template-source verification.
   - Reloads systemd after the unit file changes.
   - Ensures the `test-app` service is enabled and running; exact enablement and restart attributes require verification.
   - Ansible equivalent: template the unit file, notify a handler, run `systemd_service` with `daemon_reload: true`, then enable and start or restart `test-app`.

8. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Declares virtual `prometheus-node-exporter` package.
   - Declares virtual `prometheus-node-exporter` service.
   - Declares virtual `prometheus-pushgateway` package.
   - Declares virtual `push_app_metrics` cron.
   - Evaluates `$facts['environment'] == 'production'`.
   - In production, declares the same four virtual resources again; they remain unrealized unless another class realizes them.
   - Manages the concrete `app_health_check` cron job.
   - Ansible should not install or schedule the virtual monitoring resources solely from this module.

## Variables

**Variable Flow Summary**: 23 module-common variables, plus 7 production overrides and 6 staging overrides, across module common data, module environment data, and repository/control-repo data. Hiera values, types, encryption status, and effective precedence require verification against the actual Hiera analysis. The mappings below are therefore migration mappings, not independently confirmed source values.

### Variable Definitions

#### Module common defaults — `site-modules/profile_app_stack/data/common.yaml`

Migration note: Base defaults for all nodes. Literal values and types not explicitly shown below require verification.

- `profile_app_stack::app_name` → `app_stack_app_name`: `test-app` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::app_repo` → `app_stack_app_repo`: `file:///tmp/test-app-repo` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::app_revision` → `app_stack_app_revision`: `master` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::app_port` → `app_stack_app_port`: literal value not supplied (type: integer)
- `profile_app_stack::app_dir` → `app_stack_app_dir`: `/opt/test-app` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::app_user` → `app_stack_app_user`: `appuser` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::app_group` → `app_stack_app_group`: literal value not supplied (type: string)
- `profile_app_stack::python_version` → `app_stack_python_version`: literal value not supplied (type: string)
- `profile_app_stack::pip_packages` → `app_stack_pip_packages`: `[]` in supplied repository/test data (type: array)
- `profile_app_stack::db_host` → `app_stack_db_host`: `testdb` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::db_port` → `app_stack_db_port`: literal value not supplied (type: integer)
- `profile_app_stack::db_name` → `app_stack_db_name`: `testdb` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::db_user` → `app_stack_db_user`: `testuser` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::db_password` → `app_stack_db_password`: `{{ vault_app_stack_db_password }}` in Ansible (type: secret string); do not migrate any plaintext source value
- `profile_app_stack::worker_count` → `app_stack_worker_count`: literal value not supplied (type: integer; supplied summary contains a conflicting `sync` value)
- `profile_app_stack::worker_class` → `app_stack_worker_class`: literal value not supplied (type: string)
- `profile_app_stack::max_requests` → `app_stack_max_requests`: literal value not supplied (type: integer)
- `profile_app_stack::graceful_timeout` → `app_stack_graceful_timeout`: literal value not supplied (type: integer)
- `profile_app_stack::log_dir` → `app_stack_log_dir`: `/var/log/test-app` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::log_level` → `app_stack_log_level`: `sync` in supplied repository/test data (type: string; source value requires verification)
- `profile_app_stack::secret_key` → `app_stack_secret_key`: `{{ vault_app_stack_secret_key }}` in Ansible (type: secret string); do not migrate any plaintext source value
- `profile_app_stack::log_max_size` → `app_stack_log_max_size`: `100M` in supplied plan (type: string; source usage requires verification)
- `profile_app_stack::log_rotate_count` → `app_stack_log_rotate_count`: `7` in supplied plan (type: integer; source usage requires verification)

#### Module production data — `site-modules/profile_app_stack/data/environment/production.yaml`

Migration note: Production-specific overrides, loaded conditionally for the production environment. Literal values and encryption status require verification.

- `profile_app_stack::app_revision` → `app_stack_app_revision`: production override (type: string)
- `profile_app_stack::worker_count` → `app_stack_worker_count`: production override (type: integer)
- `profile_app_stack::max_requests` → `app_stack_max_requests`: production override (type: integer)
- `profile_app_stack::log_level` → `app_stack_log_level`: production override (type: string)
- `profile_app_stack::db_host` → `app_stack_db_host`: production override (type: string)
- `profile_app_stack::db_port` → `app_stack_db_port`: production override (type: integer)
- `profile_app_stack::secret_key` → `app_stack_secret_key`: `{{ vault_app_stack_production_secret_key }}` (type: secret string); retain only in encrypted Ansible secret storage

#### Module staging data — `site-modules/profile_app_stack/data/environment/staging.yaml`

Migration note: Staging-specific overrides, loaded conditionally for the staging environment. Literal values and secret handling require verification.

- `profile_app_stack::app_revision` → `app_stack_app_revision`: staging override (type: string)
- `profile_app_stack::worker_count` → `app_stack_worker_count`: staging override (type: integer)
- `profile_app_stack::max_requests` → `app_stack_max_requests`: staging override (type: integer)
- `profile_app_stack::log_level` → `app_stack_log_level`: staging override (type: string)
- `profile_app_stack::db_host` → `app_stack_db_host`: staging override (type: string)
- `profile_app_stack::secret_key` → `app_stack_secret_key`: `{{ vault_app_stack_staging_secret_key }}` (type: secret string); retain only in encrypted Ansible secret storage

#### Repository/control-repo common data — `data/common.yaml`

Migration note: Repository/test or inventory-level overrides. Recommended Ansible placement is test inventory or `group_vars/test.yml`, not role defaults.

- Provides repository/test overrides for application, database, worker, logging, secret, Python, and pip variables; exact key coverage requires verification.
- `profile_app_stack::pip_packages` is reported as an empty array, so the optional package loop runs zero times.
- Any source values for `profile_app_stack::db_password` and `profile_app_stack::secret_key` must be replaced with Vault or external-secret references and must not be copied into Ansible files.

#### Repository/control-repo environment data

Migration note: `data/environment/production.yaml` and `data/environment/staging.yaml` contain no confirmed relevant `profile_app_stack::` keys. Do not migrate unrelated NTP or syslog settings into this role without source verification.

### Variable Migration Summary

- **Common defaults**: 23 module-common variables.
- **OS-specific variables**: 0 identified.
- **Environment-specific variables**: 7 production keys and 6 staging keys.
- **Host-specific variables**: 0 identified.
- **Encrypted variables**: Encryption status of the Puppet sources is not verifiable from the supplied analysis. Two credentials require protected migration: the database password and application secret key.
- **Additional sensitive candidates**: Redis authentication, Redis Sentinel authentication, and TLS private-key path parameters may exist in dependency modules but are not concrete resources in this module’s execution tree.

### Cross-Level Overrides

All scalar overrides use higher-priority data over lower-priority data, subject to confirmation of the actual Hiera hierarchy:

- `app_name`: module common and repository common.
- `app_repo`: module common and repository common.
- `app_revision`: module common, production, staging, and repository common.
- `app_port`: module common and repository common.
- `app_dir`: module common and repository common.
- `app_user`: module common and repository common.
- `app_group`: module common and repository common.
- `python_version`: module common and repository common.
- `pip_packages`: module common and repository common; treat as replacement rather than concatenation unless Hiera confirms array merging.
- `db_host`: module common, production, staging, and repository common.
- `db_port`: module common, production, and repository common.
- `db_name`: module common and repository common.
- `db_user`: module common and repository common.
- `db_password`: module common and repository common; use only the Vault-backed Ansible value.
- `worker_count`: module common, production, staging, and repository common.
- `worker_class`: module common and repository common.
- `max_requests`: module common, production, staging, and repository common.
- `graceful_timeout`: module common and repository common.
- `log_dir`: module common and repository common.
- `log_level`: module common, production, staging, and repository common.
- `secret_key`: module common, production, staging, and repository common; use only Vault-backed Ansible values.

### Merge Strategy Notes

- Variables using `hash` merge: No confirmed hash variables.
- Variables using `deep` merge: No confirmed deep-merge variables.
- Variables using `first` or higher-priority replacement: All listed scalar variables.
- `pip_packages` is an array with no confirmed array merge strategy; use replacement semantics unless the actual Hiera configuration specifies otherwise.

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

The directly visible application tree uses `vcsrepo`. Other dependencies may be consumed by the base profile, `profile_postgresql`, or dependency classes not analyzed here.

**System package dependencies**:

- Python runtime and development/package dependencies derived from `profile_app_stack::python_version`; exact package names require verification.
- PostgreSQL packages supplied through `profile_postgresql` when `db_host == 'localhost'`.
- `prometheus-node-exporter`: virtual declaration only.
- `prometheus-pushgateway`: virtual declaration only.

**Service dependencies**:

- `::profile::base::base` precedes `::profile::app::stack`.
- Python setup precedes database setup.
- Database setup precedes application deployment.
- Application configuration refresh-notifies the service.
- Systemd daemon reload follows changes to `/etc/systemd/system/test-app.service`.
- Database migrations follow checkout, virtual-environment creation, requirements installation, and `.env` rendering.
- Service setup precedes monitoring.

## Puppet Facts Used

- `$facts['kernel']`
  - Provides the operating-system kernel.
  - Runs the role-level preparation branch only when the kernel is Linux.

- `$facts['environment']`
  - Provides the Puppet environment.
  - Controls production-only virtual monitoring declarations.

- `fact('environment')`
  - Provides an environment lookup used in the profile chain.
  - Exact consumer behavior outside the supplied manifests requires verification.

## Template Conversion Notes

### `profile_app_stack/logrotate.conf.erb`

- Destination: `/etc/logrotate.d/test-app`.
- Render count: 1.
- Template inputs: 4; exact names require source verification.
- Likely related values include application name, log directory, `log_max_size`, and `log_rotate_count`.
- No confirmed Ruby logic block.
- Ansible equivalent: `ansible.builtin.template` with Puppet-equivalent ownership and mode.

### `profile_app_stack/app.env.erb`

- Destination: `/opt/test-app/.env`.
- Render count: 1.
- Template inputs: 8; exact names require source verification.
- Ruby logic blocks: 1.
- Expected input categories include application settings, database connection settings, database credentials, secret key, and runtime or logging settings.
- Render database password and secret key from Vault-backed variables.
- Use `no_log: true` for tasks that render or otherwise handle credentials.
- Use restrictive ownership and permissions.

### `profile_app_stack/app.service.epp`

- Destination: `/etc/systemd/system/test-app.service`.
- Render count: 1.
- Template inputs: 11; exact names require source verification.
- Ruby logic blocks: 1.
- Expected input categories include service name, application directory, user, group, Python or virtual-environment executable, port, worker count, worker class, request limit, and graceful timeout.
- Ansible equivalent: render the unit, notify a daemon-reload handler, then enable and start or restart `test-app`.

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
- `Repository/control-repo data/common.yaml`
- `Repository/control-repo data/environment/production.yaml`
- `Repository/control-repo data/environment/staging.yaml`

**Service endpoints to check**:

- `test-app`: effective `app_stack_app_port`; literal value requires verification.
- `test-app` health endpoint: defined by `/usr/local/bin/app-healthcheck.sh`; URL and path require verification.
- Database: host `testdb` in supplied repository/test data and effective `app_stack_db_port`; literal port requires verification.
- Local PostgreSQL: verify only when effective `db_host` is `localhost`.

**Templates rendered**:

- `profile_app_stack/logrotate.conf.erb`: 1 render.
- `profile_app_stack/app.env.erb`: 1 render.
- `profile_app_stack/app.service.epp`: 1 render.

## Pre-flight checks

```bash
# Confirm the target kernel and effective deployment values
test "$(uname -s)" = "Linux"
ansible-inventory --host "$TARGET"

# Application instance: test-app
getent passwd appuser
getent group "<resolved-app-group>"
test -d /opt/test-app
test -w /opt/test-app
test -f /etc/systemd/system/test-app.service
systemd-analyze verify /etc/systemd/system/test-app.service
systemctl is-enabled test-app
systemctl is-active test-app

# Application repository and runtime
git ls-remote file:///tmp/test-app-repo
python3 --version
test -d /var/log/test-app

# Application endpoint
# Replace with the verified application port and health-check URL.
curl --fail "http://127.0.0.1:<resolved-app-port>/<verified-health-path>"

# Database instance
# Verify the effective host and port before attempting local provisioning.
getent hosts <resolved-db-host>
# Run local PostgreSQL checks only when db_host == localhost.
pg_isready -h <resolved-db-host> -p <resolved-db-port> -d testdb

# Configuration and migration
# Confirm pip_packages is [] for the supplied test data, or verify every resolved package.
# Run the verified application configuration and migration commands.
# Confirm migrations complete after checkout, virtualenv, requirements, and .env rendering.

# Scheduled jobs
crontab -l
test -x /usr/local/bin/app-healthcheck.sh
test -x /usr/local/bin/db-backup.sh

# Logrotate
logrotate --debug /etc/logrotate.d/test-app

# Monitoring
# Confirm prometheus-node-exporter, prometheus-pushgateway, and push_app_metrics
# are not installed or scheduled solely because of these unrealized Puppet
# virtual resources.

# Secret handling
# Confirm db_password and secret_key are supplied only through Ansible Vault
# or an external secret manager.
# Confirm no credentials appear in task output, command arguments, process
# listings, generated logs, or non-encrypted variable files.
```
