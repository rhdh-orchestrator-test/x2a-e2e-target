---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: `profile_app_stack` provisions a Python application service on Linux. It creates the application user, group, directories, Python runtime, virtual environment, Git checkout, application environment file, systemd unit, database migration workflow, health-check script, log rotation, and maintenance jobs. Local PostgreSQL provisioning and database creation occur only when `db_host` resolves to `localhost`. The application health-check cron is concrete; monitoring packages, services, and metric-pushing cron resources are declared virtually and are not active unless realized elsewhere. Hiera values and template contents require source verification before implementation, and database passwords or application secret keys must be stored in Ansible Vault or an external secret provider.

## Service Type and Instances

**Service Type**: Python application service managed by systemd.

**Configured Instances**:

- **Application service**
  - Service name: Resolved from `profile_app_stack::app_name`; literal value is not supplied.
  - Location/Path: Resolved from `profile_app_stack::app_dir`.
  - Port/Socket: Resolved from `profile_app_stack::app_port`.
  - User: Resolved from `profile_app_stack::app_user`.
  - Group: Resolved from `profile_app_stack::app_group`.
  - Worker count: Resolved from `profile_app_stack::worker_count`.
  - Worker class: Resolved from `profile_app_stack::worker_class`.
  - Maximum requests: Resolved from `profile_app_stack::max_requests`.
  - Graceful timeout: Resolved from `profile_app_stack::graceful_timeout`.

- **Database**
  - Host: Resolved from `profile_app_stack::db_host`.
  - Port: Resolved from `profile_app_stack::db_port`.
  - Database: Resolved from `profile_app_stack::db_name`.
  - User: Resolved from `profile_app_stack::db_user`.
  - Password: Resolved from `profile_app_stack::db_password`; exact secret handling requires source verification.
  - Local PostgreSQL provisioning and database-management commands run only when the resolved host is exactly `localhost`.
  - The database backup script and backup cron are siblings of the local-database conditional and appear unconditional unless source inspection proves otherwise.

- **Application health check**
  - Script: `/usr/local/bin/app-healthcheck.sh`.
  - Schedule: Defined by `cron[app_health_check]`; exact schedule is not supplied.
  - Status: Concrete cron resource.
  - Endpoint or command: Requires source inspection.

- **Database backup**
  - Script: `/usr/local/bin/db-backup.sh`.
  - Schedule: Defined by `cron[database_backup]`; exact schedule is not supplied.
  - Status: Appears unconditional because it is outside the `db_host == 'localhost'` conditional.
  - Credentials: Protect with Vault-backed data and restrictive file permissions if credentials are used.

- **Monitoring**
  - Package: `prometheus-node-exporter`, declared virtually.
  - Service: `prometheus-node-exporter`, declared virtually.
  - Package: `prometheus-pushgateway`, declared virtually.
  - Metric-pushing cron: `push_app_metrics`, declared virtually.
  - Production condition: The monitoring class declares the same virtual resources when `$facts['environment'] == 'production'`.
  - Status: No collector or realization is shown; these resources are not active unless realized by another class.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

profile_app_stack/
├── logrotate.conf.erb
├── app.env.erb
└── app.service.epp

data/
├── common.yaml
└── environment/
    ├── production.yaml
    └── staging.yaml
