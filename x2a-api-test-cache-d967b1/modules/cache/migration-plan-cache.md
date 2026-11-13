---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: a Memcached instance named `memcached` and a Redis instance named `6379`. Memcached is included first through the external `memcached` cookbook. Redis is configured for TCP port `6379`, password authentication, the `/run/redis` PID directory, and the `/var/log/redis` log directory. The recipe removes selected replication-related directives from `/etc/redis/6379.conf` and enables Redis through `redisio::enable`. The Redis recipes and the Memcached custom-resource implementation are not present in the supplied execution tree, so their package names, service names, defaults, and implementation details require validation against the external cookbooks before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached cache service
  - Location/Path: `/var/log/memcached` and `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: Memory `64` MB; maximum connections `1024`; maximum object size `1m`; process user `service_user`; `ulimit` `1024`; experimental options and additional CLI options are empty; threads are sourced from `node['memcached']['threads']`, but the supplied attribute-file summary does not verify whether that attribute exists.
  - Actions: Start and enable the Memcached service.
  - Validation status: The instance properties and custom-resource behavior require confirmation against the external `memcached` cookbook. The supplied execution tree confirms only the `memcached_instance[memcached]` resource.

- **`6379`**: Redis cache service
  - Location/Path: `/etc/redis/6379.conf`, `/run/redis`, and `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: Password authentication using the supplied Chef value `redis_secure_password_123`; Redis PID/runtime directory `/run/redis`; log directory owned by `redis:redis` with mode `0755`; `replicaservestaledata` explicitly set to `nil`; selected replication and client-buffer directives removed from the configuration.
  - Actions: Redis installation/configuration and enablement are expected through the external `redisio` cookbook, but the `redisio` and `redisio::enable` recipes are absent from the supplied execution tree.

## File Structure

The following files and dependency paths were identified from the supplied cookbook. Redis recipe files and the Memcached provider/custom-resource implementation are absent from the supplied execution tree.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider file path was supplied for `memcached_instance[memcached]`. Treat `memcached_instance` as an external custom resource whose implementation must be obtained from the `memcached` cookbook.

**Templates:**
```text
```

No rendered templates were identified in the supplied file listing. Confirm this against the complete resource and file inventory before migration.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` were identified. Confirm this against the complete analyzed-file inventory.

## Module Explanation

The cookbook performs operations in the following order.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe before any Redis operations.
   - Configures one Redis server item with port `6379`, password authentication, and `replicaservestaledata` set to `nil`.
   - Sets the Redis base PID directory to `/run/redis`.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Removes five directive patterns from `/etc/redis/6379.conf` through `ruby_block[fix_redis_config]`.
   - Includes the unavailable `redisio::enable` recipe.

   **Execution details:**

   - **Memcached inclusion**
     ```ruby
     include_recipe 'memcached'
     ```
     The external dependency creates or configures `memcached_instance[memcached]`. Its package installation, service account, runtime directories, service actions, and exact settings are not independently verifiable from the supplied execution tree.

   - **Redis server configuration**
     ```ruby
     node.default['redisio']['servers'] = [
       {
         'port' => '6379',
         'requirepass' => 'redis_secure_password_123',
         'replicaservestaledata' => nil
       }
     ]
     ```
     Configure exactly one Redis instance named `6379`. Store the password in an Ansible Vault variable rather than in plaintext. Preserve the unset or disabled `replicaservestaledata` behavior according to the selected Redis implementation.

   - **Redis PID directory**
     ```ruby
     node.default['redisio']['base_piddir'] = '/run/redis'
     ```
     Configure Redis to use `/run/redis`. Verify the target distribution and SELinux requirements before substituting another path.

   - **Redis installation and base configuration**
     ```ruby
     include_recipe 'redisio'
     ```
     The `redisio` recipe is missing. Obtain and validate the external implementation before finalizing the Redis package name, package version, service account, service unit, configuration template, defaults, and service behavior.

   - **Redis log directory**
     ```ruby
     directory '/var/log/redis' do
       owner 'redis'
       group 'redis'
       mode '0755'
       recursive true
     end
     ```
     Create `/var/log/redis` after Redis configuration, with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.

   - **Redis configuration cleanup**
     `ruby_block[fix_redis_config]` reads `/etc/redis/6379.conf` when the file exists, removes complete lines matching the following patterns, and writes the file back:
     ```text
     ^replica-serve-stale-data.*$
     ^replica-read-only.*$
     ^repl-ping-replica-period.*$
     ^client-output-buffer-limit.*$
     ^replica-priority.*$
     ```
     Implement this idempotently with scoped `lineinfile` tasks or an equivalent configuration-edit task. The original Chef resource does not explicitly notify a Redis restart or reload.

   - **Redis enablement**
     ```ruby
     include_recipe 'redisio::enable'
     ```
     The `redisio::enable` recipe is missing. Enable Redis at boot and start it if required by the validated Redis implementation. Confirm the exact service unit name before implementation.

   **Iterations:** No `.each` loops were identified. The Redis server collection contains exactly one configured item: `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package installation is delegated to the external `memcached` cookbook; the exact package name and implementation require validation.
