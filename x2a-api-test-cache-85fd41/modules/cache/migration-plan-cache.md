---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the `memcached` Memcached instance and the `redis-6379` Redis instance on port `6379`. Memcached uses 64 MB of memory, TCP and UDP port `11211`, wildcard binding, and a maximum of 1024 connections. Redis requires the hardcoded password `redis_secure_password_123`, uses `/run/redis` for its PID directory, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and is enabled and started. The referenced `redisio` recipes are missing, so the Ansible migration must explicitly implement Redis package installation, configuration, directory management, and service behavior.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached cache service
  - Package: `memcached`
  - Version: `nil`, using the platform package manager's default version
  - Location/Path: `/var/run/memcached` runtime directory; `/var/log/memcached` log directory
  - Port/Socket: TCP `11211`; UDP `11211`; listen address `0.0.0.0`
  - Key Config: 64 MB memory, maximum 1024 connections, maximum object size `1m`, ulimit `1024`, start and enable actions
  - Worker threads: Receives `node['memcached']['threads']`; no default is present in the supplied attributes
  - Experimental options: Empty list
  - Extra CLI options: Empty list
  - Service user: Receives `service_user`; the resolved username is not present in the supplied source

- **`redis-6379`**: Redis cache service
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket is referenced
  - Key Config: Authentication required with password `redis_secure_password_123`; replica stale-data setting unset; Redis log directory owned by `redis:redis` with mode `0755`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` directives when present
  - Service behavior: Intended to be installed, configured, enabled, and started by the missing `redisio` recipes

## File Structure

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider path was supplied for `memcached_instance`, and no `redisio` provider file was present in the directory listing.

**Templates:**
```text
```

No templates are rendered by the supplied reachable execution flow.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The following files are present in the repository catalog but are not part of the selected cookbook's reachable execution flow and must not be migrated as cache module inputs:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

All listed `data_bags/*` files are also outside the cache cookbook's reachable execution flow.

## Module Explanation

The cookbook performs operations in this order:

1. **Cache entry recipe** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` recipe.
   - Assigns one Redis server configuration for port `6379`.
   - Sets Redis authentication to `redis_secure_password_123`.
   - Sets `replicaservestaledata` to `nil`.
   - Includes the missing `redisio` installation and configuration recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` when the file exists.
   - Includes the missing `redisio::enable` recipe to enable and start Redis.

   Redis configuration values:
   - Port: `6379`
   - Password: `redis_secure_password_123`
   - PID directory: `/run/redis`
   - Replica stale-data setting: unset or disabled

2. **Memcached dependency recipe** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates the `memcached_instance[memcached]` custom resource.
   - Installs or configures the `memcached` package through the custom resource provider.
   - Configures 64 MB memory.
   - Configures TCP port `11211` and UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Sets maximum object size to `1m`.
   - Passes `node['memcached']['threads']`; no default value is supplied in the analyzed attributes file.
   - Passes empty experimental and extra CLI option lists.
   - Sets ulimit to `1024`.
   - Starts and enables the Memcached service.
   - Uses `/var/log/memcached` and `/var/run/memcached` as the log and runtime directories.
   - Receives `service_user`; the exact resolved username is unavailable, so the Ansible role must use the target platform's standard Memcached account or an exposed variable.

3. **Missing Redis installation recipe** (`redisio/recipes/default.rb`, source file unavailable):
   - The execution tree reports `redisio Recipe file not found`.
   - The Ansible role must install the Redis package appropriate to the target platform.
   - The role must create or manage `/etc/redis/6379.conf`.
   - The role must configure Redis on port `6379` with password authentication.
   - The role must use `/run/redis` as the PID directory.
   - The Redis service account must exist before Redis-owned directories are created.
   - The exact Redis package name and systemd unit name cannot be claimed from the supplied Chef source.

4. **Missing Redis enable recipe** (`redisio/recipes/enable.rb`, source file unavailable):
   - The execution tree reports `redisio::enable Recipe file not found`.
   - The intended behavior is to enable Redis at boot and start the Redis service.
   - The Ansible role must use the platform-resolved Redis service name.

5. **Redis configuration correction** (`cookbooks/cache/recipes/default.rb`, `ruby_block[fix_redis_config]`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Removes complete lines matching:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Performs no action when the configuration file does not exist.
   - The Ansible implementation should use a deterministic template or controlled replacement task.
   - A Redis restart or reload should occur only when the active configuration changes.

There are no `.each` loops in the reachable execution flow. The Redis collection contains exactly one configured item: port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- `memcached`
- Redis package appropriate to the supported target distribution; the exact package name is not exposed because the `redisio` recipe is missing

**Service dependencies**:

- Memcached is started and enabled by `memcached_instance[memcached]`.
- Redis is intended to be started and enabled by the missing `redisio::enable` recipe.
- The exact Redis service unit name is not available in the source.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None; the value is assigned directly to the Redis configuration attribute

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Usage context**: Redis `requirepass` authentication for instance `redis-6379` on port `6379`
- **Ansible migration recommendation**: Store the value in Ansible Vault, preferably as `redis_password`, and avoid exposing it in task output

No data bags are referenced by the cache cookbook's reachable execution flow. The unrelated `nginx_secrets/site` data bag must not be used for the Redis password. No Chef Vault, encrypted data bag lookup, CyberArk integration, Conjur lookup, environment-variable secret reference, TLS certificate, private key, API token, or database connection credential was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `redis-6379`: TCP port `6379`
- Redis instance `redis-6379`: no Unix socket referenced
- Redis instance `redis-6379`: PID directory `/run/redis`

**Templates rendered**:

- None; zero templates are rendered by the supplied reachable execution flow.

**Resource summary**:

- `include_recipe`: `memcached`, `redisio`, `redisio::enable`
- `memcached_instance[memcached]`: 1
- `directory[/var/log/redis]`: 1
- `ruby_block[fix_redis_config]`: 1
- Redis server configuration entries: 1, for port `6379`

## Pre-flight checks:

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
pgrep -a memcached

# Verify Memcached TCP port 11211 and wildcard binding.
ss -ltnp | grep ':11211'

# Verify Memcached UDP port 11211 and wildcard binding.
ss -lunp | grep ':11211'

# Query Memcached over TCP.
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
# Expected output includes: VERSION

# Query Memcached statistics.
printf 'stats\r\n' | nc -w 2 127.0.0.1 11211
# Expected output includes: STAT

# Verify Memcached directories and permissions.
ls -ld /var/log/memcached
ls -ld /var/run/memcached
```

```bash
# Redis instance: redis-6379
# Use the platform-resolved Redis service unit if it is not named redis.
systemctl status redis
systemctl list-units --type=service | grep -i redis
systemctl is-enabled redis
systemctl is-active redis
pgrep -a redis

# Verify Redis TCP port 6379.
ss -ltnp | grep ':6379'

# Verify the Redis configuration file and required settings.
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|dir|pidfile)' /etc/redis/6379.conf

# Verify the Redis log and PID directories.
ls -ld /var/log/redis
ls -ld /run/redis

# Verify the targeted directives were removed.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected output: no matching lines, unless rewritten by the Redis package after startup.
```

```bash
# Validate Redis authentication for instance redis-6379.
REDISCLI_AUTH='redis_secure_password_123' redis-cli -p 6379 PING
# Expected output: PONG

REDISCLI_AUTH='redis_secure_password_123' redis-cli -p 6379 INFO server
# Expected output contains Redis server information

REDISCLI_AUTH='redis_secure_password_123' redis-cli -p 6379 SET migration_check cache-ok
# Expected output: OK

REDISCLI_AUTH='redis_secure_password_123' redis-cli -p 6379 GET migration_check
# Expected output: "cache-ok"

REDISCLI_AUTH='redis_secure_password_123' redis-cli -p 6379 DEL migration_check
# Expected output: (integer) 1
```

```bash
# Review service logs.
journalctl -u memcached --since "-10 minutes" --no-pager
journalctl -u redis --since "-10 minutes" --no-pager

# Verify Redis log directory ownership and permissions.
stat -c '%A %U:%G %n' /var/log/redis
# Expected: drwxr-xr-x redis:redis /var/log/redis

# Verify Memcached directories.
stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached
```

The final Ansible implementation must verify that:

- The `memcached` instance binds to `0.0.0.0:11211` with TCP and UDP enabled.
- The `memcached` instance uses 64 MB of memory and a maximum of 1024 connections.
- The `redis-6379` instance listens on port `6379`.
- Redis rejects unauthenticated commands.
- Redis accepts authenticated commands using the vaulted password.
- `/etc/redis/6379.conf` exists before configuration cleanup runs.
- Both `memcached` and `redis-6379` are enabled at boot and active after deployment.