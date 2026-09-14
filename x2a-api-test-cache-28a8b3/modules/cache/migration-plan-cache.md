---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services by installing and configuring both memcached and Redis. It sets up a single Redis instance on port 6379 with authentication enabled and performs configuration cleanup to remove replica-related settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server (port 6379)**: Primary Redis cache instance
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Authentication enabled with password, replica settings removed

- **Memcached**: Default memcached instance
  - Location/Path: Default system configuration
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration via dependency cookbook

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration attributes:
     - Port: 6379
     - Password: redis_secure_password_123
     - Removes replica-serve-stale-data setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block to clean up Redis configuration file:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

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

### Redis Authentication Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis server authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf (Redis configuration)
- /var/log/redis/ (Redis log directory)
- /etc/memcached.conf (Memcached configuration via dependency)

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (Memcached)

**Templates rendered**: No templates rendered directly by this cookbook (handled by dependencies)

## Pre-flight checks:
```bash
# Service status for Redis Server (port 6379)
systemctl status redis-server
ps aux | grep redis-server
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
netstat -tulpn | grep 6379
lsof -i :6379

# Service status for Memcached
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
netstat -tulpn | grep 11211
lsof -i :11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
stat -c "%U:%G %a" /var/log/redis

# Test Redis functionality
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Test Memcached functionality
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\nquit\r" | nc localhost 11211
```