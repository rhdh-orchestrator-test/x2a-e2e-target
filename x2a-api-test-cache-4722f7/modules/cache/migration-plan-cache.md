---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes configuration cleanup via ruby_block manipulation. The cookbook depends on external memcached and redisio cookbooks for the actual service installation and configuration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server (port 6379)**: Primary Redis cache instance
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed via config cleanup

- **Memcached**: Standard memcached service (configuration handled by external cookbook)
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
   - Includes memcached cookbook for memcached service setup
   - Configures Redis server attributes with authentication:
     - Port: 6379
     - Password: redis_secure_password_123
     - Removes replicaservestaledata setting (set to nil)
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes configuration cleanup via ruby_block to remove replica-related settings from /etc/redis/6379.conf:
     - Removes: replica-serve-stale-data, replica-read-only, repl-ping-replica-period
     - Removes: client-output-buffer-limit, replica-priority
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

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

### Database/Cache Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis authentication password for client connections to port 6379

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)
- /etc/memcached.conf (Memcached configuration - managed by dependency)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (Memcached)
- Unix sockets: None specified
- Network interfaces: Default binding (all interfaces)

**Templates rendered**:
- Redis configuration templates rendered by redisio cookbook
- Memcached configuration templates rendered by memcached cookbook

## Pre-flight checks:
```bash
# Service status for Redis Server (port 6379)
systemctl status redis-server
ps aux | grep redis-server
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass
netstat -tulpn | grep 6379
lsof -i :6379

# Service status for Memcached
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
memcstat --servers=localhost:11211
netstat -tulpn | grep 11211
lsof -i :11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
cat /etc/memcached.conf

# Functionality tests
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key
echo -e "set test_key 0 60 10\r\ntest_value\r\nquit\r" | nc localhost 11211
echo -e "get test_key\r\nquit\r" | nc localhost 11211
echo -e "delete test_key\r\nquit\r" | nc localhost 11211

# Logs
tail -f /var/log/redis/redis-server.log
tail -f /var/log/memcached.log
journalctl -u redis-server -f
journalctl -u memcached -f
```