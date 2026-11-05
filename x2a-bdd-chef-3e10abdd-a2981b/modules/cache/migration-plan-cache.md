---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services, primarily one Redis instance on port `6379`, and references external Memcached and Redis dependency recipes. The available recipe creates `/var/log/redis`, configures Redis authentication with a hardcoded password, removes selected replication directives from `/etc/redis/6379.conf`, and attempts to enable Redis. The `memcached`, `redisio`, and `redisio::enable` recipe implementations are not present in the supplied execution tree, so their package names, service names, and detailed behavior require verification before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance configured through the external `redisio` cookbook
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config:
    - Redis owner/group: `redis:redis`
    - Log directory: `/var/log/redis`
    - Log directory mode: `0755`
    - Authentication enabled with the recipe-declared password `redis_secure_password_123`
    - `replicaservestaledata` set to `nil`
    - Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` directives

- **Memcached**: External dependency reference only; no configured Memcached instance can be confirmed from the supplied execution tree
  - Location/Path: Not specified
  - Port/Socket: Not specified
  - Key Config: The `memcached` recipe is included, but its package, service, port, configuration file, and resources are unavailable

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No custom resources or provider files were shown in the execution tree.

**Templates:**
```text
```

No templates were shown or rendered.

**Attributes:**
```text
```

No attribute files were shown. The Redis configuration is assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files were shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - The `memcached` recipe is not present in the supplied execution tree.
   - Assigns one Redis server configuration item:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - No `.each` loop is present. The configured collection contains one Redis item, identified by port `6379`.
   - Creates `directory[/var/log/redis]`:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive: `true`
   - Attempts to include the external `redisio` recipe.
   - The `redisio` recipe is not present in the supplied execution tree. Its package installation, user creation, configuration rendering, and service behavior require verification.
   - Runs `ruby_block[fix_redis_config]`:
     - Examines `/etc/redis/6379.conf` if the file exists.
     - Removes complete lines beginning with:
       - `replica-serve-stale-data`
       - `replica-read-only`
       - `repl-ping-replica-period`
       - `client-output-buffer-limit`
       - `replica-priority`
     - Writes the modified content back to `/etc/redis/6379.conf`.
     - Makes no change if the file does not exist.
   - Attempts to include `redisio::enable`.
   - The `redisio::enable` recipe is not present in the supplied execution tree. Its intended behavior is to enable Redis at boot, but the actual service unit name is unavailable.
   - Execution order:
     1. Include `memcached`
     2. Assign the Redis configuration for port `6379`
     3. Create `/var/log/redis`
     4. Include `redisio`
     5. Run `ruby_block[fix_redis_config]`
     6. Include `redisio::enable`

## Dependencies

**External cookbook dependencies**:

- `memcached`, declared version constraint `~> 6.0`
- `redisio`, with no version constraint shown
- `redisio::enable`, a recipe reference within the `redisio` dependency

The dependency references are present in the supplied plan, but the external cookbook implementations are not available for inspection.

**System package dependencies**:

- Not determinable from the available cookbook files.
- Package installation is expected to be handled by the missing `memcached` and `redisio` recipes.
- Do not infer exact package names from the cookbook dependency names.

**Service dependencies**:

- Redis service enablement is attempted through the missing `redisio::enable` recipe.
- The exact Redis service unit name is unavailable.
- Memcached service management is unavailable because the `memcached` recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe
- **Value in Chef source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance on port `6379`
- **Ansible migration guidance**:
  - Store the value in Ansible Vault, preferably as `redis_password`.
  - Do not commit the literal password to Ansible tasks or templates.
  - Use secret-safe handling, including `no_log: true` for tasks that could expose the password.

No data bags, encrypted data bags, Chef Vault items, CyberArk integration, Conjur variables, environment-variable secrets, TLS certificate references, database connection strings, or additional credential namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

The Redis data directory, log file name, and service unit path are not defined in the available cookbook and must be obtained from the `redisio` dependency or target distribution.

**Service endpoints to check**:

- Redis server on port `6379`
- Memcached endpoint: Not specified by the analyzed cookbook
- Unix sockets: None specified
- Network interfaces: None specified

**Templates rendered**:

- None rendered; render count: `0`

**Configuration cleanup operations**:

Verify that `/etc/redis/6379.conf` does not contain lines beginning with:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Redis instance on port 6379: configuration file
if test -f /etc/redis/6379.conf; then
  grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
fi
```

The `grep` command should return no matching lines after the configuration cleanup task. If the file is absent, the Chef cleanup block makes no change.

```bash
# Redis instance on port 6379: listening socket
ss -tlnp | grep ':6379'
```

Port `6379` should be listening and associated with the Redis process.

```bash
# Redis instance on port 6379: unauthenticated connectivity
redis-cli -p 6379 ping
```

An authentication error is expected when Redis requires authentication.

```bash
# Redis instance on port 6379: authenticated connectivity
redis-cli -p 6379 -a "$REDIS_PASSWORD" ping
```

Expected result:

```text
PONG
```

Use a protected environment or secret mechanism for `REDIS_PASSWORD`; do not place the literal password in shell history or committed documentation.

```bash
# Redis instance on port 6379: authentication behavior
redis-cli -p 6379 -a "$REDIS_PASSWORD" CONFIG GET requirepass
```

Confirm that a password is configured without exposing the returned value in shared logs.

```bash
# Redis instance on port 6379: log directory ownership and mode
stat -c '%U:%G %a %n' /var/log/redis
```

Expected result:

```text
redis:redis 755 /var/log/redis
```

```bash
# Redis instance on port 6379: configuration readability
ls -l /etc/redis/6379.conf
test -r /etc/redis/6379.conf
```

```bash
# Redis instance on port 6379: service status
systemctl status <redis-service-name>
```

Replace `<redis-service-name>` with the actual service unit name supplied by the `redisio` dependency.

```bash
# Redis instance on port 6379: recent service logs
journalctl -u <redis-service-name> --no-pager -n 50
```

Use the confirmed Redis service unit name.

```bash
# Redis instance on port 6379: configuration validation
redis-server /etc/redis/6379.conf --test-memory 2
```

Use the distribution-supported Redis configuration validation method if the installed Redis version does not support this command form. The validation must target `/etc/redis/6379.conf`.

**Memcached validation**:

The cookbook includes `memcached`, but no Memcached recipe or resource is present in the supplied execution tree. Do not define a Memcached port, service name, configuration file, package name, or health check until the external `memcached` cookbook or replacement implementation has been inspected.