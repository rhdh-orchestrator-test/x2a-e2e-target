---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook executes a Memcached dependency recipe and Redis-related operations. The execution flow confirms a `memcached_instance[memcached]` resource, creation of `/var/log/redis`, a `fix_redis_config` Ruby block, and an unavailable `redisio::enable` recipe. The supplied plan reports one Memcached instance named `memcached` on TCP/UDP port `11211` and one Redis instance on port `6379`; however, the detailed resource properties, Redis assignments, credentials, provider behavior, and package/service implementations require verification from the source files or target platform before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache instance
  - Location/Path: `/var/log/memcached`, `/var/run/memcached`
  - Port/Socket: TCP/UDP `11211`
  - Key Config: The `memcached_instance[memcached]` custom resource is executed. The supplied plan reports 64 MB memory, wildcard listening on `0.0.0.0`, 1,024 maximum connections, 1 MB maximum object size, 1,024 ulimit, empty experimental and extra CLI option arrays, and `start`/`enable` actions. These properties and provider-defined paths, users, groups, and defaults require source or implementation-time verification. The `threads` value is referenced but has no supplied default.

- **redis-6379**: Redis server instance
  - Location/Path: `/etc/redis/6379.conf`, `/run/redis`, `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: The supplied plan reports `requirepass` authentication, a password value of `redis_secure_password_123`, PID base directory `/run/redis`, and removal of selected replication-related directives. The Redis server collection, password, PID path, configuration path, and directive patterns require verification from `cookbooks/cache/recipes/default.rb`. The `redisio` and `redisio::enable` recipes are unavailable in the supplied execution tree.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Paths are relative to the repository root and retain the required `migration-dependencies/` prefix.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider file path was supplied in the execution tree. The `memcached_instance[memcached]` custom resource is executed, but its provider implementation is not present in the supplied file list.

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

The supplied directory also contains the following non-executed or unavailable recipe files, which are intentionally not included in the execution file list:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

These files are not included in the execution flow and must not be implemented as part of this cookbook migration.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached default recipe.
   - Assigns Redis server configuration and the Redis PID base directory; the exact assignments require source verification.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis`; the execution analysis confirms the directory resource, but ownership, group, mode, and recursive settings require source verification.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes the unavailable `redisio::enable` recipe.
   - No `.each` loop is reported. The supplied plan describes one Redis server definition on port `6379`; confirm this collection directly in the recipe before implementation.

2. **Memcached dependency recipe** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Executes `memcached_instance[memcached]`.
   - The supplied plan reports the following intended properties: 64 MB memory, TCP/UDP port `11211`, listen address `0.0.0.0`, 1,024 maximum connections, 1 MB maximum object size, `service_user`, empty experimental and extra CLI option arrays, and 1,024 ulimit.
   - The recipe references `node['memcached']['threads']`; no default value is present in the supplied attribute summary.
   - Actions are reported as `start` and `enable`.
   - The provider implementation is absent. Do not infer package, service, user, group, log directory, runtime directory, or effective default behavior without provider or target-platform verification.
   - No `.each` loop is reported.

3. **Redis installation/configuration integration** (`cookbooks/cache/recipes/default.rb`):
   - Includes `redisio`, which is unavailable in the supplied execution tree.
   - Model the missing integration point as a migration prerequisite rather than inventing Redis package or service details.
   - Verify the intended Redis instance name, port `6379`, configuration file, authentication settings, and PID directory from the recipe.

4. **Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - The execution analysis confirms the directory resource.
   - Verify owner, group, mode, and recursive creation settings from the recipe.
   - Create the directory only after the Redis service account exists.

5. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Operates on `/etc/redis/6379.conf` only if the file exists, according to the supplied plan.
   - The plan reports removal of lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Verify the file path and patterns in the recipe before implementation.
   - Translate the behavior with scoped `lineinfile` tasks using `state: absent`, while preserving the no-op behavior when the file is absent.
   - Notify the Redis service only after confirming the target service unit and restart or reload behavior.

6. **Redis enable integration** (`cookbooks/cache/recipes/default.rb`):
   - Includes `redisio::enable` after the configuration cleanup.
   - The recipe is unavailable.
   - Verify the Redis package and systemd unit name on the target platform before enabling or starting the Redis instance on port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- The supplied plan identifies `memcached`, but the execution analysis does not expose a package resource. Verify this dependency before implementation.
