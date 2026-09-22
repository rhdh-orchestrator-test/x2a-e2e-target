---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes a configuration fix to remove specific replica-related settings from the Redis config file.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Default memcached instance
  - Location/Path: Standard system installation
  - Port/Socket: 11211
  - Key Config: Uses external memcached cookbook defaults

- **redis-6379**: Redis server instance with authentication
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
   - Step 1: Includes memcached recipe from external memcached cookbook
   - Step 2: Configures Redis server attributes (port 6379, password authentication with 'redis_secure_password_123', disables replicaservestaledata)
   - Step 3: Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Step 4: Includes redisio recipe from external redisio cookbook for Redis installation
   - Step 5: Executes ruby_block to fix Redis configuration by removing replica-related settings (replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority lines)
   - Step 6: Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)
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
- /var/log/redis/redis_6379.log
- /etc/memcached.conf

**Service endpoints to check**: 
- Port 6379 (Redis)
- Port 11211 (Memcached)

**Templates rendered**: Redis and Memcached configuration templates rendered by external cookbooks (count varies by cookbook implementation)

## Pre-flight checks:
```bash
# Service status for memcached instance
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
lsof -i :11211

# Service status for redis-6379 instance  
systemctl status redis-server
ps aux | grep redis-server
netstat -tulpn | grep 6379
lsof -i :6379

# Memcached connectivity and functionality
echo "stats" | nc localhost 11211
memcstat --servers=localhost:11211
echo "stats" | nc localhost 11211 | grep -E 'bytes|curr_items|total_items'

# Redis-6379 connectivity and authentication
redis-cli -p 6379 ping  # Should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # Should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass
redis-cli -p 6379 -a redis_secure_password_123 info memory
redis-cli -p 6379 -a redis_secure_password_123 info stats

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # Should return 0
grep -c "replica-read-only" /etc/redis/6379.conf  # Should return 0
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # Should return 0
grep -c "client-output-buffer-limit" /etc/redis/6379.conf  # Should return 0
grep -c "replica-priority" /etc/redis/6379.conf  # Should return 0

# Directory and file permissions for redis-6379
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid|Access.*0755'
tail -f /var/log/redis/redis_6379.log

# Configuration validation for memcached
cat /etc/memcached.conf

# Service logs
journalctl -u redis-server -f
journalctl -u memcached -f
tail -f /var/log/memcached.log
```