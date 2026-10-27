---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: This module provisions one default Redis server intended for a Redis Cluster deployment, although Redis Cluster mode is disabled. It installs the platform Redis package, configures Redis on all interfaces at TCP port `6379` with the Hiera-supplied password `test-redis-password`, enables AOF persistence with `everysec` fsync, sets a `256mb` memory limit, and manages the Redis service. The profile-level `allkeys-lru` policy is not passed to the embedded Redis class and therefore remains unset unless explicitly configured during migration. A PuppetDB query discovers `Profile_redis_cluster` classes but its result is unused.

## Service Type and Instances

**Service Type**: In-memory database/cache and Redis server node.

**Configured Instances**:

- **default**: Implicit primary Redis instance.
  - Location/Path: `/etc/redis/redis.conf` on Debian and RedHat 9+; `/etc/redis.conf` on older RedHat
  - Port/Socket: TCP `6379`; Unix socket `/var/run/redis/redis.sock`
  - Bind address: `0.0.0.0`
  - Client password: `test-redis-password` from Hiera; migrate through Ansible Vault or an external secret backend
  - Maximum memory: `256mb`
  - Eviction policy: Unset in the effective embedded Redis configuration; the profile default is `allkeys-lru` but is not passed to the dependency
  - Append-only persistence: Enabled
  - Append fsync: `everysec`
  - Package management: Enabled
  - Service management: Enabled and running
  - Service name: `redis-server` on Debian; `redis` on RedHat
  - Redis Cluster mode: Disabled
  - Configuration mode: `0640`
  - Log path: `/var/log/redis/redis.log`
  - Data path: `/var/lib/redis`
  - Source configuration: `/etc/redis/redis.conf.puppet` on Debian and RedHat 9+; `/etc/redis.conf.puppet` on older RedHat

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
site-modules/role/manifests/redis_cluster.pp
site-modules/profile/manifests/base/base.pp
site-modules/profile/manifests/cache/redis.pp
site-modules/profile_redis_cluster/manifests/init.pp
site-modules/profile_redis_cluster/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp

redis/service_templates/redis.service.epp
redis/redis.conf.epp

data/common.yaml
data/environment/production.yaml
data/environment/staging.yaml

