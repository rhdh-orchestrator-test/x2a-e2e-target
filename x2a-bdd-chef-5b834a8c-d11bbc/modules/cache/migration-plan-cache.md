---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` and one Redis server configured on port `6379`. Memcached uses 64 MB of memory, TCP and UDP port `11211`, a `0.0.0.0` listen address, and a maximum of 1024 connections. Redis uses port `6379`, a protected authentication password, `/run/redis` as its PID base directory, `/var/log/redis` as its log directory, and a cleanup step that removes five replication-related directives from `/etc/redis/6379.conf`. Redis setup and enablement are delegated to referenced `redisio` recipes whose source files were not supplied.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service managed by the `memcached_instance[memcached]` custom resource.
  - Package: `memcached`
  - Memory: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: `node['memcached']['threads']`; no explicit default is present in the analyzed attribute file
  - Experimental options: Empty list
  - Extra CLI options: Empty list
  - Ulimit: `1024`
  - Log directory: `/var/log/memcached`
  - Runtime directory: `/var/run/memcached`
  - Service account and group: Values supplied by the custom resource and package helper attributes
  - Actions: Start and enable the Memcached service

- **Redis server configured on port `6379`**: Single Redis cache instance.
  - Port: `6379`
  - Authentication: `requirepass redis_secure_password_123`
  - PID base directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Configuration file: `/etc/redis/6379.conf`
  - Cleanup directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`
  - Service enablement: Referenced through `redisio::enable`
  - Replication: No Redis replica instances are configured

The Redis and Memcached values above are source-level observations from the supplied recipe, dependency recipe, and attribute analysis. Redis setup and enablement behavior remains subject to verification because the referenced `redisio` recipe files were not supplied.

## File Structure

The following files and directories were listed in the supplied cookbook and dependency analysis. Relative dependency paths retain the required `migration-dependencies/` prefix.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
```

**Providers:**
```text
```

No provider file was supplied for `memcached_instance[memcached]`.

**Templates:**
```text
```

No rendered templates were identified.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` were identified.

SELinux recipe files referenced by the directory analysis are outside the supplied execution flow and are excluded from the migration file set. The source analysis reports seven total files, but only the four concrete paths above were supplied in the migration file listing; the remaining paths are not identifiable from the provided analysis.

## Module Explanation

The cookbook performs operations in the following execution order.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Configures one Redis server entry on port `6379`.
   - Sets the Redis password to `redis_secure_password_123`.
   - Sets `replicaservestaledata` to `nil`.
   - Sets the Redis PID base directory to `/run/redis`.
   - Includes the Redis setup recipe `redisio`.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` when the file exists.
   - Includes `redisio::enable` to enable Redis.
   - Redis setup and enablement recipe contents were not supplied and must be verified before migration.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates and manages the named custom resource `memcached_instance[memcached]`.
   - Starts and enables the Memcached service.
   - Passes the following values to the custom resource:
     - `memory`: `64`
     - `port`: `11211`
     - `udp_port`: `11211`
     - `listen`: `0.0.0.0`
     - `maxconn`: `1024`
     - `user`: `service_user`
     - `max_object_size`: `1m`
     - `threads`: `node['memcached']['threads']`
     - `experimental_options`: `[]`
     - `extra_cli_options`: `[]`
     - `ulimit`: `1024`
   - The custom resource provider path was not supplied; provider-specific configuration filenames must not be assumed.

3. **Memcached package setup** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - Installs the `memcached` package at `node['memcached']['version']`.
   - The default package version is `nil`, allowing the platform package manager to select its default version.
   - Creates the configured system group.
   - Creates and locks the configured system user with:
     - System user enabled
     - Home management disabled
     - Home directory `/nonexistent`
     - Shell `/bin/false`
     - Comment `Memcached`
   - Creates `/var/log/memcached` with mode `0755`.
   - Creates `/var/run/memcached` with mode `0755`.
   - Assigns both directories to the configured Memcached service user and group.

4. **Memcached attributes** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`):
   - `memcached.version`: `nil`
   - `memcached.memory`: `64`
   - `memcached.port`: `11211`
   - `memcached.udp_port`: `11211`
   - `memcached.listen`: `0.0.0.0`
   - `memcached.maxconn`: `1024`
   - `memcached.max_object_size`: `1m`
   - `memcached.experimental_options`: `[]`
   - `memcached.extra_cli_options`: `[]`
   - `memcached.ulimit`: `1024`
   - `memcached.logfilepath`: `/var/log/memcached`

5. **Redis configuration cleanup** (`cookbooks/cache/recipes/default.rb`):
   - Uses `ruby_block[fix_redis_config]`.
   - Checks whether `/etc/redis/6379.conf` exists.
   - If present, removes lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The Ansible equivalent should use idempotent `lineinfile` or controlled `replace` tasks.
   - A Redis restart or reload should occur only when the configuration changes.

