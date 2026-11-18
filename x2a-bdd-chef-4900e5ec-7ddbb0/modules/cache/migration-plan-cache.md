---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the Memcached instance `memcached` on TCP and UDP port `11211`, and the Redis instance identified by port `6379`. Memcached is configured through the `memcached_instance[memcached]` custom resource and is started and enabled. Redis is configured through the external `redisio` dependency with `/run/redis` as its PID directory, `/var/log/redis` as its log directory, and authentication enabled using a password that must be migrated to Ansible Vault or an approved secrets mechanism. The Redis dependency recipes are not present in the supplied execution tree, so their package, template, provider, and service-unit implementation details must be verified separately. The cache recipe removes selected replication-related directives from `/etc/redis/6379.conf` and requests Redis enablement through `redisio::enable`.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Runtime path and log path require dependency verification; the configured Memcached log attribute is `/var/log/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: `64` MB memory, `1024` maximum connections, `1m` maximum object size, `1024` ulimit, empty experimental and extra CLI option lists, and actions `start` and `enable`
  - Package: `memcached`
  - Service account: The custom resource receives `service_user`; the resolved account name is not available in the supplied execution data
  - Threads: `node['memcached']['threads']`; no default value is defined in the supplied attribute file

- **redis-6379**: Redis cache service identified by port `6379`
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`
  - Key Config: Authentication required; password is `redis_secure_password_123` in the source recipe and must be vaulted during migration
  - Redis server collection: Exactly one item with port `6379`, `requirepass` set to the source password, and `replicaservestaledata` set to `nil`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` when present
  - Service enablement: Requested through `redisio::enable`
  - Redis package, provider, and systemd unit: Not available in the supplied execution tree and must not be inferred

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

The execution tree identifies `memcached_instance[memcached]` as a custom resource, but does not provide a provider file path. Do not invent or assume one.

**Templates:**

```text
```

No rendered templates are shown in the supplied execution tree or directory listing.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files are deployed by the shown execution flow.

## Module Explanation

The cookbook performs operations in the following execution order. The `cache::default` recipe invokes `memcached::default` before continuing with Redis configuration.

1. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Configures the custom resource `memcached_instance[memcached]`.
   - Sets memory to `64`, TCP port to `11211`, UDP port to `11211`, listen address to `0.0.0.0`, maximum connections to `1024`, maximum object size to `1m`, ulimit to `1024`, and empty experimental and extra CLI option lists.
   - Passes `node['memcached']['threads']` as the thread value; the supplied default attribute file does not define a value.
   - Passes `service_user` to the custom resource; the resolved account name is not available in the supplied execution data.
   - Starts Memcached and enables it at boot.
   - Does not expose a provider path or provider implementation in the supplied execution tree; the migration must reproduce the observable behavior without inventing one.
   - No `.each` loop is present. The single configured item is `memcached`.

2. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached`, which invokes `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Sets the Redis server collection to one item:
     - Port: `6379`
     - `requirepass`: source password `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`. The implementation is not present in the supplied execution tree, so package names, templates, providers, and service-unit names must be obtained separately.
   - Creates `/var/log/redis` through `directory[/var/log/redis]` with the analyzed intended settings:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive: `true`
     - The `redis` account and group are not created by this cache recipe; they must be supplied by the Redis dependency or managed separately.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - Does nothing when `/etc/redis/6379.conf` does not exist.
   - When the file exists, removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Rewrites the Redis configuration file only when substitutions are made.
   - Includes `redisio::enable` after Redis configuration, log-directory creation, and configuration cleanup. The exact Redis systemd unit is unavailable and must not be assumed.
   - No `.each` loop is present. The single Redis item is identified by port `6379`.

3. **Memcached default attributes** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`):
   - Defines the following analyzed defaults:
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
   - The `version` value is `nil`, so no Memcached package version is pinned.
   - No `.each` loop is present.

## Dependencies

**External cookbook dependencies**:

- `memcached`
- `redisio`
- `redisio::enable`

The Redis recipe files are not present in the supplied execution tree. Their package, provider, template, and service dependencies are unspecified.

