---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It installs both services, configures Redis on port 6379 with password authentication, creates necessary directories, and applies configuration fixes to remove specific Redis replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Default system installation
  - Port/Socket: 11211
  - Key Config: Uses external memcached cookbook defaults

- **redis**: Redis server with authentication
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
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to remove specific Redis replica settings from /etc/redis/6379.conf
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe, directory, ruby_block

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

### Redis Authentication Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis authentication password for client connections to Redis server on port 6379

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/

**Service endpoints to check**:
- 6379 (Redis)
- 11211 (memcached)

**Templates rendered**:
- No templates rendered by this cookbook (handled by external dependencies)

## Pre-flight checks:
```bash
# Service status - memcached
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
echo "stats" | nc localhost 11211

# Service status - redis
systemctl status redis-server
ps aux | grep redis-server
netstat -tulpn | grep 6379
redis-cli -p 6379 -a redis_secure_password_123 ping

# Redis authentication verification
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
ls -lah /etc/redis/

# Redis configuration fix verification
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # should return 0
grep -c "replica-read-only" /etc/redis/6379.conf  # should return 0
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # should return 0

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
journalctl -u memcached -f
```