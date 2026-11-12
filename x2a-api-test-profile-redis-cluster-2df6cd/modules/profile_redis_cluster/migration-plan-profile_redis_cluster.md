---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: This module deploys one Redis instance named `default` through `role::redis_cluster`, `profile::cache::redis`, and `profile_redis_cluster`. It installs the platform Redis package, creates configuration, log, and data directories, renders Redis configuration with authentication, AOF persistence, a 256 MB memory limit, and binding to all interfaces, then enables and starts the Redis service. Redis Cluster mode and additional instances are disabled. Effective Hiera values are `redis_password=test-redis-password` and `maxmemory_mb=256`; the profile’s `maxmemory_policy=allkeys-lru` default is not passed to the dependency class and therefore resolves to `undef`. The plan is scoped to the listed execution-tree files and source-level details; the broader analysis reported 86 files but did not provide an inventory for the remaining files.

## Service Type and Instances

**Service Type**: Redis in-memory database/cache server

**Configured Instances**:

- **default**: The single implicit Redis instance managed by the dependency module.
  - Configuration source on Debian/Ubuntu and Red Hat 9+: `/etc/redis/redis.conf.puppet`
  - Active configuration on Debian/Ubuntu and Red Hat 9+: `/etc/redis/redis.conf`
  - Configuration source on Red Hat before version 9: `/etc/redis.conf.puppet`
  - Active configuration on Red Hat before version 9: `/etc/redis.conf`
  - Package on Debian-family systems: `redis-server`
  - Package on Red Hat-family systems: `redis`
  - Service on Debian-family systems: `redis-server`
  - Service on Red Hat-family systems: `redis`
  - Port: `6379`
  - Bind address: `0.0.0.0`
  - Authentication: `test-redis-password`
  - Maximum memory: `256mb`
  - Maxmemory policy: `undef`; the profile default `allkeys-lru` is not passed to `redis`
  - AOF: enabled
  - AOF fsync: `everysec`
  - Redis Cluster mode: disabled
  - Unix socket: `/var/run/redis/redis.sock`
  - Data directory: `/var/lib/redis`
  - Log directory: `/var/log/redis`

## File Structure

The supplied plan lists 13 manifests, one custom fact, and two dependency templates. The source analysis reported 86 files overall, but no inventory was provided for the remaining files; this migration plan therefore preserves and scopes the file listing below.

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
    ├── lib/
    │   └── facter/
    │       └── redis_role.rb
    └── migration-dependencies/
        └── redis/
            ├── manifests/
            │   ├── init.pp
            │   ├── params.pp
            │   ├── preinstall.pp
            │   ├── install.pp
            │   ├── dnfmodule.pp
            │   ├── config.pp
            │   ├── instance.pp
            │   ├── ulimit.pp
            │   └── service.pp
            └── templates/
                ├── redis/
                │   └── redis.conf.epp
                └── redis/
                    └── service_templates/
                        └── redis.service.epp
