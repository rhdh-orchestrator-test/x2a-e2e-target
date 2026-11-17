---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` and one Redis instance listening on port `6379`. Memcached is started and enabled through the `memcached_instance` custom resource with 64 MB memory, TCP/UDP port `11211`, wildcard listening, a 1024-connection limit, 1 MB maximum object size, and a `service_user` account. Redis is configured with the hardcoded plaintext password `redis_secure_password_123`, uses `/run/redis` for its PID directory, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and is enabled through the unavailable `redisio::enable` recipe. The Redis dependency recipes and Memcached custom-resource provider are not present in the supplied execution tree, so their exact package and service resources cannot be reproduced from this source alone.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Resource: `memcached_instance[memcached]`
  - Location/Path: Configuration location is provider- and distribution-dependent; log path attribute is `/var/log/memcached`
  - Port/Socket: TCP `11211`, UDP `11211`; no Unix socket configured
  - Key Config: 64 MB memory, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, user `service_user`, ulimit `1024`, start and enable actions, empty experimental and additional option lists
  - Threads: Attribute-driven; no concrete default is defined in the supplied attribute file
  - Package version: `nil`; no explicit Memcached version is requested

- **redis-6379**: Redis cache service
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket configured
  - Key Config: Requires password `redis_secure_password_123`; `/var/log/redis` is created recursively with owner `redis`, group `redis`, and mode `0755`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Enablement: Delegated to the unavailable `redisio::enable` recipe
  - Restart behavior: No explicit Redis restart or reload resource is present in the supplied execution tree

## File Structure

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
data_bags/nginx_secrets/site.json
data_bags/nginx_sites/ci.cluster.local.json
data_bags/nginx_sites/status.cluster.local.json
data_bags/nginx_sites/test.cluster.local.json
```

### Recipes

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

### Providers

```text
```

No provider file is present. The `memcached_instance` custom-resource provider is not included in the supplied execution tree.

### Templates

```text
```

No templates are rendered.

### Attributes

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

### Files

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

### Data Bags

```text
data_bags/nginx_secrets/site.json
data_bags/nginx_sites/ci.cluster.local.json
data_bags/nginx_sites/status.cluster.local.json
data_bags/nginx_sites/test.cluster.local.json
```

These data bags are present in the source inventory, but no data bag lookup is shown in the `cache` execution flow.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Assigns one Redis server configuration on port `6379`.
   - Sets the Redis password to the hardcoded plaintext value `redis_secure_password_123`.
   - Sets `replicaservestaledata` to `nil`.
   - Sets the Redis PID directory to `/run/redis`.
   - Includes `redisio`; the referenced recipe is not present in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes `redisio::enable`; the referenced recipe is not present in the supplied execution tree.
   - No `.each` loops or collection iterations are present.
   - Resources represented: three `include_recipe` operations, one `directory`, and one `ruby_block`.
   - `ruby_block[fix_redis_config]` checks for `/etc/redis/6379.conf`, reads it if present, removes complete lines for `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`, then writes the modified content back.
   - If `/etc/redis/6379.conf` does not exist, the block performs no file modification.
   - The execution tree contains no explicit Redis restart or reload after configuration changes.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates one `memcached_instance['memcached']` custom resource.
   - Starts and enables the `memcached` instance.
   - Configures 64 MB memory.
   - Configures TCP port `11211` and UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets the maximum connection count to `1024`.
   - Sets the maximum object size to `1m`.
   - Passes user `service_user`.
   - Passes ulimit `1024`.
   - Passes empty experimental and additional CLI option lists.
   - Reads the thread count from `node['memcached']['threads']`; the supplied attribute file does not define a concrete value.
   - Does not contain any `.each` loops.
   - Resource count: one `memcached_instance`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- Memcached package: required, but the exact package name is owned by the missing `memcached_instance` provider and is not available in the supplied execution tree.
- Redis package: required, but the exact package name is owned by the missing `redisio` dependency and is not available in the supplied execution tree.
- Select platform-appropriate package names during Ansible implementation after confirming the target distribution.

**Service dependencies**:

