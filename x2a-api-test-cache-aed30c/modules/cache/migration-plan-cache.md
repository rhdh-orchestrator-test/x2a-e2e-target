---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It installs both services via external cookbook dependencies, creates a Redis log directory, and applies configuration fixes to remove deprecated Redis replica settings. The Redis instance runs on port 6379 with password authentication enabled.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Managed by external memcached cookbook
  - Port/Socket: Default memcached port (typically 11211)
  - Key Config: Default configuration via memcached cookbook

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
   - Sets Redis server configuration inline:
     - Port: 6379
     - Password: 'redis_secure_password_123' (requirepass)
     - Removes replicaservestaledata setting (set to nil)
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to clean up deprecated Redis settings:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines  
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

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

### Database/Cache Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/
- /var/log/redis/redis_6379.log

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: No templates rendered by this cookbook (handled by external dependencies)

## Pre-flight checks:
```bash
# Service status - memcached
systemctl status memcached
ps aux | grep memcached

# Service status - redis-6379
systemctl status redis_6379
ps aux | grep redis

# Redis connectivity and authentication - redis-6379
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity - memcached
echo "stats" | nc localhost 11211
telnet localhost 11211  # then type: stats

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid|Access.*0755'

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Memory usage
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes

# Performance tests
redis-cli -p 6379 -a redis_secure_password_123 --latency -i 1  # Redis latency
echo -e "set test 0 0 5\r\nhello\r\nget test\r\nquit" | nc localhost 11211  # Memcached test

# Logs
tail -f /var/log/redis/redis_6379.log
tail -f /var/log/memcached.log
journalctl -u redis_6379 -f
journalctl -u memcached -f
```