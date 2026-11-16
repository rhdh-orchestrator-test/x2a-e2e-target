---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache services: the `memcached` instance and one Redis instance on port `6379`. Memcached uses 64 MB of memory, TCP/UDP port `11211`, `0.0.0.0` binding, 1,024 maximum connections, a 1 MB maximum object size, and start/enable actions. Redis uses `/run/redis` for its PID directory, `/var/log/redis` for logs, password authentication, and post-configuration removal of five replication-related directives from `/etc/redis/6379.conf`. The Redis and Redis enable recipes are referenced but missing from the supplied execution tree, so their package, service, and configuration implementation must be selected and verified during migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Distributed in-memory key/value cache
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1,024 maximum connections, 1 MB maximum object size, ulimit `1024`, empty experimental and extra CLI options, start and enable actions
  - Service user: Receives `service_user`; the resolved value is not shown in the supplied files

- **Redis instance on port 6379**: In-memory data store and cache
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`
  - Key Config: Password authentication enabled; password is `redis_secure_password_123`; the following directives are removed after configuration: `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Instance identifier: One entry in `node['redisio']['servers']`
  - Additional settings: No Redis bind address, database count, memory limit, or additional Redis instance is explicitly defined

## File Structure

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

No provider, template, or static file paths were supplied. The provider for `memcached_instance[memcached]` is not present in the supplied execution tree. The four dependency recipe paths listed above are directory-listed files that were not included as executed recipe files.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached recipe.
   - Assigns one Redis server entry with port `6379`, password `redis_secure_password_123`, and `replicaservestaledata` set to `nil`.
   - Assigns Redis base PID directory `/run/redis`.
   - Includes the missing `redisio` recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Processes `/etc/redis/6379.conf` with `ruby_block[fix_redis_config]` when the file exists.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Includes the missing `redisio::enable` recipe.
   - The Ansible implementation should use idempotent replacement tasks and preserve the conditional behavior when `/etc/redis/6379.conf` is absent.
   - Chef declares no notification from `ruby_block[fix_redis_config]`; an explicit Redis restart is therefore not established by the supplied recipe.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates `memcached_instance[memcached]`.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listener `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, and the supplied `service_user`.
   - Passes an undefined `node['memcached']['threads']` value because no threads default is shown in the supplied attributes file.
   - Passes empty experimental-options and extra-CLI-options lists.
   - Starts and enables the Memcached service.
   - The underlying custom-resource provider is unavailable; do not infer provider-specific package versions, systemd unit names, generated configuration paths, or restart behavior.

3. **Redis configuration and enablement** (`redisio` and `redisio::enable`, referenced from `cookbooks/cache/recipes/default.rb`):
   - These recipes are missing from the execution tree.
   - The migration must implement Redis installation, configuration, and enablement.
   - Package name, service name, Redis configuration template, restart policy, and distribution-specific paths must be confirmed against the selected target implementation.

**Iterations**: No `.each` loops are present. The Redis collection contains exactly one configured entry:

- Redis entry on port `6379`
  - `requirepass`: `redis_secure_password_123`
  - `replicaservestaledata`: `nil`

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**System package dependencies**:

- `memcached` is referenced by the Memcached dependency package recipe.
- The Redis package name is not visible because the `redisio` recipe is missing and must not be invented before target distribution and implementation are confirmed.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Service dependencies**:

- The `memcached` service must be installed, running, and enabled.
- Redis must be installed, configured, running, and enabled.
- The `redis` user and group must exist before `/var/log/redis` is created.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in a Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext recipe value
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Enables Redis `requirepass` authentication for the instance on port `6379`
- **Migration handling**: Store the value in Ansible Vault, preferably as `redis_password`, and render it into the Redis configuration without committing the plaintext value

No data bag, Chef Vault, Conjur, CyberArk, HashiCorp Vault, AWS Secrets Manager, or secret environment-variable reference was detected. No TLS certificate, private key, `.pem`, `.key`, or `.crt` reference was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- `/var/log/memcached`
- `/var/run/memcached`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Unix sockets: none specified

**Templates rendered**:

- Chef templates: none
- Ansible templates: Redis configuration template, render count to be established by the selected implementation
- Memcached templates: none identified in the supplied execution tree

## Pre-flight checks:

```bash
# Memcached: verify service state.
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Memcached: verify the process and TCP/UDP listeners.
ps aux | grep '[m]emcached'
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'

# Memcached: verify the statistics endpoint.
printf "stats\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Memcached: verify configured values where exposed by the package.
systemctl cat memcached
ps -ef | grep '[m]emcached' | grep -E -- '-m 64|-p 11211|-U 11211|-l 0.0.0.0|-c 1024'

# Memcached: verify directories.
stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached

# Redis instance on port 6379: verify the selected service unit.
systemctl list-units --type=service | grep -E 'redis|6379'
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Redis instance on port 6379: verify the listener.
ss -ltnp | grep ':6379'

# Redis instance on port 6379: test authenticated access without storing the password in shell history.
export REDISCLI_AUTH='<retrieve-from-Ansible-Vault>'
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'

# Redis instance on port 6379: confirm unauthenticated access is rejected.
env -u REDISCLI_AUTH redis-cli -p 6379 PING

# Redis instance on port 6379: verify requirepass without exposing its value.
grep -E '^requirepass ' /etc/redis/6379.conf | sed 's/ .*/ <redacted>/'

# Redis instance on port 6379: verify removed directives are absent.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || true

# Redis instance on port 6379: verify runtime and log directories.
stat -c '%A %U:%G %n' /run/redis
stat -c '%A %U:%G %n' /var/log/redis

# Redis instance on port 6379: review logs using the confirmed service unit.
journalctl -u redis --no-pager -n 100
```

Expected results:

- The `memcached` service is active and enabled.
- Memcached listens on TCP and UDP port `11211` on `0.0.0.0`.
- Memcached uses 64 MB memory, maximum connections `1024`, listener `0.0.0.0`, and the configured ports, subject to the selected package’s command-line representation.
- The Redis instance on port `6379` is active and enabled.
- Redis listens on port `6379`.
- Authenticated Redis `PING` returns `PONG`.
- Unauthenticated Redis access fails with an authentication error.
- The five specified replication-related directives are absent from `/etc/redis/6379.conf`.
- `/run/redis` and `/var/log/redis` exist with the expected Redis ownership.