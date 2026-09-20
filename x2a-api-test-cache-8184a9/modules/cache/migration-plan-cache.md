---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Cache service cookbook that configures memcached and Redis with authentication. Sets up a single Redis instance on port 6379 with password authentication and includes configuration fixes for replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server (port 6379)**: Primary Redis cache instance
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled, replica settings removed via post-config fix

- **Memcached**: Standard memcached service (configured via external cookbook)
  - Location/Path: Managed by memcached cookbook
  - Port/Socket: Default memcached port (11211)
  - Key Config: Default memcached configuration

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
   - Applies configuration fix via ruby_block to remove problematic replica settings from /etc/redis/6379.conf
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

### Redis Authentication Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis server authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf (Redis configuration)
- /var/log/redis/ (Redis log directory)
- /etc/memcached.conf (Memcached configuration, if exists)

**Service endpoints to check**:
- 6379 (Redis)
- 11211 (Memcached)

**Templates rendered**:
- No templates in this cookbook (handled by external dependencies)

## Pre-flight checks:
```bash
# Service status
systemctl status redis-server
systemctl status memcached
ps aux | grep redis-server
ps aux | grep memcached

# Redis connectivity and authentication
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
memcstat --servers=localhost:11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing after fix
ls -lah /var/log/redis/
stat -c "%U:%G %a" /var/log/redis  # should show redis:redis 755

# Redis functionality tests
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key  # should return "test_value"
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Memcached functionality tests
echo -e "set test_key 0 60 10\r\ntest_value\r\nquit\r" | nc localhost 11211
echo -e "get test_key\r\nquit\r" | nc localhost 11211  # should return test_value
echo -e "delete test_key\r\nquit\r" | nc localhost 11211

# Logs
tail -f /var/log/redis/redis-server.log
tail -f /var/log/memcached.log
journalctl -u redis-server -f
journalctl -u memcached -f

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Memory usage
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes
```