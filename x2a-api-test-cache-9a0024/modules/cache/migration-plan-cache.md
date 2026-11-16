---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache services: Memcached instance `memcached` and Redis instance `6379`. Memcached is started and enabled with 64 MB memory, TCP/UDP port 11211, wildcard listening, 1024 maximum connections, 1 MB maximum object size, and ulimit 1024. Redis listens on port 6379 with password authentication, uses `/run/redis` for runtime/PID files, creates `/var/log/redis`, removes five replication and output-buffer directives from `/etc/redis/6379.conf`, and is enabled through the `redisio` dependency. The Redisio implementation and some attribute, metadata, and credential claims require verification because the corresponding dependency or analysis artifacts were not supplied.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached caching service managed by `memcached_instance[memcached]`
  - Package: `memcached`
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `11211`; UDP `11211`
  - Listen address: `0.0.0.0`
  - Key Config: 64 MB memory, 1024 maximum connections, 1 MB maximum object size, ulimit 1024, start and enable actions
  - Threads: `node['memcached']['threads']`; no default is present in the supplied attribute file
  - Experimental options: Empty
  - Extra CLI options: Empty
  - Runtime user/group: `service_user` and `service_group`; resolved names require verification
  - Version: `nil`; no explicit package version is configured

- **6379**: Redis server instance
  - Location/Path: `/etc/redis/6379.conf`; PID base directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication enabled with `redis_secure_password_123`; log directory owned by `redis:redis` with mode `0755` and recursive creation
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Replication setting: `replicaservestaledata` explicitly initialized to `nil`
  - Service actions: Managed through `redisio` and `redisio::enable`; the exact service name requires verification

The Redis server collection contains exactly one item, **6379**. No other Redis instances are configured.

The Memcached attribute collections are empty:

- `node['memcached']['experimental_options']`: `[]`
- `node['memcached']['extra_cli_options']`: `[]`

## File Structure

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

No provider file was supplied in the execution tree or structured analysis.

**Templates:**

No templates are rendered by the analyzed execution flow.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

No static files are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe `memcached::default`.
   - Executes `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Configures the Redis server collection with exactly one instance, **6379**:
     - Port `6379`
     - Password `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets the Redis PID base directory to `/run/redis`.
   - Includes the `redisio` recipe. Its package, service, provider, configuration template, and implementation are not present in the supplied source tree and must be verified.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block[fix_redis_config]`:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Reads the file when present.
     - Removes lines matching:
       - `replica-serve-stale-data`
       - `replica-read-only`
       - `repl-ping-replica-period`
       - `client-output-buffer-limit`
       - `replica-priority`
     - Writes the modified contents back.
     - Does not create the file when it is absent.
   - Includes `redisio::enable`.
   - Resource order:
     1. `include_recipe 'memcached'`
     2. `include_recipe 'redisio'`
     3. `directory[/var/log/redis]`
     4. `ruby_block[fix_redis_config]`
     5. `include_recipe 'redisio::enable'`

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Applies actions `start` and `enable`.
   - Configures:
     - Memory: `64`
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - Threads: `node['memcached']['threads']`; unresolved in the supplied attributes
     - Experimental options: `[]`
     - Extra CLI options: `[]`
     - Ulimit: `1024`
     - User: `service_user`
   - The equivalent Ansible implementation must install `memcached`, create or verify the service account and group, create `/var/log/memcached` and `/var/run/memcached`, configure the exact runtime options, start the service, and enable it at boot.
   - The supplied package support definitions also reference the `memcached` package, `service_group`, `service_user`, `/var/log/memcached`, and `/var/run/memcached`.
   - The resolved values of `service_user`, `service_group`, and `threads` must be verified rather than guessed.

3. **`redisio` dependency**:
   - Included from `cookbooks/cache/recipes/default.rb`.
   - Its recipe, provider, package implementation, service unit, and configuration template were not supplied.
   - The Ansible migration must verify the Redis package name, service name, configuration layout, runtime user, and exact configuration behavior.

4. **`redisio::enable` dependency**:
   - Included after the Redis configuration-fix block.
   - Must enable the verified Redis service for instance **6379**.
   - The exact service name and implementation require verification.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

These dependency and version claims require confirmation from cookbook metadata because metadata analysis was not supplied.

**System package dependencies**:

- `memcached`
- Redis package: provided indirectly by `redisio`; exact package name requires verification

**Service dependencies**:

- Memcached service for instance **memcached**
- Redis service for instance **6379**, managed by `redisio` and `redisio::enable`

**Supported platforms requiring metadata verification**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file. The credential assignment should be reconfirmed against the source analysis.

**Source**:

- **Provider**: Hardcoded
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Configured instance**: Redis **6379**
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value in Chef source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication
- **Ansible migration**: Store the value in Ansible Vault, preferably as `redis_password`, and render it into the Redis configuration without exposing it in task output.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, or environment-variable-based secret reference was detected.

No TLS certificate, private key, PEM, CRT, or database connection string containing credentials was detected.

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

- Memcached instance **memcached**: TCP `0.0.0.0:11211`
- Memcached instance **memcached**: UDP `0.0.0.0:11211`
- Redis instance **6379**: TCP port `6379`
- Unix sockets: None specified

**Templates rendered**:

- No Chef templates are present in the analyzed execution flow.
- Redis configuration template behavior must be verified from the missing `redisio` dependency.

**Configuration transformations to verify**:

- Redis password authentication is configured for instance **6379**.
- The five specified Redis directives are absent after the configuration-fix task.
- Memcached uses 64 MB memory, TCP/UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, and ulimit `1024`.
- Memcached `threads`, `service_user`, and `service_group` values are resolved explicitly during migration.

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'
```

