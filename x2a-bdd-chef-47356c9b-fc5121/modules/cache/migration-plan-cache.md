---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` on TCP and UDP port `11211` and one Redis server on port `6379` with authentication enabled. It creates `/var/log/redis`, removes five replication-related directives from `/etc/redis/6379.conf`, and enables Redis. The supplied execution tree does not contain the `redisio` implementation or the external Memcached provider, so the Ansible migration must reproduce their behavior with target-platform packages, service units, and configuration management.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached caching service
  - Memory: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: `node['memcached']['threads']`; the default is not included in the supplied files
  - Experimental options: `[]`
  - Extra CLI options: `[]`
  - Ulimit: `1024`
  - Version: `nil`; no explicit version is selected
  - User: `service_user`, resolved by the external Memcached provider
  - Actions: `start`, `enable`

- **Redis server on port 6379**: Authenticated Redis cache service
  - Port: `6379`
  - Base PID directory: `/run/redis`
  - Password: `redis_secure_password_123`
  - Replication stale-data setting: `nil`
  - Configuration file: `/etc/redis/6379.conf`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Log directory creation: Recursive
  - Enablement: Redis enablement is invoked after configuration cleanup

No `.each` loops are present in the supplied execution tree. The Redis server definition contains one array item for port `6379`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

No provider file is listed in the supplied execution tree or directory listing. The `memcached_instance` provider is external to the supplied file set and must not be invented during migration.

**Templates:**

No template files are listed or rendered.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

No static files are deployed by the supplied execution flow.

The following files appear in the directory listing but are not executed by the supplied execution tree:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached::default` recipe.
   - Sets `node.default['redisio']['servers']` to one Redis server definition for port `6379`.
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Removes selected directives from `/etc/redis/6379.conf` when the file exists.
   - Includes `redisio::enable`.
   - The supplied execution tree does not contain the `redisio` or `redisio::enable` recipe implementations.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares the external `memcached_instance['memcached']` custom resource.
   - Uses the external Memcached provider; no provider file is present in the supplied tree.
   - Configures memory `64` MB, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, experimental options `[]`, extra CLI options `[]`, and ulimit `1024`.
   - Reads the thread count from `node['memcached']['threads']`; this default is not supplied.
   - Receives `service_user` for the service user; its value is provider-resolved.
   - Starts and enables the `memcached` instance.
   - Iterations: none.

3. **Redis installation and configuration via `redisio`** (implementation not present):
   - Must install and configure Redis for port `6379`.
   - Must use `/run/redis` as the base PID directory.
   - Must configure authentication using the migrated secret.
   - Must create or manage `/etc/redis/6379.conf`.
   - The exact package name, service unit name, and configuration template path must be selected for the target operating system.

4. **Redis log directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Sets owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Ansible equivalent: `ansible.builtin.file`.

5. **`fix_redis_config` ruby block** (`cookbooks/cache/recipes/default.rb`):
   - Runs only when `/etc/redis/6379.conf` exists.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the remaining configuration back to `/etc/redis/6379.conf`.
   - Ansible equivalent: controlled `ansible.builtin.replace` tasks or an equivalent idempotent configuration task.
   - The Chef resource does not explicitly notify a service restart.

6. **Redis enablement via `redisio::enable`** (implementation not present):
   - Must enable and start the Redis service serving port `6379`.
   - Must execute after Redis installation and configuration cleanup.
   - The exact systemd unit name must be determined on the target platform.

**Execution dependency chain:**

1. `cookbooks/cache/recipes/default.rb`
2. `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
3. `memcached_instance['memcached']`
4. Redis installation and configuration via `redisio`
5. Creation of `/var/log/redis`
6. Removal of selected directives from `/etc/redis/6379.conf`
7. Redis enablement via `redisio::enable`

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package: target-platform package name must be selected and verified; no explicit package resource or package name is supplied.
- Redis package: target-platform package name must be selected and verified; no explicit package resource or package name is supplied.

The cookbook supports:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Service dependencies**:

- Memcached service for instance `memcached`, started and enabled by `memcached_instance['memcached']`
- Redis service serving port `6379`, enabled by `redisio::enable`

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
- **Usage context**: Redis client authentication for the Redis server on port `6379`
- **Migration storage**: Ansible Vault, AAP credentials, or another approved secret-management system
- **Migration requirements**:
  - Do not commit the password to a playbook or plaintext variable file.
  - Render the secret into Redis configuration with controlled permissions.
  - Suppress the secret from task output and logs.
  - Test authentication using the vaulted value without printing it.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, database connection strings, API keys, or additional credential namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- The Memcached configuration file selected by the Ansible implementation
- The Redis service unit selected for the target platform
- The Memcached service unit selected for the target platform
- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`

**Service endpoints to check**:

- Memcached instance `memcached`, TCP: `0.0.0.0:11211`
- Memcached instance `memcached`, UDP: `0.0.0.0:11211`
- Redis server on port `6379`, TCP: `0.0.0.0:6379` or the bind address selected by the target Redis configuration

**Templates rendered**:

- Chef templates: none
- Ansible templates: implementation-dependent; no template render count is present in the supplied Chef execution flow

**Unix sockets**:

No Unix socket is configured or referenced.

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
```

Expected result: the Memcached service for instance `memcached` is enabled and active.

```bash
ss -tlnp | grep ':11211'
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
```

Expected results:

- TCP port `11211` is listening.
- The Memcached response contains a version string.

```bash
ss -ulnp | grep ':11211'
```

Expected result: UDP port `11211` is listening when UDP support is enabled by the selected Memcached package and configuration.

Verify the generated Memcached configuration contains:

- Memory limit `64` MB
- TCP port `11211`
- UDP port `11211`
- Listen address `0.0.0.0`
- Maximum connections `1024`
- Maximum object size `1m`
- Ulimit `1024`

Resolve and verify the missing `node['memcached']['threads']` value before migration implementation.

### Redis server on port `6379`

```bash
systemctl list-unit-files | grep -E 'redis|redis-server'
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>
```

Expected result: the Redis service serving port `6379` is enabled and active.

```bash
ss -tlnp | grep ':6379'
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
```

Expected result:

```text
PONG
```

Use the vaulted Redis password through `REDIS_PASSWORD`; do not place the literal password in shell history or command output.

```bash
redis-cli -p 6379 PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
```

Expected results:

- The unauthenticated request is rejected when authentication is enforced.
- The authenticated request returns `PONG`.

```bash
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result: no matching directive lines remain in `/etc/redis/6379.conf`.

```bash
grep -nE '^(port|requirepass)' /etc/redis/6379.conf
```

Expected results:

- Redis is configured for port `6379`.
- Authentication is configured using the vaulted password without exposing its value.

```bash
ls -ld /var/log/redis
ls -ld /run/redis
```

Expected results:

- `/var/log/redis` exists with mode `0755`.
- `/var/log/redis` is owned by `redis:redis`.
- `/run/redis` exists or is created by the Redis service implementation.

```bash
journalctl -u <redis-service-unit> -n 100 --no-pager
```

Check for startup failures, authentication configuration errors, permission errors, and inability to bind to port `6379`.

### Combined network verification

```bash
ss -tlnp | grep -E ':(11211|6379)\b'
ss -ulnp | grep ':11211'
```

Expected results:

- Memcached instance `memcached` is listening on TCP port `11211`.
- Memcached instance `memcached` is listening on UDP port `11211` when UDP is enabled.
- Redis server on port `6379` is listening on TCP port `6379`.