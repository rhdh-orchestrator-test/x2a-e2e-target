---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The analyzed recipe creates `/var/log/redis`, defines one Redis server on port `6379` with hardcoded authentication, includes Redis enablement, and removes five replication-related directives from `/etc/redis/6379.conf`. The external Memcached and Redis recipe implementations were not present, so their package names, service names, configuration paths, and Memcached port must be verified before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Log directory: `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config:
    - Authentication enabled with `requirepass`
    - Password currently hardcoded in `cookbooks/cache/recipes/default.rb`
    - `replicaservestaledata`: `nil`
    - Remove `replica-serve-stale-data`
    - Remove `replica-read-only`
    - Remove `repl-ping-replica-period`
    - Remove `client-output-buffer-limit`
    - Remove `replica-priority`

- **Memcached**: Memcached instance included through the external `memcached` recipe
  - Location/Path: Not available in the analyzed execution tree
  - Port/Socket: Not available in the analyzed execution tree
  - Package: Not available in the analyzed execution tree
  - Service name: Not available in the analyzed execution tree
  - Key Config:
    - No Memcached-specific resources are present in the analyzed recipe
    - Obtain the package, configuration path, service name, and listening port from the external `memcached` cookbook
    - Do not infer a Memcached port or configuration path from this cookbook

## File Structure

Only the recipe file shown in the execution tree is listed. The metadata file was read for service description and dependencies but is not included because the execution-tree validation requires only `.rb` files shown in the tree.

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

The following external recipe files are referenced but were not present in the execution tree and must not be represented as cookbook files for this migration:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Defines one Redis server configuration for port `6379`.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - Removes selected directives from `/etc/redis/6379.conf` when the file exists.
   - Includes the external `redisio::enable` recipe.

   **Memcached inclusion**:
   - Chef operation: `include_recipe 'memcached'`
   - Execution-tree status: `memcached` recipe file not found.
   - The analyzed cookbook does not identify the Memcached package, configuration path, service name, or port.
   - The Ansible migration must obtain these values from the external `memcached` cookbook used by the migration environment.
   - No Memcached-specific resources are present in `cookbooks/cache/recipes/default.rb`.

   **Redis server configuration**:
   - The recipe defines one Redis server item:
     - Port: `'6379'`
     - `requirepass`: `'redis_secure_password_123'`
     - `replicaservestaledata`: `nil`
   - Generate the Redis configuration at `/etc/redis/6379.conf`.
   - Store the authentication password in Ansible Vault rather than a regular variable file.
   - Preserve port `6379` in the configuration path and service configuration.

   **Redis log directory**:
   - Chef resource: `directory['/var/log/redis']`
   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled

   Ansible equivalent:
   ```yaml
   - name: Create Redis log directory
     ansible.builtin.file:
       path: /var/log/redis
       state: directory
       owner: redis
       group: redis
       mode: "0755"
       recurse: true
   ```

   **Redis inclusion**:
   - Chef operation: `include_recipe 'redisio'`
   - Execution-tree status: `redisio` recipe file not found.
   - The external recipe is expected to install and configure Redis using the server definition.
   - Its package name, service resource, templates, and exact configuration behavior are unavailable.
   - Verify the external cookbook and target operating system before selecting package and service names.

   **Redis configuration post-processing**:
   - Chef resource: `ruby_block['fix_redis_config']`
   - Configuration file: `/etc/redis/6379.conf`
   - The block checks whether the file exists before processing it.
   - When present, it removes complete lines matching:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The migration must remove the entire matching line, including its directive and value, without deleting unrelated configuration.
   - Prefer generating the final configuration without these directives.
   - If the external Redis role generates them, use a narrowly scoped replacement or line-removal task conditional on `/etc/redis/6379.conf` existing.

   **Redis enablement**:
   - Chef operation: `include_recipe 'redisio::enable'`
   - Execution-tree status: `redisio::enable` recipe file not found.
   - Enable and start the Redis service associated with port `6379`.
   - Determine the exact service name from the external `redisio` cookbook or target host.
   - Start the service only after `/etc/redis/6379.conf` has been rendered and corrected.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, without a version constraint

**System package dependencies**:

- No packages are explicitly installed by the analyzed recipe.
- The Memcached and Redis package names are not available in the analyzed execution tree.
- Obtain package names from the external cookbook implementations or verified target-operating-system package mappings.
- Do not invent package names.

**Service dependencies**:

- Memcached service behavior is delegated to the external `memcached` cookbook.
- Redis installation and configuration behavior is delegated to the external `redisio` cookbook.
- Redis service enablement is delegated to the external `redisio::enable` recipe.
- The analyzed source explicitly references Redis configuration on TCP port `6379`.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded
- **URL**: None detected
- **Path**: None detected
- **Source file**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Literal value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the Redis server listening on port `6379`
- **Migration handling**:
  - Move the password to Ansible Vault.
  - Reference the vaulted variable when rendering `/etc/redis/6379.conf`.
  - Do not commit the plaintext password to the Ansible repository.
  - Restrict permissions on the generated Redis configuration because it contains the password.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database connection strings, or additional credential namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis server on TCP port `6379`
- Memcached endpoint: port not specified in the analyzed source
- Unix sockets: none specified
- Network interface binding: not specified

**Templates rendered**:

- None

**Configuration post-processing**:

- `/etc/redis/6379.conf` is read and modified once by `ruby_block['fix_redis_config']`, if the file exists.
- The following directives must not remain:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

The exact external service names for Redis and Memcached are unavailable. Replace the placeholders only after verifying the external cookbook implementations or target host.

### Redis server on port 6379

**Service status**:

```bash
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>
```

Expected result:

- The Redis service is enabled.
- The Redis service is active.
- The service is configured for port `6379`.

**Configuration validation**:

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf
```