```

The supplied plan explicitly identifies eight manifests and three templates. Any additional files included in a reported 97-file analysis are not identified in the supplied material and must be enumerated or explicitly marked out of scope before migration completion.

## Module Explanation

The module performs operations in this order:

1. **`role::app_stack`** (`site-modules/role/manifests/app_stack.pp`):
   - Executes a Linux-only `exec` when `$facts['kernel'].downcase == 'linux'`.
   - The resource title is reported as `exec[None]`; its command and attributes require source verification.
   - Includes `::profile::base::base`, which is outside the analyzed module.
   - Includes `::profile::app::stack`.
   - Orders `Class['::profile::base::base']` before `Class['::profile::app::stack']`.
   - Uses `$facts['kernel']` to gate Linux-specific behavior.
   - The downstream monitoring class uses the `environment` fact.

2. **`::profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`):
   - Includes `profile_app_stack`.
   - Contains no additional resources in the supplied execution tree.
   - Passes the profile chain to the application module.

3. **`profile_app_stack`** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Includes `profile_app_stack::python`.
   - Includes `profile_app_stack::database`.
   - Includes `profile_app_stack::app`.
   - Includes `profile_app_stack::service`.
   - Includes `profile_app_stack::monitoring`.
   - Orders Python setup before database setup:
     - `Class['profile_app_stack::python'] -> Class['profile_app_stack::database']`
   - Orders database setup before application setup:
     - `Class['profile_app_stack::database'] -> Class['profile_app_stack::app']`
   - Sends application changes to the service class:
     - `Class['profile_app_stack::app'] ~> Class['profile_app_stack::service']`
   - Orders service setup before monitoring:
     - `Class['profile_app_stack::service'] -> Class['profile_app_stack::monitoring']`
   - Contains no `.each` loops in the supplied execution tree.

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Installs the package list represented by `$python_packages`; exact package titles and ensure values require source verification.
   - Creates the application group from `profile_app_stack::app_group`.
   - Creates the application user from `profile_app_stack::app_user`.
   - Creates the application log directory from `profile_app_stack::log_dir`.
   - Deploys `/etc/logrotate.d/<resolved app name>` from `profile_app_stack/logrotate.conf.erb`.
   - Renders the logrotate template once.
   - The Ansible role must create the group and user before the log directory and logrotate configuration.

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Evaluates the conditional `profile_app_stack::db_host == 'localhost'`.
   - Inside the local-database branch:
     - Includes `profile_postgresql`.
     - Runs `exec[create_db_user]`.
     - Runs `exec[create_database]`.
     - Runs `exec[grant_db_privileges]`.
   - The exact commands, credentials, guards, environment, and privilege scope require source verification.
   - Outside the local-database conditional:
     - Deploys `/usr/local/bin/db-backup.sh`.
     - Schedules `cron[database_backup]`.
   - The backup script and cron must not be made conditional on local PostgreSQL without confirming the source structure.
   - Prefer `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` over shell commands for local database management.

6. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`):
   - Creates `profile_app_stack::app_dir`.
   - Checks out the application repository into the application directory using:
     - Repository: `profile_app_stack::app_repo`
     - Revision: `profile_app_stack::app_revision`
   - Creates the Python virtual environment with `exec[create_app_venv]`.
   - Installs application requirements with `exec[install_requirements]`.
   - Evaluates the `pip_packages` conditional.
   - Installs optional pip packages only when `pip_packages` is not empty.
   - `pip_packages` is manifest-referenced but has no confirmed module-common Hiera value in the supplied data.
   - Deploys `<resolved app_dir>/.env` from `profile_app_stack/app.env.erb`.
   - Renders the environment template once.
   - Installs `/usr/local/bin/app-healthcheck.sh`.
   - Runs application database migrations with `exec[run_db_migrations]`.
   - Application changes notify `profile_app_stack::service`.
   - Exact commands, ownership, modes, guards, and environment values require source inspection.

7. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`):
   - Deploys `/etc/systemd/system/<resolved app name>.service` from `profile_app_stack/app.service.epp`.
   - Renders the systemd template once.
   - Reloads systemd with `exec[systemd_daemon_reload]`.
   - Manages the resolved application service name.
   - The service should be enabled and started, with application and unit changes connected to a restart handler.
   - Orders the service class before monitoring:
     - `Class['profile_app_stack::service'] -> Class['profile_app_stack::monitoring']`

8. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Declares virtual package `prometheus-node-exporter`.
   - Declares virtual service `prometheus-node-exporter`.
   - Declares virtual package `prometheus-pushgateway`.
   - Declares virtual cron `push_app_metrics`.
   - Declares those virtual monitoring resources under the production condition `$facts['environment'] == 'production'`.
   - Contains no shown resource collector or realization for the virtual resources.
   - Manages concrete `cron[app_health_check]`.
   - The health-check cron is active; metric pushing is not active unless another class realizes `push_app_metrics`.
   - Ansible must explicitly decide whether to install monitoring packages, enable the exporter, configure Pushgateway, and schedule metric pushing.

## Variables

**Variable Flow Summary**: 19 manifest-relevant module-common variables, four additional unreferenced module-common keys, seven production keys, six staging keys, and repository-common test data containing the same application-related key set were identified. Literal values, Hiera hierarchy configuration, encryption metadata, and precedence require separate source verification.

### Variable Definitions

#### `site-modules/profile_app_stack/data/common.yaml` — module defaults

Migration note: Intended base defaults for the module. Literal YAML values were not supplied.

- `profile_app_stack::app_name` → `profile_app_stack_app_name` (type: string)
- `profile_app_stack::app_repo` → `profile_app_stack_app_repo` (type: string)
- `profile_app_stack::app_revision` → `profile_app_stack_app_revision` (type: string)
- `profile_app_stack::app_port` → `profile_app_stack_app_port` (type: integer)
- `profile_app_stack::app_dir` → `profile_app_stack_app_dir` (type: string)
- `profile_app_stack::app_user` → `profile_app_stack_app_user` (type: string)
- `profile_app_stack::app_group` → `profile_app_stack_app_group` (type: string)
- `profile_app_stack::db_host` → `profile_app_stack_db_host` (type: string)
- `profile_app_stack::db_port` → `profile_app_stack_db_port` (type: integer)
- `profile_app_stack::db_name` → `profile_app_stack_db_name` (type: string)
- `profile_app_stack::db_user` → `profile_app_stack_db_user` (type: string)
- `profile_app_stack::db_password` → `vault_profile_app_stack_db_password` (type: string; sensitivity and encryption require source verification)
- `profile_app_stack::worker_count` → `profile_app_stack_worker_count` (type: integer)
- `profile_app_stack::worker_class` → `profile_app_stack_worker_class` (type: string)
- `profile_app_stack::max_requests` → `profile_app_stack_max_requests` (type: integer)
- `profile_app_stack::graceful_timeout` → `profile_app_stack_graceful_timeout` (type: integer)
- `profile_app_stack::log_dir` → `profile_app_stack_log_dir` (type: string)
- `profile_app_stack::log_level` → `profile_app_stack_log_level` (type: string)
- `profile_app_stack::python_version` (type and value require source verification; reported as not used by the supplied manifest lookup list)
- `profile_app_stack::pip_packages` (type and value require source verification; manifest-referenced by the non-empty conditional)
- `profile_app_stack::log_max_size` (type and value require source verification; reported as unreferenced)
- `profile_app_stack::log_rotate_count` (type and value require source verification; reported as unreferenced)

#### `site-modules/profile_app_stack/data/environment/production.yaml` — production variables

Migration note: Production-specific overrides, subject to confirmation from the actual Hiera hierarchy.

- `profile_app_stack::app_revision` → `profile_app_stack_app_revision` (type: string)
- `profile_app_stack::worker_count` → `profile_app_stack_worker_count` (type: integer)
- `profile_app_stack::max_requests` → `profile_app_stack_max_requests` (type: integer)
- `profile_app_stack::log_level` → `profile_app_stack_log_level` (type: string)
- `profile_app_stack::db_host` → `profile_app_stack_db_host` (type: string)
- `profile_app_stack::db_port` → `profile_app_stack_db_port` (type: integer)
- `profile_app_stack::secret_key` → `vault_profile_app_stack_secret_key` (type: string; reported as encrypted, requiring source verification)

#### `site-modules/profile_app_stack/data/environment/staging.yaml` — staging variables

Migration note: Staging-specific overrides, subject to confirmation from the actual Hiera hierarchy.

- `profile_app_stack::app_revision` → `profile_app_stack_app_revision` (type: string)
- `profile_app_stack::worker_count` → `profile_app_stack_worker_count` (type: integer)
- `profile_app_stack::max_requests` → `profile_app_stack_max_requests` (type: integer)
- `profile_app_stack::log_level` → `profile_app_stack_log_level` (type: string)
- `profile_app_stack::db_host` → `profile_app_stack_db_host` (type: string)
- `profile_app_stack::secret_key` → `vault_profile_app_stack_secret_key` (type: string; use a separate staging secret if confirmed)

#### `data/common.yaml` — repository test data

Migration note: Test-only data. Do not copy plaintext credentials into role defaults or production variables.

- Contains the same application, database, worker, and logging key categories as the module common data.
- `profile_app_stack::db_password` is reported as a plaintext test credential; verify before migration.
- `profile_app_stack::secret_key` is reported as a plaintext test credential; verify before migration.
- The file also contains unrelated NTP, SSH, syslog, HAProxy, PostgreSQL, and Redis settings not referenced by the supplied execution tree.

#### Repository environment data

Migration note: No supplied manifest-used `profile_app_stack` values were identified.

- `data/environment/production.yaml`: NTP and syslog settings only.
- `data/environment/staging.yaml`: NTP and syslog settings only.

### Variable Migration Summary

- **Common defaults**: 19 manifest-relevant variables plus four additional reported but unreferenced keys.
- **Production-specific variables**: Seven reported keys.
- **Staging-specific variables**: Six reported keys.
- **Repository test variables**: Application-related key set reported as matching the module common data; exact count requires source verification.
- **Encrypted or sensitive variables**:
  - `profile_app_stack::db_password`
  - `profile_app_stack::secret_key`
  - Any credentials confirmed in `.env`, the database backup script, or the systemd unit.
- **Hiera evidence status**: Literal values, hierarchy configuration, encryption status, and precedence are not present in the supplied structured analysis and must be verified from source.

### Cross-Level Overrides

The following duplicate definitions are reported and require confirmation from the actual Hiera hierarchy:

- `app_name`: module common and repository common.
- `app_repo`: module common and repository common.
- `app_revision`: module common, production/staging environment data, and repository common.
- `app_port`: module common and repository common.
- `app_dir`: module common and repository common.
- `app_user`: module common and repository common.
- `app_group`: module common and repository common.
- `db_host`: module common, production/staging environment data, and repository common.
- `db_port`: module common, production data, and repository common.
- `db_name`: module common and repository common.
- `db_user`: module common and repository common.
- `db_password`: module common and repository common test data.
- `worker_count`: module common, production/staging environment data, and repository common.
- `worker_class`: module common and repository common.
- `max_requests`: module common, production/staging environment data, and repository common.
- `graceful_timeout`: module common and repository common.
- `log_dir`: module common and repository common.
- `log_level`: module common, production/staging environment data, and repository common.
- `secret_key`: production/staging environment data and repository common test data.

### Merge Strategy Notes

- No explicit Hiera merge strategy was supplied.
- The reported behavior is priority-based replacement, but the hierarchy and precedence order require verification.
- Do not assume repository test data overrides production Vault data.
- Sensitive production values must be explicitly sourced from Vault or an approved external secret provider.

## Custom Types and Providers

No custom types, providers, facts, or functions were detected.

## Dependencies

**External Puppet module dependencies**:

- `puppetlabs-vcsrepo` is suggested by the `vcsrepo` resource.
- `profile_postgresql` is referenced as an external or separately defined class.
- `::profile::base::base` is referenced outside the analyzed module.
- The reported versions for `puppetlabs-stdlib`, `puppetlabs-concat`, `puppetlabs-firewall`, `puppet-redis`, `puppet-systemd`, `puppetlabs-inifile`, and `puppetlabs-apt` require verification from Puppetfile or metadata and are not confirmed by the supplied execution tree.

**Ansible collection equivalents**:

- Git checkout: `ansible.builtin.git`
- Packages: `ansible.builtin.package`
- Users: `ansible.builtin.user`
- Groups: `ansible.builtin.group`
- Files and directories: `ansible.builtin.file`
- Templates: `ansible.builtin.template`
- Service management: `ansible.builtin.systemd_service`
- Cron: `ansible.builtin.cron`
- Python packages: `ansible.builtin.pip` or a Python-specific collection
- PostgreSQL: `community.postgresql`
- Secrets: Ansible Vault or an approved external secret lookup plugin

**System package dependencies**:

- Exact Python package titles represented by `$python_packages` require manifest verification.
- Python virtual-environment tooling requires verification.
- Git is required unless installed by another profile.
- PostgreSQL server and client packages are required when `db_host == 'localhost'`.
- `prometheus-node-exporter` and `prometheus-pushgateway` should be installed only if the virtual resources are intentionally realized.

**Service dependencies**:

- `::profile::base::base` before `::profile::app::stack`
- `profile_app_stack::python` before `profile_app_stack::database`
- `profile_app_stack::database` before `profile_app_stack::app`
- `profile_app_stack::app` notifies `profile_app_stack::service`
- `profile_app_stack::service` before `profile_app_stack::monitoring`

## Puppet Facts Used

- `$facts['kernel']`
  - Identifies the operating-system kernel.
  - Gates the Linux-only resource in `role::app_stack`.

- `$facts['environment']`
  - Identifies the Puppet environment.
  - Controls production monitoring declarations in `profile_app_stack::monitoring`.

- `fact('environment')`
  - Function-style reference to the environment fact through the profile chain.
  - The consuming resources are in `profile_app_stack::monitoring`.

## Template Conversion Notes

### `profile_app_stack/logrotate.conf.erb`

- Full source path: `profile_app_stack/logrotate.conf.erb`.
- Destination: `/etc/logrotate.d/<resolved app name>`.
- Render count: 1.
- Template variable count: 4.
- Exact variable names and directives require template inspection.
- Convert to Jinja2.
- Preserve log directory, rotation size and count, compression, missing-file handling, empty-file handling, and post-rotate behavior if present.
- Do not assume `log_max_size` or `log_rotate_count` are active without confirming template inputs.

### `profile_app_stack/app.env.erb`

- Full source path: `profile_app_stack/app.env.erb`.
- Destination: `<resolved app_dir>/.env`.
- Render count: 1.
- Template variable count: 8.
- Ruby logic blocks: 1.
- Exact variable names and conditional behavior require template inspection.
- Convert the Ruby conditional logic to equivalent Jinja2 behavior.
- Confirm whether database credentials, `secret_key`, or other sensitive values are rendered.
- Apply restrictive ownership and mode.
- Use `no_log: true` for tasks that may expose rendered secrets.

### `profile_app_stack/app.service.epp`

- Full source path: `profile_app_stack/app.service.epp`.
- Destination: `/etc/systemd/system/<resolved app name>.service`.
- Render count: 1.
- Template variable count: 12.
- Ruby logic blocks: 2.
- Exact variable names and unit directives require template inspection.
- Convert to a Jinja2 systemd unit template.
- Preserve confirmed or source-verified settings for:
  - Application command and virtual-environment path
  - Application user and group
  - Working directory
  - Application port
  - Worker count and worker class
  - Maximum requests
  - Graceful timeout
  - Environment file
  - Restart behavior
- Reload systemd before starting or restarting the service.
- Use a handler for unit-file, environment-file, and application changes.

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
- Puppetfile or module metadata, if used to confirm external dependencies
- Hiera hierarchy configuration, if used to confirm precedence

**Service endpoints to check**:

- **Application service**: Confirm the resolved systemd service name and check the resolved `profile_app_stack::app_port`.
- **Database**: Confirm connectivity to the resolved `profile_app_stack::db_host` and `profile_app_stack::db_port`.
- **Local PostgreSQL**: When the host is exactly `localhost`, confirm PostgreSQL is running and the configured database and user exist.
- **Application health check**: Confirm the endpoint or command used by `/usr/local/bin/app-healthcheck.sh`.
- **Node exporter**: Confirm whether `prometheus-node-exporter` should be installed and enabled; the Puppet resource is virtual.
- **Pushgateway**: Confirm whether `prometheus-pushgateway` should be installed and which endpoint and credentials are required.
- **Metric pushing**: Confirm whether `push_app_metrics` is realized; it is virtual in the supplied tree.

**Templates rendered**:

- `profile_app_stack/logrotate.conf.erb`: 1 render
- `profile_app_stack/app.env.erb`: 1 render
- `profile_app_stack/app.service.epp`: 1 render

## Pre-flight checks:

```bash
# Confirm the target is Linux.
uname -s

