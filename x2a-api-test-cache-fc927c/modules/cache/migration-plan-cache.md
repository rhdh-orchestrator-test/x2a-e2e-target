---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It installs both services via external cookbook dependencies, creates a Redis log directory, configures Redis with password authentication on port 6379, and applies configuration fixes to remove deprecated replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached instance
  - Location/Path: Default system paths (managed by memcached cookbook)
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration

- **redis**: Single Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration with authentication:
     - Port: 6379
     - Password: 'redis_secure_password_123'
     - Removes replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fixes via ruby_block to remove deprecated replica settings:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (installed via dependency cookbooks)
**Service dependencies**: memcached, redis-server systemd services

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
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/

**Service endpoints to check**:
- Port 6379 (redis)
- Port 11211 (memcached)

**Templates rendered**: None (configuration handled by dependency cookbooks)

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

# Configuration validation - redis
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'

# Connectivity tests - memcached
telnet localhost 11211
echo -e "set test 0 0 5\r\nhello\r\nget test\r\nquit\r\n" | nc localhost 11211

# Connectivity tests - redis
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass
redis-cli -p 6379 -a redis_secure_password_123 info memory
```