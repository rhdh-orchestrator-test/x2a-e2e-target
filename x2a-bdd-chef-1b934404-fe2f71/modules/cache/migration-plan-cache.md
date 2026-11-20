---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache tier with one Memcached instance named `memcached` and one Redis server on port `6379`. Memcached uses 64 MB of memory, TCP and UDP port `11211`, a wildcard listen address, 1024 maximum connections, a `1m` maximum object size, and ulimit `1024`; it is started and enabled. Redis uses port `6379`, a configured authentication password, PID directory `/run/redis`, and log directory `/var/log/redis`. The Redis installation and enable recipes are referenced but absent from the supplied execution tree, so their package names and exact service-unit behavior must be confirmed during implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Resource: `memcached_instance[memcached]`
  - Location/Path: Platform/provider-dependent configuration path; default log path is `/var/log/memcached`
  - Port/Socket: TCP `11211`; UDP `11211`; listen address `0.0.0.0`
  - Key Config: 64 MB memory, 1024 maximum connections, maximum object size `1m`, ulimit `1024`, configured thread value from `node['memcached']['threads']`, empty experimental and extra CLI option lists, no explicit version, actions `start` and `enable`
  - User: `service_user`, resolved by the Memcached cookbook/provider

- **redis-6379**: Redis cache server
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; bind address is not explicitly configured in the supplied execution tree
  - Key Config: Authentication password is assigned through `node['redisio']['servers'][0]['requirepass']`; `replicaservestaledata` is `nil`; selected replication and client-buffer directives are removed from the configuration
  - Service: Exact Redis service-unit name is not available because the Redis provider and enable recipe are missing

## File Structure

Only files shown in the supplied execution tree and directory listing are included below. The Redis recipe files referenced by `include_recipe 'redisio'` and `include_recipe 'redisio::enable'` were reported as not found and are therefore not listed.

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

No provider files were supplied in the execution tree. The `memcached_instance[memcached]` provider path is not included in the supplied analysis.

**Templates:**

No template files are rendered by the supplied execution flow.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

No static files are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency using `include_recipe 'memcached'`.
   - Executes `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Assigns one Redis server configuration to `node['redisio']['servers']`.
   - Configures the Redis server item named by its port, **6379**, with:
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the Redis installation/configuration dependency using `include_recipe 'redisio'`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Includes `redisio::enable` to enable the configured Redis service.
   - The `redisio` and `redisio::enable` recipe files are missing from the supplied execution tree; package names, templates, resources, and service-unit names must be confirmed during implementation.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates one `memcached_instance[memcached]` custom resource.
   - Configures memory to `64` MB.
   - Configures TCP port `11211` and UDP port `11211`.
   - Listens on `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Sets maximum object size to `1m`.
   - Applies `node['memcached']['threads']`; this value is not defined in the supplied attributes file and requires confirmation.
   - Sets user to `service_user`.
   - Sets ulimit to `1024`.
   - Uses empty `experimental_options` and `extra_cli_options` lists.
   - Requests no explicit Memcached version because `memcached.version` is `nil`.
   - Starts and enables the Memcached service.
   - The custom resource has one iteration with the actual instance name **memcached**.

3. **Redis configuration cleanup** (`cookbooks/cache/recipes/default.rb`):
   - Ensures `/etc/redis/6379.conf` is modified only if the file exists.
   - Removes the five specified directives while preserving all other configuration.
   - Restarts the Redis 6379 service when the configuration changes.
   - The handler and service-unit name must be confirmed on the target operating system.

## Dependencies

**External cookbook dependencies**:

- `memcached`
- `redisio`
- `redisio::enable`

The Redis recipe files are missing from the supplied execution tree.

**System package dependencies**:

- Memcached package: exact platform-specific package name is not present in the supplied execution tree and must be verified for the target distribution.
- Redis package: exact platform-specific package name is not present in the supplied execution tree and must be verified for the target distribution.

