---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes configuration cleanup via ruby_block manipulation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Default system installation
  - Port/Socket: 11211
  - Key Config: Managed by memcached cookbook dependency

- **redis-6379**: Redis server with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica configuration stripped

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Includes memcached cookbook for memcached installation and configuration
   - Step 2: Sets Redis server configuration with inline attributes (port 6379, password 'redis_secure_password_123', removes replicaservestaledata setting)
   - Step 3: Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Step 4: Includes redisio cookbook for Redis installation and configuration
   - Step 5: Executes ruby_block to clean up Redis configuration file (removes replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, and replica-priority lines)
   - Step 6: Includes redisio::enable recipe to start Redis service
   - Resources used: directory (1), ruby_block (1)
   - Files/templates deployed: None (handled by dependency cookbooks)
   - Iterations: No loops to expand

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (via dependency cookbooks)
**Service dependencies**: memcached.service, redis_6379.service

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Redis Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: Hardcoded string value
- **Usage context**: Redis authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**: 
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/

**Service endpoints to check**: 
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: None (configuration handled by dependency cookbooks)

## Pre-flight checks:
```bash
# Service status for memcached
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
memcached-tool localhost:11211 stats
netstat -tulpn | grep 11211
lsof -i :11211

# Service status for redis-6379
systemctl status redis_6379
ps aux | grep redis
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass
netstat -tulpn | grep 6379
lsof -i :6379

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
stat /var/log/redis | grep "Uid.*redis.*Gid.*redis"

# Connectivity tests
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 --latency -i 1
echo "stats" | nc localhost 11211 | grep bytes
```