---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching through the external `memcached` and `redisio` Chef cookbooks. The local recipe defines one Redis server on TCP port `6379`, enables authentication, creates `/var/log/redis`, includes Redis enablement, and removes five replication-related directives from `/etc/redis/6379.conf`. Memcached configuration is delegated to the external `memcached` cookbook and its port, packages, service details, and configuration files must be obtained from that dependency.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance configured through `redisio`
  - Location/Path: `/etc/redis/6379.conf`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with the hardcoded source password `redis_secure_password_123`; `replicaservestaledata` is explicitly unset/null; log directory owner `redis`, group `redis`, mode `0755`, recursive creation; Redis is enabled at boot
  - Post-configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`

- **Memcached**: Memcached service included through the external `memcached` cookbook
  - Location/Path: Not specified by the local cookbook
  - Port/Socket: Not specified by the local cookbook
  - Key Config: No local package, service, port, authentication, or configuration settings; preserve the external dependency and obtain its implementation details from the `memcached` cookbook

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only the local recipe shown in the execution tree is listed. Dependency recipes were referenced but were not present in the execution tree.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are shown or used by the analyzed local cookbook.

**Templates:**
```text
```

No local templates are shown or rendered.

**Attributes:**
```text
```

No local attribute files are shown. Redis settings are assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are deployed by the analyzed cookbook.

## Module Explanation

The cookbook performs operations in the following execution order:

1. **Default recipe** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The execution tree reports `memcached Recipe file not found`; the dependency must be represented by an equivalent Ansible role or imported task.
   - Defines one Redis server entry:
     ```ruby
     {
       'port' => '6379',
       'requirepass' => 'redis_secure_password_123',
       'replicaservestaledata' => nil
     }
     ```
   - Creates `/var/log/redis` with `directory[/var/log/redis]`.
   - Includes the external `redisio` recipe after the Redis settings have been assigned.
   - Executes `ruby_block[fix_redis_config]` after Redis configuration generation.
   - Includes `redisio::enable` to enable Redis at boot.

2. **Memcached dependency** (`memcached` external recipe; source not present):
   - Provides Memcached installation, configuration, and service management.
   - Package names, service details, configuration paths, ports, and templates are not defined by the local cookbook and must not be inferred.
   - The local recipe does not define any Memcached instances beyond this dependency inclusion.

3. **Redis dependency** (`redisio` external recipe; source not present):
   - Consumes the Redis server collection assigned by the default recipe.
   - Configures one Redis instance with the actual name **Redis server on port 6379**:
     - Port: `6379`
     - Authentication password: migrate from the source hardcoded value to Ansible Vault or another protected secret source
     - `replicaservestaledata`: unset/null
   - Generates or manages `/etc/redis/6379.conf`.
   - External package names, service unit names, generated templates, and provider files are not available in the local execution tree.

4. **Redis configuration cleanup** (`ruby_block[fix_redis_config]` in `cookbooks/cache/recipes/default.rb`):
   - Sets the target file to `/etc/redis/6379.conf`.
   - Does nothing if the file does not exist.
   - Reads the complete configuration file.
   - Removes complete lines matching:
     ```text
     ^replica-serve-stale-data.*$
     ^replica-read-only.*$
     ^repl-ping-replica-period.*$
     ^client-output-buffer-limit.*$
     ^replica-priority.*$
     ```
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - The Ansible equivalent should remove each directive with `ansible.builtin.lineinfile` using `state: absent`, after the Redis dependency has generated the file.
   - Restart or reload Redis only when the effective configuration changes.

5. **Redis enablement** (`redisio::enable` external recipe; source not present):
   - Enables the Redis service at boot.
   - Ensures Redis is started after configuration deployment.
   - Uses the service name supplied by the migrated Redis implementation because the local cookbook does not specify the unit name.

**Resource counts in the local recipe**:
- `directory`: 1 — `/var/log/redis`
- `ruby_block`: 1 — `fix_redis_config`
- Local templates rendered: 0
- Local static files deployed: 0

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**System package dependencies**:
- No package resources are present in the local recipe.
- Package installation is delegated to the external `memcached` and `redisio` recipes.
- Exact package names are not available from the analyzed local cookbook and must be verified from the external cookbook implementations.

**Service dependencies**:
- Memcached service behavior is supplied by the external `memcached` cookbook.
- Redis service behavior and enablement are supplied by the external `redisio` and `redisio::enable` recipes.
- Redis configuration cleanup runs after `redisio` generates `/etc/redis/6379.conf`.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: `cookbooks/cache/recipes/default.rb`; ultimately associated with Redis configuration `/etc/redis/6379.conf`

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded recipe value `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis server on port `6379`
- **Migration handling**:
  - Store the password in Ansible Vault or an approved AAP credential or secret mechanism.
  - Do not place the plaintext value in `group_vars`, `host_vars`, rendered logs, or an unencrypted defaults file.
  - Pass the protected value to the Redis configuration task or role.
  - Avoid printing the password during validation.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, AWS Secrets Manager, environment-variable secret, TLS certificate, private key, or database connection string was detected.

## Checks for the Migration

**Files to verify**:
- `/var/log/redis`
- `/etc/redis/6379.conf`

The Redis data directory and exact Redis log file are not specified by the local cookbook and must be obtained from the external `redisio` implementation.

**Service endpoints to check**:
- Redis server on port `6379`
- Memcached: port not specified by the local cookbook
- Unix sockets: none specified

**Templates rendered**:
- Local templates: 0
- External Memcached templates: unknown; dependency source must be analyzed
- External Redis templates: unknown; dependency source must be analyzed

## Pre-flight checks:

### Redis server on port 6379

```bash
# Service status; replace redis if the migrated role uses a different unit name
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Confirm Redis is listening on TCP port 6379
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'

# Validate the configuration file
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Confirm the five incompatible directives are absent
! grep -qE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Test authenticated access without exposing the password in shell history
read -s REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD

# Test that unauthenticated access is rejected
redis-cli -p 6379 PING

# Verify log directory ownership and permissions
stat -c '%A %U %G %n' /var/log/redis

# Inspect Redis logs; replace redis with the migrated service unit name if required
journalctl -u redis --no-pager -n 50
```

Expected results:
- Redis is enabled and active.
- Redis listens on TCP port `6379`.
- Authenticated `redis-cli` access returns `PONG`.
- Unauthenticated access returns an authentication error rather than `PONG`.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- The five replication-related directives are absent from `/etc/redis/6379.conf`.

### Memcached

```bash
# Inspect the external Memcached service
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
systemctl cat memcached

# Verify the port shown by the external service configuration
ss -tlnp | grep memcached
```

The exact Memcached port, package, service configuration, and endpoint must be documented after the external `memcached` dependency has been analyzed.