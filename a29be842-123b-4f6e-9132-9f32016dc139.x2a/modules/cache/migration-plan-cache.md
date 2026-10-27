---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Redis instance on port `6379` with password authentication, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and enables Redis through the `redisio` dependency. It also includes a Memcached dependency whose implementation is not present in the supplied execution tree. The migration must preserve the Redis configuration and ordering while moving the hardcoded password `redis_secure_password_123` to Ansible Vault or another secret-management system. Exact Memcached packages, service names, ports, and configuration paths must be verified from its dependency cookbook.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server configured through `node['redisio']['servers']`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication enabled with `requirepass`; `replicaservestaledata` set to `nil`; selected replication directives removed after configuration
  - Log directory: `/var/log/redis`
  - Log directory owner/group/mode: `redis:redis`, `0755`
  - Removed directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

- **Memcached dependency**: Included dependency with no locally available implementation
  - Location/Path: Not available from the supplied execution tree
  - Port/Socket: Not determinable from the supplied cookbook
  - Key Config: The `memcached` recipe is included before local Redis directory creation; its package, service, configuration path, and endpoint require separate dependency inspection

## File Structure

Only the locally supplied and executed recipe file is listed. The included dependency recipes are explicitly reported as not found and are therefore not included.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files were identified.

**Templates:**
```text
```

No rendered templates were identified.

**Attributes:**
```text
```

No attribute files were identified. Redis settings are assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` were identified.

## Module Explanation

The cookbook performs operations in this order:

1. **Include Memcached** (`cookbooks/cache/recipes/default.rb`)
   - Executes `include_recipe 'memcached'`.
   - The referenced Memcached recipe is not present in the supplied execution tree.
   - Implement the dependency as a separate Ansible task block or role only after inspecting the actual dependency cookbook.
   - Do not assume a Memcached package, service name, configuration path, port, or authentication setting.
   - Preserve execution before local Redis log-directory creation.

2. **Define the Redis server settings** (`cookbooks/cache/recipes/default.rb`)
   - Assigns one Redis server to `node['redisio']['servers']`.
   - Configures port `6379`.
   - Enables password authentication with `requirepass`.
   - Sets `replicaservestaledata` to `nil`.
   - Store the Redis password in an encrypted Ansible Vault variable such as `redis_password`.
   - Apply `no_log: true` to tasks that may expose the password.
   - Configure `/etc/redis/6379.conf` with:
     - `port 6379`
     - `requirepass <vault-managed password>`

3. **Create the Redis log directory** (`cookbooks/cache/recipes/default.rb`)
   - Manages `/var/log/redis` as a recursive directory.
   - Sets owner to `redis`.
   - Sets group to `redis`.
   - Sets mode to `0755`.
   - Ensure the `redis` group exists through verified dependency behavior or an explicit prerequisite task before assigning directory ownership.

4. **Include the Redis configuration recipe** (`cookbooks/cache/recipes/default.rb`)
   - Executes `include_recipe 'redisio'`.
   - The referenced `redisio` recipe is not present in the supplied execution tree.
   - Inspect the dependency before documenting exact Redis package or service names.
   - Preserve the expected configuration path `/etc/redis/6379.conf`.
   - Complete Redis configuration before cleanup runs.

5. **Remove unwanted Redis replication directives** (`cookbooks/cache/recipes/default.rb`)
   - Executes `ruby_block[fix_redis_config]`.
   - Targets `/etc/redis/6379.conf`.
   - Checks whether the file exists before modifying it.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Use five explicit `ansible.builtin.lineinfile` tasks with `state: absent`, or a template-based configuration.
   - Run cleanup after Redis configuration and before Redis enablement.
   - Notify a Redis restart or reload only when configuration changes.
   - Preserve the original conditional behavior when `/etc/redis/6379.conf` does not exist.

6. **Enable Redis** (`cookbooks/cache/recipes/default.rb`)
   - Executes `include_recipe 'redisio::enable'`.
   - The referenced `redisio::enable` recipe is not present in the supplied execution tree.
   - Enable and start the service corresponding to the Redis instance on port `6379`.
   - Confirm the exact service unit name from the `redisio` dependency or target operating system.
   - Ensure enablement occurs after `/etc/redis/6379.conf` is finalized.
   - Restart or reload Redis when cleanup changes the active configuration.

No `.each` loops were identified.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- No package resources are declared directly by the local recipe.
- No package names are confirmed from the supplied execution tree.
- Packages installed by `memcached` and `redisio` require inspection of those dependency cookbooks.

**Service dependencies**:

- Memcached service behavior is delegated to the missing `memcached` recipe.
- Redis configuration behavior is delegated to the missing `redisio` recipe.
- Redis service enablement is delegated to the missing `redisio::enable` recipe.
- Redis is expected to use `/etc/redis/6379.conf`.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Literal value in source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`
- **Migration storage**: Encrypted Ansible Vault variable such as `redis_password`
- **Migration requirements**:
  - Do not commit the literal password to role defaults or plaintext inventory.
  - Apply `no_log: true` to tasks that render, change, or test the password.
  - Avoid exposing the password in command-line process arguments where possible.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, AWS Secrets Manager, HashiCorp Vault, environment-variable secrets, TLS certificates, database connection strings, or additional credential namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis/`
- Redis service unit associated with the `redisio` dependency
- Memcached configuration file discovered by inspecting the dependency cookbook

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Memcached endpoint: not determinable from the supplied cookbook
- Unix sockets: none identified

**Redis configuration keys to verify**:

- `port 6379`
- `requirepass`
- Absence of:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- None; render count: `0`

## Pre-flight checks

```bash
# Redis instance on port 6379
# Replace <redis-service-unit> after confirming the unit name from redisio.
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>
ps aux | grep '[r]edis'

ss -tlnp | grep ':6379'
netstat -tlnp 2>/dev/null | grep ':6379'

# Redis configuration
test -f /etc/redis/6379.conf
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' /etc/redis/6379.conf
grep -E '^[[:space:]]*requirepass[[:space:]]+' /etc/redis/6379.conf

# The following command must produce no output.
grep -E '^[[:space:]]*(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Redis log directory
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis

# Expected directory properties:
# Owner: redis
# Group: redis
# Mode: 0755

# Redis authentication
export REDISCLI_AUTH='<vaulted-redis-password>'
redis-cli -p 6379 PING
unset REDISCLI_AUTH
# Expected result: PONG

# Unauthenticated access should fail with an authentication-required error.
redis-cli -p 6379 PING

# Redis logs
ls -la /var/log/redis
journalctl -u <redis-service-unit> --no-pager -n 50

# Memcached dependency
# First inspect the memcached dependency to identify its actual unit, port,
# configuration path, and package. Then run the discovered checks explicitly.
systemctl status <verified-memcached-service-unit>
systemctl is-enabled <verified-memcached-service-unit>
systemctl is-active <verified-memcached-service-unit>
ss -tlnp
test -f <verified-memcached-config-path>

# Configuration-change behavior
systemctl restart <redis-service-unit>
systemctl is-active <redis-service-unit>

export REDISCLI_AUTH='<vaulted-redis-password>'
redis-cli -p 6379 PING
unset REDISCLI_AUTH
# Expected result: PONG
```

The Ansible implementation must be idempotent. A second run must not continually modify `/etc/redis/6379.conf` or restart Redis when no configuration has changed.