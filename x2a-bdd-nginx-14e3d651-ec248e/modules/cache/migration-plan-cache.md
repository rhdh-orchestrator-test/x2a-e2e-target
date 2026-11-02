---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. Direct recipe-level details indicate one Redis instance on port `6379`, Redis authentication, creation of `/var/log/redis`, removal of five Redis replication and client-buffer directives from `/etc/redis/6379.conf`, and invocation of `redisio::enable`. The supplied execution tree confirms the local directory resource, Redis configuration cleanup block, and missing external dependency recipes, but does not independently expose all Redis attribute values or credential details. Memcached configuration, package, service, and port details must be obtained from its external dependency or the target host.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance — port 6379**: Redis cache server configured by the local recipe
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Log directory: `/var/log/redis`
  - Key Config: Authentication enabled through `requirepass`; source-level recipe details report the password as `redis_secure_password_123`
  - Additional configuration: `replicaservestaledata` is assigned `nil`
  - Cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Source-level verification status: These Redis values are reported from direct recipe inspection but are not present in the supplied structured execution summary

- **Memcached service**: Included through the external `memcached` cookbook
  - Location/Path: Not specified by the local cookbook
  - Port/Socket: Not specified by the local cookbook or supplied execution tree
  - Key Config: No local Memcached authentication, port, configuration path, or instance collection is defined
  - Dependency requirement: Inspect the external `memcached` cookbook or target host before determining the package, service name, configuration, and port

**Iterations**:

- The local recipe contains no Ruby `.each` loop.
- The source-level Redis server collection contains exactly one configured item: port `6379`.
- The external `redisio` dependency consumes the Redis server collection.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only the recipe file shown in the supplied execution tree is listed below. The metadata file was read for analysis but is not included because the required file list is restricted to `.rb` files shown in the execution tree.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are shown in the execution tree.

**Templates:**
```text
```

No template files are shown in the execution tree.

**Attributes:**
```text
```

No attribute files are shown in the execution tree. The Redis server collection is assigned directly in `cookbooks/cache/recipes/default.rb` according to the source-level recipe details.

**Files:**
```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The execution tree reports that the `memcached` recipe file is not present in this cookbook.
   - Memcached package installation, service management, configuration path, port, and templates must be supplied by an external dependency task or equivalent Ansible role.
   - Resource: `include_recipe 'memcached'`.
   - Iterations: None.

2. **default — Redis log directory setup** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Uses recursive directory creation.
   - Sets owner `redis`, group `redis`, and mode `0755`.
   - The structured execution tree confirms `directory[/var/log/redis]`.
   - No `group['redis']` resource is shown in the supplied execution tree; creation of the `redis` group is an inferred prerequisite, not a confirmed Chef resource.
   - Resources: `directory[/var/log/redis]`.
   - Iterations: None.

3. **default — Redis server collection assignment** (`cookbooks/cache/recipes/default.rb`):
   - Assigns one Redis server object to `node['redisio']['servers']`.
   - Configures port `6379`.
   - Enables Redis authentication using the source-level `requirepass` value `redis_secure_password_123`.
   - Sets `replicaservestaledata` to `nil`.
   - This is a direct recipe assignment, not an attribute-file value.
   - These values are reported from direct recipe inspection and are not exposed in the supplied structured execution summary.
   - Resources: Direct node attribute assignment.
   - Iterations: One configured Redis item, port `6379`.

4. **redisio** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The execution tree reports that the `redisio` recipe file is not present in this cookbook.
   - The dependency is expected to consume the Redis server collection and generate `/etc/redis/6379.conf`.
   - Package installation and initial Redis service setup are not defined in the supplied local cookbook or execution tree.
   - Resource: `include_recipe 'redisio'`.
   - Iterations: The configured Redis collection contains one item, port `6379`.

5. **default — Redis configuration cleanup** (`cookbooks/cache/recipes/default.rb`):
   - Executes `ruby_block[fix_redis_config]`.
   - Checks whether `/etc/redis/6379.conf` exists.
   - Reads the file when present.
   - Removes lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified content back while preserving unrelated configuration.
   - Makes no change when the configuration file is absent.
   - The structured execution tree confirms `ruby_block[fix_redis_config]`; the directive list is based on the source-level recipe details.
   - Resource: `ruby_block[fix_redis_config]`.
   - Iterations: Five explicit directive patterns are removed.

6. **enable** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio::enable` recipe.
   - The execution tree reports that the `redisio::enable` recipe file is not present in this cookbook.
   - The dependency is expected to enable Redis at boot and may start the generated Redis service.
   - The exact Redis systemd unit name must be confirmed from the dependency implementation or target host.
   - Resource: `include_recipe 'redisio::enable'`.
   - Iterations: None.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- No package names are declared by the local recipe.
