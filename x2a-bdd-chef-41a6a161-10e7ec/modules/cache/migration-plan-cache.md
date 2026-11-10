---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis cache instance on TCP port `6379` and declares dependencies on Memcached and Redis cookbooks whose recipe files are unavailable from the supplied execution tree. The visible recipe sets Redis authentication, uses `/run/redis` for the PID directory and `/var/log/redis` for logs, removes selected replication-related directives from `/etc/redis/6379.conf`, and includes Redis service enablement. No templates, static files, providers, or explicit package resources are present.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`
  - PID directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Key Config: Redis authentication enabled with `requirepass`; configured password is `redis_secure_password_123`; `replicaservestaledata` is set to `nil`
  - Post-configuration: Removes selected replication and output-buffer directives from `/etc/redis/6379.conf` when the file exists

Memcached is declared as an external cookbook dependency, but its recipe is unavailable. No Memcached instance name, port, package, configuration path, or service name can be determined from the analyzed files.

## File Structure

Only files shown as part of the supplied cookbook analysis are listed.

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

The following dependency recipes are referenced but unavailable and are not files present in this cookbook:

- `memcached`: not found
- `redisio`: not found
- `redisio::enable`: not found

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` recipe is unavailable in the supplied execution tree.
   - No Memcached resources can be documented from the available files.
   - Sets `node['redisio']['servers']` to one Redis server definition:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the external `redisio` recipe.
   - The `redisio` recipe is unavailable, so its package names, service name, templates, data directories, and configuration resources cannot be determined.
   - Creates `/var/log/redis` using `directory[/var/log/redis]`:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive: `true`
   - Executes `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Does not restart or notify a service after modifying the Redis configuration.
   - Includes the external `redisio::enable` recipe.
   - The `redisio::enable` recipe is unavailable, so the exact service name and start/enable behavior cannot be determined.
   - Iterations: None. The recipe does not contain an `.each` loop.
   - Resource counts:
     - `directory`: 1
     - `ruby_block`: 1

The Ansible migration should configure exactly one Redis instance on port `6379`, use `/run/redis` as the PID directory, create `/var/log/redis` with the specified ownership and mode, and remove the listed directives from `/etc/redis/6379.conf`. The Redis password should be moved to Ansible Vault or an approved external secret provider.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No explicit `package` resources are present in `cookbooks/cache/recipes/default.rb`.
- Packages installed by the unavailable `memcached` and `redisio` recipes cannot be determined from the supplied execution tree.

**Service dependencies**:

- Redis service enablement is delegated to the unavailable `redisio::enable` recipe.
- Redis installation and configuration are delegated to the unavailable `redisio` recipe.
- Memcached service management is delegated to the unavailable `memcached` recipe.
- No explicit service resource is visible in the analyzed cookbook.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded Chef attribute
- **URL**: None detected
- **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Value detected**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the Redis instance listening on TCP port `6379`

The migrated value must be stored in an encrypted Ansible Vault variable or an approved external secret provider. It must not be placed in a normal variable file or committed playbook.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret, TLS certificate, private key, API token, or database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`

The unavailable Redis dependency may create additional files that cannot be identified from the supplied execution tree.

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Unix sockets: none specified
- Network binding: not specified; verify the generated configuration rather than assuming loopback or all-interface binding
- Memcached endpoint: unavailable and not derivable from the analyzed cookbook

**Templates rendered**:

- None detected; render count: `0`

**Static files deployed**:

- None detected; deployment count: `0`

**Configuration changes to verify in `/etc/redis/6379.conf`**:

The following directives must be absent after the cleanup step:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

The configuration must retain the Redis listener port and password settings generated by the replacement Redis implementation.

## Pre-flight checks

### Redis instance on port 6379

```bash
# Replace <redis-service-name> after identifying the service name
# from the replacement redisio implementation.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>

ps aux | grep '[r]edis-server'
ss -tlnp | grep ':6379'
netstat -tlnp 2>/dev/null | grep ':6379'

test -f /etc/redis/6379.conf
test -d /var/log/redis
test -d /run/redis

stat -c '%A %U:%G %n' /var/log/redis
stat -c '%A %U:%G %n' /run/redis
ls -l /etc/redis/6379.conf
ls -ld /run/redis
```

Expected results:

- Redis is active and enabled using the service name supplied by the replacement implementation.
- Redis is listening on TCP port `6379`.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- `/run/redis` exists and is used as the Redis PID directory.

Validate the Redis configuration:

```bash
grep -E '^(port|requirepass|pidfile|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

The second command must return no matching lines.

Verify the configured port:

```bash
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf
```

Authenticate and perform a functional read/write test using the migrated secret:

```bash
redis-cli -p 6379 -a '<redis-password>' PING
redis-cli -p 6379 -a '<redis-password>' SET chef_migration_test ok
redis-cli -p 6379 -a '<redis-password>' GET chef_migration_test
redis-cli -p 6379 -a '<redis-password>' DEL chef_migration_test
```

Expected results:

- `PING` returns `PONG`.
- `SET` returns `OK`.
- `GET` returns `ok`.
- `DEL` returns `1`.

Verify that unauthenticated access is rejected when authentication is required:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication error rather than `PONG`.

Check Redis logs:

```bash
# Replace <redis-service-name> with the identified Redis service name.
journalctl -u <redis-service-name> --no-pager -n 100
journalctl -u <redis-service-name> -f
```

The cookbook creates `/var/log/redis` but does not define a specific log file. If the replacement Redis implementation configures file logging, verify the exact configured file.

### Memcached dependency

The `memcached` recipe is unavailable. Do not claim that Memcached is installed, configured, or running until the dependency implementation is obtained or replaced.

After its implementation is identified, verify its actual service name, package, configuration path, and port. None of these values can be derived from the analyzed `cache` cookbook.