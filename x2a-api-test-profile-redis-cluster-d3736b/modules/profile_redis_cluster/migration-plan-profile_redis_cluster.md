---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: `profile_redis_cluster` provisions one Redis instance named `default` on Linux through the bundled `puppet-redis` dependency. The effective profile configuration is Redis bound to `0.0.0.0` on TCP port `6379`, protected by the Hiera password `test-redis-password`, with `256mb` maxmemory, append-only persistence, and `everysec` fsync. The service is managed as `redis-server`, enabled, and expected to be running. Redis configuration is rendered to `/etc/redis/redis.conf.puppet` and copied to `/etc/redis/redis.conf`. The profile contains a PuppetDB query whose result is unused; the Ansible migration should use inventory data instead of PuppetDB if cluster discovery is later required.

## Service Type and Instances

**Service Type**: In-memory database/cache; Redis server.

**Configured Instances**:

- **default**: Default Redis server instance.
  - Configuration directory: `/etc/redis`
  - Active configuration: `/etc/redis/redis.conf`
  - Puppet source configuration: `/etc/redis/redis.conf.puppet`
  - Log directory: `/var/log/redis`
  - Data directory: `/var/lib/redis`
  - Service: `redis-server`
  - Port: `6379`
  - Bind address: `0.0.0.0`
  - Unix socket: `/var/run/redis/redis.sock`
  - Authentication: `test-redis-password`; migrate to Ansible Vault or an external secret provider
  - Maxmemory: `256mb`
  - Maxmemory policy: `allkeys-lru` is defined by the profile but is not passed to `class redis`; verify the rendered configuration before reproducing it as an effective Redis setting
  - Append-only persistence: enabled
  - Append fsync: `everysec`
  - Service user/group: `redis`/`redis`
  - Open-file limit: `65536`
  - Additional user-defined instances: none

## File Structure

```text
site-modules/role/manifests/redis_cluster.pp
site-modules/profile/manifests/cache/redis.pp
site-modules/profile_redis_cluster/manifests/init.pp
site-modules/profile_redis_cluster/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/templates/redis/service_templates/redis.service.epp
site-modules/profile_redis_cluster/migration-dependencies/redis/templates/redis/redis.conf.epp
site-modules/profile_redis_cluster/templates/redis.conf.erb
site-modules/profile_redis_cluster/lib/facter/redis_role.rb
```

The supplied directory listing also contains `site-modules/profile_redis_cluster/templates/redis.conf.erb`. This is not the template selected by the analyzed Redis class, which defaults to `redis/redis.conf.epp`.

## Module Explanation

The module performs operations in this order:

1. **`role::redis_cluster`** (`site-modules/role/manifests/redis_cluster.pp`):
   - Uses `$facts['kernel']`; when the lowercased kernel is `linux`, sets the default `Exec` path to `/usr/bin:/bin:/usr/sbin:/sbin`.
   - Includes external class `::profile::base::base`.
   - Contains `::profile::cache::redis`.
   - Orders `Class['::profile::base::base']` before `Class['::profile::cache::redis']`.
   - Declares no direct package, file, service, or Redis configuration resources.

2. **`profile::cache::redis`** (`site-modules/profile/manifests/cache/redis.pp`):
   - Sets `environment_name` from `fact('environment')`.
   - Includes `profile_redis_cluster`.
   - Does not use `environment_name` to alter Redis resources.

3. **`profile_redis_cluster`** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Resolves `redis_port` to `6379`.
   - Resolves `redis_password` to `test-redis-password` through `data/common.yaml`.
   - Resolves `maxmemory_mb` to `256` through `data/common.yaml`.
   - Defines `maxmemory_policy` as `allkeys-lru`.
   - Queries PuppetDB with `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }` and assigns the result to `$redis_nodes`.
   - Does not use `$redis_nodes` in a resource or conditional.
   - Contains `profile_redis_cluster::install`.

4. **`profile_redis_cluster::install`** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - Includes `redis` with `bind => ['0.0.0.0']`.
   - Passes `port => 6379`.
   - Passes `requirepass => 'test-redis-password'`.
   - Passes `maxmemory => '256mb'`.
   - Passes `appendonly => true`.
   - Passes `appendfsync => 'everysec'`.
   - Passes `manage_package => true`.
   - Does not pass `maxmemory_policy`; validate the generated Redis configuration before enforcing `allkeys-lru` in Ansible.