Expected result: the Memcached service is active and enabled, and a Memcached process is present.

```bash
printf "version\r\n" | nc -w 2 127.0.0.1 11211
printf "version\r\n" | nc -u -w 2 127.0.0.1 11211
```

Expected result: TCP returns a line beginning with `VERSION`; UDP returns a version response when UDP is enabled and supported.

```bash
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
```

Expected result: TCP and UDP port `11211` are listening on the intended wildcard address.

```bash
systemctl cat memcached
grep -R -E -- '-m[[:space:]]+64|-p[[:space:]]+11211|-U[[:space:]]+11211|-l[[:space:]]+0.0.0.0|-c[[:space:]]+1024' \
  /etc/memcached.conf /etc/sysconfig/memcached /etc/default/memcached 2>/dev/null
```

Expected result:

- Memory is 64 MB.
- TCP and UDP ports are `11211`.
- Listen address is `0.0.0.0`.
- Maximum connections are `1024`.

```bash
stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached
```

Expected result: both directories exist with ownership and permissions matching the resolved Memcached service user/group and the intended mode.

### Redis instance `6379`

First verify the service name supplied by `redisio`. Then run:

```bash
systemctl status <verified-redis-service-name>
systemctl is-enabled <verified-redis-service-name>
systemctl is-active <verified-redis-service-name>
ps aux | grep '[r]edis-server'
```

Expected result: the Redis service for instance **6379** is active and enabled, and a Redis server process is present.

```bash
redis-cli -p 6379 PING
```

Expected result: the unauthenticated request is rejected with an authentication error.

```bash
read -s REDIS_PASSWORD
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning PING
unset REDIS_PASSWORD
```

Expected result:

```text
PONG
```

```bash
grep -nE '^(requirepass|port|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result:

- `port 6379` is present.
- `requirepass` is configured from the protected Ansible secret.
- The following directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

```bash
ss -ltnp | grep ':6379'
```

Expected result: Redis is listening on TCP port `6379`.

```bash
stat -c '%A %U:%G %n' /var/log/redis
stat -c '%A %U:%G %n' /run/redis
```

Expected result:

- `/var/log/redis` exists with mode `0755`, owner `redis`, and group `redis`.
- `/run/redis` exists as the configured Redis runtime/PID directory.

```bash
journalctl -u <verified-redis-service-name> --no-pager -n 100
```

Verify Redis startup and runtime errors. If Redis logs to a file, verify the exact path selected by the `redisio` implementation.

```bash
redis-server /etc/redis/6379.conf --test-memory 2
```

If the target Redis version does not support this validation command, validate through the service manager and inspect:

```bash
systemctl status <verified-redis-service-name>
journalctl -u <verified-redis-service-name> --no-pager -n 100
```

The service must start successfully with `/etc/redis/6379.conf` and the protected password value.