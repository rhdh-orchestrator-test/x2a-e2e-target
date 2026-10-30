---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a Redis instance on port `6379` and includes external `memcached` and `redisio` recipes. The supplied execution tree contains `cookbooks/cache/recipes/default.rb`, `directory[/var/log/redis]`, and `ruby_block[fix_redis_config]`; the dependency recipe implementations are unavailable. Redis configuration details, credentials, directory properties, Ruby block behavior, dependency versions, and exact Memcached settings require verification against the source and selected Ansible implementations before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache service configuration identified by the entry recipe
  - Location/Path: `/etc/redis/6379.conf` — target path requires source verification
  - Port/Socket: `6379` — reported by the migration analysis; requires attribute/source verification
  - Key Config: Authentication, replication-related settings, and exact generated configuration require source verification
  - Log directory: `/var/log/redis` — directory resource path is confirmed; owner, group, mode, and recursive behavior require verification

**Memcached**: The entry recipe includes the external `memcached` recipe, but no Memcached instance details are available in the supplied execution tree. The package, service name, port, bind address, memory limit, connection limit, configuration path, and authentication settings must be resolved from the selected Ansible implementation or dependency source.

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

The cookbook metadata file was inspected in the original analysis but is not included in the supplied file-structure listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Entry recipe identified as `cache::default`.
   - Includes the external `memcached` recipe. The dependency recipe is not present in the supplied execution tree, so its package, service, configuration path, port, and runtime settings require verification.
   - Configures one reported Redis server item for port `6379`. The reported `requirepass` and `replicaservestaledata` values require confirmation from recipe attribute analysis before migration.
   - Creates `directory[/var/log/redis]`. The path is confirmed; owner, group, mode, and recursive-creation properties require verification.
   - Includes the external `redisio` recipe. The dependency recipe is not present in the supplied execution tree, so Redis package installation, configuration generation, user/group handling, and service management require implementation and verification in Ansible.
   - Runs `ruby_block[fix_redis_config]`. The resource is confirmed, but its target file and exact configuration transformations require source verification.
   - Includes `redisio::enable`. The dependency recipe is not present in the supplied execution tree. The intended Ansible behavior is to enable and start the Redis service associated with the configured Redis instance after its service name has been verified.

   **Reported Redis configuration item:**
   - **Redis instance on port 6379**:
     - `port`: `6379`
     - `requirepass`: reported as `redis_secure_password_123`; source and credential classification require verification
     - `replicaservestaledata`: reported as `nil`; source requires verification

   **Reported directory resource:**
   - `directory[/var/log/redis]`
   - Resource count: 1
   - Confirmed property: path `/var/log/redis`
   - Owner, group, mode, and recursive behavior: require verification

   **Reported Ruby resource:**
   - `ruby_block[fix_redis_config]`
   - Target path and directive-removal behavior: require verification

## Dependencies

**External cookbook dependencies**:

- `memcached`, reported with version constraint `~> 6.0`; metadata requires verification
- `redisio`, reported without a version constraint; metadata requires verification

**System package dependencies**: No package names or versions are verified in the supplied execution tree. Resolve package names for the target distribution and selected Ansible implementation before migration.

**Service dependencies**:

- Redis service associated with `/etc/redis/6379.conf`; exact service name requires verification
- Memcached service; exact service name requires verification

**Reported supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

Platform metadata requires verification against the cookbook metadata.

## Credentials

**Detection Summary**: One Redis credential is reported by the original analysis, but the supplied structured validation does not confirm credential findings. Source verification is required.

**Source**:
  - **Provider**: Reported as hardcoded in the Chef recipe; requires verification
  - **URL**: None verified
  - **Path**: `cookbooks/cache/recipes/default.rb` — requires source verification

### Redis authentication password

- **Variable**: Reported as `node['redisio']['servers'][0]['requirepass']`; requires verification
- **Literal value in source**: Reported as `redis_secure_password_123`; do not reproduce or migrate until confirmed
- **Source file(s)**: `cookbooks/cache/recipes/default.rb` — requires verification
- **Current storage**: Reported as a hardcoded Chef attribute value; requires verification
- **Usage context**: Reported as Redis authentication for the instance on port `6379`; requires verification
- **Migration handling**: If confirmed, store the value in Ansible Vault or an approved external secret backend. Do not place it in plaintext role defaults, regular variable files, templates, documentation, or task output.

No additional credential sources are confirmed by the supplied structured analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf` — target path requires source and dependency verification

**Service endpoints to check**:

- Redis TCP port `6379` — reported endpoint requires configuration verification
- Memcached endpoint — port and socket are not available and must be resolved from the selected implementation

**Templates rendered**: None shown or referenced in the supplied execution tree. No template render counts are available.

**Configuration transformations to verify**:

- Confirm whether `/etc/redis/6379.conf` is generated.
- Confirm whether the Ruby block modifies `/etc/redis/6379.conf`.
- Confirm the exact directives or patterns removed by `ruby_block[fix_redis_config]`.
- Confirm the Redis authentication setting and port.
- Confirm the final Redis service name and reload/restart behavior.

## Pre-flight checks:

```bash
# Verify the migrated recipe and expected configuration path
test -f cookbooks/cache/recipes/default.rb
test -f /etc/redis/6379.conf

# Redis instance on port 6379
# Use the verified service name if it differs from redis.
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Verify the reported Redis endpoint
ss -ltnp | grep ':6379'
nc -zv 127.0.0.1 6379

# Validate Redis configuration after confirming the generated configuration format
redis-cli -h 127.0.0.1 -p 6379 PING

# If authentication is confirmed, retrieve the password from secure storage
# without exposing it in shell history or logs.
redis-cli -h 127.0.0.1 -p 6379 -a '<redis-password-from-secure-storage>' PING

# Verify the reported Redis log directory path.
# Confirm owner, group, mode, and recursive behavior from source analysis first.
stat -c '%A %U %G %n' /var/log/redis

# Inspect the service logs after confirming the exact service name.
journalctl -u redis --since "10 minutes ago"

# Memcached
# Do not run endpoint checks until the selected implementation confirms:
# - package name
# - service name
# - TCP port or Unix socket
# - configuration path
```