5. **`redis`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits `redis::params`.
   - Contains `redis::preinstall`, `redis::install`, `redis::config`, and `redis::service`.
   - Uses the default empty `$instances` hash.
   - The `$instances.each |$key, $values|` loop runs zero times; no additional named instances are created.
   - Orders `redis::preinstall` before `redis::install`, and `redis::install` before `redis::config`.
   - Because `notify_service` is true, configuration changes notify `redis::service`.
   - Relevant defaults include:
     - `manage_repo`: `false`
     - `manage_package`: `true`
     - `package_ensure`: `installed`
     - `package_name`: platform-resolved Redis package from `redis::params`
     - `default_install`: `true`
     - `config_dir`: `/etc/redis`
     - `config_file`: `/etc/redis/redis.conf`
     - `config_file_orig`: `/etc/redis/redis.conf.puppet`
     - `config_file_mode`: `0640`
     - `config_owner`: `redis`
     - `config_group`: `redis`
     - `log_dir`: `/var/log/redis`
     - `workdir`: `/var/lib/redis`
     - `workdir_mode`: `0750`
     - `service_name`: `redis-server`
     - `service_manage`: `true`
     - `service_ensure`: `running`
     - `service_enable`: `true`
     - `service_user`: `redis`
     - `service_group`: `redis`
     - `ulimit_managed`: `true`
     - `ulimit`: `65536`
     - `managed_by_cluster_manager`: `false`
     - `dnf_module_stream`: `undef`
     - `cluster_enabled`: `false`
     - TLS parameters: unset
   - The `redis::params` source is referenced by inheritance but is not included in the supplied file listing; its platform-specific defaults must be verified from the external dependency.

6. **`redis::preinstall`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Evaluates `$facts['os']['name']` and `$facts['os']['family']`.
   - Does not manage repositories because `manage_repo` is `false`.
   - Does not configure Debian repositories or an Ubuntu PPA.
   - Does not declare `apt::source['redis']`.

7. **`redis::install`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Runs because `manage_package == true`.
   - Declares the Redis package with `ensure => installed`.
   - The Puppet resource title is `redis`; the expected Debian-family package is `redis-server`. Confirm the resolved package name on every supported target OS.
   - Does not include `redis::dnfmodule` because `dnf_module_stream` is unset.
   - If a DNF stream is later configured, limit that behavior to Red Hat-family hosts and configure the module before package installation.

8. **`redis::config`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - Creates `/etc/redis` as a directory owned by `redis:redis`.
   - Creates `/var/log/redis` as a directory owned by `redis:redis`.
   - Creates `/var/lib/redis` as a directory owned by `redis:redis` with mode `0750`.
   - Uses configuration file owner `redis`, group `redis`, and mode `0640`.
   - Because `default_install == true`, creates the default instance `redis::instance['default']`.
   - Passes the default instance:
     - `pid_file`: `/var/run/redis/redis-server.pid`
     - `log_file`: `redis.log`
     - `unixsocket`: `/var/run/redis/redis.sock`
     - `workdir`: `/var/lib/redis`
     - `service_name`: `redis-server`
     - `manage_service_file`: `false`
     - `acls`: `[]`
   - Does not create additional log or work directories because the instance paths equal the class defaults.
   - Contains `redis::ulimit`.
   - On Debian-family systems, manages `/etc/default/redis-server` with owner `redis`, group `redis`, and mode `0640`.
   - Does not create the Debian-specific resource on non-Debian systems.

9. **`redis::instance['default']`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`):
   - Uses `/etc/redis/redis.conf.puppet` as the rendered source configuration.
   - Uses `/etc/redis/redis.conf` as the active configuration.
   - Does not create `systemd::unit_file['redis-server.service']` because `manage_service_file` is `false`.
   - Creates the systemd drop-in `redis-server-90-limits.conf` with `LimitNOFILE=65536` because `ulimit_managed` is true.
   - Uses the standard EPP rendering branch because no Deferred values are supplied.
   - Renders `redis/redis.conf.epp` once for the `default` instance.
   - Renders the source file with owner `redis`, group `redis`, and mode `0640`.
   - Copies `/etc/redis/redis.conf.puppet` to `/etc/redis/redis.conf` using:
     - Command: `cp -p /etc/redis/redis.conf.puppet /etc/redis/redis.conf`
     - Path: `/usr/bin:/bin`
     - Refresh behavior: `true`
   - The copy command subscribes to changes in `/etc/redis/redis.conf.puppet`.

10. **`redis::ulimit`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`):
    - Is private to `redis::config`.
    - Runs because `managed_by_cluster_manager == false`.
    - Does not create `/etc/security/limits.d/redis.conf`.
    - Removes `/etc/systemd/system/redis-server.service.d/limit.conf`.
    - Relies on the systemd drop-in to set `LimitNOFILE=65536`.

