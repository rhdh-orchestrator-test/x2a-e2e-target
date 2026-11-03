---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis instance on TCP port `6379`, with authentication enabled and a post-configuration cleanup that removes selected replication-related directives from `/etc/redis/6379.conf`. It also includes the external `memcached`, `redisio`, and `redisio::enable` recipes, but those recipe files are unavailable in the supplied execution tree. Redis password handling must be migrated to Ansible Vault, an AAP credential, or another protected secret source. Redis resource properties, dependency metadata, and detailed dependency behavior should be confirmed against the source cookbook before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Authenticated Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication is enabled through `requirepass`; `replicaservestaledata` is explicitly set to `nil`; selected replication-related directives are removed after Redis configuration
  - Password: The source plan identifies `redis_secure_password_123` as a hardcoded password. Do not migrate this literal into Ansible plaintext; use a protected variable such as `redis_password`.
  - Cleanup directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

- **Memcached instance**: Referenced through the external `memcached` recipe, but not defined in the supplied execution tree
  - Location/Path: Not available
  - Port/Socket: Not available
  - Key Config: Package, service name, configuration path, listening port, and runtime options require confirmation from the missing dependency cookbook
  - Migration status: Do not invent Memcached settings until the dependency implementation is obtained

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

No templates are shown in the execution tree.

**Attributes:**
```text
```

No attribute files are shown in the execution tree. The Redis server configuration is assigned directly in `recipes/default.rb`.

**Files:**
```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The supplied execution tree reports `memcached Recipe file not found`.
   - No Memcached package, service, port, configuration file, or runtime options can be established from the available files.
   - Preserve the dependency relationship only after the Memcached implementation is identified.

2. **`default` — Redis server configuration** (`cookbooks/cache/recipes/default.rb`):
   - Assigns one Redis server definition to `node['redisio']['servers']`.
   - Configured server name: Redis server on port `6379`.
   - Configured port: `6379`.
   - Configured authentication: `requirepass`, with the password supplied during migration through a protected variable such as `redis_password`.
   - Configured value: `replicaservestaledata` is `nil`.
   - No `.each` loop is shown; the configured collection contains one server definition and must be represented as one Redis instance in Ansible.

3. **`default` — Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis` before the RedisIO recipe is included.
   - The supplied plan identifies the intended properties as:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive: `true`
   - These properties should be confirmed against the detailed Chef resource analysis before being treated as mandatory.
   - Ansible equivalent: `ansible.builtin.file` with `state: directory`.

4. **`default` — RedisIO configuration** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The supplied execution tree reports `redisio Recipe file not found`.
   - The missing dependency implementation must be obtained to confirm:
     - Redis package name
     - Redis service name
     - Configuration template or generated configuration
     - Data directory
     - Installation provider
   - Redis dependency configuration occurs after `/var/log/redis` is created.

5. **`default` — Redis configuration cleanup** (`cookbooks/cache/recipes/default.rb`):
   - Executes `ruby_block[fix_redis_config]`.
   - Target file: `/etc/redis/6379.conf`.
   - The supplied plan describes the following behavior:
     - Check whether the file exists.
     - Perform no action when the file is absent.
     - Read the file when it exists.
     - Remove lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Write the modified content back to `/etc/redis/6379.conf`.
   - These exact target and regular-expression details should be confirmed against the detailed Ruby block analysis.
   - Ansible equivalent: preferably render the complete managed configuration without these directives; otherwise use carefully scoped `ansible.builtin.replace` tasks.
   - Run this cleanup after RedisIO configuration so the dependency recipe does not overwrite it.
   - No direct service restart or reload notification is shown. Determine whether a controlled Redis restart or reload is required after confirming RedisIO service behavior.

6. **`enable`** (`cookbooks/cache/recipes/default.rb`, through `redisio::enable`):
   - Includes the external `redisio::enable` recipe.
   - The supplied execution tree reports `redisio::enable Recipe file not found`.
   - This is the final operation in the shown recipe flow.
   - Confirm the exact Redis service name and enablement behavior before adding Ansible service-management tasks.

## Dependencies

