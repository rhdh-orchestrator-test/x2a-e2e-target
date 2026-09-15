---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes a configuration fix to remove specific replica-related settings from the Redis config file.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Default system installation
  - Port/Socket: 11211
  - Key Config: Uses external memcached cookbook defaults

- **redis-6379**: Redis server with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed via post-config fix

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

**IMPORTANT: External cookbook dependencies (memcached, redisio) were not analyzed and may contain additional resources/configurations not captured in this migration specification.**

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration with port 6379 and password authentication
     - Password: 'redis_secure_password_123' (hardcoded)
     - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions via `directory[/var/log/redis]`
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via `ruby_block[fix_redis_config]` to remove replica-related settings from /etc/redis/6379.conf:
     - Removes: replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: include_recipe (3), directory (1), ruby_block (1)

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

### Database Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/
- /var/log/redis/redis_6379.log
- /etc/memcached.conf

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: No templates in this cookbook (relies on external cookbook templates)

## Pre-flight checks:
```bash
# Service status for memcached instance
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
ss -tlnp | grep memcached
lsof -i :11211

# Service status for redis-6379 instance
systemctl status redis-server
ps aux | grep redis-server
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Redis connectivity and authentication for redis-6379
redis-cli -p 6379 ping  # should fail without auth
redis-cli -p 6379 -a 'redis_secure_password_123' ping  # should return PONG
redis-cli -p 6379 -a 'redis_secure_password_123' info server
redis-cli -p 6379 -a 'redis_secure_password_123' config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211  # then type: stats, quit

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing
redis-cli -p 6379 -a 'redis_secure_password_123' config get port  # should show 6379

# Directory and permissions for redis-6379
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'  # should show redis user/group
ls -lah /var/log/redis/redis_6379.log

# Logs
tail -f /var/log/redis/redis_6379.log
journalctl -u redis-server -f
tail -f /var/log/memcached.log
journalctl -u memcached -f

# Memory usage
redis-cli -p 6379 -a 'redis_secure_password_123' info memory
echo "stats" | nc localhost 11211 | grep bytes

# Performance tests
redis-cli -p 6379 -a 'redis_secure_password_123' --latency -i 1  # Ctrl+C to stop
redis-cli -p 6379 -a 'redis_secure_password_123' eval "return 'hello world'" 0
echo -e "set test_key 0 60 5\r\nhello\r\nget test_key\r\nquit" | nc localhost 11211
```