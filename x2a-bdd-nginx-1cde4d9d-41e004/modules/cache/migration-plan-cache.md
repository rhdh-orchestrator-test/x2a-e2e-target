---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services intended to include Redis and Memcached. The only local recipe is `cache::default`, which attempts to include the unavailable `memcached`, `redisio`, and `redisio::enable` recipes. The local recipe configures one Redis instance on port `6379`, sets a hardcoded Redis password, creates `/var/log/redis`, and removes selected replication-related directives from `/etc/redis/6379.conf`. The Ansible migration must preserve the execution order, move the Redis password to an approved secret store, explicitly implement Redis package/configuration/service management, and resolve the unavailable external dependencies before deploying Memcached.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache and authentication-enabled service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`; no Unix socket identified
  - Key Config: Redis `requirepass` is configured; `replicaservestaledata` is `nil`
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Password in Chef source: `redis_secure_password_123`
  - Post-processing removes these directives from `/etc/redis/6379.conf` when present:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

**Memcached**:

- The recipe attempts to include the external `memcached` recipe.
- The execution tree reports `memcached Recipe file not found`.
- No Memcached port, package, configuration path, memory allocation, or service resource can be confirmed from the supplied cookbook.

## File Structure

Only files shown by the execution tree and directory listing are included.

```text
cookbooks/
└── cache/
    └── recipes/
        └── default.rb
```

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

External recipes referenced by the local recipe are unavailable and are not included in the directory listing:

- `memcached` — recipe file not found
- `redisio` — recipe file not found
- `redisio::enable` — recipe file not found

## Module Explanation

The cookbook performs operations in this exact order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include `memcached`; the external recipe is unavailable.
   - Assigns one Redis server configuration with port `6379`, Redis authentication, and `replicaservestaledata` set to `nil`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Attempts to include `redisio`; the external recipe is unavailable.
   - Executes `ruby_block[fix_redis_config]` to remove five directive types from `/etc/redis/6379.conf` if the file exists.
   - Attempts to include `redisio::enable`; the external recipe is unavailable.
   - Local resources:
     - `directory[/var/log/redis]`: 1
     - `ruby_block[fix_redis_config]`: 1
   - No local package, service, template, provider, file, or user resources are defined.

   **Execution details:**

   - **Attempted `memcached` inclusion**:
     - Preserve this position in the Ansible execution sequence.
     - The supplied cookbook does not identify the Memcached package, configuration path, service name, listening port, or memory allocation.
     - Do not invent these values from the local cookbook.
     - If Memcached is required, obtain the missing dependency cookbook or define its configuration as a migration input.

   - **Redis server assignment**:
     - Configure one Redis instance named **Redis instance on port 6379**.
     - Set the Redis port to `6379`.
     - Configure Redis authentication using a vaulted or externally managed password.
     - Preserve the disabled or null `replicaservestaledata` behavior in the selected Redis implementation.
     - Do not store `redis_secure_password_123` in the migrated configuration.

   - **Redis log directory**:
     - Create `/var/log/redis` recursively.
     - Set owner to `redis`.
     - Set group to `redis`.
     - Set mode to `0755`.

   - **Attempted `redisio` inclusion**:
     - Preserve this position after the Redis log directory task.
     - The unavailable recipe is expected to provide Redis package installation, configuration generation, and service management.
     - The migration must explicitly provide those functions because no package, template, configuration, or service details are available locally.

   - **`ruby_block[fix_redis_config]`**:
     - Check whether `/etc/redis/6379.conf` exists.
     - If present, read the complete file.
     - Remove lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Preserve all other configuration content.
     - Write the modified content back to `/etc/redis/6379.conf`.
     - Restart or reload Redis only if required by the selected Ansible implementation and only when the configuration changes.
     - The Chef resource does not define an explicit notification or service restart.

   - **Attempted `redisio::enable` inclusion**:
     - Preserve this as the final operation.
     - Explicitly enable and start the Redis service using the service name supplied by the selected Redis package.
     - The exact Chef service name is unavailable and must not be assumed without validating the target package.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`; recipe unavailable
- `redisio`, with no version constraint; recipe unavailable
- `redisio::enable`; recipe unavailable

**System package dependencies**:

- None are directly declared in `cookbooks/cache/recipes/default.rb`.
- Redis and Memcached package requirements are expected to come from the unavailable external cookbooks.
- Exact package names cannot be verified from the supplied cookbook and must be selected and validated for the target platform.

**Service dependencies**:

- Redis service enablement and startup are intended to come from `redisio::enable`, which is unavailable.
- Memcached service management is intended to come from the unavailable `memcached` recipe.
- No local Chef service resource is present.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe; no Vault, CyberArk, data bag, or external secret manager integration detected
- **URL**: None detected
- **Path**: None detected

### Redis Authentication Password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded literal value
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`
- **Migration handling**:
  - Store the password in Ansible Vault or the organization’s approved secret-management system.
  - Do not commit the literal password to role defaults, group variables, or rendered templates.
  - Use the vaulted variable when rendering `/etc/redis/6379.conf`.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, `node['vault']`, or `node['secrets']` usage was detected. No TLS certificate, private key, database connection string, API key, or environment-variable secret reference was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- No Redis Unix socket identified
- No Memcached endpoint confirmed because the `memcached` recipe is unavailable

**Templates rendered**:

- Local cookbook templates: none; render count `0`
- External Redis templates: unavailable; render count cannot be determined
- External Memcached templates: unavailable; render count cannot be determined

**Configuration mutation to verify**:

Confirm that `/etc/redis/6379.conf` does not contain active lines beginning with:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

### Redis instance on port 6379

```bash
# Validate the Redis service using the actual service name supplied by the target package.
systemctl status redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server

# Confirm the Redis process and TCP listener.
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'
ps aux | grep '[r]edis-server'

# Confirm the configuration file exists.
test -f /etc/redis/6379.conf

# Verify the configured port and authentication directive.
grep -nE '^(port|requirepass)[[:space:]]' /etc/redis/6379.conf
grep -nE '^port[[:space:]]+6379$' /etc/redis/6379.conf

# Verify that the cleanup directives are absent.
! grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Test authenticated Redis connectivity using the vaulted password.
redis-cli -h 127.0.0.1 -p 6379 -a '<vaulted-redis-password>' PING
redis-cli -h 127.0.0.1 -p 6379 -a '<vaulted-redis-password>' INFO server

# Confirm unauthenticated access is rejected.
redis-cli -h 127.0.0.1 -p 6379 PING

# Verify the Redis log directory.
stat -c '%A %U %G %n' /var/log/redis
ls -lah /var/log/redis

# Review service logs.
journalctl -u redis-server --no-pager -n 100
journalctl -u redis-server -p warning --no-pager
```

Expected Redis results:

- Redis is enabled and active.
- Redis listens on TCP port `6379`.
- Authenticated `PING` returns `PONG`.
- Authenticated `INFO server` returns Redis server information.
- Unauthenticated access reports that authentication is required.
- `/var/log/redis` has owner `redis`, group `redis`, and mode `0755`.
- `/etc/redis/6379.conf` contains no active lines for the five removed directive types.

### Memcached dependency validation

The local cookbook does not establish a Memcached instance or endpoint. Run these checks only if Memcached is intentionally included in the target Ansible deployment and its missing dependency configuration has been supplied:

```bash
systemctl status memcached
systemctl is-active memcached
ss -tlnp | grep ':11211'
```

The port `11211` is not derived from the supplied Chef recipe and must be confirmed separately before use.