```

The dependency template source files are supplied by the `puppet-redis` module and are not present in the provided module directory listing:

- `redis/redis.conf.epp`
- `redis/service_templates/redis.service.epp`

## Module Explanation

The module performs operations in the following order.

1. **`role::redis_cluster`** (`site-modules/role/manifests/redis_cluster.pp`)
   - Evaluates `$facts['kernel'].downcase == 'linux'`.
   - On Linux, sets the default `Exec` search path to `/usr/bin:/bin:/usr/sbin:/sbin`.
   - The analysis represents this default declaration as `exec[None]`; it is not a command-executing `exec` resource declared directly by the role.
   - Includes `::profile::base::base`; the implementation is outside the analyzed execution tree.
   - Contains `::profile::cache::redis`.
   - Establishes `Class['::profile::base::base'] -> Class['::profile::cache::redis']`.

2. **`profile::cache::redis`** (`site-modules/profile/manifests/cache/redis.pp`)
   - Consults `fact('environment')`.
   - No environment-specific Redis values are present in the supplied production or staging data.
   - Includes `profile_redis_cluster`.

3. **`profile_redis_cluster`** (`site-modules/profile_redis_cluster/manifests/init.pp`)
   - Resolves local and Hiera parameters:
     - `redis_port`: `6379`
     - `redis_password`: `test-redis-password`
     - `maxmemory_mb`: `256`
     - `maxmemory_policy`: `allkeys-lru` as a profile default, but not passed to `redis`
   - Contains `profile_redis_cluster::install`.

4. **`profile_redis_cluster::install`** (`site-modules/profile_redis_cluster/manifests/install.pp`)
   - Declares the dependency class `redis`.
   - Passes:
     - `bind`: `0.0.0.0`
     - `port`: `6379`
     - `requirepass`: `test-redis-password`
     - `maxmemory`: `256mb`
     - `appendonly`: `true`
     - `appendfsync`: `everysec`
     - `manage_package`: `true`
   - Does not pass `maxmemory_policy`; the dependency class therefore receives `undef`.

5. **`redis`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`)
   - Inherits `redis::params`.
   - Contains the following classes in order:
     - `redis::preinstall`
     - `redis::install`
     - `redis::config`
     - `redis::service`
   - Effective common parameters:
     - `manage_repo`: `false`
     - `manage_package`: `true`
     - `package_ensure`: `installed`
     - `appendonly`: `true`
     - `appendfsync`: `everysec`
     - `bind`: `0.0.0.0`
     - `port`: `6379`
     - `requirepass`: `test-redis-password`
     - `maxmemory`: `256mb`
     - `maxmemory_policy`: `undef`
     - `default_install`: `true`
     - `notify_service`: `true`
     - `service_manage`: `true`
     - `service_enable`: `true`
     - `service_ensure`: `running`
     - `ulimit_managed`: `true`
     - `managed_by_cluster_manager`: `false`
     - `manage_service_file`: `false`
     - `instances`: `{}`
   - The effective OS-specific parameters are:
     - Debian:
       - Package: `redis-server`
       - Service: `redis-server`
       - Configuration directory: `/etc/redis`
       - Configuration file: `/etc/redis/redis.conf`
       - Puppet-rendered file: `/etc/redis/redis.conf.puppet`
       - Configuration owner: `redis`
       - Configuration group: `redis` on Ubuntu, `root` on other Debian-family systems
       - Configuration directory mode: `0755`
       - Log directory: `/var/log/redis`, mode `0755`
       - Work directory: `/var/lib/redis`
       - PID file: `/var/run/redis/redis-server.pid`
       - Binary directory: `/usr/bin`
       - Daemonize: `true`
     - Red Hat 9 or later:
       - Package: `redis`
       - Service: `redis`
       - Configuration directory: `/etc/redis`
       - Configuration file: `/etc/redis/redis.conf`
       - Puppet-rendered file: `/etc/redis/redis.conf.puppet`
       - Configuration owner: `redis`
       - Configuration group: `root`
       - Configuration directory mode: `0755`
       - Log directory: `/var/log/redis`, mode `0750`
       - Work directory: `/var/lib/redis`
       - PID file: `/var/run/redis_6379.pid`
       - Binary directory: `/usr/bin`
       - Daemonize: `false`
     - Red Hat before version 9:
       - Package: `redis`
       - Service: `redis`
       - Configuration directory: `/etc/redis`
       - Configuration file: `/etc/redis.conf`
       - Puppet-rendered file: `/etc/redis.conf.puppet`
       - Configuration owner: `redis`
       - Configuration group: `root`
       - Configuration directory mode: `0755`
       - Log directory: `/var/log/redis`, mode `0750`
       - Work directory: `/var/lib/redis`
       - PID file: `/var/run/redis_6379.pid`
       - Binary directory: `/usr/bin`
       - Daemonize: `false`

6. **`redis::preinstall`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`)
   - Skips repository configuration because `manage_repo == false`.
   - Does not create `apt::ppa` or `apt::source` resources.
   - Skips both the Ubuntu PPA and Debian Redis APT repository branches.

7. **`redis::install`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`)
   - Installs package `redis-server` on Debian-family systems with `ensure => installed`.
   - Installs package `redis` on Red Hat-family systems with `ensure => installed`.
   - Does not create a `fail` resource because `dnf_module_stream == undef`.
   - Does not include `redis::dnfmodule`.
   - Runs after `redis::preinstall`.

