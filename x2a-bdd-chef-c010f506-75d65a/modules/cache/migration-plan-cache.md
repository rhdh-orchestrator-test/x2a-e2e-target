---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache services: one Memcached instance named `memcached` and one Redis server on port `6379`. Memcached uses the `memcached_instance[memcached]` custom resource with 64 MB of memory, TCP and UDP port `11211`, a listen address of `0.0.0.0`, and 1,024 maximum connections. Redis uses `/run/redis` for its PID directory, `/var/log/redis` for logs, and a password that must be migrated to Ansible Vault. The Redis installation and enable recipes are unavailable, so their exact package and service names must be verified before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Distributed in-memory cache managed by `memcached_instance[memcached]`
  - Location/Path: Memcached package configuration path is distribution-dependent and unavailable in the supplied Chef files
  - Port/Socket: TCP `11211`; UDP `11211`
  - Key Config: Memory `64` MB; listen address `0.0.0.0`; maximum connections `1024`; maximum object size `1m`; threads sourced from `node['memcached']['threads']` with no supplied default; user set from `service_user`; ulimit `1024`; experimental and additional CLI options are empty; actions are `start` and `enable`
  - Log Path: `/var/log/memcached`

- **redis-6379**: Redis in-memory datastore and cache
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password currently set to `redis_secure_password_123`; password must be stored in Ansible Vault; PID directory `/run/redis`; log directory `/var/log/redis`; service account `redis`; service group `redis`
  - Configuration Cleanup: Removes directives beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

### Referenced but unavailable recipes

```text
redisio
redisio::enable
```

No provider file path was supplied for `memcached_instance`. No templates or static files are present in the supplied execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe at `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Sets `node['redisio']['servers']` to one Redis server definition:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` recipe. Its package, configuration, and service resources must be verified separately.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf` when the file exists.
   - Removes lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Includes the unavailable `redisio::enable` recipe after Redis configuration cleanup. Its exact service behavior must be verified.
   - Preserves the observed ordering: Memcached inclusion, Redis attribute assignment, Redis recipe inclusion, Redis log directory creation, Redis configuration cleanup, and Redis enable recipe inclusion.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates exactly one custom resource: `memcached_instance[memcached]`.
   - Configures the `memcached` instance with:
     - Memory: `64` MB
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - Threads: `node['memcached']['threads']`; no default supplied
     - User: `service_user`
     - Experimental options: `[]`
     - Additional CLI options: `[]`
     - Ulimit: `1024`
     - Actions: `start`, `enable`
   - The Memcached dependency attributes include:
     - `node['memcached']['version']`: `nil`
     - `node['memcached']['memory']`: `64`
     - `node['memcached']['port']`: `11211`
     - `node['memcached']['udp_port']`: `11211`
     - `node['memcached']['listen']`: `0.0.0.0`
     - `node['memcached']['maxconn']`: `1024`
     - `node['memcached']['max_object_size']`: `1m`
     - `node['memcached']['experimental_options']`: `[]`
     - `node['memcached']['extra_cli_options']`: `[]`
     - `node['memcached']['ulimit']`: `1024`
     - `node['memcached']['logfilepath']`: `/var/log/memcached`
   - The target distribution must determine the Memcached configuration file and service unit.
   - The migration must install the verified Memcached package, configure the instance, start the service, enable it at boot, and restart it only when configuration changes.

3. **`redisio`** (`redisio` recipe path unavailable):
   - Intended to install and configure the Redis server represented by `node['redisio']['servers'][0]`.
   - Exact package name, configuration templates, ownership, service unit, and provider behavior cannot be determined from the supplied execution tree.

4. **`redisio::enable`** (`redisio::enable` recipe path unavailable):
   - Intended to enable and possibly start Redis.
   - The exact Redis service name and actions must be verified before implementation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package: exact package name is not specified in the supplied files; verify the real package name for the target distribution.
- Redis package: exact package name cannot be determined because the `redisio` recipe is unavailable.

**Service dependencies**:

- Memcached service: exact service name is not specified by the supplied custom resource implementation; verify it from the target package.
- Redis service: exact service name cannot be determined because `redisio` and `redisio::enable` are unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded Chef attribute assignment
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the server on port `6379`
- **Ansible storage**: Store the value in Ansible Vault, such as `redis_password`, and render it into the Redis configuration without committing plaintext credentials.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, or database connection strings were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- The distribution-specific Memcached configuration file
- The verified Memcached service unit
- The verified Redis service unit

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379`
- Redis PID directory: `/run/redis`
- Redis log directory: `/var/log/redis`

**Templates rendered**:

- None; no templates are rendered by the supplied execution tree.

## Pre-flight checks

```bash
# Verify the Memcached package and service name on the target distribution.
command -v memcached
systemctl list-unit-files | grep -E '^memcached'
systemctl is-enabled memcached
systemctl status memcached

# Confirm the Memcached TCP listener for the memcached instance.
ss -ltnp | grep ':11211'

# Confirm the Memcached UDP listener for the memcached instance.
ss -lunp | grep ':11211'

# Verify the memcached instance responds over TCP.
printf 'version\r\n' | nc -w 2 127.0.0.1 11211

# Verify Memcached settings for the memcached instance.
printf 'stats settings\r\n' | nc -w 2 127.0.0.1 11211 | \
  grep -E 'maxbytes|maxconns|tcpport|udpport'

# Verify the Redis package and service name after inspecting redisio.
command -v redis-server
systemctl list-unit-files | grep -E '^(redis|redis-server)'
systemctl is-enabled redis-service-name
systemctl status redis-service-name

# Confirm the redis-6379 instance is listening on TCP port 6379.
ss -ltnp | grep ':6379'

# Confirm the Redis PID directory.
ls -ld /run/redis

# Confirm the Redis log directory ownership and mode.
stat -c '%U:%G %a %n' /var/log/redis

# Confirm the Redis configuration exists.
test -f /etc/redis/6379.conf

# Confirm the redis-6379 instance responds with the vaulted password.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING

# Confirm unauthenticated access to the redis-6379 instance is rejected.
redis-cli -p 6379 PING

# Confirm the replica-related directives were removed from redis-6379.
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || true

# Confirm Redis authentication is configured without exposing the password.
grep -nE '^requirepass ' /etc/redis/6379.conf | sed 's/ .*/ <redacted>/'

# Verify both named cache instances are running.
ps -ef | grep -E '[r]edis|[m]emcached'

# Inspect Redis logs for the redis-6379 instance.
journalctl -u redis-service-name --no-pager -n 50

# Inspect Memcached logs for the memcached instance.
journalctl -u memcached --no-pager -n 50

# Check capacity for Redis runtime and log locations.
df -h /run/redis /var/log/redis
```

Expected results:

- The `memcached` service is enabled and active.
- Memcached TCP and UDP port `11211` are listening.
- The `memcached` instance responds with a version and reports the configured limits.
- The verified Redis service is enabled and active.
- Redis instance `redis-6379` is listening on port `6379`.
- `/run/redis` exists.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- Authenticated Redis access returns `PONG`.
- Unauthenticated Redis access is rejected.
- No unwanted replica-related directives remain in `/etc/redis/6379.conf`.
- The Redis password is not printed in command output or CI logs.