---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache services: a Memcached instance named `memcached` on TCP and UDP port `11211`, and a Redis server on port `6379` with a hardcoded authentication password. Memcached is configured through the external `memcached` cookbook and its `memcached_instance` custom resource. Redis configuration is delegated to the external `redisio` cookbook, followed by creation of `/var/log/redis`, cleanup of selected directives in `/etc/redis/6379.conf`, and inclusion of `redisio::enable`. The supplied execution tree does not include the `redisio` recipes or the Memcached custom-resource provider, so those dependency implementations must be verified separately before completing the Ansible role.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Memory: `64` MB
  - Listen address: `0.0.0.0`
  - TCP port: `11211`
  - UDP port: `11211`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: `node['memcached']['threads']`; not defined in the supplied attributes analysis
  - Experimental options: `node['memcached']['experimental_options']`; default empty array
  - Extra CLI options: `node['memcached']['extra_cli_options']`; default empty array
  - Ulimit: `1024`
  - Version: `nil`; no explicit version selected
  - Log path setting: `/var/log/memcached`
  - User: Passed as `service_user`; its definition is not included in the supplied execution tree
  - Actions: start and enable

- **Redis server on port 6379**: Redis cache and data-store service
  - Port: `6379`
  - Authentication password: `redis_secure_password_123`
  - PID directory: `/run/redis`
  - Configuration file: `/etc/redis/6379.conf`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Log directory creation: Recursive
  - `replicaservestaledata`: `nil`
  - Enablement: Delegated to the unavailable `redisio::enable` recipe
  - Removed configuration directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

The Memcached and Redis values above are based on the supplied recipe and dependency analysis. Verify dependency-level defaults and resource properties against the original source files before implementation where the supplied analysis does not expose them.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb

Providers:
No provider files are listed in the supplied execution tree or directory listing. The memcached_instance[memcached] custom resource is used, but its provider implementation is unavailable.

Templates:
No template files are listed or rendered by the supplied execution tree.

Attributes:
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

Files:
No static files are listed or deployed by the supplied execution tree.

Files present in the directory listing but not in the execution tree:
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

The execution tree references `redisio`, `redisio::enable`, and their associated implementations, but those recipe files are reported as unavailable. Their exact package names, service names, templates, providers, and resource properties require separate verification.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Sets the Redis server collection to one entry on port `6379` with `requirepass` set to `redis_secure_password_123` and `replicaservestaledata` set to `nil`.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the external `redisio` recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Declares `ruby_block[fix_redis_config]` to remove selected replication-related directives from `/etc/redis/6379.conf`.
   - Includes `redisio::enable`.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares the `memcached_instance[memcached]` custom resource.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental options, and empty extra CLI options.
   - Passes `node['memcached']['threads']` through unchanged because it is not defined in the supplied attributes analysis.
   - Passes `service_user` to the custom resource; the source of this value is unavailable in the supplied execution tree.
   - Applies actions `start` and `enable`.
   - The provider implementation is unavailable. The Ansible role must reproduce the observable result: install and configure Memcached, bind TCP and UDP port `11211`, apply the configured limits, start the service, and enable it at boot.

3. **Redis configuration from `cookbooks/cache/recipes/default.rb`**:
   - Uses Redis port `6379`.
   - Uses `/run/redis` as the PID directory.
   - Ensures `/etc/redis/6379.conf` is available before cleanup when the Redis dependency creates it.
   - Removes complete lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, or `replica-priority`.
   - Does not fail solely because `/etc/redis/6379.conf` is absent when the dependency has not created it.
   - Enables and starts Redis through the intended `redisio::enable` behavior without assuming an exact systemd unit name until the missing dependency is inspected.

The Redis configuration collection contains one configured item, named by its actual port:

- **Redis server `6379`**: password `redis_secure_password_123`; `replicaservestaledata` set to `nil`.

No `.each` loops are present in the supplied recipes.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package name: delegated to the external `memcached` cookbook and requires verification.
- Redis package name: delegated to the external `redisio` cookbook and requires verification.
- No package resources are directly declared in the supplied cookbook recipes.

**Service dependencies**:

