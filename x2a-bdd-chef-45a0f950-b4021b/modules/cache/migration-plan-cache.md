---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. The supplied recipe analysis reports Memcached settings of 64 MB, TCP/UDP port `11211`, listen address `0.0.0.0`, and maximum 1,024 connections. Redis is reported with password authentication, PID directory `/run/redis`, log directory `/var/log/redis`, and configuration cleanup for five replication-related directive types. The Redis dependency recipes are unavailable, and the reported dependency-derived settings must be verified before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached caching service
  - Package: `memcached` — reported; verify against the dependency provider
  - Memory allocation: `64` MB — reported; verify
  - TCP port: `11211` — reported; verify
  - UDP port: `11211` — reported; verify
  - Listen address: `0.0.0.0` — reported; verify
  - Maximum connections: `1024` — reported; verify
  - Maximum object size: `1m` — reported; verify
  - Threads: `node['memcached']['threads']`; effective value is unknown
  - Experimental options: `[]`
  - Additional CLI options: `[]`
  - Ulimit: `1024` — reported; verify
  - Log directory: `/var/log/memcached` — reported; verify
  - Runtime directory: `/var/run/memcached` — reported; verify
  - Service account and group: Dependency-defined values; exact names are unavailable
  - Service state: Started and enabled — reported; verify against the provider

- **redis_6379**: Redis caching service configured on port `6379`
  - Port: `6379` — reported; verify from the recipe and Redis dependency
  - Password: `redis_secure_password_123` — reported hardcoded value; migrate through Ansible Vault or an equivalent secret store
  - PID directory: `/run/redis` — reported; verify
  - Configuration file: `/etc/redis/6379.conf` — reported; verify
  - Log directory: `/var/log/redis` — reported; verify
  - Log directory owner: `redis` — reported; verify
  - Log directory group: `redis` — reported; verify
  - Log directory mode: `0755` — reported; verify
  - Log directory creation: Recursive — reported; verify
  - Service state: Enabled through `redisio::enable`; exact service name is unavailable
  - Additional configuration cleanup: Remove complete lines beginning with:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

The Redis package name, service name, system user and group behavior, generated configuration behavior, and provider implementation must be verified from the unavailable `redisio` dependency before migration.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only files participating in the supplied execution flow are listed below. The dependency Redis recipe files are explicitly reported as not found and are not listed as executable files.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

The `memcached_instance[memcached]` custom resource has an implementation in the Memcached dependency, but no provider file path was supplied. Do not invent a provider path.

**Templates:**
```text
```

No rendered ERB templates are present in the supplied analysis.

**Attributes:**
```text
```

An attribute file was reported in the dependency directory, but its exact path and contents were not included in the validated execution tree. The effective value of `node['memcached']['threads']` is unknown.

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` are present.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Configures the Redis server collection with one reported server on port `6379`.
   - Sets the reported Redis base PID directory to `/run/redis`.
   - Includes the Redis dependency recipe.
   - Creates the Redis log directory.
   - Removes reported incompatible Redis directives from `/etc/redis/6379.conf`.
   - Includes the Redis enable recipe.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Passes the reported memory, TCP port, UDP port, listen address, maximum connections, maximum object size, thread value, experimental options, extra CLI options, and ulimit.
   - Requests `start` and `enable` actions.
   - The custom resource is reported to install package `memcached`, create the service account and group, create `/var/log/memcached` and `/var/run/memcached`, and start and enable the service; these provider behaviors require verification.
   - The exact provider path and dependency-defined service account names are unavailable.
   - Iterations: None.

3. **Redis attribute configuration** (`cookbooks/cache/recipes/default.rb`):
   - Defines one reported Redis server item:
     - Instance name: `redis_6379`
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - The attribute assignments and literal password require confirmation against the analyzed recipe source.

4. **`redisio`** (`redisio/recipes/default.rb`):
   - The recipe file was not found in the supplied execution tree.
   - Verify the Redis package name, service name, user and group creation, configuration generation, configuration path, and password handling before implementation.

5. **Redis log directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Reported owner: `redis`.
   - Reported group: `redis`.
   - Reported mode: `0755`.
   - Reported recursive creation: enabled.
   - These properties require confirmation from the analyzed resource.

6. **`fix_redis_config` ruby block** (`cookbooks/cache/recipes/default.rb`):
   - Operates on the reported file `/etc/redis/6379.conf`.
   - If the file exists, removes lines beginning with the five reported directive names:
     `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
   - If the file does not exist, no change is made.
   - The target path and directive patterns require confirmation from the analyzed ruby block.
   - The migrated role should notify a Redis restart or reload only when the file changes, subject to verification of the Redis service behavior.

