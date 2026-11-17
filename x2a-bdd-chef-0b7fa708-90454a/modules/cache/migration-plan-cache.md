---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached is started and enabled through the `memcached_instance[memcached]` custom resource. Redis uses `/run/redis` for its PID directory, `/var/log/redis` for logs, and a password currently hardcoded in the Chef recipe. The Redis configuration at `/etc/redis/6379.conf` removes five replication-related directive families before Redis is enabled. The supplied execution tree does not include the implementations of `redisio`, `redisio::enable`, or the Memcached custom-resource provider, so package names, generated configuration paths, and exact service-unit names must be verified from the dependency sources or target platform.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: In-memory key/value cache
  - Location/Path: Provider-dependent configuration path; log path attribute `/var/log/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, maximum 1024 connections, 1 MB maximum object size, `service_user` user, ulimit `1024`, empty experimental and extra CLI options, start and enable actions. The worker-thread value is passed through from `node['memcached']['threads']`; no default is defined in the supplied attributes file. The version is `nil`, so no explicit version is configured.

- **Redis instance on port 6379**: In-memory data store and cache
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: Authentication password currently set to `redis_secure_password_123`; Redis is enabled through `redisio::enable`. The configuration removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` directives when present.

The supplied validation notes identify the Memcached and Redis attribute values as not independently verifiable from the available structured analysis. They are retained as values specified by the supplied migration plan and must be confirmed against the attributes file and dependency implementations before deployment.

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

No provider file was supplied in the execution tree. The `memcached_instance[memcached]` custom resource is used, but its provider implementation is not included in the provided file set.

**Templates:**
```text
```

No templates are rendered by the supplied recipes.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by the supplied recipes.

The following files appear in the directory listing but are not part of the executed flow:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

## Module Explanation

The cookbook performs operations in the following order.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`, resolved to `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Defines one Redis server item with port `6379`, `requirepass` set to `redis_secure_password_123`, and `replicaservestaledata` set to `nil`.
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` recipe for Redis installation and configuration.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf` when the file exists.
   - Removes complete lines matching `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
   - Writes the modified Redis configuration back in place without explicitly notifying a Redis restart or reload.
   - Includes the unavailable `redisio::enable` recipe to enable the Redis instance on port `6379`.
   - Iterations: One Redis server item is configured, with the actual item name represented by port `6379`. No executable `.each` loop is present in the supplied execution tree.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes the custom resource `memcached_instance[memcached]`.
   - Configures instance name `memcached` with memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, user `service_user`, empty experimental options, and empty extra CLI options.
   - Passes through the Memcached worker-thread attribute; no default is shown in the supplied attributes file.
   - Requests actions `:start` and `:enable`.
   - The custom-resource provider is not included, so the generated configuration path, template name, package behavior, and exact service unit must be verified from the dependency source or target system.

## Dependencies

**External cookbook dependencies**:

- `memcached`, executed from `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `redisio`, referenced by `cookbooks/cache/recipes/default.rb`; implementation unavailable
- `redisio::enable`, referenced by `cookbooks/cache/recipes/default.rb`; implementation unavailable

Additional metadata dependencies cannot be confirmed because the supplied file listing does not include metadata content.

**System package dependencies**:

- Memcached package name: not specified in the supplied recipes; verify from the Memcached dependency implementation or target platform.
- Redis package name: not specified in the supplied recipes; verify from the Redis dependency implementation or target platform.
- Service-management packages, if required: not specified; verify from the target platform.

No package version is configured for Memcached, and no Redis package version is supplied.

**Service dependencies**:

- Memcached service for instance `memcached`, started and enabled by `memcached_instance[memcached]`
- Redis service for instance `6379`, enabled by `redisio::enable`

The exact systemd unit names are unavailable from the supplied execution tree.

## Credentials

**Detection Summary**: 1 credential detected in 1 source file. This detection claim is based on the supplied recipe content; the available structured validation summary does not independently confirm it.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`
- **Migration storage**: Store the production value in Ansible Vault, for example `redis_password`
- **Migration handling**: Render the password with restricted permissions, use `no_log: true` on tasks that may expose it, and do not retain `redis_secure_password_123` as the production secret unless compatibility requires it

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, API keys, or database connection strings with embedded credentials were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- `/var/log/memcached`
- The provider-dependent Memcached configuration path
- The verified Redis service unit
- The verified Memcached service unit

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379`
- Redis Unix socket: none specified
- Redis PID directory: `/run/redis`

