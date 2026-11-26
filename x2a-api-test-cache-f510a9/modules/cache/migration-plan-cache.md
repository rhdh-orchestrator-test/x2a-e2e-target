---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached is installed and enabled through the `memcached_instance` custom resource with 64 MB memory, TCP/UDP port `11211`, `0.0.0.0` binding, and a 1024 connection limit. Redis uses the hardcoded password `redis_secure_password_123`, `/run/redis` for PID files, `/var/log/redis` for logs, and `/etc/redis/6379.conf` for configuration. The Redis recipe dependency is missing from the supplied execution tree, so its package name, provider paths, templates, and exact service resource behavior cannot be confirmed.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Package: `memcached`
  - Version: `nil`; no explicit version is requested
  - Memory: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: Read from `node['memcached']['threads']`; no default is defined
  - Experimental options: Empty list
  - Extra CLI options: Empty list
  - Ulimit: `1024`
  - Service account: `service_user`
  - Log directory: `/var/log/memcached`
  - Runtime directory: `/var/run/memcached`
  - Actions: `start`, `enable`

- **redis:6379**: Redis cache service
  - Instance count: 1
  - Port: `6379`
  - Authentication password: `redis_secure_password_123`
  - PID directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Configuration file: `/etc/redis/6379.conf`
  - Enablement: Intended through `redisio::enable`
  - Redis package and exact service name: Cannot be confirmed because the `redisio` dependency recipe is unavailable

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

No provider file is present in the supplied directory listing. The `memcached_instance[memcached]` custom resource is referenced, but its provider path was not supplied.

**Templates:**
```text
```

No templates are rendered by the reachable execution flow.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

**Data bags:**

No data bags are referenced by the reachable `cache` execution flow. Repository catalog entries under `nginx_secrets` and `nginx_sites` are unrelated to this cookbook.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Sets one Redis server configuration object with port `6379`, password `redis_secure_password_123`, and `replicaservestaledata: nil`.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`.
   - Creates `directory[/var/log/redis]` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block[fix_redis_config]`.
   - The Ruby block reads `/etc/redis/6379.conf` only if it exists, removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified Redis configuration back to `/etc/redis/6379.conf`; it does not create the file when absent.
   - Includes `redisio::enable`.
   - The `redisio` and `redisio::enable` recipe files are unavailable, so their package resources, templates, provider paths, service names, and exact service behavior cannot be inferred.
   - Directly represented resources: one `directory`, one `ruby_block`, and three `include_recipe` declarations.
   - The structured execution analysis identifies `group[redis]`; ensure the `redis` group exists before assigning `/var/log/redis` to it. The supplied recipe does not explicitly declare this group.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates the custom resource `memcached_instance[memcached]`.
   - Starts and enables the `memcached` instance.
   - Passes memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, service user `service_user`, maximum object size `1m`, `node['memcached']['threads']`, empty experimental options, empty extra CLI options, and ulimit `1024`.
   - The provider path is not present in the supplied execution tree.
   - No `.each` loops are present.

3. **_package** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - Installs package `memcached` at `node['memcached']['version']`, whose default is `nil`.
   - Creates the system group using `service_group` when the service user does not already exist.
   - Creates the locked system user using `service_user`, with home `/nonexistent`, shell `/bin/false`, comment `Memcached`, no managed home, and primary group `service_group`.
   - Creates `/var/log/memcached` owned by `service_user:service_group` with mode `0755`.
   - Creates `/var/run/memcached` owned by `service_user:service_group` with mode `0755`.

4. **default attributes** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`):
   - Defines `memcached.version` as `nil`.
   - Defines `memcached.memory` as `64`.
   - Defines `memcached.port` as `11211`.
   - Defines `memcached.udp_port` as `11211`.
   - Defines `memcached.listen` as `0.0.0.0`.
   - Defines `memcached.maxconn` as `1024`.
   - Defines `memcached.max_object_size` as `1m`.
   - Defines `memcached.experimental_options` as an empty list.
   - Defines `memcached.extra_cli_options` as an empty list.
   - Defines `memcached.ulimit` as `1024`.
   - Defines `memcached.logfilepath` as `/var/log/memcached`.
   - Does not define `memcached.threads`, although the custom resource reads it.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint
- Redis dependency recipes are missing from the supplied source

**System package dependencies**:

- `memcached`
- Redis package name and version are unconfirmed because the `redisio` recipe is unavailable

**Service dependencies**:

- Memcached is started and enabled by `memcached_instance[memcached]`.
- Redis is intended to be enabled through `redisio::enable`.
- The Redis service resource and exact service name are unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef attribute configuration
- **URL**: None detected
- **Path**: None detected
- **Data bags**: None referenced by the selected cookbook

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Value**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef node attribute
- **Usage context**: Redis authentication for the instance listening on port `6379`
- **Migration requirement**: Store the password in Ansible Vault or an external secret manager. Do not commit it to role defaults, variables, templates, or inventory.

No credentials were detected in the Memcached attributes or resources. No TLS certificate, private key, API key, environment-variable secret, Chef Vault lookup, encrypted data bag lookup, CyberArk integration, Conjur lookup, or database connection string was found in the reachable cookbook flow.

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
- Redis TCP: `0.0.0.0:6379`
- Unix sockets: None specified

**Templates rendered**:

- None; render count: `0`

**Configuration transformations to verify**:

- `/etc/redis/6379.conf` no longer contains the five removed replication-related directives.
- Redis authentication remains configured with the vaulted password.
- Memcached listens on `0.0.0.0`.
- Memcached exposes TCP and UDP port `11211`.
- Memcached maximum connections is `1024`.
- Memcached maximum object size is `1m`.

## Pre-flight checks

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

ss -ltnp | grep ':11211'
nc -vz 127.0.0.1 11211
ss -lunp | grep ':11211'

printf 'version\r\n' | nc -w 2 127.0.0.1 11211
printf 'stats\r\n' | nc -w 2 127.0.0.1 11211

# Verify Memcached configuration characteristics:
# - listen address 0.0.0.0
# - TCP port 11211
# - UDP port 11211
# - maximum connections 1024
# - maximum object size 1m

ls -ld /var/log/memcached
ls -ld /var/run/memcached
stat -c '%U:%G %a %n' /var/log/memcached /var/run/memcached

# Redis instance: redis:6379
# The exact Redis service name must be confirmed on the target distribution.
systemctl list-units --type=service | grep -i redis
systemctl is-active redis-server || systemctl is-active redis

ss -ltnp | grep ':6379'
nc -vz 127.0.0.1 6379

# Supply the password from Ansible Vault; do not place it in shell history.
redis-cli -h 127.0.0.1 -p 6379 --askpass PING
redis-cli -h 127.0.0.1 -p 6379 --askpass INFO server

test -f /etc/redis/6379.conf
grep -nE '^(requirepass|port|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Expected result: no matching output for the five removed directives.
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

ls -ld /run/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /run/redis /var/log/redis

journalctl -u redis-server --no-pager -n 50
journalctl -u redis --no-pager -n 50
```

