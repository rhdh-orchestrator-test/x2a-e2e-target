---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached is started and enabled through the `memcached_instance` custom resource with configured values of 64 MB memory, TCP and UDP port `11211`, bind address `0.0.0.0`, 1,024 maximum connections, 1 MB maximum object size, and ulimit `1024`; the `threads` value is not defined in the supplied attributes. Redis is configured with a hardcoded password, PID directory `/run/redis`, log directory `/var/log/redis`, and configuration cleanup for selected replication directives in `/etc/redis/6379.conf`. The `redisio` and `redisio::enable` implementations and the Memcached provider are unavailable from the supplied execution tree, so their package and exact service implementation details must be verified on the target system.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Package/provider-managed; exact configuration path is unavailable
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1,024 maximum connections, 1 MB maximum object size, ulimit `1024`, empty experimental and extra CLI options, started and enabled
  - Threads: Read from `node['memcached']['threads']`; no default is defined in the supplied attributes
  - Version: Unspecified
  - User: `service_user`; the value is not defined in the supplied files

- **redis-6379**: Redis server instance configured for port `6379`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`; no Unix socket configured or identified
  - Key Config: Password `redis_secure_password_123`, PID directory `/run/redis`, log directory `/var/log/redis`, and removal of selected replication-related directives
  - Log Directory: `/var/log/redis`, owned by `redis:redis`, mode `0755`
  - Enablement: Intended to be enabled through `redisio::enable`
  - Replication Setting: `replicaservestaledata` is `nil`

## File Structure

```text
cookbooks/cache/recipes/default.rb
cookbooks/cache/metadata.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Providers:**

```text
```

No provider file for `memcached_instance` is included in the supplied execution tree.

**Templates:**

```text
```

No templates are rendered by the analyzed recipes.

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The supplied execution summary states that seven files were analyzed, but the remaining files are not identified in the available plan data.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` dependency, which resolves to the supplied Memcached recipe.
   - Sets `node['redisio']['servers']` to one Redis entry:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` dependency recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block[fix_redis_config]` to modify `/etc/redis/6379.conf` when the file exists.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Does not explicitly notify Redis to restart or reload after changing the configuration.
   - Includes the unavailable `redisio::enable` recipe to enable Redis at boot.
   - Iterations: No `.each` loops are present. The Redis server collection contains one explicitly configured item, port `6379`.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates `memcached_instance['memcached']`.
   - Configures memory `64` MB.
   - Configures TCP port `11211` and UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Sets maximum object size to `1m`.
   - Reads the undefined `node['memcached']['threads']` attribute.
   - Passes empty experimental and extra CLI option lists.
   - Sets ulimit to `1024`.
   - Executes actions `start` and `enable`.
   - Uses `service_user` as the user value.
   - Iterations: No `.each` loops are present. The only custom resource instance is `memcached`.

3. **`redisio` dependency recipe** (implementation unavailable):
   - The recipe is referenced by `cache::default`.
   - Its package, configuration, provider, service name, and template behavior are unavailable from the supplied execution tree.
   - Do not invent package names or service names until the dependency implementation or target distribution mapping is verified.

4. **`redisio::enable` dependency recipe** (implementation unavailable):
   - The recipe is referenced by `cache::default`.
   - Its intended behavior is to enable Redis at boot.
   - The exact Redis service name and implementation are unavailable.

## Dependencies

**External cookbook dependencies**:

- `memcached`, constraint `~> 6.0`
- `redisio`, no version constraint

These dependency declarations are referenced by the plan but should be confirmed against the complete `cookbooks/cache/metadata.rb` analysis.

**System package dependencies**:

- Memcached and Redis are expected to be installed or configured by the external `memcached` and `redisio` cookbooks.
- Exact system package names and versions are not available in the supplied execution tree.
- Verify package mappings for the target operating system before implementation.

**Service dependencies**:

- Memcached is started and enabled by `memcached_instance['memcached']`.
- Redis is intended to be enabled by `redisio::enable`.
- The exact Redis systemd service name is unavailable.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

These platform declarations should be confirmed against the complete metadata analysis.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext string in the Chef recipe
- **Value currently configured**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the server listening on port `6379`
- **Migration handling**: Store the value in Ansible Vault or an AAP-managed credential. Do not commit it in plaintext to `group_vars`, role defaults, or templates.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, database connection strings, or additional hardcoded tokens were identified in the supplied plan data.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `cookbooks/cache/metadata.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- The target Memcached configuration path, to be discovered from the installed dependency/provider

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `127.0.0.1:6379` or the verified configured bind address
- Redis Unix socket: None configured or identified

