---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: Configures one Redis instance through `role::redis_cluster → profile::cache::redis → profile_redis_cluster → redis`. The analyzed configuration reports port `6379`, bind address `0.0.0.0`, password `test-redis-password` from plain Hiera data, maximum memory `256mb`, append-only persistence, and `appendfsync everysec`. The profile declares `maxmemory_policy: allkeys-lru`, but does not pass it to `class redis`; therefore the generated dependency configuration resolves `maxmemory_policy` to `undef` unless the Ansible migration intentionally adds `maxmemory-policy allkeys-lru`. The deployment has no additional Hiera-defined Redis instances. The base and Redis profiles are outside the Linux-only `exec[None]` conditional in the analyzed role; only that exec resource is confirmed as Linux-gated.

## Service Type and Instances

**Service Type**: Redis cache/database service

**Configured Instances**:

- **default**
  - Purpose: Primary Redis daemon created by `redis::config` when `default_install` is `true`.
  - Location/Path: OS-dependent Redis configuration and data paths.
  - Port/Socket: TCP `6379`; Unix socket `/var/run/redis/redis.sock`.
  - Bind address: `0.0.0.0`.
  - Authentication: `requirepass` set to `test-redis-password` in the supplied Hiera data. The source value is plain Hiera data, not currently vaulted.
  - Maximum memory: `256mb`.
  - Eviction policy: `maxmemory_policy` resolves to `undef`; `allkeys-lru` is only the profile-level declared default because it is not passed to `class redis`.
  - Append-only persistence: enabled.
  - Append fsync: `everysec`.
  - Service name:
    - Debian: `redis-server`
    - RedHat, FreeBSD, Suse, and Archlinux: `redis`
  - Configuration paths:
    - Debian and RedHat 9+: `/etc/redis/redis.conf.puppet` and `/etc/redis/redis.conf`
    - RedHat before version 9: `/etc/redis.conf.puppet` and `/etc/redis.conf`
  - Data directory: `/var/lib/redis` on Debian and RedHat.
  - Log directory: `/var/log/redis` on Debian and RedHat.
  - Configuration mode: `0640`.
  - Service state: enabled and running.
  - Additional instances: none; the `$instances.each` loop executes zero times because `instances` resolves to `{}`.

## File Structure

```text
site-modules/
├── role/
│   └── manifests/
│       └── redis_cluster.pp
├── profile/
│   └── manifests/
│       └── cache/
│           └── redis.pp
└── profile_redis_cluster/
    ├── manifests/
    │   ├── init.pp
    │   └── install.pp
    ├── migration-dependencies/
    │   └── redis/
    │       ├── manifests/
    │       │   ├── init.pp
    │       │   ├── preinstall.pp
    │       │   ├── install.pp
    │       │   ├── config.pp
    │       │   ├── instance.pp
    │       │   ├── ulimit.pp
    │       │   ├── service.pp
    │       │   └── dnfmodule.pp
    │       └── templates/
    │           ├── redis/
    │           │   └── redis.conf.epp
    │           └── service_templates/
    │               └── redis.service.epp
    └── lib/
        └── facter/
            └── redis_role.rb
```

Logical template references in the execution tree are:

- `redis/redis.conf.epp`
- `redis/service_templates/redis.service.epp`

The physical template locations must be confirmed in the dependency module during implementation.

## Module Explanation

The module performs operations in this order:

1. **`role::redis_cluster`** (`site-modules/role/manifests/redis_cluster.pp`)
   - References `facts['kernel']`.
   - Places only `exec[None]` inside the conditional checking whether `facts['kernel'].downcase == 'linux'`.
   - Includes `::profile::base::base`.
   - Includes `::profile::cache::redis`.
   - Orders `Class['::profile::base::base']` before `Class['::profile::cache::redis']`.
   - The analyzed tree does not establish that the two profile classes themselves are Linux-gated. Ansible must preserve the actual conditional behavior or intentionally add a documented Linux platform condition.

2. **`profile::cache::redis`** (`site-modules/profile/manifests/cache/redis.pp`)
   - References `fact('environment')`.
   - Includes `profile_redis_cluster`.
   - Is applied after `profile::base::base`.
   - No environment-specific Redis values are supplied by the analyzed data.

