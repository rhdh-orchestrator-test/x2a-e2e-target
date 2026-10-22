---
source-path: site-modules/profile_postgresql
---

# Migration Plan: profile_postgresql

**TLDR**: `profile_postgresql` provisions a local PostgreSQL server on Debian-family systems when `profile_app_stack::db_host` equals `localhost`. Its execution flow configures the PGDG APT source, installs PostgreSQL packages and `libpq-dev`, enables and starts the `postgresql` service, and supports application database initialization through resources declared by `profile_app_stack::database`. The execution tree confirms the classes, resources, ordering, and local-database condition. Concrete Hiera values for the repository, signing key, PostgreSQL version, database credentials, and application settings require verification against the referenced data files.

## Service Type and Instances

**Service Type**: Relational database server

**Configured Instances**:

- **Local PostgreSQL instance**: Local database server for the application stack
  - Activation condition: `profile_app_stack::db_host == 'localhost'`
  - Packages: `postgresql-15`, `postgresql-contrib-15`, `libpq-dev`  
    - The package resource names are present in the supplied plan; the resolved version requires Hiera verification.
  - Service: `postgresql`
  - Repository: `https://apt.postgresql.org/pub/repos/apt`  
    - Repository resource `apt::source['pgdg']` is confirmed; the concrete URL requires Hiera verification.
  - Repository release: `<Debian distribution codename>-pgdg`  
    - Requires Hiera verification.
  - Repository signing key ID: `B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8`  
    - Requires Hiera verification.
  - Repository signing key source: `https://www.postgresql.org/media/keys/ACCC4CF8.asc`  
    - Requires Hiera verification.
  - Default endpoint: TCP port `5432`
  - Application database port: `profile_app_stack::db_port`, value not supplied
  - Database/user configuration: declared by the application-stack database phase; command parameters and resolved credentials require source verification

## File Structure

**MANDATORY: Preserve this section from the original plan.**

### Manifests

- `site-modules/role/manifests/app_server.pp`
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

### Dependency manifests

- `migration-dependencies/apt/manifests/init.pp`
- `migration-dependencies/apt/manifests/update.pp`
- `migration-dependencies/apt/manifests/conf.pp`
- `migration-dependencies/apt/manifests/key.pp`
- `migration-dependencies/apt/manifests/keyring.pp`
- `migration-dependencies/apt/manifests/pin.pp`
- `migration-dependencies/apt/manifests/ppa.pp`
- `migration-dependencies/apt/manifests/setting.pp`
- `migration-dependencies/apt/manifests/source.pp`

### Templates

- `site-modules/profile_app_stack/templates/profile_app_stack/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/profile_app_stack/app.env.erb`
- `site-modules/profile_app_stack/templates/profile_app_stack/app.service.epp`

No template is rendered directly by `profile_postgresql`.

## Module Explanation

The module executes through the following containment and ordering chain:

1. **`role::app_server`** (`site-modules/role/manifests/app_server.pp`):
   - Includes the application-stack profile through `profile::app::stack`.
   - Also includes `profile::base::base`, `profile::loadbalancer::haproxy`, and `profile::cache::redis`.
   - These unrelated role dependencies are outside the analyzed PostgreSQL implementation.

2. **`profile::app::stack`** (`site-modules/profile/manifests/app/stack.pp`):
   - Bridges the role to the `profile_app_stack` class.
   - The supplied execution tree confirms the containment path but does not provide additional resource details.

3. **`profile_app_stack`** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Computes the application database URL from the database user, password, host, port, and name.
   - Contains `profile_app_stack::python`.
   - Contains `profile_app_stack::database`.
   - Contains `profile_app_stack::app`.
   - Contains `profile_app_stack::service`.
   - Contains `profile_app_stack::monitoring`.
   - Orders the phases as follows:
     - `Class['profile_app_stack::python'] -> Class['profile_app_stack::database']`
     - `Class['profile_app_stack::database'] -> Class['profile_app_stack::app']`
     - `Class['profile_app_stack::app'] ~> Class['profile_app_stack::service']`
     - `Class['profile_app_stack::service'] -> Class['profile_app_stack::monitoring']`

4. **`profile_app_stack::python`** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Runs before the database phase.
   - Detailed resources were not supplied in the structured analysis.