8. **`redis::config`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`)
   - Uses default configuration resource attributes:
     - Owner: platform-specific Redis configuration owner
     - Group: platform-specific Redis configuration group
     - Mode: `0640`
   - Creates `/etc/redis` as a directory with mode `0755`.
   - Creates `/var/log/redis` owned by `redis:redis`, with mode `0755` on Debian and `0750` on Red Hat.
   - Creates `/var/lib/redis` owned by `redis:redis`, with mode `0750`.
   - Because `default_install == true`, declares `redis::instance 'default'`.
   - Because `ulimit_managed == true`, contains `redis::ulimit`.
   - On Debian, creates `/etc/default/redis-server` as a file with the platform configuration owner, group, and mode `0640`.
   - On non-Debian systems, does not create `/etc/default/redis-server`.

9. **`redis::instance 'default'`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`)
   - Evaluates `$instances.each |$key, $values|`.
   - The `instances` hash is empty, so the loop runs zero times and creates no additional named instances.
   - The implicit instance name is exactly `default`.
   - Overrides:
     - `pid_file`: platform-specific PID path
     - `log_file`: `redis.log`, rendered as `/var/log/redis/redis.log`
     - `unixsocket`: `/var/run/redis/redis.sock`
     - `workdir`: `/var/lib/redis`
     - `daemonize`: platform-specific value
     - `service_name`: platform-specific service name
     - `manage_service_file`: `false`
     - `acls`: `[]`
   - Does not create an additional log directory or work directory.
   - Does not create a `systemd::unit_file`.
   - Does not render a Redis-specific systemd service unit.
   - Does not create a systemd drop-in because `manage_service_file` is false.
   - Does not use the Deferred inline-EPP branch because no supplied values are `Deferred`.
   - Renders `redis/redis.conf.epp` once.
   - Copies the Puppet-rendered configuration to the active configuration with a refresh-only `exec`:
     - Debian and Red Hat 9+: `cp -p /etc/redis/redis.conf.puppet /etc/redis/redis.conf`
     - Red Hat before 9: `cp -p /etc/redis.conf.puppet /etc/redis.conf`
   - Uses `/usr/bin:/bin` as the copy command path.
   - Subscribes the copy command to its source configuration file.

10. **`redis::ulimit`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`)
    - Does not create `/etc/security/limits.d/redis.conf` because `managed_by_cluster_manager == false`.
    - Ensures `/etc/systemd/system/redis-server.service.d/limit.conf` is absent on Debian.
    - Ensures `/etc/systemd/system/redis.service.d/limit.conf` is absent on Red Hat.
    - Removes the old managed service drop-in and creates no replacement `LimitNOFILE` drop-in.

11. **`redis::service`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`)
    - Manages `service 'redis-server'` on Debian-family systems:
      - `ensure`: `running`
      - `enable`: `true`
    - Manages `service 'redis'` on Red Hat-family systems:
      - `ensure`: `running`
      - `enable`: `true`
    - Service management is enabled because `service_manage == true`.

## Variables

**Variable Flow Summary**: 2 Hiera variables across 1 effective Hiera data level, plus 2 profile-level defaults and 2 profile defaults overridden by Hiera. Production and staging contain no Redis-specific overrides.

### Variable Definitions

#### `data/common.yaml` (defaults) → Migration note: Base Redis values for all nodes

- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

#### `data/environment/production.yaml` → Migration note: Production-level data; no Redis overrides

- No Redis variables.
- Contains unrelated NTP and syslog settings.

#### `data/environment/staging.yaml` → Migration note: Staging-level data; no Redis overrides

- No Redis variables.
- Contains an unrelated syslog setting.

#### Profile class defaults → Migration note: Local fallback values used when Hiera does not provide a value

- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string)
- `profile_redis_cluster::redis_password`: `CHANGEME` (type: string; overridden by Hiera)
- `profile_redis_cluster::maxmemory_mb`: `2048` (type: integer; overridden by Hiera)

#### Effective dependency-class values → Migration note: Values passed to the Redis dependency

- `redis::bind`: `0.0.0.0` (type: string)
- `redis::port`: `6379` (type: integer)
- `redis::requirepass`: `test-redis-password` (type: string)
- `redis::maxmemory`: `256mb` (type: string)
- `redis::maxmemory_policy`: `undef`
- `redis::appendonly`: `true` (type: boolean)
- `redis::appendfsync`: `everysec` (type: string)
- `redis::manage_package`: `true` (type: boolean)

### Variable Migration Summary

- **Common defaults**: 2 Redis variables from `data/common.yaml`
- **OS-specific variables**: 0 Hiera variables; OS-specific values come from `redis::params`
- **Environment-specific variables**: 0 Redis variables
- **Host-specific variables**: 0 Redis variables
- **Encrypted variables**: 1 sensitive value, `profile_redis_cluster::redis_password`

