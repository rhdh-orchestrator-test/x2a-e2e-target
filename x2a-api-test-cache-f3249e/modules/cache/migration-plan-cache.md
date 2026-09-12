---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes a configuration fix to remove specific replica-related settings from the Redis config file.

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
  - Key Config: Password authentication enabled (requirepass), replica settings removed via post-config fix

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Includes memcached cookbook for memcached installation and configuration
   - Step 2: Configures Redis server attributes (port 6379, password authentication with 'redis_secure_password_123', disables replicaservestaledata)
   - Step 3: Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Step 4: Includes redisio cookbook for Redis installation and configuration
   - Step 5: Applies configuration fix via ruby_block to remove replica-related settings from /etc/redis/6379.conf
   - Step 6: Includes redisio::enable recipe to start and enable Redis service
   - Iterations: Single Redis server configuration for port 6379

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (via external cookbooks)
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
- **Current storage**: Hardcoded string value
- **Usage context**: Redis server authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**: 
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/

**Service endpoints to check**: 
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: 
- Redis configuration templates (rendered by redisio cookbook)
- Memcached configuration templates (rendered by memcached cookbook)

## Pre-flight checks:
```bash
# Service status for memcached instance
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
echo "stats" | nc localhost 11211

# Service status for redis-6379 instance
systemctl status redis-server
ps aux | grep redis-server
netstat -tulpn | grep 6379
redis-cli -p 6379 -a redis_secure_password_123 ping

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'

# Directory permissions for redis-6379
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Access.*Uid.*redis.*Gid.*redis'

# Authentication test for redis-6379
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 info server

# Connectivity test for memcached
telnet localhost 11211
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\nquit\r" | nc localhost 11211
```