# Resolve and record all application variables for the selected environment.
# Verify app_name, app_dir, app_user, app_group, app_port, app_repo, and app_revision.

# Application service checks.
systemctl cat "<resolved-app-name>.service"
systemd-analyze verify "/etc/systemd/system/<resolved-app-name>.service"
systemctl is-enabled "<resolved-app-name>.service"
systemctl is-active "<resolved-app-name>.service"
curl --fail "http://127.0.0.1:<resolved-app-port>/health"

# Database instance checks.
getent hosts "<resolved-db-host>"
nc -zv "<resolved-db-host>" "<resolved-db-port>"

# Local PostgreSQL checks when db_host is exactly localhost.
systemctl is-active postgresql
# Confirm the configured database and user with PostgreSQL client commands.

# Application instance checks.
test -d "<resolved-app-dir>"
id "<resolved-app-user>"
getent group "<resolved-app-group>"
test -x "<resolved-app-dir>/venv/bin/python"
test -f "<resolved-app-dir>/.env"
test -x /usr/local/bin/app-healthcheck.sh
/usr/local/bin/app-healthcheck.sh

# Database backup instance checks.
test -x /usr/local/bin/db-backup.sh
crontab -l
# Confirm database_backup schedule, user, command, and credential handling.

# Monitoring instance checks.
# Confirm whether prometheus-node-exporter is intentionally installed and enabled.
# Confirm whether prometheus-pushgateway is intentionally installed.
# Confirm whether push_app_metrics is realized and has a verified endpoint.
systemctl status prometheus-node-exporter 2>/dev/null || true