Recommended Ansible mapping:

```yaml
redis_cluster_redis_port: 6379
redis_cluster_maxmemory_mb: 256
redis_cluster_maxmemory_policy: allkeys-lru
vault_redis_cluster_redis_password: "test-redis-password"
```

Store `vault_redis_cluster_redis_password` in Ansible Vault or an external secret manager. Use `no_log: true` for tasks that consume or render the password.

### Cross-Level Overrides

- `profile_redis_cluster::redis_password`: defined at the profile default and `data/common.yaml`; Hiera value wins using first-value precedence.
- `profile_redis_cluster::maxmemory_mb`: defined at the profile default and `data/common.yaml`; Hiera value wins using first-value precedence.
- `profile_redis_cluster::redis_port`: defined only as a profile default.
- `profile_redis_cluster::maxmemory_policy`: defined only as a profile default and is not passed to `redis`.
- No production or staging Redis overrides exist.
- No `lookup_options` block or explicit merge strategy is defined.

### Merge Strategy Notes

- Variables using `hash` merge combine hash values from multiple levels using a shallow merge.
- Variables using `deep` merge recursively merge nested hash values.
- Variables using `first` precedence, the default behavior, use the first value found and do not merge.
- The Redis variables in this plan use first-value precedence; no Redis hash or deep merge is configured.

## Custom Types and Providers

### Custom fact: `redis_role`

- File: `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- Scope: Linux.
- Checks `/etc/redis/conf.d/replica.conf`.
- Returns `replica` when the file exists and contains the literal string `replicaof`.
- Returns `primary` otherwise.
- The fact is not consumed by resources in the shown execution tree.
- Preserve it if other migrated roles use it.
- Ansible equivalent:
  - Implement `/etc/ansible/facts.d/redis_role.fact`, or
  - Use `stat` with `slurp`/`grep` and set a registered fact.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` Forge module version `9.6.0`
- `puppet-redis` Forge module version `11.0.0`
- `puppetlabs-apt` Forge module version `9.4.0`

**System package dependencies**:

- Debian-family systems: `redis-server`
- Red Hat-family systems: `redis`
- No repository package is managed because `manage_repo == false`.
- No DNF module is managed because `dnf_module_stream == undef`.

**Service dependencies**:

- `::profile::base::base` precedes `::profile::cache::redis`.
- `redis::preinstall` precedes `redis::install`.
- `redis::install` precedes `redis::config`.
- `redis::config` notifies `redis::service`.
- Configuration copy commands run only after their source files change.

## Puppet Facts Used

- `$facts['kernel']`
  - Determines whether the Linux-specific `Exec` path default is applied.
- `fact('environment')`
  - Consulted by `profile::cache::redis`.
  - No Redis-specific production or staging override is present.
- `$facts['os']['name']`
  - Selects the Ubuntu PPA branch in `redis::preinstall`.
  - Distinguishes Ubuntu from other Debian-family systems for configuration group selection.
- `$facts['os']['family']`
  - Selects Debian, Red Hat, FreeBSD, Suse, Archlinux, or unsupported branches.
  - Controls package names, service names, paths, permissions, and Debian defaults-file handling.
  - Determines whether DNF module configuration is applicable.
- `$facts['os']['release']['major']`
  - Selects Red Hat 9+ versus pre-9 Redis configuration paths.
- Custom `redis_role`
  - Reads `/etc/redis/conf.d/replica.conf`.
  - Is not consumed by the shown execution tree.

## Template Conversion Notes

### `redis/redis.conf.epp`

- Render count: 1, for the implicit `default` instance.
- Destination on Debian and Red Hat 9+:
  - `/etc/redis/redis.conf.puppet`
  - Copied to `/etc/redis/redis.conf`
- Destination on Red Hat before version 9:
  - `/etc/redis.conf.puppet`
  - Copied to `/etc/redis.conf`