site-modules/profile_redis_cluster/lib/facter/redis_role.rb
```

## Module Explanation

The module executes in the following order:

1. **`role::redis_cluster`** (`site-modules/role/manifests/redis_cluster.pp`):
   - Runs Linux-specific logic when `$facts['kernel'].downcase == 'linux'`.
   - Sets the default `Exec` path to `/usr/bin:/bin:/usr/sbin:/sbin`.
   - Declares no concrete `exec` resource.
   - Includes `::profile::base::base`.
   - Contains `::profile::cache::redis`.
   - Orders the base profile before the Redis profile:
     `Class['::profile::base::base'] -> Class['::profile::cache::redis']`.

2. **`profile::base::base`** (`site-modules/profile/manifests/base/base.pp`):
   - Uses defaults `manage_ntp: true`, `manage_syslog: true`, and `manage_utils: true`.
   - Includes external or unanalyzed class `base_utils` when utility management is enabled.
   - On Linux with NTP management enabled, installs `chrony` and manages `chronyd` as enabled and running.
   - On Linux with syslog management enabled, installs `rsyslog` and manages `rsyslog` as enabled and running.
   - Uses `$facts['kernel']`.
   - The supplied environment Hiera values for NTP and syslog are not looked up by the shown class parameters; manifest defaults remain effective unless control-repository data overrides them.

3. **`profile::cache::redis`** (`site-modules/profile/manifests/cache/redis.pp`):
   - Declares `class { 'profile_redis_cluster': }`.
   - Sets `environment_name` from `fact('environment')` by default.
   - Evaluates the environment fact but does not use it to alter Redis resources.

4. **`profile_redis_cluster`** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Resolves `redis_port: 6379`.
   - Resolves `redis_password: test-redis-password`.
   - Resolves `maxmemory_mb: 256`.
   - Resolves `maxmemory_policy: allkeys-lru`.
   - Queries PuppetDB with:
     `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`.
   - Stores the query result in `redis_nodes`; no later resource consumes it.
   - Contains `profile_redis_cluster::install`.

5. **`profile_redis_cluster::install`** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - Declares the embedded `redis` class with:
     - `bind: 0.0.0.0`
     - `port: 6379`
     - `requirepass: test-redis-password`
     - `maxmemory: 256mb`
     - `appendonly: true`
     - `appendfsync: everysec`
     - `manage_package: true`
   - Does not pass `maxmemory_policy`; migration should explicitly configure `maxmemory-policy: allkeys-lru` if that policy is intended.

6. **`redis`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Contains `redis::preinstall`.
   - Contains `redis::install`.
   - Contains `redis::config`.
   - Contains `redis::service`.
   - Uses `default_install: true`, `manage_repo: false`, `service_manage: true`, `service_ensure: running`, `service_enable: true`, `ulimit_managed: true`, `notify_service: true`, `managed_by_cluster_manager: false`, `manage_service_file: false`, and `cluster_enabled: false`.
   - Uses `config_file_mode: 0640`.
   - Leaves `dnf_module_stream`, TLS settings, replication settings, and additional instances unset.
   - Orders:
     `Class['redis::preinstall'] -> Class['redis::install'] -> Class['redis::config']`.
   - Configuration changes notify the service:
     `Class['redis::config'] ~> Class['redis::service']`.

7. **`redis::preinstall`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Does not manage repositories because `manage_repo: false`.
   - Does not execute the Ubuntu PPA or Debian Redis repository branches.
   - Does not create `apt` or `apt::source` resources.
   - Uses `$facts['os']['name']` and `$facts['os']['family']`.

8. **`redis::install`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Installs the Redis package because `manage_package: true`.
   - Installs `redis-server` on Debian.
   - Installs `redis` on RedHat, FreeBSD, Suse, and Archlinux.
   - Does not include `redis::dnfmodule` because `dnf_module_stream: undef`.
   - Ansible must only add a DNF module stream on RedHat systems if that option is introduced.

9. **`redis::config`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - Creates `/etc/redis` on Debian and RedHat with mode `0755`.
   - Creates `/var/log/redis` owned by `redis:redis`; mode is `0755` on Debian and `0750` on RedHat.
   - Creates `/var/lib/redis` owned by `redis:redis` with mode `0750`.
   - Uses configuration file mode `0640`.
   - On Debian, manages `/etc/default/redis-server`.
   - Creates the default instance because `default_install: true`.
   - Includes `redis::ulimit` because `ulimit_managed: true`.
   - Uses OS-specific package, service, PID, configuration, and ownership values:
     - Debian: package and service `redis-server`; PID `/var/run/redis/redis-server.pid`; configuration `/etc/redis/redis.conf`.
     - RedHat 9+: package and service `redis`; PID `/var/run/redis_6379.pid`; configuration `/etc/redis/redis.conf`.
     - RedHat before 9: package and service `redis`; configuration `/etc/redis.conf`.

10. **`redis::instance 'default'`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`):
    - This is the only expanded instance because `instances: {}`.
    - Uses TCP port `6379` and bind address `0.0.0.0`.
    - Uses Unix socket `/var/run/redis/redis.sock` with mode `0755`.
    - Uses `/var/lib/redis` as the work directory.
    - Uses `/var/log/redis/redis.log` as the log file.
    - Uses `daemonize: true` on Debian and `false` on RedHat.
    - Uses `protected_mode: true`, `tcp_backlog: 511`, `timeout: 0`, `tcp_keepalive: 0`, and `log_level: notice`.
    - Enables RDB persistence with default save intervals:
      - `900` seconds / `1` change
      - `300` seconds / `10` changes
      - `60` seconds / `10000` changes
    - Enables RDB compression and uses `dump.rdb`.
    - Sets `requirepass: test-redis-password`.
    - Sets `maxmemory: 256mb`.
    - Leaves `maxmemory_policy` unset.
    - Enables AOF with `appendfilename: appendonly.aof` and `appendfsync: everysec`.
    - Uses default replication, TLS, module, ACL, I/O-thread, and custom-option settings; no replication or TLS configuration is active.
    - Sets `cluster_enabled: false`.
    - Renders the source configuration file:
      - `/etc/redis/redis.conf.puppet` on Debian and RedHat 9+
      - `/etc/redis.conf.puppet` on older RedHat
    - Copies the source file to the active configuration:
      - `/etc/redis/redis.conf` on Debian and RedHat 9+
      - `/etc/redis.conf` on older RedHat
    - Uses `cp -p` through an `exec` with path `/usr/bin:/bin`, triggered only when the source file changes.
    - Does not create a systemd unit because `manage_service_file: false`.
    - Does not create separate log or work directories because the instance paths equal the class-level paths.

