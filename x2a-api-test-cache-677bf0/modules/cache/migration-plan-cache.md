---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services including memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes configuration cleanup via ruby_block. The cookbook depends on external memcached and redisio cookbooks for the actual service installation and configuration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server (port 6379)**: Primary Redis cache instance
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica configuration cleaned up

- **Memcached**: Default memcached instance (configured via external cookbook)
  - Location/Path: Managed by memcached cookbook
  - Port/Socket: Default memcached port (11211)
  - Key Config: Default memcached configuration

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Includes memcached cookbook for memcached installation and configuration
   - Step 2: Sets Redis server configuration with port 6379 and password authentication
   - Step 3: Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Step 4: Includes redisio cookbook for Redis installation and configuration
   - Step 5: Executes ruby_block to clean up Redis configuration file by removing replica-related directives
   - Step 6: Includes redisio::enable recipe to start and enable Redis service
   - Resources used: include_recipe (3), directory (1), ruby_block (1)
   - Iterations: No .each loops present

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: redis-server, memcached (installed via dependency cookbooks)
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
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf (Redis configuration)
- /var/log/redis/ (Redis log directory)

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (Memcached)

**Templates rendered**: 
- Redis configuration templates rendered by redisio cookbook
- Memcached configuration templates rendered by memcached cookbook

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis_6379
systemctl status memcached
ps aux | grep redis-server
ps aux | grep memcached

# Redis Server (port 6379) checks
redis-cli -p 6379 ping
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass
netstat -tulpn | grep 6379
lsof -i :6379

# Memcached checks
echo "stats" | nc localhost 11211
netstat -tulpn | grep 11211
lsof -i :11211

# Configuration validation commands
cat /etc/redis/6379.conf | grep requirepass
ls -lah /var/log/redis/
ls -lah /etc/redis/

# Network/connectivity checks
ss -tlnp | grep redis
ss -tlnp | grep memcached
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\nquit\r" | nc localhost 11211
```