5. **`profile_app_stack::database`** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Evaluates the condition `profile_app_stack::db_host == 'localhost'`.
   - Includes `profile_postgresql` only when the condition is true.
   - Declares application database initialization resources:
     - `exec['create_db_user']`
     - `exec['create_database']`
     - `exec['grant_db_privileges']`
   - Declares backup resources:
     - `file['/usr/local/bin/db-backup.sh']`
     - `cron['database_backup']`
   - The command strings, guards, environment values, ownership, mode, schedule, destination, database name, user name, and privilege set require source verification.
   - The Ansible migration should prefer PostgreSQL modules over shell commands:
     - `community.postgresql.postgresql_user`
     - `community.postgresql.postgresql_db`
     - `community.postgresql.postgresql_privs`

6. **`profile_postgresql`** (`site-modules/profile_postgresql/manifests/init.pp`):
   - Contains `profile_postgresql::repo`.
   - Contains `profile_postgresql::install`.
   - Contains `profile_postgresql::service`.
   - Orders the phases:
     - `Class['profile_postgresql::repo'] -> Class['profile_postgresql::install'] -> Class['profile_postgresql::service']`

7. **`profile_postgresql::repo`** (`site-modules/profile_postgresql/manifests/repo.pp`):
   - Includes the `apt` class.
   - Declares `apt::source['pgdg']` with `ensure => present`.
   - Configures the PGDG APT repository.
   - The repository resource expands into APT source, settings, and conditional key-management resources supplied by the APT dependency module.
   - APT update behavior depends on the configured update frequency and may use `exec['apt_update']`.
   - Optional APT purge, proxy, configuration, pin, PPA, keyring, and authentication resources are declared only when their corresponding settings are populated.
   - The APT dependency is intended for Debian-family systems.

8. **`profile_postgresql::install`** (`site-modules/profile_postgresql/manifests/install.pp`):
   - Declares `package['postgresql-15']` with `ensure => present`.
   - Declares `package['postgresql-contrib-15']` with `ensure => present`.
   - Declares `package['libpq-dev']` with `ensure => present`.
   - The supplied plan identifies `15` as the effective version, but the structured validation does not include the Hiera evidence needed to verify that override.

9. **`profile_postgresql::service`** (`site-modules/profile_postgresql/manifests/service.pp`):
   - Declares `service['postgresql']`.
   - Ensures the service is running and enabled at boot.

10. **`profile_app_stack::app`** (`site-modules/profile_app_stack/manifests/app.pp`):
    - Runs after the database phase.
    - Declares the application directory and repository resources.
    - Declares `exec['create_app_venv']`.
    - Declares `exec['install_requirements']`.
    - Contains a conditional branch based on `pip_packages`; the resulting resource or operation requires source verification.
    - Renders the application environment file from `profile_app_stack/app.env.erb`.
    - Declares `file['/usr/local/bin/app-healthcheck.sh']`.
    - Declares `exec['run_db_migrations']`.

11. **`profile_app_stack::service`** (`site-modules/profile_app_stack/manifests/service.pp`):
    - Runs after application deployment notification.
    - Renders the systemd unit from `profile_app_stack/app.service.epp`.
    - Declares `exec['systemd_daemon_reload']`.
    - Declares the application service resource.

12. **`profile_app_stack::monitoring`** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
    - Runs after the application service phase.
    - Declares virtual resources:
      - Virtual `package['prometheus-node-exporter']`
      - Virtual `service['prometheus-node-exporter']`
      - Virtual `package['prometheus-pushgateway']`
      - Virtual `cron['push_app_metrics']`
    - Realizes those virtual resources in the production environment.
    - Declares `cron['app_health_check']`.
    - These are ordinary Puppet virtual resources and do not require PuppetDB.

## Variables

**Variable Flow Summary**: The supplied plan identifies one PostgreSQL version default, one higher-priority version override, six Debian-specific PostgreSQL variables, five application database inputs, and additional application-stack variables. The concrete Hiera hierarchy and values are not verifiable from the structured execution analysis and must be confirmed before migration.

### Variable Definitions

#### `site-modules/profile_postgresql/data/common.yaml` — module defaults

Migration note: Default PostgreSQL settings for the profile. The file path is supplied by the plan; values require Hiera-source verification.

- `profile_postgresql::version`: `"16"` (type: string)
- `profile_postgresql::package_names`: `["postgresql-${version}", "postgresql-contrib-${version}"]` (type: array)
- `profile_postgresql::service_name`: `"postgresql"` (type: string)
- `profile_postgresql::repo_location`: `"https://apt.postgresql.org/pub/repos/apt"` (type: string)
- `profile_postgresql::repo_release`: `"<Debian distribution codename>-pgdg"` (type: string)
- `profile_postgresql::repo_key_id`: `"B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8"` (type: string)
- `profile_postgresql::repo_key_source`: `"https://www.postgresql.org/media/keys/ACCC4CF8.asc"` (type: string)