**Templates rendered**:

- Chef templates: none
- Ansible templates: implementation-dependent; if `/etc/redis/6379.conf` is generated by an Ansible template, verify exactly one rendered Redis configuration template for instance `6379`
- Memcached templates: provider-dependent and not present in the supplied file set

**Configuration mutations**:

- `/etc/redis/6379.conf` is modified in place by `ruby_block[fix_redis_config]`.
- The following directive families must be absent after migration:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

```bash
# Verify the target operating system and package manager.
cat /etc/os-release

# Verify the Memcached package name and installed package.
rpm -q memcached 2>/dev/null || dpkg-query -W memcached 2>/dev/null

# Verify the Redis package name and installed package.
rpm -q redis redis-server 2>/dev/null || dpkg-query -W redis redis-server 2>/dev/null
```

### Memcached instance `memcached`

```bash
# Confirm the verified Memcached service unit is active.
systemctl status memcached

# Confirm the service is enabled at boot.
systemctl is-enabled memcached

# Confirm Memcached is listening on TCP port 11211.
ss -ltnp | grep ':11211'

# Confirm Memcached is listening on UDP port 11211.
ss -lunp | grep ':11211'

# Confirm the Memcached protocol responds.
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Confirm Memcached statistics are available.
printf "stats\r\nquit\r\n" | nc -w 2 127.0.0.1 11211 | grep '^STAT'

# Verify the Memcached process arguments and configured limits.
ps -ef | grep '[m]emcached'

# Verify the provider-dependent Memcached configuration path.
# Replace the placeholder with the path discovered during implementation.
test -f <memcached-configuration-path>
```

Expected results:

- The `memcached` service is active and enabled.
- TCP and UDP port `11211` are listening on `0.0.0.0`.
- Memcached returns `VERSION` and `STAT` output.
- The process reflects the required 64 MB memory limit, maximum 1024 connections, 1 MB maximum object size, and ulimit `1024`.

### Redis instance `6379`

```bash
# Replace the placeholder with the exact unit discovered from redisio
# or the target operating system.
systemctl status <redis-6379-service-unit>

# Confirm the Redis instance is enabled at boot.
systemctl is-enabled <redis-6379-service-unit>

# Confirm Redis is listening on TCP port 6379.
ss -ltnp | grep ':6379'

# Confirm the Redis PID directory exists.
ls -ld /run/redis

# Confirm the Redis log directory ownership and mode.
stat -c '%A %U:%G %n' /var/log/redis

# Confirm the Redis configuration file exists.
test -f /etc/redis/6379.conf

# Confirm all removed directives are absent.
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected directive found"
  exit 1
else
  echo "Removed directives are absent"
fi

# Authenticate using the Ansible Vault-managed password.
redis-cli -p 6379 -a '<redis-password-from-Ansible-Vault>' PING

# Query Redis server information after authentication.
redis-cli -p 6379 -a '<redis-password-from-Ansible-Vault>' INFO server

# Verify an authenticated write/read/delete operation.
redis-cli -p 6379 -a '<redis-password-from-Ansible-Vault>' SET migration_check ok
redis-cli -p 6379 -a '<redis-password-from-Ansible-Vault>' GET migration_check
redis-cli -p 6379 -a '<redis-password-from-Ansible-Vault>' DEL migration_check
```

Expected results:

- The Redis service for instance `6379` is active and enabled.
- TCP port `6379` is listening.
- `/run/redis` exists.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- `/etc/redis/6379.conf` exists.
- All five removed directive families are absent.
- Authenticated `redis-cli PING` returns `PONG`.
- The write/read test returns `ok`.
- Redis rejects unauthenticated commands when authentication enforcement is active.

### Service logs

```bash
# Memcached instance logs.
journalctl -u memcached --no-pager -n 100

# Redis instance logs; replace the placeholder with the verified unit name.
journalctl -u <redis-6379-service-unit> --no-pager -n 100

# Verify Redis log files.
find /var/log/redis -maxdepth 1 -type f -print
```