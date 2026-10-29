---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: This module configures one Redis instance on a Redis cluster node through `role::redis_cluster` → `profile::cache::redis` → `profile_redis_cluster` → `redis`. It installs the Debian Redis package `redis-server`, listens on `0.0.0.0:6379`, enables AOF persistence with `everysec` fsync, sets `maxmemory` to `256mb`, requires the Hiera-provided password `test-redis-password`, manages Redis directories and configuration, and enables the `redis-server` service. The profile performs one PuppetDB query for `Profile_redis_cluster` class resources, but the result is unused. The Redis password must be stored in Ansible Vault during migration. The profile’s `allkeys-lru` `maxmemory_policy` parameter is not forwarded to the dependency module and therefore is not currently applied.

## Service Type and Instances

**Service Type**: Redis in-memory database/cache service

**Configured Instances**:

- **default Redis instance**: Main and only Redis instance created by the implicit `default_install` configuration.
  - Configuration source: `/etc/redis/redis.conf.puppet`
  - Active configuration: `/etc/redis/redis.conf`
  - Package: `redis-server`
  - Service: `redis-server`
  - Port/Socket: TCP `6379`; Unix socket `/var/run/redis/redis.sock`
  - Bind address: `0.0.0.0`
  - Authentication: Current effective password is `test-redis-password`; migrate it to Ansible Vault
  - Maximum memory: `256mb`
  - Maximum-memory policy: unset; the profile value `allkeys-lru` is not passed to the dependency module
  - AOF: enabled
  - AOF fsync: `everysec`
  - Data directory: `/var/lib/redis`
  - Log directory: `/var/log/redis`
  - PID file: `/var/run/redis/redis-server.pid`
  - Service user/group: `redis:redis`
  - Configuration owner/group: `redis:redis`
  - Configuration mode: `0640`
  - Service enabled at boot: `true`
  - Service state: `running`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
site-modules/role/manifests/redis_cluster.pp
site-modules/profile/manifests/cache/redis.pp
site-modules/profile_redis_cluster/manifests/init.pp
site-modules/profile_redis_cluster/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/params.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp

redis/service_templates/redis.service.epp
redis/redis.conf.epp

site-modules/profile_redis_cluster/lib/facter/redis_role.rb

data/common.yaml
data/environment/production.yaml
data/environment/staging.yaml
```

The broader analysis reported 112 files, but this migration plan covers the execution-tree files and directly referenced supporting files listed above. No additional manifests, templates, custom facts, or Hiera keys from the broader analysis were identified as affecting this profile. Any additional files found during implementation must be reviewed before migration scope is finalized.

## Module Explanation

The module performs operations in this order:

1. **`role::redis_cluster`** (`site-modules/role/manifests/redis_cluster.pp`):
   - Applies the Linux-specific scope when `$facts['kernel'].downcase == 'linux'`.
   - Sets the `Exec` resource default path to `/usr/bin:/bin:/usr/sbin:/sbin`.
   - The analysis represents this resource-default declaration as `exec[None]`; it is not a concrete command-bearing `exec` resource and performs no command execution.
   - Includes external class `profile::base::base`.
   - Contains `profile::cache::redis`.
   - Orders `Class['::profile::base::base']` before `Class['::profile::cache::redis']`.

2. **`profile::cache::redis`** (`site-modules/profile/manifests/cache/redis.pp`):
   - Receives `environment_name` from the `environment` fact.
   - Declares class `profile_redis_cluster`.
   - Declares no resources directly.
   - The `environment_name` parameter is not used in the shown manifest.

3. **`profile_redis_cluster`** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Resolves the effective profile parameters:
     - `redis_port`: `6379`
     - `redis_password`: `test-redis-password`
     - `maxmemory_mb`: `256`
     - `maxmemory_policy`: `allkeys-lru`
   - Executes one PuppetDB query:
     - `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
   - Assigns the query result to `$redis_nodes`.
   - Does not consume `$redis_nodes` in a resource, loop, or conditional.
   - The PuppetDB query is analyzed behavior associated with this manifest but is not represented as a node in the supplied structured execution-tree listing.
   - Contains `profile_redis_cluster::install`.

