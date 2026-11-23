---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the `memcached` instance on TCP/UDP port `11211` and the Redis server identified as `redis-6379` on TCP port `6379`. Memcached uses 64 MB of memory, 1,024 maximum connections, `0.0.0.0` listeners, and start/enable actions. Redis requires authentication, uses `/run/redis` as its PID directory base, creates `/var/log/redis`, and removes five replication-related directives from `/etc/redis/6379.conf`. The `redisio` and `redisio::enable` recipes are missing from the supplied execution tree, so the Ansible implementation must explicitly recreate their required behavior and determine the platform-specific Redis package and service name.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: In-memory key/value cache
  - Package: `memcached`
  - Location/Path: `/var/log/memcached`, `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Memory: `64` MB
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Worker threads: `node['memcached']['threads']`; no default value is present in the supplied attributes file
  - System user: `service_user`, resolved by the dependency cookbook
  - System group: `service_group`, resolved by the dependency cookbook
  - ULimit: `1024`
  - Experimental options: None
  - Extra CLI options: None
  - Requested actions: Start and enable
  - User account: System account with home `/nonexistent`, shell `/bin/false`, comment `Memcached`, locked after creation
  - Directory ownership: `service_user:service_group`
  - Directory mode: `0755`

- **redis-6379**: Redis cache/data store server
  - Location/Path: Configuration `/etc/redis/6379.conf`; logs `/var/log/redis`; PID directory base `/run/redis`
  - Port/Socket: TCP `6379`
  - Authentication: Required
  - Password: Stored in the source recipe as `redis_secure_password_123`; migrate to Ansible Vault or an AAP credential-backed variable
  - Directory ownership: `/var/log/redis` owned by `redis:redis`
  - Directory mode: `/var/log/redis` uses `0755`
  - Enablement: Requested through `redisio::enable`; the recipe is missing from the supplied execution tree
  - Configuration cleanup: Remove `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Replicas, databases, Unix sockets, TLS certificate paths, and replica hostnames: None specified

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider file path was supplied for `memcached_instance[memcached]`. The provider must be identified from the installed `memcached` dependency during implementation.

**Templates:**
```text
```

No templates are rendered by the recipes shown in the execution tree.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The following files were present in the directory listing but are not shown as executed in the supplied execution tree:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

The `redisio` and `redisio::enable` recipe files are referenced but missing from the supplied execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Invokes `memcached::default`, which executes before the remaining Redis-related statements in this recipe.
   - Defines one Redis server configuration item for `redis-6379` on port `6379`.
   - Sets Redis authentication to the recipe value associated with `node['redisio']['servers'][0]['requirepass']`.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the missing `redisio` recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - Includes the missing `redisio::enable` recipe to enable the Redis service.

   **Redis server configuration item:**
   - Instance: `redis-6379`
   - Port: `6379`
   - `requirepass`: `redis_secure_password_123` in the source recipe; replace with a protected Ansible variable
   - `replicaservestaledata`: `nil`

   **`ruby_block[fix_redis_config]` behavior:**
   - Checks whether `/etc/redis/6379.conf` exists.
   - Reads the file when present.
   - Removes lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, or `replica-priority`.
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Does not fail solely because the file is absent.
   - The Ansible implementation should use idempotent `ansible.builtin.replace` tasks or an equivalent scoped configuration-editing method.

   The missing `redisio` recipes prevent confirmation of the Redis package name, service unit name, user creation behavior, configuration template path, and provider implementation. These must be determined for the target operating system during implementation.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Installs the `memcached` package using the platform default version because `memcached.version` is `nil`.
   - Creates the dependency-defined `service_group` group and `service_user` system account.
   - Configures the `memcached` instance through `memcached_instance[memcached]`.
   - Creates `/var/log/memcached` owned by `service_user:service_group` with mode `0755`.
   - Creates `/var/run/memcached` owned by `service_user:service_group` with mode `0755`.
   - Requests `:start` and `:enable` actions for `memcached_instance[memcached]`.

   **`memcached_instance[memcached]` properties:**
   - Memory: `64`
   - TCP port: `11211`
   - UDP port: `11211`
   - Listen address: `0.0.0.0`
   - Maximum connections: `1024`
   - Maximum object size: `1m`
   - User: `service_user`
   - Threads: `node['memcached']['threads']`
   - Experimental options: `[]`
   - Extra CLI options: `[]`
   - ULimit: `1024`
   - Actions: `:start`, `:enable`

