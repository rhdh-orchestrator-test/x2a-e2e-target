---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The local `cache::default` recipe includes Memcached, directly assigns one Redis server on port `6379` with authentication, creates `/var/log/redis`, includes Redis setup, removes replication-related directives from `/etc/redis/6379.conf`, and finally enables Redis. The migration should preserve this execution order while replacing Chef dependencies with an approved Ansible role or explicit tasks. Redis configuration details, including the port, password, directory permissions, and cleanup directives, are recipe-source findings and should be confirmed against the source before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Authenticated Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Log directory: `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is configured; `replicaservestaledata` is assigned `nil`; the recipe removes selected replication-related directives if present
  - Configuration details requiring source confirmation: password value, directory ownership and permissions, and exact cleanup behavior

- **Memcached**: External dependency included by the local recipe
  - Location/Path: Not available in the supplied execution tree
  - Port/Socket: Not available in the supplied execution tree
  - Key Config: The local recipe includes `memcached`, but the execution tree reports `memcached Recipe file not found`; no local Memcached instance details are available

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

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

No templates are shown or rendered.

**Attributes:**

```text
```

No attribute files are shown. The Redis server collection is assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**

```text
```

No static files are deployed by the local cookbook recipe.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The execution tree reports `memcached Recipe file not found`; its packages, service name, configuration path, port, and templates are unavailable.
   - Directly assigns the Redis server collection in the recipe:
     - Redis server on port `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - These Redis assignment details are recipe-source findings and are not attribute-file definitions. Confirm them against the source before migration.
   - Creates `/var/log/redis` through `directory[/var/log/redis]`.
   - The recipe-source analysis reports owner `redis`, group `redis`, mode `0755`, and recursive creation. These settings require confirmation because they are not present in the supplied structured execution summary.
   - Includes the external `redisio` recipe.
   - The execution tree reports `redisio Recipe file not found`; its packages, configuration templates, service resources, and exact service name are unavailable.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - The recipe-source analysis reports that the block checks whether the file exists, removes lines beginning with the following directives, and writes the file back:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - These target path and directive details require confirmation against the recipe source because they are not present in the supplied structured execution summary.
   - Includes the external `redisio::enable` recipe last.
   - The execution tree reports `redisio::enable Recipe file not found`; the exact service name must be confirmed from the selected Ansible role or target operating system.
   - No `.each` loops are present in the supplied local recipe, so there are no additional iterations to expand.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package resources are declared by the local recipe.
- No package names are available or verified because package installation is delegated to the unavailable external `memcached` and `redisio` recipes.
- Do not invent package names from this cookbook alone.

**Service dependencies**:

- Redis installation and configuration are delegated to `redisio`.
- Redis enablement is delegated to `redisio::enable`.
- Memcached installation and service management are delegated to `memcached`.
- Exact system service names are unavailable in the supplied execution tree.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value in Chef source**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the instance configured on port `6379`
- **Ansible migration requirement**: Store the password in Ansible Vault or an approved external secret provider. Do not commit the plaintext value to `group_vars`, `host_vars`, or an ordinary YAML variable file.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret reference, TLS certificate reference, or database connection string was detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis TCP port `6379`
- No Unix socket is configured or referenced by the local recipe.
- No bind address or network interface is configured by the local recipe.
- Memcached endpoint: unavailable until the external dependency is inspected.

**Configuration directives to verify for Redis server on port 6379**:

- The generated configuration contains the Redis authentication setting.
- Active lines beginning with the following directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- Local cookbook: none.
- External `redisio` templates: unavailable; render count cannot be determined from the supplied execution tree.
- External `memcached` templates: unavailable; render count cannot be determined from the supplied execution tree.

## Pre-flight checks

```bash
# Redis server instance: port 6379
# Replace redis with the exact service name supplied by the selected Ansible Redis role.
systemctl status redis

# Verify a Redis process is running.
pgrep -a redis-server

# Verify TCP port 6379 is listening.
ss -ltnp | grep ':6379'

# Alternative port check.
lsof -iTCP:6379 -sTCP:LISTEN

# Verify the Redis configuration file exists.
test -f /etc/redis/6379.conf

# Verify the Redis log directory.
stat -c '%A %U:%G %n' /var/log/redis
# Expected from recipe-source analysis: drwxr-xr-x redis:redis /var/log/redis

# Inspect the configured Redis port.
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' /etc/redis/6379.conf

# Confirm that the cleanup directives are absent.
! grep -E '^[[:space:]]*(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)([[:space:]]|$)' /etc/redis/6379.conf

# Test Redis authentication and responsiveness.
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' PING
# Expected: PONG

# Test an authenticated write/read operation.
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' SET migration_check cache-ok
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' GET migration_check
# Expected: cache-ok

# Remove the migration test key.
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' DEL migration_check

# Verify Redis server information.
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' INFO server | grep -E 'redis_version|tcp_port'

# Check recent Redis service logs.
journalctl -u redis --since "15 minutes ago" --no-pager

# Memcached checks are intentionally omitted.
# The external memcached dependency does not provide an instance name,
# service name, port, configuration path, or package name in the supplied data.
```