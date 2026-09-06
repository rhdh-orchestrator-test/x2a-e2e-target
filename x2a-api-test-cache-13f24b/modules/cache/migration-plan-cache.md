---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It installs both services, configures Redis on port 6379 with password authentication, creates necessary directories, and applies configuration fixes to remove deprecated Redis replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Default system installation
  - Port/Socket: 11211
  - Key Config: Uses external memcached cookbook defaults

- **redis-6379**: Redis server with authentication
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
   - Sets Redis server configuration attributes:
     - `node.default['redisio']['servers'][0]['port'] = '6379'`
     - `node.default['redisio']['servers'][0]['requirepass'] = 'redis_secure_password_123'`
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to remove deprecated Redis replica settings:
     - Removes: replica-serve-stale-data, replica-read-only, repl-ping-replica-period
     - Removes: client-output-buffer-limit, replica-priority
     - Modifies: /etc/redis/6379.conf
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), attribute assignments (2), directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server
**Service dependencies**: memcached, redis-server (port 6379)

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
- **Usage context**: Redis authentication password for port 6379 server

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/
- /etc/memcached.conf

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: 0 (configuration handled by external cookbooks)

## Pre-flight checks:
```bash
# Service status for memcached
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
lsof -i :11211

# Service status for redis-6379
systemctl status redis-server
ps aux | grep redis-server
netstat -tulpn | grep 6379
lsof -i :6379

# Redis connectivity and authentication for redis-6379
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
ls -lah /etc/redis/

# Performance tests
redis-cli -p 6379 -a redis_secure_password_123 --latency -i 1
echo -e "set test 0 0 5\r\nhello\r\nget test\r\nquit" | nc localhost 11211
```