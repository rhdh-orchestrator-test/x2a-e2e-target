---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis instance on port `6379` and includes external Memcached and Redisio recipes. The visible recipe creates `/var/log/redis`, configures Redis authentication with the hardcoded password `redis_secure_password_123`, invokes `redisio`, removes five replication-related directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. The Memcached, Redisio, and Redisio enablement recipe files are unavailable, so their packages, service names, templates, and endpoint details must be obtained from the corresponding external cookbook implementations rather than invented during migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache and authenticated service
  - Location/Path: `/etc/redis/6379.conf`
  - Log directory: `/var/log/redis`
  - Port/Socket: `6379/TCP`
  - Key Config:
    - Authentication enabled through `requirepass`
    - Current password: `redis_secure_password_123`
    - `replicaservestaledata`: `nil`
    - The migration must store the password in Ansible Vault.
    - Remove `replica-serve-stale-data`
    - Remove `replica-read-only`
    - Remove `repl-ping-replica-period`
    - Remove `client-output-buffer-limit`
    - Remove `replica-priority`

**Memcached** is included as an external dependency, but no Memcached instance name, port, package, configuration path, or service details are present in the supplied execution tree. Do not invent Memcached values in the Ansible role. Obtain them from the installed `memcached` cookbook version if this dependency must be preserved.

## File Structure

Only files shown by the supplied execution tree and directory listing are included.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are shown or used by the supplied execution tree.

**Templates:**
```text
```

No templates are shown or rendered by the supplied execution tree.

**Attributes:**
```text
```

No attribute files are shown. Redis settings are assigned inline in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are shown as deployed by `cookbook_file` or `remote_file`.

**Referenced but unavailable recipe files:**

- `memcached`
- `redisio`
- `redisio::enable`

These dependency recipes must not be listed as cookbook files or recreated without inspecting the corresponding external implementations.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` recipe file is not present in the supplied execution tree.
   - Memcached package installation, service management, configuration, and endpoint details must be obtained from the external dependency.
   - Assigns one Redis server to `node['redisio']['servers']`:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - The password must be migrated to Ansible Vault and must not remain in plaintext in role defaults, variables, templates, or task output.

2. **Directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `directory[/var/log/redis]`.
   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled
   - Ansible equivalent:
     ```yaml
     - name: Create the Redis log directory
       ansible.builtin.file:
         path: /var/log/redis
         state: directory
         owner: redis
         group: redis
         mode: '0755'
     ```
   - Creation of the `redis` user and group is not shown and must be supplied by the external Redis installation dependency before this task runs.

3. **`redisio` include** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The `redisio` recipe file is not present in the supplied execution tree.
   - Redis package names, package versions, service name, service state, configuration template, user/group creation, data directory, log file, and bind address are not exposed.
   - Delegate these operations to an inspected Redis dependency role.

4. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Implement the cleanup with `ansible.builtin.replace` tasks that do not fail when the file is absent.
   - Register changes and notify Redis restart or reload only when configuration changes, subject to the external Redis service implementation.
   - The Chef block itself does not explicitly restart or reload Redis.

5. **`redisio::enable` include** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio::enable` recipe.
   - The recipe file and exact service provider behavior are unavailable.
   - Enable the exact Redis service name discovered from the external Redis dependency; do not infer a service name from this cookbook alone.

The execution tree confirms the five operations above. Detailed resource properties, inline Redis values, and credential findings originate from the recipe-content analysis and are not independently represented in the supplied structured execution summary.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

The dependency declarations are reported from `metadata.rb`; that file is not included in the supplied execution tree.

**System package dependencies**:

- No package resources are present in the visible cookbook.
- Exact package names and versions cannot be established from the supplied files.
- Do not claim direct installation of `redis-server`, `memcached`, or another package by `cookbooks/cache/recipes/default.rb`.

**Service dependencies**:

- Redis service behavior is delegated to `redisio`.
- Memcached service behavior is delegated to `memcached`.
- Exact service names, enablement commands, and Memcached endpoints are unavailable.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value currently used**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the server configured on port `6379`
- **Ansible migration**:
  - Store the password in Ansible Vault as `redis_password`.
  - Render or configure Redis with the vaulted value.
  - Do not commit the plaintext value to variables, defaults, templates, or task output.
  - Use `no_log: true` on tasks that may expose the password.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, private keys, API tokens, or database connection strings were detected in the supplied files. The supplied structured analysis does not include an independent credential-scan result; the finding comes from recipe-content analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis/`
- Redis data directory: not specified
- Redis log file: not specified

**Service endpoints to check**:

- Redis server on port `6379/TCP`
- Memcached endpoint: not specified
- Unix sockets: none specified
- Network bind address: not specified

**Configuration transformations to verify**:

Confirm that `/etc/redis/6379.conf` contains no lines beginning with:

```text
replica-serve-stale-data
replica-read-only
repl-ping-replica-period
client-output-buffer-limit
replica-priority
```

**Templates rendered**:

- None shown in the supplied execution tree.
- Render count: `0`

## Pre-flight checks

```bash
# Inspect the external dependency implementation before migration.
# Confirm the Redis service name, package, user/group, configuration behavior,
# and the Memcached service and endpoint if Memcached is retained.

# Redis service status for the instance on port 6379.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>

# Confirm the Redis instance is listening on TCP port 6379.
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'

# Confirm unauthenticated access is rejected.
redis-cli -p 6379 PING

# Confirm authenticated access using the vaulted password without exposing it.
REDISCLI_AUTH='<redis-password-from-ansible-vault>' redis-cli -p 6379 PING
REDISCLI_AUTH='<redis-password-from-ansible-vault>' redis-cli -p 6379 INFO server
REDISCLI_AUTH='<redis-password-from-ansible-vault>' redis-cli -p 6379 CONFIG GET requirepass

# Confirm the Redis configuration file exists and cleaned directives are absent.
test -f /etc/redis/6379.conf
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify requirepass is configured without printing its value.
grep -nE '^requirepass[[:space:]]+' /etc/redis/6379.conf

# Verify the Redis log directory for the instance on port 6379.
stat -c '%A %U %G %n' /var/log/redis
find /var/log/redis -maxdepth 1 -type f -print

# Expected directory attributes:
# Permissions: 0755
# Owner: redis
# Group: redis

# Review logs for the Redis instance on port 6379.
journalctl -u <redis-service-name> --no-pager -n 100
journalctl -u <redis-service-name> -f

# Memcached checks must use the exact service name and endpoint obtained
# from the external memcached cookbook implementation.
```