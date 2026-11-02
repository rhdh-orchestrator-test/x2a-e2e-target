---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: `profile_redis_cluster` provisions one implicit Redis instance named `default` through the vendored `puppet-redis` dependency. The effective configuration is reported as listening on `0.0.0.0:6379`, requiring the Redis password `test-redis-password`, enabling AOF persistence with `everysec` fsync, and limiting memory to `256mb`. The explicit `instances` hash is empty, so no additional named instances are created. The profile installs the OS-specific Redis package, creates Redis directories and configuration files, manages the Redis service, applies a `LimitNOFILE` value of `65536`, and copies the Puppet-generated configuration into the active Redis configuration path. Hiera values, template paths and render counts, PuppetDB usage, custom fact behavior, and several resolved OS-specific values require verification against the source manifests and data. Ansible should use inventory groups instead of PuppetDB discovery and store the Redis password in Ansible Vault or an external secret manager.

## Service Type and Instances

**Service Type**: Redis cache/database service

**Configured Instances**:

- **default**: Primary Redis daemon managed by the `redis` class.
  - Package:
    - Debian: `redis-server`
    - RedHat, Suse, FreeBSD, and Archlinux: `redis`
  - Service:
    - Debian: `redis-server`
    - RedHat, Suse, FreeBSD, and Archlinux: `redis`
  - Bind address: `0.0.0.0`
  - Port: `6379`
  - Authentication: reported effective value `test-redis-password`; source Hiera data requires verification
  - Maximum memory: reported effective value `256mb`; source Hiera data requires verification
  - Maximum-memory policy: `undef` is passed to `redis`; the profile parameter default is reported as `allkeys-lru`, but it is not passed to the Redis class and is therefore not explicitly rendered
  - Persistence:
    - `appendonly`: `true`
    - `appendfsync`: `everysec`
  - Configuration:
    - Debian active file: `/etc/redis/redis.conf`
    - Debian generated source: `/etc/redis/redis.conf.puppet`
    - RedHat 9+ active file: `/etc/redis/redis.conf`
    - RedHat 9+ generated source: `/etc/redis/redis.conf.puppet`
    - RedHat 8 and earlier active file: `/etc/redis.conf`
    - RedHat 8 and earlier generated source: `/etc/redis.conf.puppet`
  - Data directory: `/var/lib/redis`
  - Log directory: `/var/log/redis`
  - Unix socket: `/var/run/redis/redis.sock`
  - PID file:
    - Debian: `/var/run/redis/redis-server.pid`
    - RedHat: `/var/run/redis_6379.pid`
  - File-descriptor limit: `65536`

No additional explicit instance is created because `instances: {}` and the `$instances.each |$key, $values|` loop executes zero times.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
### Manifests

- `site-modules/role/manifests/redis_cluster.pp`
- `site-modules/profile/manifests/cache/redis.pp`
- `site-modules/profile_redis_cluster/manifests/init.pp`
- `site-modules/profile_redis_cluster/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`

### Custom components

- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`

### Supporting dependency components referenced by the execution tree

- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/params.pp`

No templates are present in the supplied directory listing. The vendored Redis dependency is reported to reference upstream EPP templates, including `redis/redis.conf.epp` and `redis/service_templates/redis.service.epp`, but their source files were not included in the supplied execution-tree listing.
```

## Module Explanation

The module performs operations in this order:

1. **`role::redis_cluster`** (`site-modules/role/manifests/redis_cluster.pp`):
   - Proceeds through the Linux branch when `$facts['kernel'].downcase == 'linux'`.
   - The branch contains an `exec[None]`; its exact command, path, and refresh behavior are not available in the supplied analysis.
   - Includes `::profile::base::base`; that class is outside this migration scope.
   - Includes `::profile::cache::redis`.
   - Orders `Class['::profile::base::base']` before `Class['::profile::cache::redis']`.
   - Uses `$facts['kernel']`.
   - Any use of `fact('environment')` by this role is unverified and should not be attributed to the role without source confirmation.

2. **`::profile::cache::redis`** (`site-modules/profile/manifests/cache/redis.pp`):
   - Includes `profile_redis_cluster`.
   - Has no direct resources listed in the supplied execution tree.
   - Uses `fact('environment')` according to the supplied validation information.

3. **`profile_redis_cluster`** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Receives the reported effective profile values:
     - `redis_port`: `6379`
     - `redis_password`: `test-redis-password`
     - `maxmemory_mb`: `256`
     - `maxmemory_policy`: `allkeys-lru`
   - The Hiera source, value types, hierarchy, and override behavior require verification.
   - Contains `profile_redis_cluster::install`.
   - A PuppetDB query is reported in this class, but the supplied structured execution tree does not verify it. If present in the source, it is:
     - `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
     - Intended to discover certnames containing `Profile_redis_cluster`.
     - Reported result variable: `$redis_nodes`.
     - Reported runtime behavior: the result is not subsequently consumed.
   - The query should be replaced in Ansible with an inventory group such as `redis_cluster`, host variables, or another service-discovery source.
   - The query must not be treated as confirmed until the manifest source is inspected.

