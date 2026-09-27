---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both Memcached and Redis with authentication. Redis is configured on port 6379 with password authentication and custom configuration cleanup. The cookbook depends on external memcached and redisio cookbooks for the actual service installation and configuration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Single Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), custom replica settings removed

- **Memcached Server**: Single Memcached instance (configured via external cookbook)
  - Location/Path: Managed by memcached cookbook dependency
  - Port/Socket: Default memcached port (typically 11211)
  - Key Config: Default memcached configuration

## File Structure

**Recipes:**
```
cookbooks/cache/recipes/default.rb
```

**Providers:**
```
(None - uses external cookbook dependencies)
```

**Templates:**
```
(None - templates managed by dependency cookbooks)
```

**Attributes:**
```
(None - attributes defined inline in recipe)
```

**Files:**
```
(None)
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for Memcached installation and configuration
   - Sets Redis server configuration with authentication:
     - Port: 6379
     - Password: redis_secure_password_123 (hardcoded)
     - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Performs configuration cleanup via ruby_block to remove specific Redis replica settings:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: Redis server, Memcached (installed via dependency cookbooks)
**Service dependencies**: redis, memcached systemd services

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
- **Usage context**: Redis server authentication password for client connections

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)
- /var/log/memcached.log (Memcached log file, if configured)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (Memcached default)
- Unix sockets: None specified
- Network interfaces: Default binding (all interfaces)

**Templates rendered**:
- Redis configuration templates managed by redisio cookbook
- Memcached configuration templates managed by memcached cookbook

## Pre-flight checks:
```bash
# Service status - Redis Server
systemctl status redis-server
ps aux | grep redis
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass
netstat -tulpn | grep 6379
lsof -i :6379

# Service status - Memcached Server
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
netstat -tulpn | grep 11211
lsof -i :11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis/ | grep -E 'Access.*Uid.*redis.*Gid.*redis'

# Logs
tail -f /var/log/redis/redis-server.log
tail -f /var/log/memcached.log
journalctl -u redis-server -f
journalctl -u memcached -f

# Performance tests
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\ndelete test_key\r\nquit\r\n" | nc localhost 11211
```