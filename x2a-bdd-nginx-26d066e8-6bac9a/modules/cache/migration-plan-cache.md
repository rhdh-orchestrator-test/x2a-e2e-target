---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook includes the external `memcached` and `redisio` cookbooks, defines one Redis instance on port `6379`, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and enables Redis through `redisio::enable`. The Redis password is currently hardcoded in the Chef recipe and must be migrated to Ansible Vault or an AAP-managed credential. External cookbook recipes are not present in the supplied execution tree, so their exact package names, service names, Memcached settings, and dependency-specific defaults must be confirmed from the target roles or original cookbooks.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis_6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config:
    - `requirepass` is set to the protected migration value corresponding to the Chef value `redis_secure_password_123`
    - `replicaservestaledata` is explicitly `nil`
    - Lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` are removed after configuration generation

- **memcached**: External Memcached service included through the `memcached` cookbook
  - Location/Path: Not defined by the local cookbook
  - Port/Socket: Not defined by the local cookbook
  - Key Config: Package, service name, listening address, port, socket, authentication, and configuration path are delegated to the external cookbook and must be confirmed before migration

The local recipe defines one Redis server configuration item. There are no Chef `.each` loops in the local recipe.

## File Structure

Only the local recipe is present in the supplied execution tree. External dependency recipes are referenced but unavailable and are not listed as local files.

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

```text
```

No provider files were supplied or shown in the execution tree.

**Templates:**

```text
```

No templates were supplied or shown in the execution tree.

**Attributes:**

```text
```

There is no `attributes/default.rb` file. The Redis server collection is defined inline in `cookbooks/cache/recipes/default.rb`.

**Files:**

```text
```

No static files are deployed by the local recipe.

## Module Explanation

The cookbook performs operations in this order. The Redis server attribute assignment is recipe setup performed before the listed resources; it is not an independent execution-tree resource.

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe first.
   - The external dependency is responsible for Memcached package installation, configuration, and service management.
   - Exact Memcached package name, service name, port, configuration path, and defaults are not defined locally.
   - Iterations: None.

2. **default** (`cookbooks/cache/recipes/default.rb`) — Redis server configuration setup:
   - Assigns one item to `node.default['redisio']['servers']`.
   - Defines Redis instance `redis_6379` with port `6379`.
   - Sets the Redis password to `redis_secure_password_123` in the current Chef implementation.
   - Sets `replicaservestaledata` to `nil`.
   - In Ansible, represent the password with a protected variable such as `vault_redis_requirepass`; do not commit the plaintext value.
   - Iterations: One Redis item, `redis_6379`.

3. **default** (`cookbooks/cache/recipes/default.rb`) — Redis log directory:
   - Creates `/var/log/redis`.
   - Sets owner `redis`.
   - Sets group `redis`.
   - Sets mode `0755`.
   - Enables recursive creation.
   - Ensure the Redis user and group exist before this task. They are expected to be created by the Redis installation role or external `redisio` implementation.
   - Resources used: `directory[/var/log/redis]`.
   - Iterations: None.

4. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The dependency is responsible for Redis package installation, user and group creation, configuration generation, and service setup.
   - Generate the configuration for `redis_6379` at `/etc/redis/6379.conf`.
   - Apply the configured port and password.
   - Ensure `/etc/redis/6379.conf` exists before the cleanup task.
   - Exact package and service names are not available from the supplied files.
   - Iterations: None.

5. **default** (`cookbooks/cache/recipes/default.rb`) — `ruby_block[fix_redis_config]`:
   - Reads `/etc/redis/6379.conf` when the file exists.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Implement the transformation with idempotent Ansible `replace` tasks or an equivalent idempotent script.
   - Do not remove unrelated Redis settings.
   - Restart or reload Redis only when the file changes and the selected Redis role requires it.
   - Iterations: None.

6. **enable** (`cookbooks/cache/recipes/default.rb`, via `redisio::enable`):
   - Includes the external `redisio::enable` recipe last.
   - Enables the Redis service corresponding to `redis_6379`.
   - Starts the service if required by the target Redis implementation.
   - Confirm the actual service unit name before configuring the Ansible service task.
   - Iterations: None.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint
- `redisio::enable`, provided by `redisio`

**System package dependencies**:

- Not explicitly declared in the local cookbook.
- Package installation is delegated to the external `memcached` and `redisio` implementations.
- Exact package names must be obtained from those implementations or the target Ansible roles; none can be verified from the supplied local files.

**Service dependencies**:

- Memcached service provided by `memcached`
- Redis service for `redis_6379`, enabled through `redisio::enable`
- Exact service unit names are not available from the supplied files

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis Authentication Password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for `redis_6379` on TCP port `6379`
- **Migration handling**:
  - Store the value in Ansible Vault or an AAP-managed credential.
  - Reference it through a protected variable such as `vault_redis_requirepass`.
  - Do not commit the plaintext password to role defaults, vars, templates, or inventory.
  - Ensure the generated Redis configuration contains the equivalent `requirepass` setting.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, TLS certificates, private keys, API tokens, or additional connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

External package- and service-specific files owned by the `memcached` and `redisio` implementations must be confirmed from those implementations.

**Service endpoints to check**:

- `redis_6379`: TCP port `6379`
- `memcached`: Port not configured by the local cookbook; confirm the effective endpoint before adding a port-specific check
- Unix sockets: None configured or referenced by the local recipe

**Templates rendered**:

- None; the local cookbook contains no templates

## Pre-flight checks:

```bash
# Confirm the Redis service unit name supplied by the target Ansible Redis role.
systemctl status <redis-service-for-redis_6379>
systemctl is-enabled <redis-service-for-redis_6379>
systemctl is-active <redis-service-for-redis_6379>

# Confirm Redis is running and listening for redis_6379.
ps aux | grep '[r]edis-server'
ss -tlnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Confirm the Redis configuration exists and uses port 6379.
test -f /etc/redis/6379.conf
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf

# Confirm the Redis password directive exists without printing its value.
grep -E '^requirepass[[:space:]]+' /etc/redis/6379.conf

# Confirm the unwanted directive families are absent.
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis replication directives remain"
  exit 1
else
  echo "Redis replication directives are absent"
fi

# Confirm the Redis log directory ownership and mode.
test -d /var/log/redis
stat -c '%U %G %a %n' /var/log/redis
# Expected:
# redis redis 755 /var/log/redis

# Validate Redis authentication without exposing the password.
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" PING
# Expected:
# PONG

# Confirm the effective Redis log and data paths.
grep -E '^(logfile|dir)' /etc/redis/6379.conf

# Confirm the Memcached service name and port from the external role before running:
systemctl status <memcached-service-name>
systemctl is-active <memcached-service-name>
ss -tlnp | grep ':<configured-memcached-port>'

# If the external role confirms the conventional Memcached port:
ss -tlnp | grep ':11211'
printf 'version\r\n' | nc -w 2 127.0.0.1 11211

# Validate the Redis service after migration.
systemctl show <redis-service-for-redis_6379> --property=ActiveState,SubState
journalctl -u <redis-service-for-redis_6379> --since "10 minutes ago" --no-pager
```

Expected migration results:

- `redis_6379` is active and listening on TCP port `6379`.
- `/etc/redis/6379.conf` exists.
- Redis authentication succeeds using the protected secret.
- All five unwanted directive families are absent.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- Memcached is validated using the confirmed service name and endpoint.
- An unchanged Ansible run does not trigger an unnecessary Redis restart.
