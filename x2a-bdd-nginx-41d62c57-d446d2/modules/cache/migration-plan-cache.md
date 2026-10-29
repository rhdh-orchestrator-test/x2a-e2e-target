---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures caching through the external `memcached` and `redisio` cookbooks. The locally available recipe defines one Redis instance on port `6379`, enables Redis authentication with the hardcoded password `redis_secure_password_123`, creates `/var/log/redis`, removes unsupported replication-related directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. The dependency recipe files are unavailable, so their package names, service names, templates, and detailed configuration behavior must be confirmed before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis caching service configured by the local recipe
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Log directory: `/var/log/redis`
  - Authentication: Enabled with `requirepass`
  - Password: `redis_secure_password_123`
  - `replicaservestaledata`: `nil`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Additional configuration cleanup:
    - Removes `replica-serve-stale-data`
    - Removes `replica-read-only`
    - Removes `repl-ping-replica-period`
    - Removes `client-output-buffer-limit`
    - Removes `replica-priority`

No explicit Memcached instance, port, listen address, or configuration value is available from the locally available recipe. Memcached is referenced through the external `memcached` cookbook.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only the locally executed recipe file is available. The dependency recipe files are referenced but unavailable.

**Recipes:**
```text
recipes/default.rb
```

**Providers:**
```text
None identified.
```

**Templates:**
```text
None identified.
```

**Attributes:**
```text
None identified.
```

**Files:**
```text
None identified.
```

## Module Explanation

The cookbook performs operations in the following execution-tree order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` recipe file is unavailable in the supplied execution tree.
   - The Memcached package name, service name, listening port, bind address, configuration file, authentication settings, and memory limits cannot be determined from the local recipe.

2. **default** (`cookbooks/cache/recipes/default.rb`):
   - Assigns one Redis server configuration to `node['redisio']['servers']`.
   - Configured Redis item:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - No additional Redis instances are configured.

3. **default** (`cookbooks/cache/recipes/default.rb`):
   - Creates the `/var/log/redis` directory recursively.
   - Sets owner to `redis`.
   - Sets group to `redis`.
   - Sets mode to `0755`.

4. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The `redisio` recipe file is unavailable in the supplied execution tree.
   - The dependency is expected to consume `node['redisio']['servers']`.
   - Redis package names, the service unit name, user and group creation behavior, generated configuration, templates, and startup behavior cannot be determined locally.

5. **default** (`cookbooks/cache/recipes/default.rb`):
   - Executes `ruby_block['fix_redis_config']`.
   - The block operates on `/etc/redis/6379.conf`.
   - If the file exists, reads its contents and removes every line matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified contents back to `/etc/redis/6379.conf`.
   - Does nothing when `/etc/redis/6379.conf` does not exist.
   - The recipe does not explicitly notify or restart Redis after this block.

6. **enable** (`cookbooks/cache/recipes/default.rb`, included as `redisio::enable`):
   - Includes the external `redisio::enable` recipe.
   - The `redisio::enable` recipe file is unavailable in the supplied execution tree.
   - The exact Redis service unit and enablement implementation must be confirmed from the dependency cookbook or target system.

The Redis attribute assignment is source-level configuration and is not represented as a separate execution-tree resource.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**System package dependencies**:
- None declared directly in `cookbooks/cache/recipes/default.rb`.
- Package names supplied by the external `memcached` and `redisio` cookbooks are unavailable and must be confirmed before migration.
- Do not invent package names from the local cookbook.

**Service dependencies**:
- Memcached service: provided by the unavailable `memcached` cookbook; service name and port are unknown.
- Redis service: provided by the unavailable `redisio` and `redisio::enable` recipes; exact service name is unknown.
- Redis listener: TCP port `6379`.

**Supported platforms from metadata**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext attribute value
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Passed to the Redis dependency as the `requirepass` setting for the Redis instance on port `6379`.
- **Migration handling**: Store the password in Ansible Vault or an AAP credential/injected secret. Do not preserve it as plaintext in a normal variable file or directly in a task.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, AWS Secrets Manager, HashiCorp Vault, or environment-variable secret references were detected.

No TLS certificate, private key, database connection string, API token, or SSH credential was detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

Dependency-created files cannot be listed because the `memcached` and `redisio` recipe files are unavailable.

**Service endpoints to check**:
- Redis TCP port `6379`
- Memcached port: unavailable
- Unix sockets: none specified
- Network bind address: not specified

**Templates rendered**:
- None identified
- Render count: `0`

**Configuration directives to verify in `/etc/redis/6379.conf`**:
- `replica-serve-stale-data` is absent
- `replica-read-only` is absent
- `repl-ping-replica-period` is absent
- `client-output-buffer-limit` is absent
- `replica-priority` is absent

## Pre-flight checks

```bash
# Verify the locally migrated recipe source
test -f cookbooks/cache/recipes/default.rb

# Redis configuration file for the named Redis instance
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Confirm unsupported directives were removed from the Redis instance configuration
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected replication-related directive remains in /etc/redis/6379.conf"
  exit 1
fi

# Redis log directory for the named Redis instance
test -d /var/log/redis
stat -c '%U %G %a %n' /var/log/redis
# Expected: redis redis 755 /var/log/redis

# Discover the Redis service unit supplied by redisio
systemctl list-unit-files | grep -E 'redis|redis-server'

# Replace <redis-service-unit> with the service unit identified above
systemctl status <redis-service-unit>

# Verify that the Redis instance is listening on port 6379
ss -ltnp | grep ':6379'

# Unauthenticated access may fail when requirepass is enabled
redis-cli -p 6379 PING

# Authenticated access must succeed
redis-cli -p 6379 -a '<redis-password-from-Ansible-Vault>' PING

# Verify the configured Redis port
redis-cli -p 6379 -a '<redis-password-from-Ansible-Vault>' CONFIG GET port

# Check Redis logs
journalctl -u <redis-service-unit> --no-pager -n 100
find /var/log/redis -maxdepth 1 -type f -print

# Memcached checks cannot be completed until the dependency identifies
# the service unit, listening port, bind address, and configuration path.
```