---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis instance on port `6379` and references Memcached through an external dependency. The local recipe creates `/var/log/redis`, includes the `redisio` and `redisio::enable` dependency recipes, and removes five replication-related directives from `/etc/redis/6379.conf`. Redis authentication currently uses the hardcoded password `redis_secure_password_123`, which must be migrated to Ansible Vault or an approved AAP credential. The supplied execution tree does not include the `memcached`, `redisio`, or `redisio::enable` implementations, so their package names, templates, service names, ports, and startup behavior require dependency-cookbook inspection before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server configured through `node['redisio']['servers']`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is set to `redis_secure_password_123`; `replicaservestaledata` is `nil`
  - Log Directory: `/var/log/redis`
  - Log Directory Owner/Group: `redis:redis`
  - Log Directory Mode: `0755`
  - Cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`

- **Memcached dependency instance**: Memcached referenced through the external `memcached` recipe
  - Location/Path: Not declared in the supplied cookbook
  - Port/Socket: Not declared in the supplied cookbook
  - Key Config: Package, service, configuration path, listening address, port, authentication, and memory limits require inspection of the `memcached` dependency cookbook
  - Migration Status: Do not infer package, service, configuration, or endpoint values from this cookbook alone

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
None
```

**Templates:**
```text
None
```

**Attributes:**
```text
None
```

**Files:**
```text
None
```

The metadata file was inspected to identify cookbook dependencies, but it is not included in the execution-tree file list and is therefore not listed as an executable migration file.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe. The recipe is not present in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe. The recipe is not present in the supplied execution tree.
   - Executes `ruby_block[fix_redis_config]` to modify `/etc/redis/6379.conf` when the file exists.
   - Includes the external `redisio::enable` recipe. The recipe is not present in the supplied execution tree.
   - Defines one Redis server entry:
     - Name: Redis instance on port `6379`
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`

2. **`memcached`** (`memcached` dependency recipe, implementation not supplied):
   - The local recipe invokes `include_recipe 'memcached'`.
   - Retrieve the dependency cookbook before implementing Ansible tasks.
   - Verify the Memcached package name.
   - Verify the Memcached service name.
   - Verify the configuration file path.
   - Verify the listening address and port.
   - Verify authentication, memory limits, enablement, and startup behavior.
   - No local templates or resources from this recipe are available for migration.

3. **Redis log directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Uses one `directory` resource.
   - Sets `owner: redis`.
   - Sets `group: redis`.
   - Sets `mode: '0755'`.
   - Sets `recursive: true`.
   - The Ansible equivalent is `ansible.builtin.file` with `state: directory`.
   - This task runs before the Redis dependency configuration.

4. **`redisio`** (`redisio` dependency recipe, implementation not supplied):
   - The local recipe invokes `include_recipe 'redisio'`.
   - The dependency is expected to consume the single Redis server definition on port `6379`.
   - Obtain and verify the Redis package name.
   - Obtain and verify Redis user and group creation.
   - Obtain and verify configuration template paths.
   - Obtain and verify service unit names.
   - Obtain and verify data directory and log file paths.
   - Obtain and verify service startup behavior.
   - No local templates or resources from this recipe are available for migration.

5. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Targets `/etc/redis/6379.conf`.
   - Performs no action if the configuration file does not exist.
   - Removes complete lines beginning with `replica-serve-stale-data`.
   - Removes complete lines beginning with `replica-read-only`.
   - Removes complete lines beginning with `repl-ping-replica-period`.
   - Removes complete lines beginning with `client-output-buffer-limit`.
   - Removes complete lines beginning with `replica-priority`.
   - Runs after the `redisio` configuration has generated the Redis configuration file.
   - Uses one `ruby_block` resource.
   - The local recipe does not declare a service restart or reload notification.
   - The Ansible equivalent should use `ansible.builtin.replace` or another controlled line-removal implementation.

6. **`redisio::enable`** (`redisio/recipes/enable.rb`, dependency implementation not supplied):
   - The local recipe invokes `include_recipe 'redisio::enable'`.
   - Verify the exact Redis service name.
   - Verify whether the Redis service is enabled at boot.
   - Verify whether the Redis service is started immediately.
   - Verify whether the service is managed separately for port `6379`.
   - Do not invent a service name until the dependency cookbook is inspected.

## Dependencies

**External cookbook dependencies**:

- `memcached`, constraint `~> 6.0`
- `redisio`, no version constraint
- `redisio::enable`, provided by the `redisio` cookbook

**System package dependencies**:

- No package is installed directly by the supplied local recipe.
- No package name is available or verified from the supplied execution tree.
- Package names must be obtained from the `memcached` and `redisio` dependency implementations before creating Ansible package tasks.

**Service dependencies**:

- Memcached service behavior is defined by the missing `memcached` recipe.
- Redis configuration behavior is defined by the missing `redisio` recipe.
- Redis service enablement is intended to be defined by the missing `redisio::enable` recipe.
- The local recipe directly references `/etc/redis/6379.conf`.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected
  - **Source file**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute value
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`
- **Migration handling**:
  - Replace the literal with an Ansible Vault variable such as `redis_password`.
  - Do not store the password in `defaults/main.yml`, plaintext task arguments, or generated documentation.
  - Use the vaulted value when rendering or configuring Redis.
  - Apply `no_log: true` to tasks that could expose the password.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, API keys, or database connection strings were detected in the supplied recipe.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- Redis data directory supplied by the `redisio` dependency