Expected result:

- `/etc/redis/6379.conf` exists.
- The file contains `port 6379`.
- The file contains the migrated Redis password configuration without exposing the password in command output or logs.

Verify removal of the five directives:

```bash
! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result:

- The command exits successfully.
- None of the five directives are present.

**Authentication and connectivity**:

```bash
read -r REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD
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

- The command does not return an unauthenticated `PONG`.
- Redis reports that authentication is required.

**Listening-port verification**:

```bash
ss -tlnp | grep ':6379'
netstat -tulpn 2>/dev/null | grep ':6379'
```

Expected result:

- A Redis process is listening on TCP port `6379`.

**Log-directory verification**:

```bash
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis
```

Expected result:

- Directory: `/var/log/redis`
- Owner: `redis`
- Group: `redis`
- Permissions: `0755`

**Service logs**:

```bash
journalctl -u <redis-service-name> --no-pager -n 100
journalctl -u <redis-service-name> --no-pager -n 100 | grep -Ei 'error|fatal|permission|bind|6379'
```

Check for configuration, permission, binding, and startup errors.

### Memcached

The analyzed source does not specify the Memcached service name, port, configuration path, or package name. Verify these values from the external `memcached` cookbook before running endpoint checks.

**Service status**:

```bash
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>
```

Expected result:

- The verified Memcached service is enabled.
- The verified Memcached service is active.

**Endpoint verification**:

```bash
ss -tlnp
```

Confirm the verified Memcached service is listening on the port obtained from the external cookbook. Do not substitute an assumed port or service name.

## Migration Ordering

1. Load the Redis password from Ansible Vault.
2. Install the Redis and Memcached packages identified from the external cookbook behavior.
3. Create the `redis` user and group if they are not created by the selected Redis package.
4. Create `/var/log/redis` with owner `redis`, group `redis`, and mode `0755`.
5. Render `/etc/redis/6379.conf` for the Redis server on port `6379`.
6. Configure Redis authentication using the vaulted password.
7. Ensure the five unwanted replication-related directives are absent.
8. Enable and start the verified Redis service.
9. Configure and enable Memcached using values confirmed from the external `memcached` cookbook.
10. Run the Redis authentication, port, configuration, service, and log checks.
11. Run the verified Memcached service and endpoint checks.