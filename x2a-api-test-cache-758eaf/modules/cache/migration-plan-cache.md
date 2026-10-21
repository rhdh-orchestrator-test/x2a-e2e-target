---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis instance on port `6379`, with authentication enabled and configuration stored at `/etc/redis/6379.conf`. It creates `/var/log/redis`, removes selected replication and client buffer directives from the Redis configuration, and attempts to include the `memcached`, `redisio`, and `redisio::enable` recipes. Those dependency recipes are unavailable in the analyzed execution tree, so package names, exact service names, and dependency-managed configuration cannot be confirmed from this cookbook.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is set to the hardcoded value `redis_secure_password_123`; `replicaservestaledata` is `nil`
  - Log directory: `/var/log/redis`
  - Post-processing: Removes selected replication and client buffer directives from the generated configuration
  - Intended service management: `redisio::enable`, but the recipe and exact service name are unavailable

**Memcached**: The cookbook attempts to include the `memcached` recipe, but the recipe file is unavailable. No Memcached instance, package, port, configuration file, or service resource can be confirmed from the analyzed execution flow.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

The cookbook metadata file was inspected for service description and dependencies, but it is not an executable recipe, provider, template, attribute, or deployed static file and is therefore omitted from the migration file list.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the unavailable `memcached` recipe.
   - Assigns one Redis server entry to `node['redisio']['servers']`.
   - Configures the Redis instance on port `6379`.
   - Sets `requirepass` to `redis_secure_password_123`.
   - Sets `replicaservestaledata` to `nil`.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Attempts to include the unavailable `redisio` recipe, which is expected to install and configure Redis.
   - Executes `ruby_block[fix_redis_config]`.
   - Attempts to include the unavailable `redisio::enable` recipe.

   **Attempted dependency includes:**
   - `memcached`: Recipe file not found. Its package, configuration, and service resources are unavailable.
   - `redisio`: Recipe file not found. Its package names, configuration template, service name, user creation, and startup behavior are unavailable.
   - `redisio::enable`: Recipe file not found. Its exact service-management behavior is unavailable.

   **Redis server collection:**
   ```ruby
   node.default['redisio']['servers'] = [
     {
       'port' => '6379',
       'requirepass' => 'redis_secure_password_123',
       'replicaservestaledata' => nil,
     }
   ]
   ```

   **Resources:**
   - `directory[/var/log/redis]`
     - Path: `/var/log/redis`
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation: enabled
   - `ruby_block[fix_redis_config]`
     - Operates on `/etc/redis/6379.conf`.
     - Does nothing if the file does not exist.
     - Reads the complete file and writes the modified content back to the same path.
     - Removes complete lines beginning with:
       - `replica-serve-stale-data`
       - `replica-read-only`
       - `repl-ping-replica-period`
       - `client-output-buffer-limit`
       - `replica-priority`

   **Configuration cleanup patterns:**
   ```text
   /^replica-serve-stale-data.*$/
   /^replica-read-only.*$/
   /^repl-ping-replica-period.*$/
   /^client-output-buffer-limit.*$/
   /^replica-priority.*$/
   ```

   **Iterations:** No `.each` loops are present. The Redis server collection contains one explicit instance: Redis on port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`; recipe unavailable
- `redisio`, no version constraint; recipe unavailable
- `redisio::enable`; recipe unavailable

**System package dependencies**: None verified. No package resources are present in the analyzed recipe, and the dependency recipes are unavailable. Package names such as `redis-server` or `memcached` must not be treated as confirmed dependencies.

**Service dependencies**: Redis service management is intended through `redisio::enable`, but the exact service name and service resource are unavailable. Memcached service management cannot be confirmed.

## Credentials

**Detection Summary**: 1 hardcoded credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext recipe value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the Redis instance on port `6379`
- **Ansible handling**: Replace the plaintext value with an Ansible Vault variable such as `redis_password`

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, environment-variable secret, TLS certificate, private key, database connection string, or external secret-manager reference was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis server on port `6379`
- Unix sockets: none specified
- Network bind address: not specified

**Templates rendered**:

- None
- Render count: `0`

**Configuration directives to verify for Redis on port 6379**:

The following directives must not be present after `fix_redis_config` runs:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks:

```bash
# Verify the Redis configuration for the Redis instance on port 6379
test -f /etc/redis/6379.conf

grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Confirm that unwanted directives were removed from Redis on port 6379
! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Verify the Redis log directory for the Redis instance on port 6379
stat -c '%A %U:%G %n' /var/log/redis
# Expected: permissions equivalent to 0755 and owner/group redis:redis

# Verify the Redis service.
# The exact service name is unavailable and must be confirmed from the migrated Redis dependency.
systemctl list-unit-files | grep -E '^redis'
systemctl status redis --no-pager
systemctl is-enabled redis

# Confirm that Redis on port 6379 is listening
ss -ltnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Unauthenticated access should be rejected when authentication is enabled
redis-cli -p 6379 PING
# Expected: authentication error

# Authenticated health check for Redis on port 6379
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 PING
# Expected: PONG

# Redis instance information
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 INFO server
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 INFO replication

# Basic cache write/read/delete test for Redis on port 6379
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 SET migration_health_check ok
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 GET migration_health_check
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 DEL migration_health_check

# Redis service logs
journalctl -u redis --no-pager -n 100
ls -lah /var/log/redis
```

The value of `REDIS_PASSWORD` must come from the Ansible Vault-backed variable. Do not place the plaintext Chef password in shell history, task output, or a committed Ansible variable file.