---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes a configuration fix to remove specific replica-related settings. The cookbook depends on external memcached and redisio cookbooks for the actual service installation and configuration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Primary Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: requirepass='redis_secure_password_123', replica settings removed

- **Memcached**: Standard memcached service (configuration handled by external cookbook)
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
   - Includes memcached cookbook for memcached service setup
   - Configures Redis server attributes:
     - Sets port to 6379
     - Sets requirepass to 'redis_secure_password_123'
     - Disables replicaservestaledata
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to remove replica-related settings from /etc/redis/6379.conf:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: directory (1), ruby_block (1), include_recipe (3)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: redis-server, memcached (installed by dependency cookbooks)
**Service dependencies**: redis, memcached systemd services

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Database/Cache Authentication Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis server authentication password for client connections

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)
- /var/log/redis/redis_6379.log (Redis log file)
- /etc/memcached.conf (Memcached configuration file)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (Memcached)
- Unix sockets: None
- Network interfaces: All interfaces (default binding)

**Templates rendered**:
- Redis configuration templates rendered by redisio cookbook
- Memcached configuration templates rendered by memcached cookbook

## Pre-flight checks:
```bash
# Service status for Redis instance
systemctl status redis_6379
ps aux | grep redis-server

# Service status for Memcached instance
systemctl status memcached
ps aux | grep memcached

# Redis connectivity and authentication
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211  # then type: stats, quit

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing
cat /etc/memcached.conf

# Directory and permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Access.*Uid.*redis.*Gid.*redis'

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis-server
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Test basic operations
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key  # should return "test_value"
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Memcached test
echo -e "set test_key 0 60 10\r\ntest_value\r\nget test_key\r\nquit\r\n" | nc localhost 11211
```