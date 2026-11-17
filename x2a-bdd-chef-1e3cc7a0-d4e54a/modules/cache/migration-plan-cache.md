---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures Memcached through the external `memcached::default` recipe and references Redis configuration and enablement through the unavailable `redisio` and `redisio::enable` recipes. The supplied execution tree confirms the `memcached_instance[memcached]` resource and the Redis-related directory and configuration-cleanup resources, but does not include the Memcached provider, Redis recipes, package names, service names, attribute analysis, or credential analysis. Unavailable implementation details must be confirmed on the target system rather than inferred.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache instance managed by the external `memcached_instance` custom resource
  - Location/Path: Service configuration path is provider-defined and was not supplied
  - Port/Socket: TCP and UDP ports are provider-defined; the plan identifies port `11211`, but this value is not verifiable from the supplied execution tree
  - Key Config: Resource actions are `start` and `enable`; provider implementation, package name, service user, memory, connection limits, and other defaults were not supplied

- **Redis server on port 6379**: Redis instance referenced by the entry recipe
  - Location/Path: `/etc/redis/6379.conf`; runtime PID directory is intended to be `/run/redis`
  - Port/Socket: TCP port `6379`
  - Key Config: Redis installation and service implementation are delegated to the unavailable `redisio` and `redisio::enable` recipes. The entry recipe creates `/var/log/redis` and removes specified replication-related directives from `/etc/redis/6379.conf` when that file exists. Password configuration and other Redis attributes require confirmation from the complete recipe and credential analysis.

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

No custom-resource provider file was included in the execution tree. The `memcached_instance[memcached]` provider is therefore treated as an external implementation whose path was not supplied.

**Templates:**

```text
```

No templates are rendered by the supplied recipes or execution tree.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The directory listing also contains Memcached’s `_package.rb` recipe and SELinux recipes, but they are not present in the execution tree and are excluded from this migration scope.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached::default` recipe.
   - The included Memcached recipe path is `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - References Redis configuration through the unavailable `redisio` recipe.
   - Creates `directory[/var/log/redis]` with recursive creation enabled.
   - The directory owner, group, and mode are stated as `redis`, `redis`, and `0755` in the plan, but these properties require confirmation from the complete resource analysis.
   - Executes `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Does not create `/etc/redis/6379.conf` when the file is absent.
   - Includes `redisio::enable`; the recipe file and exact Redis service name were not supplied.
   - No `.each` loops or collection iterations are present in the supplied execution tree.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates `memcached_instance[memcached]`.
   - Applies actions `start` and `enable`.
   - The custom-resource provider path and implementation are not included in the execution tree.
   - Package installation, service configuration, service user, ports, limits, and other provider behavior must be confirmed from the provider or target platform.
   - No `.each` loops or collection iterations are present.

3. **redisio** (`redisio/recipes/default.rb`):
   - Referenced by `cookbooks/cache/recipes/default.rb`.
   - Recipe file not found in the supplied execution tree.
   - Redis package name, configuration templates, service name, configuration attributes, and provider behavior are unavailable and must not be invented.

4. **enable** (`redisio/recipes/enable.rb`):
   - Referenced by `cookbooks/cache/recipes/default.rb`.
   - Recipe file not found in the supplied execution tree.
   - The intended operation is to enable Redis, but the exact service unit name is unavailable.

## Dependencies

**External cookbook dependencies**: `memcached` via `memcached::default`; `redisio` via `redisio` and `redisio::enable`

**System package dependencies**: Not verifiable from the supplied execution tree. No package names may be selected until the Memcached provider and Redis implementation are confirmed.

**Service dependencies**: `memcached_instance[memcached]` is intended to start and enable Memcached. `redisio::enable` is intended to enable Redis, but the exact Redis service name is unavailable.

## Credentials

**Detection Summary**: 0 credentials confirmed in the supplied execution tree. The claimed Redis password was not present in the supplied execution-tree analysis and requires confirmation from the complete recipe and credential analysis.

**Source**:
  - **Provider**: None confirmed
  - **URL**: None detected
  - **Path**: None detected

No credentials or secrets can be confirmed from the supplied execution tree. If a Redis password is confirmed in the complete source analysis, store it in Ansible Vault or an equivalent secret-management mechanism rather than a committed plaintext variables file.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`

**Service endpoints to check**:

- Memcached instance `memcached`: port and protocol must be confirmed from the provider; the plan identifies TCP and UDP port `11211`
- Redis server on port `6379`: TCP port `6379`
- Unix sockets: None specified

**Templates rendered**:

- None

**Configuration transformations to verify**:

The following directives must not remain in `/etc/redis/6379.conf` after the cleanup task:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Confirm the target operating system and available package metadata
cat /etc/os-release
command -v systemctl
```

### Memcached instance: memcached

```bash
# Confirm whether the Memcached service unit exists
systemctl list-unit-files | grep -i memcached

# Check service status when the verified unit name is available
systemctl status memcached

# Confirm the Memcached process
pgrep -a memcached

# Check the planned TCP endpoint
ss -tlnp | grep ':11211'

# Check the planned UDP endpoint
ss -ulnp | grep ':11211'

# Verify the Memcached protocol over TCP
printf "version\r\n" | nc -w 2 127.0.0.1 11211
```

Confirm the actual Memcached package, service unit, listener configuration, resource limits, and service user from the provider or target host before implementation.

### Redis server on port 6379

```bash
# Discover the Redis service unit; do not assume the result
systemctl list-unit-files | grep -E '^redis|^redis-server'

# Confirm the Redis process
pgrep -a redis

# Confirm the Redis TCP listener
ss -tlnp | grep ':6379'

# Confirm the Redis configuration file
test -f /etc/redis/6379.conf && echo "Redis configuration exists"

# Confirm the runtime directory
test -d /run/redis && ls -ld /run/redis

# Confirm the log directory
test -d /var/log/redis && ls -ld /var/log/redis
```

### Redis configuration cleanup

```bash
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Expected: no matching lines
```

### Redis configuration and logs

```bash
# Inspect configured Redis paths and port
grep -nE '^(port|pidfile|dir|logfile)' /etc/redis/6379.conf

# Replace <redis-service-name> with the verified service unit
systemctl cat <redis-service-name>
systemctl status <redis-service-name>
journalctl -u <redis-service-name> --no-pager -n 100
```

### Directory and resource checks

```bash
# Confirm Redis runtime and log directories
ls -ld /run/redis /var/log/redis

# Confirm available space
df -h /run/redis /var/log/redis
```

### Migration implementation order

1. Confirm the Memcached provider, package, service unit, listener settings, and service user.
2. Install and configure the verified Memcached package.
3. Start and enable the `memcached` instance.
4. Confirm the Redis package, service unit, configuration path, and available Redis attributes.
5. Configure Redis on port `6379` if confirmed by the complete source analysis.
6. Configure `/run/redis` as the runtime PID directory if confirmed by the Redis implementation.
7. Create `/var/log/redis` with the verified ownership and mode.
8. Apply an idempotent cleanup task to `/etc/redis/6379.conf` for the five specified directives.
9. Start and enable the verified Redis service.
10. Validate the Memcached TCP and UDP endpoints.
11. Validate the Redis TCP endpoint and authenticated access only after a password is confirmed through source analysis.