11. **`redis::ulimit`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`):
    - Does not create `/etc/security/limits.d/redis.conf` because `managed_by_cluster_manager: false`.
    - Removes the legacy systemd drop-in:
      - Debian: `/etc/systemd/system/redis-server.service.d/limit.conf`
      - RedHat: `/etc/systemd/system/redis.service.d/limit.conf`
    - The Ansible migration should preserve this removal for convergence.

12. **`redis::service`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
    - Manages the service because `service_manage: true`.
    - Ensures the Debian `redis-server` service is enabled and running.
    - Ensures the RedHat `redis` service is enabled and running.
    - Receives notifications from configuration changes.

13. **`$instances.each` loop** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
    - Iterates over an empty hash: `instances: {}`.
    - Iterations: none.
    - No additional named Redis instances are created.
    - The only instance is `redis::instance 'default'`, created by `default_install: true`.

## Variables

**Variable Flow Summary**: 4 Redis profile variables are effective: 2 from `data/common.yaml` and 2 manifest defaults. Environment files contain 4 additional values, but none are consumed by the supplied Redis execution path. The embedded Redis dependency supplies additional manifest defaults, with no hash or deep merges active.

### Variable Definitions

#### `data/common.yaml` (common defaults) → Migration note: Base Redis values for all nodes

- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string; sensitive plaintext secret)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

#### `profile_redis_cluster` manifest defaults → Migration note: Effective defaults when no Hiera override exists

- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string)

#### `data/environment/production.yaml` → Migration note: Production environment values; not referenced by the shown Redis profile path

- `ntp::servers`: `['0.pool.ntp.org', '1.pool.ntp.org']` (type: array)
- `syslog::server`: `127.0.0.1` (type: string)
- `syslog::facility`: `local0` (type: string)

#### `data/environment/staging.yaml` → Migration note: Staging environment value; not referenced by the shown Redis profile path

- `syslog::server`: `127.0.0.1` (type: string)

#### Embedded Redis dependency defaults → Migration note: Preserve as role defaults unless intentionally changed

- `redis::bind`: `0.0.0.0` (type: string)
- `redis::port`: `6379` (type: integer)
- `redis::requirepass`: `test-redis-password` (type: string; sensitive)
- `redis::maxmemory`: `256mb` (type: string)
- `redis::appendonly`: `true` (type: boolean)
- `redis::appendfsync`: `everysec` (type: string)
- `redis::manage_package`: `true` (type: boolean)
- `redis::default_install`: `true` (type: boolean)
- `redis::instances`: `{}` (type: hash)
- `redis::manage_repo`: `false` (type: boolean)
- `redis::dnf_module_stream`: `undef` (type: optional string)
- `redis::config_file_mode`: `0640` (type: string)
- `redis::service_manage`: `true` (type: boolean)
- `redis::service_ensure`: `running` (type: string)
- `redis::service_enable`: `true` (type: boolean)
- `redis::service_user`: `redis` (type: string)
- `redis::service_group`: `redis` (type: string)
- `redis::notify_service`: `true` (type: boolean)
- `redis::ulimit_managed`: `true` (type: boolean)
- `redis::managed_by_cluster_manager`: `false` (type: boolean)
- `redis::manage_service_file`: `false` (type: boolean)
- `redis::cluster_enabled`: `false` (type: boolean)
- TLS certificate, key, CA, and TLS port variables: `undef` (type: optional string)
- Replication variables: unset (type: optional values)
- `redis::maxmemory_policy`: `undef` in the effective dependency invocation (type: optional string)
- `redis::acls`: `[]` (type: array)
- `redis::custom_options`: `{}` (type: hash)

### Variable Migration Summary

- **Common defaults**: 2 Redis variables from `data/common.yaml`
- **Manifest defaults**: 2 Redis profile variables
- **OS-specific variables**: 0 supplied directly; package names, service names, and paths are selected from facts
- **Environment-specific variables**: 0 Redis variables; 4 unrelated NTP/syslog values
- **Host-specific variables**: 0 supplied
- **Encrypted variables**: 0
- **Secrets requiring secure migration**: 1 plaintext Redis password
- **External TLS assets**: 0 active; dependency TLS paths are unset
- **Named Redis instances**: 0; only the implicit `default` instance exists

### Hiera → Ansible Mapping

Use role defaults for non-secret values:

```yaml
redis_cluster_redis_port: 6379
redis_cluster_maxmemory_mb: 256
redis_cluster_maxmemory_policy: allkeys-lru
redis_cluster_bind: "0.0.0.0"
redis_cluster_appendonly: true
redis_cluster_appendfsync: everysec
redis_cluster_manage_package: true
redis_cluster_instances: []
```

Store the password in Ansible Vault or an external secret backend:

```yaml
redis_cluster_redis_password: "{{ vault_redis_cluster_redis_password }}"
```

The Ansible role should explicitly render `maxmemory-policy: allkeys-lru` if the profile default is intended to become effective.

### Cross-Level Overrides

- `profile_redis_cluster::redis_password`: common Hiera only; first value found; effective value `test-redis-password`
- `profile_redis_cluster::maxmemory_mb`: common Hiera only; first value found; effective value `256`
- `profile_redis_cluster::redis_port`: manifest default only; effective value `6379`
- `profile_redis_cluster::maxmemory_policy`: manifest default only; effective value `allkeys-lru`

### Merge Strategy Notes

- Variables using `hash` merge: none in the supplied Redis profile data.
- Variables using `deep` merge: none in the supplied Redis profile data.
- Variables using `first` merge: profile base Boolean parameters and all effective Redis scalar values.
- `instances` is an empty hash and produces no additional instance resources.

## Custom Types and Providers

### Custom fact: `redis_role`

- File: `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- Scope: Linux only
- Checks `/etc/redis/conf.d/replica.conf`.
- Returns `replica` when the file exists and contains the substring `replicaof`.
- Returns `primary` otherwise.
- No supplied manifest references this fact directly.

