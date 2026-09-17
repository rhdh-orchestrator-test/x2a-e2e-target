---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services (memcached and Redis) with Redis running on port 6379 with password authentication and custom configuration cleanup. It depends on external cookbooks for the actual service installation and management.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Managed by external memcached cookbook
  - Port/Socket: Default memcached port (typically 11211)
  - Key Config: Default configuration via external cookbook

- **redis-6379**: Redis server with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), custom replica settings removed

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached service installation and configuration
   - Configures Redis server attributes:
     - Sets port to 6379
     - Enables password authentication with 'redis_secure_password_123'
     - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block to clean up Redis configuration file:
     - Removes replica-serve-stale-data configuration lines
     - Removes replica-read-only configuration lines
     - Removes repl-ping-replica-period configuration lines
     - Removes client-output-buffer-limit configuration lines
     - Removes replica-priority configuration lines
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
- **Usage context**: Redis server authentication password for port 6379

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: 0 (no templates in this cookbook)

## Pre-flight checks:
```bash
# Service status for memcached
systemctl status memcached
ps aux | grep memcached

# Service status for redis-6379
systemctl status redis_6379
ps aux | grep redis-server

# Redis connectivity and authentication for redis-6379
redis-cli -p 6379 ping  # Should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # Should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211  # Then type: stats, quit

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # Should return nothing
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'  # Should show redis:redis ownership

# Redis configuration cleanup verification for redis-6379
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # Should return 0
grep -c "replica-read-only" /etc/redis/6379.conf  # Should return 0
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # Should return 0
grep -c "client-output-buffer-limit" /etc/redis/6379.conf  # Should return 0
grep -c "replica-priority" /etc/redis/6379.conf  # Should return 0

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

# Performance testing
redis-cli -p 6379 -a redis_secure_password_123 --latency -i 1  # Redis latency
echo -e "set test_key 0 0 5\r\nhello\r\nget test_key\r\nquit" | nc localhost 11211  # Memcached test
```