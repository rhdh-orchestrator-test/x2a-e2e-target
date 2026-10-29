---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through Memcached and Redis dependencies, but only the `cache::default` recipe is available in the supplied execution tree. The executable recipe defines one Redis server on TCP port `6379`, enables authentication using a hardcoded password, creates `/var/log/redis`, invokes the unavailable `memcached`, `redisio`, and `redisio::enable` recipes in that order, and removes five replication-related directive families from `/etc/redis/6379.conf`. The migration should implement the Redis configuration with Ansible, store the password in Ansible Vault, and determine package and service names from the target distribution because the dependency recipes are unavailable.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache and authenticated Redis service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`
  - Log directory: `/var/log/redis`
  - Key Config: Redis authentication enabled through `requirepass`; `replicaservestaledata` is unset; replication-related directives are removed after configuration
  - Password source: Hardcoded in `cookbooks/cache/recipes/default.rb`; migrate to Ansible Vault
  - Removed directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

No Memcached instance parameters, port, configuration path, or service settings are available because the referenced Memcached dependency recipe is not present in the analyzed execution tree.

## File Structure

Only files shown by the supplied execution tree are listed. Referenced dependency recipes are not present and are therefore not included.

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

## Module Explanation

The cookbook performs operations in the following order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` recipe.
     - The execution tree reports `memcached Recipe file not found`.
     - No Memcached package, template, service, port, or configuration resource can be derived from the supplied files.
   - Assigns one Redis server definition:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation enabled
   - Includes the `redisio` recipe.
     - The execution tree reports `redisio Recipe file not found`.
   - Executes `ruby_block[fix_redis_config]`.
     - Checks whether `/etc/redis/6379.conf` exists.
     - Reads the file when it exists.
     - Removes complete lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Writes the modified content back to `/etc/redis/6379.conf`.
     - Makes no change when the file does not exist.
   - Includes `redisio::enable`.
     - The execution tree reports `redisio::enable Recipe file not found`.
   - Resources from the execution tree:
     - `directory`: 1
     - `ruby_block`: 1
   - Iterations: No `.each` loops are present.

### Ansible implementation sequence

1. Store the Redis password in Ansible Vault.
2. Install and configure the Redis dependency required by the target operating system.
3. Define the Redis server on TCP port `6379`.
4. Configure Redis authentication using the vaulted password.
5. Create `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
6. Ensure the Redis service is enabled at boot and started.
7. Apply the configuration cleanup to `/etc/redis/6379.conf`.
8. Restart or reload Redis only when the Redis configuration changes.

Implement the cleanup idempotently with Ansible tasks such as `ansible.builtin.lineinfile` using regular expressions. Remove each unwanted directive from `/etc/redis/6379.conf`.

The exact systemd service name cannot be established from the supplied files because the `redisio` dependency recipe is unavailable. Determine it from the selected Redis package and target distribution during implementation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- Exact package names are not exposed by the supplied execution tree.
- Do not infer package names or versions from this cookbook alone.
- Resolve package names using the selected Ansible distribution variables or the unavailable dependency implementations.

**Service dependencies**:

- Redis is intended to be enabled through `redisio::enable`.
- The exact Redis service unit name is unavailable because `redisio::enable` is not present.
- Memcached service management is unavailable because the `memcached` recipe is not present.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded Chef attribute assignment
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value detected**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the Redis server listening on TCP port `6379`
- **Ansible migration**: Store the password in Ansible Vault and reference the vaulted variable from the Redis configuration template or an idempotent Ansible task. Do not commit the plaintext password to the Ansible repository.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret, TLS certificate, private key, API token, or database connection credential was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis server on port `6379`
- Unix sockets: None specified
- Network interfaces: None specified

**Configuration directives to verify**:

- Redis listens on port `6379`.
- Redis authentication is enabled.
- The following directive families are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- None. No templates are referenced by the available recipe.
- Redis configuration is expected to be created or managed by the unavailable `redisio` dependency.

## Pre-flight checks:

```bash
# Redis instance: Redis server on port 6379
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Verify the Redis log directory
stat -c '%A %U:%G %n' /var/log/redis
# Expected: mode 0755, owner redis, group redis

# Verify unwanted replication directives are absent
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected replication directives remain"
  exit 1
fi

# Verify the Redis instance is listening on TCP port 6379
ss -ltnp | grep ':6379'
# Expected: a Redis process listening on TCP port 6379

# Verify the Redis service
# Replace redis-service-name with the exact service name discovered on the target host.
systemctl status redis-service-name

# Verify authenticated Redis responsiveness without exposing the password
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
# Expected: PONG

# Verify authenticated Redis server information
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server | grep -E 'redis_version|tcp_port'
# Expected: redis_version is present and tcp_port is 6379

# Verify unauthenticated access is rejected
redis-cli -p 6379 PING
# Expected: an authentication-required error, not PONG

# Validate Redis configuration using the installed Redis binary
redis-server /etc/redis/6379.conf --test-memory 2
```

The final syntax-check command may vary by Redis package version. If the installed Redis binary does not support that invocation, use the package-provided configuration validation method instead.

No Memcached-specific pre-flight check can be defined because the Memcached dependency implementation is unavailable. Do not add a Memcached port or service check unless the missing dependency establishes those values.