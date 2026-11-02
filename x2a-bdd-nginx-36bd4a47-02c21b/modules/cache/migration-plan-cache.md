---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The analyzed execution tree contains only `cookbooks/cache/recipes/default.rb`; dependency recipes are unavailable. The local recipe includes Memcached, configures one Redis server on port `6379` with a hardcoded authentication password, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and includes the Redis enable recipe. No local package, service, template, provider, attribute, or static file resources are present.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server configured by `node['redisio']['servers']`**: Redis cache and authentication service
  - Location/Path: `/etc/redis/6379.conf`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config:
    - Authentication enabled with the current hardcoded password `redis_secure_password_123`
    - `replicaservestaledata`: `nil`
    - Removes these directives from `/etc/redis/6379.conf` when the file exists:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`

- **Memcached service included through `memcached`**: External Memcached dependency
  - Location/Path: Not determinable from the supplied execution tree
  - Port/Socket: Not specified by the analyzed cookbook
  - Key Config: Package, listen address, memory limit, service name, and configuration path are supplied by the separately migrated `memcached` dependency. They must not be invented in this role.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
cookbooks/cache/recipes/default.rb

Providers:

No provider files are shown in the execution tree.

Templates:

No templates are rendered by the analyzed execution flow.

Attributes:

No attribute files are shown. The Redis server configuration is assigned directly in the recipe.

Files:

No static files are deployed by cookbook_file or remote_file.
```

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` cookbook using `include_recipe 'memcached'`.
   - The dependency recipe is not present in the supplied execution tree.
   - The Ansible migration must call the separately migrated Memcached role or task include without assuming package names, ports, service names, or configuration paths.

2. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Assigns one Redis server definition directly to `node['redisio']['servers']`:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - The Ansible equivalent should define exactly one Redis server:
     ```yaml
     redis_servers:
       - port: 6379
         requirepass: "{{ vault_redis_password }}"
         replicaservestaledata: null
     ```
   - Store the password in Ansible Vault rather than in plaintext role source.

3. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Creates the Redis log directory using `directory[/var/log/redis]`.
   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled
   - Direct resource count: one `directory` resource.

4. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `redisio` cookbook using `include_recipe 'redisio'`.
   - The dependency recipe is not present in the supplied execution tree.
   - The separately migrated Redis role must consume the Redis server definition and create `/etc/redis/6379.conf` before the configuration cleanup step.
   - Exact packages, templates, generated configuration, and service resources cannot be confirmed locally.

5. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Runs `ruby_block[fix_redis_config]`.
   - Sets the configuration path to `/etc/redis/6379.conf`.
   - Does nothing when the file does not exist.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Direct resource count: one `ruby_block` resource.
   - Ansible should use scoped `lineinfile` tasks or an equivalent replacement operation, preserving the missing-file behavior with an existence check or `failed_when: false`.
   - The Chef recipe does not explicitly notify or restart Redis. A restart handler should be added only if required by the migrated Redis role.

6. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include `redisio::enable` using `include_recipe 'redisio::enable'`.
   - The dependency recipe is not present in the supplied execution tree.
   - The migrated Redis role must enable and start the Redis service associated with port `6379`.
   - The exact systemd unit name cannot be confirmed. Do not assume a unit such as `redis-server@6379` without verification.

**Iterations**: No `.each` loops are present in the supplied execution tree.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- Not determinable from the local execution tree.
- Package installation is expected to be handled by the external `memcached` and `redisio` cookbooks, whose recipe files are unavailable.

**Service dependencies**:
- Memcached service, referenced through the missing `memcached` recipe
- Redis service for port `6379`, referenced through the missing `redisio` and `redisio::enable` recipes
- Exact service unit names are unavailable from the analyzed files

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value currently present**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the Redis server listening on port `6379`
- **Migration storage**: Move the value to Ansible Vault as `vault_redis_password` and reference it from the Redis role or configuration template.

No Chef data bags, encrypted data bags, Chef Vault items, CyberArk or Conjur calls, environment-variable secrets, TLS certificate references, database connection strings, or other credential sources were detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:
- Redis server: TCP port `6379`
- Memcached service: endpoint not specified by the analyzed cookbook
- Unix sockets: none specified

**Templates rendered**:
- None; render count: `0`

**Redis configuration directives to verify**:

The following directives must be absent as active configuration lines from `/etc/redis/6379.conf`:

```text
replica-serve-stale-data
replica-read-only
repl-ping-replica-period
client-output-buffer-limit
replica-priority
```

## Pre-flight checks

### Redis server configured by `node['redisio']['servers']`

```bash
# Identify the Redis service unit associated with port 6379.
systemctl list-units --type=service | grep -E 'redis|6379'

# Replace <redis-6379-unit> with the verified unit name.
systemctl status <redis-6379-unit>

# Verify that Redis is listening on TCP port 6379.
ss -ltnp | grep ':6379'
nc -zv 127.0.0.1 6379

# Verify the configuration file exists and inspect relevant settings.
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify Redis authentication using the vaulted password.
redis-cli -h 127.0.0.1 -p 6379 -a '<redis-password>' PING
redis-cli -h 127.0.0.1 -p 6379 -a '<redis-password>' INFO server

# Verify the Redis log directory.
stat -c '%A %U %G %n' /var/log/redis
ls -la /var/log/redis

# Check Redis service logs.
journalctl -u <redis-6379-unit> --no-pager -n 100
```

Expected results:

- Redis service is enabled and running.
- TCP port `6379` is listening.
- `PING` returns `PONG`.
- `INFO server` returns Redis server information.
- `/etc/redis/6379.conf` contains `port 6379`.
- The five removed directives do not appear as active configuration lines.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.

### Memcached service included through `memcached`

The analyzed cookbook does not provide a Memcached port, service name, package name, or configuration path. After migrating the external `memcached` dependency, substitute its verified values in the following checks:

```bash
systemctl status <memcached-unit>
ss -ltnp | grep '<memcached-port>'
```

Do not assign a Memcached port or service unit based solely on this cookbook.