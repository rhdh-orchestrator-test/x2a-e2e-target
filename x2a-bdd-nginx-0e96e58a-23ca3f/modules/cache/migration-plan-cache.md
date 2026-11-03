---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook is intended to configure Redis and Memcached, but the supplied execution tree contains only `cookbooks/cache/recipes/default.rb`. The recipe includes `memcached`, `redisio`, and `redisio::enable`, although those recipe files are unavailable. The analyzed resources are one directory resource for `/var/log/redis` and one `ruby_block` named `fix_redis_config`. Redis port, password, configuration-path, directory properties, and cleanup directives are reported by the original plan but are not confirmed by the available structured validation and must be verified before implementation. The migration should preserve the observed recipe order and replace any hardcoded credential with Ansible Vault if confirmed.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Intended Redis cache instance; configuration details are reported by the original plan but are not confirmed by the supplied structured analysis.
  - Location/Path: Reported as `/etc/redis/6379.conf`; unverified
  - Port/Socket: TCP `6379`; unverified
  - Key Config: Redis authentication and replication-related configuration were reported but are unverified. The intended service enablement is `redisio::enable`.
- **Memcached**: Declared as a cookbook dependency and included by the recipe, but no Memcached instance, configuration, port, package, or service was confirmed.
  - Location/Path: Not available
  - Port/Socket: Not available
  - Key Config: No explicit Memcached configuration is present in the analyzed execution tree

No Chef `.each` loop or resource iteration is present. No additional configured instance names were identified.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

No provider, template, attribute, or static file is shown as used by the execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - The execution tree reports that the `memcached` recipe file is not found.
   - The original plan reports an assignment of one Redis server definition on port `6379`, including `requirepass` and `replicaservestaledata`; these attribute assignments are not confirmed by the supplied structured analysis.
   - Creates `directory[/var/log/redis]`.
   - The analyzed resource count is one directory resource. Ownership, group, mode, and recursive-creation properties were not provided by validation.
   - Attempts to include the external `redisio` recipe.
   - The execution tree reports that the `redisio` recipe file is not found.
   - Executes `ruby_block[fix_redis_config]`.
   - The analyzed resource count is one Ruby block. Its target file, conditional behavior, and directive-removal patterns are not provided by validation and must be confirmed from the recipe before migration.
   - Attempts to include `redisio::enable`.
   - The execution tree reports that the `redisio::enable` recipe file is not found.
   - Preserve this ordering in Ansible: external-recipe checks, Redis attribute/configuration handling if confirmed, log-directory creation, Redis configuration, cleanup block behavior if confirmed, and service enablement.

**Iterations**: No `.each` loops are present. No loop items require expansion.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint
- `redisio::enable` is included by the recipe but is not separately listed as a metadata dependency

The corresponding recipe files are unavailable in the supplied execution tree.

**System package dependencies**:

- None verified
- No package name or version is present in the analyzed recipe

**Service dependencies**:

- Intended Redis service, reportedly configured on port `6379`; port and service name are unverified
- Memcached is declared and included, but no executable Memcached recipe or service configuration is available
- Exact Redis and Memcached service names are not shown

## Credentials

**Detection Summary**: 1 hardcoded credential reported in 1 file; detection is unverified by the supplied structured analysis.

**Source**:

- **Provider**: Reported as hardcoded in the Chef recipe; unverified
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: Reported as `node['redisio']['servers'][0]['requirepass']`; unverified
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as a hardcoded value; unverified
- **Current value**: Reported as `redis_secure_password_123`; unverified
- **Usage context**: Reported as Redis authentication for the intended instance on port `6379`; unverified

If confirmed, replace the hardcoded value with an Ansible Vault variable, render it with restrictive permissions, and use `no_log: true` on tasks that could expose it. No Chef data bags, encrypted data bags, Chef Vault, external secret provider, TLS certificate references, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf` — reported by the original plan but unverified

**Service endpoints to check**:

- Redis TCP port `6379` — reported but unverified
- Memcached endpoint — not available from the supplied execution tree
- Unix sockets: none specified

**Templates rendered**:

- None
- Render count: `0`

**Resources to verify**:

- `directory[/var/log/redis]` — confirmed, count `1`
- `ruby_block[fix_redis_config]` — confirmed, count `1`
- Includes for `memcached`, `redisio`, and `redisio::enable` — confirmed as attempted, with recipe files missing

**Configuration cleanup to verify**:

The original plan reports that the following directives are removed from `/etc/redis/6379.conf`, but validation did not confirm this behavior:

```text
replica-serve-stale-data
replica-read-only
repl-ping-replica-period
client-output-buffer-limit
replica-priority
```

## Pre-flight checks

```bash
# Confirm the available cookbook files and missing external recipes.
test -f cookbooks/cache/recipes/default.rb
find cookbooks -path '*/recipes/memcached.rb' -o \
             -path '*/recipes/redisio.rb' -o \
             -path '*/recipes/redisio/enable.rb'

# Confirm candidate Redis service names on the target host.
systemctl list-unit-files | grep -E 'redis|redis-server'

# Redis instance: port 6379, if confirmed by recipe inspection and deployment requirements.
systemctl status redis
systemctl status redis-server
ps aux | grep '[r]edis'
ss -tlnp | grep ':6379'
test -f /etc/redis/6379.conf

# Verify the reported Redis configuration only after confirming the path and port.
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Verify the reported cleanup behavior only after confirming fix_redis_config.
! grep -E '^replica-serve-stale-data' /etc/redis/6379.conf
! grep -E '^replica-read-only' /etc/redis/6379.conf
! grep -E '^repl-ping-replica-period' /etc/redis/6379.conf
! grep -E '^client-output-buffer-limit' /etc/redis/6379.conf
! grep -E '^replica-priority' /etc/redis/6379.conf

# Verify the analyzed Redis log directory resource.
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis

# Test Redis authentication only if requirepass and the password are confirmed.
read -s REDISCLI_AUTH
export REDISCLI_AUTH
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
unset REDISCLI_AUTH

# Review logs using the service name confirmed on the target host.
journalctl -u redis --no-pager -n 100
journalctl -u redis-server --no-pager -n 100
```

Do not run both `redis` and `redis-server` service commands in production unless both units are confirmed to exist.

**Memcached instance**:

No Memcached package, port, configuration file, service resource, or health check can be derived from the supplied execution tree. If Memcached is required, confirm its package, service name, port, configuration path, and endpoint before adding Ansible tasks.