3. **`profile_redis_cluster`** (`site-modules/profile_redis_cluster/manifests/init.pp`)
   - Receives the profile parameters:
     - `redis_port`: reported as `6379`.
     - `redis_password`: reported as `test-redis-password` from `data/common.yaml`, overriding the manifest default `CHANGEME`.
     - `maxmemory_mb`: reported as `256` from `data/common.yaml`, overriding the manifest default `2048`.
     - `maxmemory_policy`: manifest default `allkeys-lru`; no Hiera override is reported.
   - Executes `puppetdb_query("resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }")`.
   - Assigns the result to `$redis_nodes`, but no resource consumes it.
   - Contains `profile_redis_cluster::install`.

4. **`profile_redis_cluster::install`** (`site-modules/profile_redis_cluster/manifests/install.pp`)
   - Declares `class redis` with:
     - `bind`: `0.0.0.0`
     - `port`: `6379`
     - `requirepass`: `test-redis-password`
     - `maxmemory`: `256mb`
     - `appendonly`: `true`
     - `appendfsync`: `everysec`
     - `manage_package`: `true`
   - Does not pass `maxmemory_policy`; the dependency receives `undef`.
   - Includes and contains:
     - `redis::preinstall`
     - `redis::install`
     - `redis::config`
     - `redis::service`
   - Orders preinstallation before package installation and package installation before configuration.
   - Sends configuration changes from `Class['redis::config']` to `Class['redis::service']`.

5. **`redis`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`)
   - Inherits OS-dependent values from `redis::params`.
   - Contains `redis::preinstall`, `redis::install`, `redis::config`, and `redis::service`.
   - Evaluates `$instances.each |$key, $values| { redis::instance { $key: * => $values } }` zero times because `instances` is `{}`.
   - Creates the implicit `redis::instance 'default'` through `redis::config` because `default_install` is `true`.
   - Uses `manage_package: true`, `service_manage: true`, `service_enable: true`, `service_ensure: running`, `ulimit_managed: true`, and `managed_by_cluster_manager: false`.
   - Uses `manage_repo: false`, `manage_service_file: false`, and `notify_service: true`.
   - Uses `redis/redis.conf.epp` as the configuration template.
   - Uses configuration mode `0640` and work-directory mode `0750`.
   - Sets the default log file to `redis.log` and Unix socket to `/var/run/redis/redis.sock`.

6. **`redis::preinstall`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`)
   - References `facts['os']['name']` and `facts['os']['family']`.
   - Evaluates `manage_repo: false`.
   - Skips Ubuntu PPA and Debian Redis repository branches.
   - Creates no `apt`, `apt::ppa`, or `apt::source` resources.
   - Installs no repository key.

7. **`redis::install`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`)
   - References `facts['os']['family']`.
   - Evaluates `manage_package: true`.
   - Installs the platform package with `ensure: installed`:
     - Debian: `redis-server`
     - RedHat: `redis`
     - FreeBSD: `redis`
     - Suse: `redis`
     - Archlinux: `redis`
   - Evaluates `dnf_module_stream: undef`; `redis::dnfmodule` is not executed.
   - Does not perform DNF module validation.

8. **`redis::config`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`)
   - Creates the configuration directory.
   - Creates the log directory.
   - Creates the Redis work directory.
   - Uses OS-dependent owners, groups, and directory modes.
   - Debian defaults:
     - Configuration directory: `/etc/redis`, mode `0755`.
     - Log directory: `/var/log/redis`, mode `0755`.
     - Work directory: `/var/lib/redis`, mode `0750`.
   - RedHat defaults:
     - Configuration directory: `/etc/redis`, mode `0755`, owner `redis`, group `root`.
     - Log directory: `/var/log/redis`, mode `0750`.
     - Work directory: `/var/lib/redis`, mode `0750`.
   - Declares the implicit `redis::instance 'default'`.
   - Contains `redis::ulimit` because `ulimit_managed` is `true`.
   - On Debian-family systems, manages `/etc/default/redis-server` with mode `0640`.
   - Does not manage `/etc/default/redis-server` on non-Debian systems.

