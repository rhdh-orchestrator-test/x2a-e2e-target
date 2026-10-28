---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook is intended to configure Memcached and Redis, but only `cookbooks/cache/recipes/default.rb` is present in the supplied execution tree. The recipe attempts to include `memcached`, `redisio`, and `redisio::enable`; all three referenced recipes are unavailable. Source-level configuration assigns one Redis instance to port `6379`, sets Redis authentication, creates `/var/log/redis`, and removes selected replication-related directives from `/etc/redis/6379.conf`. Redis package, service, template, and exact resource behavior must be validated against the replacement implementation because the dependency recipes are missing.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache and authenticated client endpoint
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config:
    - Redis authentication is assigned through `requirepass`
    - Source-level password value: `redis_secure_password_123`
    - `replicaservestaledata` is assigned `nil`
    - `/var/log/redis` is created for Redis logs
    - The following directives are removed from the generated configuration:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`
    - The Redis package and service unit are not determinable because the `redisio` dependency is unavailable

- **Memcached**: Intended cache dependency, not configured by an available recipe
  - Location/Path: Not determinable
  - Port/Socket: Not determinable
  - Key Config: The recipe attempts to include `memcached`, but the execution tree reports `memcached Recipe file not found`. No Memcached package, configuration, service, endpoint, or template is available to migrate.

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

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

No attribute files are shown in the execution tree. Redis attributes are assigned directly inside `cookbooks/cache/recipes/default.rb`.

**Files:**

```text
```

No static files are deployed by the executed recipe.

## Module Explanation

The cookbook performs operations in the following order. The supplied recipe contains no `.each` loops; it assigns exactly one Redis server definition.

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the unavailable `memcached` dependency.
   - Assigns one Redis server definition on port `6379`.
   - Sets Redis authentication and assigns `replicaservestaledata` as `nil`.
   - Creates `/var/log/redis` as a directory for Redis logs.
   - Attempts to include the unavailable `redisio` dependency.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` when that file exists.
   - Attempts to include the unavailable `redisio::enable` dependency.

   **Memcached dependency inclusion:**

   ```ruby
   include_recipe 'memcached'
   ```

   The execution tree reports:

   ```text
   memcached Recipe file not found
   ```

   Migration requirements:

   - Do not invent a Memcached package, service, port, configuration file, or template.
   - Invoke an equivalent Memcached role only if one is separately supplied.
   - Otherwise record Memcached as an unresolved dependency.

   **Redis server assignment:**

   ```ruby
   node.default['redisio']['servers'] = [
     {
       'port' => '6379',
       'requirepass' => 'redis_secure_password_123',
       'replicaservestaledata' => nil
     }
   ]
   ```

   Migration requirements:

   - Represent exactly one Redis server definition with port `6379`.
   - Configure Redis authentication using an Ansible Vault variable.
   - Preserve `replicaservestaledata` as unset or equivalent to `nil`.
   - Do not create additional Redis instances.

   **Redis log directory:**

   Resource:

   ```text
   directory[/var/log/redis]
   ```

   Source-level directory properties are:

   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled

   The structured execution analysis confirms the directory resource but does not independently expose these properties. Verify them directly against the source before treating them as validated migration requirements.

   Ansible equivalent:

   - Use `ansible.builtin.file`.
   - Set `state: directory`.
   - Set owner `redis`.
   - Set group `redis`.
   - Set mode `'0755'`.
   - Create parent directories as needed.

   **Redis dependency inclusion:**

   ```ruby
   include_recipe 'redisio'
   ```

   The execution tree reports:

   ```text
   redisio Recipe file not found
   ```

   Migration requirements:

   - Supply an equivalent Redis installation and configuration role.
   - Do not infer the Redis package name, repository, configuration template, or service name.
   - The expected Redis configuration path for the subsequent Ruby block is `/etc/redis/6379.conf`.

   **Redis configuration cleanup:**

   Resource:

   ```text
   ruby_block[fix_redis_config]
   ```

   The source-level operation targets:

   ```text
   /etc/redis/6379.conf
   ```

   When the file exists, the block reads the complete file, removes lines matching the following patterns, and writes the modified content back:

   - `^replica-serve-stale-data.*$`
   - `^replica-read-only.*$`
   - `^repl-ping-replica-period.*$`
   - `^client-output-buffer-limit.*$`
   - `^replica-priority.*$`

   If the file does not exist, the block does nothing.

   The structured execution analysis confirms `ruby_block[fix_redis_config]` but does not independently expose the path, patterns, existence guard, or write-back behavior. Verify these source-level details before implementation.

   Ansible equivalent:

   - Run the cleanup after the Redis configuration has been generated.
   - Use `ansible.builtin.replace` or another idempotent file-editing mechanism.
   - Target `/etc/redis/6379.conf`.
   - Do not fail when the file is absent.
   - Notify a Redis restart or reload only when the file changes, subject to the replacement Redis role.

   **Redis enablement:**

   ```ruby
   include_recipe 'redisio::enable'
   ```

   The execution tree reports:

   ```text
   redisio::enable Recipe file not found
   ```

   Migration requirements:

   - Enable and start Redis only after the replacement implementation identifies the correct service unit.
   - Do not assume `redis`, `redis-server`, or `redis@6379`.
   - Validate the service name against the target distribution and replacement Redis role.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`, as declared by the supplied cookbook metadata
- `redisio`, with no version constraint, as declared by the supplied cookbook metadata

The dependency recipes are not present in the supplied execution tree. The execution tree specifically reports missing `memcached`, `redisio`, and `redisio::enable` recipes. Dependency version declarations should be confirmed against `metadata.rb` before migration sign-off.

**System package dependencies**:

- None directly declared by `cookbooks/cache/recipes/default.rb`
- Package names are not determinable because the dependency recipes are unavailable
- Do not claim that a specific Memcached or Redis package was installed by this cookbook

**Service dependencies**:

- Redis enablement is attempted through `redisio::enable`, but that recipe is unavailable
- The Redis service unit name is not determinable from the supplied source
- Memcached service management is not observable because the `memcached` recipe is unavailable

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef node attribute assignment
- **Usage context**: Redis client authentication for the Redis instance listening on TCP port `6379`

Ansible migration requirements:

- Store the password in an Ansible Vault variable such as `redis_password`.
- Render or configure Redis authentication from the vaulted variable.
- Do not commit `redis_secure_password_123` to the Ansible repository.
- Update application clients to use the same vaulted credential.
- No data bag, encrypted data bag, Chef Vault, CyberArk, Conjur, environment variable, TLS certificate, private key, or database connection credential was detected in the supplied source.

The structured execution analysis does not independently expose the credential value. Confirm the credential directly in `cookbooks/cache/recipes/default.rb` before migration sign-off.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis TCP port `6379`
- No Unix socket is specified
- No Memcached endpoint is available from the supplied execution tree

**Configuration directives to verify**:

- Redis is configured to listen on port `6379`.
- Redis authentication is enabled.
- The following directives are absent from `/etc/redis/6379.conf`:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- None detected
- Render count: `0`

## Pre-flight checks:

```bash
# Confirm the Redis service unit supplied by the replacement Redis implementation.
systemctl list-unit-files | grep -E '^redis(@|\.service)|^redis-server\.service'