- Receives the resolved Redis parameters listed below:
  - `daemonize`: `true` on Debian, `false` on Red Hat
  - `pid_file`: `/var/run/redis/redis-server.pid` on Debian; `/var/run/redis_6379.pid` on Red Hat
  - `protected_mode`: `true`
  - `port`: `6379`
  - `tcp_backlog`: `511`
  - `bind_arr`: `['0.0.0.0']`
  - `unixsocket`: `/var/run/redis/redis.sock`
  - `unixsocketperm`: `0755`
  - `timeout`: `0`
  - `tcp_keepalive`: `0`
  - `log_level`: `notice`
  - `log_file`: `/var/log/redis/redis.log`
  - `syslog_enabled`: `false`
  - `syslog_facility`: `undef`
  - `databases`: `16`
  - `save_db_to_disk`: `true`
  - `save_db_to_disk_interval`: `{ '900': '1', '300': '10', '60': '10000' }`
  - `stop_writes_on_bgsave_error`: `true`
  - `rdbcompression`: `true`
  - `dbfilename`: `dump.rdb`
  - `workdir`: `/var/lib/redis`
  - `slaveof`: `undef`
  - `replicaof`: `undef`
  - `masterauth`: `undef`
  - `slave_serve_stale_data`: `true`
  - `slave_read_only`: `true`
  - `repl_announce_ip`: `undef`
  - `repl_announce_port`: `undef`
  - `repl_ping_slave_period`: `10`
  - `repl_timeout`: `60`
  - `repl_disable_tcp_nodelay`: `false`
  - `repl_backlog_size`: `1mb`
  - `repl_backlog_ttl`: `3600`
  - `slave_priority`: `100`
  - `min_slaves_to_write`: `0`
  - `min_slaves_max_lag`: `10`
  - `requirepass`: `test-redis-password`
  - `rename_commands`: `{}`
  - `maxclients`: `10000`
  - `maxmemory`: `256mb`
  - `maxmemory_policy`: `undef`
  - `maxmemory_samples`: `undef`
  - `appendonly`: `true`
  - `appendfilename`: `appendonly.aof`
  - `appendfsync`: `everysec`
  - `no_appendfsync_on_rewrite`: `false`
  - `auto_aof_rewrite_percentage`: `100`
  - `auto_aof_rewrite_min_size`: `64mb`
  - `aof_load_truncated`: `true`
  - `slowlog_log_slower_than`: `10000`
  - `slowlog_max_len`: `1024`
  - `latency_monitor_threshold`: `0`
  - `notify_keyspace_events`: `undef`
  - `hash_max_ziplist_entries`: `512`
  - `hash_max_ziplist_value`: `64`
  - `list_max_ziplist_entries`: `512`
  - `list_max_ziplist_value`: `64`
  - `set_max_intset_entries`: `512`
  - `zset_max_ziplist_entries`: `128`
  - `zset_max_ziplist_value`: `64`
  - `hll_sparse_max_bytes`: `3000`
  - `activerehashing`: `true`
  - `output_buffer_limit_slave`: `256mb 64mb 60`
  - `output_buffer_limit_pubsub`: `32mb 8mb 60`
  - `hz`: `10`
  - `aof_rewrite_incremental_fsync`: `true`
  - `cluster_enabled`: `false`
  - `cluster_config_file`: `nodes.conf`
  - `cluster_node_timeout`: `5000`
  - `cluster_slave_validity_factor`: `0`
  - `cluster_require_full_coverage`: `true`
  - `cluster_migration_barrier`: `1`
  - `extra_config_file`: `undef`
  - TLS parameters: unset except `tls_auth_clients=no`, `tls_replication=false`, `tls_cluster=false`, and `tls_prefer_server_ciphers=false`
  - `modules`: `[]`
  - `io_threads`: `undef`
  - `io_threads_do_reads`: `undef`
  - `cluster_allow_reads_when_down`: `undef`
  - `cluster_replica_no_failover`: `undef`
  - `dynamic_hz`: `undef`
  - `activedefrag`: `undef`
  - `active_defrag_ignore_bytes`: `100mb`
  - `active_defrag_threshold_lower`: `10`
  - `active_defrag_threshold_upper`: `100`
  - `active_defrag_cycle_min`: `1`
  - `active_defrag_cycle_max`: `100`
  - `active_defrag_max_scan_fields`: `1000`
  - `jemalloc_bg_thread`: `undef`
  - `rdb_save_incremental_fsync`: `undef`
  - `acls`: `[]`
  - `custom_options`: `{}`
- No Deferred values are present.
- The password is rendered into the configuration as `requirepass`; protect the rendered and copied files and do not expose their contents in logs.

### `redis/service_templates/redis.service.epp`