9. **`redis::instance 'default'`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`)
   - Selects the original and active configuration paths by OS release:
     - Debian: `/etc/redis/redis.conf.puppet` → `/etc/redis/redis.conf`.
     - RedHat 9+: `/etc/redis/redis.conf.puppet` → `/etc/redis/redis.conf`.
     - RedHat before version 9: `/etc/redis.conf.puppet` → `/etc/redis.conf`.
   - Does not create additional log or work directories because the instance paths equal the global paths.
   - Does not create a `systemd::unit_file` because `manage_service_file` is `false`.
   - Declares the equivalent systemd limits drop-in through `systemd::manage_dropin` with:
     - `LimitNOFILE`: `65536`
     - `notify_service`: `false`
   - Renders `redis/redis.conf.epp` once.
   - Writes the rendered file to the original configuration path with owner and group selected by the OS and mode `0640`.
   - Copies the original configuration to the active path with `cp -p`.
   - Runs the copy only when the original configuration changes.
   - Uses the following effective settings:
     - `daemonize`: Debian `true`; RedHat `false`.
     - `pid_file`: Debian `/var/run/redis/redis-server.pid`; RedHat `/var/run/redis_6379.pid`.
     - `protected_mode`: `true`.
     - `port`: `6379`.
     - `tcp_backlog`: `511`.
     - `bind`: `0.0.0.0`.
     - `unixsocket`: `/var/run/redis/redis.sock`.
     - `unixsocketperm`: `0755`.
     - `log_level`: `notice`.
     - `log_file`: `/var/log/redis/redis.log`.
     - `databases`: `16`.
     - `save_db_to_disk`: `true`.
     - `requirepass`: `test-redis-password`.
     - `maxmemory`: `256mb`.
     - `maxmemory_policy`: `undef`.
     - `appendonly`: `true`.
     - `appendfilename`: `appendonly.aof`.
     - `appendfsync`: `everysec`.
     - `cluster_enabled`: `false`.
     - `modules`: `[]`.
     - `acls`: `[]`.
     - `custom_options`: `{}`.
     - TLS, replication, Sentinel, and Redis Cluster authentication settings: unset or disabled.

10. **`redis::ulimit`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`)
    - Is private and intended to be called by `redis::config`.
    - Evaluates `managed_by_cluster_manager: false`.
    - Does not create `/etc/security/limits.d/redis.conf`.
    - Ensures the legacy systemd limit drop-in is absent:
      - Debian: `/etc/systemd/system/redis-server.service.d/limit.conf`
      - Other supported service-name defaults: `/etc/systemd/system/redis.service.d/limit.conf`

11. **`redis::service`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`)
    - Evaluates `service_manage: true`.
    - Enables and starts the service:
      - Debian: `redis-server`
      - RedHat, FreeBSD, Suse, and Archlinux: `redis`
    - Receives configuration refresh notifications from `Class['redis::config']`.
    - Uses the Puppet Redis provider behavior for service refresh and restart operations.

## Variables

**Variable Flow Summary**: Four profile parameters are defined by the manifest. The supplied plan reports two effective values from `data/common.yaml`, one manifest-only value, and one profile default that is not propagated to the dependency class. The Hiera hierarchy and reported values require verification against the actual data files.

### Variable Definitions

#### `site-modules/profile_redis_cluster/manifests/init.pp` — manifest defaults

- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::redis_password`: `CHANGEME` (type: string; overridden according to the supplied plan)
- `profile_redis_cluster::maxmemory_mb`: `2048` (type: integer; overridden according to the supplied plan)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string; not passed to `class redis`)

#### `data/common.yaml` — reported common values

Migration note: The supplied plan identifies this file as the common Hiera source. Confirm the file contents, types, and lookup precedence during implementation.

- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string; secret value supplied as plain Hiera data)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

#### `data/environment/production.yaml`

Migration note: Reported as containing no Redis lookup variables.

- No Redis variables reported.
- Any NTP and syslog values in this file are unreferenced by the analyzed Redis module.