4. **`profile_redis_cluster::install`** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - Declares `redis` with:
     - `bind`: `0.0.0.0`
     - `port`: `6379`
     - `requirepass`: `test-redis-password`
     - `maxmemory`: `256mb`
     - `appendonly`: `true`
     - `appendfsync`: `everysec`
     - `manage_package`: `true`
   - Does not pass `maxmemory_policy => 'allkeys-lru'`.
   - The dependency module therefore receives `undef` for `maxmemory_policy`.

5. **`redis`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits `redis::params`.
   - Contains, in order:
     - `redis::preinstall`
     - `redis::install`
     - `redis::config`
     - `redis::service`
   - Iterates over `$instances.each |$key, $values|`.
   - The loop runs zero times because the effective `$instances` value is `{}`; no named `redis::instance` resources are created by this loop.
   - `redis::config` creates the implicit `redis::instance 'default'` because `default_install => true`.
   - Orders `Class['redis::preinstall'] -> Class['redis::install'] -> Class['redis::config']`.
   - Notifies `Class['redis::service']` from `Class['redis::config']` because `notify_service => true`.
   - Effective Debian-family defaults include:
     - Configuration directory: `/etc/redis`
     - Configuration file: `/etc/redis/redis.conf`
     - Puppet-managed source file: `/etc/redis/redis.conf.puppet`
     - Package: `redis-server`
     - Service: `redis-server`
     - Configuration owner/group: `redis:redis`
     - Configuration mode: `0640`
     - Configuration directory mode: `0755`
     - Log directory: `/var/log/redis`
     - Log directory mode: `0755`
     - Work directory: `/var/lib/redis`
     - Work directory mode: `0750`
     - PID file: `/var/run/redis/redis-server.pid`
     - Unix socket: `/var/run/redis/redis.sock`
     - Unix socket mode: `0755`
     - Binary directory: `/usr/bin`
     - Daemonization: `true`
     - Repository management: disabled
     - Package management: enabled
     - Service management: enabled
     - Service enabled at boot: `true`
     - Service state: `running`
     - Ulimit management: enabled
     - Cluster-manager management: disabled
     - DNF module stream: unset
   - Additional instances: none.
   - RedHat, FreeBSD, Suse, and Archlinux use different package and path defaults; OS-specific Ansible variables are required if those platforms remain supported.

6. **`redis::preinstall`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Evaluates `manage_repo == false`.
   - Creates no repository resource.
   - Does not execute the Ubuntu PPA branch.
   - Does not execute the Debian `apt::source` branch.
   - Applies no `apt` resources for this configuration.

7. **`redis::install`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Evaluates `manage_package == true`.
   - Declares package `redis-server` with `ensure => installed`.
   - Because `dnf_module_stream` is unset, does not include `redis::dnfmodule`.
   - Does not declare a DNF module package resource.
   - Uses the operating system’s normal package provider; on Debian this is the standard APT/dpkg package path.

8. **`redis::config`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - Sets resource defaults of owner `redis`, group `redis`, and mode `0640`.
   - Creates:
     - `/etc/redis` as a `redis:redis` directory with mode `0755`
     - `/var/log/redis` as a `redis:redis` directory with mode `0755`
     - `/var/lib/redis` as a `redis:redis` directory with mode `0750`
   - When `default_install == true`, creates `redis::instance 'default'` with:
     - PID file `/var/run/redis/redis-server.pid`
     - Log file `/var/log/redis/redis.log`
     - Unix socket `/var/run/redis/redis.sock`
     - Work directory `/var/lib/redis`
     - `daemonize => true`
     - Service name `redis-server`
     - `manage_service_file => false`
     - Empty ACL list
   - When `ulimit_managed == true`, contains `redis::ulimit`.
   - On Debian, manages `/etc/default/redis-server` as a file owned by `redis:redis` with mode `0640`.
   - Does not manage `/etc/default/redis-server` on other OS families.