**Templates rendered**:

- None

**Configuration transformations**:

Remove lines beginning with the following directives from `/etc/redis/6379.conf`:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Confirm the target operating system and available service units.
cat /etc/os-release
systemctl list-unit-files | grep -E '^(memcached|redis|redis-server)'

# Memcached instance: memcached
systemctl is-enabled memcached
systemctl is-active memcached
systemctl status memcached --no-pager

# Verify Memcached TCP and UDP listeners.
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'

# Verify the Memcached process and effective arguments.
ps -ef | grep '[m]emcached'

# Query Memcached over TCP.
printf "stats\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Verify the effective Memcached configuration or process arguments:
# memory = 64 MB
# TCP port = 11211
# UDP port = 11211
# listen address = 0.0.0.0
# maximum connections = 1024
# maximum object size = 1m
# ulimit = 1024
#
# Discover the package-managed configuration path before using a
# path-specific assertion. The threads value must be checked against
# the target dependency default because no supplied default is defined.

# Redis instance: redis-6379
# Replace the commands below with the verified service name if it is
# neither redis-server nor redis.
systemctl is-enabled redis-server 2>/dev/null || systemctl is-enabled redis 2>/dev/null
systemctl is-active redis-server 2>/dev/null || systemctl is-active redis 2>/dev/null
systemctl status redis-server --no-pager 2>/dev/null || systemctl status redis --no-pager 2>/dev/null

# Verify the Redis listener.
ss -tlnp | grep ':6379'

# Verify the Redis PID directory.
test -d /run/redis
ls -ld /run/redis

# Verify the Redis log directory.
test -d /var/log/redis
stat -c '%U %G %a %n' /var/log/redis

# Expected log directory result:
# redis redis 755 /var/log/redis

# Verify the Redis configuration file.
test -f /etc/redis/6379.conf

# Confirm the password directive without printing its value.
grep -E '^requirepass ' /etc/redis/6379.conf | sed 's/ .*$/ <redacted>/'

# Confirm the unwanted directives were removed.
! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Test Redis authentication using a protected Ansible Vault value.
redis-cli -h 127.0.0.1 -p 6379 \
  -a 'REPLACE_WITH_ANSIBLE_VAULT_VALUE' PING

# Expected result:
# PONG

# Test a Redis write and read operation.
redis-cli -h 127.0.0.1 -p 6379 \
  -a 'REPLACE_WITH_ANSIBLE_VAULT_VALUE' SET migration_check ok

redis-cli -h 127.0.0.1 -p 6379 \
  -a 'REPLACE_WITH_ANSIBLE_VAULT_VALUE' GET migration_check

# Expected result:
# ok

# Remove the validation key.
redis-cli -h 127.0.0.1 -p 6379 \
  -a 'REPLACE_WITH_ANSIBLE_VAULT_VALUE' DEL migration_check

# Review service logs using the verified Redis service name.
journalctl -u redis-server --no-pager -n 100 2>/dev/null || \
journalctl -u redis --no-pager -n 100 2>/dev/null

# Verify both cache processes.
ps -ef | grep '[r]edis'
ps -ef | grep '[m]emcached'

# Review Redis log files.
find /var/log/redis -maxdepth 1 -type f -ls
```

The Ansible task that modifies `/etc/redis/6379.conf` should notify the verified Redis restart or reload handler when the file changes.