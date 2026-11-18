---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Memcached instance named `memcached` and one Redis instance identified by port `6379`. The supplied source configures Memcached through `memcached_instance[memcached]` and sets Redis attributes, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and includes Redis enablement. The Redis recipes and the Memcached custom-resource provider are missing from the supplied file set. Memcached values, Redis resource details, and the hardcoded Redis password are identified in the source-level plan but require verification against the complete cookbook analysis.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached in-memory cache
  - Location/Path: Provider-generated configuration path is not supplied
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1,024 maximum connections, 1 MB maximum object size, `service_user`, ulimit `1024`, empty experimental and additional CLI options, start and enable actions
  - Version: `nil`; no explicit version is pinned
  - Threads: `node['memcached']['threads']`; no default value is present in the supplied attribute analysis
  - Log Path: `/var/log/memcached` attribute; the supplied recipe does not explicitly create this path

- **6379**: Redis instance
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: Redis password is configured through `requirepass`; Redis is enabled through the missing `redisio::enable` recipe
  - Log Directory: Owner `redis`, group `redis`, mode `0755`, recursive creation
  - Configuration Cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` when present
  - Service Name: Not available from the supplied Redis cookbook files

The Memcached property values and Redis resource details above are source-level details from the migration plan. The supplied structured validation summary confirms the resource names but does not independently expose all properties, defaults, ownership, paths, or regular expressions.

## File Structure

```text
cookbooks/cache/recipes/default.rb

migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

**Providers:**

No provider files are included. The execution tree identifies the custom resource `memcached_instance[memcached]`, but its provider path is not supplied.

**Templates:**

No templates are listed or rendered.

**Static Files:**

No static files are listed or deployed.

**Missing referenced recipes:**

- `redisio::default`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **Cache default recipe** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency through `include_recipe 'memcached'`.
   - The included recipe resolves to `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Sets one Redis server object for port `6379` with `requirepass` set to the hardcoded value identified in the source as `redis_secure_password_123`.
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`; the corresponding `redisio::default` recipe is missing.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation, subject to verification against the complete source analysis.
   - Runs `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf` when the file exists.
   - Removes lines matching these directives:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Includes `redisio::enable`; the recipe is missing. The intended behavior is to enable Redis, but the resulting service name cannot be determined from the supplied files.

2. **Memcached default recipe** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates the custom resource `memcached_instance[memcached]`.
   - Configures the `memcached` instance with the source-level values below:
     - Memory: `64`
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - User: `service_user`
     - Threads: `node['memcached']['threads']`
     - Experimental options: `[]`
     - Additional CLI options: `[]`
     - Ulimit: `1024`
   - Starts and enables the `memcached` instance.
   - The custom-resource provider, package name, generated configuration path, and generated service unit are not included and must be verified before implementation.

No `.each` loops or other collection iterations requiring expansion were identified. The Redis configuration contains exactly one instance, named by port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`
- `redisio`

The `memcached` dependency is present in the supplied execution tree. The `redisio` recipes are missing.

**System package dependencies**:

- No package names are verified by the supplied source or execution tree.
- The target implementation must install the distribution-specific packages required for Memcached and Redis after validating the target operating system and the missing dependency cookbook behavior.

**Service dependencies**:

- `memcached` must be started and enabled.
- Redis must be configured and enabled after its configuration is created.
- The exact Redis service name is unavailable.
- The Memcached provider-generated service name and configuration path require verification.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute
- **Usage context**: Redis authentication for instance `6379`
- **Migration requirement**: Store the value in Ansible Vault or an approved AAP secret-management system. Do not commit the plaintext value to a playbook, role default, or inventory.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, database connection strings, or additional hardcoded credentials were detected.

The credential identification is based on the source-level plan; the supplied structured validation summary does not include an independent credential-detection result.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- Memcached's provider-generated configuration path
- Memcached's service configuration
- Redis's generated service configuration
- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the listener configured by the missing `redisio` cookbook
- Redis Unix socket: none specified
- Redis PID directory: `/run/redis`

**Templates rendered**:

- None

## Pre-flight checks

### Memcached instance: `memcached`

```bash
# Confirm the service exists, is running, and is enabled
systemctl status memcached
systemctl is-enabled memcached

# Confirm the Memcached process exists
pgrep -a memcached

# Confirm TCP port 11211 is listening
ss -ltnp | grep ':11211'

# Confirm UDP port 11211 is listening
ss -lunp | grep ':11211'

# Confirm the listener is bound to 0.0.0.0
ss -ltnp | grep '0.0.0.0:11211'

# Basic Memcached protocol check
printf 'version\r\n' | nc -w 2 127.0.0.1 11211

# Expected output includes:
# VERSION <version>

# Check runtime statistics
printf 'stats\r\n' | nc -w 2 127.0.0.1 11211 | grep -E \
  'STAT bytes|STAT curr_connections|STAT limit_maxbytes|STAT threads'

# 64 MB should correspond to approximately 67108864 bytes for limit_maxbytes,
# subject to provider unit conversion.
# Verify the maximum connection value through the available runtime statistics
# or the generated service configuration.

# Verify the configured logging destination after the provider path is identified
journalctl -u memcached --no-pager -n 100
```

### Redis instance: `6379`

```bash
# Identify the Redis service unit supplied by the target redisio implementation
systemctl list-unit-files | grep -E '^redis|redis-server'

# Check the Redis service after resolving its actual service name
systemctl status <redis-service-name>

# Confirm Redis is listening on port 6379
ss -ltnp | grep ':6379'

# Verify the Redis configuration file exists
test -f /etc/redis/6379.conf

# Verify the configured PID directory exists
test -d /run/redis

# Verify the Redis log directory and permissions
stat -c '%A %U %G %n' /var/log/redis

# Verify the five unwanted directives were removed
grep -nE \
  '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# The command should produce no output if the migration matches the
# source-level Chef behavior.

# Authenticate using the vaulted Redis password
redis-cli -h 127.0.0.1 -p 6379 \
  -a '<redis_password_from_ansible_vault>' PING

# Expected result:
# PONG

# Verify an authenticated write/read operation
redis-cli -h 127.0.0.1 -p 6379 \
  -a '<redis_password_from_ansible_vault>' SET migration_check ok

redis-cli -h 127.0.0.1 -p 6379 \
  -a '<redis_password_from_ansible_vault>' GET migration_check

# Expected result:
# ok

# Verify Redis is enabled at boot
systemctl is-enabled <redis-service-name>

# Review Redis service logs
journalctl -u <redis-service-name> --no-pager -n 100
```

### General checks

```bash
# Confirm both processes exist
pgrep -a memcached
pgrep -a redis

# Verify the Redis log directory contains expected files
find /var/log/redis -maxdepth 1 -type f -print

# Verify network connectivity to both configured endpoints
nc -zv 127.0.0.1 11211
nc -zv 127.0.0.1 6379
```

The placeholder `<redis-service-name>` must be replaced with the service name provided by the target Redis implementation. The Memcached log path and generated configuration path must be resolved from the custom-resource provider, which is not included in the supplied file listing.