11. **`redis::service`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
    - Runs because `service_manage == true`.
    - Manages `service['redis-server']` with `ensure => running` and `enable => true`.
    - Receives notifications from `redis::config`.
    - The Ansible equivalent is a handler that restarts or reloads `redis-server` after configuration changes.

12. **`redis::dnfmodule`** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`):
    - Is present in the dependency tree but is not included for this configuration.
    - No DNF module resource is created because `dnf_module_stream` is unset.

13. **Additional instance loop**:
    - The user-supplied `$instances` loop runs zero times.
    - The only instance is `redis::instance['default']`.
    - The `default` instance uses port `6379`, bind address `0.0.0.0`, service `redis-server`, active configuration `/etc/redis/redis.conf`, source configuration `/etc/redis/redis.conf.puppet`, data directory `/var/lib/redis`, and log directory `/var/log/redis`.

## Variables

**Variable Flow Summary**: 4 profile parameters across manifest defaults and Hiera data, with approximately 100 inherited Redis dependency parameters. The supplied Redis-specific Hiera data contains common defaults and no environment-specific or host-specific overrides.

### Variable Definitions

#### `data/common.yaml` — common defaults

Migration note: Base Redis values for all nodes using this Hiera hierarchy.

- `profile_redis_cluster::redis_password`: `"test-redis-password"` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

The file also contains unrelated NTP, SSH, syslog, HAProxy, application-stack, and PostgreSQL variables, which are outside this migration.

#### `data/environment/production.yaml` — environment-specific

Migration note: Production-level Redis overrides.

- No Redis-related variables.

#### `data/environment/staging.yaml` — environment-specific

Migration note: Staging-level Redis overrides.

- No Redis-related variables.

#### Manifest defaults in `site-modules/profile_redis_cluster/manifests/init.pp`

Migration note: Fallback values used when no higher-priority Hiera value is present.

- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::redis_password`: `"CHANGEME"` (type: string; overridden by Hiera)
- `profile_redis_cluster::maxmemory_mb`: `2048` (type: integer; overridden by Hiera)
- `profile_redis_cluster::maxmemory_policy`: `"allkeys-lru"` (type: string; not passed to `class redis`)

#### Recommended Ansible variables

```yaml
redis_cluster_port: 6379
redis_cluster_password: "{{ vault_redis_cluster_password }}"
redis_cluster_maxmemory_mb: 256
redis_cluster_maxmemory_policy: allkeys-lru
redis_cluster_bind:
  - "0.0.0.0"
redis_cluster_appendonly: true
redis_cluster_appendfsync: everysec
redis_cluster_service_name: redis-server
redis_cluster_ulimit: 65536
```

### Variable Migration Summary

- **Common defaults**: 2 Redis variables from `data/common.yaml`.
- **Manifest defaults**: 4 profile parameters.
- **OS-specific variables**: Dependency defaults vary by platform; verify `redis::params`, especially package name and directory modes.
- **Environment-specific variables**: 0 Redis variables.
- **Host-specific variables**: 0 supplied.
- **Encrypted variables**: 0.
- **Plaintext secrets requiring migration**: 1, `redis_password`.
- **PuppetDB-derived variables**: 1 unused variable, `$redis_nodes`.

### Cross-Level Overrides

- **`profile_redis_cluster::redis_password`**:
  - Defined in the manifest as `"CHANGEME"`.
  - Defined in `data/common.yaml` as `"test-redis-password"`.
  - Effective value: `"test-redis-password"`.
  - Merge strategy: `first`; Hiera data overrides the manifest default.
  - Migration: store only in Ansible Vault or an external secret manager.

- **`profile_redis_cluster::maxmemory_mb`**:
  - Defined in the manifest as `2048`.
  - Defined in `data/common.yaml` as `256`.
  - Effective value: `256`.
  - Merge strategy: `first`.

