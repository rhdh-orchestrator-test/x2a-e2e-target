---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached uses 64 MB of memory, TCP/UDP port `11211`, binding `0.0.0.0`, a maximum of 1024 connections, a maximum object size of `1m`, a ulimit of `1024`, and is started and enabled through the `memcached_instance` custom resource. Redis is configured with PID directory `/run/redis`, log directory `/var/log/redis`, and a hardcoded authentication password that must be migrated to Ansible Vault. The recipe removes five replication-related directives from `/etc/redis/6379.conf` and enables Redis. The `redisio` installation and enable recipe implementations were not available, so package names, service names, templates, providers, and exact resource behavior must not be inferred.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Configuration path is supplied by the selected Memcached implementation; log path attribute is `/var/log/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, maximum 1024 connections, maximum object size `1m`, user `service_user`, ulimit `1024`, empty experimental and additional CLI option lists
  - Actions: Start and enable
  - Resource: `memcached_instance[memcached]`

- **Redis server on port 6379**: Redis cache service
  - Location/Path: Configuration file `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: Authentication password configured as `redis_secure_password_123` in the source cookbook; migrate this value to an Ansible Vault variable. Redis bind address is not specified.
  - Log directory ownership: `redis:redis`, mode `0755`, recursive creation enabled
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Actions: Installation/configuration is delegated to `redisio`; service enablement is delegated to `redisio::enable`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb

Providers:
No provider files supplied.

Templates:
No template files supplied.

Attributes:
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

Files:
No static files supplied.
```

The `memcached_instance[memcached]` custom resource is used, but its provider path was not supplied. The `redisio` and `redisio::enable` recipe files were also unavailable.

## Module Explanation

The cookbook performs operations in the following order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Assigns one Redis server definition on port `6379`.
   - Assigns Redis base PID directory `/run/redis`.
   - Includes the Redis installation/configuration recipe.
   - Creates `/var/log/redis`.
   - Removes selected directives from `/etc/redis/6379.conf`.
   - Includes the Redis enable recipe.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares exactly one `memcached_instance` resource named `memcached`.
   - Configures 64 MB memory, TCP port `11211`, UDP port `11211`, and listen address `0.0.0.0`.
   - Configures maximum connections `1024`, maximum object size `1m`, user `service_user`, and ulimit `1024`.
   - Passes `node['memcached']['threads']` for the thread setting; no explicit default for that attribute was present.
   - Uses empty experimental and additional CLI option lists.
   - Starts and enables Memcached.
   - Exact package name, configuration path, service unit, and provider path are not present in the supplied execution tree.

3. **Redis server attribute assignment** (`cookbooks/cache/recipes/default.rb`):
   - Defines exactly one Redis server entry:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - The password must be replaced with an Ansible Vault variable during migration.

4. **`redisio` installation/configuration recipe** (recipe file unavailable):
   - Installs and configures the Redis instance on port `6379`.
   - The exact package name, service name, Redis version, user creation, provider, configuration template, destination resources, and restart notifications are unavailable.
   - These details must be obtained from the supported `redisio` equivalent or explicitly defined for the target distribution.

5. **Redis log directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Sets owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Equivalent Ansible resource: `ansible.builtin.file` with `state: directory`.

6. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Operates only when `/etc/redis/6379.conf` exists.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Should be migrated using a line-oriented task such as `ansible.builtin.replace`.
   - Must not remove unrelated configuration lines.
   - Chef does not show an explicit Redis restart or reload notification for this block.

7. **`redisio::enable`** (recipe file unavailable):
   - Enables the configured Redis service.
   - The exact service unit name and implementation are unavailable and must be selected from the target Redis implementation.

No `.each` loops are present in the available recipes. The Redis configuration contains one explicitly defined server entry: port `6379`.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- Memcached package supplied by the `memcached` dependency cookbook; exact package name is not exposed.
- Redis package supplied by the `redisio` dependency cookbook; exact package name is not exposed.

**Service dependencies**:
- Memcached service, started and enabled by `memcached_instance[memcached]`; exact unit name is not exposed.
- Redis service, installed/configured by `redisio` and enabled by `redisio::enable`; exact unit name is not exposed.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: Redis `requirepass` value in `node.default['redisio']['servers']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value: `redis_secure_password_123`
- **Usage context**: Client authentication for the Redis instance on port `6379`
- **Migration requirement**: Replace the plaintext value with an Ansible Vault variable. Do not store it in ordinary role defaults, group variables, host variables, or templates.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur calls, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- Memcached configuration file produced by the selected implementation
- Memcached log path represented by `/var/log/memcached`

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Redis Unix socket: none specified

**Templates rendered**:
- None; no templates are listed in the execution tree.

**Configuration transformations**:
- Remove `replica-serve-stale-data` lines from `/etc/redis/6379.conf`.
- Remove `replica-read-only` lines from `/etc/redis/6379.conf`.
- Remove `repl-ping-replica-period` lines from `/etc/redis/6379.conf`.
- Remove `client-output-buffer-limit` lines from `/etc/redis/6379.conf`.
- Remove `replica-priority` lines from `/etc/redis/6379.conf`.

## Pre-flight checks

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
nc -vz 127.0.0.1 11211
printf "version\r\n" | nc 127.0.0.1 11211
printf "stats\r\n" | nc 127.0.0.1 11211

# Verify Memcached configuration values using the path selected by Ansible.
# Confirm:
# - Memory: 64 MB
# - TCP port: 11211
# - UDP port: 11211
# - Listen address: 0.0.0.0
# - Maximum connections: 1024
# - Maximum object size: 1m
# - Ulimit: 1024

# Redis instance: port 6379
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
ss -tlnp | grep ':6379'
nc -vz 127.0.0.1 6379

# Use the Ansible Vault-managed value rather than placing the password in shell history.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING

# Verify Redis configuration.
grep -E '^(port|requirepass|dir|pidfile)' /etc/redis/6379.conf
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Expected:
# - Redis port is 6379.
# - requirepass is sourced from the vaulted variable.
# - PID configuration resolves under /run/redis.
# - No cleanup directive lines are returned.

# Verify Redis log directory.
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis

# Expected:
# - Directory exists.
# - Owner is redis.
# - Group is redis.
# - Mode is 0755.

# Verify Redis PID directory.
ls -ld /run/redis
find /run/redis -maxdepth 1 -type f -ls

# Check Redis logs using the service unit selected by the target implementation.
journalctl -u redis --no-pager -n 100

# End-to-end Memcached check.
printf "set migration_check 0 60 5\r\nhello\r\nget migration_check\r\n" | nc 127.0.0.1 11211

# End-to-end Redis check.
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET migration_check hello EX 60
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET migration_check
```

Expected results:

- Memcached is active and enabled, listens on TCP and UDP port `11211`, and returns protocol statistics.
- Redis is active and enabled, listens on TCP port `6379`, and returns `PONG` after authentication.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- `/run/redis` exists and permits Redis to create its PID file.
- Redis has no configuration parse errors and reports readiness to accept connections.
- Memcached and Redis both successfully store and retrieve the `migration_check` value.