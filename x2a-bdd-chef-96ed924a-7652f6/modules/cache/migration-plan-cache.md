---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance identified by port `6379`. Memcached is started and enabled through the `memcached_instance` custom resource. Redis is configured with password authentication, uses `/run/redis` for its PID directory, creates `/var/log/redis`, removes five replication-related directives from `/etc/redis/6379.conf`, and is enabled through `redisio::enable`. The supplied execution tree does not include the `redisio` recipes or the Memcached custom-resource provider, so their exact package names, service names, configuration paths, and provider behavior must be verified before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached cache service
  - Location/Path: Configuration path is not confirmed because the `memcached_instance` provider is unavailable. The configured log path attribute is `/var/log/memcached`.
  - Port/Socket: TCP `11211`; UDP `11211`
  - Key Config: Memory `64` MB; listen address `0.0.0.0`; maximum connections `1024`; maximum object size `1m`; service user `service_user`; `ulimit` `1024`; empty experimental and extra CLI option lists; threads value is sourced from `node['memcached']['threads']` but is not defined in the supplied attribute file; no explicit version is selected.

- **`6379`**: Redis server instance
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is configured; the Chef value is `redis_secure_password_123`; `replicaservestaledata` is initially `nil` and is removed by the configuration cleanup block. Redis bind address and exact service name are not confirmed because the `redisio` dependency is unavailable.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb

Providers:
No provider path supplied for memcached_instance.

Templates:
No templates shown as rendered.

Attributes:
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

Files:
No static files shown as deployed.

Unavailable dependency files:
redisio recipe file
redisio::enable recipe file
memcached_instance provider implementation
```

The structured analysis reports seven analyzed files, but the supplied inventory identifies only the files and unavailable dependency artifacts listed above. The remaining analyzed files must be reconciled against the source checkout before migration completion.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Assigns the Redis server collection containing exactly one item, `6379`.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive directory creation.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes the unavailable `redisio::enable` recipe.

2. **`default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates `memcached_instance['memcached']`.
   - Applies the actions `start` and `enable`.
   - Sources configuration from `node['memcached']`.
   - Configures memory `64` MB, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, user `service_user`, `ulimit` `1024`, empty experimental options, and empty extra CLI options.
   - Sources the threads value from `node['memcached']['threads']`; no value is defined in the supplied attribute file.
   - Uses no explicit version because the configured version is `nil`.
   - Requires provider verification before selecting the package name, service name, configuration path, or exact handling of the `threads` setting.

3. **Redis server assignment** (`cookbooks/cache/recipes/default.rb`):
   - Assigns one Redis server item:
     - Instance identifier: `6379`
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets the Redis base PID directory to `/run/redis`.
   - Does not use an iteration over the server collection.
   - Requires verification of the unavailable `redisio` dependency before selecting package, service, repository, or template details.

4. **`redisio`** (`redisio/recipes/default.rb`, unavailable):
   - The dependency recipe is not present in the execution tree.
   - The migration must provide one Redis server on port `6379`.
   - The migration must provide `/run/redis` as the PID directory and `/etc/redis/6379.conf` as the configuration path because the subsequent cleanup block operates on that path.
   - The Redis package and service name must be discovered from the dependency source or target distribution.

5. **`directory[/var/log/redis]`** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Sets owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - This directory must exist before Redis writes logs there.

6. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Operates on `/etc/redis/6379.conf`.
   - Makes no change when the file does not exist.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified content back to the same file.
   - The Ansible implementation should use conditional `ansible.builtin.replace` tasks or an equivalent controlled template.
   - Redis should be restarted or notified only when the effective configuration changes.

7. **`redisio::enable`** (`redisio/recipes/enable.rb`, unavailable):
   - The dependency recipe is not present in the execution tree.
   - The intended operation is to enable and start the Redis instance at boot.
   - The actual service name must be discovered; it may be an instance-specific unit associated with port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package: required, but the exact package name is not available from the supplied provider analysis.
- Redis package: required, but the exact package name is not available from the supplied `redisio` analysis.
- No additional system package is explicitly visible in the supplied recipes.

**Service dependencies**:

- Memcached instance `memcached`, started and enabled by `memcached_instance['memcached']`
- Redis instance `6379`, enabled by the unavailable `redisio::enable` recipe

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in a Chef attribute assignment
- **Usage context**: Redis password authentication for instance `6379`
- **Migration handling**: Store the value in Ansible Vault, AAP credentials, or an approved secret-management system. Do not commit the literal value to the Ansible role. Use `no_log: true` where appropriate.

No data bag, encrypted data bag, Chef Vault item, Conjur variable, CyberArk data bag, environment-variable secret, TLS certificate, private key, or database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`
- `/var/log/memcached`
- The Memcached configuration file identified by the provider replacement
- The Redis service unit identified from the `redisio` replacement

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `11211`, UDP `11211`, listen address `0.0.0.0`
- Redis instance `6379`: TCP `6379`
- Redis bind address: discover from the `redisio` replacement
- Unix sockets: none specified

**Templates rendered**:

- None shown in the supplied execution tree; render count `0`

**Configuration transformations to verify**:

- Memcached instance `memcached` starts and is enabled.
- Memcached uses the configured memory, ports, listen address, maximum connections, object size, user, and `ulimit`.
- Redis instance `6379` requires authentication.
- Redis instance `6379` uses `/run/redis` for PID files.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- The five specified replication-related directives are absent from `/etc/redis/6379.conf`.

## Pre-flight checks

Run these checks after the Ansible migration. Replace placeholder service and configuration names with the values discovered from the unavailable dependency implementations.

### Memcached instance `memcached`

```bash
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>

ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'

printf "version\r\n" | nc -w 2 127.0.0.1 11211
```

Expected results:

- The Memcached service is enabled and active.
- TCP port `11211` is listening.
- UDP port `11211` is listening.
- The version command returns a `VERSION` response.

Verify the configured values using the provider-confirmed configuration path:

```bash
grep -E '(^-m[[:space:]]+64|^-p[[:space:]]+11211|^-U[[:space:]]+11211|^-l[[:space:]]+0\.0\.0\.0|-c[[:space:]]+1024)' <memcached-config-path>
ps -ef | grep '[m]emcached'
```

Confirm the process uses memory `64` MB, TCP and UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, the intended service user, and the verified threads value.

### Redis instance `6379`

```bash
systemctl status <redis-6379-service-name>
systemctl is-enabled <redis-6379-service-name>
systemctl is-active <redis-6379-service-name>

ss -tlnp | grep ':6379'
test -f /etc/redis/6379.conf
test -d /run/redis
```

Verify authentication using a secret supplied from Ansible Vault:

```bash
redis-cli -p 6379 -a '<password-from-Ansible-Vault>' PING
```

Expected result:

```text
PONG
```

Verify unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication-required error.

Verify the Redis configuration:

```bash
grep -E '^requirepass[[:space:]]+' /etc/redis/6379.conf
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

The first command must show password authentication. The second command must return no matching lines.

### Redis log directory

```bash
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis
```

Expected result:

```text
drwxr-xr-x redis redis /var/log/redis
```

### Final service verification

```bash
systemctl --failed
systemctl is-active <memcached-service-name>
systemctl is-active <redis-6379-service-name>
```

The `memcached` and `6379` instances must both report `active`, and no failed systemd unit may be attributable to the migration.