- **`profile_redis_cluster::redis_port`**:
  - Defined only in the manifest.
  - Effective value: `6379`.

- **`profile_redis_cluster::maxmemory_policy`**:
  - Defined only in the manifest.
  - Effective profile value: `allkeys-lru`.
  - Not forwarded to `class redis`; validate the generated configuration before treating it as effective.

### Merge Strategy Notes

- `hash` merge combines hash values from multiple levels using a shallow merge.
- `deep` merge recursively combines nested hash values.
- `first` merge, the default behavior, uses the first value found and performs no merging.
- The Redis profile values documented here use effective first-value resolution rather than hash or deep merging.

## Custom Types and Providers

### Custom fact: `redis_role`

- File: `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- Scope: Linux.
- Reads `/etc/redis/conf.d/replica.conf`.
- Returns `replica` when the file exists and contains `replicaof`.
- Returns `primary` otherwise.
- No reference to this fact is shown in the supplied Redis execution tree.
- Ansible equivalent:
  - Use `stat` and `slurp`, followed by `set_fact`; or
  - Deploy a local fact at `/etc/ansible/facts.d/redis_role.fact`.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.6.0`
- `puppet-redis` `11.0.0`
- `puppetlabs-apt` `9.4.0`

`redis::params` is inherited from the Redis dependency and must be checked in the external module source to confirm all platform-specific defaults.

**System package dependencies**:

- Redis package resolved by `redis::params`.
- Expected Debian-family package: `redis-server`.
- Repository resources are available through `puppetlabs-apt` but are unused because `manage_repo` is `false`.
- DNF module support is unused because `dnf_module_stream` is unset.

**Service dependencies**:

- `Class['::profile::base::base'] -> Class['::profile::cache::redis']`
- `redis::preinstall -> redis::install -> redis::config`
- `redis::config ~> redis::service`
- `file[/etc/redis/redis.conf.puppet] -> exec[copy /etc/redis/redis.conf.puppet to /etc/redis/redis.conf]`
- Configuration changes notify `service[redis-server]`.
- No custom `redis-server.service` unit is rendered for the default instance.

## Puppet Facts Used

- `$facts['kernel']`: Determines whether the role applies the Linux-specific `Exec` path.
- `fact('environment')`: Supplies the unused `environment_name` parameter in `profile::cache::redis`.
- `$facts['os']['name']`: Used by repository preinstallation logic to detect Ubuntu.
- `$facts['os']['family']`: Selects Debian-specific `/etc/default/redis-server` handling and validates Red Hat-family DNF behavior.
- Custom fact `redis_role`: Returns `primary` or `replica` from `/etc/redis/conf.d/replica.conf`; no use is shown in the analyzed execution tree.

## Template Conversion Notes

### `redis/redis.conf.epp`

- Render count: 1, for `redis::instance['default']`.
- Render destination: `/etc/redis/redis.conf.puppet`.
- Active configuration: `/etc/redis/redis.conf`, populated by the subsequent copy command.
- Rendering branch: standard EPP; no Deferred values are supplied.
- File owner/group/mode: `redis:redis`, `0640`.
- Important rendered values:
  - `bind`: `0.0.0.0`
  - `port`: `6379`
  - `requirepass`: `test-redis-password`
  - `maxmemory`: `256mb`
  - `appendonly`: enabled
  - `appendfsync`: `everysec`
  - `workdir`: `/var/lib/redis`
  - `log_file`: `/var/log/redis/redis.log`
  - `cluster_enabled`: `false`
  - TLS: disabled and unconfigured
  - Replication source: unset
- The complete resolved template parameter set includes Redis persistence, replication, authentication, client limits, memory, AOF, clustering, TLS, module, ACL, and custom-option parameters. Undefined values remain unset, and `acls` and `modules` are empty.
- Ansible conversion:
  - Render a Jinja2 template directly to `/etc/redis/redis.conf`, unless compatibility with the two-file Puppet workflow is required.
  - Use `no_log: true` when rendering the password directly.
  - Set owner `redis`, group `redis`, and mode `0640`.
  - Notify a Redis restart or reload handler.

### `redis/service_templates/redis.service.epp`