4. **`profile_redis_cluster::install`** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - Declares `redis` with the reported values:
     - `redis::bind`: `0.0.0.0`
     - `redis::port`: `6379`
     - `redis::requirepass`: `test-redis-password`
     - `redis::maxmemory`: `256mb`
     - `redis::appendonly`: `true`
     - `redis::appendfsync`: `everysec`
     - `redis::manage_package`: `true`
   - Contains `redis`.

5. **`redis`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits `redis::params`.
   - Uses the reported effective parameters:
     - `bind`: `0.0.0.0`
     - `port`: `6379`
     - `requirepass`: `test-redis-password`
     - `maxmemory`: `256mb`
     - `maxmemory_policy`: `undef`
     - `appendonly`: `true`
     - `appendfsync`: `everysec`
     - `manage_package`: `true`
     - `manage_repo`: `false`
     - `default_install`: `true`
     - `instances`: `{}`
     - `config_file_mode`: `0640`
     - `log_dir`: `/var/log/redis`
     - `workdir`: `/var/lib/redis`
     - `service_user`: `redis`
     - `service_group`: `redis`
     - `service_manage`: `true`
     - `service_enable`: `true`
     - `service_ensure`: `running`
     - `notify_service`: `true`
     - `ulimit_managed`: `true`
     - `managed_by_cluster_manager`: `false`
     - `manage_service_file`: `false`
     - `ulimit`: `65536`
     - `unixsocket`: `/var/run/redis/redis.sock`
     - `unixsocketperm`: `0755`
     - `conf_template`: `redis/redis.conf.epp`
     - `databases`: `16`
     - `protected_mode`: `true`
     - `save_db_to_disk`: `true`
     - `dbfilename`: `dump.rdb`
     - `log_file`: `redis.log`
     - `log_level`: `notice`
     - `maxclients`: `10000`
     - `cluster_enabled`: `false`
     - `modules`: `[]`
     - `acls`: `[]`
   - Uses OS-dependent configuration directories, ownership, modes, daemonization, service names, and configuration groups reported in the original plan. These values require source and parameter-file verification.
   - Contains, in order:
     1. `redis::preinstall`
     2. `redis::install`
     3. `redis::config`
     4. `redis::service`
   - Orders `Class['redis::preinstall'] -> Class['redis::install'] -> Class['redis::config']`.
   - Sends configuration changes from `Class['redis::config']` to `Class['redis::service']` because `notify_service` is `true`.

6. **`redis::preinstall`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Does not manage repositories when `manage_repo: false`.
   - The repository-management branch executes zero times.
   - No APT repository, PPA, signing key, or keyring resources are created.
   - Reported inactive repository values include:
     - Location: `https://packages.redis.io/deb/`
     - Repository: `main`
     - Key ID: `54318FA4052D1E61A6B6F7BB5F4349D6BF53AA0C`
     - Key server: `hkp://keyserver.ubuntu.com/`
   - These inactive values are not required for the current migration.

7. **`redis::install`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Creates a package resource because `manage_package: true`.
   - Reported package resources:
     - Debian: `package['redis-server']` with `ensure => installed`
     - RedHat: `package['redis']` with `ensure => installed`
     - FreeBSD: `package['redis']` with `ensure => installed`
     - Suse: `package['redis']` with `ensure => installed`
     - Archlinux: `package['redis']` with `ensure => installed`
   - Does not create the DNF module package because `dnf_module_stream` is `undef`.

