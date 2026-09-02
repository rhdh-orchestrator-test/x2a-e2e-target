---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a dual-cache setup with memcached and Redis services. It installs memcached via external cookbook dependency, configures a single Redis instance on port 6379 with authentication, and applies configuration fixes to remove problematic Redis replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Default memcached instance
  - Location/Path: Managed by external memcached cookbook
  - Port/Socket: Default memcached port (typically 11211)
  - Key Config: Standard memcached configuration

- **redis-6379**: Redis server instance with authentication
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
   - Sets Redis server configuration attributes:
     - Port: 6379
     - Password: redis_secure_password_123
     - Removes replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to remove problematic Redis replica settings:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines  
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (via external cookbooks)
**Service dependencies**: memcached.service, redis_6379.service

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
- **Usage context**: Redis authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf (Redis configuration)
- /var/log/redis/ (Redis log directory)
- /var/log/memcached.log (memcached logs, if configured)

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**:
- Redis configuration templates rendered by redisio cookbook
- Memcached configuration templates rendered by memcached cookbook

## Pre-flight checks:
```bash
# Service status for memcached instance
systemctl status memcached
ps aux | grep memcached

# Service status for redis-6379 instance
systemctl status redis_6379
ps aux | grep redis-server

# Redis connectivity and authentication for redis-6379
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity for memcached instance
echo "stats" | nc localhost 11211
telnet localhost 11211  # then type: stats, quit

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'  # should show redis:redis ownership

# Redis configuration fix verification for redis-6379
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # should return 0
grep -c "replica-read-only" /etc/redis/6379.conf  # should return 0
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # should return 0
grep -c "client-output-buffer-limit" /etc/redis/6379.conf  # should return 0
grep -c "replica-priority" /etc/redis/6379.conf  # should return 0

# Network listening verification
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Cache functionality tests for redis-6379
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key  # should return "test_value"
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Cache functionality tests for memcached
echo -e "set test_key 0 60 10\r\ntest_value\r\nquit\r" | nc localhost 11211
echo -e "get test_key\r\nquit\r" | nc localhost 11211  # should return test_value
echo -e "delete test_key\r\nquit\r" | nc localhost 11211

# Memory usage checks
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes

# Log verification
tail -f /var/log/redis/redis_6379.log
journalctl -u redis_6379 -f
tail -f /var/log/memcached.log
journalctl -u memcached -f
```