**System package dependencies explicitly shown**:

- `memcached`

No Redis package name is confirmed by the supplied execution tree.

**System accounts and groups**:

- Redis ownership is configured as `redis:redis` for `/var/log/redis`, but the cache recipe does not create the account or group.
- Memcached receives `service_user` and `service_group`; their resolved names are unavailable.
- `/var/log/memcached` and `/var/run/memcached` are dependency/runtime paths requiring verification, not explicitly analyzed resources in the supplied execution tree.

**Service dependencies**:

- Memcached is started and enabled by `memcached_instance[memcached]`.
- Redis configuration and enablement are delegated to `redisio` and `redisio::enable`.
- The exact Redis service unit is unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef attribute assignment
- **Usage context**: Redis authentication for the Redis instance on port `6379`
- **Migration storage**: Store in Ansible Vault or an approved AAP credential/secrets mechanism
- **Migration handling**: Use the vaulted value when managing Redis configuration and suppress it from task output

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database connection strings, or additional hardcoded tokens were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- `/var/log/memcached` — dependency/runtime path requiring verification
- `/var/run/memcached` — dependency/runtime path requiring verification

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379`
- Redis Unix socket: None specified

**Templates rendered**:

- None rendered by the supplied execution tree

**Configuration transformations**:

- `/etc/redis/6379.conf` is modified by removing five directive families.
- No configuration template rendering is shown.
- No `.each` iterations require expansion beyond the named Memcached and Redis instances.

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ss -ltnup | grep ':11211'
printf "version\r\n" | nc -w 2 127.0.0.1 11211
ps aux | grep '[m]emcached'
getent passwd memcached
getent group memcached
ls -ld /var/log/memcached
ls -ld /var/run/memcached
```

Expected results:

- The Memcached service is active and enabled.
- A TCP listener exists on port `11211`.
- A UDP listener exists on port `11211`.
- The Memcached request returns a `VERSION` response.
- Account and group ownership match the resolved `service_user` and `service_group` values. The supplied cookbook data does not expose those final names.

### Redis instance `redis-6379`

Identify the Redis unit supplied by the `redisio` dependency:

```bash
systemctl list-unit-files | grep -i redis
systemctl list-units --type=service | grep -i redis
```

Check the discovered unit:

```bash
systemctl status <discovered-redis-unit>
systemctl is-enabled <discovered-redis-unit>
systemctl is-active <discovered-redis-unit>
```

Check the Redis listener and authentication:

```bash
ss -ltnp | grep ':6379'
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -h 127.0.0.1 -p 6379 PING
```

Expected results:

- Redis is active and enabled.
- A TCP listener exists on port `6379`.
- Authenticated `redis-cli` returns `PONG`.
- Unauthenticated access fails with an authentication-required error and does not return `PONG`.

Validate the Redis configuration cleanup:

```bash
grep -E '^(requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected results:

- The Redis authentication directive is present according to the Redis dependency’s configuration behavior.
- These directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

Validate Redis directories and ownership:

```bash
ls -ld /var/log/redis
ls -ld /run/redis
stat -c '%A %U:%G %n' /var/log/redis
stat -c '%A %U:%G %n' /etc/redis/6379.conf
find /var/log/redis -maxdepth 1 -type f -print
```

Expected results:

- `/var/log/redis` exists with mode `0755` and owner/group `redis:redis`, provided those account and group objects are supplied by the Redis dependency or separately managed.
- `/run/redis` exists if created by the Redis dependency.
- No exact Redis log filename is assumed.

Review Redis logs using the discovered unit:

```bash
journalctl -u <discovered-redis-unit> --no-pager -n 100
```

### Idempotence

Run the Ansible role twice and verify that:

- The `memcached` instance remains started and enabled.
- The `redis-6379` instance remains started and enabled.
- `/var/log/redis` is unchanged after the first successful run.
- `/etc/redis/6379.conf` does not accumulate changes.
- All five removed Redis directive families remain absent.
- The Redis password remains stored only in the vaulted secret source.
