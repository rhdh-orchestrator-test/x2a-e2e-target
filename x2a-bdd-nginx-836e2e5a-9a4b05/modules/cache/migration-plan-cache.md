---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis cache instance on TCP port `6379`, with a hardcoded Redis password and a log directory at `/var/log/redis`. The recipe also includes Memcached and the `redisio` dependency cookbook, but their recipe files are absent from the supplied execution tree. It additionally attempts to enable Redis through `redisio::enable`. The Ansible migration must reproduce the visible Redis directory creation, Redis configuration values, configuration cleanup, and service enablement while separately resolving the missing dependency roles or collections. The Redis password must be migrated to Ansible Vault or another approved secret store.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`
  - Authentication: `requirepass` set to `redis_secure_password_123` in the Chef source; migrate this value to secure storage
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Replica-related setting: `replicaservestaledata` is explicitly set to `nil`
  - Post-configuration cleanup removes:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

Memcached is included by the recipe, but no Memcached instance attributes, package resources, port, configuration file, or service resource are present in the supplied execution tree. Its implementation is unavailable for direct migration from this cookbook path.

## File Structure

Only the following Ruby recipe file is shown in the supplied execution tree.

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

The supplied execution tree does not list `metadata.rb` as an executable recipe file, dependency recipe files, provider files, templates, attribute files, or static files.

Referenced dependency recipes reported as not found:

- `memcached` recipe file not found
- `redisio` recipe file not found
- `redisio::enable` recipe file not found

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` recipe before configuring Redis.
   - The `memcached` recipe is not present in the supplied execution tree.
   - Does not expose Memcached package, port, configuration, or service details.
   - Ansible must not invent Memcached settings from this cookbook alone.

   - Assigns one Redis server configuration to `node['redisio']['servers']`:
     - Redis instance name: port `6379`
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - The single collection item must be represented as one Redis instance in Ansible.

   - Creates `directory[/var/log/redis]`:
     - Destination: `/var/log/redis`
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation: enabled
   - Ansible equivalent: `ansible.builtin.file` with `state: directory`, owner `redis`, group `redis`, and mode `'0755'`.

   - Includes the `redisio` recipe.
   - The `redisio` recipe is not present in the supplied execution tree.
   - Its intended role is to configure the Redis server using the previously assigned Redis server collection.
   - The available cookbook does not expose the Redis package name, configuration template, service resource, or package-installation behavior.
   - These details must be supplied by the selected Ansible Redis role after confirming the target operating system and Redis implementation.

   - Executes `ruby_block[fix_redis_config]`:
     - Configuration path: `/etc/redis/6379.conf`
     - Checks whether the file exists.
     - Reads the complete file.
     - Removes complete lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Writes the modified content back to `/etc/redis/6379.conf`.
   - Ansible equivalent:
     - Use `ansible.builtin.replace` or an equivalent controlled line-removal strategy.
     - Run the cleanup after the Redis configuration task creates the file.
     - Preserve the Chef conditional behavior so a missing file does not fail the play unnecessarily.
     - Notify a Redis restart or reload only when the configuration changes, subject to the selected Redis role.

   - Includes the `redisio::enable` recipe.
   - The `redisio::enable` recipe is not present in the supplied execution tree.
   - Its intended role is to enable Redis at boot and potentially start the service.
   - Use the service name supplied by the selected Redis package or Ansible role; no exact systemd service name is visible in this cookbook.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint shown

**System package dependencies**:

- No `package` resources appear in the supplied execution tree.
- No package names are verified by this cookbook.
- The exact Memcached and Redis package names must be confirmed for the target operating system and selected Ansible roles before implementation.

**Service dependencies**:

- Redis service enablement is intended through the missing `redisio::enable` recipe.
- The exact Redis systemd service name is not present in the supplied execution tree.
- Memcached service management is unavailable because the `memcached` recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the Redis instance on TCP port `6379`
- **Ansible migration**: Store the password in Ansible Vault, an AAP credential, or an approved external secret provider. Render it into the Redis configuration without exposing it in task output.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, database connection strings, or secret-related attribute namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

The exact Redis data directory and log file are not shown in the supplied execution tree and must be obtained from the selected Redis package or Ansible role.

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Unix sockets: None detected
- Network interfaces: Not specified; do not assume a bind address from this cookbook

**Templates rendered**:

- None; render count: `0`

**Post-configuration transformations**:

- `/etc/redis/6379.conf` is modified by removing complete lines beginning with:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

Replace `<redis-service-name>` with the verified service name supplied by the selected Redis package or Ansible role. Do not place the Redis password directly in shell history in production; use a protected environment variable or another approved secret-handling method.

```bash
# Redis instance: TCP port 6379
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>

# Redis process verification
ps aux | grep '[r]edis'

# Redis endpoint verification
ss -tlnp | grep ':6379'

# Authenticated Redis health check
redis-cli -p 6379 -a '<REDIS_PASSWORD>' PING
# Expected result: PONG

# Authenticated Redis information check
redis-cli -p 6379 -a '<REDIS_PASSWORD>' INFO server
redis-cli -p 6379 -a '<REDIS_PASSWORD>' CONFIG GET requirepass

# Configuration file verification
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Verify Chef cleanup directives are absent
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected result: no matching lines

# Log directory verification for the Redis instance
stat -c '%A %U %G %n' /var/log/redis
# Expected result: mode 755, owner redis, group redis

# Redis service logs
journalctl -u <redis-service-name> --no-pager -n 100

# Authenticated connectivity and write/read test for port 6379
redis-cli -p 6379 -a '<REDIS_PASSWORD>' SET migration_check success
redis-cli -p 6379 -a '<REDIS_PASSWORD>' GET migration_check
# Expected result: success
redis-cli -p 6379 -a '<REDIS_PASSWORD>' DEL migration_check
```

Memcached-specific checks cannot be defined from the supplied cookbook because the `memcached` recipe is missing and no Memcached port or configuration is present in the execution tree.