- Render count: 0 for `default`, because `manage_service_file` is `false`.
- If custom service-file management is enabled for a future instance, render one unit per configured custom service instance.
- Relevant parameters include:
  - `bin_path`
  - `instance_title`
  - `port`
  - `redis_file_name`
  - `service_name`
  - `service_user`
  - `service_timeout_start`
  - `service_timeout_stop`
  - `ulimit`
  - `ulimit_managed`
- For `default`, use the distribution-provided `redis-server.service`.

## PuppetDB Dependencies

**Context**: PuppetDB is referenced for class-resource discovery, but the returned data does not affect the supplied Redis resources.

- **PuppetDB Queries**:
  - Query: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
  - Returned data: certnames containing the `Profile_redis_cluster` class.
  - Consumer: `$redis_nodes` in `profile_redis_cluster`.
  - Usage: No resource or conditional consumes `$redis_nodes`.
  - Migration: Do not require PuppetDB in Ansible. Use inventory groups or an explicit Redis-node list if cluster topology is later needed.
  - Validation note: The supplied structured execution summary does not independently establish the query count; retain the query behavior but do not rely on an occurrence count.

- **Exported Resources**:
  - None. No `@@` resources are present.

- **Resource Collectors**:
  - None. No `<<| |>>` collectors are present.

- **Host Identity Data**:
  - No host identity data is used to classify Redis nodes beyond the unused PuppetDB query result.

## Credentials

- **Redis authentication password**:
  - Effective value: `test-redis-password`.
  - Source: `data/common.yaml`.
  - Manifest fallback: `CHANGEME`.
  - Current storage: plaintext Hiera/Puppet data.
  - Migration: store in Ansible Vault or an external secret provider, use restrictive permissions, and apply `no_log`.

- **Redis `masterauth`**:
  - Effective value: unset.
  - If replication is added, store the value in Vault or an external secret provider.

- **Redis TLS private key, certificate, and CA**:
  - Effective values: unset.
  - If TLS is enabled, distribute certificate material through protected PKI or secret automation.
  - Set private-key mode to `0600`.

- **Sentinel credentials and TLS paths**:
  - Not used by this execution tree.
  - Do not add Sentinel tasks unless the migration scope expands.

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
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/templates/redis/redis.conf.epp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/templates/redis/service_templates/redis.service.epp`
- `site-modules/profile_redis_cluster/templates/redis.conf.erb`
- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- `data/common.yaml`
- `data/environment/production.yaml`
- `data/environment/staging.yaml`
- External `redis::params` source from `puppet-redis` `11.0.0`

**Service endpoints to check**:

- `default` instance TCP endpoint: `6379`
- `default` instance Unix socket: `/var/run/redis/redis.sock`

**Templates rendered**:

- `redis/redis.conf.epp`: 1 render for `default`
- `redis/service_templates/redis.service.epp`: 0 renders for `default`

## Pre-flight checks

```bash
# Confirm the target operating system and resolved package name.
cat /etc/os-release
ansible redis -m package_facts

# Confirm the default Redis service account and group.
getent passwd redis
getent group redis

# Confirm the secret is available through Ansible Vault or the configured secret provider.
ansible-vault view group_vars/redis/vault.yml

# Confirm the default instance directories and permissions.
stat -c '%U:%G %a %n' /etc/redis /var/lib/redis /var/log/redis

# Confirm the default instance configuration files.
stat -c '%U:%G %a %n' /etc/redis/redis.conf /etc/redis/redis.conf.puppet

# Confirm effective default-instance settings.
grep -E '^(bind|port|requiredpass|maxmemory|appendonly|appendfsync)' /etc/redis/redis.conf

# Confirm the open-file-limit drop-in for the default instance.
systemctl cat redis-server
test -f /etc/systemd/system/redis-server.service.d/90-limits.conf

# Confirm the legacy limits file is absent.
test ! -e /etc/systemd/system/redis-server.service.d/limit.conf

# Validate the Redis configuration using the platform-supported Redis validation command.
redis-server /etc/redis/redis.conf --check-config

# Confirm the default instance is enabled and running.
systemctl is-enabled redis-server
systemctl is-active redis-server

# Verify authentication for the default instance.
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning ping

# Verify the default instance listens on TCP port 6379.
ss -lntp | grep ':6379'

# Verify the default instance Unix socket.
test -S /var/run/redis/redis.sock

# Change the rendered configuration and confirm the Ansible handler restarts or reloads
# the default redis-server service.
```