#### `data/environment/staging.yaml`

Migration note: Reported as containing no Redis lookup variables.

- No Redis variables reported.
- The reported syslog value is unreferenced by the analyzed Redis module.

### Variable Migration Summary

- **Common defaults**: `2` reported effective variables from `data/common.yaml`.
- **Manifest-only defaults**: `2` variables: `redis_port` and `maxmemory_policy`.
- **OS-specific variables**: Package names, paths, owners, groups, service names, PID paths, and daemonization behavior.
- **Environment-specific Redis variables**: `0` reported.
- **Host-specific Redis variables**: `0` reported.
- **Encrypted variables**: `0` confirmed. The password is currently reported as plain Hiera data and must be moved to Ansible Vault or an external secret store.
- **PuppetDB-derived values**: One unused query result, `$redis_nodes`.

### Complete Hiera-to-Ansible Mapping

`defaults/main.yml`:

```yaml
redis_cluster_redis_port: 6379
redis_cluster_maxmemory_mb: 256
redis_cluster_maxmemory_policy: allkeys-lru
```

`group_vars/all/vault.yml` or an external secret store:

```yaml
redis_cluster_redis_password: "test-redis-password"
```

Ansible must verify the Hiera values before treating them as authoritative. The password must be protected with Ansible Vault or an external lookup plugin, and tasks using it must set `no_log: true`.

### Cross-Level Overrides

- `profile_redis_cluster::redis_password`
  - Defined in the manifest and reported in common Hiera.
  - Reported effective value: `test-redis-password`.
  - Merge strategy: scalar priority lookup; common Hiera overrides the manifest default.
  - Verification required because the supplied validation summary does not include the actual Hiera lookup output.

- `profile_redis_cluster::maxmemory_mb`
  - Defined in the manifest and reported in common Hiera.
  - Reported effective value: `256`.
  - Merge strategy: scalar priority lookup; common Hiera overrides the manifest default.
  - Verification required against the actual Hiera data.

- `profile_redis_cluster::redis_port`
  - Defined only as a manifest default in the supplied plan.
  - Reported value: `6379`.
  - Verify that no higher-priority Hiera value exists.

- `profile_redis_cluster::maxmemory_policy`
  - Defined as the manifest default `allkeys-lru`.
  - Not passed to `class redis`.
  - Effective dependency/template value: `undef`.
  - The Ansible role must explicitly decide whether to preserve this behavior or add `maxmemory-policy allkeys-lru`.

### Merge Strategy Notes

- Scalar values use first-value or priority lookup; a higher-priority Hiera value overrides a lower-priority value.
- Hash values use shallow merge only where explicitly configured with `hash`.
- Recursive hash merging requires an explicit `deep` merge configuration.
- No Redis hash merge is reported in the supplied data.
- The dependency `custom_options` value is `{}` and contributes no additional settings.

## Custom Types and Providers

### Custom fact

- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
  - Reported as Linux-confined.
  - Reads `/etc/redis/conf.d/replica.conf`.
  - Reported behavior: returns `replica` when the file exists and contains `replicaof`; otherwise returns `primary`.
  - The implementation details require verification from the source file because they are not independently supported by the supplied validation summary.
  - Ansible equivalent: create `/etc/ansible/facts.d/redis_role.fact`, or use `stat` and `slurp` tasks.
  - No custom Ansible module is required.

### Dependency-defined resources

- `redis::instance`
  - Puppet defined type for additional Redis instances.
  - Not expanded because `instances` is `{}`.
- `redis::dnfmodule`
  - Defined dependency class for DNF module streams.
  - Not executed because `dnf_module_stream` is `undef`.
- `systemd::unit_file`
  - Used only when `manage_service_file` is `true`.
  - Not used for the default instance.
