---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. Redis is configured on port 6379 with password authentication and includes a configuration cleanup hack to remove replica-related settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached instance
  - Location/Path: Default system configuration
  - Port/Socket: 11211
  - Key Config: Managed by memcached cookbook dependency

- **redis**: Single Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed via configuration cleanup

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration with port 6379 and password authentication
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes configuration cleanup hack to remove replica-related settings from Redis config
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: directory (1), ruby_block (1)
   - Note: Analysis limited to main recipe file - external cookbook dependencies (memcached, redisio) require separate analysis

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (via dependency cookbooks)
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
- /etc/redis/6379.conf
- /var/log/redis/
- /var/log/memcached.log

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (Memcached)

**Templates rendered**: No templates in this cookbook (handled by dependency cookbooks)

## Pre-flight checks:
```bash
# Service status - memcached
systemctl status memcached
ps aux | grep memcached

# Service status - redis
systemctl status redis-server
ps aux | grep redis-server

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211

# Redis connectivity with authentication
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing after cleanup

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

# Memory usage
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes

# Performance checks
redis-cli -p 6379 -a redis_secure_password_123 --latency -i 1
redis-cli -p 6379 -a redis_secure_password_123 info stats
```