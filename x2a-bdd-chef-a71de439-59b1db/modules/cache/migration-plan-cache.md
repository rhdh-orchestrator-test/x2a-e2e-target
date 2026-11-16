---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached uses 64 MB of memory, TCP/UDP port `11211`, listener `0.0.0.0`, a maximum of 1,024 connections, and a 1 MB maximum object size. Redis uses `/run/redis` for its PID directory, `/var/log/redis` for logs, and password authentication. The Redis password is hardcoded in the Chef recipe and must be migrated to Ansible Vault or another protected secret store. The Redis package, service unit, and provider behavior require target-platform confirmation because the referenced `redisio` recipes were unavailable in the analyzed execution tree.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached caching service
  - Package: `memcached`
  - Package version: No explicit version pin; `node['memcached']['version']` defaults to `nil`
  - Memory: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: `node['memcached']['threads']`; not defined in the supplied default attributes and must be resolved before implementation
  - Experimental options: Empty list
  - Extra CLI options: Empty list
  - Ulimit: `1024`
  - Log directory: `/var/log/memcached`
  - Runtime directory: `/var/run/memcached`
  - Service account/group: `service_user` and `service_group`; exact resolved values are unavailable and must be obtained from the dependency implementation or target platform
  - Service state: Started and enabled

- **Redis instance `6379`**: Redis caching service
  - Port: `6379`
  - Authentication: Required
  - Password variable: `redis_password` in Ansible
  - PID directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Configuration file: `/etc/redis/6379.conf`
  - Configured collection item: Exactly one server definition with port `6379`
  - Removed configuration directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`
  - Package and service unit: Not available in the analyzed `redisio` source; determine for the supported target distribution before implementation

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
```

**Providers:**
```text
```

No provider file path was supplied in the execution tree. `memcached_instance[memcached]` is a custom resource, but its provider implementation is not available in the analyzed execution data.

**Templates:**
```text
```

No templates are rendered by the analyzed recipes.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file` resources.

The following listed files were not included because they are not executed or referenced by the supplied execution tree:

```text
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency using `include_recipe 'memcached'`.
   - Executes `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Sets the Redis server collection to exactly one item:
     ```yaml
     redisio_servers:
       - port: 6379
         requirepass: "{{ redis_password }}"
         replicaservestaledata: null
     ```
   - Sets the Redis PID directory to `/run/redis`.
   - Includes `redisio`; the referenced recipe was not found in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block['fix_redis_config']`, which removes complete lines matching the five Redis directives from `/etc/redis/6379.conf` when that file exists.
   - Includes `redisio::enable`; the referenced recipe was not found in the supplied execution tree.
   - The Ansible implementation must enable and start the selected Redis service after confirming the target distribution's package and service unit.
   - Resources identified in this recipe:
     - `directory` (1)
     - `ruby_block` (1)
     - `include_recipe 'memcached'` (1)
     - `include_recipe 'redisio'` (1)
     - `include_recipe 'redisio::enable'` (1)

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes exactly one custom resource: `memcached_instance['memcached']`.
   - Configures the instance named `memcached` with:
     - `memory`: `64`
     - `port`: `11211`
     - `udp_port`: `11211`
     - `listen`: `0.0.0.0`
     - `maxconn`: `1024`
     - `max_object_size`: `1m`
     - `threads`: unresolved because it is not defined in the supplied default attributes
     - `experimental_options`: empty list
     - `extra_cli_options`: empty list
     - `ulimit`: `1024`
     - `action`: `[:start, :enable]`
   - Passes the unresolved `service_user` value to the custom resource.
   - The custom resource provider is not present in the supplied execution tree. The provider-specific package, account, directory, and service behavior must be confirmed separately before implementation.

3. **Memcached dependency package setup** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - This file is present in the source structure, but its provider execution was not included in the analyzed execution tree.
   - The following dependency implementation details are therefore unverified and require separate source confirmation:
     - Installs package `memcached` with no explicit version pin.
     - Creates a system group represented by `service_group`.
     - Creates and locks a system user represented by `service_user`, with home `/nonexistent`, shell `/bin/false`, comment `Memcached`, and no managed home.
     - Creates `/var/log/memcached` with mode `0755`.
     - Creates `/var/run/memcached` with mode `0755`.
   - If confirmed, reproduce these settings in Ansible using resolved service account and group variables rather than assuming either is named `memcached`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- `memcached`
- Redis package: not visible in the analyzed files; select and verify the appropriate package for the supported target distribution

**Service dependencies**:

- Memcached instance `memcached` is intended to be started and enabled by `memcached_instance['memcached']`.
- Redis instance `6379` is intended to be enabled by `redisio::enable`, but the recipe and service unit were unavailable.
- Redis service account `redis` is required for the analyzed Redis log-directory resource.
- Memcached `service_user` and `service_group` must be resolved from the dependency implementation or target platform.

