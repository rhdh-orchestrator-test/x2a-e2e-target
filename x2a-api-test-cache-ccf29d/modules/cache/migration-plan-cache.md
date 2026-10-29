---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures caching services through Memcached and Redis dependencies. The available recipe defines one Redis instance on port `6379`, creates `/var/log/redis`, configures Redis authentication, includes the `redisio` and `redisio::enable` recipes, and removes five replication-related directive types from `/etc/redis/6379.conf`. Memcached and Redis dependency recipe files are unavailable, so their package names, service resources, and Memcached settings must be obtained from the dependency cookbooks or deployment requirements.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-6379**: Redis server configured through `node['redisio']['servers']`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is enabled; `replicaservestaledata` is `nil`; the Redis log directory is `/var/log/redis`, owned by `redis:redis` with mode `0755`
  - Configuration cleanup removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`

- **Memcached**: Included through the `memcached` dependency recipe
  - Location/Path: Not available; dependency recipe is missing
  - Port/Socket: Not specified in the available cookbook
  - Key Config: Package name, service name, bind address, memory allocation, connection limit, and configuration path must be obtained from the `memcached` dependency cookbook or deployment requirements

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
  cookbooks/cache/recipes/default.rb

Providers:
  None

Templates:
  None

Attributes:
  None

Files:
  None
```

The Redis server configuration is assigned directly inside `cookbooks/cache/recipes/default.rb`. No separate attribute files, templates, providers, `cookbook_file` resources, or `remote_file` resources are present.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` recipe.
   - The dependency reports `memcached Recipe file not found`; its package, service, port, bind address, memory allocation, connection limit, and configuration path cannot be determined from this cookbook.
   - Assigns one Redis server definition to `node['redisio']['servers']`:
     - Instance: `redis-6379`
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the `redisio` recipe.
   - The dependency reports `redisio Recipe file not found`; Redis installation, package resources, configuration generation, and service resource details are unavailable.
   - Executes `ruby_block[fix_redis_config]` after the Redis configuration step:
     - Reads `/etc/redis/6379.conf` when the file exists.
     - Removes lines beginning with `replica-serve-stale-data`.
     - Removes lines beginning with `replica-read-only`.
     - Removes lines beginning with `repl-ping-replica-period`.
     - Removes lines beginning with `client-output-buffer-limit`.
     - Removes lines beginning with `replica-priority`.
     - Writes the modified configuration back to `/etc/redis/6379.conf`.
     - Performs no action when the configuration file does not exist.
   - Includes `redisio::enable`.
   - The dependency reports `redisio::enable Recipe file not found`; the exact Redis service name cannot be determined.
   - No `.each` loops are present in the available recipe. The configured Redis collection contains exactly one item, `redis-6379`.

The execution order is:

1. `memcached` dependency inclusion.
2. Redis server definition for `redis-6379`.
3. Creation of `/var/log/redis`.
4. `redisio` dependency inclusion.
5. Execution of `ruby_block[fix_redis_config]`.
6. `redisio::enable` dependency inclusion.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- Not determinable from the available execution tree.
- Package resources are expected to be supplied by the unavailable `memcached` and `redisio` dependency recipes.
- No package name should be added until verified from those dependency implementations or the target deployment requirements.

**Service dependencies**:

- **Memcached**: Included through `memcached`; service name and service behavior are unavailable.
- **Redis instance `redis-6379`**: Enabled through `redisio::enable`; exact service name is unavailable and may be distribution- or dependency-specific.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef node attribute assignment
- **Value currently present**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for instance `redis-6379` on port `6379`
- **Configuration target**: Expected to be consumed by `redisio` and written to `/etc/redis/6379.conf`

The migration must move this value to Ansible Vault, using a variable such as `redis_password`. The plaintext value must not be stored in role defaults, task files, committed templates, command-line arguments, or migration logs. Generated configuration files containing the password must have appropriately restrictive permissions.

No data bags, encrypted data bags, Chef Vault items, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, database credentials, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

Dependency-managed files requiring verification after the missing cookbooks are obtained:

- Redis package and executable files
- Redis service unit or init script
- Memcached configuration file
- Memcached service unit or init script

**Service endpoints to check**:

- **redis-6379**: TCP port `6379`
- **Memcached**: Port not specified; obtain the value from the `memcached` dependency before defining an acceptance check
- Unix sockets: None specified

**Templates rendered**:

- None; zero templates are rendered by the available cookbook recipe.

**Redis configuration checks**:

- `/etc/redis/6379.conf` contains port `6379`.
- `/etc/redis/6379.conf` contains a `requirepass` directive without exposing its value in logs.
- The following directive types are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Redis log directory checks**:

- `/var/log/redis` exists.
- Owner is `redis`.
- Group is `redis`.
- Mode is `0755`.

**Memcached checks**:

Before finalizing Memcached validation, obtain and document its exact service name, listening port, bind address, configuration path, memory allocation, and connection limit from the missing dependency implementation. No guessed Memcached port should be used.

## Pre-flight checks

```bash
# Redis instance redis-6379: identify the service name supplied by redisio
systemctl status redis
systemctl status redis-server

# Redis instance redis-6379: verify the process
ps aux | grep '[r]edis-server'

# Redis instance redis-6379: verify TCP port 6379
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Redis instance redis-6379: unauthenticated access should be rejected
redis-cli -p 6379 PING

# Redis instance redis-6379: authenticated connectivity
REDISCLI_AUTH='<retrieve-from-Ansible-Vault>' redis-cli -p 6379 PING

# Expected authenticated response:
# PONG

# Verify Redis instance redis-6379 configuration
grep -E '^[[:space:]]*port[[:space:]]+6379' /etc/redis/6379.conf
grep -E '^[[:space:]]*requirepass[[:space:]]+' /etc/redis/6379.conf

# Verify removed directives for Redis instance redis-6379
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Expected result: no matching lines are returned.

# Verify Redis log directory for redis-6379
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis

# Expected result:
# drwxr-xr-x redis redis /var/log/redis

# Verify an authenticated Redis operation for redis-6379
REDISCLI_AUTH='<retrieve-from-Ansible-Vault>' redis-cli -p 6379 SET migration_check success
REDISCLI_AUTH='<retrieve-from-Ansible-Vault>' redis-cli -p 6379 GET migration_check
REDISCLI_AUTH='<retrieve-from-Ansible-Vault>' redis-cli -p 6379 DEL migration_check

# Expected results:
# OK
# "success"
# (integer) 1

# Inspect Redis logs for redis-6379
find /var/log/redis -maxdepth 1 -type f -print
journalctl -u redis --no-pager -n 50
journalctl -u redis-server --no-pager -n 50
```

Use only the Redis service name actually created by the `redisio` dependency.

```bash
# Memcached instance: service and endpoint checks cannot be completed
# until the missing memcached dependency is inspected.
#
# After obtaining the verified service name and port:
systemctl status <verified-memcached-service>
ss -tlnp | grep ':<verified-memcached-port>'
```

Do not use a guessed Memcached port or service name as a migration acceptance criterion.