8. **`redis::config`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - Creates `/etc/redis` as a directory on Debian/RedHat-style systems.
   - Creates `/var/log/redis` as a Redis-owned log directory.
   - Creates `/var/lib/redis` as a Redis-owned data directory.
   - Uses reported modes:
     - Configuration directory: `0755`
     - Log directory: Debian `0755`, RedHat `0750`
     - Data directory: `0750`
   - Creates the implicit `redis::instance['default']` because `default_install: true`.
   - Supplies the default instance with:
     - `pid_file`: Debian `/var/run/redis/redis-server.pid`; RedHat `/var/run/redis_6379.pid`
     - `log_file`: `redis.log`
     - `unixsocket`: `/var/run/redis/redis.sock`
     - `workdir`: `/var/lib/redis`
     - `daemonize`: Debian `true`; RedHat `false`
     - `service_name`: Debian `redis-server`; RedHat `redis`
     - `manage_service_file`: `false`
     - `acls`: `[]`
   - Contains `redis::ulimit` because `ulimit_managed: true`.
   - Creates `/etc/default/redis-server` only on Debian systems.
   - The non-Debian branch for that resource executes zero times.

9. **`redis::ulimit`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`):
   - Does not create cluster-manager limits because `managed_by_cluster_manager: false`.
   - Removes obsolete drop-ins:
     - Debian: `/etc/systemd/system/redis-server.service.d/limit.conf`
     - RedHat and other `redis` service systems: `/etc/systemd/system/redis.service.d/limit.conf`
   - Manages a systemd drop-in for the `default` instance:
     - Unit: `redis-server` on Debian or `redis` on RedHat
     - Limit: `LimitNOFILE: 65536`
     - Notification: disabled for the drop-in
   - Does not create a complete instance-specific systemd unit because `manage_service_file: false`.

10. **`redis::instance['default']`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`):
    - The explicit `$instances.each |$key, $values|` loop executes zero times because `instances: {}`.
    - The implicit `default` instance is created by `redis::config`.
    - Uses the main configuration paths rather than suffixed multi-instance paths.
    - Does not create additional log or data directories because the instance paths equal `/var/log/redis` and `/var/lib/redis`.
    - Does not create a complete systemd unit because `manage_service_file: false`.
    - Uses direct EPP rendering because no template parameter is reported as a `Deferred` value.
    - Writes the generated configuration to:
      - Debian and RedHat 9+: `/etc/redis/redis.conf.puppet`
      - RedHat 8 and earlier: `/etc/redis.conf.puppet`
    - Copies the generated file to:
      - Debian and RedHat 9+: `/etc/redis/redis.conf`
      - RedHat 8 and earlier: `/etc/redis.conf`
    - The copy command is refresh-only and is reported as:
      - `cp -p /etc/redis/redis.conf.puppet /etc/redis/redis.conf`
      - `cp -p /etc/redis.conf.puppet /etc/redis.conf`
      - Executable path: `/usr/bin:/bin`
    - Configuration changes refresh the copy command, and the copy command notifies the Redis service.

11. **`redis::service`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
    - Manages the service because `service_manage: true`.
    - Enables and starts:
      - Debian: `service['redis-server']`
      - RedHat, Suse, FreeBSD, and Archlinux: `service['redis']`
    - Applies `ensure => running` and `enable => true`.
    - Receives refresh notifications from `redis::config`.

## Variables

**Variable Flow Summary**: 4 profile parameters are reported, with 2 values attributed to `data/common.yaml` and 2 manifest defaults. The supplied validation information does not include structured Hiera data, so Hiera paths, hierarchy levels, types, and override behavior require verification. The Redis class also receives OS-specific defaults from `redis::params`.

### Variable Definitions

**Reported `data/common.yaml` values — source verification required**  
Migration note: These values were present in the original plan but are not supported by the supplied structured validation analysis.

