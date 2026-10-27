---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures caching through the `memcached` and `redisio` dependencies. The analyzed entry recipe defines one Redis instance on port `6379`, configures Redis authentication, creates `/var/log/redis`, includes Redis enablement, and removes five replication-related directives from `/etc/redis/6379.conf`. The dependency recipe implementations are unavailable, so their package names, service names, templates, and Memcached settings require source verification before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis**
  - Purpose: Redis cache service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Log directory: `/var/log/redis`
  - Authentication: Redis `requirepass` configured
  - Configuration value: `replicaservestaledata: nil`
  - Post-configuration cleanup removes:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

**Memcached**:

- The entry recipe includes the `memcached` dependency.
- The Memcached recipe is unavailable in the supplied execution tree.
- Its package name, service name, configuration path, port, templates, and startup behavior require verification from the dependency cookbook.
- No Memcached instance is explicitly configured by the analyzed local recipe.

## File Structure

The execution tree contains one analyzed local recipe. Dependency recipe files are reported as unavailable and are not listed as local cookbook files.

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

```text
```

No provider files are shown or used.

**Templates:**

```text
```

No templates are shown or rendered.

**Attributes:**

```text
```

No attribute files are shown. The Redis server collection is assigned directly inside `cookbooks/cache/recipes/default.rb`.

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in the following order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency.
   - The execution tree reports `memcached Recipe file not found`.
   - Memcached package installation, configuration, service management, and endpoint settings cannot be determined from the supplied source.
   - Assigns one Redis server:
     - Port: `6379`
     - Authentication password: `redis_secure_password_123` in the analyzed recipe
     - `replicaservestaledata`: `nil`
   - The password must be migrated to Ansible Vault, an approved AAP credential, or another protected secret store.
   - Creates `directory[/var/log/redis]`:
     - Path: `/var/log/redis`
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation: enabled
   - Includes the Redis dependency.
   - The execution tree reports `redisio Recipe file not found`.
   - The dependency is expected to create `/etc/redis/6379.conf`, but its package installation, configuration template, service resources, and exact service name require verification.
   - Executes `ruby_block[fix_redis_config]`:
     - Target file: `/etc/redis/6379.conf`
     - Performs no action if the file does not exist.
     - Reads the existing file when present.
     - Removes complete lines beginning with:
       - `replica-serve-stale-data`
       - `replica-read-only`
       - `repl-ping-replica-period`
       - `client-output-buffer-limit`
       - `replica-priority`
     - Writes the modified content back to `/etc/redis/6379.conf`.
   - Includes `redisio::enable`.
   - The intended behavior is to enable Redis at boot, but the exact service resource and service unit name require verification from the `redisio` dependency.

The Ansible implementation should use an explicit Redis instance:

```yaml
redis_instances:
  - port: 6379
    requirepass: "{{ redis_password }}"
    replicaservestaledata: null
```

The Redis log directory can be represented as:

```yaml
- name: Create Redis log directory
  ansible.builtin.file:
    path: /var/log/redis
    state: directory
    owner: redis
    group: redis
    mode: "0755"
    recurse: true
```

The configuration cleanup should occur after the Redis dependency creates the configuration file:

```yaml
- name: Check whether Redis 6379 configuration exists
  ansible.builtin.stat:
    path: /etc/redis/6379.conf
  register: redis_config_file_stat

- name: Remove unsupported Redis replication directives
  ansible.builtin.replace:
    path: /etc/redis/6379.conf
    regexp: '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority).*$\n?'
    replace: ''
  when: redis_config_file_stat.stat.exists
  notify: Restart Redis
```

The exact Redis service name and restart behavior must be verified from the `redisio` dependency and target platform.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0` as reported by the migration analysis; metadata source verification is required.
- `redisio`, with no version constraint as reported by the migration analysis; metadata source verification is required.

**Supported platforms**:

- Ubuntu `>= 18.04` as reported by the migration analysis; metadata source verification is required.
- CentOS `>= 7.0` as reported by the migration analysis; metadata source verification is required.

**System package dependencies**:

- No package resources are present in the analyzed local recipe.
- Exact package names cannot be established because the `memcached` and `redisio` dependency recipes are unavailable.
- Do not add package tasks until the dependency implementations or verified target-platform package mappings have been inspected.

**Service dependencies**:

- Redis is intended to be enabled through `redisio::enable`.
- The Redis service unit name is unavailable.
- Memcached service management is unavailable because the `memcached` recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 file according to the recipe-level migration analysis. This finding requires confirmation against the original recipe source.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None
- **Path**: None

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef node attribute value
- **Configured value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the server listening on port `6379`
- **Ansible migration**:
  - Replace the plaintext value with an Ansible Vault variable, AAP credential, or another approved secret source.
  - Do not place the password in a normal variables file, template, task argument visible in logs, or Git repository.
  - Use `no_log: true` on tasks that may expose the password.

No data bags, encrypted data bags, Chef Vault calls, CyberArk/Conjur integrations, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings were identified in the analyzed recipe.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- Redis runtime data and log locations created by the unavailable `redisio` dependency
- Dependency source for `memcached`
- Dependency source for `redisio`

**Service endpoints to check**:

- Redis TCP port: `6379`
- Unix sockets: None identified
- Network interface binding: Not specified
- Memcached endpoint: Pending dependency source verification

**Templates rendered**:

- None identified
- No `.erb` templates are present in the supplied execution tree
- Dependency template rendering counts: unavailable because dependency recipe files are missing

**Configuration edits to verify**:

The following directive families must be absent from `/etc/redis/6379.conf` after the cleanup task:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Verify the Redis service name after inspecting the redisio dependency
systemctl status <verified-redis-service-name>

# Verify that Redis is listening on port 6379
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'

# Redis connectivity and authentication
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' redis-cli -p 6379 PING
# Expected output: PONG

# Redis server information
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' redis-cli -p 6379 INFO server

# Verify the configured port
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' redis-cli -p 6379 CONFIG GET port
# Expected value: 6379

# Verify that authentication is enabled
grep -E '^[[:space:]]*requirepass[[:space:]]+' /etc/redis/6379.conf

# Verify that the five removed directives are absent
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected result: no matching lines

# Verify the Redis log directory
stat -c '%A %U %G %n' /var/log/redis
# Expected result includes: drwxr-xr-x redis redis /var/log/redis

# Check Redis logs using the verified service name
journalctl -u <verified-redis-service-name> --no-pager -n 100

# Confirm Redis responds to a write/read test
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' redis-cli -p 6379 SET migration_healthcheck ok
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' redis-cli -p 6379 GET migration_healthcheck
# Expected output: ok

# Remove the temporary health-check key
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' redis-cli -p 6379 DEL migration_healthcheck
```

Memcached-specific pre-flight checks cannot be defined accurately until its dependency source is obtained and its package name, service name, configuration path, and port are verified.

Migration sequencing:

1. Obtain and inspect the `memcached` and `redisio` dependency implementations.
2. Verify metadata versions and supported platforms against the original cookbook source.
3. Install and configure the dependencies using verified package and service names.
4. Define the Redis instance on port `6379`.
5. Store the Redis password in Ansible Vault or an AAP-managed credential.
6. Create `/var/log/redis` with owner `redis`, group `redis`, and mode `0755`.
7. Ensure `/etc/redis/6379.conf` exists after Redis dependency configuration.
8. Remove the five replication-related directive lines.
9. Restart or reload Redis only when the configuration changes.
10. Enable the verified Redis service at boot.
11. Run the Redis connectivity, authentication, port, configuration, and log checks.
12. Add Memcached checks only after its dependency behavior has been verified.