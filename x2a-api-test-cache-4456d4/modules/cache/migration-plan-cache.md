---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a dual caching layer with memcached and Redis services. It installs memcached via external cookbook dependency, configures a single Redis instance on port 6379 with authentication, and applies configuration fixes to remove deprecated Redis replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Managed by external memcached cookbook
  - Port/Socket: Default memcached port (typically 11211)
  - Key Config: Standard memcached configuration

- **redis-6379**: Redis server instance with authentication
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
   - Sets Redis server configuration with port 6379 and password authentication
     - Password: 'redis_secure_password_123' (hardcoded)
     - Removes replicaservestaledata setting (set to nil)
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fixes via ruby_block to remove deprecated Redis replica settings:
     - Removes: replica-serve-stale-data, replica-read-only, repl-ping-replica-period
     - Removes: client-output-buffer-limit, replica-priority
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

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
- **Current storage**: hardcoded
- **Usage context**: Redis server authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/
- /var/log/redis/redis_6379.log

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: No templates in this cookbook (handled by external dependencies)

## Pre-flight checks:
```bash
# Service status
systemctl status memcached
systemctl status redis-server
systemctl status redis_6379

# Process checks
ps aux | grep memcached
ps aux | grep redis-server

# Redis connectivity and authentication - redis-6379 instance
redis-cli -p 6379 ping
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity - memcached instance
echo "stats" | nc localhost 11211
telnet localhost 11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Access.*Uid.*redis.*Gid.*redis'

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Test basic operations - redis-6379 instance
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Test basic operations - memcached instance
echo -e "set test_key 0 60 10\r\ntest_value\r\nquit" | nc localhost 11211
echo -e "get test_key\r\nquit" | nc localhost 11211
echo -e "delete test_key\r\nquit" | nc localhost 11211
```