3. **Memcached dependency defaults** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`):
   - `memcached.version`: `nil`
   - `memcached.memory`: `64`
   - `memcached.port`: `11211`
   - `memcached.udp_port`: `11211`
   - `memcached.listen`: `0.0.0.0`
   - `memcached.maxconn`: `1024`
   - `memcached.max_object_size`: `1m`
   - `memcached.experimental_options`: `[]`
   - `memcached.extra_cli_options`: `[]`
   - `memcached.ulimit`: `1024`
   - `memcached.logfilepath`: `/var/log/memcached`

## Dependencies

**External cookbook dependencies**:
- `memcached`, represented by `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `redisio`, referenced by `cache::default`; its recipes are missing from the supplied execution tree

**System package dependencies**:
- `memcached`
- Redis package: Not determinable from the supplied execution tree because the `redisio` recipe is missing

**Service dependencies**:
- `memcached_instance[memcached]` starts and enables Memcached
- `redisio::enable` is intended to enable `redis-6379`, but the exact Redis service unit name is unavailable

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Usage context**: Redis authentication for `redis-6379` on port `6379`
- **Migration requirement**: Store the password in Ansible Vault or an AAP credential-backed variable. Do not commit the literal value to the Ansible role or plaintext variable files.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, database connection strings, TLS certificate references, `.pem` files, `.key` files, or `.crt` files were identified in the supplied files.

## Checks for the Migration

**Files to verify**:
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:
- `memcached`: TCP `0.0.0.0:11211`
- `memcached`: UDP `0.0.0.0:11211`
- `redis-6379`: TCP port `6379`
- Unix sockets: None specified

**Templates rendered**:
- None; no Chef templates are present in the supplied execution tree

**Configuration edits to verify**:
- `/etc/redis/6379.conf` no longer contains:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

```bash
# Memcached service status
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Memcached TCP endpoint
ss -tlnp | grep ':11211'
printf 'version\r\n' | nc -w 2 127.0.0.1 11211

# Memcached UDP endpoint
ss -ulnp | grep ':11211'

# Memcached configuration
systemctl cat memcached
ps -ef | grep '[m]emcached'

# Verify Memcached directories and permissions
ls -ld /var/log/memcached /var/run/memcached
stat -c '%U:%G %a %n' /var/log/memcached /var/run/memcached

# Redis service discovery; select the unit corresponding to redis-6379
systemctl list-unit-files | grep -E 'redis|redis-server'
systemctl list-units --type=service | grep -E 'redis|redis-server'

# Redis service status after identifying the unit
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Use the Vault- or AAP-provided password, not the literal source password
ss -tlnp | grep ':6379'
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server

# Redis configuration and cleanup validation
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Redis log and PID directories
ls -ld /var/log/redis /run/redis
stat -c '%U:%G %a %n' /var/log/redis

# Service logs; substitute redis-server if that is the discovered unit name
journalctl -u redis --no-pager -n 100
journalctl -u memcached --no-pager -n 100
```

Expected results:

- `memcached` is active and enabled.
- Memcached listens on TCP and UDP port `11211` at `0.0.0.0`.
- Memcached uses 64 MB of memory, 1,024 maximum connections, maximum object size `1m`, and ULimit `1024`.
- `/var/log/memcached` and `/var/run/memcached` exist with mode `0755` and dependency-defined ownership.
- `redis-6379` is active and enabled using port `6379`.
- Redis authentication succeeds with the protected migration credential.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- `/run/redis` exists and is usable for the Redis PID file.
- `/etc/redis/6379.conf` contains port `6379`, uses the migrated authentication secret, and contains none of the five removed directives.
- Redis and Memcached logs contain no startup, authentication, permission, or configuration parsing errors.