- Exact package names cannot be verified from the supplied execution tree.
- Package installation must be obtained from the external `memcached` and `redisio` implementations or confirmed for the target distribution before creating Ansible tasks.

**Service dependencies**:

- Memcached service supplied by the external `memcached` cookbook; exact unit name is unknown.
- Redis service for port `6379` supplied by the external `redisio` cookbook; exact unit name is unknown.
- The Redis `redis` group is required for the configured log-directory ownership but is not shown as a confirmed Chef resource.

## Credentials

**Detection Summary**: 1 credential reported from direct recipe inspection in 1 file; the supplied structured analysis does not independently expose credential-detection results.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded literal in the recipe: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the instance listening on TCP port `6379`

The Ansible migration must not reproduce this password as a plaintext default in a publicly stored role. Store it in an AAP credential, Ansible Vault variable, or another approved secret-management system, and render it into the Redis configuration with restrictive permissions.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk/Conjur calls, Vault namespaces, secret environment variables, TLS certificate references, or database connection strings were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Memcached endpoint: port not specified; confirm from the external dependency or target host
- Unix sockets: none specified

**Templates rendered**:

- None

**Configuration transformations to verify**:

The following directives should be absent from `/etc/redis/6379.conf` after migration:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks:

```bash
# Confirm the Redis configuration file and log directory
test -f /etc/redis/6379.conf
test -d /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis

# Confirm Redis service unit discovery for the 6379 instance
systemctl list-units --type=service --all | grep -i redis

# Replace "redis" with the exact unit discovered from redisio or the target host
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Confirm that the Redis 6379 instance is listening
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'

# Validate Redis configuration and removed directives
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Use the migrated secret from an approved secret store rather than shell history
export REDIS_PASSWORD='<retrieve-from-approved-secret-store>'

# Verify authenticated Redis access for the 6379 instance
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server

# Verify unauthenticated access is rejected
redis-cli -p 6379 PING

# Verify Redis read/write behavior
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET migration_check "ok"
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET migration_check
redis-cli -p 6379 -a "$REDIS_PASSWORD" DEL migration_check

# Discover the Memcached service and endpoint
systemctl list-units --type=service --all | grep -i memcached
ss -ltnp | grep -i memcached

# Only if the external dependency confirms TCP port 11211
printf 'version\r\n' | nc -w 2 127.0.0.1 11211

# Review logs for the Redis 6379 instance and Memcached service
journalctl -u redis --no-pager -n 100
journalctl -u memcached --no-pager -n 100
ls -lah /var/log/redis
```

Expected Redis results:

- The Redis service for port `6379` is active and enabled.
- A Redis process listens on TCP port `6379`.
- Authenticated `PING` returns `PONG`.
- Unauthenticated access returns an authentication-required error.
- `/etc/redis/6379.conf` exists and contains the configured port.
- The five removed directives do not appear in the configuration.
- `/var/log/redis` exists with ownership `redis:redis` and mode `0755`.

Expected Memcached results:

- The Memcached service and port are confirmed from the external dependency or target host.
- The service is active.
- If TCP port `11211` is confirmed, the version command returns a Memcached version response.
- Port `11211` must not be assumed in the Ansible role without confirmation.