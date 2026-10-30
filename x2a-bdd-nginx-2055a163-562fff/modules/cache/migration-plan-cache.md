---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures a cache layer through external Memcached and Redis recipes. Its supplied execution tree contains one Redis configuration on port `6379`, creation of `/var/log/redis`, a `ruby_block[fix_redis_config]`, and inclusions of `memcached`, `redisio`, and `redisio::enable`. The detailed Redis settings and hardcoded password are reported by the migration source but are not independently confirmed by the supplied structured analysis. External cookbook behavior, package names, service names, Memcached settings, and generated Redis templates must be verified before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port `6379`**: Redis cache instance configured through the external `redisio` cookbook.
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Reported `requirepass` value; `replicaservestaledata` reported as `nil`; exact values are not confirmed by the supplied structured analysis.
  - Log Directory: `/var/log/redis`, owned by `redis:redis` with mode `0755`
  - Configuration Cleanup: The reported `fix_redis_config` behavior removes selected replication directives when the configuration file exists. The exact block implementation is not confirmed by the supplied structured analysis.

- **Memcached**: Included through the external `memcached` recipe.
  - Location/Path: Not specified
  - Port/Socket: Not specified
  - Key Config: Package, service name, configuration path, bind address, port, and logging configuration must be obtained from the external Memcached cookbook or role.

## File Structure

Only files shown in the supplied execution tree are listed below.

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

No attribute files are shown. The Redis server collection is reported as being assigned directly in `cookbooks/cache/recipes/default.rb`, but that assignment is not present in the supplied structured analysis.

**Files:**
```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The Memcached recipe is not present in the supplied execution tree.
   - Its packages, templates, service resources, configuration path, port, and service name cannot be derived from this cookbook.
   - The Ansible migration must use the corresponding external Memcached role or collection after verifying its settings.

2. **default — Redis server configuration** (`cookbooks/cache/recipes/default.rb`):
   - The migration source reports one Redis server definition on port `6379`.
   - The reported configuration path is `/etc/redis/6379.conf`.
   - The reported settings include a `requirepass` value and `replicaservestaledata: nil`.
   - These attribute values are not confirmed by the supplied structured analysis and must be verified against the recipe source or dependency behavior.
   - The Ansible representation, if confirmed, should contain one Redis instance:
     ```yaml
     redis_servers:
       - port: 6379
         requirepass: "{{ redis_password }}"
         replicaservestaledata: null
     ```
   - Any Redis password must be stored in Ansible Vault, an AAP credential, or another approved secret store.

3. **default — Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates `directory[/var/log/redis]`.
   - Sets owner to `redis`.
   - Sets group to `redis`.
   - Sets mode to `0755`.
   - Enables recursive parent-directory creation.
   - The Redis system group must be supplied by the Redis package or dependency role; no `group[redis]` Chef resource is confirmed in the supplied execution tree.

4. **default — Redis installation and configuration** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The `redisio` recipe is not present in the supplied execution tree.
   - Its package names, configuration templates, service resources, data paths, log paths, and port-binding behavior cannot be confirmed from this cookbook.

5. **default — Redis configuration cleanup** (`cookbooks/cache/recipes/default.rb`):
   - Contains `ruby_block[fix_redis_config]`.
   - The migration source reports that the block operates on `/etc/redis/6379.conf` when the file exists.
   - The reported directives removed by the block are:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The exact file path, regular expressions, and removal behavior are not confirmed by the supplied structured analysis.
   - Prefer managing the configuration declaratively with an Ansible template.
   - If the external Redis role owns the file, remove matching lines after generation with `ansible.builtin.replace` or `ansible.builtin.lineinfile`.
   - Restart or reload Redis only when required by the selected role and only when the configuration changes.

6. **default — Redis service enablement** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio::enable` recipe.
   - The `redisio::enable` recipe is not present in the supplied execution tree.
   - The exact Redis service unit name must be obtained from the external Redis role or target distribution.
   - The Ansible equivalent must enable and start the verified Redis service.

