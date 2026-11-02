---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The only locally available recipe is `cookbooks/cache/recipes/default.rb`; dependency recipe implementations are unavailable. The local recipe creates `/var/log/redis`, configures one Redis instance on port `6379` with password authentication, removes five replication-related directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. Memcached is included as a dependency, but its package, configuration path, service name, port, and daemon options cannot be determined from the supplied files.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is configured; `replicaservestaledata` is unset; five replication-related directives are removed after dependency configuration
  - Log Directory: `/var/log/redis`
  - Log Directory Owner/Group: `redis:redis`
  - Log Directory Mode: `0755`
  - Authentication: Password is defined by `node['redisio']['servers'][0]['requirepass']`; migrate it to Ansible Vault or an approved AAP credential
  - Configured Server Values:
    - `port`: `6379`
    - `requirepass`: hardcoded source value `redis_secure_password_123`
    - `replicaservestaledata`: `nil`

- **Memcached instance**: Included through the external `memcached` recipe; no exact instance name or runtime configuration is available
  - Location/Path: Not determinable from the supplied files
  - Port/Socket: Not specified
  - Key Config: Package, service name, configuration file, bind address, daemon options, and restart behavior must be obtained from `memcached` cookbook version `~> 6.0`

## File Structure

Only files shown as locally present or executed by the supplied execution tree are listed.

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

No attribute files are shown in the execution tree. Redis configuration is assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are shown as deployed by the execution tree.

The following dependency recipes are referenced by the local recipe but are unavailable and therefore are not listed as local cookbook files:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Assigns one Redis server definition to `node.default['redisio']['servers']`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - Removes selected directives from `/etc/redis/6379.conf`.
   - Includes `redisio::enable` to enable the configured Redis service.

   **Memcached dependency:**
   - Execution-tree status: `memcached Recipe file not found`.
   - The supplied files do not establish the package name, configuration path, service name, listening port, bind address, daemon options, or handlers.
   - These values must be confirmed from the `memcached` cookbook implementation before migration.

   **Redis server collection:**
   - The recipe configures exactly one Redis server item:
     - Instance: Redis server on port `6379`
     - Port: `6379`
     - Password: `redis_secure_password_123` in the source recipe
     - `replicaservestaledata`: `nil`
   - The password must be stored in Ansible Vault or an approved AAP credential mechanism and must not be placed in clear text in Ansible task files.

   **`directory[/var/log/redis]`:**
   - Creates `/var/log/redis`.
   - Uses `ansible.builtin.file` with:
     - `state: directory`
     - `owner: redis`
     - `group: redis`
     - `mode: '0755'`
   - The directory must exist before Redis is enabled.

   **Redis dependency:**
   - Execution-tree status: `redisio Recipe file not found`.
   - Expected role: install and configure Redis using the configured server on port `6379`.
   - The exact Redis package name, service name, installation paths, and template behavior must be confirmed from the `redisio` cookbook version.

   **`ruby_block[fix_redis_config]`:**
   - Sets the target file to `/etc/redis/6379.conf`.
   - Checks whether the file exists.
   - Reads the complete file.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified contents back to `/etc/redis/6379.conf`.
   - The Ansible implementation should use idempotent `ansible.builtin.replace` tasks.
   - Redis should be restarted or reloaded only through a handler notified when configuration changes; the original Ruby block does not explicitly notify a restart.

   **`redisio::enable`:**
   - Execution-tree status: `redisio::enable Recipe file not found`.
   - Intended role: enable the configured Redis service at boot.
   - The exact service unit name must be confirmed from the `redisio` dependency rather than guessed.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint
- `redisio::enable`, referenced recipe from the `redisio` cookbook

**System package dependencies**:

- Memcached package: not determinable from the supplied files
- Redis package: not determinable from the supplied files

The local cookbook does not directly install packages. Do not infer package names without inspecting the dependency cookbook versions.

**Service dependencies**:

- Memcached service: included through the unavailable `memcached` recipe; exact service name is unknown
- Redis service: enabled through the unavailable `redisio::enable` recipe; exact service name is unknown
- Redis configuration: `/etc/redis/6379.conf`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal source value**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis client authentication for the Redis instance listening on port `6379`
- **Migration handling**:
  - Store the password in Ansible Vault or an approved AAP credential.
  - Do not commit it to `group_vars`, `host_vars`, task files, or templates.
  - Use `no_log: true` for tasks that could expose the password.
  - Render the Redis configuration with restrictive permissions, preferably mode `0600` if supported by the target package.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secrets, TLS certificates, private keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis server on port `6379`
- Memcached instance: port not specified
- Unix sockets: none specified
- Network interfaces: none specified

**Configuration directives to verify in `/etc/redis/6379.conf`**:

The following directives must not remain:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

The Redis configuration must retain the configured password without exposing it in normal command output.

**Templates rendered**:

- None; no templates are present in the execution tree.
- Render count: `0`

## Pre-flight checks

Redis service names and package names must be confirmed from the `redisio` dependency before running service-specific commands. Memcached values must be confirmed from the `memcached` dependency before adding instance-specific validation.

```bash
# Redis instance: server on port 6379
systemctl status <confirmed-redis-service>
systemctl is-enabled <confirmed-redis-service>
ps aux | grep '[r]edis-server'
ss -ltnp | grep ':6379'

# Use a protected credential mechanism; do not place the password directly in shell history.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING

# Expected response:
# PONG

# Redis configuration file
test -f /etc/redis/6379.conf
grep -nE '^(port|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
! grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
grep -nE '^port[[:space:]]+6379$' /etc/redis/6379.conf

# Redis log directory
test -d /var/log/redis
stat -c '%A %U:%G %n' /var/log/redis
# Expected: drwxr-xr-x redis:redis /var/log/redis

# Redis logging destination
grep -nE '^(logfile|syslog-enabled|syslog-ident)' /etc/redis/6379.conf

# Use the confirmed Redis service name if it is not "redis".
journalctl -u <confirmed-redis-service> --no-pager -n 100

# Validate configuration through the installed Redis package.
redis-server /etc/redis/6379.conf --test-memory 2

# If the installed Redis version does not support the validation command,
# verify startup and inspect the service journal.
systemctl status <confirmed-redis-service>
journalctl -u <confirmed-redis-service> --no-pager -n 100
```

Memcached validation cannot be completed from the supplied cookbook files. After the dependency implementation confirms the exact service and port for the Memcached instance, run:

```bash
# Memcached instance: exact service and port must be confirmed first.
systemctl status <confirmed-memcached-service>
ss -ltnp | grep ':<confirmed-memcached-port>'
```