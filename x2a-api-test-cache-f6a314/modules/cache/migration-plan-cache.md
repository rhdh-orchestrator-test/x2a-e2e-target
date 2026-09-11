---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. Redis is configured on port 6379 with a hardcoded password and includes custom configuration cleanup via ruby_block manipulation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Default system installation
  - Port/Socket: 11211
  - Key Config: Managed by external memcached cookbook dependency

- **redis**: Redis server with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: 
    - Authentication enabled with password: `redis_secure_password_123`
    - Custom configuration cleanup removes replica-related settings
    - Log directory: /var/log/redis
    - Owner: redis user/group

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
     - Password: `redis_secure_password_123` (hardcoded)
     - Disables `replicaservestaledata` setting
   - Creates Redis log directory `/var/log/redis` with redis:redis ownership and 0755 permissions
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

**External cookbook dependencies**: 
- memcached (~> 6.0)
- redisio

**System package dependencies**: 
- memcached (via memcached cookbook)
- redis-server (via redisio cookbook)

**Service dependencies**: 
- memcached service
- redis service (port 6379)

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
- **Usage context**: Redis authentication password for server on port 6379

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
# Service status for memcached instance
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
netstat -tulpn | grep 11211
lsof -i :11211

# Service status for redis instance  
systemctl status redis-server
systemctl status redis_6379
ps aux | grep redis-server
netstat -tulpn | grep 6379
lsof -i :6379

# Redis connectivity and authentication for redis instance
redis-cli -p 6379 ping
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Configuration validation for redis instance
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Access.*Uid.*redis'

# Memory usage checks
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes

# Log monitoring
tail -f /var/log/redis/redis_6379.log
journalctl -u redis-server -f
journalctl -u memcached -f
```