---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two explicitly named cache instances: Memcached and Redis. Memcached is managed through `memcached_instance['memcached']` and is configured to start and enable on TCP and UDP port `11211`, listening on `0.0.0.0`. Redis is configured as a single server on port `6379`, with a hardcoded authentication password, `/run/redis` as its PID directory base, and `/var/log/redis` as its log directory. The Redis installation and enablement recipes are unavailable in the analyzed source, so the Ansible implementation must determine the target platform’s Redis package, service, and configuration details while preserving the observable settings documented here. The detailed Memcached and Redis values are extracted from the source plan but are not independently represented in the supplied structured validation summary.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service managed by the `memcached_instance['memcached']` custom resource
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `11211`; UDP `11211`
  - Key Config: Listen address `0.0.0.0`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; ulimit `1024`; experimental options and additional CLI options empty; actions `start` and `enable`
  - Package: `memcached`, with no explicit version
  - Service user/group: Provided by the Memcached dependency’s `service_user` and `service_group` values
  - Worker threads: Passed from `node['memcached']['threads']`; no value is available in the supplied attributes analysis

- **redis**: Redis cache service with one explicitly configured server
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory base `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication password is sourced from the hardcoded Chef attribute `node.default['redisio']['servers'][0]['requirepass']`; the source value is `redis_secure_password_123`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` from `/etc/redis/6379.conf`
  - Package/service: Not recoverable because the referenced `redisio` recipes were not found; determine the exact package and service names on the target platform

No `.each` iteration over a collection was identified. The Redis configuration contains one server entry on port `6379`.

## File Structure

The following complete directory listing is preserved from the original migration plan.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

The provider implementation for `memcached_instance` was not included in the execution tree. No provider path is inferred.

**Templates:**
```text
```

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

The following files were present in the directory listing but were not shown as executed by the supplied execution tree:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

## Module Explanation

The cookbook performs operations in the following execution order. No `.each` loops were identified.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Configures one Redis server entry on port `6379` with the source password value `redis_secure_password_123` and `replicaservestaledata: nil`.
   - Sets the Redis PID directory base to `/run/redis`.
   - Includes `redisio`; the referenced recipe file was not found in the execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block['fix_redis_config']`, which checks for `/etc/redis/6379.conf`, removes lines beginning with the five replication-related directives, and rewrites the file when it exists.
   - Includes `redisio::enable`; the referenced recipe file was not found in the execution tree.
   - Analyzed resources confirmed by the supplied execution tree: `directory['/var/log/redis']` and `ruby_block['fix_redis_config']`.
   - The Redis group is an inferred migration prerequisite for assigning group ownership to `/var/log/redis`; it is not shown as an analyzed Chef resource in the supplied execution tree.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares `memcached_instance['memcached']`.
   - Passes memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, empty experimental options, empty extra CLI options, ulimit `1024`, and actions `start` and `enable`.
   - Passes the service user and the value of `node['memcached']['threads']`; the available validation summary does not provide a confirmed worker-thread value.
   - Installs the `memcached` package without forcing a version.
   - Creates or preserves the dependency-provided service account and group.
   - Creates `/var/log/memcached` and `/var/run/memcached` with mode `0755`.
   - Configures Memcached for TCP and UDP port `11211`, listener `0.0.0.0`, memory `64` MB, maximum connections `1024`, maximum object size `1m`, and ulimit `1024`.
   - Starts and enables the Memcached service.
   - No Memcached template was provided; use the target platform’s native configuration mechanism or generate a file only when required.

3. **Redis installation/configuration referenced by `redisio`** (`redisio`):
   - The recipe file was not found in the supplied execution tree.
   - Determine and install the target platform’s verified Redis package.
   - Configure the Redis server on port `6379`.
   - Configure authentication using the vaulted migration secret.
   - Use `/run/redis` as the PID directory base.
   - Ensure the inferred prerequisite `redis` group exists.
   - Create `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Ensure `/etc/redis/6379.conf` exists after installation.
   - Remove the five specified directives from `/etc/redis/6379.conf`.
   - Do not infer an unavailable package name, service name, template path, or configuration implementation.

4. **Redis enablement referenced by `redisio::enable`** (`redisio::enable`):
   - The recipe file was not found in the supplied execution tree.
   - Discover the exact Redis service name on the target platform.
   - Enable and start that service.
   - Notify a Redis restart or reload only when the configuration changes.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- `memcached`, confirmed by the Memcached dependency
- Redis package name not available from the analyzed source; verify it for the target operating system before implementation

**Service dependencies**:
- Memcached service, started and enabled by `memcached_instance['memcached']`
- Redis service, intended to be enabled by `redisio::enable`; exact service name unavailable

## Credentials

**Detection Summary**: 1 credential detected in 1 source file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef attribute value
- **Source value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the instance listening on port `6379`

The Ansible migration must not preserve the password as plaintext in the playbook or committed variable files. Store it in Ansible Vault or an approved AAP credential/secret integration and use the vaulted variable when rendering Redis configuration.

No data bag, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secret, TLS certificate, private key, database connection string, API token, or SSH key reference was detected.

## Checks for the Migration

**Files to verify**:
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- The platform-specific Memcached configuration file, if generated
- The platform-specific Redis PID directory under `/run/redis`

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379`
- Unix sockets: none specified

**Templates rendered**:
- Chef templates: none identified or rendered
- Ansible templates: target-platform Redis or Memcached templates, only if required by the implementation; expected Chef render count is zero

**Configuration transformations**:
- `/etc/redis/6379.conf` is rewritten by the equivalent of `ruby_block['fix_redis_config']` when it exists.
- The Ansible implementation must remove the five specified directives idempotently and report changes only when a directive is removed.

## Pre-flight checks:

```bash
# Confirm the Memcached instance individually
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
ps auxww | grep '[m]emcached'
ls -ld /var/log/memcached /var/run/memcached

# Verify Memcached configuration values
printf "version\r\n" | nc -w 2 127.0.0.1 11211
printf "version\r\n" | nc -u -w 2 127.0.0.1 11211
# Confirm listener 0.0.0.0, TCP/UDP port 11211, memory 64 MB,
# max connections 1024, max object size 1m, and ulimit 1024
# using the platform-specific configuration file or process command line.

# Discover and confirm the exact Redis service name before running these checks.
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
ss -ltnp | grep ':6379'
ps aux | grep '[r]edis'

# Confirm the Redis runtime and configuration paths
getent group redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis
grep -E '^(port|pidfile|dir)' /etc/redis/6379.conf

# Confirm the five directives were removed
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Test Redis authentication without placing the password in shell history.
read -r REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD

# Expected authenticated response:
# PONG

# Confirm unauthenticated access is rejected when authentication is enabled.
redis-cli -p 6379 PING

# Check Redis logs using the exact discovered service name.
journalctl -u redis --since "-10 minutes" --no-pager

# Check both named service endpoints.
ss -ltnp | grep -E ':(6379|11211)\b'
ss -lunp | grep ':11211'
```