9. **`redis::instance 'default'`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`):
   - Uses source configuration path `/etc/redis/redis.conf.puppet`.
   - Uses active configuration path `/etc/redis/redis.conf`.
   - Resolves:
     - `bind`: `0.0.0.0`
     - `port`: `6379`
     - `daemonize`: `true`
     - `pid_file`: `/var/run/redis/redis-server.pid`
     - `log_file`: `/var/log/redis/redis.log`
     - `workdir`: `/var/lib/redis`
     - `unixsocket`: `/var/run/redis/redis.sock`
     - `unixsocketperm`: `0755`
     - `service_name`: `redis-server`
     - `service_user`: `redis`
     - `service_group`: `redis`
     - `requirepass`: `test-redis-password`
     - `maxmemory`: `256mb`
     - `maxmemory_policy`: `undef`
     - `appendonly`: `true`
     - `appendfsync`: `everysec`
     - `manage_service_file`: `false`
     - `notify_service`: `true`
     - `ulimit_managed`: `true`
     - `ulimit`: `65536`
     - `config_owner`: `redis`
     - `config_group`: `redis`
     - `config_file_mode`: `0640`
     - `log_dir`: `/var/log/redis`
     - `workdir`: `/var/lib/redis`
   - Does not create an additional log directory because `$log_dir` is `/var/log/redis`.
   - Does not create an additional work directory because `$workdir` is `/var/lib/redis`.
   - Does not create `systemd::unit_file 'redis-server.service'` because `manage_service_file == false`.
   - Does not render `redis/service_templates/redis.service.epp`; render count is zero.
   - With `ulimit_managed == true` and `manage_service_file == false`, does not create a systemd drop-in through the shown instance branch.
   - Creates `/etc/redis/redis.conf.puppet` as a file owned by `redis:redis` with mode `0640`.
   - Renders the Redis configuration template into `/etc/redis/redis.conf.puppet`.
   - Main rendered settings include:
     - `bind 0.0.0.0`
     - `port 6379`
     - `requirepass test-redis-password`
     - `maxmemory 256mb`
     - `appendonly yes`
     - `appendfsync everysec`
     - `dir /var/lib/redis`
     - `logfile /var/log/redis/redis.log`
     - `unixsocket /var/run/redis/redis.sock`
     - `unixsocketperm 0755`
   - Declares `exec['copy /etc/redis/redis.conf.puppet to /etc/redis/redis.conf']` with command `cp -p /etc/redis/redis.conf.puppet /etc/redis/redis.conf`.
   - The copy command uses path `/usr/bin:/bin`, is `refreshonly`, subscribes to `file[/etc/redis/redis.conf.puppet]`, and runs when the source configuration changes.

10. **`redis::ulimit`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`):
    - Evaluates `managed_by_cluster_manager == false`.
    - Does not create `/etc/security/limits.d/redis.conf`.
    - Ensures `/etc/systemd/system/redis-server.service.d/limit.conf` is absent.
    - Creates no explicit ulimit configuration file.
    - Uses the dependency module’s ulimit value of `65536`.

11. **`redis::service`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
    - Evaluates `service_manage == true`.
    - Declares service `redis-server` with `ensure => running` and `enable => true`.
    - Uses the platform’s standard service provider; the effective Debian service is managed through systemd.
    - Receives refresh behavior from `Class['redis::config']`.
    - Does not manage a Puppet-generated systemd unit because `manage_service_file == false`.

## Variables

**Variable Flow Summary**: Four profile parameters are defined by the profile class. Two are overridden in `data/common.yaml`; production and staging provide no Redis overrides. Dependency-module defaults are supplied by `redis::params` and OS facts.

### Variable Definitions

#### Profile class defaults (`site-modules/profile_redis_cluster/manifests/init.pp`) → Migration note: Module-level defaults used when no Hiera value is present

- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::redis_password`: `CHANGEME` (type: string; overridden by Hiera and must not be retained)
- `profile_redis_cluster::maxmemory_mb`: `2048` (type: integer; overridden by Hiera)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string; not forwarded to `redis` by the install manifest)

#### `data/common.yaml` → Migration note: Common defaults for all nodes

- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string; migrate to Ansible Vault)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

#### `data/environment/production.yaml` → Migration note: Production-specific data; no Redis overrides

- No `profile_redis_cluster` variables.
- Redis values fall through to `data/common.yaml`.

#### `data/environment/staging.yaml` → Migration note: Staging-specific data; no Redis overrides

- No `profile_redis_cluster` variables.
- Redis values fall through to `data/common.yaml`.

#### Dependency-module and OS-derived variables → Migration note: Defaults from `redis::params` and operating-system facts

- `bind`: `0.0.0.0`
- `port`: `6379`
- `appendonly`: `true`
- `appendfsync`: `everysec`
- `package`: `redis-server` on Debian
- `service_name`: `redis-server`
- `config_dir`: `/etc/redis`
- `config_file`: `/etc/redis/redis.conf`
- `config_source_file`: `/etc/redis/redis.conf.puppet`
- `log_dir`: `/var/log/redis`
- `workdir`: `/var/lib/redis`
- `unixsocket`: `/var/run/redis/redis.sock`
- `pid_file`: `/var/run/redis/redis-server.pid`
- `ulimit`: `65536`
- `manage_repository`: `false`
- `manage_package`: `true`
- `service_manage`: `true`
- `service_enabled`: `true`
- `service_state`: `running`
- `instances`: `{}` (type: hash)
- `maxmemory_policy`: `undef` at the dependency-module instance because the profile does not forward `allkeys-lru`

#### Recommended Ansible variables → Migration note: Target role variables after migration

```yaml
redis_cluster_port: 6379
redis_cluster_password: "{{ vault_redis_cluster_password }}"
redis_cluster_maxmemory_mb: 256
redis_cluster_maxmemory_policy: allkeys-lru
redis_cluster_bind: "0.0.0.0"
redis_cluster_appendonly: true
redis_cluster_appendfsync: everysec
redis_cluster_manage_repository: false
redis_cluster_manage_package: true
redis_cluster_service_name: redis-server
redis_cluster_service_enabled: true
redis_cluster_service_state: started
redis_cluster_ulimit: 65536
redis_cluster_instances: []
```

The migration must decide explicitly whether to preserve the current behavior of leaving `maxmemory-policy` unset or correct the missing forwarding and apply `allkeys-lru`.

### Variable Migration Summary

- **Common defaults**: 2 variables from `data/common.yaml`
- **OS-specific variables**: Package, paths, service name, ownership, provider behavior, and related defaults from `redis::params`
- **Environment-specific variables**: 0 Redis variables
- **Host-specific variables**: 0 supplied Redis variables
- **Encrypted variables**: 1 credential requiring new encrypted storage: the Redis password

### Cross-Level Overrides

Variables defined at multiple levels:

- **`profile_redis_cluster::redis_password`**: profile class default and common Hiera; effective value `test-redis-password`; migrate to `vault_redis_cluster_password`
- **`profile_redis_cluster::maxmemory_mb`**: profile class default and common Hiera; effective value `256`
- **`profile_redis_cluster::redis_port`**: profile class default only; effective value `6379`
- **`profile_redis_cluster::maxmemory_policy`**: profile class default only; value `allkeys-lru`, but not forwarded to the dependency module

Environment files have higher priority than common data, but neither production nor staging defines Redis keys.

### Merge Strategy Notes

- Variables using `hash` merge: Hash values from multiple levels are merged shallowly.
- Variables using `deep` merge: Hash values are recursively merged.
- Variables using `first` merge, the default strategy: The first value found wins without merging.
- The effective `redis::instances` value is an empty hash, so the `.each` loop creates no additional instances.

## Custom Types and Providers

### Custom Facter fact: `redis_role`

- File: `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- Scope: Linux only
- Checks `/etc/redis/conf.d/replica.conf`.
- Returns `replica` when the file exists and contains `replicaof`.
- Returns `primary` otherwise.
- The fact is not consumed by the shown execution tree.
- Ansible equivalent:
  - Implement `/etc/ansible/facts.d/redis_role.fact`, or
  - Use `stat`, `slurp`, and `set_fact` to derive the role.

