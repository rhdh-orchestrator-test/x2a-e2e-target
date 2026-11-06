---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services, primarily one Redis instance on port **6379**, with a hardcoded Redis authentication password. It includes the external `memcached`, `redisio`, and `redisio::enable` recipes, but those dependency recipe files are not present in the supplied execution tree. The Ansible migration must reproduce the local Redis log-directory creation, Redis configuration correction, and dependency-inclusion intent without inventing unavailable package names, service names, templates, or files.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` set to `redis_secure_password_123`; `replicaservestaledata` set to `nil`
  - Log Directory: `/var/log/redis`
  - Log Directory Owner/Group: `redis:redis`
  - Log Directory Mode: `0755`
  - Removed Configuration Directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

- **Memcached**: Included external recipe with no locally verifiable instance configuration
  - Location/Path: Not available
  - Port/Socket: Not available
  - Key Config: Package, service, port, and configuration details cannot be determined because the external recipe is not present

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
cookbooks/cache/recipes/default.rb

Providers:
None

Templates:
None

Attributes:
None

Files:
None
```

The following files are intentionally excluded because they are not shown as executed or referenced in the supplied execution tree:

- `metadata.rb`
- External `memcached` recipe files
- External `redisio` recipe files
- External `redisio::enable` recipe files
- Templates or providers from dependency cookbooks

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Does not locally define the memcached package, configuration, port, service, or templates.
   - Assigns one Redis server configuration to the `redisio` node attributes:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - The dependency recipe is unavailable, so its package installation, configuration template rendering, and service-resource behavior cannot be determined.
   - Defines `ruby_block[fix_redis_config]`, which:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Reads the file when present.
     - Removes complete lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Writes the modified contents back to `/etc/redis/6379.conf`.
   - Includes the external `redisio::enable` recipe.
   - The exact service enablement and startup behavior cannot be determined because the dependency recipe is unavailable.

   **Ansible migration resources and actions**:
   - Use `ansible.builtin.file` for `/var/log/redis` with:
     - `state: directory`
     - `owner: redis`
     - `group: redis`
     - `mode: '0755'`
   - Use explicit `ansible.builtin.lineinfile` tasks or one controlled configuration-editing task to remove each of the five directives from `/etc/redis/6379.conf`.
   - Make configuration cleanup safe when `/etc/redis/6379.conf` does not exist.
   - Confirm the Redis package and service name before adding package, service, restart, reload, enablement, or startup tasks.
   - Store the Redis password in Ansible Vault rather than committing the plaintext value.
   - Iterations: No `.each` loops are present.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- None are declared in the supplied execution tree.
- Package installation is delegated to the missing external recipes.
- No package name can be verified from the supplied files.

**Service dependencies**:

- Redis is intended to be enabled through `redisio::enable`.
- The exact Redis systemd service name is unavailable.
- Memcached service behavior is unavailable because its recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file.

**Source**:

- **Provider**: Hardcoded in Chef recipe source
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef attribute assignment
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Configures authentication for the Redis instance listening on port `6379`
- **Migration recommendation**: Store the value in Ansible Vault, for example as `redis_password`, and use the vaulted variable when configuring Redis. Do not commit the plaintext password to the Ansible repository.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secrets, TLS certificate references, private keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- **Redis instance on port 6379**: TCP port `6379`
- Unix sockets: None identified
- Network interface binding: Not specified

**Templates rendered**:

- None

**Static files deployed**:

- None

**Redis configuration directives to verify as absent from `/etc/redis/6379.conf`**:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Verify the Redis configuration file exists
test -f /etc/redis/6379.conf

# Verify the Redis instance on TCP port 6379 is listening
ss -ltnp | grep ':6379'

# Alternative listener check
netstat -ltnp 2>/dev/null | grep ':6379'

# Redis health check
# Prefer REDISCLI_AUTH or another protected secret source over a plaintext command argument.
export REDISCLI_AUTH='redis_secure_password_123'
redis-cli -p 6379 PING
# Expected output:
# PONG
unset REDISCLI_AUTH

# Verify Redis server information
export REDISCLI_AUTH='redis_secure_password_123'
redis-cli -p 6379 INFO server
unset REDISCLI_AUTH

# Verify the configured Redis port
export REDISCLI_AUTH='redis_secure_password_123'
redis-cli -p 6379 CONFIG GET port
unset REDISCLI_AUTH
# Expected port value:
# 6379

# Verify the Redis log directory
stat -c '%A %U %G %n' /var/log/redis
# Expected:
# mode 0755, owner redis, group redis

# Verify the Redis configuration does not contain removed directives
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected output:
# no matching lines

# Verify Redis authentication configuration.
# The exact representation may vary by Redis package or role.
grep -E '^(requirepass|masterauth)' /etc/redis/6379.conf

# Confirm the Redis process is running
pgrep -a redis

# Confirm the Redis service name supplied by the selected package or Ansible role.
# Do not substitute an unverified service name.
systemctl status <confirmed-redis-service-name>
systemctl is-enabled <confirmed-redis-service-name>
```

No locally verifiable memcached endpoint, configuration path, package, or service name is available for pre-flight validation.