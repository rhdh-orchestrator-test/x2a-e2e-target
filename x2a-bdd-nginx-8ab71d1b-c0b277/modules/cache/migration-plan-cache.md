---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached is started and enabled through `memcached_instance[memcached]` with 64 MB memory, TCP/UDP port `11211`, 1,024 maximum connections, a wildcard listener, and a 1 MB maximum object size. Redis is configured with password authentication, PID directory `/run/redis`, log directory `/var/log/redis`, and an in-place configuration cleanup for `/etc/redis/6379.conf`. The `redisio` and `redisio::enable` recipes are unavailable in the supplied execution tree, so Redis package, account, service-unit, and unresolved dependency behavior must be explicitly established during migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: `/var/run/memcached`; log directory `/var/log/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1,024 maximum connections, 1 MB maximum object size, `ulimit` 1,024, empty experimental and additional CLI option lists, and start/enable actions
  - Threads: Read from `node['memcached']['threads']`; no default is present in the supplied attributes analysis
  - Service account: `service_user` and `service_group` are supplied to the custom resource, but their resolved values are unavailable

- **6379**: Redis cache service
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`
  - Key Config: Password `redis_secure_password_123`; `replicaservestaledata` set to `nil`; Redis enablement requested through `redisio::enable`
  - Log directory ownership: `redis:redis`, mode `0755`
  - Package and service name: Unresolved because the `redisio` implementation is unavailable

## File Structure

```text
### Recipes

cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb

### Providers

No provider file path was supplied in the execution tree for memcached_instance[memcached].

### Templates

No rendered ERB templates are shown in the execution tree.

### Attributes

migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

### Files

No static file deployed by cookbook_file or remote_file is shown.
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`, resolved to `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Defines one Redis server configuration for port `6379` with password `redis_secure_password_123` and `replicaservestaledata` set to `nil`.
   - Sets the Redis base PID directory to `/run/redis`.
   - Attempts to include `redisio`; the recipe is missing from the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]`:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Removes lines matching `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
     - Writes the modified configuration back to `/etc/redis/6379.conf`.
     - Makes no change when the file does not exist.
   - Attempts to include `redisio::enable`; the recipe is missing from the supplied execution tree.
   - The Ansible migration must establish the Redis package, account, configuration, service unit, enablement, and startup behavior explicitly.
   - Resource summary: three `include_recipe` operations, one `directory`, and one `ruby_block`. No explicit `group` resource is confirmed.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listener `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, `ulimit` `1024`, empty experimental options, and empty additional CLI options.
   - Passes `service_user` as the service user.
   - Reads the thread count from `node['memcached']['threads']`, for which no default is present in the supplied attributes analysis.
   - Requests actions `start` and `enable`.
   - The provider implementation is not present in the supplied execution tree. Package, account, runtime-directory, and log-directory behavior associated with the custom resource must therefore be treated as unresolved implementation behavior rather than independently verified resources.
   - Source-level observations identify the `memcached` package, `/nonexistent` home, `/bin/false` shell, locked account, `/var/run/memcached`, and `/var/log/memcached`; these require confirmation from the dependency implementation before being treated as migration requirements.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- `memcached`
- Redis package name unresolved because the `redisio` recipe is unavailable

**Service dependencies**:
- Memcached must be started and enabled
- Redis must be configured, enabled, and started after its missing dependency behavior is resolved
- Redis service-unit name is unresolved; it may be `redis`, `redis-server`, or a port-specific unit

**Supported platforms declared by metadata**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: None detected; the value is hardcoded in the recipe
  - **URL**: Not applicable
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in a Chef recipe
- **Usage context**: Redis authentication for instance `6379`
- **Detected integrations**: No data bags, Chef Vault, external secret manager, environment secret, TLS key, certificate, or PEM references were identified in the supplied source analysis
- **Migration handling**: Store the password in Ansible Vault and pass it to the Redis configuration through a protected variable

## Checks for the Migration

**Files to verify**:
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Redis bind address: not explicitly specified
- Unix sockets: none configured

**Templates rendered**:
- None; no Chef templates are shown
- Redis configuration is modified in place by `ruby_block[fix_redis_config]`, with one configuration file modification operation

## Pre-flight checks

```bash
# Confirm the target platform and required packages
cat /etc/os-release
command -v memcached
command -v redis-server || command -v redis

# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
printf "version\r\n" | nc -w 2 127.0.0.1 11211
printf "stats\r\n" | nc -w 2 127.0.0.1 11211
systemctl cat memcached
getent passwd memcached
getent group memcached
ls -ld /var/log/memcached
ls -ld /var/run/memcached

# Verify Memcached configuration
# Confirm the migrated service exposes:
# - TCP port 11211
# - UDP port 11211
# - Listener 0.0.0.0
# - Memory limit 64 MB
# - Maximum connections 1024
# - Maximum object size 1m
# - Ulimit 1024
# Resolve service_user and service_group before validating account names.

# Redis instance: 6379
systemctl list-unit-files | grep -E 'redis|redis-server'
systemctl list-units --type=service | grep -E 'redis|redis-server'

# Replace REDIS_UNIT with the service unit discovered above.
systemctl status "$REDIS_UNIT"
systemctl is-enabled "$REDIS_UNIT"
systemctl is-active "$REDIS_UNIT"
ps aux | grep '[r]edis-server'
ss -ltnp | grep ':6379'

# Use a protected secret mechanism instead of exposing the password in shell history.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server

# Verify Redis configuration and directories
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
ls -ld /run/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis

# Confirm the following directives were removed when present:
# replica-serve-stale-data
# replica-read-only
# repl-ping-replica-period
# client-output-buffer-limit
# replica-priority

# Review Redis logs using the resolved unit name.
journalctl -u "$REDIS_UNIT" --no-pager -n 100

# Verify service resource behavior
systemctl show memcached | grep -E 'MemoryCurrent|LimitNOFILE|TasksCurrent'
systemctl show "$REDIS_UNIT" | grep -E 'MemoryCurrent|LimitNOFILE|TasksCurrent'
```