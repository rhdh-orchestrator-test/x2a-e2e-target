---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer with one Memcached instance named `memcached` and one Redis instance identified by port `6379`. Memcached is configured through the `memcached_instance[memcached]` custom resource with 64 MB of memory, TCP/UDP port `11211`, a `0.0.0.0` bind address, 1024 maximum connections, and a 1 MB maximum object size. Redis uses `/run/redis` for its PID directory, `/var/log/redis` for logs, `/etc/redis/6379.conf` for configuration, and a hardcoded authentication password that must be migrated to Ansible Vault or an approved secret store. The underlying Memcached provider and `redisio` recipes are unavailable, so package names, service unit names, generated configuration paths, and provider-specific behavior require target-platform confirmation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Resource: `memcached_instance[memcached]`
  - Memory: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: Not explicitly defined in the supplied default attributes
  - User: `service_user`
  - Ulimit: `1024`
  - Experimental options: Empty list
  - Extra CLI options: Empty list
  - Version: `nil`; no explicit version is selected by the cookbook defaults
  - Log path attribute: `/var/log/memcached`
  - Actions: Start and enable the service
  - Provider: Not included in the supplied execution tree or directory listing

- **redis-6379**: Redis cache service identified by port `6379`
  - Port: `6379`
  - Authentication password: `redis_secure_password_123` in the source cookbook; migrate to an approved secret store
  - PID directory: `/run/redis`
  - Configuration file: `/etc/redis/6379.conf`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Log directory creation: Recursive
  - Service action: Enabled through `redisio::enable`
  - Redis server collection: One configured item on port `6379`
  - `replicaservestaledata`: `nil`
  - Configuration cleanup:
    - Removes `replica-serve-stale-data`
    - Removes `replica-read-only`
    - Removes `repl-ping-replica-period`
    - Removes `client-output-buffer-limit`
    - Removes `replica-priority`

The Redis resource details and attributes above are reported by the source migration plan but require confirmation against the complete recipe and attributes analysis. The supplied validation summary independently confirms only the presence of `directory[/var/log/redis]` and `ruby_block[fix_redis_config]`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb

Providers:
No provider files supplied.

Templates:
No template files supplied.

Attributes:
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

Files:
No static files supplied.

Additional directory-listing files not included in the executed recipe flow:
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

The file inventory is based on the supplied directory listing. The validation summary did not include a complete analyzed file inventory.

## Module Explanation

The cookbook performs operations in the following order.

1. **Memcached dependency** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Includes the Memcached default recipe.
   - Declares the custom resource `memcached_instance[memcached]`.
   - Starts and enables the `memcached` instance.
   - Configures 64 MB of memory.
   - Configures TCP and UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets the maximum connection count to `1024`.
   - Sets the maximum object size to `1m`.
   - Uses the `service_user` account.
   - Applies ulimit `1024`.
   - Passes empty experimental-options and extra-CLI-options lists.
   - Leaves the thread count unspecified because no explicit value is present in the supplied default attributes.
   - The custom-resource provider, package name, configuration path, service name, and exact command-line rendering are unavailable and must be confirmed on the target platform.
   - Iterations: No `.each` loop is identified for Memcached.

2. **Cache wrapper recipe** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe before configuring Redis.
   - Assigns one Redis server definition to `node['redisio']['servers']`.
   - Configures the single Redis item, `redis-6379`, with port `6379`, password `redis_secure_password_123`, and `replicaservestaledata` set to `nil`.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` recipe.
   - Creates or manages `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - The Redis service account and group are expected to be provided by the Redis implementation; the supplied validation summary does not independently confirm a `group[redis]` resource.
   - Executes `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Includes `redisio::enable` after the configuration cleanup.
   - Iterations: The Redis server collection contains one expanded item: `redis-6379` on port `6379`. No additional `.each` loop is identified.

3. **Redis dependency** (`redisio`, recipe file unavailable):
   - Provides the underlying Redis package, configuration, account, directory, and service implementation.
   - The recipe file was not present in the supplied execution tree.
   - Package name, generated configuration layout, service unit name, and service resource behavior require target-platform confirmation.

4. **Redis service enablement** (`redisio::enable`, recipe file unavailable):
   - Enables the Redis service for the configured instance `redis-6379`.
   - The exact service unit name and start behavior require target-platform confirmation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, included as `memcached::default`
- `redisio`, included as `redisio`
- `redisio::enable`

Cookbook metadata and dependency versions were not supplied.

**System package dependencies**:

- Memcached package: not declared by the visible recipes; the package name is hidden in the unavailable `memcached_instance` provider.
- Redis package: not declared by the visible recipes; the package name is hidden in the unavailable `redisio` implementation.
- No package names can be verified from the supplied files. Resolve the real package names for the target distribution before migration.

**Service dependencies**:

- Memcached instance `memcached`, listening on TCP/UDP `11211`
- Redis instance `redis-6379`, listening on TCP `6379`
- Redis service account and group `redis`, required for Redis-owned directories

## Credentials

**Detection Summary**: 1 credential reported in 1 source file. The supplied validation summary did not include complete credential analysis, so this detection requires confirmation against the full source analysis.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Value in source**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute
- **Usage context**: Redis authentication for instance `redis-6379` on port `6379`
- **Migration storage**: Ansible Vault, AAP credential, or another approved secret-management integration

Do not place the literal password in plaintext Ansible variables, templates, task output, shell history, or debug messages.

No data bags, Chef Vault, Conjur, CyberArk, Vault URL, TLS key, certificate, API key, or environment-variable secret reference was identified in the supplied files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- Memcached configuration path: confirm from the missing `memcached_instance` provider
- Redis service unit path and name: confirm from the missing `redisio::enable` recipe
- Memcached service configuration: confirm on the target platform

**Service endpoints to check**:

- Instance `memcached`, TCP: `0.0.0.0:11211`
- Instance `memcached`, UDP: `0.0.0.0:11211`
- Instance `redis-6379`, TCP: `0.0.0.0:6379` or the target Redis bind address
- Unix sockets: None specified

**Templates rendered**:

- None; render count: `0`

**Configuration transformations**:

- `/etc/redis/6379.conf` is edited in place when present.
- Five replication-related directive types are removed.
- No template rendering or static-file deployment is specified.

## Pre-flight checks

```bash
# Confirm the target operating system and available package names
cat /etc/os-release
command -v dnf || command -v yum || command -v apt-get

