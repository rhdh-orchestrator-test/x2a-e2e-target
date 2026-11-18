---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache instances: Memcached named `memcached` and Redis on port `6379`. The supplied plan reports Memcached settings of 64 MB memory, TCP/UDP port `11211`, wildcard listening address `0.0.0.0`, and 1,024 maximum connections. It also reports Redis authentication, `/run/redis` as the PID directory, `/var/log/redis` as the log directory, and removal of five replication-related directives from `/etc/redis/6379.conf`. The Memcached dependency recipe and attributes file are present, while the `redisio` and `redisio::enable` implementations and the Memcached custom-resource provider are unavailable. Values not independently confirmed by the supplied structured analysis must be validated before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service managed by the `memcached_instance[memcached]` custom resource
  - Location/Path: `/var/log/memcached` and `/var/run/memcached`
  - Port/Socket: TCP `11211`, UDP `11211`, listening on `0.0.0.0`
  - Key Config: 64 MB memory, maximum 1,024 connections, maximum object size `1m`, ulimit `1024`, empty experimental and additional option lists, start and enable actions
  - Package: `memcached`
  - Threads: Uses `node['memcached']['threads']`; the value is not supplied
  - Service user/group: Passed as `service_user` and `service_group`; resolved names are not supplied
  - Validation status: Resource-level settings are reported by the source plan but are not independently confirmed by the supplied structured analysis

- **Redis on port 6379**: Redis cache service configured through `node['redisio']['servers']`
  - Location/Path: Configuration `/etc/redis/6379.conf`, PID directory `/run/redis`, log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Reported `requirepass` value `redis_secure_password_123`; log directory owner `redis`, group `redis`, mode `0755`; removal of five replication-related directives
  - Configuration directives removed when present:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`
  - Service actions: Intended to be enabled by `redisio::enable`; exact service unit is unavailable
  - Validation status: Redis values are reported by the source plan but are not independently confirmed by the supplied structured analysis

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No custom-resource provider path was supplied for `memcached_instance`. Do not invent a provider path during migration.

**Templates:**
```text
```

No templates are rendered by the visible recipes.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The structured analysis reports seven analyzed files, but the supplied directory listing identifies only the three paths above. The remaining analyzed paths are not available in the supplied input and must not be inferred.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Assigns one Redis server collection item, expanded as the single Redis instance on port `6379`.
   - Sets `redisio.base_piddir` to `/run/redis`.
   - Includes `redisio`; the implementation is missing from the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block[fix_redis_config]`.
   - Includes `redisio::enable`; the implementation is missing from the supplied execution tree.
   - Redis collection iteration:
     - **Port `6379`**: `port: 6379`, `requirepass: redis_secure_password_123`, and `replicaservestaledata: nil`.
   - `ruby_block[fix_redis_config]` checks for `/etc/redis/6379.conf`, removes lines matching the five specified directives, and preserves unrelated content.
   - The source does not explicitly notify a Redis service after the configuration edit; do not add an automatic restart unless required by the target Redis implementation.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Passes memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental options, and empty additional CLI options.
   - Passes `node['memcached']['threads']` as the thread value; no resolved value is supplied.
   - Passes unresolved `service_user` and `service_group` values.
   - Requests `start` and `enable` actions.
   - The provider is not present in the supplied file inventory, so package, account, directory, and service implementation details are reported but unverified.
   - Reported provider behavior to validate:
     - Install package `memcached` with no explicit version because `node['memcached']['version']` defaults to `nil`.
     - Create the system group represented by `service_group`.
     - Create and lock the system user represented by `service_user`, with home `/nonexistent`, comment `Memcached`, and shell `/bin/false`.
     - Create `/var/log/memcached` and `/var/run/memcached` with owner `service_user`, group `service_group`, and mode `0755`.
     - Start Memcached and enable it at boot.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- `memcached`
- Redis package: not identified because the `redisio` recipe is missing; do not select a package name without target-platform validation

**Service dependencies**:

- Memcached service managed by `memcached_instance[memcached]`
- Redis service intended to be managed by `redisio::enable`
- Exact Redis service unit name unavailable

## Credentials

**Detection Summary**: 1 credential reported in 1 file; the credential finding is not independently confirmed by the supplied structured analysis.

**Source**:
  - **Provider**: Hardcoded in the reported Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Value reported in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis `requirepass` authentication for the Redis instance on port `6379`
- **Migration handling**: Store the value in Ansible Vault, such as `redis_requirepass`, and render it with restrictive permissions. Do not retain the plaintext value in role defaults, inventory, or publicly readable variable files.

No data bags, encrypted data bags, Chef Vault items, CyberArk integration, Conjur variables, environment-variable secrets, TLS certificates, private keys, database connection strings, or API tokens were reported in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the validated Redis bind address
- Unix sockets: none specified

**Templates rendered**:

- None; render count `0`

**Configuration modifications**:

- `/etc/redis/6379.conf` is modified in place if it exists.
- The following directives must be absent after migration:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

```bash
# Confirm operating system and package availability
cat /etc/os-release
command -v memcached
command -v redis-server || true
command -v redis-cli || true

# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
printf "version\r\n" | nc -w 2 127.0.0.1 11211
printf "stats\r\n" | nc -w 2 127.0.0.1 11211
ls -ld /var/log/memcached
ls -ld /var/run/memcached
journalctl -u memcached --lines 50 --no-pager

# Validate Memcached configuration
# Confirm the generated configuration contains:
# memory: 64 MB
# TCP port: 11211
# UDP port: 11211
# listen address: 0.0.0.0
# maximum connections: 1024
# maximum object size: 1m
# ulimit: 1024

# Redis instance: port 6379
# Replace <redis-service-name> only after validating the target service unit.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>
ps aux | grep '[r]edis'
ss -ltnp | grep ':6379'
ls -ld /run/redis
ls -ld /var/log/redis
find /var/log/redis -maxdepth 1 -type f -print

# Validate Redis configuration
test -f /etc/redis/6379.conf
grep -E '^(requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Confirm the five unwanted directives are absent
! grep -Eq '^[[:space:]]*replica-serve-stale-data' /etc/redis/6379.conf
! grep -Eq '^[[:space:]]*replica-read-only' /etc/redis/6379.conf
! grep -Eq '^[[:space:]]*repl-ping-replica-period' /etc/redis/6379.conf
! grep -Eq '^[[:space:]]*client-output-buffer-limit' /etc/redis/6379.conf
! grep -Eq '^[[:space:]]*replica-priority' /etc/redis/6379.conf

# Use the Ansible Vault-managed password; do not place the plaintext password
# directly in shell history.
redis-cli -h 127.0.0.1 -p 6379 -a '<redis-password-from-vault>' PING
redis-cli -h 127.0.0.1 -p 6379 PING

# Redis logs
journalctl -u <redis-service-name> --lines 50 --no-pager

# Filesystem and runtime checks
df -h /var/log/redis
df -h /var/log/memcached
test -d /run/redis
test -d /var/run/memcached
test -d /var/log/redis
test -d /var/log/memcached
```

Expected results:

- The `memcached` instance is enabled, active, and listening on TCP and UDP port `11211`.
- Memcached responds to `version` and `stats`.
- The Redis instance on port `6379` is enabled, active, and reachable.
- Authenticated Redis access returns `PONG`; unauthenticated access fails when password enforcement is active.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- `/run/redis`, `/var/log/memcached`, and `/var/run/memcached` exist with permissions appropriate to their services.
- Both services start without permission, bind, or configuration parsing errors.