- Memcached service behavior is supplied by `memcached_instance[memcached]`.
- Redis service behavior is supplied by `redisio` and `redisio::enable`; their recipe files are unavailable in the supplied execution tree.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute
- **Usage context**: Redis authentication on port `6379`
- **Migration handling**: Store the value in Ansible Vault rather than plaintext defaults, variable files, or committed rendered configuration. Use `no_log: true` for tasks that process the password.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, database credentials, API keys, or token attributes were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379`
- Unix sockets: None configured

**Configuration values to verify**:

- Memcached memory: `64` MB
- Memcached maximum connections: `1024`
- Memcached maximum object size: `1m`
- Memcached listen address: `0.0.0.0`
- Memcached TCP port: `11211`
- Memcached UDP port: `11211`
- Redis port: `6379`
- Redis PID directory: `/run/redis`
- Redis password configured from protected Ansible storage
- Selected Redis directives absent from `/etc/redis/6379.conf`

**Templates rendered**:

- None. No templates are listed or rendered by the supplied execution tree.

## Pre-flight checks:

```bash
# Identify the installed Redis service unit because redisio::enable is unavailable.
systemctl list-unit-files | grep -i redis
systemctl list-units --type=service | grep -i redis
```

### Memcached instance: `memcached`

```bash
# Confirm the Memcached process is running.
pgrep -a memcached

# Confirm the Memcached TCP listener.
ss -ltnp | grep ':11211'

# Confirm the Memcached UDP listener.
ss -lunp | grep ':11211'

# Query Memcached statistics over TCP.
printf "stats\r\nquit\r\n" | nc 127.0.0.1 11211

# Confirm the configured memory and connection limits.
printf "stats settings\r\nquit\r\n" | nc 127.0.0.1 11211 | \
  grep -E 'limit_maxbytes|maxconns'

# Confirm the service is enabled and running.
systemctl is-enabled memcached
systemctl status memcached --no-pager
journalctl -u memcached --no-pager -n 50
```

Expected results:

- A Memcached process is present.
- TCP and UDP port `11211` are listening.
- Memcached returns runtime statistics.
- `limit_maxbytes` corresponds to `64` MB.
- The configured maximum connection limit is present.
- The service is enabled and running.

### Redis instance: `6379`

Set the password through a protected mechanism before running the checks:

```bash
export REDISCLI_AUTH='<protected-redis-password>'
```

Do not store the literal password in shell history or expose it through process arguments.

```bash
# Confirm a Redis process is running.
pgrep -a redis

# Confirm Redis is listening on TCP port 6379.
ss -ltnp | grep ':6379'

# Authenticate and verify Redis responds.
redis-cli -h 127.0.0.1 -p 6379 PING

# Query Redis server information.
redis-cli -h 127.0.0.1 -p 6379 INFO server

# Verify Redis can write and read a temporary key.
redis-cli -h 127.0.0.1 -p 6379 SET migration_check success
redis-cli -h 127.0.0.1 -p 6379 GET migration_check
redis-cli -h 127.0.0.1 -p 6379 DEL migration_check

# Confirm the configured Redis port.
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET port

# Verify the PID directory exists.
ls -ld /run/redis

# Verify the Redis log directory and permissions.
ls -ld /var/log/redis

# Replace <redis-unit-name> with the unit discovered above.
systemctl is-enabled <redis-unit-name>
systemctl status <redis-unit-name> --no-pager
journalctl -u <redis-unit-name> --no-pager -n 50
```

Expected results:

- Redis responds with `PONG`.
- `INFO server` returns Redis server information.
- The temporary key returns `success`.
- Redis reports port `6379`.
- `/run/redis` exists.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- The discovered Redis service is enabled and running.

### Redis configuration cleanup

```bash
# Confirm the Redis configuration file exists.
test -f /etc/redis/6379.conf

# Confirm the removed directives are absent.
grep -nE \
  '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

Expected result: the second command produces no matching lines.

### Log locations

```bash
ls -lah /var/log/redis
ls -lah /var/log/memcached
```

The Redis password must not appear in Ansible task output, command arguments, shell history, or service logs.