#### `data/common.yaml` — control-repository override

Migration note: Higher-priority common data intended to override the module default. The override requires verification against the actual Hiera data.

- `profile_postgresql::version`: `"15"` (type: string)
  - Intended effective value: `"15"`
  - Effective package names if confirmed:
    - `postgresql-15`
    - `postgresql-contrib-15`

#### `site-modules/profile_postgresql/data/os/Debian.yaml` — Debian-specific data

Migration note: Debian-family package, service, repository, and signing-key settings. The listed values require verification against the actual file.

- `profile_postgresql::package_names`: `["postgresql-${version}", "postgresql-contrib-${version}"]` (type: array)
- `profile_postgresql::service_name`: `"postgresql"` (type: string)
- `profile_postgresql::repo_location`: `"https://apt.postgresql.org/pub/repos/apt"` (type: string)
- `profile_postgresql::repo_release`: `"<Debian distribution codename>-pgdg"` (type: string)
- `profile_postgresql::repo_key_id`: `"B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8"` (type: string)
- `profile_postgresql::repo_key_source`: `"https://www.postgresql.org/media/keys/ACCC4CF8.asc"` (type: string)

#### `environment/production.yaml` — production data

Migration note: No PostgreSQL-specific overrides were supplied in the plan. Verify that the file contains no relevant overrides.

- No verified `profile_postgresql` variables supplied.

#### `environment/staging.yaml` — staging data

Migration note: No PostgreSQL-specific overrides were supplied in the plan. Verify that the file contains no relevant overrides.

- No verified `profile_postgresql` variables supplied.

#### Application database variables

Migration note: These variables are referenced by the application-stack manifests, but their values, types, and Hiera levels were not supplied.

- `profile_app_stack::db_host`: unresolved value and type
- `profile_app_stack::db_port`: unresolved value and type
- `profile_app_stack::db_name`: unresolved value and type
- `profile_app_stack::db_user`: unresolved value and type
- `profile_app_stack::db_password`: unresolved sensitive value and type

The local PostgreSQL branch is enabled only when `profile_app_stack::db_host` equals `"localhost"`.

#### Additional application-stack variables

Migration note: These variables are referenced by the surrounding application stack. Their Hiera sources, values, and types require verification.

- `profile_app_stack::app_name`: unresolved value and type
- `profile_app_stack::app_repo`: unresolved value and type
- `profile_app_stack::app_revision`: unresolved value and type
- `profile_app_stack::app_port`: unresolved value and type
- `profile_app_stack::app_dir`: unresolved value and type
- `profile_app_stack::app_user`: unresolved value and type
- `profile_app_stack::app_group`: unresolved value and type
- `profile_app_stack::worker_count`: unresolved value and type
- `profile_app_stack::worker_class`: unresolved value and type
- `profile_app_stack::max_requests`: unresolved value and type
- `profile_app_stack::graceful_timeout`: unresolved value and type
- `profile_app_stack::log_dir`: unresolved value and type
- `profile_app_stack::log_level`: unresolved value and type
- `profile_app_stack::secret_key`: unresolved sensitive value and type

### Variable Migration Summary

- **Common defaults**: 1 verified variable category; exact Hiera contents require verification
- **Control-repository overrides**: 1 intended PostgreSQL version override
- **OS-specific variables**: 6 intended package, service, repository, and signing-key variables
- **Environment-specific variables**: 0 PostgreSQL-specific values supplied
- **Application database variables**: 5 unresolved variables required by database initialization
- **Additional application variables**: 15 unresolved variables used by the surrounding stack
- **Encrypted variables**: 0 eyaml-encrypted values detected in the supplied material
- **Sensitive variables**: `profile_app_stack::db_password` and `profile_app_stack::secret_key` are referenced as sensitive inputs; their actual storage and values are unverified

### Complete Hiera-to-Ansible Mapping

