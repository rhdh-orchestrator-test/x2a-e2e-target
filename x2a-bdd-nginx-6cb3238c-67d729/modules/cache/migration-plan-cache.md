---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis cache instance on TCP port `6379` with authentication enabled and password `redis_secure_password_123`, creates `/var/log/redis`, and removes selected replication-related directives from `/etc/redis/6379.conf`. The recipe also attempts to include `memcached`, `redisio`, and `redisio::enable`, but those dependency recipes are missing from the supplied execution tree. Consequently, package names, service names, user creation, Redis data paths, and Memcached settings must be verified from the dependency cookbooks before implementation. The Redis password must be migrated to Ansible Vault and rotated because it is stored in plaintext in the Chef recipe.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Authenticated Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config:
    - `port`: `6379`
    - `requirepass`: `redis_secure_password_123`
    - `replicaservestaledata`: unset/`nil`
    - Log directory: `/var/log/redis`
    - Log directory owner: `redis`
    - Log directory group: `redis`
    - Log directory mode: `0755`
    - Recursive directory creation: enabled
    - The following directives are removed from the generated configuration when present:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`

**Memcached**: The metadata declares the `memcached` cookbook as a dependency, and the default recipe attempts to include it. The execution tree reports `memcached Recipe file not found`. No Memcached package, port, configuration path, service name, or instance-specific settings can be confirmed from the supplied cookbook. Memcached tasks must not be added until the dependency cookbook is inspected.

There are no collection iterations in the supplied execution tree. The Redis server collection contains exactly one configured item: the Redis server on port `6379`.

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

The following dependency recipe paths are referenced but missing from the execution tree:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - The execution tree reports `memcached Recipe file not found`.
   - No Memcached installation, configuration, or service behavior can be inferred.
   - Do not assume a Memcached package or service name.

2. **Redis server attribute assignment** (`cookbooks/cache/recipes/default.rb`):
   - Assigns exactly one Redis server definition to `node['redisio']['servers']`.
   - Configures the Redis server on port `6379`.
   - Enables authentication using `requirepass`.
   - Sets the password to `redis_secure_password_123` in the source recipe.
   - Sets `replicaservestaledata` to `nil`.
   - No replica, Sentinel, cluster, persistence, or additional Redis settings are shown.
   - The Ansible implementation must store the password in an Ansible Vault-encrypted variable.

3. **Directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Uses owner `redis`, group `redis`, and mode `0755`.
   - Enables recursive creation.
   - The visible recipe does not create the `redis` user or group; that behavior may belong to the missing `redisio` dependency.

4. **`redisio` recipe include** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `redisio` recipe.
   - The execution tree reports `redisio Recipe file not found`.
   - Redis package names, package versions, user and group creation, service name, configuration generation, data directory, persistence settings, and startup behavior are unavailable from the visible cookbook.
   - These values must be obtained from the actual `redisio` cookbook or an approved Ansible Redis role.

5. **`fix_redis_config` Ruby block** (`cookbooks/cache/recipes/default.rb`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Does nothing when the file is absent.
   - Reads the complete file when it exists.
   - Removes complete lines beginning with `replica-serve-stale-data`.
   - Removes complete lines beginning with `replica-read-only`.
   - Removes complete lines beginning with `repl-ping-replica-period`.
   - Removes complete lines beginning with `client-output-buffer-limit`.
   - Removes complete lines beginning with `replica-priority`.
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Declares no explicit service restart or reload notification.
   - Ansible can implement this behavior with `ansible.builtin.replace`; a restart handler should only be added if required by the approved Ansible implementation.

6. **`redisio::enable` recipe include** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `redisio::enable` recipe.
   - The execution tree reports `redisio::enable Recipe file not found`.
   - The source cookbook intends to enable Redis at boot, but the service name and implementation are unavailable.
   - Enable the service only after confirming the actual Redis service name from the dependency implementation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package resources appear in the visible `cache::default` recipe.
- Package names and versions cannot be determined from the supplied execution tree.
- Package installation may be performed by the missing `memcached` and `redisio` recipes.
- Do not invent package names or versions.

**Service dependencies**:

- Redis enablement is attempted through the missing `redisio::enable` recipe.
- No concrete Redis systemd service name is available.
- Memcached service management is unavailable because the `memcached` recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file.

**Source**:

- **Provider**: Hardcoded in Chef attribute assignment
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value in the Chef recipe
- **Usage context**: Redis client authentication for the Redis server listening on port `6379`
- **Ansible migration recommendation**:
  - Store the password in an Ansible Vault-encrypted variable.
  - Render it into the Redis configuration with restrictive permissions.
  - Use `no_log: true` when the password is passed directly to an Ansible module or command.
  - Rotate the password during migration because it is present in source code.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, database connection strings, or additional credentials were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

The Redis data directory and exact Redis log file are not specified in the visible recipe and must be confirmed from the missing `redisio` implementation.

**Service endpoints to check**:

- Redis TCP port `6379`
- No Redis Unix socket specified
- No Memcached port available from the supplied files

**Templates rendered**:

- None; render count: `0`

**Static files deployed**:

- None; deployment count: `0`

**Configuration transformations to verify**:

The following directives must not remain in `/etc/redis/6379.conf` after the workaround:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Confirm the Redis service name from the redisio implementation before running these commands.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
```

### Redis server on port 6379

```bash
# Confirm that Redis is listening on the configured port.
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'

# Confirm that the Redis configuration file exists.
test -f /etc/redis/6379.conf

# Authenticated connectivity check.
# Supply the migrated password securely rather than committing it to shell history.
redis-cli -p 6379 -a '<REDIS_PASSWORD>' PING
# Expected response: PONG

# Verify Redis server information.
redis-cli -p 6379 -a '<REDIS_PASSWORD>' INFO server

# Verify that authentication is required.
redis-cli -p 6379 PING
# Expected result: authentication error or NOAUTH response

# Verify the configured port.
redis-cli -p 6379 -a '<REDIS_PASSWORD>' CONFIG GET port
```

### Verify removed Redis directives

```bash
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

Expected result: no matching output.

### Verify the Redis log directory

```bash
stat -c '%A %U %G %n' /var/log/redis
```

Expected values:

- Permissions: `drwxr-xr-x`
- Owner: `redis`
- Group: `redis`
- Path: `/var/log/redis`

### Check Redis logs

The visible cookbook does not specify the exact Redis log file. Identify the configured destination:

```bash
grep -nE '^(logfile|syslog-enabled|syslog-ident)' /etc/redis/6379.conf
```

Then inspect the resulting log file or service journal:

```bash
journalctl -u <redis-service-name> --no-pager -n 100
```

### Memcached dependency validation

The supplied cookbook does not provide a Memcached package, port, configuration path, or service name. Do not run Memcached validation commands until the missing `memcached` recipe has been inspected and its service details have been confirmed.