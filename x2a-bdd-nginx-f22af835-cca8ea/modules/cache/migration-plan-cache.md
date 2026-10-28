---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer with one locally defined Redis instance on port `6379` and an included Memcached dependency. The local recipe creates `/var/log/redis`, assigns one Redis server definition with a hardcoded password, removes selected replication-related directives from `/etc/redis/6379.conf`, and attempts to include and enable Redis through the external `redisio` cookbook. The `memcached`, `redisio`, and `redisio::enable` recipes are unavailable in the analyzed cookbook tree, so their package names, service names, configuration paths, and endpoints cannot be verified from this cookbook alone.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config:
    - `requirepass`: hardcoded source-level value `redis_secure_password_123`; migrate to Ansible Vault
    - `replicaservestaledata`: `nil`
    - Log directory: `/var/log/redis`
    - Log directory owner: `redis`
    - Log directory group: `redis`
    - Log directory mode: `0755`
    - Replication-related directives removed:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`

- **Memcached dependency instance**: Included external dependency with no locally verifiable instance configuration
  - Location/Path: Not available from the analyzed files
  - Port/Socket: Not available from the analyzed files
  - Key Config: Package name, service name, port, and configuration path require analysis of the external `memcached` cookbook

## File Structure

The following is the complete locally analyzed directory listing. Dependency recipes were reported as unavailable and are not included as local files.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
None
```

**Templates:**
```text
None
```

**Attributes:**
```text
None
```

**Files:**
```text
None
```

## Module Explanation

The cookbook performs operations in the following execution order. The execution tree identifies `cache::default` as the only locally analyzed recipe. The `memcached`, `redisio`, and `redisio::enable` recipes are external and unavailable.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - Execution tree result: `memcached Recipe file not found`.
   - Creates `/var/log/redis` using `directory[/var/log/redis]`.
   - Sets the directory owner to `redis`, group to `redis`, mode to `0755`, and enables recursive creation according to the source-level recipe analysis.
   - Assigns exactly one Redis server definition to `node['redisio']['servers']`.
   - Iterates once for the Redis instance named **port 6379**:
     - `port`: `"6379"`
     - `requirepass`: `"redis_secure_password_123"`
     - `replicaservestaledata`: `nil`
   - Attempts to include the external `redisio` recipe.
   - Execution tree result: `redisio Recipe file not found`.
   - Creates `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, reads the file, removes lines matching the following expressions, and writes the modified content back:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - If `/etc/redis/6379.conf` does not exist, the cleanup makes no change.
   - Does not declare a service notification from `ruby_block[fix_redis_config]`.
   - Attempts to include the external `redisio::enable` recipe.
   - Execution tree result: `redisio::enable Recipe file not found`.
   - The exact Redis package, service resource, service name, templates, and enablement mechanism must be obtained from the external `redisio` cookbook.

**Locally confirmed resource summary:**
- `directory`: 1 resource, `/var/log/redis`
- `ruby_block`: 1 resource, `fix_redis_config`
- Included but unavailable recipes:
  - `memcached`
  - `redisio`
  - `redisio::enable`

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- No package resources are present in the analyzed execution tree.
- Package names cannot be determined because the external `memcached` and `redisio` recipes are unavailable.
- No unverified package name should be added to the migration.

**Service dependencies**:
- Redis enablement is intended through the unavailable `redisio::enable` recipe.
- The Redis service name is not available from the analyzed files.
- Memcached service management is not available from the analyzed files.

**Supported platforms declared by metadata**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value in the recipe
- **Value currently configured**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the Redis instance listening on TCP port `6379`
- **Migration handling**:
  - Store the password in Ansible Vault, such as `redis_password`.
  - Do not place the password directly in a public role or plaintext task.
  - Use the vaulted variable when rendering or configuring Redis.
  - Avoid exposing the password in shell history or process listings during validation.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, Conjur, CyberArk, Vault URL, environment-variable secret, TLS certificate, private key, API token, or database credential was detected.

The password, Redis attributes, directory properties, configuration path, and directive patterns are source-level findings from the detailed recipe analysis; they are not present in the supplied structured execution-tree summary.

## Checks for the Migration

**Files to verify**:
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:
- Redis instance on TCP port `6379`
- Memcached dependency instance: endpoint not determinable from the analyzed cookbook
- Unix sockets: none referenced
- Network bind address: not specified

**Templates rendered**:
- None; no templates are present

**Static files deployed**:
- None

## Pre-flight checks

### Redis instance on port 6379

```bash
# Determine the service name supplied by the redisio dependency
systemctl list-unit-files | grep -E 'redis|redis-server'

# Check the confirmed Redis endpoint after identifying the actual service unit
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Verify the Redis process
ps aux | grep '[r]edis-server'

# Use the Ansible Vault value for authentication
redis-cli -p 6379 -a '<redis_password>' PING
redis-cli -p 6379 -a '<redis_password>' INFO server
redis-cli -p 6379 -a '<redis_password>' CONFIG GET requirepass
```

Expected results:

- A Redis process listens on TCP port `6379`.
- `PING` returns `PONG`.
- `INFO server` returns Redis server information.
- `requirepass` is configured and is not empty.

```bash
# Verify the Redis configuration file and cleanup
test -f /etc/redis/6379.conf
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result: the five targeted directive types are absent from `/etc/redis/6379.conf`.

```bash
# Verify the Redis log directory
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis
```

Expected results:

- `/var/log/redis` exists.
- Owner is `redis`.
- Group is `redis`.
- Permissions are `0755`.

```bash
# Inspect Redis service logs after confirming the actual service name
journalctl -u redis --no-pager -n 50
journalctl -u redis-server --no-pager -n 50

# Inspect the configured log behavior
grep -nE '^(logfile|syslog-enabled|syslog-ident)' /etc/redis/6379.conf
```

### Memcached dependency instance

```bash
# The Memcached service name and endpoint are unavailable from this cookbook.
# Obtain and analyze the external memcached cookbook before running endpoint checks.
echo "Memcached endpoint and service checks require external cookbook analysis"
```

Do not assume a Memcached port, package name, service name, configuration path, or socket. Add an individually named Memcached service and endpoint check only after those values are obtained from the external `memcached` cookbook.

