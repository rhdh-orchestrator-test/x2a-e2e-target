---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services by installing and configuring both memcached and Redis. It sets up a single Redis instance on port 6379 with authentication enabled and applies configuration fixes to remove deprecated replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached installation
  - Location/Path: Default system paths
  - Port/Socket: 11211
  - Key Config: Default memcached configuration via external cookbook

- **redis-6379**: Redis server instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration with port 6379 and password authentication
   - Creates directory `/var/log/redis` with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fixes via `ruby_block[fix_redis_config]` to remove deprecated replica settings from /etc/redis/6379.conf
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory[/var/log/redis] (1), ruby_block[fix_redis_config] (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (installed via external cookbooks)
**Service dependencies**: memcached.service, redis_6379.service

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
- **Usage context**: Redis authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration)
- /var/log/redis/ (Redis log directory)
- /etc/memcached.conf (memcached configuration, if created by external cookbook)

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: 
- No templates rendered by this cookbook (handled by external dependencies)

## Pre-flight checks:
```bash
# Service status for memcached instance
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
ss -tlnp | grep memcached
lsof -i :11211

# Service status for redis-6379 instance
systemctl status redis_6379
ps aux | grep redis
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Redis connectivity and authentication for redis-6379
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211  # then type "version" and "quit"

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing (removed by ruby_block)
cat /etc/redis/6379.conf | grep port

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid|Access.*0755'

# Logs
tail -f /var/log/redis/redis_6379.log
journalctl -u redis_6379 -f
journalctl -u memcached -f
tail -f /var/log/memcached.log

# Memory usage
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes

# Performance tests
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\ndelete test_key\r\nquit\r\n" | nc localhost 11211
```