---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook includes the external `memcached`, `redisio`, and `redisio::enable` recipes, but those recipe files are unavailable in the supplied execution tree. The only directly confirmed resources are `directory[/var/log/redis]` and `ruby_block[fix_redis_config]`. The cookbook is intended to configure caching services, including a Redis instance and Memcached, but the Redis port, configuration path, directory properties, credentials, package names, service names, and external recipe behavior require verification from the underlying recipe sources or deployment requirements.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis**: Intended Redis cache instance configured through the external `redisio` cookbook
  - Location/Path: Not verified from the supplied execution analysis
  - Port/Socket: Port `6379` is stated in the migration source but is not verified by the supplied structured analysis
  - Key Config: Intended password authentication and Redis configuration cleanup are stated in the migration source but require verification from `cookbooks/cache/recipes/default.rb` and the external `redisio` cookbook

- **Memcached**: External Memcached cache service
  - Location/Path: Not available
  - Port/Socket: Not specified
  - Key Config: The external `memcached` recipe is included, but its package, configuration, service, bind address, and port are unavailable

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No attribute files are shown in the supplied execution tree.

**Files:**
```text
```

No static files are shown or deployed by the supplied execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **Memcached inclusion** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The external recipe file is unavailable in the supplied execution tree.
   - The Memcached package name, configuration path, service name, listening port, bind address, and handlers cannot be determined from this cookbook alone.
   - Ansible should include the external Memcached role only after its implementation and deployment requirements are verified.
   - No `.each` loops are present in the supplied recipe analysis.

2. **Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates the resource `directory[/var/log/redis]`.
   - The resource is explicitly present in the supplied execution tree.
   - Owner, group, mode, recursive behavior, and creation timing are stated in the migration source but are not verified by the supplied structured analysis.
   - If confirmed from the recipe source, implement this with `ansible.builtin.file` and the verified directory properties.
   - Do not infer Redis user or group requirements until the external Redis role or platform package behavior is confirmed.

3. **Redis recipe inclusion** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The external recipe file is unavailable in the supplied execution tree.
   - The migration source identifies one intended Redis instance on port `6379`, but the instance definition, port, configuration path, package, service, and authentication settings are not verified by the supplied structured analysis.
   - Obtain the Redis instance definition and all service properties from the external `redisio` cookbook or deployment requirements before implementing the Ansible role.
   - No `.each` loops are present in the supplied recipe analysis.

4. **Redis configuration cleanup** (`cookbooks/cache/recipes/default.rb`):
   - Executes the resource `ruby_block[fix_redis_config]`.
   - The resource is explicitly present in the supplied execution tree.
   - The migration source states that the block processes `/etc/redis/6379.conf` and removes lines for `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
   - These configuration path and directive-removal details are not verified by the supplied structured analysis.
   - If confirmed from the recipe source, implement the cleanup with `ansible.builtin.lineinfile` tasks using `create: false`.
   - Run cleanup only after the external Redis role has generated the configuration.
   - Notify the verified Redis restart or reload handler only when the file changes.

5. **Redis enablement** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio::enable` recipe.
   - The external recipe file is unavailable in the supplied execution tree.
   - The intended behavior is Redis service enablement, but the service name, start behavior, and enablement mechanism are not available.
   - Obtain the exact service unit from the external Redis role or target operating system before implementing this step.

## Dependencies

**External cookbook dependencies**: `memcached` and `redisio`; both are included by the recipe but their version constraints are not verified by the supplied structured analysis.

**System package dependencies**: None are directly declared in the supplied execution tree. Package names and versions are delegated to the unavailable external `memcached` and `redisio` recipes and must not be inferred.

**Service dependencies**: Memcached service management is delegated to the unavailable `memcached` recipe. Redis service configuration and enablement are delegated to the unavailable `redisio` and `redisio::enable` recipes. No direct `service` resource is shown.

## Credentials

**Detection Summary**: 0 credentials verified by the supplied structured analysis; one Redis password claim in the migration source requires confirmation against the recipe source.

**Source**:
  - **Provider**: Not verified
  - **URL**: None verified
  - **Path**: `cookbooks/cache/recipes/default.rb` is identified by the migration source but the credential assignment is not verified

### Redis Authentication Password

- **Variable(s)**: The migration source identifies `node['redisio']['servers'][0]['requirepass']`; this requires verification
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`, pending source confirmation
- **Current storage**: Reported as a hardcoded Chef node attribute assignment, but not verified by the supplied structured analysis
- **Usage context**: Reported as Redis authentication for the intended Redis instance on port `6379`, but not verified

If the password is confirmed in the recipe source:

- Store it in Ansible Vault, AAP credentials, or another protected secret backend.
- Do not commit it in plaintext variables or rendered templates.
- Use a protected variable such as `redis_password`.
- Apply `no_log: true` to tasks that could expose the value.
- Use `REDISCLI_AUTH` for Redis validation commands.

No data bags, encrypted data bags, Chef Vault records, API tokens, certificates, private keys, or connection strings are verified by the supplied structured analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`, if confirmed as a managed directory
- `/etc/redis/6379.conf`, if confirmed as the Redis configuration path

**Service endpoints to check**:

- Intended Redis TCP port: `6379`, pending verification
- Memcached TCP port: not specified
- Unix sockets: none specified
- Network interfaces: none specified

**Templates rendered**:

- None shown or rendered in the supplied execution tree

**Resources to verify**:

- `directory[/var/log/redis]`
- `ruby_block[fix_redis_config]`

**Configuration changes to verify**:

If the Redis configuration cleanup is confirmed, verify that `/etc/redis/6379.conf` does not contain active lines beginning with:

```text
replica-serve-stale-data
replica-read-only
repl-ping-replica-period
client-output-buffer-limit
replica-priority
```

## Pre-flight checks:

```bash
# Confirm the cookbook recipe source and external dependency availability
test -f cookbooks/cache/recipes/default.rb

# Redis instance check: intended port and path require confirmation first
ss -ltnp | grep ':6379'
test -f /etc/redis/6379.conf

# Redis service check: replace the service name after verifying redisio::enable
systemctl list-units --type=service | grep -i redis
systemctl status <verified-redis-service>
systemctl is-enabled <verified-redis-service>

# Redis connectivity check after confirming the intended port and credentials
export REDISCLI_AUTH='REPLACE_WITH_PROTECTED_REDIS_PASSWORD'
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'

# Verify Redis configuration cleanup if /etc/redis/6379.conf is confirmed
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

! grep -Eq '^replica-serve-stale-data' /etc/redis/6379.conf
! grep -Eq '^replica-read-only' /etc/redis/6379.conf
! grep -Eq '^repl-ping-replica-period' /etc/redis/6379.conf
! grep -Eq '^client-output-buffer-limit' /etc/redis/6379.conf
! grep -Eq '^replica-priority' /etc/redis/6379.conf

# Verify the Redis log directory only after its ownership and mode are confirmed
stat -c '%A %U:%G %n' /var/log/redis
find /var/log/redis -maxdepth 1 -type f -ls

# Review Redis logs after identifying the verified service name
journalctl -u <verified-redis-service> --no-pager -n 50

# Memcached checks require the port and service name from the external cookbook
systemctl list-units --type=service | grep -i memcached
ss -ltnp | grep -i memcached
```