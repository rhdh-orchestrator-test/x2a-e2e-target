---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes configuration cleanup via ruby_block manipulation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Primary caching service with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed via config cleanup

- **Memcached**: Secondary caching service (configured via external cookbook)
  - Location/Path: Managed by memcached cookbook dependency
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Configures Redis server attributes inline:
     - Sets port to 6379
     - Enables password authentication with 'redis_secure_password_123'
     - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block 'fix_redis_config' to clean up Redis configuration:
     - Removes replica-serve-stale-data configuration lines
     - Removes replica-read-only configuration lines  
     - Removes repl-ping-replica-period configuration lines
     - Removes client-output-buffer-limit configuration lines
     - Removes replica-priority configuration lines
   - Includes redisio::enable recipe to start and enable Redis service

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

### Database/Cache Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis server authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)
- /var/log/memcached.log (Memcached logs)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (Memcached)

**Templates rendered**: No templates rendered directly by this cookbook (handled by dependency cookbooks)

## Pre-flight checks:
```bash
# Service status
systemctl status redis-server
systemctl status memcached
ps aux | grep redis-server
ps aux | grep memcached

# Redis connectivity and authentication
redis-cli -p 6379 ping  # Should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # Should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
memcstat --servers=localhost:11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # Should return nothing (cleaned by ruby_block)

# Directory permissions
ls -lah /var/log/redis/
stat -c "%U:%G %a" /var/log/redis  # Should show redis:redis 755

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Test basic operations
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key  # Should return "test_value"
redis-cli -p 6379 -a redis_secure_password_123 del test_key

echo -e "set test_key 0 0 10\r\ntest_value\r\nget test_key\r\ndelete test_key\r\nquit\r\n" | nc localhost 11211
```