---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached uses the `memcached_instance` custom resource with 64 MB memory, TCP and UDP port `11211`, a `0.0.0.0` listener, 1,024 maximum connections, a `1m` maximum object size, and start/enable actions. Redis uses `/run/redis` for its PID directory, `/var/log/redis` for logs, password authentication, and post-processing that removes five replication-related directive families from `/etc/redis/6379.conf`. The `redisio` and `redisio::enable` recipes and the Memcached provider are unavailable, so their package names, templates, service unit names, and provider-specific behavior must be confirmed on the target platform.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached cache service
  - Location/Path: Provider/platform-dependent service configuration; no exact path is supplied
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1,024 maximum connections, `1m` maximum object size, `1024` ulimit, empty experimental and extra CLI option lists, start and enable actions
  - Threads: Read from `node['memcached']['threads']`; no supplied default exists
  - User: `service_user`; concrete account value is not defined in the supplied files

- **Redis server on port `6379`**: Authenticated Redis cache service
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`
  - Key Config: `requirepass` set to the hardcoded value `redis_secure_password_123`; log directory owner `redis`, group `redis`, mode `0755`, recursive creation
  - Post-configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` directives when `/etc/redis/6379.conf` exists
  - Enablement: Delegated to the unavailable `redisio::enable` recipe

## File Structure

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Recipes referenced but not found:**

```text
redisio
redisio::enable
```

**Providers:**

```text
```

No `memcached_instance` provider file is listed.

**Templates:**

```text
```

No rendered templates are listed.

**Files:**

```text
```

No static files deployed through `cookbook_file` or `remote_file` are listed.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe before configuring Redis.
   - Sets one Redis server entry on port `6379` with `requirepass` set to `redis_secure_password_123` and `replicaservestaledata` set to `nil`.
   - Sets `redisio['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` recipe. Its package resources, service resources, templates, and provider behavior cannot be determined from the supplied files.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Runs `ruby_block[fix_redis_config]` to rewrite `/etc/redis/6379.conf` when the file exists.
   - Removes lines matching `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
   - Does not explicitly restart or reload Redis after rewriting the configuration.
   - Includes the unavailable `redisio::enable` recipe after the Redis configuration and cleanup operations.
   - Iterations: one Redis server entry is configured on port `6379`; no `.each` loop is present.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates one `memcached_instance['memcached']` custom resource.
   - Configures memory `64` MB.
   - Configures TCP port `11211` and UDP port `11211`.
   - Listens on `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Sets maximum object size to `1m`.
   - Passes `node['memcached']['threads']`; no default is supplied.
   - Passes empty `experimental_options` and `extra_cli_options` lists.
   - Sets ulimit to `1024`.
   - Passes the `service_user` account value.
   - Applies actions `start` and `enable`.
   - Iterations: one custom resource named `memcached` is created; no `.each` loop is present.

## Dependencies

**External cookbook dependencies**:

- `memcached`, constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package installation is delegated to the unavailable `memcached_instance` provider; the package name is not supplied.
- Redis package installation is delegated to the unavailable `redisio` recipe; the package name is not supplied.
- No package names or versions can be verified from the supplied files.

**Service dependencies**:

- Memcached service, started and enabled by `memcached_instance['memcached']`
- Redis service, intended to be enabled by `redisio::enable`
- Redis system account and group `redis`, required for `/var/log/redis`

**Operating system support**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded in a Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the instance listening on port `6379`
- **Migration handling**: Store the value in Ansible Vault or an AAP-managed credential, use the vaulted variable when rendering Redis configuration, and apply `no_log: true` to tasks that could expose it.

No data bag, Chef Vault, CyberArk, Conjur, environment-variable secret reference, TLS certificate, private key, or database connection credential was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- Memcached service configuration path, to be confirmed for the target platform
- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379`
- Unix sockets: None specified

**Templates rendered**:

- None; no Chef templates are listed as rendered.

**Configuration mutations**:

- `/etc/redis/6379.conf` is rewritten in place when present.
- Removed directive families:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks:

```bash
# Confirm required commands are available
command -v systemctl
command -v ss
command -v nc
command -v redis-cli

# Confirm no failed systemd units
systemctl --failed
```

### Memcached instance `memcached`

```bash
# Confirm the service is active and enabled
systemctl status memcached
systemctl is-enabled memcached

# Confirm the Memcached process is running
pgrep -a memcached

# Verify the configured TCP listener
ss -ltnp | grep ':11211'

# Verify the configured UDP listener
ss -lunp | grep ':11211'

# Test the Memcached TCP protocol
printf "version\r\n" | nc -w 2 127.0.0.1 11211

# Verify TCP reachability
nc -zv 127.0.0.1 11211

# Review service logs
journalctl -u memcached --since "15 minutes ago"
```

Expected results:

- The Memcached service is active and enabled.
- A TCP listener exists on port `11211`.
- A UDP listener exists on port `11211`.
- The protocol test returns a line beginning with `VERSION`.

### Redis instance on port `6379`

```bash
# Confirm the actual Redis unit name and status
systemctl status redis
systemctl status redis-server
systemctl is-enabled redis || systemctl is-enabled redis-server

# Confirm the Redis process is running
pgrep -a redis-server

# Verify the Redis TCP listener
ss -ltnp | grep ':6379'

# Verify the Redis configuration file
test -f /etc/redis/6379.conf && echo "Redis configuration exists"

# Verify the Redis PID directory
test -d /run/redis && ls -ld /run/redis

# Verify the Redis log directory and permissions
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis

# Verify removed directives are absent
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || echo "Cleanup directives are absent"

# Supply the vaulted password without committing it to shell history
read -rsp 'Redis password: ' REDIS_PASSWORD
export REDIS_PASSWORD
echo

# Test authenticated access
redis-cli -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning PING

# Verify Redis server information
redis-cli -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning INFO server \
  | grep -E 'redis_version|tcp_port'

# Verify authentication is required
redis-cli -p 6379 PING

# Review Redis service logs
journalctl -u redis --since "15 minutes ago"
journalctl -u redis-server --since "15 minutes ago"

# Verify filesystem permissions
find /var/log/redis -maxdepth 1 -printf '%M %u:%g %p\n'
find /run/redis -maxdepth 1 -printf '%M %u:%g %p\n'
stat /etc/redis/6379.conf
```

Expected results:

- Redis is active and enabled under the confirmed service unit.
- Redis listens on port `6379`.
- An authenticated `PING` returns `PONG`.
- An unauthenticated `PING` fails with an authentication error.
- The five removed directive families do not appear in `/etc/redis/6379.conf`.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- `/run/redis` exists and is usable by the Redis service.

The migration is complete when the `memcached` instance is enabled and reachable on TCP and UDP port `11211`, Redis is enabled and authenticated on port `6379`, the Redis directories have the required configuration and permissions, and the Redis cleanup has been applied without exposing the Redis password.