# Check the validated Redis service unit after identifying its name.
systemctl status <validated-redis-service-unit>
systemctl is-enabled <validated-redis-service-unit>
systemctl is-active <validated-redis-service-unit>

# Verify the Redis configuration file exists.
test -f /etc/redis/6379.conf
ls -l /etc/redis/6379.conf

# Verify the Redis log directory and its source-level metadata.
test -d /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis
# Expected source-level metadata:
# redis:redis 755 /var/log/redis

# Verify Redis is listening on the configured endpoint.
ss -tlnp | grep ':6379'

# Authenticated Redis health check.
# REDIS_PASSWORD must be supplied by the Ansible Vault-backed deployment environment.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
# Expected result:
# PONG

# Verify Redis server information.
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server

# Verify the configured Redis port.
redis-cli -p 6379 -a "$REDIS_PASSWORD" CONFIG GET port
# Expected result:
# port
# 6379

# Verify the Redis configuration cleanup.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected result: no matching lines

# Review Redis logs using the validated service unit.
journalctl -u <validated-redis-service-unit> --since "15 minutes ago"

# Verify Redis write, read, and delete operations.
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET migration_health_check ok
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET migration_health_check
redis-cli -p 6379 -a "$REDIS_PASSWORD" DEL migration_health_check
# Expected read result:
# ok

# Verify the Redis process and port ownership.
ps aux | grep '[r]edis'
lsof -iTCP:6379 -sTCP:LISTEN
```

Memcached-specific pre-flight checks cannot be defined because the `memcached` recipe is missing and no Memcached port, service, configuration file, or template appears in the supplied execution tree.