---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer intended to use Memcached and Redis. The entry recipe includes the external `memcached`, `redisio`, and `redisio::enable` recipes, defines one Redis instance on port **6379**, enables Redis authentication, creates `/var/log/redis`, and removes five replication-related directives from `/etc/redis/6379.conf`. The external dependency recipe files are unavailable, so their package installation, service resources, templates, and Memcached settings must be confirmed before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with `requirepass`; password must be stored in Ansible Vault or another protected secret source. The directives `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` are removed from the configuration.
  - Log Directory: `/var/log/redis`
  - Log Directory Ownership: `redis:redis`
  - Log Directory Mode: `0755`

- **Memcached instance**: Intended Memcached service; no explicit instance configuration is available
  - Location/Path: Not specified
  - Port/Socket: Not specified
  - Key Config: The external `memcached` recipe is included, but its package, service name, configuration path, and endpoint settings are unavailable.

## File Structure

Only the recipe file shown in the supplied execution tree is included.

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

No attribute files are shown in the execution tree. Redis server configuration is assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` dependency is not present in the supplied execution tree, so its packages, service resources, templates, configuration path, and port cannot be inferred.
   - Assigns one Redis server definition to `node['redisio']['servers']`:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - The `redisio` dependency is not present in the supplied execution tree. It is expected to consume the Redis server definition, but its packages, service resources, templates, and configuration behavior must be verified.
   - Executes `ruby_block[fix_redis_config]`:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Reads the file only when it exists.
     - Removes complete lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Writes the modified content back while preserving all other configuration.
   - Includes the external `redisio::enable` recipe.
   - The `redisio::enable` dependency is not present in the supplied execution tree. Confirm the Redis service name before implementing service enablement in Ansible.
   - Resources shown in the execution tree:
     - `directory[/var/log/redis]`
     - `ruby_block[fix_redis_config]`

No `.each` loops are present in the analyzed recipe, so there are no additional loop iterations to expand.

## Dependencies

**External cookbook dependencies**:

- `memcached` — version constraint not verified in the supplied execution tree
- `redisio` — version constraint not verified in the supplied execution tree
- `redisio::enable` — recipe included from `redisio`

**System package dependencies**:

- Not determinable from the analyzed files.
- Package names and versions must be confirmed from the external `memcached` and `redisio` cookbooks or target operating-system metadata.
- Do not assume package names or versions during migration.

**Service dependencies**:

- Memcached service — referenced through `include_recipe 'memcached'`; service name unavailable.
- Redis service — referenced through `include_recipe 'redisio'` and `include_recipe 'redisio::enable'`; service name unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext string
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis authentication. The value is assigned to the Redis server definition and is expected to be rendered into the Redis configuration by the external `redisio` cookbook.
- **Ansible migration**:
  - Store the password in Ansible Vault, for example as `redis_requirepass`.
  - Do not place the plaintext value in `group_vars`, `host_vars`, or an ordinary template.
  - Render it into the Redis configuration with restrictive permissions.
  - Prevent the password from appearing in task output, logs, or command history.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, API keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`, if created by the external `redisio` dependency

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Memcached instance: port not specified
- Unix sockets: none specified

**Configuration directives to verify**:

The following directives must not remain in `/etc/redis/6379.conf`:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

**Templates rendered**:

- None shown in the execution tree; render count: `0`

**Static files deployed**:

- None shown in the execution tree; deployment count: `0`

## Pre-flight checks:

```bash
# Confirm the Redis configuration file exists
test -f /etc/redis/6379.conf
echo "redis_config_exit_code=$?"

# Confirm Redis is listening on the configured port
ss -ltnp | grep ':6379'
nc -zv 127.0.0.1 6379

# Confirm the Redis service name in the redisio dependency before running this check
systemctl status <confirmed-redis-service-name>

# Query Redis using a protected secret mechanism
redis-cli -p 6379 -a '<redis-password-from-secure-storage>' PING
# Expected output: PONG

# Verify the configured Redis port
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' \
  /etc/redis/6379.conf

# Verify authentication is configured without printing its value
grep -E '^[[:space:]]*requirepass[[:space:]]+' \
  /etc/redis/6379.conf

# Confirm all unwanted replication directives are absent
if grep -Eq '^[[:space:]]*(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf; then
  echo "Unexpected replication directives remain"
  exit 1
else
  echo "Replication directives removed"
fi

# Inspect Redis logs
journalctl -u <confirmed-redis-service-name> --no-pager -n 100

# Verify the Redis log directory
test -d /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis
# Expected: redis:redis 755 /var/log/redis
```

Before validating Memcached, inspect the external `memcached` cookbook to determine its package, service name, configuration path, and port:

```bash
# Check the confirmed Memcached service
systemctl status <confirmed-memcached-service-name>

# Check the confirmed Memcached listener
ss -ltnp | grep ':<confirmed-memcached-port>'

# Query the confirmed Memcached endpoint
printf 'version\r\n' | nc 127.0.0.1 <confirmed-memcached-port>
# Expected output should contain: VERSION
```

Run the Ansible playbook twice to verify idempotence:

```bash
ansible-playbook -i <inventory> <playbook>.yml
ansible-playbook -i <inventory> <playbook>.yml
```

On the second run, verify that:

- `/var/log/redis` is unchanged.
- `/etc/redis/6379.conf` is unchanged after the five unwanted directives are removed.
- Redis is not restarted unnecessarily.
- The Redis password is not exposed in Ansible output.
- Redis remains enabled after its service name is confirmed.
- The named Memcached instance remains healthy after its service name and port are confirmed.