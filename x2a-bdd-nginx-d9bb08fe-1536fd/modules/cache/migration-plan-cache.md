---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services, with the supplied recipe analysis reporting one Redis instance named by port **6379**. The visible recipe includes Memcached, configures RedisIO, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and enables Redis through dependency recipes that are not present in the supplied execution tree. Redis authentication is reported as configured with a hardcoded password that must be moved to Ansible Vault or an approved secret manager. Memcached and RedisIO package, service, and template details require verification from the missing dependency cookbooks.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache listener
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is reported as enabled; `replicaservestaledata` is reported as `nil`; selected replication-related directives are removed from the configuration after RedisIO renders it.
  - Log directory: `/var/log/redis`
  - Configuration status: The instance definition and values are reported by the supplied plan but require confirmation against the recipe source or detailed attribute analysis.

**Memcached**: The `memcached` dependency recipe is referenced but is not present in the supplied execution tree. Its instance name, port, configuration path, package, authentication settings, and service name cannot be determined without inventing data.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
cookbooks/cache/recipes/default.rb

Providers:

Templates:

Attributes:

Files:
```

`metadata.rb` was read for service identification and dependency metadata, but it is not listed as an executed recipe file or migration artifact under the supplied file-structure rules.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` dependency recipe.
   - The execution tree reports `memcached Recipe file not found`.
   - Preserve this dependency only after obtaining the intended Memcached cookbook or collection.
   - The supplied data does not establish the Memcached package, service, configuration path, port, or management behavior.

2. **default** (`cookbooks/cache/recipes/default.rb`):
   - Assigns a RedisIO server collection reported to contain one Redis item:
     - Instance: Redis on port `6379`
     - Port: `6379`
     - Authentication password: `redis_secure_password_123`
     - Replica stale-data setting: `null`
   - Store the password in Ansible Vault or an approved external secret manager rather than a plaintext variable file.
   - The exact assignment and collection behavior require confirmation against the recipe source or detailed attribute analysis.

3. **default** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - The supplied plan reports owner `redis`, group `redis`, mode `0755`, and recursive creation enabled; these attributes require confirmation against the recipe source.
   - Implement the verified behavior with `ansible.builtin.file`.
   - No independent `group[redis]` resource is confirmed by the execution tree; do not add one unless required by the target Redis installation.

4. **redisio** (`cookbooks/cache/recipes/redisio.rb`, dependency recipe not present):
   - Is included after the Redis server configuration is assigned.
   - Is responsible for installing and configuring RedisIO-managed Redis instances.
   - The dependency recipe is missing, so package names, package versions, service names, data directories, ownership, configuration templates, and rendering behavior cannot be determined.
   - Obtain the dependency implementation before creating installation and configuration tasks.

5. **default** (`cookbooks/cache/recipes/default.rb`):
   - Executes `ruby_block[fix_redis_config]`.
   - The supplied plan reports that the block targets `/etc/redis/6379.conf`.
   - When the file exists, it removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - When the file does not exist, it performs no action.
   - These target and pattern details require confirmation against the recipe source or detailed resource analysis.
   - Implement verified behavior with an idempotent `ansible.builtin.replace` or equivalent task.

6. **redisio::enable** (`cookbooks/cache/recipes/redisio/enable.rb`, dependency recipe not present):
   - Is included after Redis configuration and cleanup.
   - Represents the Redis enablement step.
   - The exact service unit and whether the dependency starts, enables, or both cannot be determined until the missing recipe is obtained.
   - Map the verified behavior to `ansible.builtin.service` or `ansible.builtin.systemd`.

**Iterations**: No verified `.each` loop or collection iteration is available in the supplied execution tree. The supplied plan reports one Redis item named by port `6379`; confirm the collection logic against the recipe source before implementation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint reported as `~> 6.0`; verify against `metadata.rb`
- `redisio`, with no version constraint reported; verify against `metadata.rb`

**System package dependencies**: Not determinable from the supplied execution tree. The visible recipe contains no `package` resource. Package names may be declared by the missing `memcached` and `redisio` dependency recipes.

**Service dependencies**:

- Redis enablement is delegated to the missing `redisio::enable` recipe.
- Memcached service management is delegated to the missing `memcached` recipe.
- No explicit service resource is visible in `cookbooks/cache/recipes/default.rb`.

**Supported platforms reported by metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential reported in 1 recipe file; confirm against the recipe source or credential analysis.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as hardcoded directly in the Chef recipe
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the Redis instance listening on TCP port `6379`
- **Migration handling**:
  - Store the value in Ansible Vault or an approved external secret-management system.
  - Render it into Redis configuration without exposing it in task output.
  - Use `no_log: true` for tasks whose arguments or output could contain the password.
  - Do not commit the literal password to a plaintext variable file.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, `node['vault']`, or `node['secrets']` usage is identified in the supplied recipe analysis. No TLS certificate, private key, database connection string, API token, or environment-variable secret reference is identified.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

The Redis data directory and exact Redis log file are not specified. Do not invent them.

**Service endpoints to check**:

- Redis instance on port `6379`
- Unix sockets: none identified
- Network interface binding: not identified

Memcached endpoints cannot be listed until the missing dependency recipe is obtained.

**Templates rendered**:

- None identified in the supplied file structure.
- No `.erb` templates are present in the supplied execution tree.
- Redis configuration is expected to be generated by the missing `redisio` dependency, but its template path and render count are unavailable.
- No Memcached templates are available for verification.

**Configuration directives to verify as absent for the Redis instance on port 6379**:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

Run the following checks for the named Redis instance. Replace the service placeholder only after inspecting the missing `redisio::enable` recipe.

```bash
# Redis instance: port 6379
test -f /etc/redis/6379.conf

# Verify the selected directives are absent
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected result: no matching lines

# Verify the Redis log directory
stat -c '%A %U:%G %n' /var/log/redis
# Expected result when the reported attributes are confirmed:
# mode 0755 and owner/group redis:redis

# Verify the Redis listener for the 6379 instance
ss -ltnp | grep ':6379'
# Expected result: Redis is listening on TCP port 6379

# Verify unauthenticated behavior without exposing the password
redis-cli -p 6379 PING
# Expected result when authentication is enabled:
# NOAUTH Authentication required

# Verify authenticated connectivity using a securely retrieved password
redis-cli -p 6379 -a '<retrieve-from-secure-secret-store>' PING
# Expected result: PONG

# Verify Redis server information
redis-cli -p 6379 -a '<retrieve-from-secure-secret-store>' INFO server
# Expected result: Redis server information is returned

# Verify authentication is configured without sharing the returned password
redis-cli -p 6379 -a '<retrieve-from-secure-secret-store>' CONFIG GET requirepass
# Expected result: requirepass is configured; do not print the password in shared logs

# Verify core Redis configuration
grep -nE '^(port|requirepass)' /etc/redis/6379.conf
# Expected result: port 6379 and a configured requirepass directive

# Verify the confirmed Redis service unit
journalctl --no-pager -n 100 -u '<confirmed-redis-service-name>'
# Expected result: no startup or configuration errors

# Confirm the missing dependencies before finalizing the migration
# - Obtain the memcached recipe and identify its package, service, port, and configuration.
# - Obtain the redisio recipe and identify its package, service, data path, and template.
# - Obtain the redisio::enable recipe and identify its exact enable/start behavior.
```