---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a source-reported Redis instance named `redis-6379` on port `6379`, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and enables Redis. The `memcached`, `redisio`, and `redisio::enable` dependency recipes are missing from the supplied execution tree. Redis configuration details, dependency metadata, credential detection, and the absence of templates or static files require source or dependency verification before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-6379**: Source-reported Redis server instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Key Config: Redis authentication through `requirepass`; `replicaservestaledata` is source-reported as `nil`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Verification status: The supplied structured analysis confirms the Redis-related directory and cleanup resources but does not independently verify the port, configuration path, ownership, mode, authentication, or directive list.

Memcached is referenced by `cache::default`, but the `memcached` recipe is missing from the analyzed execution tree. No Memcached instance name, package, service, configuration path, or port can be determined from this cookbook.

## File Structure

The following is the complete directory listing supplied for the analyzed cookbook.

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

```text
```

No provider files are reported.

**Templates:**

```text
```

No template files are reported in the supplied analysis.

**Attributes:**

```text
```

No attribute files are reported.

**Files:**

```text
```

No static files are reported.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - Assigns one source-reported Redis server configuration to `node.default['redisio']['servers']`.
   - The source-reported Redis configuration uses port `6379`, password `redis_secure_password_123`, and `replicaservestaledata: nil`.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Includes the external `redisio` recipe.
   - Executes `ruby_block[fix_redis_config]` after Redis configuration.
   - Includes the external `redisio::enable` recipe.

   **Dependency and configuration status**:
   - `memcached` reports `Recipe file not found`.
   - `redisio` reports `Recipe file not found`.
   - `redisio::enable` reports `Recipe file not found`.
   - The structured analysis confirms one `directory` resource and one `ruby_block` resource.
   - Redis package names, service names, data directories, startup commands, and configuration rendering behavior are unavailable because the `redisio` implementation is not included.

   **Redis instance iteration**:
   - `redis-6379`: port `6379`; source-reported `requirepass`; `replicaservestaledata` set to `nil`.

2. **External `memcached` recipe** (`memcached`):
   - Included before Redis configuration.
   - Recipe implementation is missing.
   - Do not create Memcached package, service, configuration, port, or validation tasks without separately analyzing the external cookbook.

3. **External `redisio` recipe** (`redisio`):
   - Included after the Redis server attributes and log directory setup.
   - Recipe implementation is missing.
   - The replacement Ansible role must install and configure the selected Redis implementation.

4. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Examines the source-reported path `/etc/redis/6379.conf`.
   - If the file exists, removes lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified contents back to the same file.
   - The structured analysis confirms the Ruby block resource but does not independently list its regular expressions. These directives require source review before implementation.
   - Implement with `ansible.builtin.replace` tasks after Redis configuration generation.
   - Preserve conditional behavior for a missing configuration file while allowing permission and malformed-configuration errors to fail deployment.

5. **External `redisio::enable` recipe** (`redisio::enable`):
   - Recipe implementation is missing.
   - The Ansible equivalent must enable and start the Redis service after configuration.
   - Confirm the actual systemd service name from the selected Redis package or replacement role.
   - Confirm that the service listens on TCP port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, source-reported version constraint `~> 6.0`; dependency metadata was not included in the supplied file analysis.
- `redisio`, with no source-reported version constraint; dependency metadata was not included in the supplied file analysis.

The supplied execution tree reports the following missing recipes:

- `memcached`
- `redisio`
- `redisio::enable`

**System package dependencies**:

- No package resources are present in the analyzed recipe or execution tree.
- No package names or versions are verified by the supplied analysis.
- Package requirements must be obtained from the selected Redis role or package repository.
- Memcached packages must not be added without analyzing its external cookbook.

**Service dependencies**:

- Redis service for instance `redis-6379`, listening on TCP port `6379`.
- The exact systemd service name is not available from the supplied files.
- No Memcached service dependency is verified.

## Credentials

**Detection Summary**: 1 source-reported credential in 1 recipe file; the supplied structured analysis does not independently verify the credential finding.

**Source**:

- **Provider**: Hardcoded Chef attribute
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`; Ansible migration variable: `redis_password`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Source-reported hardcoded Chef recipe value
- **Usage context**: Redis client authentication through the Redis `requirepass` directive
- **Migration handling**:
  - Store the value in Ansible Vault or an approved AAP credential mechanism.
  - Do not copy the literal password into Ansible source.
  - Do not expose it in task output, debug output, normal variable files, or command-line arguments.
  - Use `no_log: true` for tasks that could display the secret.

No data bag, encrypted data bag, Chef Vault item, Conjur variable, CyberArk data bag, environment-variable secret, TLS certificate, private key, or credential-bearing database connection string is reported.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

The Redis data directory and exact Redis log file are not available from the supplied analysis.

**Service endpoints to check**:

- `redis-6379`: TCP port `6379`
- Unix sockets: None referenced
- Network interface binding: Not specified

**Templates rendered**:

- None reported.
- Render count: `0` verified template files; dependency templates are unavailable because `redisio` is missing.

**Configuration transformations**:

For `redis-6379`, verify that `/etc/redis/6379.conf` does not contain:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks:

```bash
# Redis instance: redis-6379
# Replace <redis-service-name> with the service name supplied by the selected Redis role.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>

# Confirm the Redis instance endpoint.
ss -ltnp | grep ':6379'
nc -zv 127.0.0.1 6379

# Confirm the configuration file and log directory.
test -f /etc/redis/6379.conf
ls -ld /var/log/redis

# Expected directory properties:
# owner: redis
# group: redis
# mode: 0755

# Verify the port and cleanup directives without displaying the password.
grep -nE '^(port|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Authenticate without placing the password in shell history.
export REDISCLI_AUTH='<retrieve-from-approved-secret-store>'
redis-cli -p 6379 PING
unset REDISCLI_AUTH

# Expected result:
# PONG

# Functional Redis check for redis-6379.
export REDISCLI_AUTH='<retrieve-from-approved-secret-store>'
redis-cli -p 6379 SET migration_check success
redis-cli -p 6379 GET migration_check
redis-cli -p 6379 DEL migration_check
unset REDISCLI_AUTH

# Expected output:
# OK
# "success"
# (integer) 1

# Inspect Redis service logs.
journalctl -u <redis-service-name> --no-pager -n 100

# Apply and validate configuration changes.
systemctl restart <redis-service-name>
systemctl is-active <redis-service-name>
ss -ltnp | grep ':6379'

# Revalidate authenticated connectivity after restart.
export REDISCLI_AUTH='<retrieve-from-approved-secret-store>'
redis-cli -p 6379 PING
unset REDISCLI_AUTH

# No Memcached pre-flight check is defined because its recipe,
# package, service, configuration, and port are unavailable.
```