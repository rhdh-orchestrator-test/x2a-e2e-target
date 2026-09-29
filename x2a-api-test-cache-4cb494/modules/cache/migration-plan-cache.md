---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It installs both services via external cookbook dependencies, creates a Redis log directory, configures a single Redis instance on port 6379 with password authentication, and applies configuration fixes to remove deprecated Redis replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Default system installation (via memcached cookbook dependency)
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration via external cookbook

- **redis-6379**: Redis server with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings cleaned up
  - Log Directory: /var/log/redis (owner: redis, group: redis, mode: 0755)

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Configures Redis server attributes:
     - Sets port to 6379
     - Enables password authentication with 'redis_secure_password_123'
     - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fixes via ruby_block to remove deprecated Redis replica settings:
     - Removes replica-serve-stale-data configuration
     - Removes replica-read-only configuration  
     - Removes repl-ping-replica-period configuration
     - Removes client-output-buffer-limit configuration
     - Removes replica-priority configuration
   - Includes redisio::enable recipe to start and enable Redis service
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
- **Usage context**: Redis server authentication password for port 6379

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)
- /var/log/redis/redis_6379.log (Redis log file)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (memcached)
- Unix sockets: None
- Network interfaces: Default (all interfaces)

**Templates rendered**: 0 (configuration handled by external cookbooks)

## Pre-flight checks:
```bash
# Service status for memcached
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
netstat -tulpn | grep 11211
lsof -i :11211

# Service status for redis-6379
systemctl status redis-server
systemctl status redis_6379
ps aux | grep redis-server
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
netstat -tulpn | grep 6379
lsof -i :6379

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep port
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'

# Directory and permissions for redis-6379
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid|Access.*0755'
tail -f /var/log/redis/redis_6379.log

# Connectivity tests for memcached
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\ndelete test_key\r\nquit\r\n" | nc localhost 11211
echo "stats" | nc localhost 11211 | grep bytes

# Connectivity tests for redis-6379
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key
redis-cli -p 6379 -a redis_secure_password_123 info memory
```