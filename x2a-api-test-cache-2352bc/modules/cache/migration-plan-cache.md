---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both Memcached and Redis with authentication. Redis is configured on port 6379 with password authentication and includes custom configuration cleanup. The cookbook depends on external memcached and redisio cookbooks for the actual service installation and configuration.

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

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook recipe for Memcached installation and configuration
   - Sets Redis server configuration attributes:
     - Port: 6379
     - Password: 'redis_secure_password_123' (hardcoded)
     - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook recipe for Redis installation and configuration
   - Executes custom configuration cleanup via ruby_block to remove replica configuration lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

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
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (Memcached)

**Templates rendered**: None (templates managed by dependency cookbooks)

## Pre-flight checks:
```bash
# Service status for Redis Server
systemctl status redis-server
ps aux | grep redis-server
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Service status for Memcached Server
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
ss -tlnp | grep memcached
lsof -i :11211

# Redis connectivity and authentication
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a 'redis_secure_password_123' ping  # should return PONG
redis-cli -p 6379 -a 'redis_secure_password_123' info server
redis-cli -p 6379 -a 'redis_secure_password_123' config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
memcstat --servers=localhost:11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
ls -lah /var/log/redis/
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing

# Redis configuration cleanup verification
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # should return 0
grep -c "replica-read-only" /etc/redis/6379.conf  # should return 0
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # should return 0
grep -c "client-output-buffer-limit" /etc/redis/6379.conf  # should return 0
grep -c "replica-priority" /etc/redis/6379.conf  # should return 0

# Data persistence testing
redis-cli -p 6379 -a 'redis_secure_password_123' set test_key "test_value"
redis-cli -p 6379 -a 'redis_secure_password_123' get test_key  # should return "test_value"
redis-cli -p 6379 -a 'redis_secure_password_123' del test_key

# Cache functionality testing
echo -e "set test_key 0 60 10\r\ntest_value\r\nquit\r" | nc localhost 11211
echo -e "get test_key\r\nquit\r" | nc localhost 11211  # should return test_value
```