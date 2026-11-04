---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer consisting of one Redis instance and an included Memcached dependency. Redis listens on port `6379`, uses a hardcoded authentication password that must be migrated to secure Ansible storage, creates `/var/log/redis`, and removes selected replication directives from `/etc/redis/6379.conf`. The `memcached`, `redisio`, and `redisio::enable` dependency recipes are referenced but absent from the supplied execution tree, so their package names, service names, templates, and exact Memcached port cannot be determined.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server configured through redisio**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is set to the migrated secret; `replicaservestaledata` is explicitly unset; replication-related directives are removed after configuration
  - User/Group: `redis:redis` for `/var/log/redis`
  - Log directory mode: `0755`

- **Memcached dependency**: Included cache dependency
  - Location/Path: Not determinable; the `memcached` recipe is absent
  - Port/Socket: Not determinable from the supplied files
  - Key Config: Package, service name, configuration path, enablement behavior, and port must be obtained from the actual `memcached` dependency cookbook or target platform requirements
  - Status: `include_recipe 'memcached'` is requested, but the recipe is not present in the supplied execution tree

## File Structure

Only files present in the supplied execution tree are listed.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
None identified
```

**Templates:**
```text
None identified
```

**Attributes:**
```text
None identified
```

**Files:**
```text
None identified
```

The following referenced dependency recipes are absent from the execution tree:

- `memcached`
- `redisio`
- `redisio::enable`

`metadata.rb` was inspected for cookbook metadata and dependencies but is not included in the executable file list.

## Module Explanation

The cookbook performs operations in the following order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` recipe.
   - Execution result: `memcached` recipe file not found.
   - The supplied cookbook does not define Memcached package installation, configuration, service management, or port settings.
   - Sets one Redis server definition:
     - Instance: Redis server configured through redisio
     - Port: `6379`
     - Authentication: `requirepass` set to `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the `redisio` recipe.
   - Execution result: `redisio` recipe file not found.
   - The missing dependency is expected to provide Redis package installation, configuration, service management, user creation, and configuration rendering, but those details are not present in the supplied files.
   - Executes the `ruby_block 'fix_redis_config'` resource against `/etc/redis/6379.conf`.
   - If `/etc/redis/6379.conf` exists, reads the complete file, removes matching lines, and writes the modified content back.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Does nothing if `/etc/redis/6379.conf` does not exist.
   - Includes the `redisio::enable` recipe.
   - Execution result: `redisio::enable` recipe file not found.
   - The intended behavior is to enable Redis at boot, but the actual service name and provider implementation are unavailable.
   - Resource counts in this recipe:
     - `directory`: 1
     - `ruby_block`: 1
     - Explicit Chef `group` resources: 0
     - Included recipes: 3 attempted includes, all absent from the supplied execution tree
   - Iterations: None. The recipe configures exactly one Redis server definition with port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- Not determinable from the supplied execution tree.
- The cache cookbook contains no explicit `package` resource.
- Do not invent package names; obtain them from the actual `memcached` and `redisio` implementations or target platform requirements.

**Service dependencies**:

- Redis is intended to be configured and enabled through `redisio` and `redisio::enable`.
- The Redis service name and provider implementation are unavailable.
- Memcached is included, but its service name and enablement behavior are unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe source
  - **URL**: None detected
  - **Path**: Not applicable

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef attribute assignment
- **Usage context**: Redis authentication through the `requirepass` configuration setting
- **Migration handling**:
  - Store the value in Ansible Vault, an AAP credential, or another approved secret store.
  - Reference it through a variable such as `redis_password`.
  - Do not commit the literal password to the Ansible role or plaintext inventory.
  - Use the secret when rendering Redis configuration and running authenticated Redis validation commands.

No data bag, encrypted data bag, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secret, TLS certificate, private key, or database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

The cookbook does not explicitly create a Redis data directory, Redis log file, or Memcached configuration file.

**Service endpoints to check**:

- Redis server configured through redisio: TCP `6379`
- Memcached dependency: port unavailable from the supplied files
- Unix sockets: none identified
- Network interfaces: none specified

**Templates rendered**:

- None identified in the supplied execution tree.
- Redis configuration template rendering is expected to be performed by the missing `redisio` dependency and must be verified after that dependency is obtained.

**Configuration transformations to verify**:

- `/etc/redis/6379.conf` exists after Redis configuration.
- Redis listens on TCP port `6379`.
- Redis authentication remains configured with the migrated secret.
- The following directives are absent after the `fix_redis_config` operation:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.

## Pre-flight checks

The exact Redis service name is unavailable from the missing `redisio` dependency. Replace `<redis-service-name>` with the service name provided by the selected Ansible Redis implementation.

```bash
# Redis server configured through redisio: service status
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>

# Redis server configured through redisio: process verification
ps aux | grep '[r]edis-server'

# Redis server configured through redisio: configuration file
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Redis server configured through redisio: port verification
ss -tlnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Redis server configured through redisio: authenticated connectivity
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
# Expected output: PONG

# Redis server configured through redisio: server information
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO replication

# Redis server configured through redisio: removed directive verification
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected replication directives remain"
  exit 1
else
  echo "Replication directives were removed"
fi

# Redis server configured through redisio: log directory
stat -c '%A %U %G %n' /var/log/redis
find /var/log/redis -maxdepth 1 -type f -print

# Redis server configured through redisio: logs
journalctl -u <redis-service-name> --no-pager -n 100

# Memcached dependency
echo "Memcached checks cannot be completed until the missing memcached dependency is obtained."
echo "After obtaining the dependency, verify its exact service name, package, configuration path, port, listening socket, and protocol-level health check."
```