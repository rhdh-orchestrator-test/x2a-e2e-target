---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook manages Redis and requests Memcached through the external `redisio` and `memcached` cookbooks. The local execution tree contains only `cache::default`; dependency recipe files are unavailable. The confirmed local resources create `/var/log/redis` and execute `ruby_block[fix_redis_config]`. Source inspection reports one Redis instance on port `6379`, Redis authentication, and removal of five directives from `/etc/redis/6379.conf`, but these details require verification against the complete recipe analysis. Memcached package, service, port, and configuration details are not available locally and must be confirmed before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server**: Redis cache instance configured through the external `redisio` cookbook
  - Location/Path: `/etc/redis/6379.conf`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Source inspection reports Redis authentication and removal of the following directives: `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`. These details require confirmation from the complete recipe analysis.
  - Service name: Not confirmed; `redis-server` is a common platform value but must not be assumed.

- **Memcached dependency**: Memcached requested through the external `memcached` cookbook
  - Location/Path: Not specified in the available local execution data
  - Port/Socket: Not specified in the available local execution data
  - Key Config: Package name, service name, configuration path, and port must be obtained from the external cookbook equivalent or deployment requirements.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

No provider, template, attribute, or static file is shown as used by the execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe. The dependency recipe is not present in the analyzed local source, so its package, service, port, and configuration behavior cannot be confirmed.
   - Configures the Redis server attribute collection before including `redisio`. Source inspection reports one Redis configuration object using port `6379`, authentication, and an unset `replicaservestaledata` value. These attribute details require confirmation against the complete recipe analysis.
   - Creates `/var/log/redis` through `directory[/var/log/redis]`. Ownership, group, mode, and recursive settings are reported by the plan but are not confirmed by the available structured analysis and must be verified before implementation.
   - Attempts to include the external `redisio` recipe. Redis package installation and initial configuration are delegated to that dependency.
   - Executes `ruby_block[fix_redis_config]`, confirmed by the execution tree. Source inspection reports that it checks `/etc/redis/6379.conf` and removes these directives:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Attempts to include `redisio::enable`, which is intended to enable Redis as a system service. The exact service resource and service name are not available locally.

   **Resource counts:**
   - `directory[/var/log/redis]`: 1
   - `ruby_block[fix_redis_config]`: 1

   **Iterations:** None. No `.each` loops are present in the analyzed execution tree.

**Execution order:**

1. Include `memcached`.
2. Configure the reported Redis server attributes.
3. Create `/var/log/redis`.
4. Include `redisio`.
5. Remove the reported replication-related directives from `/etc/redis/6379.conf`.
6. Include `redisio::enable`.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- No local `package` resources are present.
- The Memcached and Redis package names are not available in the analyzed local execution tree.
- Do not assume package names solely from the cookbook names; obtain them from the external cookbook equivalents or target-platform requirements.

**Service dependencies**:
- Redis service enablement is delegated to `redisio::enable`; the service name is not confirmed.
- Memcached service management is delegated to the unavailable `memcached` dependency recipe.

## Credentials

**Detection Summary**: 1 credential reported by source inspection in 1 file; the available structured validation summary does not independently confirm it.

**Source**:
  - **Provider**: Hardcoded in the reported Chef recipe
  - **URL**: None detected
  - **Path**: Redis configuration; no external secret path detected

### Redis authentication password

- **Variable(s)**: Reported as `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded literal; confirmation required
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the reported Redis instance on port `6379`
- **Ansible migration**:
  - Store the confirmed password in Ansible Vault or an AAP credential.
  - Reference the vaulted variable when rendering Redis configuration.
  - Do not place the literal in role defaults, normal variable files, templates, Git, or command-line arguments.
  - Avoid exposing the password in migration logs or shell history.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, or environment-variable secret reference was identified.

No TLS certificate, private key, database connection string, API token, or SSH credential was detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

The following paths are not confirmed by the local recipe and require verification from the external implementations:
- Redis data directory
- Redis log file
- Memcached configuration file
- Memcached log file

**Service endpoints to check**:
- Redis server: TCP `6379`
- Memcached dependency: port not specified
- Unix sockets: none specified

**Templates rendered**:
- None; no local templates are shown in the execution tree.
- Render count: `0`

## Pre-flight checks

```bash
# Confirm the target Redis service name before running these commands.
systemctl status <confirmed-redis-service>
systemctl is-enabled <confirmed-redis-service>
systemctl is-active <confirmed-redis-service>

# Redis server endpoint.
ss -tlnp | grep ':6379'
nc -zv 127.0.0.1 6379

# Confirm the Redis configuration file.
test -f /etc/redis/6379.conf

# Confirm that the reported directives were removed.
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Confirm the Redis log directory and reported ownership requirements
# only after ownership and mode are verified from the complete recipe analysis.
stat -c '%A %U %G %n' /var/log/redis

# Inspect Redis logging and endpoint settings.
grep -nE '^(logfile|dir|port|requirepass)' /etc/redis/6379.conf

# Use the confirmed Redis service name for logs.
journalctl -u <confirmed-redis-service> --no-pager -n 50

# Validate Redis authentication without exposing the password.
read -s REDIS_PASSWORD
redis-cli -h 127.0.0.1 -p 6379 --no-auth-warning -a "$REDIS_PASSWORD" PING
redis-cli -h 127.0.0.1 -p 6379 --no-auth-warning -a "$REDIS_PASSWORD" INFO server
unset REDIS_PASSWORD

# Confirm the Memcached service name, package, configuration path, and port
# from the external cookbook equivalent before running these checks.
systemctl status <confirmed-memcached-service>
ss -tlnp | grep ':<confirmed-memcached-port>'
printf 'version\r\n' | nc 127.0.0.1 <confirmed-memcached-port>
```