---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - Memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes a configuration fix to remove specific replica-related settings. The cookbook depends on external memcached and redisio cookbooks for the actual service installation and configuration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Single instance cache server
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed via post-config fix

- **Memcached Server**: Single instance cache server (configured via external cookbook)
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
   - Step 1: Includes memcached cookbook for memcached installation and configuration
   - Step 2: Sets Redis server configuration attributes (port 6379, password 'redis_secure_password_123', removes replicaservestaledata setting)
   - Step 3: Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Step 4: Includes redisio cookbook for Redis installation and configuration
   - Step 5: Executes ruby_block to fix Redis configuration by removing replica-related settings (replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority)
   - Step 6: Includes redisio::enable recipe to start and enable Redis service
   - Iterations: No .each loops present

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: Redis server, Memcached (installed via dependency cookbooks)
**Service dependencies**: redis-server, memcached systemd services

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
- **Usage context**: Redis server authentication password for client connections

## Checks for the Migration

**Files to verify**: 
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/

**Service endpoints to check**: 
- Port 6379 (Redis)
- Port 11211 (Memcached)

**Templates rendered**: 
- Redis configuration templates rendered by redisio cookbook
- Memcached configuration templates rendered by memcached cookbook

## Pre-flight checks:
```bash
# Service status for Redis Server
systemctl status redis-server
ps aux | grep redis-server
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
netstat -tulpn | grep 6379
lsof -i :6379

# Service status for Memcached Server  
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
netstat -tulpn | grep 11211
lsof -i :11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'

# Redis functionality test
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Memcached functionality test
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\nquit\r\n" | nc localhost 11211
```