---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` on TCP and UDP port `11211`, and one Redis instance on TCP port `6379`. Memcached uses 64 MB of memory, listens on `0.0.0.0`, allows 1024 connections, and starts and enables its service. Redis uses `/run/redis` for its PID directory, creates `/var/log/redis` with owner `redis:redis` and mode `0755`, configures password authentication, removes five replication-related directive families from `/etc/redis/6379.conf`, and starts and enables the service. The `redisio` dependency recipes and the Memcached custom-resource provider are unavailable in the supplied execution tree, so the Ansible migration must implement equivalent installation, configuration, and service behavior while verifying target-platform package and unit names.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Provider-specific configuration path; the source provider is unavailable. Attribute-defined log path: `/var/log/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1024 maximum connections, `1m` maximum object size, `1024` ulimit, user `service_user`, empty experimental and extra CLI option lists, start and enable actions
  - Threads: Referenced as `node['memcached']['threads']` but not defined in the supplied attributes; expose as an explicit Ansible variable and confirm the intended value

- **Redis on port 6379**: Redis cache service
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Password authentication, `requirepass` configured from a protected secret, log directory owner `redis`, group `redis`, mode `0755`, recursive creation, Redis service enabled and running
  - Removed directives: `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`

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

No provider file was supplied in the execution tree or directory listing. The provider implementation for `memcached_instance[memcached]` is therefore unavailable for direct migration.

**Templates:**

```text
```

No templates are rendered by the supplied recipes.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The following listed files are not included because they are not executed or referenced by the supplied execution tree:

- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb`

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency before Redis-specific tasks.
   - Configures one Redis server collection item on port `6379`.
   - Sets the Redis PID directory to `/run/redis`.
   - Includes the unavailable `redisio` installation/configuration recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` if the file exists.
   - Includes the unavailable `redisio::enable` recipe to enable and run Redis.
   - Redis configuration values represented by the recipe are:
     - Port: `6379`
     - `requirepass`: the source literal is `redis_secure_password_123`; the migration must store it in Ansible Vault or another approved secret-management system
     - `replicaservestaledata`: `nil`

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes the custom resource `memcached_instance[memcached]`.
   - Starts and enables the `memcached` instance.
   - Configures 64 MB memory.
   - Configures TCP port `11211`.
   - Configures UDP port `11211`.
   - Listens on `0.0.0.0`.
   - Sets the maximum connection count to `1024`.
   - Sets the maximum object size to `1m`.
   - Sets ulimit to `1024`.
   - Uses user `service_user`.
   - Passes empty experimental-options and extra-CLI-options lists.
   - References an undefined `threads` attribute; the Ansible role must expose this as an explicit variable without inventing a value.
   - The supplied default attributes are:
     - `version`: `nil`
     - `memory`: `64`
     - `port`: `11211`
     - `udp_port`: `11211`
     - `listen`: `0.0.0.0`
     - `maxconn`: `1024`
     - `max_object_size`: `1m`
     - `experimental_options`: `[]`
     - `extra_cli_options`: `[]`
     - `ulimit`: `1024`
     - `logfilepath`: `/var/log/memcached`

The Redis dependency implementation is unavailable. The replacement Ansible role must install Redis, create or use the `redis` service account, configure port `6379`, configure the protected password, use `/run/redis` for the PID directory, create or manage `/etc/redis/6379.conf`, and expose a verified service unit for enablement and restart operations.

The Memcached custom-resource provider is also unavailable. The replacement Ansible role must install Memcached, generate equivalent service configuration, configure the values above, start the service, and enable it at boot.

No `.each` loops are present in the supplied execution flow.

## Dependencies

**External cookbook dependencies**: `memcached`; `redisio`; `redisio::enable`. The `redisio` and `redisio::enable` recipes are unavailable, and the Memcached custom-resource provider is unavailable.