- Memcached instance `memcached`: must be started and enabled.
- Redis instance `redis-6379`: must be started and enabled; exact service-unit name is unavailable because the `redisio` dependency recipes are missing.

## Credentials

**Detection Summary**: 2 sensitive values or credential-bearing records detected across 2 files.

**Source**:

- **Provider**: Hardcoded plaintext Redis configuration assignment in the Chef recipe; encrypted Chef data bag for the unrelated `nginx_secrets/site` token
- **URL**: None detected
- **Path**:
  - Redis password: `cookbooks/cache/recipes/default.rb`
  - Encrypted data bag: `data_bags/nginx_secrets/site.json`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value in the recipe’s Redis server configuration assignment
- **Value**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`
- **Migration handling**: Store the password in Ansible Vault or an AAP credential/secret integration. Do not commit the plaintext value to defaults or regular variables.

### Encrypted `nginx_secrets/site` token

- **Variable(s)**: `token`
- **Source file(s)**: `data_bags/nginx_secrets/site.json`
- **Current storage**: Encrypted Chef data bag
- **Data bag item**: `nginx_secrets/site`
- **Encryption metadata**: AES-256-CBC, version `1`, encrypted payload present, IV present
- **Usage context**: No lookup or usage is shown in the supplied `cache` execution flow. Treat it as an unrelated detected secret unless another cookbook consumes it.
- **Migration handling**: If required by another migrated role, store the decrypted equivalent in Ansible Vault or an AAP-managed secret. Do not copy the encrypted Chef payload directly into Ansible variables.

### Detected non-secret data bag configuration

- `data_bags/nginx_sites/ci.cluster.local.json`
  - ID: `ci.cluster.local`
  - Document root: `/var/www/ci.cluster.local`
  - SSL enabled: `true`
- `data_bags/nginx_sites/status.cluster.local.json`
  - ID: `status.cluster.local`
  - Document root: `/var/www/status.cluster.local`
  - SSL enabled: `true`
- `data_bags/nginx_sites/test.cluster.local.json`
  - ID: `test.cluster.local`
  - Document root: `/var/www/test.cluster.local`
  - SSL enabled: `true`

No use of these records is shown in the cache execution flow.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`
- `/var/log/memcached`
- Target-distribution Memcached configuration path, as determined by the selected provider implementation

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the configured Redis bind address
- Unix sockets: none configured or identified

**Templates rendered**: None; render count `0`.

**Configuration mutations to verify**:

- `/etc/redis/6379.conf` is rewritten only when it exists.
- No active lines remain for `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, or `replica-priority`.

## Pre-flight checks

Replace `<redis-service-name>` and `<memcached-service-name>` with the service-unit names selected for the target distribution.

```bash
# Redis instance: redis-6379
ls -ld /run/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis
test -f /etc/redis/6379.conf

grep -nE '^[[:space:]]*(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

ss -tlnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>

redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" INFO server
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" CONFIG GET requirepass

journalctl -u <redis-service-name> --no-pager -n 100

# Memcached instance: memcached
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>

ss -tlnp | grep ':11211'
lsof -iTCP:11211 -sTCP:LISTEN
ss -ulnp | grep ':11211'

printf 'version\r\n' | nc -w 2 127.0.0.1 11211
printf 'stats\r\n' | nc -w 2 127.0.0.1 11211
printf 'stats settings\r\n' | nc -w 2 127.0.0.1 11211

ls -ld /var/log/memcached
```

Expected results:

- The `redis-6379` instance is active and enabled.
- Redis is listening on port `6379`.
- Authenticated `redis-cli` connectivity returns `PONG`.
- `/run/redis` exists.
- `/var/log/redis` exists, is owned by `redis:redis`, and has mode `0755`.
- No active Redis configuration lines remain for the five removed directives.
- The `memcached` instance is active and enabled.
- Memcached is listening on TCP port `11211` and UDP port `11211`.
- The Memcached version and statistics commands return successfully.
- Memcached statistics expose approximately 64 MB of configured memory and a maximum connection setting of `1024`, where supported by the target platform.
- The target platform’s Memcached configuration or service arguments reflect listen address `0.0.0.0`, maximum object size `1m`, user `service_user`, and ulimit `1024`.