**External cookbook dependencies**: `memcached` with reported constraint `~> 6.0`; `redisio` with no reported version constraint. Confirm both names and constraints in `metadata.rb`.

**System package dependencies**: No package resources or verified package names are available from the supplied execution tree. Do not invent Memcached or Redis package names.

**Service dependencies**:
- Redis service enablement is delegated to the missing `redisio::enable` recipe.
- Memcached service management is delegated to the missing `memcached` recipe.
- Exact service names cannot be established from the supplied files.

## Credentials

**Detection Summary**: 1 hardcoded Redis credential identified in 1 file; confirm against the source recipe and credential analysis.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`; migration variable `redis_password`
- **Literal value in source**: `redis_secure_password_123` as identified by the supplied plan; do not retain this value in Ansible plaintext
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded recipe value
- **Usage context**: Redis client authentication for the Redis server listening on TCP port `6379`
- **Migration storage**: Ansible Vault, an AAP credential, or an approved secret manager
- **Handling requirements**:
  - Do not expose the password in task names, debug output, generated logs, or unencrypted variable files.
  - Supply the value through a protected variable such as `redis_password`.

No additional credential types are established by the supplied execution tree. Claims regarding data bags, encrypted data bags, Chef Vault, environment-variable secrets, TLS keys, API tokens, or connection strings require confirmation from a complete credential analysis.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

The Redis data directory and dedicated Redis log file are not exposed by the supplied execution tree and require confirmation from the missing `redisio` implementation.

**Service endpoints to check**:
- Redis server on TCP port `6379`
- Memcached endpoint: not determinable from the supplied files
- Unix sockets: none shown

**Templates rendered**:
- None shown
- Render count: `0` confirmed templates in the supplied execution tree

**Additional verification**:
- Confirm the Redis bind address; none is specified in the supplied cookbook.
- Confirm package names and service names from the missing dependency cookbooks.
- Confirm `/var/log/redis` ownership, group, mode, and recursive behavior from the detailed resource analysis.
- Confirm the Redis password and cleanup behavior against the source recipe.

## Pre-flight checks:
```bash
# Redis instance: Redis server on port 6379

# Verify that the Redis configuration exists
test -f /etc/redis/6379.conf

# Verify the Redis log directory
stat -c '%A %U:%G %n' /var/log/redis
# Expected if confirmed from the Chef resource:
# directory owned by redis:redis with mode equivalent to 0755

# Identify the Redis service name if the redisio::enable implementation
# has not yet established it
systemctl list-unit-files | grep -E 'redis|redis-server'

# Replace redis with the confirmed service name
systemctl status redis
systemctl is-enabled redis

# Verify that the Redis process is running
ps aux | grep '[r]edis'

# Verify that Redis listens on TCP port 6379
ss -tlnp | grep ':6379'
netstat -tlnp 2>/dev/null | grep ':6379'

# Supply REDIS_PASSWORD through a protected environment mechanism.
# Do not place the password directly in shell history.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
# Expected: PONG

redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server

redis-cli -p 6379 -a "$REDIS_PASSWORD" CONFIG GET port
# Expected: port 6379

# Verify the password directive without printing its value
grep -E '^[[:space:]]*requirepass[[:space:]]+' /etc/redis/6379.conf \
  | sed -E 's/requirepass[[:space:]]+.*/requirepass <redacted>/'

# Verify that the cleanup directives are absent
grep -nE \
  '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected: no output when the cleanup behavior is reproduced exactly.

# Check Redis logs using the confirmed service name
journalctl -u redis --no-pager -n 100
journalctl -u redis -p warning..alert --no-pager


# Memcached instance: unresolved dependency

# Do not assume a Memcached service name, port, package, or configuration path.
# After the memcached cookbook is obtained, replace the placeholders below
# with its verified values.

systemctl list-unit-files | grep -i memcached
systemctl status <confirmed-memcached-service>
systemctl is-enabled <confirmed-memcached-service>
ss -tlnp | grep ':<confirmed-memcached-port>'

# Perform a protocol-level health check using the confirmed endpoint.
# Example only; do not run until the actual port and service are verified:
printf 'version\r\n' | nc 127.0.0.1 <confirmed-memcached-port>
```