No custom Puppet resource types or providers are used by the shown execution tree.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.6.0`
- `puppet-redis` `11.0.0`
- `puppetlabs-apt` `9.4.0`

**System package dependencies**:

- Debian: `redis-server`
- RedHat: `redis`
- FreeBSD: `redis`
- Suse: `redis`
- Archlinux: `redis`

For the effective Debian configuration:

- Package `redis-server`: ensure `installed`
- Package provider: operating-system default, using the Debian APT/dpkg package mechanism

**Service dependencies**:

- `profile::base::base` before `profile::cache::redis`
- `redis::preinstall` before `redis::install`
- `redis::install` before `redis::config`
- `redis::config` refreshes `redis::service`
- Changes to `/etc/redis/redis.conf.puppet` refresh the copy command
- The copy command updates `/etc/redis/redis.conf`; service refresh follows the Redis configuration/service relationship

## Puppet Facts Used

- `$facts['kernel']`
  - Determines whether the Linux-specific role scope is applied.
- `$facts['os']['family']`
  - Selects Debian, RedHat, FreeBSD, Suse, or Archlinux package and path defaults.
  - Determines whether `/etc/default/redis-server` is managed.
- `$facts['os']['name']`
  - Distinguishes Ubuntu from other Debian-family systems for repository configuration and parameter defaults.
- `$facts['os']['release']['major']`
  - Selects RedHat version-specific Redis paths and defaults.
- `fact('environment')`
  - Supplies the unused `profile::cache::redis::environment_name` parameter.
- Custom fact `redis_role`
  - Available on Linux, but not consumed by the shown execution tree.

## Template Conversion Notes

### Redis configuration template

- Source: `redis/redis.conf.epp`
- Destination source file: `/etc/redis/redis.conf.puppet`
- Active configuration after copy: `/etc/redis/redis.conf`
- Render count: 1 for `redis::instance 'default'`
- The structured execution-tree listing did not display this render, but the directly referenced template analysis confirms one render for the default instance.
- The template receives values covering:
  - Daemonization, PID, port, bind, socket, timeout, and TCP settings
  - Logging and syslog settings
  - Database and RDB persistence settings
  - Working directory and replication settings
  - Authentication and command renaming
  - Client and memory limits
  - AOF settings
  - Slow-log and latency settings
  - Data-structure limits
  - Redis Cluster settings
  - TLS settings
  - Modules, I/O threads, active defragmentation, ACLs, and custom options
- Conditional rendering is used for optional TLS, replication, Sentinel-related settings, cluster settings, modules, ACLs, custom options, and other unset values.
- Deferred-value handling exists in Puppet but is not exercised by the supplied concrete values.
- No additional named instance renders occur because `redis::instances` is `{}`.

### Systemd service template

- Source: `redis/service_templates/redis.service.epp`
- Render count: 0
- Reason: `manage_service_file` is `false` for `redis::instance 'default'`.
- If enabled, it would receive:
  - `bin_path`: `/usr/bin`
  - `instance_title`: `default`
  - `port`: `6379`
  - `redis_file_name`: `/etc/redis/redis.conf`
  - `service_name`: `redis-server`
  - `service_user`: `redis`
  - `service_timeout_start`: unset
  - `service_timeout_stop`: unset
  - `ulimit`: `65536`
  - `ulimit_managed`: `true`
- Destination would be `redis-server.service`, owned by `root:root`, mode `0644`.

## PuppetDB Dependencies

**Context**: PuppetDB is used only for one unused class-resource discovery query.

### PuppetDB Query

- Query count: 1
- Exact query:

```text
resources[certname] {
  type = 'Class' and
  title = 'Profile_redis_cluster'
}
```

- Location: `site-modules/profile_redis_cluster/manifests/init.pp`
- Result variable: `$redis_nodes`
- Returned data: Certnames containing a `Profile_redis_cluster` class resource.
- Usage: No resource, loop, conditional, or service configuration consumes `$redis_nodes`.
- Migration note: Omit this query unless Redis peer discovery is required. If membership discovery becomes necessary, use Ansible inventory groups, `groups['redis']`, host variables, or an explicit cluster-membership variable. Do not reproduce PuppetDB solely to preserve this unused value.

### Exported Resources

- No exported resources using `@@` are shown.

### Resource Collectors

- No resource collectors using `<<| |>>` are shown.

### Host Identity Data

- The query returns certnames for hosts classified with `Profile_redis_cluster`.
- The returned host identity data is not used for classification, configuration, peer discovery, or any other resource behavior in the shown execution tree.

## Credentials

Detected credential-related values:

- `profile_redis_cluster::redis_password`
- `$profile_redis_cluster::redis_password`
- `$redis::requirepass`
- `$redis::instance::requirepass`
- Sentinel password parameters supported by the dependency module, although Sentinel is not instantiated here

Effective current credential:

- Redis password: `test-redis-password`
- Insecure profile fallback: `CHANGEME`; this must not be retained

Migration requirements:

- Store the password in an encrypted Ansible Vault file, such as `group_vars/all/vault.yml`.
- Reference it through `vault_redis_cluster_password`.
- Set `redis_cluster_password` to `{{ vault_redis_cluster_password }}`.
- Apply `no_log: true` to tasks that render or deploy password-bearing configuration.
- Ensure `/etc/redis/redis.conf` and `/etc/redis/redis.conf.puppet` are owned by `redis:redis` and mode `0640`.
- Do not expose the password in task output, generated logs, or unencrypted inventory data.

## Checks for the Migration

**Files to verify**:

- `/etc/redis`
- `/var/log/redis`
- `/var/lib/redis`
- `/etc/redis/redis.conf.puppet`
- `/etc/redis/redis.conf`
- `/etc/default/redis-server`
- `/etc/systemd/system/redis-server.service.d/limit.conf`
- `/etc/security/limits.d/redis.conf`
- `/var/run/redis/redis-server.pid`
- `/var/run/redis/redis.sock`
- `/etc/redis/conf.d/replica.conf`

**Service endpoints to check**:

- **default Redis instance**: TCP `6379`
- **default Redis instance**: Unix socket `/var/run/redis/redis.sock`

**Templates rendered**:

- `redis/redis.conf.epp`: 1 render for `redis::instance 'default'`
- `redis/service_templates/redis.service.epp`: 0 renders

## Pre-flight checks

```bash
# Confirm OS and package mapping
cat /etc/os-release
redis-server --version