- `profile_redis_cluster::redis_password`: `test-redis-password` (reported type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (reported type: integer)

**`profile_redis_cluster` manifest defaults**

- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::redis_password`: `CHANGEME` (type: string; reported as overridden)
- `profile_redis_cluster::maxmemory_mb`: `2048` (type: integer; reported as overridden)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string; reported as not passed to `redis`)

**Values passed from the profile to `redis`**

- `redis::bind`: `0.0.0.0` (type: string)
- `redis::port`: `6379` (type: integer)
- `redis::requirepass`: `test-redis-password` (type: string; source value requires verification)
- `redis::maxmemory`: `256mb` (type: string; source value requires verification)
- `redis::appendonly`: `true` (type: boolean)
- `redis::appendfsync`: `everysec` (type: string)
- `redis::manage_package`: `true` (type: boolean)

**OS-specific values from `redis::params`**

- Package name:
  - Debian: `redis-server`
  - RedHat, Suse, FreeBSD, and Archlinux: `redis`
- Service name:
  - Debian: `redis-server`
  - RedHat, Suse, FreeBSD, and Archlinux: `redis`
- Configuration path:
  - Debian and RedHat 9+: `/etc/redis/redis.conf`
  - RedHat 8 and earlier: `/etc/redis.conf`
- Generated configuration path:
  - Debian and RedHat 9+: `/etc/redis/redis.conf.puppet`
  - RedHat 8 and earlier: `/etc/redis.conf.puppet`
- Configuration owner: normally `redis`
- Configuration group:
  - Ubuntu: `redis`
  - Debian non-Ubuntu: `root`
  - RedHat: `root`
- Daemonization:
  - Debian: `true`
  - RedHat: `false`
- Log directory mode:
  - Debian: `0755`
  - RedHat: `0750`

### Variable Migration Summary

- **Common defaults**: 2 reported variables from `data/common.yaml`; values require Hiera verification
- **Manifest defaults**: 4 profile parameters, including 2 reported effective overrides
- **OS-specific variables**: package names, service names, paths, ownership, modes, and daemonization settings
- **Environment-specific variables**: 0 supplied variables
- **Host-specific variables**: 0 supplied variables
- **Encrypted variables**: 0 eyaml values detected in the supplied plan
- **Sensitive variables**: 1 active Redis password requiring Vault or external secret storage

Recommended Ansible variables:

```yaml
redis_cluster_port: 6379
redis_cluster_password: "{{ vault_redis_cluster_password }}"
redis_cluster_maxmemory: "256mb"
redis_cluster_maxmemory_policy: "allkeys-lru"
redis_cluster_bind:
  - "0.0.0.0"
redis_cluster_appendonly: true
redis_cluster_appendfsync: "everysec"
redis_cluster_instances: []
```

### Cross-Level Overrides

The following overrides are reported but require verification against the actual Hiera hierarchy:

- `profile_redis_cluster::redis_password`:
  - Manifest default: `CHANGEME`
  - Reported common Hiera value: `test-redis-password`
  - Reported effective value: `test-redis-password`
  - Merge strategy: scalar override; higher-priority Hiera value wins
- `profile_redis_cluster::maxmemory_mb`:
  - Manifest default: `2048`
  - Reported common Hiera value: `256`
  - Reported effective value: `256`
  - Merge strategy: scalar override; higher-priority Hiera value wins

### Merge Strategy Notes

- Variables using `hash` merge combine values from multiple levels with a shallow merge.
- Variables using `deep` merge recursively combine nested hash values.
- Variables using `first` use the first value found; this is the default scalar behavior.
- The supplied analysis does not establish any active deep or hash merge for this profile.
- `instances` is reported as an empty hash and therefore produces no explicit instances.

## Custom Types and Providers

### Custom fact: `redis_role`

- File: `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- Reported confinement: Linux
- Reported input: `/etc/redis/conf.d/replica.conf`
- Reported result:
  - `replica` when the file exists and contains `replicaof`
  - `primary` otherwise
- Parameters: none
- The supplied structured execution analysis does not include the custom fact implementation, so confinement, file path, matching behavior, and return values require source verification.
- The Redis profile execution tree does not show this fact being consumed.
- Ansible equivalent, if confirmed as required:
  - Deploy `/etc/ansible/facts.d/redis_role.fact`, or
  - Use `stat` and `slurp` followed by `set_fact`.
  - Preserve the `replicaof` substring test.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` version `9.6.0`
- `puppet-redis` version `11.0.0`
- `puppetlabs-apt` version `9.4.0`

**System package dependencies**:

- Debian: `redis-server`
- RedHat: `redis`
- Suse: `redis`
- FreeBSD: `redis`
- Archlinux: `redis`

**Service dependencies**:

- `redis::preinstall -> redis::install -> redis::config`
- `redis::config ~> redis::service`
- Generated configuration changes refresh the copy command.
- The copy command notifies the Redis service.
- The default instance does not create a complete systemd unit because `manage_service_file: false`.

## Puppet Facts Used

- `$facts['kernel']`
  - Determines whether `role::redis_cluster` enters the Linux branch.
- `fact('environment')`
  - Used by `::profile::cache::redis` according to the supplied validation information.
  - Usage by `role::redis_cluster` is not confirmed and is not attributed to that class.
- `$facts['os']['name']`
  - Reported as distinguishing Ubuntu from other operating systems in parameter and repository logic.
- `$facts['os']['family']`
  - Reported as selecting Debian, RedHat, FreeBSD, Suse, Archlinux, or default behavior.
- `$facts['os']['release']['major']`
  - Reported as selecting RedHat 9+ versus earlier RedHat configuration paths.
- `redis_role`
  - Reported as identifying replica configuration.
  - Custom fact behavior requires source verification.
  - Consumption is not shown in the supplied execution tree.

## Template Conversion Notes

### Redis configuration template

- Source reported by the vendored dependency: `redis/redis.conf.epp`
- Render count: reported as `1`, but not verifiable from the supplied structured analysis
- Destination:
  - Debian and RedHat 9+: `/etc/redis/redis.conf.puppet`
  - RedHat 8 and earlier: `/etc/redis.conf.puppet`
- Rendered for the implicit `default` instance.
- Direct EPP rendering is reported because no active template parameter is `Deferred`.
- The reported effective settings include:
  - `bind 0.0.0.0`
  - `port 6379`
  - `requirepass test-redis-password`
  - `maxmemory 256mb`
  - `appendonly yes`
  - `appendfsync everysec`
- Preserve the reported save intervals:
  - `save 900 1`
  - `save 300 10`
  - `save 60 10000`
- Omit `undef` values instead of rendering invalid Redis directives.
- Convert Puppet booleans, arrays, and hashes to Redis-compatible directives.
- Ensure empty arrays and hashes do not produce unwanted configuration lines.
- Template source, render count, destination, and detailed EPP logic require verification against the template analysis or source file.

### Systemd service template

- Source reported by the vendored dependency: `redis/service_templates/redis.service.epp`
- Render count reported as `0` for the current default instance, but not verifiable from the supplied structured analysis.
- The default instance does not use this template because `manage_service_file: false`.
- If an additional instance is later configured with `manage_service_file: true`, the reported parameters include:
  - `bin_path`: `/usr/bin`
  - `instance_title`: instance name
  - `port`: instance port
  - `redis_file_name`: instance active configuration path
  - `service_name`: instance service name
  - `service_user`: `redis`
  - `service_timeout_start`: `undef`
  - `service_timeout_stop`: `undef`
  - `ulimit`: `65536`
  - `ulimit_managed`: `true`

## PuppetDB Dependencies

The supplied structured execution tree does not verify PuppetDB usage. The following dependency is reported in the original plan and must be confirmed against `site-modules/profile_redis_cluster/manifests/init.pp` before migration:

- **PuppetDB query**:
  - Query: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
  - Location: `profile_redis_cluster`
  - Reported purpose: discover certnames containing `Profile_redis_cluster`
  - Reported result variable: `$redis_nodes`
  - Reported use: no subsequent resource consumes the result
  - Migration: remove the query and represent cluster membership with an Ansible inventory group such as `redis_cluster`, `groups['redis_cluster']`, host variables, or a service-discovery source

No exported resources (`@@`) or resource collectors (`<<| |>>`) are shown in the supplied plan. The query is not confirmed by the structured validation data.

## Credentials and Secret Handling

- **Active Redis client password**
  - Puppet key: `profile_redis_cluster::redis_password`
  - Reported effective value: `test-redis-password`
  - Passed as: `redis::requirepass`
  - Migration: store the value in Ansible Vault or an external secret manager; use `no_log: true` for tasks that handle it
  - Do not copy the reported plaintext value into the Ansible repository

- **Optional replication master credential**
  - `redis::masterauth`
  - `redis::instance::masterauth`

- **Optional Redis client credentials**
  - `redis::requirepass`
  - `redis::instance::requirepass`

- **Optional Sentinel credentials**
  - `redis::sentinel::auth_pass`
  - `redis::sentinel::requirepass`

- **Optional TLS certificate and key references**
  - `redis::tls_cert_file`
  - `redis::tls_key_file`
  - `redis::tls_ca_cert_file`
  - `redis::tls_ca_cert_dir`
  - Per-instance equivalents
  - Sentinel equivalents

- **Repository key material parameters**
  - `apt::key::content`
  - `apt::key::source`
  - `apt::keyring::content`
  - `apt::keyring::source`

No `ENC[PKCS7,...]` values or active `Sensitive`-typed profile password are shown in the supplied plan.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/redis_cluster.pp`
- `site-modules/profile/manifests/cache/redis.pp`
- `site-modules/profile_redis_cluster/manifests/init.pp`
- `site-modules/profile_redis_cluster/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/params.pp`
- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- `data/common.yaml`
- Referenced EPP source files, if available:
  - `redis/redis.conf.epp`
  - `redis/service_templates/redis.service.epp`

**Service endpoints to check**:

- Default instance TCP endpoint: `127.0.0.1:6379`
- Default instance bind endpoint: `0.0.0.0:6379`
- Default instance Unix socket: `/var/run/redis/redis.sock`
- Default instance Redis authentication using the vaulted password
- Default instance Redis protocol response from `redis-cli -h 127.0.0.1 -p 6379`

**Templates rendered**:

- `redis/redis.conf.epp`: reported 1 render; verify against template analysis
- `redis/service_templates/redis.service.epp`: reported 0 renders for `default`; verify against template analysis

## Pre-flight checks

```bash
# Confirm operating system and release
facter os
facter kernel

# Confirm the resolved package and service names
case "$(facter os --show-legacy)" in
  *Debian*) echo "Expected package/service: redis-server" ;;
  *)        echo "Expected package/service: redis" ;;
esac

# Default instance: verify package
dpkg-query -W redis-server 2>/dev/null || rpm -q redis 2>/dev/null

# Default instance: verify service state
systemctl is-enabled redis-server 2>/dev/null || systemctl is-enabled redis 2>/dev/null
systemctl is-active redis-server 2>/dev/null || systemctl is-active redis 2>/dev/null

# Default instance: verify configuration paths
test -f /etc/redis/redis.conf || test -f /etc/redis.conf
test -f /etc/redis/redis.conf.puppet || test -f /etc/redis.conf.puppet

# Default instance: verify directories
test -d /var/lib/redis
test -d /var/log/redis
stat -c '%U:%G %a %n' /var/lib/redis /var/log/redis

# Default instance: verify Unix socket
test -S /var/run/redis/redis.sock

# Default instance: verify TCP listener
ss -ltn '( sport = :6379 )'

# Default instance: verify Redis connectivity and authentication
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning ping

# Default instance: verify active configuration
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning CONFIG GET bind
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning CONFIG GET port
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning CONFIG GET maxmemory
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning CONFIG GET appendonly
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning CONFIG GET appendfsync

# Default instance: verify systemd file-descriptor limit
systemctl show redis-server -p LimitNOFILE 2>/dev/null || systemctl show redis -p LimitNOFILE 2>/dev/null

# Default instance: verify ownership and permissions
stat -c '%U:%G %a %n' \
  /etc/redis/redis.conf \
  /etc/redis/redis.conf.puppet \
  /etc/redis.conf \
  /etc/redis.conf.puppet \
  /var/lib/redis \
  /var/log/redis 2>/dev/null

# Default instance: validate Redis configuration syntax where supported
redis-server --test-memory 2 2>/dev/null || true
```