## Dependencies

**External cookbook dependencies**:

- `memcached`; the reported constraint is `~> 6.0`, but this version is not confirmed by the supplied structured analysis.
- `redisio`; no confirmed version constraint is available from the supplied structured analysis.
- `redisio::enable`; included as a recipe from `redisio`.

**System package dependencies**:

- No package resources are present in the supplied recipe.
- Exact package names cannot be confirmed because the external dependency recipes are unavailable.
- Do not assume package names such as `redis-server` or `memcached` until the dependency role and target operating system are verified.

**Service dependencies**:

- Memcached service provided by the external `memcached` recipe.
- Redis service provided and enabled by the external `redisio` and `redisio::enable` recipes.
- Reported Redis configuration path: `/etc/redis/6379.conf`.
- Reported Redis port: `6379`.

## Credentials

**Detection Summary**: 1 credential reported in 1 file; the credential finding is not represented in the supplied structured analysis and requires verification.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected; the value is reportedly assigned directly to the Redis server attributes

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext Chef attribute value
- **Configured value**: `redis_secure_password_123` as reported; verify before migration
- **Usage context**: Redis `requirepass` authentication for the Redis instance on port `6379`
- **Migration handling**:
  - Move the value to Ansible Vault, an AAP credential, or another approved secret store.
  - Do not commit the literal password to group variables, role defaults, or templates.
  - Render it with restrictive permissions, normally `0600` where supported.
  - Use `no_log: true` for secret-handling tasks.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret, TLS certificate, private key, or database connection string was detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`
- Redis data directory, once supplied by the external Redis role
- Redis log file, once supplied by the external Redis role
- Redis service unit, once supplied by the external Redis role
- Memcached configuration file, once supplied by the external Memcached role
- Memcached log file, once supplied by the external Memcached role

**Service endpoints to check**:

- Redis instance: TCP port `6379`
- Memcached instance: endpoint not specified and must be obtained from the external role
- Unix sockets: none specified
- Network interfaces: none specified

**Templates rendered**:

- Cookbook templates: none shown or rendered.
- Redis configuration template: expected to be supplied by the unavailable `redisio` dependency; path and render count are unknown.
- Memcached templates: supplied by the unavailable `memcached` dependency; path and render count are unknown.

## Pre-flight checks

```bash
# Confirm the cookbook recipe is present
test -f cookbooks/cache/recipes/default.rb

# Redis instance on TCP port 6379
test -f /etc/redis/6379.conf
ss -ltnp | grep ':6379'
lsof -nP -iTCP:6379 -sTCP:LISTEN

# Verify the reported Redis configuration
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf

# Verify the reported directives are absent after configuration cleanup
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Expected result: no matching lines

# Verify Redis log directory ownership and permissions
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis
sudo -u redis test -w /var/log/redis

# Expected result:
# drwxr-xr-x redis redis /var/log/redis

# Verify Redis service status using the service name supplied by the external role
systemctl status <verified-redis-service>
systemctl is-enabled <verified-redis-service>
systemctl is-active <verified-redis-service>

# Verify Redis authentication without exposing the password in shell history
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" PING

# Expected output:
# PONG

# Verify unauthenticated access is rejected
redis-cli -h 127.0.0.1 -p 6379 PING

# Expected result: an authentication error rather than PONG

# Verify authenticated Redis server information
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" INFO server

# Identify Redis logs using the verified service name
systemctl cat <verified-redis-service>
journalctl -u <verified-redis-service> --no-pager -n 100

# Memcached instance
# Obtain the package, service name, configuration path, bind address,
# port, socket, and log path from the external Memcached role before running checks.
systemctl status <verified-memcached-service>
systemctl is-enabled <verified-memcached-service>
systemctl is-active <verified-memcached-service>
ss -ltnp | grep ':<verified-memcached-port>'
```

