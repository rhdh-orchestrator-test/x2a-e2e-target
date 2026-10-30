---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a Redis cache instance on port `6379` and includes the external `memcached` and `redisio` cookbooks. The supplied execution tree contains only `cache::default`; the dependency recipes `memcached`, `redisio`, and `redisio::enable` are unavailable. The local recipe creates `/var/log/redis`, configures Redis authentication, removes five replication-related directive families from `/etc/redis/6379.conf`, and delegates Redis installation and service enablement to the unavailable `redisio` dependencies. The Redis password must be moved from the hardcoded recipe value into Ansible Vault or an approved secret backend.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with `requirepass`; replication-related directives removed; log directory `/var/log/redis`
  - Authentication password: Currently hardcoded as `redis_secure_password_123`; store securely during migration
  - Replication setting: `replicaservestaledata` is set to `nil`

**Memcached dependency**:

- The recipe includes `memcached` before configuring Redis.
- The `memcached` dependency recipe is unavailable.
- No Memcached instance name, port, package, service name, configuration path, socket, or authentication settings are available.
- These values must be obtained from the actual Memcached dependency cookbook or deployment role and must not be inferred from this cookbook.

## File Structure

Only files shown by the supplied execution tree and directory listing are included.

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

The metadata file identifies the cookbook description and dependencies but is not included in the supplied executable or referenced file listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` recipe is unavailable in the supplied execution tree. The migration must invoke an equivalent dependency role without assuming package names, service names, ports, paths, or configuration values.
   - Defines exactly one Redis server configuration for port `6379`:
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - The `redisio` recipe is unavailable in the supplied execution tree. The migration must use an equivalent Redis installation and configuration role and ensure `/etc/redis/6379.conf` exists before applying the configuration cleanup.
   - Processes `/etc/redis/6379.conf` through `ruby_block[fix_redis_config]`:
     - Removes complete lines beginning with `replica-serve-stale-data`.
     - Removes complete lines beginning with `replica-read-only`.
     - Removes complete lines beginning with `repl-ping-replica-period`.
     - Removes complete lines beginning with `client-output-buffer-limit`.
     - Removes complete lines beginning with `replica-priority`.
     - Leaves all other configuration lines unchanged.
     - Does nothing if `/etc/redis/6379.conf` does not exist.
     - Does not add replacement values for the removed directives.
   - Includes `redisio::enable`.
   - The `redisio::enable` recipe is unavailable. The migration must enable and start the Redis service after the Redis package, configuration, log directory, and configuration cleanup are complete.
   - No `.each` loops are present; the Redis server configuration is one explicit instance named **Redis server on port 6379**.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- None are declared by the available recipe.
- The dependency recipes that install packages are unavailable.
- No package names may be inferred from this cookbook alone.

**Service dependencies**:

- Memcached service: exact service name unavailable.
- Redis service: exact service name unavailable.
- Redis must be enabled and started through the equivalent of `redisio::enable`.

**Supported platforms declared in metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`

The Ansible migration must:

- Store the password in Ansible Vault or an approved external secret manager.
- Avoid placing the plaintext value in `defaults/main.yml`, ordinary variable files, or source-controlled templates.
- Render the Redis `requirepass` setting from the protected variable.
- Use the protected value securely during validation without exposing it in shell history, command output, or logs.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, Vault URL, or environment-variable secret reference was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

The Redis data directory and exact Redis log filename are not specified.

**Service endpoints to check**:

- Redis server on port `6379`
- Memcached endpoint: unavailable from the supplied execution data
- Unix sockets: none specified

**Configuration values to verify for Redis server on port 6379**:

- A `requirepass` directive is present in `/etc/redis/6379.conf`.
- The following directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- No bind address is assumed; verify the generated Redis configuration.

**Templates rendered**:

- None rendered; render count: `0`.

## Pre-flight checks

Replace `redis-server` with the actual Redis service unit name supplied by the `redisio` dependency role before running these checks.

### Redis server on port 6379: service status

```bash
systemctl status redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server
```

Expected result:

- The Redis service is enabled.
- The Redis service is active and running.

### Redis server on port 6379: configuration

```bash
test -f /etc/redis/6379.conf
grep -nE '^(requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result:

- `/etc/redis/6379.conf` exists.
- A `requirepass` directive is present.
- No line begins with any of the five removed directive names.
- The password is not printed in command output or logs.

### Redis server on port 6379: authentication and connectivity

Use the protected password from Ansible Vault or the approved secret backend:

```bash
export REDISCLI_AUTH='<redis_password_from_secure_storage>'
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
unset REDISCLI_AUTH
```

Expected result:

```text
PONG
```

The reported TCP port must be `6379`.

### Redis server on port 6379: listening socket

```bash
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'
```

Expected result:

- Redis is listening on TCP port `6379`.
- The bind address complies with the intended security policy.

### Redis server on port 6379: log directory

```bash
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis
```

Expected result:

- Directory: `/var/log/redis`
- Owner: `redis`
- Group: `redis`
- Permissions: `0755`

### Redis server on port 6379: logs

```bash
grep -nE '^(logfile|syslog-enabled|syslog-ident)' /etc/redis/6379.conf
journalctl -u redis-server --no-pager -n 50
```

Inspect the specific file named by the `logfile` directive if one is configured. The cookbook does not define an exact Redis log filename.

### Memcached dependency

The supplied cookbook does not provide a Memcached port or service name. After the `memcached` dependency is resolved, obtain its exact service and endpoint values from that dependency role and add a specific health check. Successful Memcached deployment cannot be established from this cookbook alone.