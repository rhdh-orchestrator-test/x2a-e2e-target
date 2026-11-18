---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached is managed through the `memcached_instance` custom resource and is started and enabled. Redis is configured through the unavailable `redisio` dependency, followed by creation of `/var/log/redis`, cleanup of selected directives in `/etc/redis/6379.conf`, and inclusion of `redisio::enable`. Memcached settings and Redis values are derived from the supplied recipe and dependency files where available; the missing `redisio` implementation must be validated before finalizing Redis package, service, data-directory, and configuration details.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached caching service
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: Package `memcached`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; ULimit `1024`; worker threads from `node['memcached']['threads']`; empty `experimental_options` and `extra_cli_options`; actions `start` and `enable`
  - Service account: Dependency-defined `service_user` and `service_group`; concrete values require validation from the dependency cookbook

- **redis-6379**: Redis cache service
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory base `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket configured in the supplied recipe
  - Key Config: Exactly one Redis server configured; `requirepass` is set by the Chef recipe to `redis_secure_password_123`; `replicaservestaledata` is `nil`; five replication and buffer directives are removed from the configuration when present
  - Service: Enabled through the unavailable `redisio::enable` recipe; exact service name requires dependency validation

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

No provider file was supplied in the execution tree. The provider implementation for `memcached_instance[memcached]` is unresolved and must be validated from the dependency cookbook.

**Templates:**
```text
```

No rendered ERB templates are present in the supplied execution tree.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` are present in the supplied execution tree.

The following files were present in the directory listing but are not part of the executed flow:

- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb`

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Sets the Redis server collection to exactly one item on port `6379`.
   - Sets the Redis password to `redis_secure_password_123`.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the Memcached dependency recipe.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis`.
   - Runs `ruby_block['fix_redis_config']`.
   - Includes the unavailable `redisio::enable` recipe.

   **Redis configuration assigned by this recipe:**
   - Port: `6379`
   - `requirepass`: `redis_secure_password_123`
   - `replicaservestaledata`: `nil`
   - PID directory base: `/run/redis`

   **Redis configuration cleanup:**
   - Operates only when `/etc/redis/6379.conf` exists.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes changes back to `/etc/redis/6379.conf`.
   - The Chef resource does not explicitly declare a service notification. Ansible should restart or reload Redis only when the resulting file changes, subject to validation of the Redis implementation.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates or configures the `memcached_instance[memcached]` custom resource.
   - Configures the instance named `memcached`.
   - Passes memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ULimit `1024`, empty experimental options, and empty extra CLI options.
   - Passes worker threads from `node['memcached']['threads']`.
   - Passes dependency-defined `service_user` and `service_group` values.
   - Executes actions `start` and `enable`.
   - The custom-resource provider is not present in the supplied execution tree; reproduce the observed service state after validating the dependency provider.

3. **`redisio`** (`redisio` dependency recipe; source file unavailable):
   - Intended to install and configure the Redis instance on port `6379`.
   - Expected to generate or manage `/etc/redis/6379.conf`.
   - Expected to create the Redis user, group, data directory, and service.
   - Exact package name, service name, configuration-generation behavior, data directory, and ownership must be obtained from the dependency cookbook before production migration.

4. **`directory[/var/log/redis]`** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis` recursively.
   - Sets owner `redis`, group `redis`, and mode `0755`.

5. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Checks for `/etc/redis/6379.conf`.
   - Performs no action when the file does not exist.
   - Removes the five specified directive classes from complete configuration lines when the file exists.
   - Preserves the file path and writes the modified content in place.

6. **`redisio::enable`** (`redisio` dependency recipe; source file unavailable):
   - Intended to enable Redis at boot after Redis configuration cleanup.
   - Exact service resource and service name require validation from the dependency cookbook.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint
- SELinux dependency artifacts are present in the directory listing but are not part of the executed flow

**System package dependencies**:

- `memcached`
- Redis package name: unresolved because the `redisio` recipe is unavailable; do not finalize the package name until the dependency implementation is validated

**Service dependencies**:

- Memcached service managed by `memcached_instance[memcached]`
- Redis service intended to be enabled by `redisio::enable`; exact service name unresolved
- Redis configuration must be deployed before the Redis service is enabled or started

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Configured value**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute assignment
- **Usage context**: Redis password authentication for the Redis instance on port `6379`

The Ansible migration must store the password in Ansible Vault or an external secret-management system. It must not retain the password in plaintext in a normal variables file, command line, process arguments, or shell history. The Redis `requirepass` behavior must be preserved.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificates, private keys, database connection strings, or API tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

The Redis data directory and final Redis log-file path require validation from the unavailable `redisio` dependency.

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `6379`
- Redis Unix socket: none configured

**Templates rendered**:

- None detected; render count: `0`

**Configuration transformations**:

- `/etc/redis/6379.conf` is conditionally modified in place by removing five classes of replica and buffer directives.

## Pre-flight checks

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
pgrep -a memcached

# Memcached TCP and UDP endpoints
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'

# Expected protocol response
printf "version\r\n" | nc -w 2 127.0.0.1 11211

# Memcached directories
stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached

# Redis instance: redis-6379
# Replace redis.service with the validated service name from redisio.
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
pgrep -a redis
ss -ltnp | grep ':6379'

# Redis authenticated connectivity.
# Supply the vaulted password through a protected mechanism; do not place it
# literally in the command line or shell history.
redis-cli -p 6379 --askpass PING

# Redis configuration
test -f /etc/redis/6379.conf
stat -c '%A %U:%G %n' /etc/redis/6379.conf
grep -E '^[[:space:]]*requirepass[[:space:]]+' /etc/redis/6379.conf

# Expected: no matching active lines
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Redis directories
stat -c '%A %U:%G %n' /var/log/redis
stat -c '%A %U:%G %n' /run/redis

# Expected for /var/log/redis: redis:redis ownership and mode equivalent to 0755
journalctl -u memcached --no-pager -n 50
journalctl -u redis --no-pager -n 50

# Package verification
dpkg-query -W memcached 2>/dev/null || rpm -q memcached

# Verify the Redis package only after obtaining its exact name from redisio.
```

Before production migration, validate the missing `redisio` and `redisio::enable` implementations for the Redis package, service name, configuration-generation behavior, data directory, user and group, and startup behavior.