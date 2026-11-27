---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the Memcached instance `memcached` on TCP and UDP port `11211`, and the Redis instance `6379` on TCP port `6379`. Memcached is managed through the external `memcached_instance` custom resource with 64 MB of memory, 1,024 maximum connections, and a 1 MB maximum object size. Redis uses `/etc/redis/6379.conf`, `/run/redis` for its PID directory, `/var/log/redis` for logs, and password authentication. The `redisio` and `redisio::enable` recipe files are missing from the supplied execution tree, so Redis installation, service-unit naming, startup, and enablement must be implemented explicitly or obtained from the missing dependency.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Platform-specific service configuration; `/var/log/memcached` is the configured default log path, but it is not explicitly passed to the custom resource
  - Port/Socket: TCP `11211`; UDP `11211`; listen address `0.0.0.0`
  - Key Config: 64 MB memory, 1,024 maximum connections, 1 MB maximum object size, file descriptor limit `1024`, empty experimental and extra CLI option lists, start and enable actions
  - Service user: Passed as `service_user`; concrete value is not defined in the supplied files
  - Version: `nil`; no explicit package version is selected

- **6379**: Redis server instance
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Password authentication enabled; log directory owned by `redis:redis` with mode `0755`; obsolete replication-related directives removed after configuration
  - Authentication: Hardcoded password `redis_secure_password_123` in the Chef recipe; migrate this value to Ansible Vault or an injected secret
  - Replica configuration: No Redis replica hostnames or additional Redis instances are configured

Redis configuration cleanup removes complete lines beginning with:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

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

No provider file is present in the supplied directory listing. The `memcached_instance` custom resource provider is external to the listed files.

**Templates:**

```text
```

No Chef templates are rendered by the reachable execution flow.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

**Data bags:**

No data bags are referenced by the reachable `cache` execution flow. The repository catalog contains `nginx_secrets/site` and three `nginx_sites` items, but they are unrelated to this cookbook and must not be migrated as `cache` inputs.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` cookbook.
   - Configures one Redis server entry named `6379` with port `6379`, password authentication, and `replicaservestaledata` set to `nil`.
   - Sets the Redis base PID directory to `/run/redis`.
   - Includes the unavailable `redisio` installation/configuration recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Runs the `fix_redis_config` Ruby block to remove five obsolete Redis directives from `/etc/redis/6379.conf` when the file exists.
   - Includes the unavailable `redisio::enable` recipe.
   - The `redisio` and `redisio::enable` recipe files are not present in the supplied execution tree. Redis package installation, service-unit naming, startup, and enablement are therefore implementation requirements rather than behavior verified from available recipe files.

   **Redis server collection:**
   - **`6379`**:
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`

   **Redis log directory:**
   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled

   **Redis configuration cleanup:**
   - Checks whether `/etc/redis/6379.conf` exists.
   - Removes complete lines beginning with `replica-serve-stale-data`.
   - Removes complete lines beginning with `replica-read-only`.
   - Removes complete lines beginning with `repl-ping-replica-period`.
   - Removes complete lines beginning with `client-output-buffer-limit`.
   - Removes complete lines beginning with `replica-priority`.
   - Does not fail solely because the configuration file is absent.
   - Should notify the Redis service only when the configuration changes.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates one `memcached_instance['memcached']` custom-resource instance.
   - Configures TCP port `11211`.
   - Configures UDP port `11211`.
   - Listens on `0.0.0.0`.
   - Allocates 64 MB of memory.
   - Allows 1,024 connections.
   - Sets maximum object size to `1m`.
   - Passes the external `service_user` value without a concrete value in the supplied files.
   - Passes the Memcached thread value from `node['memcached']['threads']`; no explicit default is defined in the supplied attribute file.
   - Sets the file descriptor limit to `1024`.
   - Uses empty experimental and extra CLI option lists.
   - Starts the service and enables it at boot.
   - The custom-resource provider is external and is not present in the supplied execution tree.

