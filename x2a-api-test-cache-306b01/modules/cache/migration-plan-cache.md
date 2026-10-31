---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis cache instance on TCP port `6379`, with authentication enabled by a hardcoded password that must be migrated to Ansible Vault. It creates `/var/log/redis` with Redis ownership and removes selected replication-related directives from `/etc/redis/6379.conf`. The cookbook also includes external `memcached` and `redisio` dependencies, but their recipes are not present in the analyzed cookbook, so their package, service, and configuration details require separate verification.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`
  - Key Config: Authentication enabled with `requirepass`; password is `redis_secure_password_123` in Chef and must be stored in Ansible Vault; `replicaservestaledata` is `nil`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`

**Memcached dependency**:

- The recipe includes the external `memcached` cookbook.
- The local cookbook does not provide the included Memcached recipe.
- No Memcached port, configuration path, authentication setting, or service resource is visible in the analyzed execution tree.
- Do not invent Memcached settings. Resolve the external `memcached` cookbook separately if Memcached must be migrated.

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

No templates are shown in the execution tree.

**Attributes:**
```text
```

No attribute files are shown in the execution tree. The Redis server collection is assigned directly inside `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe. The dependency recipe is not present locally, and its implementation is unavailable.
   - Assigns one Redis server entry to `node.default['redisio']['servers']`:
     - Redis server on port `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation enabled
   - Includes the external `redisio` recipe. The dependency recipe is not present locally.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` through `ruby_block[fix_redis_config]` when the file exists.
   - Includes the external `redisio::enable` recipe as the final dependency recipe. Its service name and enablement behavior are unavailable locally.
   - Local resources identified by the structured execution tree, in order:
     1. `directory[/var/log/redis]`
     2. `ruby_block[fix_redis_config]`
   - Resource summary:
     - `directory`: 1 — `/var/log/redis`
     - `ruby_block`: 1 — `fix_redis_config`
   - No `.each` loops are present. The Redis collection contains one explicitly assigned item: the Redis server on port `6379`.

### Redis configuration cleanup

`ruby_block[fix_redis_config]`:

- Reads `/etc/redis/6379.conf` only when the file exists.
- Removes complete lines beginning with:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- Writes the modified contents back to `/etc/redis/6379.conf`.

The Ansible migration should:

- Check whether `/etc/redis/6379.conf` exists.
- Remove matching directives using `ansible.builtin.replace`, `ansible.builtin.lineinfile`, or a controlled configuration template.
- Preserve the no-op behavior when the file does not exist.
- Notify a Redis restart or reload only when the configuration changes.
- Run the cleanup after the Redis configuration has been generated.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint
- `redisio::enable`, provided by the `redisio` cookbook

**System package dependencies**:

- No system package names are directly declared in `cookbooks/cache/recipes/default.rb`.
- Package installation is delegated to the unavailable external `memcached` and `redisio` recipes.
- No exact package names can be verified from the supplied cookbook and none should be invented.

**Service dependencies**:

- Redis installation and configuration behavior are delegated to `redisio`.
- Redis service enablement is delegated to `redisio::enable`.
- Memcached service behavior is delegated to `memcached`.
- The local recipe directly references Redis configuration on TCP port `6379`.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef attribute assignment
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value in Chef**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis server on port `6379`

Migration requirements:

- Store the password in Ansible Vault, for example:
  ```yaml
  redis_password: "redis_secure_password_123"
  ```
- Do not commit the plaintext value to ordinary role defaults or variables.
- Use the vaulted variable when rendering the Redis configuration.
- Set `no_log: true` on tasks that may expose the password.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, database connection strings, or API tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis TCP port `6379`
- Memcached endpoint: not defined by the local cookbook or execution tree

**Unix sockets**:

- None identified.

**Network interfaces**:

- No bind address is specified in the analyzed recipe.

**Templates rendered**:

- None identified; render count: `0`

**Static files deployed**:

- None identified; deployment count: `0`

## Pre-flight checks:

```bash
# Redis service status.
# Substitute the exact service name after inspecting the external redisio cookbook.
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Redis server instance on TCP port 6379.
ss -ltnp | grep ':6379'

# Unauthenticated access should be rejected when requirepass is enabled.
redis-cli -p 6379 PING
# Expected: NOAUTH Authentication required.

# Authenticate with the vaulted password without exposing it in shell history.
redis-cli -p 6379 -a '<redis-password>' PING
# Expected: PONG

# Verify Redis configuration for the instance on port 6379.
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Confirm port 6379 and authentication are configured.
# Confirm these directives are absent:
# replica-serve-stale-data
# replica-read-only
# repl-ping-replica-period
# client-output-buffer-limit
# replica-priority

# Redis authentication and read/write validation for the instance on port 6379.
redis-cli -p 6379 -a '<redis-password>' SET chef_migration_check success
redis-cli -p 6379 -a '<redis-password>' GET chef_migration_check
redis-cli -p 6379 -a '<redis-password>' DEL chef_migration_check
# Expected results: OK, success, and 1.

# Redis log directory ownership and permissions.
stat -c '%U %G %a %n' /var/log/redis
ls -ld /var/log/redis
# Expected: redis redis 755 /var/log/redis

# Redis logs. Use the actual service name if redisio configures a different one.
journalctl -u redis --no-pager -n 100

# Memcached dependency checks.
# Confirm the service name, port, and configuration from the external cookbook first.
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
```