- Redis package installation is delegated to the unavailable `redisio` cookbook; the exact package name and version require validation for the target operating system.
- No additional verified package names are available from the supplied execution tree.

**Service dependencies**:

- `memcached_instance[memcached]`: expected to start and enable the Memcached service; implementation requires validation.
- Redis: expected to be configured and enabled through `redisio` and `redisio::enable`; both recipe implementations are unavailable.
- The exact Redis systemd unit name is not available.

**Supported operating systems declared by metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe; migrate to Ansible Vault
  - **URL**: None detected
  - **Path**: Redis configuration for instance `6379`

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in Chef**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis `requirepass` authentication for the Redis server listening on port `6379`
- **Ansible migration**:
  - Store the password in an encrypted Ansible Vault variable such as `redis_requirepass`.
  - Reference the vaulted variable in the Redis configuration task.
  - Do not commit the literal password to the Ansible role, inventory, or defaults.
  - Restrict permissions on any rendered Redis configuration file containing the password.

No data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur variables, environment-variable secrets, TLS certificate references, database connection strings, or additional hardcoded tokens were identified in the supplied plan. The credential finding should be confirmed against the complete recipe-level analysis.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Redis Unix socket: none specified
- Redis bind address: not specified; verify the validated `redisio` defaults before exposing the service

**Templates rendered**:

- None identified in the supplied file listing. Confirm with the complete resource scan.
- Render count: `0` confirmed from the supplied plan; external cookbook templates remain subject to dependency validation.

**Configuration edits performed**:

- `/etc/redis/6379.conf` is edited in place.
- The following directives are removed when present:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

```bash
# Confirm supported operating system
cat /etc/os-release

# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211
printf "stats\r\nquit\r\n" | nc -w 2 127.0.0.1 11211
ps -ef | grep '[m]emcached'
ls -ld /var/log/memcached
ls -ld /var/run/memcached

# Verify Memcached configuration values where supported by the implementation
# Confirm port 11211, UDP port 11211, listen address 0.0.0.0,
# memory 64 MB, maximum connections 1024, maximum object size 1m,
# process user service_user, ulimit 1024, and configured thread behavior.

# Redis instance: 6379
systemctl list-unit-files | grep -i redis
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
ss -tlnp | grep ':6379'
ls -ld /run/redis
ls -ld /var/log/redis
find /var/log/redis -maxdepth 1 -type f -print

# Redis configuration validation
test -f /etc/redis/6379.conf
grep -E '^(requirepass|port|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify that the Redis port is 6379, authentication is configured,
# and all five removed directives are absent.

# Redis authenticated connectivity
read -s REDIS_PASSWORD
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD

# Expected authenticated response:
# PONG

# Redis unauthenticated behavior
redis-cli -h 127.0.0.1 -p 6379 PING
# Expected result: an authentication-required error when password protection is active.

# Redis logs and service status
journalctl -u redis --no-pager -n 100
systemctl is-active redis

# If the validated Redis implementation uses a different unit name,
# replace "redis" with that exact service name.

# Configuration-change behavior
# After changing the Ansible-managed Redis configuration, use the validated
# reload or restart handler and confirm that the service returns to active.
systemctl reload redis
systemctl is-active redis
```
