---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching through the external `memcached` and `redisio` cookbooks. It defines one Redis instance on TCP port `6379`, with authentication, configuration at `/etc/redis/6379.conf`, and log directory `/var/log/redis`. After Redis configuration, it removes five replication-related directives and then enables Redis. The dependency recipes are unavailable, so their package names, service units, templates, and Memcached settings must be verified before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`
  - Key Config: `requirepass` is set to `redis_secure_password_123`; `replicaservestaledata` is explicitly set to `nil`
  - Log Directory: `/var/log/redis`
  - Ownership: `redis:redis`
  - Permissions: `0755`
  - Post-configuration cleanup removes:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

Memcached is included through the external `memcached` cookbook, but its instance name, port, package, configuration path, authentication settings, and service details are not available in the supplied execution tree. These values must be obtained from the dependency cookbook before migration.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

Referenced dependency recipes were not present in the execution tree:

- `memcached`
- `redisio`
- `redisio::enable`

A structural analysis mentioned a `group['redis']` resource, but the authoritative execution tree and `cookbooks/cache/recipes/default.rb` do not declare it. It is excluded from the migration plan.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Defines one Redis server with port `6379`, password `redis_secure_password_123`, and `replicaservestaledata` set to `nil`.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Includes the external `redisio` recipe.
   - Removes five replication-related directives from `/etc/redis/6379.conf` if the file exists.
   - Includes `redisio::enable`.

   **Iteration expansion**:
   - `node['redisio']['servers']` contains exactly one item:
     - Redis server on port `6379`
       - `requirepass`: `redis_secure_password_123`
       - `replicaservestaledata`: `nil`

   **Step 1: Include `memcached`**
   - Chef statement: `include_recipe 'memcached'`
   - The dependency recipe is unavailable.
   - Package name, configuration path, service name, port, and authentication behavior cannot be determined from this cookbook.
   - The migration must include the dependency role or equivalent tasks after validating its implementation.

   **Step 2: Define the Redis server**
   - Chef configuration:
     ```ruby
     node.default['redisio']['servers'] = [
       {
         'port' => '6379',
         'requirepass' => 'redis_secure_password_123',
         'replicaservestaledata' => nil
       }
     ]
     ```
   - Represent this as one explicitly defined Redis instance on port `6379`.
   - Replace the hardcoded password with an Ansible Vault variable or another approved secrets backend.

   **Step 3: Create `/var/log/redis`**
   - Resource: `directory`
   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled
   - Ansible equivalent: `ansible.builtin.file` with `state: directory`

   **Step 4: Include `redisio`**
   - Chef statement: `include_recipe 'redisio'`
   - The dependency recipe is unavailable.
   - It is expected to consume the Redis server definition and generate `/etc/redis/6379.conf`.
   - The migration must verify the dependency’s package, user, group, configuration template, and service implementation.
   - Configure port `6379` and authentication using a vaulted password.
   - Do not infer package names or service unit names from this cookbook.

   **Step 5: Run `ruby_block[fix_redis_config]`**
   - Runs after `redisio` and before `redisio::enable`.
   - Target: `/etc/redis/6379.conf`
   - If the file exists, reads it, removes complete lines beginning with the following directives, and writes the result back:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - If the file does not exist, performs no action.
   - Ansible equivalent: five explicit `ansible.builtin.replace` tasks removing matching complete lines.
   - Notify a Redis restart or reload only when configuration changes, subject to the final service implementation.
   - The Chef recipe does not declare a service restart notification itself.

   **Step 6: Include `redisio::enable`**
   - Chef statement: `include_recipe 'redisio::enable'`
   - Runs after `fix_redis_config`.
   - Enables Redis at boot and starts it after configuration is complete.
   - The actual service unit name must be verified on the target operating system and against the dependency implementation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**System package dependencies**:

- No package resources are directly visible in `cookbooks/cache/recipes/default.rb`.
- Package names from the external `memcached` and `redisio` cookbooks are unavailable and must be verified before migration.
- No package name should be hardcoded without validating the dependency implementation and target operating system.

**Service dependencies**:

- Memcached service: provided by the unavailable `memcached` recipe; service name is not specified.
- Redis service: enabled by the unavailable `redisio::enable` recipe; service unit name is not specified.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis Password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the instance listening on port `6379`
- **Migration storage**: Ansible Vault or another approved secrets backend
- **Migration variable**: `redis_password`
- **Handling**: Use `no_log: true` on tasks that could expose the secret

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis/`

The cookbook does not specify a Redis log filename. Determine the configured log destination from `/etc/redis/6379.conf` or the target service unit. Do not use a wildcard log path in validation scripts.

**Service endpoints to check**:

- Redis instance on port `6379`
- Unix sockets: None specified
- Memcached endpoint: Not specified in the analyzed cookbook

**Configuration directives to verify in `/etc/redis/6379.conf`**:

- `port 6379` is present.
- Authentication is enabled with the vaulted Redis password.
- The following directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- Cookbook templates: none
- Render count: `0`
- Dependency templates: unavailable and not counted as cookbook files

## Pre-flight checks

The exact Redis and Memcached service unit names must be obtained from the dependency implementations and target host before running service-specific checks.

```bash
# Redis service status for the Redis instance on port 6379
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>

# Redis port check
ss -ltnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Redis configuration file and primary settings
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Redis cleanup verification
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected replication-related directives remain"
  exit 1
else
  echo "Redis cleanup directives are absent"
fi

# Redis authenticated connectivity
redis-cli -h 127.0.0.1 -p 6379 -a '<REDIS_PASSWORD>' PING
redis-cli -h 127.0.0.1 -p 6379 -a '<REDIS_PASSWORD>' INFO server

# Redis unauthenticated access must be rejected
redis-cli -h 127.0.0.1 -p 6379 PING

# Redis log directory
stat -c '%A %U %G %n' /var/log/redis
ls -la /var/log/redis

# Redis logging configuration
grep -E '^(logfile|syslog-enabled|daemonize)' /etc/redis/6379.conf

# Redis service logs
journalctl -u <redis-service-unit> --since "15 minutes ago" --no-pager

# Memcached service validation after dependency inspection
systemctl status <memcached-service-unit>
ss -ltnp
```

Expected results:

- The Redis service for the port `6379` instance is active and enabled.
- Redis listens on TCP port `6379`.
- Authenticated `redis-cli` access returns `PONG`.
- Unauthenticated access fails with an authentication-required error.
- `/etc/redis/6379.conf` contains port `6379` and a securely managed authentication directive.
- All five replication-related directives are absent.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- Redis logs show no startup or configuration errors and report readiness to accept connections.
- Memcached service and endpoint checks must use values obtained from the unavailable `memcached` dependency; no port or configuration path may be assumed.