Ansible can reproduce it with `stat`, `slurp`, and `set_fact`, or with a local fact at `/etc/ansible/facts.d/redis_role.fact`.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` version `9.6.0`
- `puppet-redis` version `11.0.0`
- `puppetlabs-apt` version `9.4.0`

The Redis and APT dependency source is embedded under:

- `site-modules/profile_redis_cluster/migration-dependencies/`

**System package dependencies**:

- `chrony` when Linux and NTP management are enabled
- `rsyslog` when Linux and syslog management are enabled
- `redis-server` on Debian
- `redis` on RedHat, FreeBSD, Suse, and Archlinux
- No APT repository because `manage_repo: false`
- No DNF module stream because `dnf_module_stream: undef`

**Service dependencies**:

- `Class['::profile::base::base'] -> Class['::profile::cache::redis']`
- `Class['redis::preinstall'] -> Class['redis::install'] -> Class['redis::config']`
- `Class['redis::config'] ~> Class['redis::service']`
- Legacy Redis systemd limit drop-ins must be removed during convergence

## Puppet Facts Used

- `$facts['kernel']`: Selects Linux-specific execution behavior and controls `chrony` and `rsyslog` management.
- `fact('environment')`: Supplies `environment_name` to `profile::cache::redis`; does not alter Redis resources.
- `$facts['os']['name']`: Selects Ubuntu-specific repository logic.
- `$facts['os']['family']`: Selects package names, service names, configuration paths, and Debian default-file management.
- `$facts['os']['release']['major']`: Selects RedHat 9+ versus pre-9 configuration paths.
- Custom fact `redis_role`: Detects `replica` or `primary` from `/etc/redis/conf.d/replica.conf`; not consumed by the supplied manifests.

## Template Conversion Notes

### `redis/redis.conf.epp`

- Render count: 1, for `redis::instance 'default'`.
- Renders network, socket, process, logging, persistence, AOF, memory, replication, security, performance, cluster, TLS, module, I/O, and custom-option settings.
- Effective values include `bind_arr: ['0.0.0.0']`, `port: 6379`, `protected_mode: true`, `unixsocket: /var/run/redis/redis.sock`, `pid_file` platform value, `requirepass: test-redis-password`, `maxmemory: 256mb`, `appendonly: true`, `appendfsync: everysec`, and `cluster_enabled: false`.
- Preserve handling for unset values, booleans, arrays, ACLs, save intervals, TLS options, and custom options.
- The template is rendered to the Puppet source configuration and copied to the active configuration path.

### `redis/service_templates/redis.service.epp`

- Render count: 0 in the effective configuration because `manage_service_file: false`.
- Potential render count: one per explicitly managed named instance if service-file management is enabled.
- Receives the service binary path, instance title, port, active configuration path, service name, service user, timeout values, `ulimit: 65536`, and `ulimit_managed: true`.
- Replace with a systemd unit template only when named instances or explicitly managed service files are required.

### Deferred rendering

- The defined type supports Puppet `Deferred` template parameters through escaped EPP and `inline_epp`.
- No Deferred parameter is supplied in the effective execution path.
- No Ansible deferred-rendering equivalent is required.

## PuppetDB Dependencies

**Context**: PuppetDB is used only for an unused node-discovery query.

- **PuppetDB query**:
  - Exact query: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
  - Returned data: Certnames containing the `Profile_redis_cluster` class.
  - Usage: Assigned to `redis_nodes` in `profile_redis_cluster`.
  - Effect: None; no subsequent resource consumes `redis_nodes`.
  - Migration: Omit the query unless Redis peer discovery is required. If required, replace it with Ansible inventory membership such as `groups['redis_cluster']`, host variables, or service discovery.

- **Exported resources (`@@`)**: None.
- **Resource collectors (`<<| |>>`)**: None.
- **Virtual resources (`@`)**: None.
- **Host identity data**: No PuppetDB host identity data is used for classification or configuration.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/redis_cluster.pp`
- `site-modules/profile/manifests/base/base.pp`
- `site-modules/profile/manifests/cache/redis.pp`
- `site-modules/profile_redis_cluster/manifests/init.pp`
- `site-modules/profile_redis_cluster/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`
- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`
- `redis/redis.conf.epp`
- `redis/service_templates/redis.service.epp`

**Service endpoints to check**:

- Instance `default` TCP endpoint: `0.0.0.0:6379`
- Instance `default` Unix socket: `/var/run/redis/redis.sock`
- Instance `default` authentication using the Ansible Vault password
- Instance `default` active configuration path for the target OS
- Redis cluster bus: not configured because `cluster_enabled: false`

**Templates rendered**:

- `redis/redis.conf.epp`: 1 render for `redis::instance 'default'`
- `redis/service_templates/redis.service.epp`: 0 renders

## Pre-flight checks

```bash
# Confirm supported operating system and identify package/service names
. /etc/os-release
uname -s
systemctl list-unit-files | grep -E '^(redis-server|redis)\.service'

