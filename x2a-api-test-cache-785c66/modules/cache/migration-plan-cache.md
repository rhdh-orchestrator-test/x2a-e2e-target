---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` listening on TCP and UDP port `11211`, with 64 MB memory, 1,024 maximum connections, a `0.0.0.0` listen address, and a 1 MB maximum object size; and one Redis server on port `6379`. Redis uses `/run/redis` for PID data, `/var/log/redis` for logs, and a hardcoded authentication password that must be migrated to Ansible Vault or another secret store. The Redis installation and enablement recipes are unavailable from the supplied execution tree, so the Ansible implementation must explicitly resolve the Redis package, service, and installation details.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Package: `memcached`
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `11211`; UDP `11211`
  - Listen address: `0.0.0.0`
  - Key Config: 64 MB memory, 1,024 maximum connections, 1 MB maximum object size, ulimit `1024`
  - Actions: Start and enable the service
  - Worker threads: Not explicitly defined; do not invent a value
  - Experimental options: Empty
  - Additional CLI options: Empty
  - Service account: The custom resource receives `service_user`; the resolved value is not present in the supplied files

- **Redis server on port 6379**: Redis cache service configured through `redisio`
  - Package: Not determinable because the `redisio` recipe is unavailable
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is set in the Chef source to `redis_secure_password_123`; the five specified replication and buffer directives are removed
  - Log ownership: `redis:redis`
  - Log mode: `0755`
  - Actions: Configure and enable Redis
  - Service unit: Not determinable from the supplied execution tree

There are no collection iterations or `.each` loops in the supplied recipe flow. The cookbook configures exactly one Memcached instance, `memcached`, and one Redis server on port `6379`.

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

No provider file path was supplied for `memcached_instance`. Do not invent a provider path. The `memcached_instance` custom resource is nevertheless part of the execution flow.

**Templates:**
```text
```

No templates are rendered by the supplied recipes or listed in the execution tree.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The `redisio` and `redisio::enable` recipe files are referenced by the execution flow but are unavailable and therefore are not listed as existing files.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Sets the Redis server configuration for port `6379`.
   - Sets the Redis password and `replicaservestaledata` to `nil`.
   - Sets the Redis PID directory to `/run/redis`.
   - Includes `redisio`; the referenced recipe is unavailable.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes `redisio::enable`; the referenced recipe is unavailable.
   - Direct resources declared in the supplied recipe are:
     - `directory[/var/log/redis]`
     - `ruby_block[fix_redis_config]`
   - The supplied execution tree does not confirm a direct `group[redis]` resource. The Redis user and group remain prerequisites for the log directory and must be created by the resolved Redis installation implementation.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Configures the named instance `memcached` with:
     - Memory: `64`
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - User: `service_user`
     - Threads: `node['memcached']['threads']`, not defined in the supplied default attributes
     - Experimental options: empty list
     - Additional CLI options: empty list
     - Ulimit: `1024`
     - Actions: start and enable
   - The Ansible implementation must install the verified `memcached` package, configure the values above, and start and enable the Memcached service.
   - Supporting package-recipe details for the Memcached user, group, log directory, and runtime directory are not treated as independently executed steps because `recipes/_package.rb` is not present in the supplied file listing.

3. **`redisio`** (recipe file unavailable):
   - The entry recipe includes `redisio` after assigning Redis attributes.
   - The Ansible implementation must provide or obtain the missing Redis installation behavior.
   - Required outcomes are:
     - Redis configured on port `6379`.
     - PID directory set to `/run/redis`.
     - Authentication password configured securely.
     - `/var/log/redis` created as `redis:redis` with mode `0755`.
     - `/etc/redis/6379.conf` modified to remove the five specified directive families.
   - Do not assume an exact Redis package name, package version, template, service unit, or installation path beyond the explicitly supplied paths.

4. **`directory[/var/log/redis]`** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis` recursively.
   - Sets owner `redis`.
   - Sets group `redis`.
   - Sets mode `0755`.
   - The Redis user and group must exist before this task runs.

5. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Reads the complete file when present.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified file back.
   - The Ansible equivalent should use a prior `stat` check and a guarded `replace` task.
   - The Chef resource does not declare a service notification.

6. **`redisio::enable`** (recipe file unavailable):
   - Intended to enable Redis at boot.
   - The Ansible implementation must enable the resolved Redis systemd service after installation and configuration.
   - The exact Redis service unit name must be confirmed on the target host or from the missing cookbook.

## Attributes

The supplied Memcached default attributes are:

| Attribute | Value |
|---|---:|
| `node['memcached']['version']` | `nil` |
| `node['memcached']['memory']` | `64` |
| `node['memcached']['port']` | `11211` |
| `node['memcached']['udp_port']` | `11211` |
| `node['memcached']['listen']` | `0.0.0.0` |
| `node['memcached']['maxconn']` | `1024` |
| `node['memcached']['max_object_size']` | `1m` |
| `node['memcached']['experimental_options']` | `[]` |
| `node['memcached']['extra_cli_options']` | `[]` |
| `node['memcached']['ulimit']` | `1024` |
| `node['memcached']['logfilepath']` | `/var/log/memcached` |

The Redis values assigned by `cookbooks/cache/recipes/default.rb` are:

| Attribute | Value |
|---|---|
| `node['redisio']['servers']` | One server entry |
| Redis server port | `6379` |
| Redis `requirepass` | `redis_secure_password_123` |
| Redis `replicaservestaledata` | `nil` |
| `node['redisio']['base_piddir']` | `/run/redis` |

These values are taken from the supplied recipe and attributes content. The password must not be copied as plaintext into the Ansible implementation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- `memcached`
- Redis package: unspecified because the `redisio` recipe is unavailable

**Service dependencies**:

- Memcached service, started and enabled by `memcached_instance[memcached]`
- Redis service, enabled through the unavailable `redisio::enable` recipe

**Supported platforms declared by metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The Ansible role must account for platform-specific Redis package and service naming.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded Chef attribute
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the server listening on port `6379`
- **Migration handling**: Store the password in Ansible Vault or an AAP credential/secret integration and render it with restrictive permissions. Do not commit the plaintext value to the Ansible role or variables.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, or external secret-manager URL was detected.

No SSL/TLS certificate, private key, database connection string, API key, or environment-variable secret reference was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

The exact Redis data directory and Redis log file are not supplied and must not be assumed.

**Service endpoints to check**:

- Memcached `memcached`: TCP `0.0.0.0:11211`
- Memcached `memcached`: UDP `0.0.0.0:11211`
- Redis server on port `6379`: TCP port `6379`
- Redis Unix socket: None specified

**Templates rendered**:

- None; no templates are listed or rendered.

**Configuration transformations**:

- Redis configuration is modified once by `fix_redis_config`.
- The five named Redis directive families must be absent after migration.
- Redis authentication must be configured from a protected secret source.

## Pre-flight checks

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'

printf "version\r\n" | nc -w 2 127.0.0.1 11211
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
lsof -iTCP:11211 -sTCP:LISTEN

grep -R -E -- '-m 64|-p 11211|-U 11211|-l 0.0.0.0|-c 1024' \
  /etc/memcached.conf /etc/default/memcached /etc/sysconfig/memcached 2>/dev/null

stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached

# Redis instance: port 6379
systemctl list-unit-files | grep -E 'redis|redis-server'
systemctl status <resolved-redis-service>
systemctl is-enabled <resolved-redis-service>
systemctl is-active <resolved-redis-service>

ss -ltnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN
ps aux | grep '[r]edis'

test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|pidfile|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf

! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

test -d /run/redis
stat -c '%A %U:%G %n' /run/redis

test -d /var/log/redis
stat -c '%A %U:%G %n' /var/log/redis

# Use the Ansible Vault-provided password without committing or logging it.
REDISCLI_AUTH='<vault-provided-password>' redis-cli -h 127.0.0.1 -p 6379 PING

# Confirm unauthenticated access is rejected.
redis-cli -h 127.0.0.1 -p 6379 PING

journalctl -u <resolved-redis-service> --no-pager -n 100
journalctl -u <resolved-redis-service> --no-pager -n 100 | grep -iE 'error|fatal|warning'

# General checks
systemctl --failed
df -h /var/log/redis
df -h /run/redis
```

Expected results:

- The `memcached` service is active and enabled.
- Memcached listens on TCP and UDP port `11211` with the intended `0.0.0.0` binding.
- Memcached uses 64 MB memory and 1,024 maximum connections.
- `/var/log/memcached` and `/var/run/memcached` exist with the Memcached service ownership.
- The resolved Redis service is active and enabled.
- Redis listens on TCP port `6379`.
- `/etc/redis/6379.conf` exists and contains the required port configuration.
- The five obsolete or incompatible Redis directive families are absent.
- `/run/redis` exists.
- `/var/log/redis` exists with owner `redis:redis` and mode `0755`.
- Authenticated Redis access returns `PONG`.
- Unauthenticated Redis access is rejected.
- No related systemd units are failed and the relevant filesystems have sufficient space.