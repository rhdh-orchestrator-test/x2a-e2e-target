---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes configuration cleanup via ruby_block manipulation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Single instance cache server
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (redis_secure_password_123), configuration cleanup for replica settings

- **Memcached Server**: Single instance cache server (configured via external cookbook)
  - Location/Path: Managed by memcached cookbook dependency
  - Port/Socket: Default memcached port (11211)
  - Key Config: Default memcached configuration

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Configures Redis server attributes with port 6379 and password authentication
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block[fix_redis_config] to clean up Redis configuration file by removing replica-related settings
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: redis-server, memcached (installed via dependency cookbooks)
**Service dependencies**: redis-server, memcached systemd services

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
- /var/log/memcached.log (Memcached log file)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (Memcached)

**Templates rendered**:
- No templates rendered directly by this cookbook (handled by dependency cookbooks)

## Pre-flight checks:
```bash
# Service status
systemctl status redis-server
systemctl status memcached
ps aux | grep redis-server
ps aux | grep memcached

# Redis connectivity and authentication
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211  # then type: stats, quit

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return empty (cleaned by ruby_block)
ls -lah /var/log/redis/
ls -lah /var/log/redis/ | grep redis  # check ownership

# Redis configuration test
redis-server /etc/redis/6379.conf --test-config

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Test basic operations
# Redis
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key  # should return "test_value"
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Memcached
echo -e "set test_key 0 60 10\r\ntest_value\r\nquit" | nc localhost 11211
echo -e "get test_key\r\nquit" | nc localhost 11211  # should return test_value
echo -e "delete test_key\r\nquit" | nc localhost 11211
```