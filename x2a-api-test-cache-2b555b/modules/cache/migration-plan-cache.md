---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache instances in sequence: Memcached instance `memcached` through the `memcached_instance[memcached]` custom resource, followed by Redis instance `6379` through the `redisio` dependency. The visible recipe assigns Memcached settings of 64 MB memory, TCP/UDP port `11211`, bind address `0.0.0.0`, and 1,024 maximum connections, and assigns Redis port `6379`, password authentication, PID directory `/run/redis`, and Redis log directory `/var/log/redis`. The supplied execution tree does not expose the Memcached provider, Redis dependency recipes, or the implementation details of the Redis configuration cleanup, so those values and side effects require confirmation during implementation. The reported Redis password must be migrated to Ansible Vault or another approved secret store.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached distributed in-memory cache
  - Location/Path: `/var/log/memcached`, `/var/run/memcached`; configuration path is platform-dependent and requires confirmation
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, maximum 1,024 connections, maximum object size `1m`, `ulimit` `1024`, empty experimental and extra CLI options, and configured start/enable actions. The exact service user, service group, and thread count are not present in the supplied structured analysis and require confirmation from the dependency implementation.

- **6379**: Redis cache and in-memory data store
  - Location/Path: `/etc/redis/6379.conf`, PID directory `/run/redis`, log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Password authentication, Redis service account expected to own the log directory, log directory mode `0755`, and one configured Redis instance. The recipe assignment, password, PID directory, log ownership, and `replicaservestaledata` value are reported by the migration analysis but are not independently visible in the supplied structured execution summary and require confirmation.

## File Structure

Only files represented by the supplied execution flow or directly used by that flow are listed below. Dependency recipe files retain their exact paths from the supplied directory listing.

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

```text
```

No provider file path was supplied for `memcached_instance[memcached]`. The custom resource is present in the execution tree, but its provider implementation is not listed in the provided file inventory. Do not invent a provider path; inspect the dependency artifact separately if implementation-level provider behavior is required.

**Templates:**

```text
```

No rendered templates are present in the supplied execution tree.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files deployed by `cookbook_file` or `remote_file` are present in the supplied execution tree.

The following listed files are not included because the execution tree does not execute them:

- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb`

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - The executed dependency recipe is `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Invokes `memcached_instance[memcached]`.
   - The reported resource settings are memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, `ulimit` `1024`, empty experimental options, empty extra CLI options, and actions `start` and `enable`.
   - The exact resolved service user, service group, and thread count are not available in the supplied structured analysis.
   - Sets the reported Redis server configuration for instance `6379`, including port `6379`, password authentication, PID directory `/run/redis`, and `replicaservestaledata` unset. These assignments require confirmation from the recipe source because they are not shown in the supplied structured execution summary.
   - Includes `redisio`; the Redis recipe implementation is unavailable.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`; the Redis account and group must exist before this operation.
   - Executes `ruby_block[fix_redis_config]`. The migration analysis reports that, when `/etc/redis/6379.conf` exists, the block removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The Ruby block implementation and its exact transformations are not present in the supplied structured analysis and must be confirmed before implementation.
   - Includes `redisio::enable`; the recipe implementation is unavailable.
   - Ansible must implement the observable behavior idempotently:
     - Install the verified Memcached package.
     - Configure and enable/start Memcached instance `memcached`.
     - Resolve the target platform’s Memcached configuration path and service unit.
     - Install and configure the verified Redis package and service for instance `6379`.
     - Create `/run/redis` and `/var/log/redis` with confirmed ownership and permissions.
     - Store the Redis password in Ansible Vault.
     - Manage `/etc/redis/6379.conf`.
     - Remove the five reported Redis directives only after confirming the Ruby block behavior.
     - Enable and start Redis instance `6379`.

## Dependencies

**External cookbook dependencies**: `memcached`, `redisio`, and `redisio::enable`. No metadata file was found under `cookbooks/cache`, so additional metadata dependencies cannot be confirmed.

**System package dependencies**: `memcached` is the only explicitly identified package. The Redis package name is not available because the `redisio` recipe was not supplied and must be verified for the target distribution.

**Service dependencies**: Memcached service for instance `memcached`; Redis service for instance `6379`.

## Credentials

**Detection Summary**: 1 reported credential in 1 file; the supplied structured validation summary does not independently verify the assignment.

**Source**:
  - **Provider**: Hardcoded in Chef source, according to the migration analysis
  - **URL**: Not detected
  - **Path**: Not detected
  - **Migration target**: Ansible Vault or an approved external secret-management integration

### Redis Password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Reported value in Chef source**: `redis_secure_password_123`; confirm against the source before migration
- **Current storage**: Reported as a hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis password authentication for instance `6379`
- **Ansible handling**:
  - Store the password in an encrypted Ansible Vault variable.
  - Do not place the plaintext value in `defaults/main.yml`, normal vars files, task arguments, or committed templates.
  - Render the Redis configuration with the vaulted value.
  - Restrict permissions on generated Redis configuration files containing the password.
  - Do not expose the password through task output or debug statements.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, API tokens, or database connection strings were detected in the supplied source.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `6379`: TCP port `6379`
- Redis Unix socket: none specified

**Templates rendered**: None. No Chef templates are present in the supplied execution tree.

**Configuration transformations**: The reported Redis cleanup removes complete lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` from `/etc/redis/6379.conf` when the file exists. Confirm the Ruby block implementation before treating this transformation as authoritative.

## Pre-flight checks

```bash
# Confirm the source assignments and dependency behavior
grep -nE 'memcached_instance|redisio|requirepass|base_piddir|fix_redis_config' \
  cookbooks/cache/recipes/default.rb

grep -nE 'memory|port|udp_port|listen|maxconn|threads|max_object_size|ulimit|service_user|service_group' \
  migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
test -d /var/log/memcached
test -d /var/run/memcached
printf "version\r\n" | nc -w 2 127.0.0.1 11211

# Redis instance: 6379
systemctl list-units --type=service | grep -E 'redis|6379'
ss -tlnp | grep ':6379'
test -f /etc/redis/6379.conf
test -d /run/redis
test -d /var/log/redis
stat -c '%A %U:%G %n' /var/log/redis /run/redis

# Do not expose the password in command history or output.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING

# Verify Redis configuration without printing the password
grep -E '^(port|pidfile|dir)' /etc/redis/6379.conf
if test -f /etc/redis/6379.conf; then
  ! grep -qE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
    /etc/redis/6379.conf
fi

# Functional checks for Redis instance 6379
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET migration_check chef_to_ansible EX 60
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET migration_check
redis-cli -p 6379 -a "$REDIS_PASSWORD" DEL migration_check

# Service logs
journalctl -u memcached --no-pager -n 100
journalctl -u redis --no-pager -n 100
```

Expected results:

- Memcached instance `memcached` is enabled, active, listening on TCP and UDP port `11211`, and responds to the protocol check.
- Redis instance `6379` is enabled, active, listening on TCP port `6379`, authenticates successfully, and passes the set/get/delete checks.
- `/var/log/redis` exists with confirmed ownership and mode `0755`.
- `/run/redis`, `/var/log/memcached`, and `/var/run/memcached` exist as required by the confirmed dependency behavior.
- The five reported Redis directives are absent as active configuration lines only after the Ruby block behavior has been verified.