# Verify the Git repository and requested revision are reachable before checkout.
git ls-remote "<resolved-app-repository>" "<resolved-app-revision>"

# Verify Python, virtual-environment tooling, Git, and required package repositories.
python3 --version
git --version

# Verify secrets exist in the selected Vault or external secret provider.
# Confirm production and staging use separate secret values.
# Do not print secret values.

# Verify restrictive permissions on the environment file and backup-related files.
stat -c '%U:%G %a %n' "<resolved-app-dir>/.env" /usr/local/bin/db-backup.sh

# Verify cron resources.
crontab -l
```

## Credentials and Secret Handling

- **Database password**
  - Puppet variable: `profile_app_stack::db_password`.
  - Ansible variable: `vault_profile_app_stack_db_password`.
  - The supplied plan reports both encrypted module data and plaintext repository test data; this requires source verification.
  - Do not place production credentials in role defaults, ordinary group variables, Git, command arguments, or debug output.

- **Application secret key**
  - Puppet variable: `profile_app_stack::secret_key`.
  - Ansible variable: `vault_profile_app_stack_secret_key`.
  - Production and staging values should be separate Vault values if confirmed by source inspection.
  - The reported insecure `changeme` fallback requires verification and must not be retained for production.

- **Backup credentials**
  - Inspect `/usr/local/bin/db-backup.sh` and its inputs for database credentials.
  - Store any credentials in Vault and use restrictive ownership and permissions.

- **Environment-file credentials**
  - Inspect `profile_app_stack/app.env.erb` to identify exact sensitive variables.
  - Protect the rendered `.env` file and use `no_log: true` during deployment.

- **Monitoring credentials**
  - Inspect the metric-pushing command for endpoints, tokens, or other credentials.
  - Treat any discovered values as secrets and store them in Vault.