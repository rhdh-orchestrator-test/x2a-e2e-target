---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both Memcached and Redis with authentication. Redis is configured on port 6379 with password authentication and includes a configuration cleanup hack to remove replica-related settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Single Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (redis_secure_password_123), replica settings removed via post-configuration cleanup

- **Memcached Server**: Default memcached instance (configured via external cookbook)
  - Location/Path: Managed by memcached cookbook dependency
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration

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
     - Password: redis_secure_password_123 (requirepass)
     - Removes replicaservestaledata setting (set to nil)
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes configuration cleanup via ruby_block to remove replica-related settings from /etc/redis/6379.conf:
     - Removes: replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: directory (1), ruby_block (1)

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
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/
- /etc/memcached.conf

**Service endpoints to check**:
- 6379 (Redis)
- 11211 (Memcached)

**Templates rendered**: No templates in this cookbook (handled by dependency cookbooks)

## Pre-flight checks:
```bash
# Service status - Redis Server
systemctl status redis
ps aux | grep redis-server
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Service status - Memcached Server
systemctl status memcached
ps aux | grep memcached
echo "stats" | nc localhost 11211
memcstat --servers=localhost:11211
netstat -tulpn | grep 11211
ss -tlnp | grep memcached
lsof -i :11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
stat -c "%U:%G %a" /var/log/redis

# Functionality tests
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key
redis-cli -p 6379 -a redis_secure_password_123 del test_key
echo -e "set test_key 0 60 10\r\ntest_value\r\nquit\r" | nc localhost 11211
echo -e "get test_key\r\nquit\r" | nc localhost 11211
echo -e "delete test_key\r\nquit\r" | nc localhost 11211

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis -f
journalctl -u memcached -f
tail -f /var/log/memcached.log

# Memory usage
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes
```