---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It installs both services via external cookbook dependencies, creates a Redis log directory, and applies configuration fixes to Redis by removing specific replica-related settings from the config file.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Default memcached instance
  - Location/Path: Managed by external memcached cookbook
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration

- **redis**: Single Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed via post-config fix

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration inline with port 6379 and password authentication
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to remove replica-related settings from /etc/redis/6379.conf:
     - Removes: replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority
   - Includes redisio::enable recipe to enable and start Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (installed via external cookbooks)
**Service dependencies**: memcached, redis-server systemd services

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Database/Cache Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: No templates in this cookbook (handled by external dependencies)

## Pre-flight checks:
```bash
# Service status for memcached instance
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
echo "stats" | nc localhost 11211

# Service status for redis instance
systemctl status redis-server
ps aux | grep redis
netstat -tulpn | grep 6379
redis-cli -p 6379 -a redis_secure_password_123 ping

# Redis connectivity and authentication
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing after fix
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'  # should show redis:redis ownership

# Redis configuration fix verification
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # should be 0
grep -c "replica-read-only" /etc/redis/6379.conf  # should be 0
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # should be 0
grep -c "client-output-buffer-limit" /etc/redis/6379.conf  # should be 0
grep -c "replica-priority" /etc/redis/6379.conf  # should be 0

# Test basic operations
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key  # should return "test_value"
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Memcached test
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\nquit\r\n" | nc localhost 11211
```