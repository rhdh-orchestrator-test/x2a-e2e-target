---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis instance on port `6379` and includes the external `memcached`, `redisio`, and `redisio::enable` recipes. The local recipe creates `/var/log/redis`, assigns Redis authentication and replication-related settings, removes five replication directives from `/etc/redis/6379.conf`, and enables Redis through the external cookbook. The execution tree confirms the local resources and missing external recipes, but the supplied structured analysis does not independently verify the local attribute values, resource properties, or Ruby block contents; those details require source-file verification during migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache and authentication service
  - Location/Path: `/etc/redis/6379.conf`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is configured with the source-reported value `redis_secure_password_123`; `replicaservestaledata` is unset. The source-reported configuration removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
  - Log directory ownership: `redis:redis`
  - Log directory mode: `0755`
  - Log directory creation: recursive

- **Memcached dependency**: External cache service included by the cookbook
  - Location/Path: Not specified by the local cookbook
  - Port/Socket: Not specified by the local cookbook
  - Key Config: Package, service name, listen address, port, memory limit, user, group, and configuration path are provided by the external `memcached` cookbook, which is unavailable in the execution tree.

The Redis attribute values, directory properties, and configuration-editing behavior are reported by the source plan but require verification against `cookbooks/cache/recipes/default.rb`.

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

The metadata file was inspected to identify the cookbook description and external dependencies, but it is not included in the execution-tree file list. External dependency recipes are unavailable and are not listed.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe. The execution tree reports `memcached Recipe file not found`.
   - Assigns one Redis server definition to `node['redisio']['servers']`:
     - Port: `6379`
     - Authentication: `requirepass`
     - Source-reported password: `redis_secure_password_123`
     - `replicaservestaledata`: unset
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe. The execution tree reports `redisio Recipe file not found`.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - If `/etc/redis/6379.conf` exists, removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - If `/etc/redis/6379.conf` does not exist, performs no configuration-editing action.
   - Includes `redisio::enable`. The execution tree reports `redisio::enable Recipe file not found`.
   - No `.each` loops are present in the supplied local recipe or execution description.

The external recipes must be obtained or replaced with verified Ansible implementation details before package names, service names, templates, data directories, or exact service-management behavior are finalized.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint
- `redisio::enable`, included by the local recipe

**System package dependencies**:

- None specified by `cookbooks/cache/recipes/default.rb`
- Package names from the external `memcached` and `redisio` cookbooks are unavailable and must not be invented.

**Service dependencies**:

- Redis instance on TCP port `6379`
- Memcached service, with service name and port unspecified
- Redis service name is unspecified because `redisio` and `redisio::enable` are unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file. The credential is source-reported and requires verification against the recipe.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None
  - **Path**: None

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Value currently present**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the instance listening on TCP port `6379`

Migration requirements:

- Store the password in Ansible Vault under a variable such as `redis_requirepass`.
- Do not place the plaintext value in `defaults/main.yml`, `vars/main.yml`, committed templates, or task output.
- Use `no_log: true` on tasks that may expose the password.
- Ensure any Redis configuration file containing the password has restrictive permissions.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database credentials, or API tokens were detected in the supplied recipe.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

The following dependency-managed paths cannot be confirmed from the local cookbook:

- Redis data directory
- Redis log file
- Redis service unit or init script
- Memcached configuration file
- Memcached service unit or init script

**Service endpoints to check**:

- Redis TCP port `6379`
- Memcached port: not specified by this cookbook
- Unix sockets: none specified
- Network bind address: not specified

**Templates rendered**:

- Local templates: none; render count `0`
- External `memcached` templates: unavailable; render count cannot be determined
- External `redisio` templates: unavailable; render count cannot be determined

**Configuration directives to verify as absent from `/etc/redis/6379.conf`**:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Identify all available Redis and Memcached service units.
systemctl list-unit-files | grep -E 'redis|memcached'
systemctl list-units --type=service | grep -E 'redis|memcached'

# Verify the Redis 6379 configuration file and log directory.
test -f /etc/redis/6379.conf
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis

# Expected Redis log directory:
# owner: redis
# group: redis
# mode: 0755

# Verify Redis 6379 configuration without exposing the password.
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Confirm the five unwanted directives are absent.
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis replication directives found"
  exit 1
fi

# Confirm the Redis 6379 process and endpoint.
ps aux | grep '[r]edis-server'
ss -tlnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Replace REDIS_SERVICE_NAME with the service name verified on the target host.
systemctl status REDIS_SERVICE_NAME

# Use a vaulted password supplied through the environment.
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 PING
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 SET chef_migration_test ok
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 GET chef_migration_test
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 DEL chef_migration_test

# Expected Redis results:
# PING: PONG
# SET: OK
# GET: ok
# DEL: 1

# Verify authentication is required without printing the password.
redis-cli -p 6379 PING

# Inspect Redis logging settings without exposing credentials.
grep -E '^(logfile|dir|port)' /etc/redis/6379.conf

# Replace REDIS_SERVICE_NAME with the verified Redis service name.
journalctl -u REDIS_SERVICE_NAME --no-pager -n 50

# Identify and check the external Memcached service.
systemctl list-units --type=service | grep memcached
systemctl status memcached

# Do not add a Memcached port check until the external dependency or
# target requirements provide the exact port.
```