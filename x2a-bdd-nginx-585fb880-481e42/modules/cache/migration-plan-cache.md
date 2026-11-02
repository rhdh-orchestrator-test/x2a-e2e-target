---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis instance on port `6379`, creates `/var/log/redis`, assigns a Redis authentication password, removes five replication-related directives from `/etc/redis/6379.conf`, and intends to enable Redis. The `memcached`, `redisio`, and `redisio::enable` recipes are referenced dependencies but are absent from the supplied execution tree. Their packages, templates, service names, and exact behavior must be resolved before migration. The Redis password must be moved from plaintext Chef attributes to Ansible Vault or an approved secret manager.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication is configured with `requirepass`; the source value is `redis_secure_password_123` and must be migrated securely. The `replicaservestaledata` attribute is explicitly set to `nil`.
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` when present.

- **Memcached**: Intended dependency, not a configured instance in the supplied execution tree
  - Location/Path: Not determined
  - Port/Socket: Not determined
  - Key Config: The `memcached` recipe is referenced and declared as dependency `~> 6.0`, but its recipe is missing. Do not create Memcached configuration until the dependency is obtained and analyzed.

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

No template files are shown in the execution tree.

**Attributes:**
```text
```

No attribute files are shown in the execution tree. The Redis server collection is assigned directly inside `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` are shown.

## Module Explanation

The cookbook performs operations in this order:

1. `memcached` recipe — not found in the supplied execution tree.
2. `directory[/var/log/redis]`
3. `redisio` recipe — not found in the supplied execution tree.
4. `ruby_block[fix_redis_config]`
5. `redisio::enable` recipe — not found in the supplied execution tree.

### 1. `cache::default` (`cookbooks/cache/recipes/default.rb`)

- Assigns the Redis server collection:
  - Instance port: `6379`
  - `requirepass`: `redis_secure_password_123`
  - `replicaservestaledata`: `nil`
- Attempts to include the external `memcached` recipe.
- Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
- Attempts to include the external `redisio` recipe.
- Defines `ruby_block[fix_redis_config]`.
- Attempts to include the external `redisio::enable` recipe.
- No `.each` loops are shown in the supplied recipe, so there are no additional loop iterations to expand.

### 2. `memcached` dependency recipe — not found

- The cookbook metadata declares dependency `memcached`, version `~> 6.0`.
- The referenced recipe is absent from the supplied execution tree.
- Package names, configuration paths, service names, ports, templates, and resources cannot be determined.
- Do not claim that Memcached is installed or create Memcached Ansible tasks from this cookbook alone.

### 3. `directory[/var/log/redis]` (`cookbooks/cache/recipes/default.rb`)

- Creates `/var/log/redis`.
- Enables recursive directory creation.
- Sets owner to `redis`.
- Sets group to `redis`.
- Sets mode to `0755`.
- The supplied recipe does not create the `redis` user or group. The migration must verify that the Redis dependency or target package creates them.

### 4. `redisio` dependency recipe — not found

- The cookbook metadata declares dependency `redisio` without a version constraint.
- The referenced recipe is absent from the supplied execution tree.
- Package names, configuration templates, generated configuration contents, service resources, and service names cannot be determined.
- The Redis installation and configuration implementation must be specified or analyzed separately before migration.

### 5. `ruby_block[fix_redis_config]` (`cookbooks/cache/recipes/default.rb`)

The block operates on `/etc/redis/6379.conf`:

- Checks whether the file exists.
- Reads the complete file when present.
- Removes lines matching:
  - `^replica-serve-stale-data.*$`
  - `^replica-read-only.*$`
  - `^repl-ping-replica-period.*$`
  - `^client-output-buffer-limit.*$`
  - `^replica-priority.*$`
- Writes the modified content back to `/etc/redis/6379.conf`.
- Does nothing when the file does not exist.

The Ansible migration should preferably control the complete Redis configuration through a template. If post-generation cleanup is required, use explicit `ansible.builtin.replace` tasks after the Redis dependency creates the file. Any Redis restart or reload should occur only when configuration changes, and the supplied recipe does not establish an automatic service notification.

### 6. `redisio::enable` dependency recipe — not found

- Intended to enable Redis at system startup.
- The exact service resource and service name are unavailable.
- Do not assume the service is named `redis`, `redis-server`, or an instance-specific unit.
- Resolve the service name from the missing dependency or the target operating system before managing enabled or running state.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- None are declared by resources in the supplied execution tree.
- No package name can be verified because the `memcached` and `redisio` recipes are missing.

**Service dependencies**:

- Redis enablement is intended through the missing `redisio::enable` recipe.
- The Redis service name is unresolved.
- Memcached service behavior is unresolved because its recipe is missing.

**Platform support declared in metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`
- **Migration handling**: Store the password in Ansible Vault or an approved external secret manager. Do not place it in ordinary role defaults, public templates, unencrypted group variables, or task output.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret reference, TLS certificate, private key, or database connection string was detected in the supplied source.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis server on TCP port `6379`
- Unix sockets: none identified
- Network interface binding: not specified

**Templates rendered**:

- None shown in the execution tree.

**Redis server on port 6379 checks**:

- Redis configuration exists at `/etc/redis/6379.conf`.
- Redis authentication is enabled using the vaulted password.
- The configuration contains port `6379`.
- The five unwanted replication-related directives are absent.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- The resolved Redis service is enabled and active.
- Redis accepts authenticated commands and rejects unauthenticated commands.

**Memcached checks**:

- Not applicable until the missing `memcached` dependency is obtained and analyzed.
- No Memcached package, service, endpoint, configuration path, template, or health-check command is available from the supplied source.

## Pre-flight checks:

```bash
# Verify the Redis configuration file
test -f /etc/redis/6379.conf
```

```bash
# Verify the Redis log directory
stat -c '%A %U %G %n' /var/log/redis
# Expected: directory owned by redis:redis with mode 0755
```

```bash
# Verify the Redis user and group exist
getent passwd redis
getent group redis
```

```bash
# Check Redis service status after resolving the service name
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>
```

```bash
# Verify Redis is listening on the configured port
ss -ltnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN
```

```bash
# Verify the configured Redis port
grep -E '^[[:space:]]*port[[:space:]]+6379' /etc/redis/6379.conf
```

```bash
# Verify unwanted replication directives were removed
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected replication directives remain"
  exit 1
else
  echo "Unwanted replication directives are absent"
fi
```

```bash
# Verify authenticated Redis access
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
# Expected: PONG
```

```bash
# Verify unauthenticated access is rejected
redis-cli -p 6379 PING
# Expected: an authentication error, not PONG
```

```bash
# Verify authenticated Redis operation
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET migration_probe "ok"
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET migration_probe
# Expected: ok
redis-cli -p 6379 -a "$REDIS_PASSWORD" DEL migration_probe
```

```bash
# Inspect Redis log files
find /var/log/redis -maxdepth 1 -type f -print
```

```bash
# Check recent Redis service logs after resolving the service name
journalctl -u <redis-service-name> --no-pager -n 100
```

```bash
# Verify Redis process and memory state
pgrep -a redis
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO memory
```

Do not replace `<redis-service-name>` with an invented name. Resolve it from the `redisio` dependency implementation or the target distribution’s Redis package. Supply `REDIS_PASSWORD` through a secure environment or secret mechanism rather than placing the password directly in shell history.

Memcached-specific pre-flight checks must not be added until the missing `memcached` dependency is analyzed.