7. **`redisio::enable`** (`redisio/recipes/enable.rb`):
   - The recipe file was not found in the supplied execution tree.
   - Its intended behavior is to enable the Redis service at boot.
   - The exact service name and implementation require verification.
   - Iterations: None.

## Dependencies

**External cookbook dependencies**:

- `memcached` — reported version constraint `~> 6.0`; verify from cookbook metadata
- `redisio` — reported dependency with no version constraint; verify from cookbook metadata

**System package dependencies**:

- `memcached` — reported; verify against the Memcached provider
- Redis package — package name unavailable until the `redisio` dependency is inspected

**Service dependencies**:

- Memcached service — reported as started and enabled by `memcached_instance[memcached]`; exact service implementation requires verification
- Redis service — intended to be enabled by `redisio::enable`; exact service name is unavailable

**Supported platforms**:

- Ubuntu `>= 18.04` — reported; verify from cookbook metadata
- CentOS `>= 7.0` — reported; verify from cookbook metadata

## Credentials

**Detection Summary**: 1 reported credential in 1 source file; confirm against credential-analysis output.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: Redis configuration for port `6379`

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123` — reported; do not reproduce in migrated secret files
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext in a Chef node attribute assignment
- **Usage context**: Redis client authentication; reported to be passed into the Redis configuration generated by `redisio`
- **Migration storage**: Ansible Vault or an AAP credential/secret mechanism
- **Handling requirements**: Render with restrictive permissions and use `no_log: true` for tasks handling the password

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database connection strings, or additional tokens were reported.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `:6379`
- Redis Unix socket: None reported

**Templates rendered**:

- None

**Configuration transformations**:

- Remove reported directive lines from `/etc/redis/6379.conf`:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

```bash
# Verify the Memcached instance named memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
printf 'stats\r\n' | nc -w 2 127.0.0.1 11211

# Verify the Redis instance named redis_6379.
# Discover the service name because redisio is unavailable.
systemctl list-unit-files | grep -E 'redis|redis-server'
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>

# Verify Redis configuration and directories
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|dir|pidfile)' /etc/redis/6379.conf
stat -c '%A %U:%G %n' /run/redis
stat -c '%A %U:%G %n' /var/log/redis
ss -tlnp | grep ':6379'

# Verify that reported incompatible directives are absent
! grep -E '^replica-serve-stale-data' /etc/redis/6379.conf
! grep -E '^replica-read-only' /etc/redis/6379.conf
! grep -E '^repl-ping-replica-period' /etc/redis/6379.conf
! grep -E '^client-output-buffer-limit' /etc/redis/6379.conf
! grep -E '^replica-priority' /etc/redis/6379.conf

# Test Redis authentication with the vaulted password
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' PING
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' INFO server

# Review logs for both named instances
journalctl -u memcached --no-pager -n 50
journalctl -u <redis-service-name> --no-pager -n 50

# Verify filesystem capacity and directory state
df -h /var/log
df -h /run
ls -ld /var/log/redis
ls -ld /var/log/memcached
ls -ld /var/run/memcached
ls -ld /run/redis
```

Expected results:

- `memcached` is active and enabled.
- Memcached listens on TCP and UDP port `11211`.
- The Memcached version and statistics commands return responses.
- `redis_6379` listens on TCP port `6379`.
- Redis authentication succeeds with the vaulted password.
- `/etc/redis/6379.conf` exists and contains the expected port and authentication configuration.
- The five reported incompatible Redis directive types are absent.
- `/var/log/redis`, `/var/log/memcached`, `/var/run/memcached`, and `/run/redis` exist with verified ownership and modes.
- Redis service status checks use the service name discovered from the `redisio` dependency.