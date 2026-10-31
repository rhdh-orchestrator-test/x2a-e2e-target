---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer with one locally defined Redis instance on port `6379` and an attempted external Memcached dependency. The Chef execution order is: include `memcached`, create `/var/log/redis`, include `redisio`, remove five replication-related directives from `/etc/redis/6379.conf`, and include `redisio::enable`. Redis authentication is enabled with a password hardcoded in the recipe and must be migrated to Ansible Vault or an approved secret backend. The supplied execution tree does not include the external dependency implementations, so their package names, service names, templates, and provider behavior are unconfirmed.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance configured by the local recipe
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with `requirepass`; `replicaservestaledata` is unset; replication-related directives are removed after the Redis configuration is generated
  - Log Directory: `/var/log/redis`
  - Log Directory Owner/Group: `redis:redis`
  - Log Directory Mode: `0755`

- **Memcached**: External cache dependency included by the recipe; configuration is not available in the supplied execution tree
  - Location/Path: Not established
  - Port/Socket: Not established
  - Key Config: Package, service, configuration path, endpoint, and templates are unavailable because the `memcached` recipe is missing
  - Migration Status: Implement only after inspecting the separately supplied dependency or confirming target-distribution defaults

The local recipe attempts to include these external recipes:

- `memcached` — recipe file not found
- `redisio` — recipe file not found
- `redisio::enable` — recipe file not found

## File Structure

The execution tree reports only one analyzed recipe file. No provider, template, attribute, or static file is listed as executed or referenced.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
None listed in the execution tree.
```

**Templates:**
```text
None listed in the execution tree.
```

**Attributes:**
```text
None listed in the execution tree.
```

**Files:**
```text
None listed in the execution tree.
```

The cookbook metadata was inspected to identify the cookbook description and external dependencies, but it is not included in the executable file list because the supplied execution tree contains only `cookbooks/cache/recipes/default.rb`.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` recipe is reported as missing, so its package, service, configuration, endpoint, and templates cannot be confirmed.
   - Sets `node.default['redisio']['servers']` to one Redis configuration item:
     - **Redis server on port 6379**
       - `port`: `6379`
       - `requirepass`: `redis_secure_password_123`
       - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation enabled
   - Includes the external `redisio` recipe.
   - The `redisio` recipe is reported as missing. It is expected to consume the Redis server collection and generate `/etc/redis/6379.conf`, but its packages, templates, service resources, and provider behavior are not available for confirmation.
   - Executes `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified Redis configuration back to `/etc/redis/6379.conf`.
   - The cleanup is conditional and performs no action when `/etc/redis/6379.conf` does not exist.
   - Includes the external `redisio::enable` recipe.
   - The `redisio::enable` recipe is reported as missing. Its intended behavior is to enable and start Redis, but the exact service unit name must be confirmed from the dependency or target platform.
   - The local recipe contains one `directory` resource and one `ruby_block` resource.
   - No standalone `group` resource is present; the `redis` owner and group are assigned directly to the directory resource.

### Ansible migration behavior

The equivalent Ansible implementation must preserve this execution order:

1. Attempt or implement the confirmed Memcached dependency behavior.
2. Create `/var/log/redis`.
3. Install and configure Redis through a verified replacement for `redisio`.
4. Remove the five unwanted directives from `/etc/redis/6379.conf`.
5. Enable and start Redis using the verified service unit name.

The Redis cleanup should use an `ansible.builtin.stat` check followed by idempotent `ansible.builtin.replace` tasks. The Redis password must not be stored as a plaintext literal in the Ansible role.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`; implementation not present
- `redisio`, with no version constraint shown; implementation not present
- `redisio::enable`, provided by the missing `redisio` dependency

**System package dependencies**:

- No package resources are present in the local recipe.
- No package names are confirmed because the external `memcached` and `redisio` recipes are missing.
- Package names such as `redis-server` or `memcached` must not be treated as confirmed cookbook behavior without inspecting the external implementations or target distribution.

**Service dependencies**:

- Redis server on TCP port `6379`
- Memcached service through the external `memcached` recipe
- Exact systemd unit names are not available in the supplied execution tree.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded literal
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the Redis server on port `6379`
- **Migration handling**: Store the password in Ansible Vault or an approved secret-management integration, then reference the vaulted variable when configuring `/etc/redis/6379.conf`.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, database connection strings, or other credentials were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

The external dependency recipes may create additional files, but those files are not listed in the supplied execution tree.

**Service endpoints to check**:

- Redis server on port `6379`
- Memcached endpoint: not established by the supplied cookbook analysis
- Unix sockets: none configured or referenced
- Bind address/network interface: none configured or referenced

**Templates rendered**:

- No templates rendered
- Template count: `0`

**Configuration cleanup to verify**:

`/etc/redis/6379.conf` must not contain active lines matching:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

### Redis server on port 6379

```bash
# Locate the Redis process
ps aux | grep '[r]edis'

# Verify the Redis configuration file
test -f /etc/redis/6379.conf

# Verify the Redis log directory
stat -c '%A %U %G %n' /var/log/redis
# Expected: mode 755, owner redis, group redis

# Verify Redis is listening on TCP port 6379
ss -ltnp | grep ':6379'
# Expected: a Redis process listening on port 6379

# Authenticate and test Redis
redis-cli -p 6379 -a '<retrieve-from-secret-store>' PING
# Expected: PONG

# Verify a write/read operation
redis-cli -p 6379 -a '<retrieve-from-secret-store>' SET migration_check success
redis-cli -p 6379 -a '<retrieve-from-secret-store>' GET migration_check
# Expected: success

# Verify Redis server information
redis-cli -p 6379 -a '<retrieve-from-secret-store>' INFO server

# Confirm unwanted replication directives were removed
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected: no matching active configuration lines

# Inspect Redis log files
find /var/log/redis -maxdepth 1 -type f -print
```

### Memcached

The `memcached` recipe is missing, so the cookbook does not establish a Memcached port, service name, configuration path, or protocol endpoint. Add dependency-specific checks after the external recipe is supplied and inspected.

If the dependency confirms the standard Memcached port, use:

```bash
# Run only after confirming the dependency configures Memcached on port 11211
ss -ltnp | grep ':11211'
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
```

Port `11211` is not confirmed behavior of the supplied `cache` cookbook.

### Redis service state

```bash
# Inspect available Redis service units
systemctl list-units --type=service | grep -i redis

# Check the Redis process command line
pgrep -a redis

# Check the service only after confirming its unit name from the redisio dependency
systemctl status '<confirmed-redis-service-unit>'

# Review recent Redis service logs
journalctl -u '<confirmed-redis-service-unit>' --no-pager -n 50
```

The final migration must use the confirmed Redis service unit and must not assume `redis`, `redis-server`, or `redis@6379` without verifying the external dependency or target platform.