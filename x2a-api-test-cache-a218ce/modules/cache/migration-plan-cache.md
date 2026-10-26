---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures Memcached and one Redis instance through the external `memcached` and `redisio` cookbooks. The available `cache::default` recipe includes the Memcached recipe, defines a Redis server on port `6379` with a source-level hardcoded password, creates `/var/log/redis`, includes Redis installation and enablement recipes, and removes specified Redis directives from `/etc/redis/6379.conf`. The dependency recipes are unavailable in the supplied execution tree, so their package names, service names, templates, and exact Memcached settings require separate verification. The Redis password must be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache and authenticated key-value service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is set in the source recipe to `redis_secure_password_123`; the `replicaservestaledata` value is unset (`nil`); unsupported replication directives are removed from the configuration; logs use `/var/log/redis`
  - Verification status: These Redis settings come from source-level recipe inspection. The supplied structured execution analysis does not expose the attribute assignment or the `ruby_block` implementation.

- **Memcached**: Memcached service included through the external `memcached` cookbook
  - Location/Path: Not available from the supplied cookbook
  - Port/Socket: Not specified
  - Key Config: Package, service name, configuration path, bind address, port, and authentication settings require inspection of the `memcached` dependency

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

```text
```

No provider files are shown or used by the supplied execution tree.

**Templates:**

```text
```

No templates are shown or rendered.

**Attributes:**

```text
```

No attribute files are shown. Redis settings are assigned directly in `cookbooks/cache/recipes/default.rb` according to source-level inspection.

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The following dependency recipes are referenced but unavailable and are not part of the supplied cookbook file structure:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in the following order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Defines one Redis server entry with port `6379`, Redis authentication, and an unset `replicaservestaledata` value.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation according to source-level inspection.
   - Includes the external `redisio` recipe.
   - Removes selected Redis directives from `/etc/redis/6379.conf` when that file exists.
   - Includes the external `redisio::enable` recipe.
   - No `.each` loops are present in the supplied recipe.

   **Source-level Redis assignment:**

   ```ruby
   node.default['redisio']['servers'] = [
     {
       'port' => '6379',
       'requirepass' => 'redis_secure_password_123',
       'replicaservestaledata' => nil
     }
   ]
   ```

   **Included dependency order:**

   1. `memcached` — dependency recipe unavailable
   2. `redisio` — dependency recipe unavailable
   3. `redisio::enable` — dependency recipe unavailable

   **Memcached dependency behavior:**

   - The execution tree reports `memcached Recipe file not found`.
   - Package installation, service management, configuration paths, ports, bind addresses, and templates cannot be determined from the supplied cookbook.
   - Implement Memcached only after inspecting the dependency or deployment requirements.

   **Redis directory resource:**

   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled
   - The `redis` user and group are expected to be created by the Redis dependency and are not created directly by this recipe.

   **Redis configuration cleanup:**

   - Resource: `ruby_block[fix_redis_config]`
   - File: `/etc/redis/6379.conf`
   - The block performs no action when the file does not exist.
   - It removes complete lines matching these directives:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The supplied structured analysis confirms the `ruby_block` resource but does not expose its implementation. The directive list and file behavior therefore require source-level verification.
   - No explicit service restart or notification is visible in the supplied recipe.
   - The Ansible implementation should use idempotent `ansible.builtin.lineinfile` tasks or a controlled template and should restart Redis only when required by the target implementation.

   **Ansible migration behavior:**

   - Store the Redis password in Ansible Vault as `vault_redis_password`.
   - Configure the Redis instance on port `6379`.
   - Create `/var/log/redis` with the stated ownership and mode after confirming the dependency creates the `redis` user and group.
   - Manage the actual Redis service name supplied by the selected package.
   - Enable and start Redis.
   - Remove the five unsupported directives from `/etc/redis/6379.conf`.
   - Preserve all other Redis configuration content.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package resources are present in the supplied recipe.
- Exact package names and versions are not verified.
- Obtain package names from the unavailable dependency recipes or the selected Ansible roles.
- Supported platforms identified by the cookbook metadata:
  - Ubuntu `>= 18.04`
  - CentOS `>= 7.0`

**Service dependencies**:

- Memcached service management is delegated to the unavailable `memcached` recipe.
- Redis installation and base configuration are delegated to the unavailable `redisio` recipe.
- Redis enablement is delegated to the unavailable `redisio::enable` recipe.
- No explicit Chef `service` resource is present in the available recipe.
- The target Redis service name must be verified from the selected package.
- The target Memcached service name must be obtained from the dependency implementation.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Usage context**: Redis authentication for the Redis server listening on port `6379`

Migration requirements:

- Do not copy the password into Ansible role defaults, plaintext variable files, or generated documentation.
- Store the value in Ansible Vault as `vault_redis_password`.
- Reference the vaulted variable from the Redis configuration task.
- Use restrictive permissions for generated Redis configuration files.
- Do not expose the password in shell history during validation.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, API keys, or database connection strings were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis server on TCP port `6379`
- Memcached server: endpoint not determinable from the supplied cookbook
- Unix sockets: none specified
- Redis bind address: not specified
- Memcached bind address: not specified

**Templates rendered**:

- None; render count: `0`

**Configuration transformations to verify**:

- Redis listens on port `6379`.
- Redis authentication is configured from Ansible Vault.
- `replicaservestaledata` remains unset or omitted.
- The following directives are absent from `/etc/redis/6379.conf`:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- Redis is enabled and active.
- Memcached settings are verified only after its dependency implementation is obtained.

## Pre-flight checks:

```bash
# Confirm the migrated files are present
test -f /etc/redis/6379.conf
test -d /var/log/redis

# Redis service status
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Replace "redis" with the service name provided by the selected Redis package
# if the target distribution uses a versioned or alternate unit name.
```

```bash
# Redis instance on TCP port 6379
ss -tlnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Expected result: Redis is listening on TCP port 6379.
```

```bash
# Redis configuration for the port-6379 instance
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Confirm unsupported directives are absent
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis replication directive remains"
  exit 1
fi
```

```bash
# Redis authentication and connectivity
# Supply REDIS_PASSWORD securely rather than placing the password directly
# in shell history.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server
redis-cli -p 6379 -a "$REDIS_PASSWORD" CONFIG GET port

# Expected results:
# PING returns PONG.
# INFO server returns Redis server information.
# CONFIG GET port reports 6379.
```

```bash
# Authenticated read/write check for the Redis instance on port 6379
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET chef_ansible_migration_check ok
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET chef_ansible_migration_check
redis-cli -p 6379 -a "$REDIS_PASSWORD" DEL chef_ansible_migration_check

# Expected results:
# SET returns OK.
# GET returns ok.
# DEL removes the temporary key.
```

```bash
# Redis log directory
stat -c '%A %U:%G %n' /var/log/redis
ls -la /var/log/redis

# Expected result:
# Directory exists.
# Owner is redis.
# Group is redis.
# Mode is 0755.
```

```bash
# Redis logs
journalctl -u redis --no-pager -n 100

# Use the actual Redis service name if the selected package provides
# a versioned Redis unit.
```

```bash
# Memcached instance validation
# The exact service name, port, bind address, and configuration path must
# be filled in after inspecting the memcached dependency.

systemctl status <verified-memcached-service>
systemctl is-enabled <verified-memcached-service>
systemctl is-active <verified-memcached-service>

ss -tlnp | grep ':<verified-memcached-port>'

# Run the protocol health check required by the selected Memcached
# implementation after its endpoint is verified.
```