- `profile_postgresql::version` → `postgresql_version`
- `profile_postgresql::package_names` → `postgresql_package_names`
- `profile_postgresql::service_name` → `postgresql_service_name`
- `profile_postgresql::repo_location` → `postgresql_repo_location`
- `profile_postgresql::repo_release` → `postgresql_repo_release`
- `profile_postgresql::repo_key_id` → `postgresql_repo_key_id`
- `profile_postgresql::repo_key_source` → `postgresql_repo_key_source`
- `profile_app_stack::db_host` → `app_db_host`
- `profile_app_stack::db_port` → `app_db_port`
- `profile_app_stack::db_name` → `app_db_name`
- `profile_app_stack::db_user` → `app_db_user`
- `profile_app_stack::db_password` → `app_db_password`
- `profile_app_stack::app_name` → `app_name`
- `profile_app_stack::app_repo` → `app_repo`
- `profile_app_stack::app_revision` → `app_revision`
- `profile_app_stack::app_port` → `app_port`
- `profile_app_stack::app_dir` → `app_dir`
- `profile_app_stack::app_user` → `app_user`
- `profile_app_stack::app_group` → `app_group`
- `profile_app_stack::worker_count` → `app_worker_count`
- `profile_app_stack::worker_class` → `app_worker_class`
- `profile_app_stack::max_requests` → `app_max_requests`
- `profile_app_stack::graceful_timeout` → `app_graceful_timeout`
- `profile_app_stack::log_dir` → `app_log_dir`
- `profile_app_stack::log_level` → `app_log_level`
- `profile_app_stack::secret_key` → `app_secret_key`

### Cross-Level Overrides

- **`profile_postgresql::version`**
  - Intended definitions:
    - `site-modules/profile_postgresql/data/common.yaml`: `"16"`
    - `data/common.yaml`: `"15"`
  - Intended merge strategy: first value from the higher-priority Hiera level wins
  - Intended effective value: `"15"`
  - Status: requires verification against actual Hiera lookup behavior

### Merge Strategy Notes

- Variables using `hash` merge have values from multiple levels merged shallowly.
- Variables using `deep` merge are recursively merged.
- Variables using `first`, the default strategy, use the first value found.
- No confirmed hash or deep merge declarations were supplied.

### Recommended Ansible Defaults

```yaml
# roles/profile_postgresql/defaults/main.yml
postgresql_version: "16"
postgresql_service_name: "postgresql"
postgresql_package_names:
  - "postgresql-{{ postgresql_version }}"
  - "postgresql-contrib-{{ postgresql_version }}"
postgresql_repo_location: "https://apt.postgresql.org/pub/repos/apt"
postgresql_repo_key_id: "B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8"
postgresql_repo_key_source: "https://www.postgresql.org/media/keys/ACCC4CF8.asc"
postgresql_dev_package: "libpq-dev"

# Higher-precedence inventory or group variable, pending Hiera verification
postgresql_version: "15"
```

## Custom Types and Providers

No custom Puppet types or providers were identified in the supplied material.

No custom facts or functions can be confirmed from the structured execution analysis. The previous claim regarding a custom `profile_app_stack::app_db_url` function is unsupported and should not be migrated as a custom function without source evidence.

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

`puppetlabs-apt` is directly relevant to the PostgreSQL repository.

**System package dependencies**:

- `postgresql-15`
- `postgresql-contrib-15`
- `libpq-dev`
- GnuPG support may be required for repository signing-key management

**Service dependencies**:

- PGDG repository configuration precedes package installation.
- Package installation precedes PostgreSQL service activation.
- PostgreSQL service activation precedes application database initialization.
- Application database initialization precedes application deployment.
- Application deployment notifies the application service phase.
- Application service setup precedes monitoring.

## Puppet Facts Used

- `$facts['os']['family']`
  - Used to identify Debian-family systems for APT behavior.
- `$facts['os']['name']`
  - Used by the APT dependency module for distribution-specific behavior.
- `$facts['os']['release']['full']`
  - Used by the APT dependency module for release-version comparisons.
- `apt_update_last_success`
  - Used to determine whether a scheduled APT update is due.
- `$facts['environment']`
  - Used by monitoring to realize Prometheus resources in production.
- `fact('environment')`
  - Used by the application-stack context to obtain the Puppet environment.

Ansible equivalents:

- `ansible_facts.os_family`
- `ansible_facts.distribution`
- `ansible_facts.distribution_release`
- `ansible_facts.distribution_version`
- Inventory or group variables for environment classification

## Template Conversion Notes

No template is rendered directly by `profile_postgresql`.

The surrounding application stack references these templates:

- `site-modules/profile_app_stack/templates/profile_app_stack/logrotate.conf.erb`
  - Destination: `/etc/logrotate.d/<app_name>`
  - Expected render count: one per application-stack instance
  - Variables and Ruby logic require template-source inspection.
- `site-modules/profile_app_stack/templates/profile_app_stack/app.env.erb`
  - Destination: `<app_dir>/.env`
  - Expected render count: one
  - May contain application database connection values and sensitive values; exact contents require inspection.
  - Render with restrictive permissions and protect Ansible output.
- `site-modules/profile_app_stack/templates/profile_app_stack/app.service.epp`
  - Destination: `/etc/systemd/system/<app_name>.service`
  - Expected render count: one
  - Exact variables, conditionals, and service commands require template-source inspection.

