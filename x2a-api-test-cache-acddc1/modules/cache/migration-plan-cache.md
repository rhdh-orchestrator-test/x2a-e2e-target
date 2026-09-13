---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes configuration cleanup via ruby_block manipulation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Primary Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: requirepass='redis_secure_password_123', custom replica settings removed

- **Memcached**: Standard memcached service
  - Location/Path: Managed by memcached cookbook dependency
  - Port/Socket: 11211
  - Key Config: Default memcached configuration

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
     - Sets requirepass to 'redis_secure_password_123'
     - Disables replicaservestaledata
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block 'fix_redis_config' to clean up Redis configuration:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines  
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
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

### Redis Authentication Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: Hardcoded string value
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/

**Service endpoints to check**:
- 6379 (Redis)
- 11211 (Memcached)

**Templates rendered**: 0 (configuration handled by dependencies)

## Pre-flight checks:
```bash
# Service status for Redis Server
systemctl status redis
ps aux | grep redis-server
netstat -tulpn | grep 6379
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server

# Service status for Memcached
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
echo "stats" | nc localhost 11211

# Configuration validation for Redis Server
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
stat -c "%U:%G %a" /var/log/redis

# Redis configuration cleanup verification
grep -c "replica-serve-stale-data" /etc/redis/6379.conf
grep -c "replica-read-only" /etc/redis/6379.conf
grep -c "repl-ping-replica-period" /etc/redis/6379.conf
grep -c "client-output-buffer-limit" /etc/redis/6379.conf
grep -c "replica-priority" /etc/redis/6379.conf

# Performance testing for Redis Server
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Performance testing for Memcached
memcstat --servers=localhost:11211
```