3. **Memcached attributes** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`):
   - Defines `memcached.version` as `nil`.
   - Defines `memcached.memory` as `64`.
   - Defines `memcached.port` as `11211`.
   - Defines `memcached.udp_port` as `11211`.
   - Defines `memcached.listen` as `0.0.0.0`.
   - Defines `memcached.maxconn` as `1024`.
   - Defines `memcached.max_object_size` as `1m`.
   - Defines `memcached.experimental_options` as an empty list.
   - Defines `memcached.extra_cli_options` as an empty list.
   - Defines `memcached.ulimit` as `1024`.
   - Defines `memcached.logfilepath` as `/var/log/memcached`.
   - The `logfilepath` attribute is not explicitly passed to `memcached_instance` in the supplied recipe and must not be treated as an explicit custom-resource property unless the external provider consumes it implicitly.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package: exact package name is not exposed by the supplied custom-resource provider.
- Redis package: exact package name is not exposed because the `redisio` recipe is missing.
- No package names can be verified from the supplied cookbook files. The Ansible implementation must select real platform-specific package names separately and document the selected packages.

**Service dependencies**:

- Memcached instance `memcached` must be started and enabled.
- Redis instance `6379` must be started and enabled.
- Redis must use `/etc/redis/6379.conf`.
- Redis must use `/run/redis` as its PID directory.
- Redis must have `/var/log/redis` available with owner `redis`, group `redis`, and mode `0755`.
- The `redis` user and group must exist before `/var/log/redis` is created and before Redis starts. The supplied analysis does not confirm an explicit Chef `group[redis]` resource.

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: Redis configuration for instance `6379`
- **Referenced data bags**: None

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef node attribute
- **Usage context**: Password authentication for Redis instance `6379`
- **Migration handling**:
  - Store the password in Ansible Vault or an AAP credential/injected secret.
  - Do not commit the plaintext value to role defaults, inventory, or group variables.
  - Render it into the Redis configuration with restrictive permissions.
  - Use `no_log: true` for secret-handling tasks.
  - Do not place the plaintext password in verification commands or shell history.

The repository data bag catalog contains `nginx_secrets/site`, `nginx_sites/ci.cluster.local`, `nginx_sites/status.cluster.local`, and `nginx_sites/test.cluster.local`. None are referenced by the reachable `cache` execution flow and none are migration inputs for this cookbook.

No TLS certificate, private key, database connection string, environment-variable secret, Chef Vault lookup, CyberArk lookup, Conjur variable, or cloud secret-manager reference was detected in the reachable cookbook flow.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`
- Memcached’s platform-specific service configuration file
- Memcached’s platform-specific log path, if created by the selected package

**Service endpoints to check**:

- Memcached instance `memcached`, TCP `0.0.0.0:11211`
- Memcached instance `memcached`, UDP `0.0.0.0:11211`
- Redis instance `6379`, TCP `0.0.0.0:6379` or the configured local bind address
- Redis instance `6379`, no Unix socket specified

**Templates rendered**:

- Chef templates rendered: `0`
- Ansible templates required: Redis configuration only if the implementation uses a template; no Chef template source is available

**Configuration mutations**:

The Redis cleanup task modifies `/etc/redis/6379.conf` by removing complete lines beginning with:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

The Redis service unit name cannot be verified because the `redisio` and `redisio::enable` recipes are missing. Replace `<redis-6379-service-unit>` with the unit created by the selected Redis package or Ansible role. Inject `REDIS_PASSWORD` securely rather than assigning the plaintext password in the shell.

```bash
# Verify the Memcached instance named memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
pgrep -a memcached
ps -o pid,user,cmd -C memcached

# Verify Memcached TCP endpoint for instance memcached
ss -tlnp | grep ':11211'
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Verify Memcached UDP endpoint for instance memcached
ss -ulnp | grep ':11211'

# Verify the Memcached file descriptor limit
systemctl show memcached | grep -E 'LimitNOFILE|User'

# Verify the Redis instance named 6379
systemctl status <redis-6379-service-unit>
systemctl is-enabled <redis-6379-service-unit>
systemctl is-active <redis-6379-service-unit>
pgrep -a redis

# Verify the Redis TCP endpoint for instance 6379
ss -tlnp | grep ':6379'

# Verify the Redis configuration and required directories
test -f /etc/redis/6379.conf
test -d /run/redis
test -d /var/log/redis
stat -c '%U:%G %a %n' /run/redis
stat -c '%U:%G %a %n' /var/log/redis

# Inspect non-secret Redis settings
grep -E '^(port|dir|pidfile|logfile)' /etc/redis/6379.conf

# Authenticate to Redis without exposing the password in this plan or shell history
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 PING
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 INFO server

# Confirm obsolete Redis directives are absent
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
    echo "Obsolete Redis directives remain"
    exit 1
fi

# Review service logs
journalctl -u memcached --no-pager -n 50
journalctl -u <redis-6379-service-unit> --no-pager -n 50

# Check resource and disk state
df -h /var/log/redis /run/redis
ps -o pid,user,%mem,%cpu,cmd -C memcached
pgrep -a redis
```

Expected results:

- The `memcached` instance is active and enabled.
- Memcached listens on TCP port `11211`.
- Memcached listens on UDP port `11211`.
- The Memcached text protocol returns a `VERSION` response.
- The Memcached process uses the intended service user.
- The Memcached open-file limit is consistent with `1024`.
- The Redis instance `6379` is active and enabled after the actual service unit is substituted.
- Redis listens on TCP port `6379`.
- Authenticated `redis-cli` access returns `PONG`.
- `/run/redis` exists.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- The five obsolete Redis directive patterns produce no output.
- Redis and Memcached logs show successful startup without configuration errors.

Migration is complete when the named `memcached` instance is active on TCP and UDP port `11211`, the named Redis instance `6379` accepts authenticated connections, Redis is enabled at boot, the required directories have the specified state, and all five obsolete Redis directives are absent from `/etc/redis/6379.conf`.