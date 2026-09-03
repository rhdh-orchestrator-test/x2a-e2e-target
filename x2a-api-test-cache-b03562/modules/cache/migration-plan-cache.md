---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It creates a Redis log directory and applies configuration fixes to remove problematic replica settings, relying on external cookbooks for service installation and configuration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Default system installation
  - Port/Socket: 11211
  - Key Config: Uses external memcached cookbook defaults

- **redis**: Redis server with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: 
    - Password authentication via redisio cookbook
    - Log directory: /var/log/redis
    - Replica settings removed via configuration cleanup

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Includes redisio cookbook for Redis installation and configuration
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Applies configuration fix via ruby_block to clean up Redis config file:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (via external cookbooks)
**Service dependencies**: memcached.service, redis.service

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: External cookbook (redisio)
  - **URL**: N/A
  - **Path**: N/A

### Redis Authentication Password
- **Variable(s)**: Configured via redisio cookbook attributes
- **Source file(s)**: cookbooks/cache/recipes/default.rb (via external cookbook inclusion)
- **Current storage**: External cookbook configuration
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf (Redis configuration)
- /var/log/redis/ (Redis log directory)
- /etc/memcached.conf (memcached configuration, via external cookbook)

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**:
- Redis configuration templates rendered by redisio cookbook
- Memcached configuration templates rendered by memcached cookbook

## Pre-flight checks:
```bash
# Service status for memcached
systemctl status memcached
ps aux | grep memcached | grep -v grep

# Service status for redis
systemctl status redis
ps aux | grep redis-server | grep -v grep

# memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211

# redis connectivity
redis-cli -p 6379 ping
redis-cli -p 6379 info server

# Configuration validation for redis
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/

# Configuration validation for memcached
cat /etc/memcached.conf

# Network listening verification
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
lsof -i :6379
lsof -i :11211

# Functionality tests
redis-cli -p 6379 set test_key "test_value"
redis-cli -p 6379 get test_key
echo -e "set test_key 0 60 10\r\ntest_value\r\nquit\r" | nc localhost 11211
echo -e "get test_key\r\nquit\r" | nc localhost 11211
```