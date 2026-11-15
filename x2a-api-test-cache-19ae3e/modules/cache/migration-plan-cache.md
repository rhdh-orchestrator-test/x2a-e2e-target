---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` on TCP and UDP port `11211` and one Redis instance named `6379` on TCP port `6379`. The supplied execution tree confirms the Memcached custom-resource invocation, Redis log-directory creation, Redis configuration cleanup, and Redis enablement references. Memcached defaults and Redis settings are present in the supplied source files, while the Memcached provider implementation and Redis dependency recipes are not included and require confirmation before finalizing account, package, service-unit, configuration-owner, and log-file details.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached caching service
  - Location/Path: `/var/run/memcached`; log path `/var/log/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: Memory `64` MB; maximum connections `1024`; maximum object size `1m`; ulimit `1024`; experimental options `[]`; additional CLI options `[]`; actions `start` and `enable`
  - Package: `memcached`
  - Threads: `node['memcached']['threads']`; no default value is present in the supplied attribute file
  - Service account: `service_user`; concrete username and group require confirmation from the unavailable custom-resource provider
  - Additional source-defined behavior requiring provider confirmation: `/nonexistent` home, `/bin/false` shell, locked account, `Memcached` comment, `service_group`, and `/var/run/memcached` runtime-directory handling

- **6379**: Redis caching service
  - Location/Path: Configuration file `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; bind address is not specified
  - Key Config: `requirepass` set in the supplied source to `redis_secure_password_123`; `replicaservestaledata` assigned `nil`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` lines when `/etc/redis/6379.conf` exists
  - Log directory: Owner `redis`, group `redis`, mode `0755`, recursive directory resource
  - Enablement: Requested through `redisio::enable`
  - Package and service unit: Not determinable because the supplied `redisio` recipe files are unavailable

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

No provider path was supplied for `memcached_instance[memcached]`. The Ansible migration must reproduce the observable behavior of this custom resource without assuming an unavailable provider implementation.

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

No static files are deployed by `cookbook_file` or `remote_file` resources.

The structured execution listing supplies three concrete file paths, although the analysis reports seven files in total. The remaining four analyzed files are not enumerated in the supplied listing and must be identified before claiming complete seven-file migration coverage.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe at `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Defines one Redis server collection item named `6379`.
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes the `redisio` dependency.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive behavior.
   - Executes `ruby_block[fix_redis_config]` to modify `/etc/redis/6379.conf` when the file exists.
   - Includes `redisio::enable` to request Redis boot enablement.
   - The exact Redis dependency recipe and service implementation are unavailable in the supplied execution tree.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes exactly one custom resource: `memcached_instance[memcached]`.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental options, and empty extra CLI options.
   - Requests `start` and `enable` actions.
   - Uses `node['memcached']['threads']`, `service_user`, and `service_group`, whose concrete values are not defined in the supplied attribute file.
   - The provider path and underlying account, directory, and service resources are unavailable; those resulting states require confirmation before implementation.

3. **Redis server collection item `6379`** (`cookbooks/cache/recipes/default.rb`):
   - Sets port `6379`.
   - Sets `requirepass` to the source value `redis_secure_password_123`.
   - Sets `replicaservestaledata` to `nil`.
   - Uses `/run/redis` as the Redis PID base directory.
   - The collection contains exactly one Redis item; no additional Redis instances are configured.

4. **`redisio` dependency include** (referenced by `cookbooks/cache/recipes/default.rb`):
   - The dependency recipe is not present in the supplied execution tree.
   - Known inputs are one Redis server on port `6379`, password authentication, and PID base directory `/run/redis`.
   - The Redis package name, configuration template, service unit, configuration ownership, and provider behavior require confirmation from the actual `redisio` cookbook.

5. **`directory[/var/log/redis]`** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Sets owner `redis`, group `redis`, and mode `0755`.
   - Uses recursive directory behavior.
   - Execution-tree coverage confirms one directory resource; the detailed properties require source-property confirmation if not otherwise available.

6. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Removes lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Does not require the task to fail when the file is absent.
   - The execution tree confirms one Ruby block; the path and expressions require confirmation from detailed resource-property analysis if unavailable.
   - No explicit service notification is present in the supplied recipe.

7. **`redisio::enable`** (referenced by `cookbooks/cache/recipes/default.rb`):
   - Requests Redis enablement at boot.
   - The recipe file and exact service resource are unavailable.
   - The Ansible implementation must discover and confirm the Redis service unit before enabling it.

No `.each` loops are present in the supplied execution analysis. The only collection item requiring expansion is Redis server `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- `memcached`
- Redis package: not identified in the supplied execution tree; determine from the actual `redisio` cookbook before implementation

**Service dependencies**:

- Memcached service, requested to start and enable through `memcached_instance[memcached]`
- Redis service for instance `6379`, intended to be enabled through `redisio::enable`
- Exact Redis service unit name is unavailable

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 hardcoded credential observed in 1 source file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for instance `6379`
- **Migration handling**: Store the value in Ansible Vault or an AAP credential-backed variable. Do not commit the plaintext password to defaults or vars files.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secrets, TLS certificates, private keys, database connection strings, or API tokens were identified in the supplied files.

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

The analysis reports four additional analyzed files that are not enumerated in the supplied directory listing. Identify those files before final migration sign-off.

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis instance `6379`: TCP port `6379`; bind address unspecified
- Redis PID directory: `/run/redis`
- Memcached runtime directory: `/var/run/memcached`

**Templates rendered**:

- None rendered: `0`

**Configuration transformations**:

- `/etc/redis/6379.conf` is modified in place when present.
- Five replication-related directive classes are removed.

## Pre-flight checks

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
pgrep -a memcached
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
ls -ld /var/run/memcached
ls -ld /var/log/memcached
getent passwd service_user
getent group service_group
stat -c '%U:%G %a %n' /var/run/memcached /var/log/memcached
printf "version\r\n" | nc -w 2 127.0.0.1 11211

# Expected Memcached response:
# VERSION <version>

# Redis instance: 6379
# Replace redis-service-name with the service unit confirmed from redisio.
systemctl status redis-service-name
systemctl is-enabled redis-service-name
systemctl is-active redis-service-name
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|pidfile|logfile|bind)' /etc/redis/6379.conf
! grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis
ls -ld /run/redis
ss -tlnp | grep ':6379'

# Test Redis authentication without exposing the password in shell history.
read -s REDIS_PASSWORD
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning PING
unset REDIS_PASSWORD

# Expected result:
# PONG

read -s REDIS_PASSWORD
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning INFO server | grep '^redis_version:'
unset REDIS_PASSWORD

# Service logs
journalctl -u redis-service-name --since "15 minutes ago" --no-pager
journalctl -u memcached --since "15 minutes ago" --no-pager

# Filesystem capacity
df -h /var/log/redis /var/log/memcached

# Confirm no unwanted Redis directives remain.
grep -nE 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority' /etc/redis/6379.conf
# Expected result: no output
```

Use the concrete Memcached service account and group resolved from the custom-resource provider if they differ from `service_user` and `service_group`. Confirm the Redis package, service unit, configuration ownership, and exact log-file path from the `redisio` implementation before deploying the final Ansible role.