**System package dependencies**: Memcached and Redis packages are required. Exact package names are not stated in the supplied source and must be verified for the target distribution before implementation; no unverified package name is assumed in this plan.

**Service dependencies**: Memcached service unit name must be verified because the custom-resource provider is unavailable. Redis service unit name must be verified because the `redisio` recipes are unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Chef recipe
  - **URL**: Not applicable
  - **Path**: `cookbooks/cache/recipes/default.rb`
  - **Expression**: `node.default['redisio']['servers'][0]['requirepass']`
  - **Provider implementation**: Not applicable; the password is assigned directly in the recipe

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in a Chef recipe
- **Literal source value**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`
- **Migration storage**: Ansible Vault, an AAP credential, or an approved external secret provider; do not commit the literal password to plaintext defaults, variable files, or templates

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, Vault URL, AWS Secrets Manager reference, environment-variable secret, TLS certificate, private key, or database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- `/var/log/memcached`
- The verified Memcached configuration path
- The verified Redis service unit
- The verified Memcached service unit

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance on port `6379`: TCP `:6379`
- Redis PID directory: `/run/redis`
- Redis Unix socket: none specified

**Templates rendered**: 0. No Chef templates are rendered by the supplied execution flow.

**Configuration operations**:

- Memcached is configured through the unavailable `memcached_instance[memcached]` provider.
- Redis `/etc/redis/6379.conf` is modified by removing lines beginning with:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks:

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
printf "version\r\n" | nc -w 2 127.0.0.1 11211
ps -ef | grep '[m]emcached'
```

Verify:

- The verified Memcached unit is enabled and active.
- TCP port `11211` is listening on `0.0.0.0`.
- UDP port `11211` is listening on `0.0.0.0`.
- The Memcached version command returns a response.
- The process uses 64 MB memory, maximum connections `1024`, listen address `0.0.0.0`, maximum object size `1m`, ulimit `1024`, and the confirmed threads value.
- The process uses user `service_user` where supported by the target platform.

Check the migrated configuration using the verified platform-specific path:

```bash
grep -R --line-number -E '11211|0\.0\.0\.0|1024|64|1m' \
  /etc/memcached* /etc/sysconfig/memcached /etc/default/memcached 2>/dev/null
```

### Redis instance on port `6379`

```bash
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

ss -tlnp | grep ':6379'
ps -ef | grep '[r]edis-server'
```

If the target platform uses an instance-specific unit, replace `redis` with the verified unit name.

Verify:

- Redis is enabled and active.
- Redis listens on TCP port `6379`.
- A Redis server process is running.
- `/run/redis` exists and is used for the PID path.
- `/etc/redis/6379.conf` exists.
- `/var/log/redis` exists with owner `redis:redis` and mode `0755`.

Inspect non-secret Redis settings:

```bash
grep --line-number -E '^(port|pidfile)' /etc/redis/6379.conf
```

Verify that the configuration contains `port 6379` and a PID path under `/run/redis`. Verify the password through a secure secret-management process without exposing it in command output or logs.

Confirm removed directives are absent:

```bash
grep --line-number -E \
  '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

Expected result: no matching lines are returned.

Test authentication without placing the password in shell history:

```bash
read -s REDISCLI_AUTH
export REDISCLI_AUTH
redis-cli -h 127.0.0.1 -p 6379 PING
unset REDISCLI_AUTH
```

Expected result:

```text
PONG
```

Check Redis directories and logs:

```bash
stat -c '%A %U %G %n' /var/log/redis
ls -ld /run/redis
journalctl -u redis --no-pager -n 50
```

### Combined service and network verification

```bash
ss -tlnp | grep -E ':(6379|11211)\b'
ss -ulnp | grep ':11211'
systemctl list-unit-files | grep -E 'memcached|redis'
systemctl --failed
```

Expected listeners:

- Redis TCP port `6379`
- Memcached TCP port `11211`
- Memcached UDP port `11211`

Both named service instances must be enabled and running, and no related service unit should be failed.