Sensitive values must be stored in Ansible Vault or an external secret manager. Tasks consuming or rendering `app_db_password` or `app_secret_key` should use `no_log: true`, and passwords must not be passed as shell command-line arguments.

## PuppetDB Dependencies

No PuppetDB dependencies were detected.

- No exported resources using `@@`
- No resource collectors using `<<| |>>`
- No `puppetdb_query()` calls

The monitoring class uses ordinary Puppet virtual resources and realizes them directly in the production conditional.

## Credentials

- **Application database password**
  - Puppet variable: `profile_app_stack::db_password`
  - Ansible variable: `app_db_password`
  - Used by application database initialization and potentially the application environment file
  - Value, Hiera source, encryption status, and exact handling require verification
  - Store in Ansible Vault or an external secret manager
  - Use `no_log: true`
  - Do not place it in command-line arguments or ordinary task output

- **Application secret key**
  - Puppet variable: `profile_app_stack::secret_key`
  - Ansible variable: `app_secret_key`
  - Referenced by the surrounding application stack
  - No verified plaintext fallback was supplied; the previous `"changeme"` claim must not be treated as authoritative
  - Store in Ansible Vault or an external secret manager
  - Use `no_log: true`

No eyaml-encrypted values were detected in the supplied material. Redis credentials and TLS values belong to the separately referenced Redis profile.

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
- `site-modules/profile_postgresql/manifests/init.pp`
- `site-modules/profile_postgresql/manifests/repo.pp`
- `site-modules/profile_postgresql/manifests/install.pp`
- `site-modules/profile_postgresql/manifests/service.pp`
- `site-modules/profile_postgresql/data/common.yaml`
- `site-modules/profile_postgresql/data/os/Debian.yaml`
- `data/common.yaml`
- `environment/production.yaml`
- `environment/staging.yaml`
- `site-modules/profile_app_stack/templates/profile_app_stack/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/profile_app_stack/app.env.erb`
- `site-modules/profile_app_stack/templates/profile_app_stack/app.service.epp`
- `migration-dependencies/apt/manifests/init.pp`
- `migration-dependencies/apt/manifests/update.pp`
- `migration-dependencies/apt/manifests/conf.pp`
- `migration-dependencies/apt/manifests/key.pp`
- `migration-dependencies/apt/manifests/keyring.pp`
- `migration-dependencies/apt/manifests/pin.pp`
- `migration-dependencies/apt/manifests/ppa.pp`
- `migration-dependencies/apt/manifests/setting.pp`
- `migration-dependencies/apt/manifests/source.pp`

**Service endpoints to check**:

- **Local PostgreSQL instance**: service `postgresql`, TCP port `5432`
- **Application database endpoint**: `profile_app_stack::db_port`, value unresolved
- **Application service**: service name and port unresolved pending Hiera and manifest verification

**Templates rendered**:

- **PostgreSQL templates**: none
- `profile_app_stack/logrotate.conf.erb`: one render per application-stack instance
- `profile_app_stack/app.env.erb`: one render
- `profile_app_stack/app.service.epp`: one render

## Pre-flight checks

```bash
# Confirm the target operating system
facter os.family
facter os.name
facter os.release.full

# Confirm the local PostgreSQL branch is enabled after resolving Hiera
# profile_app_stack::db_host must equal localhost

# Confirm the intended PostgreSQL version and package names
apt-cache policy postgresql-15
apt-cache policy postgresql-contrib-15
apt-cache policy libpq-dev

# Confirm the PGDG repository and signing key after Hiera verification
grep -R "apt.postgresql.org" /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null
gpg --list-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Validate APT metadata
apt-get update

# Check the individually named local PostgreSQL instance
systemctl is-enabled postgresql
systemctl is-active postgresql
pg_isready --host 127.0.0.1 --port 5432

# Verify installed packages for the local PostgreSQL instance
dpkg-query -W postgresql-15 postgresql-contrib-15 libpq-dev

# Verify the application database resources after their unresolved
# names, credentials, guards, and parameters are recovered
# community.postgresql.postgresql_user
# community.postgresql.postgresql_db
# community.postgresql.postgresql_privs

# Verify application database connectivity on the resolved application port
# pg_isready --host localhost --port <profile_app_stack::db_port>

# Validate application migrations and service configuration after source inspection
# <application migration command>
# systemctl daemon-reload
# systemctl status <application service>

# Confirm sensitive values are absent from Ansible output and shell history
# Check app_db_password and app_secret_key handling with no_log enabled
```