# Confirm the Redis account and group
getent passwd redis
getent group redis

# Confirm the Memcached account
getent passwd service_user

# Confirm the required directories
ls -ld /run
ls -ld /var/log
```

### Instance `memcached`

```bash
# Identify the installed Memcached service unit
systemctl list-unit-files | grep -i memcached

# Check the target Memcached service after confirming its unit name
systemctl status memcached

# Verify process settings
ps auxww | grep '[m]emcached'

# Verify TCP port 11211
ss -tlnp | grep ':11211'

# Verify UDP port 11211
ss -ulnp | grep ':11211'

# Test the Memcached protocol
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Verify memory and connection settings when represented as command-line options
ps auxww | grep '[m]emcached' | grep -E -- '-m 64|-c 1024'

# Verify service enablement
systemctl is-enabled memcached
```

Expected results:

- The Memcached service is active and enabled.
- TCP port `11211` is listening.
- UDP port `11211` is bound.
- The protocol check returns a `VERSION` response.
- The process configuration reflects 64 MB and a 1024-connection limit where those settings are represented as command-line options.
- The actual service unit name must be substituted if the target distribution does not use `memcached`.

### Instance `redis-6379`

```bash
# Identify the Redis service unit
systemctl list-unit-files | grep -E 'redis|redis-server'

# Check the Redis service after confirming its unit name
systemctl status redis
systemctl status redis-server

# Verify Redis is listening on port 6379
ss -tlnp | grep ':6379'

# Verify the Redis process
ps aux | grep '[r]edis-server'

# Verify the runtime PID directory
ls -ld /run/redis

# Verify the log directory, ownership, and mode
ls -ld /var/log/redis
stat -c '%U %G %a %n' /var/log/redis

# Verify service enablement
systemctl is-enabled redis
systemctl is-enabled redis-server
```

Expected results:

- The Redis service for instance `redis-6379` is active.
- The Redis service is enabled.
- Port `6379` is listening.
- `/run/redis` exists.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `755`.
- The actual service unit name must be substituted if the target distribution does not use `redis` or `redis-server`.

### Redis authentication and database query

Retrieve the password from the approved secret source without exposing it in shell history or command output.

```bash
export REDISCLI_AUTH='<retrieve from Ansible Vault or AAP credential at execution time>'

redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
redis-cli -p 6379 DBSIZE

unset REDISCLI_AUTH
```

Expected results:

- `PING` returns `PONG`.
- `tcp_port` reports `6379`.
- Authentication succeeds without exposing the password.

### Redis configuration cleanup for `redis-6379`

```bash
test -f /etc/redis/6379.conf

grep -nE \
  '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

Expected results:

- `/etc/redis/6379.conf` exists.
- The second command produces no output because the five directive types were removed.
- If the file does not exist, the migration preserves the Chef behavior by skipping the cleanup rather than failing solely because the file is absent.

### Redis logs for `redis-6379`

Use the confirmed Redis service unit:

```bash
journalctl -u redis --since "15 minutes ago" --no-pager
journalctl -u redis-server --since "15 minutes ago" --no-pager

ls -lah /var/log/redis
```

Expected results:

- The Redis service starts successfully.
- No configuration or authentication errors are reported.
- Redis log storage is available under `/var/log/redis`.