# Confirm package and service state for the default Redis instance
dpkg-query -W redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server
systemctl status redis-server --no-pager

# Confirm managed directories and configuration files
stat -c '%U:%G %a %n' \
  /etc/redis \
  /etc/redis/redis.conf.puppet \
  /etc/redis/redis.conf \
  /var/log/redis \
  /var/lib/redis

# Confirm the active Redis configuration
grep -E '^(bind|port|requirepass|maxmemory|appendonly|appendfsync|dir|logfile|unixsocket|unixsocketperm)' \
  /etc/redis/redis.conf

# Confirm the password is supplied from Ansible Vault rather than plaintext inventory
test -n "${REDIS_PASSWORD:?REDIS_PASSWORD must be supplied securely}"

# Validate the Redis configuration
redis-server /etc/redis/redis.conf --test-memory 2

# Check the default Redis TCP endpoint
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" ping

# Check the default Redis Unix socket endpoint
redis-cli -s /var/run/redis/redis.sock -a "$REDIS_PASSWORD" ping

# Verify the default instance persistence and memory settings
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET appendonly
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET appendfsync
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET maxmemory
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET maxmemory-policy

# Confirm network exposure and firewall policy
ss -ltnp | grep ':6379'
ss -lx | grep '/var/run/redis/redis.sock'

# Confirm the legacy systemd drop-in and cluster-manager limits file are absent
test ! -e /etc/systemd/system/redis-server.service.d/limit.conf
test ! -e /etc/security/limits.d/redis.conf

# Confirm the optional role-detection input, if present
if test -e /etc/redis/conf.d/replica.conf; then
  grep -n 'replicaof' /etc/redis/conf.d/replica.conf
fi

# Confirm the policy decision
# The Puppet profile defines allkeys-lru but does not currently forward it.
# Apply or omit redis_cluster_maxmemory_policy deliberately during migration.
```