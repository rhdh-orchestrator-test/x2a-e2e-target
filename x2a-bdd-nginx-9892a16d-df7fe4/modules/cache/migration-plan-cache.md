---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The locally available recipe creates `/var/log/redis`, configures one Redis instance named `redis-6379` on port `6379` with password authentication, removes five replication-related directive families from `/etc/redis/6379.conf`, and enables Redis through `redisio::enable`. The Memcached dependency is requested but its recipe is unavailable, so its package, service, port, configuration path, and log path must be inspected before migration. The Redis password is currently hardcoded and must be migrated to Ansible Vault or an approved secret backend.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Password authentication enabled through `requirepass`; `replicaservestaledata` is `nil`; five replication-related directive families are removed after the Redis configuration is generated
  - Log Directory: `/var/log/redis`
  - Log Directory Ownership: `redis:redis`
  - Log Directory Mode: `0755`

- **memcached**: Memcached service requested through the external `memcached` cookbook
  - Location/Path: Not specified; dependency recipe unavailable
  - Port/Socket: Not specified
  - Key Config: Package, service name, port, bind address, configuration path, log path, and authentication settings must be obtained from the dependency cookbook before implementation

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are shown in the execution tree.

**Templates:**
```text
```

No template files are shown in the execution tree.

**Attributes:**
```text
```

No attribute files are shown in the execution tree. The Redis server configuration is assigned directly inside `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Assigns one Redis server configuration to `node['redisio']['servers']`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - Removes selected directive lines from `/etc/redis/6379.conf` when the file exists.
   - Includes the external `redisio::enable` recipe.

   **Redis configuration assigned by the recipe:**
   - Instance: `redis-6379`
   - Port: `6379`
   - `requirepass`: currently hardcoded as `redis_secure_password_123`; migrate this value to Ansible Vault or another approved secret backend.
   - `replicaservestaledata`: `nil`

   **Resource operations:**
   - `directory[/var/log/redis]`
     - Creates `/var/log/redis` recursively.
     - Sets ownership to `redis:redis`.
     - Sets mode to `0755`.
   - `ruby_block[fix_redis_config]`
     - Checks whether `/etc/redis/6379.conf` exists.
     - Reads the complete file when present.
     - Removes complete lines beginning with:
       - `replica-serve-stale-data`
       - `replica-read-only`
       - `repl-ping-replica-period`
       - `client-output-buffer-limit`
       - `replica-priority`
     - Writes the modified content back to `/etc/redis/6379.conf`.
     - Does nothing when the configuration file does not exist.

   **Included external recipes:**
   - `memcached`
     - Requested by `include_recipe 'memcached'`.
     - The dependency recipe is not present in the supplied execution tree.
     - Do not invent package, service, configuration, port, or log details.
   - `redisio`
     - Requested by `include_recipe 'redisio'`.
     - The dependency recipe is not present in the supplied execution tree.
     - It is expected to consume the Redis server configuration for instance `redis-6379`.
   - `redisio::enable`
     - Requested after the Redis configuration changes.
     - Intended to enable Redis at boot.
     - The exact service name and service implementation are unavailable locally.

   **Ansible migration behavior:**
   - Represent the Redis configuration as one explicit `redis_instances` item named `redis-6379`.
   - Store the Redis password in Ansible Vault or an approved secret-management system.
   - Use `ansible.builtin.file` for `/var/log/redis`.
   - Use `ansible.builtin.replace` operations against `/etc/redis/6379.conf` to remove the five directive families, conditional on the file existing.
   - Notify a Redis restart or reload only after the `redisio` dependency confirms the service name and reload support.
   - Do not replace the complete Redis configuration unless the dependency cookbook is intentionally being reimplemented.
   - Inspect the external `memcached` and `redisio` cookbooks before adding package or service tasks.

   **Resource summary:**
   - `directory`: 1
   - `ruby_block`: 1
   - `include_recipe`: 3
     - `memcached`
     - `redisio`
     - `redisio::enable`
   - No local package, service, template, file, or group resources are shown.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint shown

**System package dependencies**:
- No package resources are present in the locally available recipe.
- No package names are verified from the supplied files.
- Package names for Memcached and Redis must be obtained from the external dependency recipes before adding Ansible package tasks.

**Service dependencies**:
- Redis is expected to be enabled by `redisio::enable`.
- The Redis systemd service name is not available in the supplied files.
- Memcached service behavior and service name are unavailable because the referenced recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected
  - **Secret name**: Redis authentication password

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Source line**: Redis server collection assignment, line 8 of the recipe
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication through the Redis `requirepass` configuration
- **Ansible migration**:
  - Store the value in Ansible Vault or an approved secret-management system.
  - Reference it from the Redis configuration template or module variable.
  - Do not commit the plaintext value to the Ansible repository.
  - Do not place the password directly on a command line during validation.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database connection strings, or API tokens were detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis/`
- Redis data directory: not specified
- Redis log file: not specified
- Memcached configuration path: not specified
- Memcached log path: not specified

**Service endpoints to check**:
- **redis-6379**: TCP port `6379`
- **redis-6379**: Unix socket not specified
- **memcached**: Port not specified until the dependency cookbook is inspected
- Network bind addresses: not specified

**Templates rendered**:
- None shown in the execution tree
- Render count: `0`

**Configuration changes to verify**:
- Redis instance `redis-6379` listens on port `6379`.
- Redis password authentication is enabled.
- `/etc/redis/6379.conf` does not contain lines beginning with:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- `/var/log/redis` exists with ownership `redis:redis` and mode `0755`.
- Memcached configuration and endpoint details remain pending dependency inspection.

## Pre-flight checks

```bash
# Verify the locally migrated recipe source
test -f cookbooks/cache/recipes/default.rb

# Verify the Redis configuration file for instance redis-6379
test -f /etc/redis/6379.conf

# Verify the Redis log directory for instance redis-6379
stat -c '%U:%G %a %n' /var/log/redis
# Expected: redis:redis 755 /var/log/redis

# Verify Redis is listening for instance redis-6379
ss -tlnp | grep ':6379'
# Expected: a Redis listener on TCP port 6379

# Check Redis connectivity using the vaulted password for instance redis-6379
REDISCLI_AUTH='<retrieve-from-approved-secret-store>' \
  redis-cli -h 127.0.0.1 -p 6379 PING
# Expected: PONG

# Verify authentication is required for instance redis-6379
redis-cli -h 127.0.0.1 -p 6379 PING
# Expected: an authentication error if unauthenticated access is disabled

# Check Redis server information for instance redis-6379
REDISCLI_AUTH='<retrieve-from-approved-secret-store>' \
  redis-cli -h 127.0.0.1 -p 6379 INFO server
# Expected: Redis server information including the running version

# Verify the five removed directive families for instance redis-6379
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected: no output

# Validate the configured Redis authentication for instance redis-6379
REDISCLI_AUTH='<retrieve-from-approved-secret-store>' \
  redis-cli -h 127.0.0.1 -p 6379 CONFIG GET requirepass
# Expected: the configured password or a masked/secured representation,
# depending on the Redis version and client behavior

# Check the Redis service for instance redis-6379
systemctl status <redis-service-name>
# Replace <redis-service-name> with the service name confirmed from redisio.

# Review Redis logs for instance redis-6379
journalctl -u <redis-service-name> --no-pager -n 100
# Replace <redis-service-name> with the service name confirmed from redisio.

# Memcached instance validation is pending dependency inspection.
# Before adding Memcached checks, identify its package, service name,
# listening port, bind address, configuration path, log path, and any
# authentication or SASL settings from the external memcached cookbook.
```