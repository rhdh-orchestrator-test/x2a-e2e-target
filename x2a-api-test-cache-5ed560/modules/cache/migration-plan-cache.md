---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services through the `memcached` and `redisio` dependencies. The analyzed recipe includes the `memcached` dependency, assigns one Redis server definition on port `6379` with a hardcoded password, creates `/var/log/redis`, includes `redisio`, removes five replication-related directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. The dependency recipes are not present in the execution tree, so Memcached package, port, configuration, and service details, as well as Redis package and service-unit details, must be confirmed before implementing the Ansible role. The Redis values and credential details reported below require verification against the recipe source and dependency cookbooks.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server definition on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is reported as `redis_secure_password_123`; the following directives are removed from the configuration: `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Redis service enablement: Requested through `redisio::enable`
  - Verification status: Port, configuration path, password, directory properties, and directive-removal behavior must be confirmed against `cookbooks/cache/recipes/default.rb`

- **Memcached dependency instance**: Memcached service referenced by the cookbook
  - Location/Path: Not specified
  - Port/Socket: Not specified
  - Key Config: Included through the external `memcached` recipe
  - Package name: Not specified
  - Service name: Not specified
  - Verification status: Confirm from the `memcached` dependency cookbook or target environment before implementation

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

The referenced `memcached`, `redisio`, and `redisio::enable` recipes are not present in the execution tree and are therefore not listed as cookbook files.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Assigns one Redis server item to `node['redisio']['servers']`.
   - Creates `/var/log/redis`.
   - Includes the external `redisio` recipe.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes the external `redisio::enable` recipe.

   **Memcached dependency inclusion**:
   - Executes `include_recipe 'memcached'`.
   - The dependency recipe is not present in the execution tree.
   - Preserve the dependency ordering by handling Memcached before Redis if Memcached is required.
   - Do not invent the Memcached package name, port, configuration path, listen address, or service name.
   - Confirm the dependency behavior before creating Ansible tasks.

   **Redis server collection**:
   - The reported assignment contains one item:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Represent this as one Redis instance in Ansible.
   - Store the password in Ansible Vault.
   - Confirm the assignment and password against the recipe source before migration because the validation summary does not independently show these values.

   **Redis log directory**:
   - Creates `/var/log/redis`.
   - The reported properties are:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation: enabled
   - Implement with `ansible.builtin.file`.
   - Confirm the owner, group, mode, and recursive setting against the source declaration before treating them as authoritative.

   **Redis dependency inclusion**:
   - Executes `include_recipe 'redisio'`.
   - The dependency recipe is not present in the execution tree.
   - Configure the reported Redis instance on port `6379` only after confirming the dependency behavior.
   - Manage `/etc/redis/6379.conf` only if that path is confirmed by the recipe or dependency cookbook.
   - Configure authentication through a vaulted variable.
   - Do not invent Redis package versions or service-unit names.

   **`ruby_block[fix_redis_config]`**:
   - The reported block operates on `/etc/redis/6379.conf`.
   - If the file exists, it reads the file, removes matching lines, and writes the modified content back.
   - The reported regular expressions are:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - If the file does not exist, the block does nothing.
   - Implement the confirmed behavior with one `ansible.builtin.replace` task per directive, or a carefully scoped equivalent.
   - Confirm the file path and expressions against the Ruby block source before implementation.
   - The Chef block does not explicitly notify or restart Redis.

   **Redis enablement**:
   - Executes `include_recipe 'redisio::enable'`.
   - The dependency recipe is not present in the execution tree.
   - Enable and start the Redis instance only after confirming the service behavior.
   - Do not invent the exact systemd service name.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- No package resources or verified package names are present in the analyzed execution tree.
- Memcached and Redis package names must be obtained from their dependency cookbooks or confirmed on the target platform.

**Service dependencies**:
- Memcached service, referenced through `memcached`; service name and endpoint are not specified.
- Redis service, enabled through `redisio::enable`; service name is not specified.
- Redis configuration instance reported on TCP port `6379`; confirm before implementation.

## Credentials

**Detection Summary**: 1 credential is reported in 1 file; the validation summary does not independently expose the credential-analysis result, so the details require source verification.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe, as reported
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`, reported but requiring verification
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as a hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis authentication; passed to the Redis server configuration as the `requirepass` value
- **Migration storage**: Move to Ansible Vault under a variable such as `redis_requirepass`
- **Handling requirements**:
  - Do not commit the literal password to `defaults/main.yml`, templates, task files, or generated inventories.
  - Ensure the resulting Redis configuration uses the syntax required by the installed Redis version.
  - Confirm the literal value and assignment in the recipe before migration.

No data bag, encrypted data bag, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secret, TLS certificate, private key, API token, or database connection credential was identified in the supplied plan.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`, if confirmed by the Redis dependency
- `/var/log/redis`, if confirmed by the directory resource
- Memcached configuration path, after it is obtained from the dependency cookbook

**Service endpoints to check**:
- Redis instance `6379`: TCP port `6379`, subject to source verification
- Memcached instance: port not specified; obtain from the dependency cookbook
- Unix sockets: None specified

**Templates rendered**:
- None; no templates are present in the execution tree.

**Static files deployed**:
- None; no `cookbook_file` or `remote_file` resources are present.

**Redis configuration settings to verify**:
- Authentication is enabled through `requirepass`.
- The following directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

```bash
# Verify the analyzed source before implementation
grep -nE "redisio|memcached|6379|requirepass|fix_redis_config|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority|/var/log/redis" \
  cookbooks/cache/recipes/default.rb

# Discover Redis service units for the Redis 6379 instance
systemctl list-units --type=service | grep -i redis
systemctl status redis

# Verify the Redis 6379 endpoint
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'

# Verify unauthenticated access is rejected
redis-cli -p 6379 PING

# Verify authenticated access without placing the password in command history
export REDISCLI_AUTH='<retrieve-from-secure-secret-store>'
redis-cli -p 6379 PING

# Verify the Redis configuration
grep -E '^(requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Verify the Redis log directory
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis

# Review Redis logs
journalctl -u redis --no-pager -n 100
find /var/log/redis -maxdepth 1 -type f -print

# Discover and verify the Memcached service only after dependency details are confirmed
systemctl list-units --type=service | grep -i memcached
```

Expected Redis results:

- The Redis `6379` instance is enabled and running, if confirmed by `redisio::enable`.
- Redis listens on TCP port `6379`.
- An unauthenticated `PING` fails with an authentication error.
- An authenticated `PING` returns `PONG`.
- `requirepass` is present in the expected Redis configuration format.
- The five reported replication-related directives are absent.
- `/var/log/redis` has the confirmed ownership and mode.
- The exact Redis log filename is not assumed.

Expected Memcached results:

- The service name, package, port, and configuration path are obtained from the `memcached` dependency cookbook or target environment.
- Validation uses those confirmed values rather than guessed settings.