No collection iterations or `.each` loops were identified. The plan contains one Memcached custom-resource instance named `memcached` and one Redis server entry on port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`
- `redisio`
- `redisio::enable`

The `redisio` and `redisio::enable` source recipe files were not supplied.

**System package dependencies**:

- `memcached`

The Redis package name is not shown in the supplied analysis and must be confirmed on the target platform.

**Service dependencies**:

- Memcached service, started and enabled by `memcached_instance[memcached]`
- Redis service, configured and enabled through the referenced `redisio` recipes
- The exact Redis service unit name must be confirmed on the target operating system

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Usage context**: Redis server authentication through the `requirepass` setting
- **Migration handling**: Replace the literal with an Ansible Vault variable such as `redis_password`.
- **Required protection**:
  - Store the value in an encrypted variables file.
  - Do not expose the password in task output.
  - Do not commit the literal password to the Ansible repository.
  - Do not print the password in validation commands or logs.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur variables, environment-variable secrets, TLS certificates, private keys, database connection strings, or additional hardcoded tokens were identified.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Unix sockets: none identified

**Templates rendered**:

- None identified

**Configuration modifications**:

- `/etc/redis/6379.conf`: five replication-related directive classes are removed.
- No Memcached template was identified.

## Pre-flight checks

### Memcached instance: `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
rpm -q memcached 2>/dev/null || dpkg-query -W -f='${Status} ${Version}\n' memcached
ps -ef | grep '[m]emcached'
```

Expected results:

- The `memcached` package is installed.
- The `memcached` service is enabled and active.
- The process runs under the configured service account.

Verify the effective configuration:

```bash
grep -R --line-number -E '(^|[[:space:]])(-m[[:space:]]+64|64)([[:space:]]|$)|(-p[[:space:]]+11211)|(-U[[:space:]]+11211)|(-l[[:space:]]+0\.0\.0\.0)|(-c[[:space:]]+1024)' \
  /etc/memcached.conf /etc/sysconfig/memcached /etc/default/memcached 2>/dev/null
```

Verify directories and ownership:

```bash
ls -ld /var/log/memcached
ls -ld /var/run/memcached
```

Expected results:

- `/var/log/memcached` exists with mode `0755`.
- `/var/run/memcached` exists with mode `0755`.
- Both directories are owned by the configured Memcached service user and group.

Verify TCP connectivity:

```bash
nc -vz 127.0.0.1 11211
printf "version\r\nquit\r\n" | nc 127.0.0.1 11211
```

Expected result:

- TCP port `11211` accepts connections.
- The response includes a Memcached version line.

Verify UDP and listening sockets:

```bash
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
```

Expected results:

- Memcached listens on TCP port `11211`.
- Memcached listens on UDP port `11211`.
- Listeners are bound according to the configured `0.0.0.0` address.

### Redis server configured on port `6379`

Identify the Redis service unit:

```bash
systemctl list-unit-files | grep -E '^redis|redis-server'
systemctl status redis redis-server 2>/dev/null
systemctl is-enabled redis redis-server 2>/dev/null
systemctl is-active redis redis-server 2>/dev/null
```

Verify configuration and cleanup:

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

Expected results:

- `/etc/redis/6379.conf` exists.
- The configured port is `6379`.
- Redis authentication is configured through the protected Ansible-managed secret.
- The following directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

Do not print the Redis password in command output or logs.

Verify Redis directories:

```bash
ls -ld /var/log/redis
ls -ld /run/redis
```

Expected results:

- `/var/log/redis` exists.
- `/var/log/redis` is owned by `redis:redis`.
- `/var/log/redis` has mode `0755`.
- `/run/redis` exists when the Redis service is active.

Verify Redis connectivity without exposing the password:

```bash
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server | grep -E 'redis_version|tcp_port'
```

Expected results:

- `PING` returns `PONG`.
- `tcp_port:6379` is reported.
- `REDIS_PASSWORD` is supplied securely through the shell environment and is not written directly in command history.

Verify the Redis socket:

```bash
ss -tlnp | grep ':6379'
```

Expected result:

- Redis listens on TCP port `6379`.

Verify Redis logs:

```bash
journalctl -u redis --no-pager -n 100 2>/dev/null
journalctl -u redis-server --no-pager -n 100 2>/dev/null
find /var/log/redis -maxdepth 1 -type f -print
```

Confirm that the active Redis unit reports no configuration or authentication errors.

Verify cleanup idempotence after two Ansible runs:

```bash
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

Expected result:

- No matching directives are present after either run.
- The second Ansible run reports no unnecessary configuration changes or service restarts.