**Service dependencies**:

- Memcached service; exact unit name must be confirmed.
- Redis service for port `6379`; exact unit name must be confirmed.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded Chef attribute assignment
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value in the recipe
- **Usage context**: Redis authentication for the server listening on port `6379`

The migrated implementation must not retain this password in a committed defaults or task file. Store it in Ansible Vault, an AAP credential, or another approved secret-management integration. Use the protected variable when configuring Redis authentication.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, secret-manager URLs, environment-variable secrets, TLS certificate references, private keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`
- `/run/redis`
- Platform/provider-dependent Memcached configuration file
- Platform/provider-dependent Redis log file

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` unless the missing Redis recipe applies a different bind address

**Unix sockets**:

- None configured or referenced.

**Templates rendered**:

- None; zero templates are rendered by the supplied execution flow.

## Pre-flight checks

### Memcached instance `memcached`

```bash
# Confirm the Memcached service is enabled and running.
systemctl status memcached
systemctl is-enabled memcached

# Confirm the Memcached process is present.
pgrep -a memcached

# Confirm TCP port 11211 is listening.
ss -ltnp | grep ':11211'

# Confirm UDP port 11211 is listening.
ss -lunp | grep ':11211'

# Verify Memcached responds over TCP.
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Inspect Memcached statistics.
printf "stats\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Inspect the platform-specific effective configuration.
grep -E '(^|-m |-p |-U |-l |-c |-I |-t )' \
  /etc/sysconfig/memcached /etc/memcached.conf 2>/dev/null

# Review the Memcached service journal.
journalctl -u memcached --no-pager -n 100
```

Expected results:

- The Memcached unit is enabled and running.
- A Memcached process is present.
- TCP and UDP port `11211` are listening.
- Memcached responds to `version` and `stats`.
- The effective configuration reflects 64 MB memory, TCP and UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, the configured thread value, and ulimit `1024`.

### Redis instance `redis-6379`

```bash
# Identify the Redis service unit created for port 6379.
systemctl list-units --type=service --all | grep -Ei 'redis|6379'

# Replace the placeholder after confirming the actual unit name.
systemctl status <redis-6379-service-unit>
systemctl is-enabled <redis-6379-service-unit>

# Confirm the Redis process is present.
pgrep -a redis

# Confirm TCP port 6379 is listening.
ss -ltnp | grep ':6379'

# Verify Redis authentication using an approved secret-store value.
export REDISCLI_AUTH='<retrieve-from-approved-secret-store>'
redis-cli -p 6379 PING

# Verify Redis server information.
redis-cli -p 6379 INFO server

# Confirm unauthenticated access fails.
env -u REDISCLI_AUTH redis-cli -p 6379 PING

# Confirm the configured PID directory exists.
ls -ld /run/redis

# Confirm the Redis log directory ownership and mode.
ls -ld /var/log/redis
stat -c '%U %G %a %n' /var/log/redis

# Inspect the Redis 6379 configuration.
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Review the Redis service journal.
journalctl -u <redis-6379-service-unit> --no-pager -n 100

# Review files in the Redis log directory.
find /var/log/redis -maxdepth 1 -type f -ls
```

Expected results:

- The Redis service for port `6379` is enabled and running.
- TCP port `6379` is listening.
- Authenticated `redis-cli -p 6379 PING` returns `PONG`.
- Unauthenticated `PING` fails.
- `/run/redis` exists.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- The five directives removed by `fix_redis_config` are absent from `/etc/redis/6379.conf`.

### Redis configuration cleanup

```bash
# Each command should return no matching lines after migration.
grep -E '^replica-serve-stale-data' /etc/redis/6379.conf
grep -E '^replica-read-only' /etc/redis/6379.conf
grep -E '^repl-ping-replica-period' /etc/redis/6379.conf
grep -E '^client-output-buffer-limit' /etc/redis/6379.conf
grep -E '^replica-priority' /etc/redis/6379.conf
```