**Supported platforms declared by metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: Chef recipe
  - **URL**: Not applicable
  - **Path**: `cookbooks/cache/recipes/default.rb`
  - **Provider path**: No separate provider; the password is assigned directly in the recipe

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`; migrated variable: `redis_password`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the Chef recipe
- **Usage context**: Redis authentication for instance `6379`
- **Ansible storage**: Ansible Vault or an approved external secret provider
- **Required handling**: Do not reproduce the literal password in role defaults, plaintext inventory, normal variable files, shell commands, or command history. Reference the vaulted `redis_password` variable in the Redis configuration task.

The source literal is `redis_secure_password_123`; it must not be copied into the migrated role.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, or environment-variable secret reference was detected. No TLS certificate, private key, PEM, CRT, or database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached instance `memcached`, TCP: `0.0.0.0:11211`
- Memcached instance `memcached`, UDP: `0.0.0.0:11211`
- Redis instance `6379`, TCP: configured port `6379`
- Unix sockets: none configured or referenced in the analyzed files

**Templates rendered**:

- None; zero templates are rendered.

**Configuration transformations to verify**:

Confirm that `/etc/redis/6379.conf` contains no active lines matching:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

Run these checks after applying the Ansible role. Resolve `MEMCACHED_SERVICE_USER` and `MEMCACHED_SERVICE_GROUP` from the finalized role variables before running the Memcached checks. Use a protected value for `REDIS_PASSWORD_VERIFY`; do not place the password directly in shell history.

```bash
# Define these from the finalized Ansible role configuration.
export MEMCACHED_SERVICE_USER="<resolved-memcached-service-user>"
export MEMCACHED_SERVICE_GROUP="<resolved-memcached-service-group>"
# Provide REDIS_PASSWORD_VERIFY securely, without embedding it in this script.

# Identify the Memcached service unit
systemctl list-unit-files | grep -i '^memcached'

# Verify Memcached instance memcached is enabled and active
systemctl is-enabled memcached
systemctl is-active memcached
systemctl status memcached

# Confirm the Memcached process
ps -ef | grep '[m]emcached'

# Verify the Memcached package
rpm -q memcached 2>/dev/null || dpkg-query -W memcached

# Verify the resolved Memcached service account and group
getent passwd "$MEMCACHED_SERVICE_USER"
getent group "$MEMCACHED_SERVICE_GROUP"

# Verify Memcached directories
stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached

# Verify Memcached TCP endpoint for instance memcached
ss -ltnp | grep ':11211'
nc -vz 127.0.0.1 11211

# Verify Memcached UDP endpoint for instance memcached
ss -lunp | grep ':11211'

# Test the Memcached text protocol
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Validate expected runtime parameters where exposed by the process command line
ps -ef | grep '[m]emcached' | grep -E -- '--memory-limit|--conn-limit|--listen|--port|--threads'
```

Expected results for Memcached instance `memcached`:

- The `memcached` service is enabled and active.
- TCP port `11211` is listening on the configured listener.
- UDP port `11211` is listening on the configured listener.
- The version command returns a Memcached response.
- The process uses the configured memory, connection limit, listener, and object-size settings where supported by the target platform's service implementation.

```bash
# Identify the Redis service unit for instance 6379.
systemctl list-unit-files | grep -i redis
systemctl list-units --type=service --all | grep -i redis

# After identifying the target Redis unit, verify that instance 6379 is enabled and active.
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>
systemctl status <redis-service-unit>

# Verify the Redis configuration file for instance 6379.
test -f /etc/redis/6379.conf
ls -l /etc/redis/6379.conf

# Verify Redis runtime and log directories.
stat -c '%A %U:%G %n' /run/redis
stat -c '%A %U:%G %n' /var/log/redis

# Verify the Redis TCP endpoint for instance 6379.
ss -ltnp | grep ':6379'

# Test that Redis requires authentication.
redis-cli -p 6379 PING
# Expected result: an authentication error or NOAUTH response.

# Test authenticated Redis connectivity using a securely supplied verification variable.
REDISCLI_AUTH="$REDIS_PASSWORD_VERIFY" redis-cli -p 6379 PING
# Expected result: PONG.

# Test authenticated read/write operations.
REDISCLI_AUTH="$REDIS_PASSWORD_VERIFY" redis-cli -p 6379 SET migration_check chef_to_ansible
REDISCLI_AUTH="$REDIS_PASSWORD_VERIFY" redis-cli -p 6379 GET migration_check
REDISCLI_AUTH="$REDIS_PASSWORD_VERIFY" redis-cli -p 6379 DEL migration_check

# Verify that removed configuration directives are absent.
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected result: no matching active lines.

# Inspect Redis logs without using a wildcard path.
find /var/log/redis -maxdepth 1 -type f -print
journalctl --since "-15 minutes" | grep -i redis
```

Expected results for Redis instance `6379`:

- The target-platform Redis service is enabled and active.
- TCP port `6379` is listening.
- An unauthenticated `PING` is rejected.
- An authenticated `PING` returns `PONG`.
- Authenticated `SET`, `GET`, and `DEL` operations succeed.
- `/etc/redis/6379.conf` contains none of the five removed active directives.
- Redis uses `/run/redis` for its PID-related runtime path where supported by the selected Redis package and service implementation.