- No Redis package name is confirmed because the `redisio` recipe is unavailable. Select the package according to the target distribution only after verification.

**Service dependencies**:

- `memcached_instance[memcached]`, with reported `start` and `enable` actions; provider behavior requires verification.
- Redis instance `redis-6379`, enabled through unavailable `redisio::enable`; the service unit must be discovered or confirmed on the target platform.

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential is reported in 1 source file, but the supplied structured analysis does not independently expose the recipe contents or confirm credential detection.

**Source**:

- **Provider**: Reported hardcoded Chef attribute assignment; source verification required
- **URL**: None detected
- **Path**: Reported Redis configuration for port `6379`

### Redis authentication password

- **Variable**: Reported as `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext value; source verification required
- **Value currently present**: `redis_secure_password_123`
- **Usage context**: Reported Redis `requirepass` authentication for Redis instance `redis-6379`
- **Ansible migration**: Store the confirmed value in Ansible Vault, such as `vault_redis_password`, and render it with restrictive permissions. Do not commit plaintext credentials to the role, inventory, or defaults.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database connection strings, or other credential sources were reported.

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

- Memcached `memcached`: TCP `0.0.0.0:11211`
- Memcached `memcached`: UDP `0.0.0.0:11211`
- Redis `redis-6379`: TCP `6379`
- Unix sockets: none reported

**Templates rendered**:

- None; render count: `0`

**Configuration transformations**:

- Verify whether `/etc/redis/6379.conf` exists.
- If confirmed by the recipe, remove the five reported directive families:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

### Memcached instance `memcached`

```bash
# Service discovery and status
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Verify the process and TCP/UDP endpoints
ps aux | grep '[m]emcached'
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'

# Verify reported directories if confirmed during implementation
ls -ld /var/log/memcached
ls -ld /var/run/memcached

# Verify ownership and permissions after provider behavior is confirmed
stat -c '%U:%G %a %n' /var/log/memcached
stat -c '%U:%G %a %n' /var/run/memcached

# Memcached protocol checks
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
printf 'stats\r\n' | nc -w 2 127.0.0.1 11211
printf 'quit\r\n' | nc -w 2 127.0.0.1 11211
```

Expected results:

- The `memcached` service is active and enabled.
- TCP port `11211` is listening.
- UDP port `11211` is bound if enabled by the verified provider configuration.
- The version command returns a `VERSION` response.
- The stats command returns Memcached statistics.

### Redis instance `redis-6379`

```bash
# Discover the actual Redis unit before using service-specific commands
systemctl list-units --type=service | grep -i redis
systemctl list-unit-files | grep -i redis

# After identifying the unit, verify its status and enablement
systemctl status <verified-redis-unit>
systemctl is-enabled <verified-redis-unit>
systemctl is-active <verified-redis-unit>

# Verify the Redis process and port
ps aux | grep '[r]edis'
ss -ltnp | grep ':6379'

# Verify the reported PID directory
ls -ld /run/redis
stat -c '%U:%G %a %n' /run/redis

# Verify the reported configuration file
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|dir|pidfile)' /etc/redis/6379.conf

# Verify removal of the reported directive families
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || true

# Verify authentication using the vaulted password
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server | grep -E 'redis_version|tcp_port'
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET migration_check cache_ok
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET migration_check
redis-cli -p 6379 -a "$REDIS_PASSWORD" DEL migration_check
```

Expected results:

- The verified Redis service for `redis-6379` is active and enabled.
- Port `6379` is listening.
- `PING` returns `PONG` with the vaulted password.
- The temporary key returns `cache_ok`.
- The reported directive families are absent if their removal is confirmed in the recipe.

### Redis log directory for `redis-6379`

```bash
test -d /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis

# Replace with the verified Redis unit name
journalctl --no-pager -u <verified-redis-unit> -n 100
```

Verify the expected `redis:redis` ownership and `0755` mode only after confirming those values in the source recipe.

### Combined endpoint and service verification

```bash
# Confirm both named instances independently
ss -ltnp | grep -E ':(6379|11211)\b'
ss -lunp | grep ':11211'

journalctl --no-pager -u memcached -n 100
journalctl --no-pager -u <verified-redis-unit> -n 100
```

The migration must validate `memcached` separately on TCP/UDP `11211` and `redis-6379` separately on TCP `6379`.