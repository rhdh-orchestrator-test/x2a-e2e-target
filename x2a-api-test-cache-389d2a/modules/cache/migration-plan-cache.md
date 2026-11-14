---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` and one Redis instance configured on port `6379`. The execution tree confirms the `memcached` dependency, the missing `redisio` and `redisio::enable` recipes, creation of `/var/log/redis`, and the `ruby_block[fix_redis_config]` resource. The supplied source-derived details additionally describe Memcached defaults, Redis authentication, `/run/redis`, and Redis configuration cleanup, but these values require verification against the original recipe and attribute files because they are not present in the supplied structured execution summary.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Resource: `memcached_instance[memcached]`
  - Service state: Started and enabled
  - Memory: `64` MB, source-derived and requiring verification
  - TCP port: `11211`, source-derived and requiring verification
  - UDP port: `11211`, source-derived and requiring verification
  - Listen address: `0.0.0.0`, source-derived and requiring verification
  - Maximum connections: `1024`, source-derived and requiring verification
  - Maximum object size: `1m`, source-derived and requiring verification
  - Threads: `node['memcached']['threads']`; no value was supplied
  - User: `service_user`
  - Ulimit: `1024`, source-derived and requiring verification
  - Experimental options: Empty list, source-derived and requiring verification
  - Extra CLI options: Empty list, source-derived and requiring verification
  - Package version: `node['memcached']['version']`; default reportedly `nil`, with no pinned version configured

- **Redis on port `6379`**: Redis cache service
  - Configured port: `6379`, source-derived and requiring verification
  - Password authentication: Reported as enabled; requires verification
  - Password: `redis_secure_password_123`, reported as hardcoded; requires verification
  - PID base directory: `/run/redis`, source-derived and requiring verification
  - Configuration file: `/etc/redis/6379.conf`, source-derived and requiring verification
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`, source-derived and requiring verification
  - Log directory group: `redis`, source-derived and requiring verification
  - Log directory mode: `0755`, source-derived and requiring verification
  - Redis service enablement: Requested through `redisio::enable`
  - Replication setting: `replicaservestaledata` reportedly set to `nil`; requires verification

The execution tree confirms one Memcached resource and one Redis configuration flow. No additional Memcached or Redis instances are identified.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Providers**: None supplied.

**Templates**: None supplied.

**Static files**: None supplied.

The `memcached_instance` custom resource is used, but its provider path is not present in the supplied execution tree. The `redisio` and `redisio::enable` recipe files are also not present.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Sets the Redis server collection and Redis PID base directory, according to source-derived details requiring verification.
   - Includes `redisio`.
   - Creates `/var/log/redis`.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes `redisio::enable`.

   **Configured Memcached iteration**:
   - No `.each` loop is present.
   - Declares the single resource `memcached_instance[memcached]`.
   - Configures the reported values: 64 MB memory, TCP/UDP port `11211`, listen address `0.0.0.0`, maximum 1,024 connections, maximum object size `1m`, `service_user`, ulimit `1024`, empty experimental options, and empty extra CLI options.
   - Starts and enables the Memcached service.
   - The custom resource provider is not included; reproduce only the observable behavior after verifying the original implementation.

   **Configured Redis item**:
   - No `.each` loop is present.
   - The source-derived plan reports one Redis item on port `6379`, with `requirepass` set to `redis_secure_password_123` and `replicaservestaledata` set to `nil`.
   - The source-derived plan reports `node['redisio']['base_piddir'] = '/run/redis'`.
   - These assignments are not present in the supplied structured execution summary and must be verified from `cookbooks/cache/recipes/default.rb`.

   **Included recipe: `memcached`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares `memcached_instance[memcached]`.
   - Uses Memcached attribute defaults from `attributes/default.rb`, subject to source verification.
   - No `.each` loops or additional instances are identified.

   **Included recipe: `redisio`** (`redisio` recipe path not supplied):
   - The execution tree identifies the include, but the recipe file is missing.
   - Redis package, configuration, provider, and service resources cannot be determined from the supplied files.
   - Do not invent package names, template paths, or service unit names.

   **Resource: `directory[/var/log/redis]`**:
   - Creates `/var/log/redis`.
   - The source-derived plan reports owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - These properties require verification against the original recipe.

   **Resource: `ruby_block[fix_redis_config]`**:
   - The execution tree confirms the resource exists.
   - The source-derived plan reports that it operates on `/etc/redis/6379.conf` and removes lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The file path and directive behavior are not present in the supplied structured execution summary and must be verified before migration.
   - If confirmed, implement the cleanup with an idempotent Ansible configuration task and notify the Redis service only when the file changes.

   **Included recipe: `redisio::enable`** (`redisio::enable` recipe path not supplied):
   - The execution tree identifies the include, but the recipe file is missing.
   - Intended behavior is to enable the configured Redis service at boot.
   - Determine the actual service unit name from the target installation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package names are verified in the supplied execution tree.
