---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer with one Redis instance on TCP port **6379** and an included Memcached dependency. The entry recipe defines Redis authentication, creates `/var/log/redis`, includes the external `redisio` cookbook, removes selected replication-related directives from `/etc/redis/6379.conf`, and requests `redisio::enable`. The supplied execution tree does not include the `memcached`, `redisio`, or `redisio::enable` recipes, so their package names, service names, templates, ports, and exact configuration behavior must be resolved before completing the Ansible migration. The Redis password is currently hardcoded and must be migrated to Ansible Vault or an approved secrets provider.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance `6379`**: Redis cache and authentication endpoint
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`
  - Key Config:
    - Authentication enabled with `requirepass`
    - Current password: `redis_secure_password_123`
    - `replicaservestaledata` is set to `nil`
    - Log directory: `/var/log/redis`
    - Log directory owner/group: `redis:redis`
    - Log directory mode: `0755`
    - Recursive directory creation enabled
    - The following directives are removed from the generated configuration when present:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`

- **Memcached dependency**: Included cache dependency
  - Location/Path: Not available in the supplied execution tree
  - Port/Socket: Not determinable from the supplied cookbook
  - Key Config:
    - Requested by `include_recipe 'memcached'`
    - Package, service name, configuration path, bind address, port, and templates must be resolved from the external `memcached` cookbook or deployment requirements
    - Do not assume the conventional port `11211` until verified

## File Structure

Only files present in the supplied directory listing and execution analysis are listed.

### Recipes

```text
cookbooks/cache/recipes/default.rb
```

### Providers

```text
None
```

### Templates

```text
None
```

### Attributes

```text
None
```

### Files

```text
None
```

Referenced recipes unavailable from the supplied execution tree:

```text
memcached
redisio
redisio::enable
```

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` recipe is unavailable in the supplied execution tree.
   - Resolve the Memcached package name, service name, configuration path, bind address, port, and startup behavior before implementing the dependency in Ansible.
   - Defines one Redis server entry:
     - Instance name: `6379`
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` as a directory owned by `redis:redis` with mode `0755` and recursive creation enabled.
   - Includes the external `redisio` recipe.
   - The `redisio` recipe is unavailable in the supplied execution tree and is expected to install Redis and generate `/etc/redis/6379.conf`.
   - Removes complete matching lines from `/etc/redis/6379.conf` when the file exists:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - The Chef `ruby_block[fix_redis_config]` does not explicitly restart or reload Redis.
   - Ansible should preserve the file-existence behavior with an existence check or an appropriate non-failing task and should notify a Redis restart only when configuration content changes.
   - Includes `redisio::enable`.
   - The `redisio::enable` recipe is unavailable; resolve whether it enables, starts, or otherwise manages the Redis service before implementing the equivalent Ansible service task.

### External dependency behavior to resolve

- **`memcached`**:
  - Exact package name
  - Exact service name
  - Configuration file or command-line configuration
  - Listening port and bind address
  - Enablement and startup behavior
  - Any templates rendered

- **`redisio`**:
  - Redis package name and version
  - Redis service name
  - Configuration template or managed configuration mechanism
  - Runtime user and group
  - Data directory
  - Log file path
  - Service restart behavior
  - Handling of `requirepass`
  - Handling of `replicaservestaledata: nil`

- **`redisio::enable`**:
  - Redis service enablement behavior
  - Redis service startup behavior
  - Any instance-specific service management

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package resources are defined in `cookbooks/cache/recipes/default.rb`.
- No system package names are verified by the supplied execution tree.
- Resolve the exact Memcached and Redis package names from the unavailable external cookbooks or target-platform requirements before implementation.

**Service dependencies**:

- Memcached service name: unresolved; verify from the external `memcached` cookbook.
- Redis service name: unresolved; verify from the external `redisio` cookbook or target platform.
- `redisio::enable` behavior: unresolved because the recipe is unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for instance `6379` on TCP port `6379`
- **Migration storage**: Store the value in Ansible Vault or an approved external secrets provider and reference it through a variable such as `redis_password`.
- **Security requirement**: Do not reproduce the plaintext password in committed Ansible defaults, templates, logs, or command output.

No data bag, encrypted data bag, Chef Vault item, Conjur variable, CyberArk data bag, environment-variable secret, TLS certificate, private key, or database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis/`

Paths potentially created by unavailable dependencies and requiring separate verification:

- Redis data directory
- Redis log file
- Redis PID or runtime directory
- Memcached configuration file

**Service endpoints to check**:

- Redis instance `6379`: TCP port `6379`
- Memcached dependency: port unresolved; verify from the external cookbook or target deployment configuration

**Templates rendered**:

- Supplied `cache` cookbook: 0 templates
- External `redisio` templates: unknown; dependency unavailable
- External `memcached` templates: unknown; dependency unavailable

## Pre-flight checks

```bash
# Redis instance 6379: resolve the actual service name before running these commands
systemctl status <resolved-redis-service-name>
systemctl is-enabled <resolved-redis-service-name>
systemctl is-active <resolved-redis-service-name>

# Redis configuration for instance 6379
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Confirm removed directives are absent from instance 6379 configuration
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis directives found"
  exit 1
fi

# Redis instance 6379 listener
ss -ltnp | grep ':6379'
lsof -nP -iTCP:6379 -sTCP:LISTEN

# Redis instance 6379 authentication and connectivity
# Supply the password securely; do not expose it in shell history or CI logs.
REDISCLI_AUTH='<vault-supplied-password>' redis-cli -p 6379 PING
REDISCLI_AUTH='<vault-supplied-password>' redis-cli -p 6379 INFO server

# Redis log directory
stat -c '%A %U:%G %n' /var/log/redis
ls -la /var/log/redis

# Expected directory properties:
# drwxr-xr-x redis:redis /var/log/redis

# Redis logging configuration
grep -E '^(logfile|syslog-enabled|syslog-ident)' /etc/redis/6379.conf
journalctl -u <resolved-redis-service-name> --no-pager -n 100
journalctl -u <resolved-redis-service-name> --no-pager | grep -Ei 'error|fatal|warning'

# Memcached dependency: resolve the service name and port before running these commands
systemctl status <resolved-memcached-service-name>
systemctl is-enabled <resolved-memcached-service-name>
systemctl is-active <resolved-memcached-service-name>
ss -ltnp | grep ':<resolved-memcached-port>'

# Typical Memcached protocol check after the port is verified
printf 'version\r\n' | nc 127.0.0.1 <resolved-memcached-port>
```

Expected results:

- Redis instance `6379` is enabled and active.
- `/etc/redis/6379.conf` exists.
- Redis listens on TCP port `6379`.
- Redis authentication succeeds without exposing the password.
- The five specified replication-related directive patterns produce no output.
- `/var/log/redis` exists with owner `redis:redis` and mode `0755`.
- The resolved Memcached service is enabled and active.
- The verified Memcached port is listening and returns a response beginning with `VERSION`.