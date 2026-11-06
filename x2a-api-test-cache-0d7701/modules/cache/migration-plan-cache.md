---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services through the external `memcached` and `redisio` cookbooks. The supplied execution tree contains only `cookbooks/cache/recipes/default.rb`; the external dependency recipes are unavailable for analysis. The local recipe configures one Redis instance on port `6379`, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and enables Redis through `redisio::enable`. Redis authentication uses a hardcoded password that must be migrated to protected secret storage. No Memcached instance attributes, package names, configuration paths, or ports are defined locally.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache and database service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with `requirepass`; password source value is `redis_secure_password_123`; log directory is `/var/log/redis`; `replicaservestaledata` is set to `nil`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Configuration cleanup removes:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

- **Memcached instance**: Memcached service included through the external `memcached` cookbook
  - Location/Path: Not specified in the supplied execution tree
  - Port/Socket: Not specified in the supplied execution tree
  - Key Config: No local Memcached attributes or configuration values are defined. Obtain the values from the replacement cookbook or target deployment requirements; do not invent them.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only files present in the supplied execution tree are listed.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are present in the execution tree.

**Templates:**
```text
```

No templates are present in the execution tree.

**Attributes:**
```text
```

No attribute files are present in the execution tree. The Redis settings are assigned directly inside `recipes/default.rb`.

**Files:**
```text
```

No static files are deployed by the analyzed recipe.

The metadata file was inspected to determine dependencies and service purpose, but it is not an executed recipe file and is therefore omitted from the required execution-tree file list.

## Module Explanation

The cookbook performs operations in this order:

1. **memcached default recipe** (`memcached::default`; external cookbook recipe not present in the supplied execution tree):
   - Includes or implements Memcached installation and configuration.
   - The local recipe provides no Memcached instance names, package names, configuration paths, ports, or listener settings.
   - The exact external recipe implementation must be obtained from the `memcached` cookbook version being replaced.

2. **cache default recipe** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Sets the Redis server collection with one configured server:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
   - Includes the external `redisio` recipe.
   - Executes `ruby_block[fix_redis_config]`:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Reads the complete file when it exists.
     - Removes complete lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
     - Writes the modified contents back to `/etc/redis/6379.conf`.
     - Performs no file modification when the file does not exist.
   - Includes the external `redisio::enable` recipe.
   - The local resources execute in this order:
     1. `directory[/var/log/redis]`
     2. `ruby_block[fix_redis_config]`

3. **redisio default recipe** (`redisio::default`; external cookbook recipe not present in the supplied execution tree):
   - Provides the Redis installation and configuration behavior referenced by the local recipe.
   - The exact package names, service names, generated configuration behavior, and user/group creation are unavailable from the supplied execution tree.

4. **redisio enable recipe** (`redisio::enable`; external cookbook recipe not present in the supplied execution tree):
   - Provides Redis service enablement behavior.
   - The exact service unit name must be determined from the target operating system and selected Redis implementation.

The local recipe contains no standalone `group` resource. The `redis` user and group are referenced as ownership values for `/var/log/redis` and are expected to be created by the external Redis dependency.

### Ansible implementation guidance

Use an Ansible task order equivalent to the Chef flow:

1. Implement or include Memcached setup using verified values from the selected external implementation.
2. Define the Redis instance configuration for port `6379`.
3. Create `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
4. Implement Redis installation and configuration.
5. Apply the cleanup to `/etc/redis/6379.conf` only when the file exists.
6. Enable Redis.

The cleanup must remove complete lines matching the five specified directives, remain idempotent, avoid unrelated configuration lines, and notify a Redis restart or reload only when the file changes. The Chef `ruby_block` does not explicitly declare a service notification, so the desired operational behavior must be confirmed before adding a handler.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- No package resources are present in the analyzed local recipe.
- Package names from the unavailable external recipes cannot be verified from the supplied execution tree and must be obtained from the selected target implementation.

**Service dependencies**:

- Memcached service, included through the external `memcached` recipe.
- Redis service for instance `6379`, included through the external `redisio` and `redisio::enable` recipes.
- Exact systemd unit names must be determined from the target operating system and selected Ansible implementation.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value in the recipe
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`

For Ansible, store the password in Ansible Vault, an AAP credential, or another approved secret-management integration. Do not preserve it in plaintext in role tasks or defaults. Render it into the Redis configuration with protected file permissions and avoid exposing it through task output.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificates, private keys, API keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Memcached endpoint: determine from the migrated configuration; no port is specified in the supplied execution tree
- No Unix socket is configured or referenced by the analyzed recipe

**Templates rendered**:

- None; no templates are present and no templates are rendered

**Configuration transformation to verify**:

The following directives must not remain in `/etc/redis/6379.conf` after cleanup:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Verify the Redis service using the unit name selected by the Ansible implementation.
systemctl status redis
systemctl status redis-server

# Verify the Redis instance configuration.
test -f /etc/redis/6379.conf
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# The directive check should return no matching lines.
# Verify the Redis listener.
ss -tlnp | grep ':6379'
netstat -tlnp | grep ':6379'

# Use the Ansible Vault-managed password rather than placing it in shell history.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server
redis-cli -p 6379 -a "$REDIS_PASSWORD" CONFIG GET requirepass

# Expected Redis results:
# - PING returns PONG.
# - INFO server returns Redis server information.
# - requirepass is configured.

# Verify the Redis log directory.
test -d /var/log/redis
stat -c '%U %G %a %n' /var/log/redis
ls -la /var/log/redis

# Expected directory properties:
# - Owner: redis
# - Group: redis
# - Mode: 755

# Inspect Redis service logs using the applicable unit name.
journalctl -u redis --no-pager -n 100
journalctl -u redis-server --no-pager -n 100

# If a file-based Redis log is configured, inspect its path.
grep -nE '^logfile ' /etc/redis/6379.conf

# Verify the Memcached service using the unit name selected by the Ansible implementation.
systemctl status memcached

# Verify the actual Memcached listener configured by the migration.
# Do not assume a port because none is specified in the supplied Chef files.

# Perform a Memcached protocol-level health check against the configured listener.
# printf 'version\r\n' | nc <verified-memcached-host> <verified-memcached-port>
```