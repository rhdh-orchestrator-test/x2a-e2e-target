---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer with declared Memcached and Redis dependencies. The visible recipe explicitly configures one Redis instance on port `6379`, enables password authentication, creates `/var/log/redis`, removes five replication-related directives from `/etc/redis/6379.conf`, and intends to enable Redis. The `memcached`, `redisio`, and `redisio::enable` dependency recipes are not present in the supplied execution tree, so their packages, service names, templates, configuration paths, and endpoints must not be inferred. The Redis password must be migrated from hardcoded Chef configuration into Ansible Vault.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server**: Explicitly configured Redis instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication enabled with `requirepass`; `replicaservestaledata` set to `nil`; five replication-related directives removed after configuration
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`

- **Memcached dependency**: Declared dependency with no visible configuration
  - Location/Path: Not specified
  - Port/Socket: Not specified
  - Key Config: The `memcached` recipe is included, but its recipe file is absent from the supplied execution tree. Package, service name, configuration path, listen address, port, and startup state are unavailable and must not be inferred.

## File Structure

Only files shown in the supplied cookbook execution tree are listed below. Dependency recipes referenced by `include_recipe` are not included because they were reported as not found.

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

No attribute files are shown in the execution tree.

**Files:**
```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` dependency.
   - Defines exactly one Redis server under `node['redisio']['servers']`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the `redisio` dependency.
   - Removes selected replication-related directives from `/etc/redis/6379.conf`.
   - Includes `redisio::enable` to enable Redis.
   - No `.each` loops are present in the supplied recipe.

   **Dependency include: `memcached`**
   - The recipe executes `include_recipe 'memcached'`.
   - The execution tree reports `memcached Recipe file not found`.
   - The supplied cookbook does not establish Memcached package names, service names, listen addresses, ports, configuration files, or startup behavior.
   - Preserve the dependency relationship only if the Memcached dependency is migrated separately.

   **Redis server definition**
   - The recipe assigns:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Represent this as one explicit Redis instance in Ansible.
   - Store the password in Ansible Vault rather than committing the plaintext value.

   **Resource: `directory[/var/log/redis]`**
   - Creates `/var/log/redis`.
   - Uses recursive creation.
   - Sets owner to `redis`.
   - Sets group to `redis`.
   - Sets mode to `0755`.
   - The supplied execution tree does not show creation of the `redis` user or group. Do not add user or group creation unless it is provided by the migrated Redis dependency.

   **Dependency include: `redisio`**
   - The recipe executes `include_recipe 'redisio'`.
   - The execution tree reports `redisio Recipe file not found`.
   - The visible cookbook relies on this dependency to consume `node['redisio']['servers']` and create the Redis configuration.
   - The supplied execution tree does not show Redis package installation, configuration template rendering, service creation, or service startup.

   **Resource: `ruby_block[fix_redis_config]`**
   - Operates on `/etc/redis/6379.conf`.
   - Checks whether the file exists.
   - Reads the complete file.
   - Removes lines matching the following expressions:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - The Ansible implementation should use five `ansible.builtin.lineinfile` tasks with `state: absent`, one for each directive.
   - These tasks should tolerate the file being absent if the Redis dependency has not created it yet.
   - The original Chef resource does not explicitly notify a service. The Ansible migration should define a Redis restart or reload policy after confirming the correct policy with the Redis dependency.

   **Dependency include: `redisio::enable`**
   - The recipe executes `include_recipe 'redisio::enable'`.
   - The execution tree reports `redisio::enable Recipe file not found`.
   - The cookbook intends to enable Redis, but the actual service resource and service name are unavailable.
   - Do not invent a Redis service name. Use the name documented by the migrated `redisio` dependency.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- No package resources are present in the supplied recipe or execution tree.
- Exact package names cannot be established from the supplied data.
- Package installation is presumably delegated to the missing `memcached` and `redisio` dependency recipes.

**Service dependencies**:

- Redis is intended to be enabled by `redisio::enable`.
- The Redis systemd or init service name is not shown.
- Memcached service management is not shown because its recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis client authentication through the `requirepass` configuration setting
- **Ansible migration**: Store the value in Ansible Vault and use the vaulted variable when configuring Redis.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, environment-variable secret references, TLS certificate references, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis/`

**Service endpoints to check**:

- Redis server: TCP port `6379`
- Memcached dependency: No port or socket specified by the supplied cookbook
- Unix sockets: None specified
- Network bind address: Not specified

**Configuration directives to verify**:

- Redis authentication is enabled with `requirepass`.
- The following directives are absent from `/etc/redis/6379.conf`:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- None. No templates are shown in the execution tree.

**Static files deployed**:

- None. No static files are shown in the execution tree.

## Pre-flight checks:

```bash
# Redis instance: verify service status.
# Replace redis with the service name supplied by the migrated redisio dependency.
systemctl status redis
```

```bash
# Redis instance: verify that the configured port is listening.
ss -tlnp | grep ':6379'
netstat -tulpn | grep ':6379'
```

```bash
# Redis instance: verify the configuration file exists.
test -f /etc/redis/6379.conf
```

```bash
# Redis instance: verify the log directory ownership and mode.
stat -c '%A %U %G %n' /var/log/redis
```

Expected output:

```text
drwxr-xr-x redis redis /var/log/redis
```

```bash
# Redis instance: verify password authentication is configured.
# Do not print the password in migration logs.
grep -E '^[[:space:]]*requirepass[[:space:]]+' /etc/redis/6379.conf
```

```bash
# Redis instance: verify authenticated access.
# Supply the password through a protected Ansible Vault-backed value.
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_VAULT>' PING
```

Expected output:

```text
PONG
```

```bash
# Redis instance: verify unauthenticated access is rejected.
redis-cli -p 6379 PING
```

Expected output should indicate that authentication is required, such as:

```text
NOAUTH Authentication required.
```

```bash
# Redis instance: verify the five unwanted directives are absent.
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

Expected result: no matching lines.

```bash
# Redis instance: verify an authenticated INFO request.
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_VAULT>' INFO server
```

```bash
# Redis instance: verify a temporary authenticated key/value operation.
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_VAULT>' SET migration_check ok
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_VAULT>' GET migration_check
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_VAULT>' DEL migration_check
```

Expected results:

```text
OK
"ok"
(integer) 1
```

```bash
# Redis instance: review service logs.
# Replace redis with the service name supplied by the migrated redisio dependency.
journalctl -u redis --no-pager -n 100
```

```bash
# Memcached dependency: no endpoint, package, service name, or configuration
# path is available in the supplied cookbook. Inspect the separately migrated
# memcached dependency before running Memcached-specific status, port, or
# connectivity checks.
```

The supplied cookbook does not provide enough information to perform a Memcached port or health check without inventing configuration.