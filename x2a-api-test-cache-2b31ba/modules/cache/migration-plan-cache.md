---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes a configuration fix to remove specific replica-related settings from the Redis config file.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis_6379**: Single instance Redis cache server
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed via post-config fix

- **memcached**: Default memcached service
  - Location/Path: Default system configuration
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration via external cookbook

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration attributes:
     - Port: 6379
     - Password: redis_secure_password_123 (requirepass)
     - Disables replicaservestaledata
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block to fix Redis configuration by removing replica-related settings:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (via external cookbooks)
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
- /var/log/redis/redis_6379.log
- /etc/memcached.conf

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (Memcached)

**Templates rendered**: 0 (configuration handled by external cookbooks and ruby_block)

## Pre-flight checks:
```bash
# Service status for redis_6379
systemctl status redis-server
ps aux | grep redis-server
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass
netstat -tulpn | grep 6379
lsof -i :6379

# Service status for memcached
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
memcstat --servers=localhost:11211
netstat -tulpn | grep 11211
lsof -i :11211

# Configuration validation for redis_6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'

# Redis configuration fix verification for redis_6379
grep -c "replica-serve-stale-data" /etc/redis/6379.conf
grep -c "replica-read-only" /etc/redis/6379.conf
grep -c "repl-ping-replica-period" /etc/redis/6379.conf
grep -c "client-output-buffer-limit" /etc/redis/6379.conf
grep -c "replica-priority" /etc/redis/6379.conf

# Test data operations for redis_6379
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Test data operations for memcached
echo -e "set test_key 0 0 10\r\ntest_value\r\nget test_key\r\ndelete test_key\r\nquit\r\n" | nc localhost 11211
```