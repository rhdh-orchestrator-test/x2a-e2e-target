---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a Redis cache instance on port `6379`, creates `/var/log/redis`, sets Redis authentication, removes selected replication directives from `/etc/redis/6379.conf`, and attempts to include Memcached and Redis dependency recipes. The available execution tree contains only `cookbooks/cache/recipes/default.rb`; the `memcached`, `redisio`, and `redisio::enable` recipes are referenced but unavailable. Redis credentials must be migrated to Ansible Vault or an approved external secret provider.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Log directory: `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config:
    - `requirepass`: `redis_secure_password_123` in the source Chef recipe; migrate this value to a protected secret
    - `replicaservestaledata`: `nil`
    - Redis configuration cleanup removes:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`

- **Memcached instance**: External Memcached service included by the recipe
  - Location/Path: Not determinable; the `memcached` dependency recipe is missing
  - Port/Socket: Not determinable from the supplied cookbook
  - Key Config: Package, service name, configuration path, listening port, authentication, memory settings, and enablement behavior must be obtained from the missing dependency cookbook or deployment requirements. Do not invent Memcached settings.

## File Structure

Only files shown in the supplied execution tree are included.

```text
Recipes:
cookbooks/cache/recipes/default.rb

Providers:

Templates:

Attributes:

Files:
```

The external recipes `memcached`, `redisio`, and `redisio::enable` are referenced by `include_recipe` but are not present in the supplied execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Assigns one Redis server configuration to `node.default['redisio']['servers']`:
     - Redis instance: port `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Includes the external `redisio` recipe to install and configure Redis using the assigned server attributes.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` with `ruby_block[fix_redis_config]`.
   - Includes the external `redisio::enable` recipe to enable and potentially start Redis.
   - Execution-tree status:
     - `memcached`: recipe not found
     - `redisio`: recipe not found
     - `redisio::enable`: recipe not found
   - Resources present in the supplied recipe:
     - `directory[/var/log/redis]`: 1
     - `ruby_block[fix_redis_config]`: 1

   **Memcached include:**
   - The recipe executes `include_recipe 'memcached'`.
   - The dependency must be resolved before claiming Memcached parity.
   - Confirm the Memcached package, service name, configuration path, listening port, authentication, memory settings, and service enablement behavior from the dependency implementation.

   **Redis attribute assignment:**
   - The recipe defines exactly one Redis server item:
     ```ruby
     {
       'port' => '6379',
       'requirepass' => 'redis_secure_password_123',
       'replicaservestaledata' => nil
     }
     ```
   - The Ansible implementation must define the Redis instance before the Redis installation and configuration role runs.
   - The password must be supplied from Ansible Vault or an approved external secret provider rather than hardcoded in production content.

   **Redis log directory:**
   - Creates `/var/log/redis`.
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled

   **Redis include:**
   - The recipe executes `include_recipe 'redisio'`.
   - The dependency recipe is unavailable, so its package name, service name, user and group creation, configuration template, binding behavior, and service-start behavior cannot be confirmed.
   - The migrated Redis role must create `/etc/redis/6379.conf`, because the later cleanup operation targets that exact path.

   **Redis configuration cleanup:**
   - Resource: `ruby_block[fix_redis_config]`
   - If `/etc/redis/6379.conf` exists, the block reads the file and removes complete lines matching:
     ```text
     ^replica-serve-stale-data.*$
     ^replica-read-only.*$
     ^repl-ping-replica-period.*$
     ^client-output-buffer-limit.*$
     ^replica-priority.*$
     ```
   - The modified file is written back to the same path.
   - The Ansible equivalent must:
     - Check for `/etc/redis/6379.conf`.
     - Remove lines beginning with `replica-serve-stale-data`.
     - Remove lines beginning with `replica-read-only`.
     - Remove lines beginning with `repl-ping-replica-period`.
     - Remove lines beginning with `client-output-buffer-limit`.
     - Remove lines beginning with `replica-priority`.
     - Preserve all other configuration lines.
     - Restart or reload Redis only when the file changes.
   - The Chef `ruby_block` does not explicitly notify or restart a service.

   **Redis enablement include:**
   - The recipe executes `include_recipe 'redisio::enable'`.
   - The dependency recipe is unavailable, so the exact Redis service resource and service name cannot be confirmed.
   - The Ansible implementation must enable and start the Redis service associated with the port `6379` configuration after validating the target service name.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No explicit `package` resources are present in the supplied recipe.
- Package names are delegated to the missing `memcached` and `redisio` dependency recipes and cannot be reliably determined from the supplied execution tree.

**Service dependencies**:

- Redis is intended to be enabled through the missing `redisio::enable` recipe.
- Memcached is intended to be configured through the missing `memcached` recipe.
- Exact service names cannot be confirmed from the available files.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None
  - **Path**: None

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded value
- **Value detected**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the Redis instance listening on TCP port `6379`

Store the migrated password in Ansible Vault or an approved external secret provider. Do not commit the plaintext value to role defaults, group variables, templates, or task files. Render the Redis `requirepass` directive from the protected variable and restrict access to generated configuration files containing the secret.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, database connection strings, or external secret-manager URLs were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Memcached instance: port not determinable until the missing `memcached` dependency is resolved
- Unix sockets: none referenced
- Network interface binding: not specified

**Templates rendered**:

- None. No templates are present or referenced in the supplied cookbook.
- Render count: `0`

**Resource summary**:

- `directory`: `1`
- `ruby_block`: `1`
- Included but unavailable recipes:
  - `memcached`
  - `redisio`
  - `redisio::enable`

## Pre-flight checks

```bash
# Redis instance on port 6379
# Replace <redis-service-name> only after confirming the service name
# provided by the missing redisio dependency.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>

# Verify Redis is listening on TCP port 6379
ss -tlnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Verify the Redis configuration file exists
test -f /etc/redis/6379.conf

# Verify the Redis configuration and cleanup targets
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# The five removed directives should not be present as active lines
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Validate Redis authentication using the migrated protected secret
REDISCLI_AUTH='<redis-password>' redis-cli -p 6379 PING

# Expected result:
# PONG

# Verify authentication is enforced
redis-cli -p 6379 PING

# Verify the Redis log directory
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis

# Expected result:
# drwxr-xr-x redis redis /var/log/redis

# Check Redis service logs
journalctl -u <redis-service-name> --no-pager -n 100
journalctl -u <redis-service-name> -f

# Validate the Redis configuration with the installed Redis binary
redis-server /etc/redis/6379.conf --test-memory 2

# Memcached instance
# Resolve the missing memcached dependency before running these checks.
# Confirm its actual service name and port from the dependency implementation.
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>
ss -tlnp | grep ':<memcached-port>'
```

The Memcached service name, port, configuration path, and runtime settings must not be assumed from this cookbook alone.