# Confirm the default instance package
# Debian:
dpkg-query -W -f='${Status}\n' redis-server
# RedHat:
rpm -q redis

# Confirm the default instance directories and ownership
stat -c '%A %U:%G %n' /var/log/redis /var/lib/redis
test -d /var/log/redis
test -d /var/lib/redis

# Confirm the default instance configuration path and mode
if [ -f /etc/redis/redis.conf ]; then
  stat -c '%A %U:%G %n' /etc/redis/redis.conf
elif [ -f /etc/redis.conf ]; then
  stat -c '%A %U:%G %n' /etc/redis.conf
else
  echo "Redis configuration file not found" >&2
  exit 1
fi

# Confirm the source configuration and remove or preserve it deliberately
test -f /etc/redis/redis.conf.puppet || test -f /etc/redis.conf.puppet

# Confirm the legacy systemd limit drop-ins are absent
test ! -e /etc/systemd/system/redis-server.service.d/limit.conf
test ! -e /etc/systemd/system/redis.service.d/limit.conf

# Validate Redis configuration where supported
redis-server --test-memory 2

# Check the default instance service
systemctl is-enabled redis-server || systemctl is-enabled redis
systemctl is-active redis-server || systemctl is-active redis

# Check the default instance TCP endpoint and authentication
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" PING

# Check the default instance Unix socket where supported
redis-cli -s /var/run/redis/redis.sock -a "$REDIS_PASSWORD" PING

# Check effective default instance settings
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET bind
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET port
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET appendonly
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET appendfsync
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET maxmemory
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET maxmemory-policy
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET cluster-enabled

# If Redis Cluster behavior is required, explicitly verify inventory-based peer
# membership, cluster-enabled, cluster configuration, and cluster bus settings.
# None are enabled by the supplied Puppet configuration.
```