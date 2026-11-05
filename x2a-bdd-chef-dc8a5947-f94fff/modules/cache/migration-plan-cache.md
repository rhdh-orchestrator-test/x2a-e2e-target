---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through Memcached and Redis. The only local recipe is `cookbooks/cache/recipes/default.rb`; the referenced `memcached`, `redisio`, and `redisio::enable` recipes are external dependencies and are not present in the supplied execution tree. The local recipe attempts to include Memcached, defines one Redis server on port `6379` with authentication, creates `/var/log/redis`, includes Redis configuration, removes specified replication-related directives from `/etc/redis/6379.conf`, and finally enables Redis. The Ansible migration must preserve this order, move the Redis password to Ansible Vault or an approved secret store, and resolve the missing dependency implementations before claiming complete parity.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance configured through `node['redisio']['servers']`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled; `replicaservestaledata` is unset/null; replication-related directives are removed after Redis configuration generation
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`

- **Memcached**: External Memcached instance included through the missing `memcached` recipe
  - Location/Path: Not specified in the analyzed cookbook
  - Port/Socket: Not specified in the analyzed cookbook
  - Key Config: Package, service, port, configuration path, and templates must be obtained from the external `memcached` cookbook before migration completion
  - Status: Unresolved external dependency; no local implementation is present

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

The following referenced recipes are not present in the supplied execution tree:

- `memcached`
- `redisio`
- `redisio::enable`

They must not be represented as local cookbook files unless their dependency sources are separately supplied.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe first.
   - Defines exactly one Redis server on port `6379`.
   - Configures the Redis `requirepass` attribute and leaves `replicaservestaledata` unset/null.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe to install and configure Redis.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` when the file exists.
   - Includes the external `redisio::enable` recipe last to enable Redis.
   - Resources used:
     - `directory`: 1
     - `ruby_block[fix_redis_config]`: 1
   - Files modified:
     - `/var/log/redis`
     - `/etc/redis/6379.conf`
   - Templates rendered: None
   - Iterations: No `.each` loops are present. The Redis server collection contains exactly one item:
     - Port: `6379`
     - Password attribute: `requirepass`
     - Password value in the source cookbook: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`

   **Execution details:**

   - **External `memcached` inclusion**:
     - The recipe executes `include_recipe 'memcached'`.
     - The implementation is not present in the supplied execution tree.
     - Do not infer Memcached package names, ports, service names, configuration files, or templates.
     - Preserve this as the first logical operation and resolve the external dependency separately.

   - **Redis server definition**:
     - The source defines one Redis instance on port `6379`.
     - Redis authentication is enabled through `requirepass`.
     - The plaintext source value must not be copied into Ansible role defaults or tasks.
     - Store the migrated password in Ansible Vault or an approved external secret backend.

   - **Redis log directory creation**:
     - Create `/var/log/redis` recursively.
     - Set owner to `redis`.
     - Set group to `redis`.
     - Set mode to `0755`.
     - Ensure the Redis user and group exist before ownership is applied. Their creation is expected from the external Redis dependency or the target operating system package because no local user or group resource is present.

   - **External `redisio` inclusion**:
     - The recipe executes `include_recipe 'redisio'`.
     - The implementation is not present in the supplied execution tree.
     - Confirm the external dependency’s package and service behavior before implementation.
     - Confirmed local behavior includes:
       - Redis on port `6379`
       - Redis authentication
       - Configuration file `/etc/redis/6379.conf`
       - Log directory `/var/log/redis`

   - **`ruby_block[fix_redis_config]`**:
     - Check whether `/etc/redis/6379.conf` exists.
     - If it exists, remove complete lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Write the modified file back.
     - Do not fail solely because the configuration file does not exist.
     - Restart or reload Redis only when the migrated configuration task changes the file and the resolved Redis dependency requires it.

   - **External `redisio::enable` inclusion**:
     - The recipe executes `include_recipe 'redisio::enable'` last.
     - The implementation is not present in the supplied execution tree.
     - Resolve the actual Redis service name from the external dependency or target operating system before configuring service enablement and startup.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- Not determinable from the available local recipe.
- Package installation is expected to be handled by the missing `memcached` and `redisio` recipes.
- Do not claim package names until confirmed from the dependency implementations or target platform.

**Service dependencies**:

- Memcached service behavior is delegated to the missing `memcached` recipe.
- Redis installation and configuration behavior is delegated to the missing `redisio` recipe.
- Redis enablement is delegated to the missing `redisio::enable` recipe.
- The exact Redis and Memcached service unit names are not present in the analyzed files.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the Redis instance listening on TCP port `6379`
- **Migration storage**: Ansible Vault or an approved external secret backend
- **Migration variable**: For example, `redis_requirepass`
- **Migration requirements**:
  - Do not expose the secret in task output.
  - Render the Redis configuration using the vaulted value.
  - Apply appropriate permissions to the Redis configuration file.
  - Do not retain the source plaintext value in Ansible role files or defaults.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret, TLS certificate, private key, database connection string, or external vault URL was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis TCP port `6379`
- Memcached endpoint: port not specified by the analyzed cookbook
- Unix sockets: none specified
- Network interface binding: not specified

**Templates rendered**:

- None; render count: `0`

**Configuration mutations to verify**:

`/etc/redis/6379.conf` must not contain lines beginning with:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

**Dependency verification**:

- Confirm the external Memcached package, service, port, configuration path, and templates.
- Confirm the external Redis package and service name.
- Confirm the Redis user and group used for `/var/log/redis`.
- Confirm the service behavior implemented by `redisio::enable`.

## Pre-flight checks

The exact Redis and Memcached service names must be substituted after the external dependency implementations or target platform are confirmed.

### Redis instance on port 6379

```bash
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>
ps aux | grep '[r]edis'
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN
```

Expected results:

- The Redis service is enabled.
- The Redis service is active.
- A Redis process is listening on TCP port `6379`.

### Redis authentication

Use the migrated vaulted password without printing it in shell history or logs:

```bash
redis-cli -p 6379 -a "$REDIS_REQUIREPASS" PING
```

Expected result:

```text
PONG
```

Verify that unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result:

- The command fails with an authentication-required response.

### Redis configuration

```bash
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Verify that all cleanup patterns are absent:

```bash
! grep -Eq '^replica-serve-stale-data.*$' /etc/redis/6379.conf
! grep -Eq '^replica-read-only.*$' /etc/redis/6379.conf
! grep -Eq '^repl-ping-replica-period.*$' /etc/redis/6379.conf
! grep -Eq '^client-output-buffer-limit.*$' /etc/redis/6379.conf
! grep -Eq '^replica-priority.*$' /etc/redis/6379.conf
```

### Redis log directory

```bash
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis
```

Expected result:

```text
drwxr-xr-x redis redis /var/log/redis
```

Verify:

- Mode is `0755`.
- Owner is `redis`.
- Group is `redis`.

### Memcached instance

The Memcached recipe is external and does not specify a port, package, configuration path, or service name in the supplied execution tree. Resolve those values from the external dependency before running instance-specific checks:

```bash
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>
```

After the dependency is resolved, verify its confirmed listening port:

```bash
ss -tlnp | grep ':<memcached-port>'
netstat -tulpn | grep ':<memcached-port>'
lsof -iTCP:<memcached-port> -sTCP:LISTEN
```

Do not mark the Memcached migration complete until its package, service, port, and configuration behavior have been confirmed.