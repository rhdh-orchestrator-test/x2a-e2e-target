---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching through the external `memcached` and `redisio` cookbooks. The directly analyzed recipe, `cache::default`, defines one Redis instance named `redis-6379`, listening on TCP port `6379`, with password authentication, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and attempts to enable Redis. The dependency recipes for Memcached, RedisIO, and RedisIO enablement are unavailable, so their package names, service names, templates, and additional endpoints must be verified against the target distribution.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Authentication: Redis `requirepass` set to the protected value currently represented by `redis_secure_password_123`
  - `replicaservestaledata`: unset/null
  - Configuration directives removed after RedisIO configuration:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

The Redis configuration collection contains exactly one item:

- **redis-6379**
  - `port`: `'6379'`
  - `requirepass`: `'redis_secure_password_123'`
  - `replicaservestaledata`: `nil`

No Memcached instance is directly configured in the analyzed execution tree. The unavailable `memcached` dependency does not provide enough information to identify a Memcached instance name, port, service, configuration path, or bind address.

## File Structure

Only files explicitly shown in the supplied execution tree and directory listing are included.

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

No templates are shown or rendered by the supplied execution tree.

**Attributes:**
```text
```

No standalone attribute files are shown. The Redis server configuration is assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are deployed by the supplied execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - Assigns one Redis configuration item for `redis-6379`.
   - Creates `/var/log/redis` with recursive directory creation.
   - Attempts to include the external `redisio` recipe.
   - Removes selected replication-related directives from `/etc/redis/6379.conf`.
   - Attempts to include `redisio::enable`.

   **Execution details:**

   - **Include `memcached`**:
     - Executes `include_recipe 'memcached'`.
     - The dependency recipe is unavailable according to the execution tree.
     - Memcached package names, service name, configuration path, listening port, bind address, and templates cannot be determined from the supplied cookbook analysis.

   - **Assign Redis server configuration**:
     - Defines exactly one Redis item:
       - Instance: `redis-6379`
       - Port: `6379`
       - Password: `redis_secure_password_123`
       - `replicaservestaledata`: unset/null
     - The password must be moved to Ansible Vault or an approved external secret provider.
     - Preserve the unset/null `replicaservestaledata` value if the target Redis configuration requires an equivalent representation.

   - **Create Redis log directory**:
     - Uses the `directory` resource for `/var/log/redis`.
     - Sets owner to `redis`.
     - Sets group to `redis`.
     - Sets mode to `0755`.
     - Enables recursive creation.
     - Ansible equivalent: `ansible.builtin.file` with `state: directory`.

   - **Include `redisio`**:
     - Executes `include_recipe 'redisio'`.
     - The dependency recipe is unavailable according to the execution tree.
     - Redis package name, version, configuration-generation behavior, and service name must be verified against the selected target distribution.

   - **Run `ruby_block[fix_redis_config]`**:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Performs no action if the file does not exist.
     - Reads the file when present.
     - Removes complete lines beginning with:
       - `replica-serve-stale-data`
       - `replica-read-only`
       - `repl-ping-replica-period`
       - `client-output-buffer-limit`
       - `replica-priority`
     - Writes the modified configuration back to `/etc/redis/6379.conf`.
     - Ansible can implement this behavior with conditional `ansible.builtin.replace` tasks or a controlled configuration template.
     - The supplied Chef resource does not explicitly declare a service notification.

   - **Include `redisio::enable`**:
     - Executes `include_recipe 'redisio::enable'`.
     - The dependency recipe is unavailable according to the execution tree.
     - The intended behavior is to enable Redis, but the actual service name and enablement behavior must be verified against the selected Redis package.
     - No explicit Chef service resource is present in the analyzed recipe.

   **Resources identified**:
   - `directory[/var/log/redis]`
   - `ruby_block[fix_redis_config]`
   - `include_recipe 'memcached'`
   - `include_recipe 'redisio'`
   - `include_recipe 'redisio::enable'`

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**System package dependencies**:

- Not determinable from the supplied execution tree.
- The `memcached` and `redisio` dependency recipes are unavailable.
- Package names and versions must be verified against the intended target distribution before implementation.

**Service dependencies**:

- Redis enablement is intended through the unavailable `redisio::enable` recipe.
- The Redis service name is not provided.
- Memcached service behavior is unavailable because the `memcached` recipe is missing.
- No explicit Chef service resource is present in the analyzed recipe.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected
- **Source file**: `cookbooks/cache/recipes/default.rb`

### Redis Authentication Password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef attribute assignment
- **Usage context**: Redis authentication for instance `redis-6379` on port `6379`
- **Ansible migration**:
  - Store the value in Ansible Vault or an approved external secret provider.
  - Do not commit the plaintext value to ordinary role defaults, `group_vars`, or `host_vars`.
  - Render the protected value into the Redis configuration with `no_log: true` where appropriate.
  - Validate authentication with an authenticated Redis client command.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, private keys, API keys, or database connection strings were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Instance `redis-6379`: TCP port `6379`
- Unix sockets: None identified
- Bind address: None identified

**Configuration checks**:

- Confirm instance `redis-6379` listens on TCP port `6379`.
- Confirm password authentication is enabled.
- Confirm the following directives are absent from `/etc/redis/6379.conf`:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- Confirm `/var/log/redis` has owner `redis`, group `redis`, and mode `0755`.
- Confirm the Redis configuration contains the intended port and protected password.
- Confirm the Redis service is enabled and running after its package-specific service name is verified.

**Templates rendered**:

- None rendered (`0`).

## Pre-flight checks:

The Redis service name must be replaced with the name provided by the selected Redis package.

```bash
# Redis instance redis-6379: service status
systemctl status <redis-service-name>

# Redis instance redis-6379: confirm a Redis process is running
ps aux | grep '[r]edis-server'

# Redis instance redis-6379: confirm the configuration file exists
test -f /etc/redis/6379.conf

# Redis instance redis-6379: confirm the service is enabled
systemctl is-enabled <redis-service-name>

# Redis instance redis-6379: confirm Redis is listening on TCP port 6379
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'

# Confirm the Redis log directory ownership and mode
stat -c '%U %G %a %n' /var/log/redis
# Expected:
# redis redis 755 /var/log/redis

# Redis instance redis-6379: validate authenticated access
redis-cli -h 127.0.0.1 -p 6379 -a '<redis-password-from-vault>' PING
# Expected:
# PONG

# Redis instance redis-6379: confirm unauthenticated access is rejected
redis-cli -h 127.0.0.1 -p 6379 PING
# Expected: an authentication-required error

# Redis instance redis-6379: validate an authenticated INFO request
redis-cli -h 127.0.0.1 -p 6379 -a '<redis-password-from-vault>' INFO server

# Confirm the five removed directives are absent
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected: no output

# Confirm the configured port and authentication directive
grep -nE '^(port|requirepass)' /etc/redis/6379.conf

# Review Redis logs for instance redis-6379
journalctl -u <redis-service-name> --no-pager -n 100

# Verify the Redis log directory contents
ls -lah /var/log/redis
```

No Memcached pre-flight endpoint or service check can be specified because the `memcached` dependency recipe is unavailable and no Memcached instance is identified in the supplied execution tree.