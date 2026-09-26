---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both Memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes configuration cleanup via ruby_block manipulation. The cookbook depends on external memcached and redisio cookbooks for the actual service installation and configuration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Primary Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf (managed by redisio cookbook)
  - Port/Socket: 6379 (typical default)
  - Key Config: Password authentication enabled, replica settings cleanup

- **Memcached**: Standard memcached service
  - Location/Path: Managed by memcached cookbook
  - Port/Socket: 11211 (typical default)
  - Key Config: Default memcached configuration

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached service setup
   - Configures Redis server attributes (port 6379, password authentication)
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block to clean up Redis configuration file (removes replica-related settings)
   - Includes redisio::enable recipe to start Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: redis-server, memcached (installed via external cookbooks)
**Service dependencies**: redis, memcached systemd services

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Database/Cache Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded as "redis_secure_password_123"
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- /var/log/redis/ (Redis log directory - confirmed created)
- /etc/redis/6379.conf (Redis configuration - managed by external cookbook)

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (Memcached)

**Templates rendered**:
- Redis configuration templates rendered by redisio cookbook (count unknown - external cookbook)
- Memcached configuration templates rendered by memcached cookbook (count unknown - external cookbook)

## Pre-flight checks:
```bash
# Service status for Redis Server
systemctl status redis-server
ps aux | grep redis-server
netstat -tulpn | grep 6379
lsof -i :6379

# Service status for Memcached
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
lsof -i :11211

# Redis log directory verification (confirmed created by cookbook)
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'  # should show redis:redis ownership

# Redis connectivity and authentication
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211

# Configuration cleanup verification (ruby_block execution)
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # should return 0 after cleanup
grep -c "replica-read-only" /etc/redis/6379.conf  # should return 0 after cleanup
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # should return 0 after cleanup
grep -c "client-output-buffer-limit" /etc/redis/6379.conf  # should return 0 after cleanup
grep -c "replica-priority" /etc/redis/6379.conf  # should return 0 after cleanup

# Basic functionality tests
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key

echo -e "set test_key 0 60 10\r\ntest_value\r\nquit\r" | nc localhost 11211
echo -e "get test_key\r\nquit\r" | nc localhost 11211
```