- Redis log file supplied by the `redisio` dependency
- Memcached configuration file supplied by the `memcached` dependency

**Service endpoints to check**:

- Redis TCP port `6379`
- Memcached endpoint: port not specified in the supplied cookbook
- Unix sockets: none specified
- Network bind address: not specified

**Configuration directives to verify in `/etc/redis/6379.conf`**:

- Redis listens on port `6379`.
- Redis password authentication is enabled.
- `replica-serve-stale-data` is absent after cleanup.
- `replica-read-only` is absent after cleanup.
- `repl-ping-replica-period` is absent after cleanup.
- `client-output-buffer-limit` is absent after cleanup.
- `replica-priority` is absent after cleanup.

**Templates rendered**:

- Supplied cookbook: `0`
- `memcached` dependency: render count not available
- `redisio` dependency: render count not available
- Dependency templates require separate inspection.

## Pre-flight checks:

```bash
# Redis service checks.
# Replace <redis-service-name> with the verified service name from redisio.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>

# Redis configuration file.
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Confirm Redis cleanup directives are absent.
! grep -E '^replica-serve-stale-data' /etc/redis/6379.conf
! grep -E '^replica-read-only' /etc/redis/6379.conf
! grep -E '^repl-ping-replica-period' /etc/redis/6379.conf
! grep -E '^client-output-buffer-limit' /etc/redis/6379.conf
! grep -E '^replica-priority' /etc/redis/6379.conf

# Confirm Redis is listening on port 6379.
ss -tlnp | grep ':6379'

# Redis authentication and connectivity.
# Supply the vaulted password through a protected environment or interactive mechanism.
export REDISCLI_AUTH='<redis-password-from-vault>'
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server
redis-cli -p 6379 CONFIG GET port

# Expected Redis results:
# PING returns PONG.
# CONFIG GET port reports 6379.
# INFO server returns server information without an authentication error.

# Redis log directory.
stat -c '%U %G %a %n' /var/log/redis
# Expected:
# redis redis 755 /var/log/redis
ls -la /var/log/redis

# Redis logs.
# Replace <redis-log-file> with the verified path from redisio.
test -f <redis-log-file>
tail -n 100 <redis-log-file>
grep -E 'WARNING|ERR|MISCONF|OOM|Authentication' <redis-log-file>

# Redis journal.
journalctl -u <redis-service-name> --no-pager -n 100

# Memcached service checks.
# Replace placeholders with values verified from the memcached dependency.
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
ss -tlnp | grep ':<memcached-port>'

# Memcached configuration.
# Replace <memcached-config-file> with the verified dependency path.
test -f <memcached-config-file>
```

