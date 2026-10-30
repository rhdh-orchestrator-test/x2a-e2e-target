---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures Redis and includes Memcached through external cookbook dependencies. It creates `/var/log/redis`, configures one Redis instance on port `6379` with authentication, removes selected replication-related directives from `/etc/redis/6379.conf`, and enables Redis. The `memcached` and `redisio` dependency recipe files are unavailable, so their package names, service units, configuration paths, and Memcached endpoint details must be resolved before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Log directory: `/var/log/redis`
  - Authentication: `requirepass` set to a vaulted equivalent of `redis_secure_password_123`
  - `replicaservestaledata`: Explicitly configured as `nil`, equivalent to unset or omitted
  - Removed directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

- **Memcached instance**: Included through the external `memcached` cookbook
  - Location/Path: Not specified in the analyzed files
  - Port/Socket: Not specified in the analyzed files
  - Package: Not specified in the analyzed files
  - Service name: Not specified in the analyzed files
  - Configuration: Resolve from the `memcached` dependency version used by the target Ansible environment

Do not infer Memcached package, service, port, or configuration values from this cookbook alone.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only files shown in the supplied execution tree are listed below. Dependency recipe files are referenced by the cookbook but were not found and are not listed as executable files.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
None listed in the execution tree.
```

**Templates:**
```text
None listed in the execution tree.
```

**Attributes:**
```text
None listed in the execution tree.
```

**Files:**
```text
None listed in the execution tree.
```

The cookbook metadata file was inspected for service identification and dependencies, but it is not an executable recipe and is intentionally excluded from the required executable file list.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe. The dependency recipe was not available in the execution tree.
   - Sets `node['redisio']['servers']` to one Redis configuration item:
     - Port: `6379`
     - Authentication password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation enabled
   - Includes the external `redisio` recipe. The dependency recipe was not available in the execution tree.
   - Removes complete matching lines from `/etc/redis/6379.conf` when the file exists:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Includes `redisio::enable` to enable Redis. The dependency recipe was not available in the execution tree.
   - Resource summary:
     - `directory`: 1, for `/var/log/redis`
     - `ruby_block`: 1, for `fix_redis_config`
     - `include_recipe`: 3, for `memcached`, `redisio`, and `redisio::enable`
   - The Chef `ruby_block` does not explicitly notify or restart Redis after changing `/etc/redis/6379.conf`. Preserve this behavior unless the resolved dependency implementation requires a handler.

The external dependency execution details are unavailable:

- `memcached Recipe file not found`
- `redisio Recipe file not found`
- `redisio::enable Recipe file not found`

The Ansible implementation must resolve dependency-specific package names, service units, users, groups, templates, configuration paths, and endpoint values before deployment. No package or service name should be invented from the visible recipe.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package resources are present in the visible cookbook.
- Package names installed by `memcached` and `redisio` cannot be established because their recipe files are unavailable.
- Resolve and verify the actual package names from the dependency implementations before migration.

**Service dependencies**:

- `memcached` recipe: unavailable
- `redisio` recipe: unavailable
- `redisio::enable` recipe: unavailable
- Redis configuration path explicitly manipulated by the visible recipe: `/etc/redis/6379.conf`

## Credentials

**Detection Summary**: 1 credential detected across 1 recipe file.

**Source**:

- **Provider**: Hardcoded
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Value in Chef source**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the instance listening on port `6379`

Store the password in Ansible Vault or the approved secret-management system. Do not place it directly in the Ansible role or committed variables. Render it into the Redis configuration with restrictive permissions and prevent exposure through task output, debug output, shell history, CI logs, or unencrypted inventory variables.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk reference, environment-variable secret reference, TLS certificate reference, database connection string, or additional credential namespace was identified.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

The following dependency-controlled paths cannot be confirmed from the visible cookbook:

- Memcached configuration file
- Memcached log file
- Redis service unit file
- Redis data directory
- Redis PID or socket path

**Service endpoints to check**:

- Redis TCP port `6379`
- Memcached port: unresolved from the analyzed files
- Unix sockets: None specified
- Network interface binding: Not specified

**Templates rendered**:

- None listed in the execution tree
- Render count: `0`

**Resource counts**:

- `directory`: `1`
- `ruby_block`: `1`
- `include_recipe`: `3`

The structured resource listing mentions a `group['redis']` resource, but it is not present in the supplied execution tree. Obtain Redis user and group requirements from the resolved `redisio` dependency rather than adding an unverified standalone group task.

## Pre-flight checks

### Redis instance on port 6379

Resolve the actual Redis service unit from the `redisio` dependency, then run:

```bash
systemctl status <redis-6379-service-unit>
systemctl is-enabled <redis-6379-service-unit>
systemctl is-active <redis-6379-service-unit>
```

Verify the listener:

```bash
ss -ltnp | grep ':6379'
```

Expected result: a Redis process is listening on TCP port `6379`.

Validate unauthenticated access behavior:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication error or `NOAUTH` response.

Validate authenticated access using a protected secret-injection mechanism:

```bash
redis-cli -p 6379 -a '<redis-password>' PING
```

Expected result:

```text
PONG
```

Validate the configuration file:

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf
```

Verify that the selected directives are absent:

```bash
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result: no matching lines are returned.

Validate the Redis log directory:

```bash
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis
```

Expected result:

```text
drwxr-xr-x redis redis /var/log/redis
```

Validate Redis read/write functionality:

```bash
redis-cli -p 6379 -a '<redis-password>' SET chef_ansible_migration_check ok
redis-cli -p 6379 -a '<redis-password>' GET chef_ansible_migration_check
redis-cli -p 6379 -a '<redis-password>' DEL chef_ansible_migration_check
```

Expected results:

- `SET`: `OK`
- `GET`: `ok`
- `DEL`: `1`

Validate the configured password through a protected mechanism:

```bash
redis-cli -p 6379 CONFIG GET requirepass
```

Check Redis logs:

```bash
find /var/log/redis -maxdepth 1 -type f -print
journalctl -u <redis-6379-service-unit> --no-pager -n 100
```

Check for configuration parsing failures, authentication errors, and startup failures. The password must not be exposed in shell history, command output, or CI logs.

### Memcached instance

The cookbook includes Memcached, but its exact instance name, service unit, port, package, and configuration path are unavailable. Resolve those values from the `memcached` dependency before running the following checks:

```bash
systemctl status <memcached-service-unit>
systemctl is-enabled <memcached-service-unit>
systemctl is-active <memcached-service-unit>
ss -ltnp | grep '<memcached-port>'
```

Replace the placeholders only with values verified from the actual `memcached` dependency implementation. Do not assume Memcached values from the visible `cache` recipe.