- `systemd::manage_dropin`
  - Used for the non-managed-service-file branch to apply `LimitNOFILE: 65536`.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` Forge module version `9.6.0`
- `puppet-redis` Forge module version `11.0.0`
- `puppetlabs-apt` Forge module version `9.4.0`

**System package dependencies**:

- Debian: `redis-server`
- RedHat: `redis`
- FreeBSD: `redis`
- Suse: `redis`
- Archlinux: `redis`

Repository packages are not configured because `manage_repo` is `false`.

**Service dependencies**:

- `Class['::profile::base::base'] -> Class['::profile::cache::redis']`
- `Class['redis::preinstall'] -> Class['redis::install']`
- `Class['redis::install'] -> Class['redis::config']`
- `Class['redis::config'] ~> Class['redis::service']`
- The original Puppet-managed configuration file triggers the copy to the active configuration file.
- No additional instance service dependency exists.

## Puppet Facts Used

- `facts['kernel']`
  - Determines the conditional containing `exec[None]` in the role.
- `fact('environment')`
  - Referenced by the Redis profile context.
- `facts['os']['name']`
  - Selects Ubuntu-specific repository behavior and OS-specific parameter defaults.
- `facts['os']['family']`
  - Selects package names, paths, service names, and configuration behavior for Debian, RedHat, FreeBSD, Suse, and Archlinux.
  - Determines whether `/etc/default/redis-server` is managed.
  - Validates DNF module behavior.
- `facts['os']['release']['major']`
  - Selects RedHat 9+ versus pre-9 configuration paths.
- `redis_role`
  - Custom fact derived from `/etc/redis/conf.d/replica.conf`.
  - Defined by the custom fact component but not shown as consumed by the supplied execution tree.

## Template Conversion Notes

### `redis/redis.conf.epp`

- Render count: `1`.
- Destination:
  - Debian and RedHat 9+: `/etc/redis/redis.conf.puppet`, copied to `/etc/redis/redis.conf`.
  - RedHat before version 9: `/etc/redis.conf.puppet`, copied to `/etc/redis.conf`.
- No Deferred template parameter is supplied; the normal EPP rendering branch executes.
- The template receives the resolved Redis options from `redis::instance 'default'`.
- Bind values render as `0.0.0.0`.
- Relative `log_file: redis.log` resolves under `/var/log/redis`.
- `requirepass` renders the configured password.
- `maxmemory` renders as `256mb`.
- `appendonly yes` and `appendfsync everysec` are rendered.
- `maxmemory-policy` is not rendered because the effective dependency value is `undef`.
- TLS, replication, Redis Cluster, ACL, module, and advanced I/O settings are unset or disabled.
- `custom_options` is empty.
- Full template contents and exact conditional logic must be verified from the physical template before implementation.

### `redis/service_templates/redis.service.epp`

- Render count: `0`.
- The template is skipped because `manage_service_file` is `false` for the default instance.
- If future additional instances enable managed service files, the template is expected to receive:
  - `bin_path`: `/usr/bin`
  - `instance_title`: instance name
  - `port`: instance port
  - `redis_file_name`: active configuration path
  - `service_name`: instance service name
  - `service_user`: `redis`
  - `service_timeout_start`: `undef`
  - `service_timeout_stop`: `undef`
  - `ulimit`: `65536`
  - `ulimit_managed`: `true`
- The reported count of five logic blocks requires verification from the physical template.

## PuppetDB Dependencies

**Context**: PuppetDB is used for a class-resource query, but the returned data does not affect the analyzed resource graph.

- **PuppetDB query**
  - Exact query: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
  - Location: `site-modules/profile_redis_cluster/manifests/init.pp`
  - Returned data: certnames whose catalogs contain `Profile_redis_cluster`.
  - Result variable: `$redis_nodes`.
  - Usage: assigned but not consumed by any resource.
  - Migration note: no Ansible equivalent is required for current behavior. If Redis peer discovery is later required, use Ansible inventory groups or explicit host variables instead of a runtime PuppetDB query.

- **Exported resources**
  - None.

- **Resource collectors**
  - None.

- **Host identity data**
  - No per-host PuppetDB identity data is consumed by the Redis resources.

## Credentials and Secret Handling

- **Redis client authentication password**
  - Profile variable: `profile_redis_cluster::redis_password`
  - Dependency parameter: `$redis_password`
  - Instance parameter: `redis::instance::requirepass`
  - Effective reported value: `test-redis-password`
  - Current source: plain Hiera data in `data/common.yaml`
  - Migration requirement: move to Ansible Vault or an external secret provider.

- **Redis replication/master authentication**
  - Dependency parameter: `$redis::masterauth`
  - Instance parameter: `redis::instance::masterauth`
  - Current value: `undef`

- **Redis Sentinel authentication**
  - Parameters: `$redis::sentinel::auth_pass` and `redis::sentinel::auth_pass`
  - Current status: not used in this execution tree.

- **TLS private key**
  - Parameters: `$redis::tls_key_file`, `redis::instance::tls_key_file`, and `redis::sentinel::tls_key_file`
  - Current value: `undef`

No eyaml values, external secret-provider calls, certificate source files, or embedded credentials in `exec` commands are confirmed in the supplied plan.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/redis_cluster.pp`
- `site-modules/profile/manifests/cache/redis.pp`
- `site-modules/profile_redis_cluster/manifests/init.pp`
- `site-modules/profile_redis_cluster/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`
- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- `redis/redis.conf.epp`
- `redis/service_templates/redis.service.epp`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`

**Configuration paths to verify for the `default` instance**:

- Debian:
  - `/etc/redis/redis.conf.puppet`
  - `/etc/redis/redis.conf`
  - `/etc/default/redis-server`
  - `/var/log/redis`
  - `/var/lib/redis`
- RedHat 9 or later:
  - `/etc/redis/redis.conf.puppet`
  - `/etc/redis/redis.conf`
  - `/var/log/redis`
  - `/var/lib/redis`
- RedHat before version 9:
  - `/etc/redis.conf.puppet`
  - `/etc/redis.conf`
  - `/var/log/redis`
  - `/var/lib/redis`

**Service endpoints to check for the `default` instance**:

- Debian service: `redis-server`
- RedHat, FreeBSD, Suse, and Archlinux service: `redis`
- TCP listener: `0.0.0.0:6379`
- Unix socket: `/var/run/redis/redis.sock`

**Templates rendered**:

- `redis/redis.conf.epp`: `1` render for `redis::instance 'default'`
- `redis/service_templates/redis.service.epp`: `0` renders

## Pre-flight checks

```bash
# Confirm the target platform and release.
test "$(uname -s)" = "Linux"
. /etc/os-release
printf 'OS family: %s\nOS release: %s\n' "$ID" "$VERSION_ID"

