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
  - Key Config: Password authentication enabled (requirepass), replica settings removed via post-configuration fix

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration with port 6379 and password authentication
   - Password: 'redis_secure_password_123' (hardcoded)
   - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to remove replica-related settings from /etc/redis/6379.conf:
     - Removes: replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority
   - Includes redisio::enable recipe to start and enable Redis service
   - Iterations: No loops to expand

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

### Redis Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: Hardcoded
- **Usage context**: Redis authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf
- /var/log/redis/
- /var/log/redis/redis_6379.log
- /etc/memcached.conf

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: Redis and memcached configuration templates rendered by external cookbooks

## Pre-flight checks:
```bash
# Service status for memcached
systemctl status memcached
ps aux | grep memcached

# Service status for redis-6379
systemctl status redis-server
ps aux | grep redis-server

# Redis connectivity and authentication for redis-6379
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing
ls -lah /var/log/redis/
ls -lah /etc/redis/

# Redis configuration fix verification for redis-6379
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # should return 0
grep -c "replica-read-only" /etc/redis/6379.conf  # should return 0
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # should return 0
grep -c "client-output-buffer-limit" /etc/redis/6379.conf  # should return 0
grep -c "replica-priority" /etc/redis/6379.conf  # should return 0

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Memory and performance for redis-6379
redis-cli -p 6379 -a redis_secure_password_123 info memory
redis-cli -p 6379 -a redis_secure_password_123 info stats

# Memory and performance for memcached
echo "stats" | nc localhost 11211 | grep -E 'bytes|curr_items|total_items'

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid|Access.*0755'
```