- Render count: 0.
- The `manage_service_file == false` branch prevents the service template from rendering.
- Ansible should use the distribution-provided Redis systemd unit unless migration requirements change this setting.

## PuppetDB Dependencies

No PuppetDB dependency is included in the cleaned execution-tree plan.

The supplied validation notes reported claims about a query of `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }` assigned to `$redis_nodes`, but the structured execution tree contains no PuppetDB query node, `puppetdb_query()` call, or `$redis_nodes` assignment. No exported resources, resource collectors, or PuppetDB infrastructure queries are therefore migrated.

## Credentials and Sensitive Data

- `profile_redis_cluster::redis_password`
  - Effective value: `test-redis-password`
  - Is rendered as Redis `requirepass`.
  - Has an insecure profile fallback of `CHANGEME`.
  - Must be stored in Ansible Vault or an external secret manager.
- Redis dependency parameter `requirepass`
  - Accepts plain strings, `Sensitive[String]`, or `Deferred` values.
  - Is populated with the effective password.
- Redis dependency parameter `masterauth`
  - Is unset.
- TLS certificate and key parameters exist but are unset in this execution.
- Migration controls:
  - Store the password securely.
  - Use `no_log: true` for secret-consuming tasks.
  - Deploy configuration with restrictive ownership and mode.
  - Do not print rendered Redis configuration in debug output.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/redis_cluster.pp`
- `site-modules/profile/manifests/cache/redis.pp`
- `site-modules/profile_redis_cluster/manifests/init.pp`
- `site-modules/profile_redis_cluster/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/params.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`
- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- `/etc/redis` on Debian and Red Hat
- `/var/log/redis`
- `/var/lib/redis`
- `/etc/redis/redis.conf.puppet` on Debian and Red Hat 9+
- `/etc/redis/redis.conf` on Debian and Red Hat 9+
- `/etc/redis.conf.puppet` on Red Hat before version 9
- `/etc/redis.conf` on Red Hat before version 9
- `/etc/default/redis-server` on Debian-family systems
- `/etc/security/limits.d/redis.conf` should not be created by this module
- `/etc/systemd/system/redis-server.service.d/limit.conf` should be absent on Debian
- `/etc/systemd/system/redis.service.d/limit.conf` should be absent on Red Hat

**Service endpoints to check**:

- **default instance**:
  - TCP port `6379`
  - Unix socket `/var/run/redis/redis.sock`
  - Service `redis-server` on Debian-family systems
  - Service `redis` on Red Hat-family systems

**Templates rendered**:

- `redis/redis.conf.epp`: 1 render for `redis::instance 'default'`
- `redis/service_templates/redis.service.epp`: 0 renders because `manage_service_file == false`

## Pre-flight checks

```bash
# Confirm platform and package selection
cat /etc/os-release
uname -s
uname -m

# On Red Hat-family systems, confirm the major version
rpm -E '%{rhel}' 2>/dev/null || true

# Confirm the expected package is available
# Debian/Ubuntu:
apt-cache policy redis-server
# Red Hat:
dnf info redis

# Confirm service names
systemctl list-unit-files redis-server.service redis.service

# Confirm the default instance directories and permissions
stat -c '%U:%G %a %n' /var/lib/redis /var/log/redis

# Confirm configuration paths
test -f /etc/redis/redis.conf.puppet || test -f /etc/redis.conf.puppet
test -f /etc/redis/redis.conf || test -f /etc/redis.conf

# Validate the active Redis configuration where supported
redis-server --test-memory 2
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" ping

# Verify the default instance service
systemctl is-enabled redis-server 2>/dev/null || systemctl is-enabled redis
systemctl is-active redis-server 2>/dev/null || systemctl is-active redis

# Verify the default instance endpoint and authentication
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" ping
test -S /var/run/redis/redis.sock
redis-cli -s /var/run/redis/redis.sock -a "$REDIS_PASSWORD" ping

# Verify effective Redis settings
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET appendonly
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET appendfsync
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET maxmemory
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET cluster-enabled

# Verify obsolete ulimit drop-ins are absent
test ! -e /etc/systemd/system/redis-server.service.d/limit.conf
test ! -e /etc/systemd/system/redis.service.d/limit.conf

# Verify configuration changes trigger service refresh
systemctl status redis-server 2>/dev/null || systemctl status redis
```