- The Memcached package is managed through the unavailable `memcached_instance` provider implementation.
- The Redis package is managed by the unavailable `redisio` implementation.
- Confirm the target operating system and actual cookbook implementations before selecting Ansible package names.

**Service dependencies**:

- Memcached must be started and enabled.
- Redis must be started and enabled according to the available `redisio` implementation.
- The `redis` user and group must exist before applying ownership to `/var/log/redis`, if those ownership settings are confirmed.

## Credentials

**Detection Summary**: 1 credential reported in 1 file; detection requires verification because the supplied structured analysis does not include the relevant attribute assignment.

**Source**:

- **Provider**: Reported as hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as hardcoded plaintext Chef attribute assignment
- **Value**: `redis_secure_password_123`, requiring verification
- **Usage context**: Redis authentication for the instance on port `6379`
- **Migration storage**: Store as an Ansible Vault variable such as `redis_password`
- **Task handling**: Use `no_log: true` for tasks that may expose the secret

No data bag, encrypted data bag, Chef Vault, CyberArk, Conjur, external secret-manager URL, environment-variable secret, TLS certificate, private key, database connection string, or additional credential is identified.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`, if confirmed by source inspection
- `/var/log/redis`
- `/run/redis`, if confirmed by source inspection
- Memcached configuration file created by the custom resource; exact path unavailable
- `/var/log/memcached`, if created or used by the target Memcached package

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the actual configured bind address
- Unix sockets: None identified

**Templates rendered**:

- None identified
- Reported Redis configuration changes are made in place by `ruby_block[fix_redis_config]`; no Chef template is identified

## Pre-flight checks

Use verified service unit names and configuration values on the target host. The Redis unit name and package name cannot be determined from the supplied `redisio` files because those files are missing.

### Memcached instance: `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached

ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'

printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

ps aux | grep '[m]emcached'
ls -ld /var/log/memcached
```

Expected results:

- The Memcached service is active.
- The service is enabled at boot.
- TCP port `11211` is listening.
- UDP port `11211` is listening.
- The Memcached query returns a response beginning with `VERSION`.

### Redis instance on port `6379`

```bash
systemctl list-unit-files | grep -E 'redis|redis-server'

# Replace <redis-service-unit> with the verified service unit.
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>

ss -tlnp | grep ':6379'

test -d /run/redis
ls -ld /run/redis

test -d /var/log/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis

test -f /etc/redis/6379.conf
```

If password authentication is verified and configured through Ansible Vault:

```bash
export REDISCLI_AUTH='<retrieve securely from Ansible Vault>'

redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
redis-cli -p 6379 CONFIG GET port

unset REDISCLI_AUTH
```

Expected authenticated response:

```text
PONG
```

If password authentication is verified, an unauthenticated check should return an authentication-required error:

```bash
redis-cli -p 6379 PING
```

If the Redis configuration cleanup is verified from the source:

```bash
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

The command should produce no matching output after migration.

Inspect Redis logs with the verified service unit:

```bash
journalctl -u <redis-service-unit> --no-pager -n 100
find /var/log/redis -maxdepth 1 -type f -print
```