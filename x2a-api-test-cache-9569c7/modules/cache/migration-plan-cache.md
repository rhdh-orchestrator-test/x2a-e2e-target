---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It installs both services, configures Redis on port 6379 with password authentication, creates necessary directories, and applies configuration fixes to remove deprecated Redis replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached instance
  - Location/Path: Default system installation
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration via external cookbook

- **redis**: Redis server with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings cleaned up

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
     - Password: 'redis_secure_password_123' 
     - Removes replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to clean up deprecated Redis replica settings:
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

### Redis Authentication Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: Hardcoded
- **Usage context**: Redis server authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/
- /etc/memcached.conf

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
ps aux | grep redis-server
netstat -tulpn | grep 6379
redis-cli -p 6379 -a redis_secure_password_123 ping

# Configuration validation for redis instance
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep port
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'

# Directory permissions for redis instance
ls -lah /var/log/redis/
stat /var/log/redis/ | grep -E 'Access.*0755|Uid.*redis|Gid.*redis'

# Connectivity tests for redis instance
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Connectivity tests for memcached instance
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\nquit\r\n" | nc localhost 11211
```