# Confirm the package repository contains the platform package.
# Debian:
apt-cache policy redis-server
# RedHat-compatible systems:
dnf info redis

# Confirm the default instance directories and ownership.
stat -c '%U:%G %a %n' /var/lib/redis /var/log/redis

# Confirm the default instance configuration paths.
# Debian and RedHat 9+:
test -f /etc/redis/redis.conf.puppet
test -f /etc/redis/redis.conf
# RedHat before version 9:
test -f /etc/redis.conf.puppet
test -f /etc/redis.conf

# Debian-only configuration.
test ! -e /etc/default/redis-server || stat /etc/default/redis-server

# Confirm the password is supplied through Ansible Vault or an external secret store.
# Do not print the secret value or expose it in task output.

# Validate the rendered default-instance configuration without exposing credentials.
redis-server --test-memory 2 >/dev/null 2>&1 || true
# Use the platform-supported Redis configuration validation command where available.

# Check the default instance service state on Debian.
systemctl is-enabled redis-server
systemctl is-active redis-server

# Check the default instance service state on RedHat and other supported systems.
systemctl is-enabled redis
systemctl is-active redis

# Check the default instance TCP listener.
ss -ltnp | grep ':6379'

# Check the default instance Unix socket.
test -S /var/run/redis/redis.sock

# Authenticate without logging the password.
# Supply the password through a protected environment or interactive mechanism.
redis-cli -h 127.0.0.1 -p 6379 ping

# Verify persistence settings for the default instance.
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET appendonly
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET appendfsync

# Verify memory settings for the default instance.
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET maxmemory
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET maxmemory-policy

# Confirm the intended migration behavior for maxmemory-policy:
# preserve the Puppet result of unset, or intentionally add allkeys-lru.
```