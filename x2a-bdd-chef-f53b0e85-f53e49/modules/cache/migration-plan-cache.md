---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a Redis cache instance on port `6379` and references an external Memcached dependency. The available recipe is `cache::default`, which includes `memcached`, configures one Redis server entry, sets the Redis PID directory to `/run/redis`, includes `redisio`, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. Detailed resource attributes, Redis values, and credential findings require verification against the complete recipe analysis because they are not present in the supplied structured validation summary.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port `6379`**: Redis cache instance configured by `cache::default`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication is reported as enabled; `replicaservestaledata` is reported as `nil`; PID directory is reported as `/run/redis`; log directory is `/var/log/redis`
  - Verification status: Port, authentication, PID directory, and password values require confirmation from the detailed recipe analysis

No explicit instance name is defined in the available recipe. The instance is identified by its Redis port, `6379`.

Memcached is referenced through the external `memcached` cookbook, but no Memcached instance, port, package, configuration file, or service resource is visible in the supplied cookbook tree.

## File Structure

Only the recipe file shown in the supplied execution tree is included.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
None reported in the supplied execution tree; complete-tree verification required
```

**Templates:**
```text
None reported in the supplied execution tree; complete-tree verification required
```

**Attributes:**
```text
None reported in the supplied execution tree; complete-tree verification required
```

**Files:**
```text
None reported in the supplied execution tree; complete-tree verification required
```

The following referenced recipe files are external dependencies and are not present in this cookbook tree:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The external recipe is not present in the supplied tree, so its package, configuration, service, and port behavior cannot be enumerated from this cookbook.
   - Assigns one reported Redis server configuration to `node['redisio']['servers']`:
     - Redis entry on port `6379`
     - `requirepass`: reported as `redis_secure_password_123`
     - `replicaservestaledata`: reported as `nil`
   - Sets the reported Redis PID directory attribute `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the external `redisio` recipe.
   - Creates `/var/log/redis`, reportedly with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation enabled
   - Runs `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes complete lines matching:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified Redis configuration back to `/etc/redis/6379.conf`.
   - Includes the external `redisio::enable` recipe to enable Redis at boot.
   - The detailed directory-resource properties, Redis attribute assignments, and Ruby block behavior require confirmation from the complete recipe analysis because the supplied structured validation summary confirms only the resource and include names.

There is no Chef `.each` loop in the available recipe. The configured Redis collection contains one reported item: the Redis entry on port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**System package dependencies**:

- None directly declared or verifiable in the available recipe
- Packages installed by the external `memcached` and `redisio` cookbooks must be determined from those cookbooks

**Service dependencies**:

- Redis service, intended to be enabled through the external `redisio::enable` recipe
- Memcached service behavior referenced through the external `memcached` recipe
- Exact service unit names require verification on the target host

## Credentials

**Detection Summary**: 1 credential reported in 1 file; the finding requires confirmation from the complete credential analysis.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext value
- **Reported current value**: `redis_secure_password_123`
- **Usage context**: Redis password authentication for the Redis server on port `6379`
- **Verification status**: The supplied structured validation summary does not include recipe contents or credential findings; confirm the value and usage before migration

Store the migrated password in Ansible Vault rather than a regular variable file:

```yaml
redis_password: !vault |
  ...
```

Reference it from the Redis configuration:

```yaml
redisio_servers:
  - port: 6379
    requirepass: "{{ redis_password }}"
    replicaservestaledata: null
```

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, database credentials, or external secret-manager URLs were identified in the supplied analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`

**Configuration directives to verify as absent from `/etc/redis/6379.conf`**:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Unix sockets: none configured or referenced by the available recipe
- Network bind address: not specified by the available recipe
- Memcached endpoint: not determinable from the available cookbook tree

**Templates rendered**:

- None reported; complete-tree verification required

**Configuration modifications**:

- `/etc/redis/6379.conf` is reportedly edited in place by `ruby_block[fix_redis_config]`
- No full-template replacement is reported

## Pre-flight checks

```bash
# Verify the source recipe and confirm reported attributes/resources
sed -n '1,240p' cookbooks/cache/recipes/default.rb

# Confirm the Redis runtime directory for the Redis instance on port 6379
ls -ld /run/redis
stat -c '%U:%G %a %n' /run/redis

# Confirm the Redis log directory for the Redis instance on port 6379
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis

# Confirm the Redis configuration for the Redis instance on port 6379
test -f /etc/redis/6379.conf
ls -l /etc/redis/6379.conf

# Verify that the Redis instance is listening on TCP port 6379
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'

# Discover the actual Redis service unit supplied by the external redisio cookbook
systemctl list-units --type=service | grep -i redis

# Check the discovered Redis service unit
systemctl status redis --no-pager

# Verify that the configured directives were removed for the Redis instance on port 6379
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || true

# Inspect relevant configuration for the Redis instance on port 6379
grep -nE '^(port|requirepass|pidfile|dir|logfile|bind|protected-mode)' \
  /etc/redis/6379.conf

# Authenticate to the Redis instance on port 6379 without placing the password in shell history
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379 PING

# Verify authenticated Redis server access on port 6379
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379 INFO server

# Review Redis service logs using the discovered service unit
journalctl -u redis --no-pager -n 100

# If the configuration specifies file logging, identify and inspect the configured path
grep -n '^logfile' /etc/redis/6379.conf
```

The Redis service unit may have a name other than `redis`; use the exact unit reported by `systemctl list-units`. The Redis password, directory-resource properties, and configuration-cleanup behavior must be confirmed against the complete source analysis before deployment.