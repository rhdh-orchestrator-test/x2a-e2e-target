---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis (port 6379) with authentication. The cookbook includes a workaround to clean up Redis configuration by removing specific replica-related directives from the config file.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Default memcached instance
  - Location/Path: Standard system installation
  - Port/Socket: 11211
  - Key Config: Uses memcached cookbook defaults

- **redis-6379**: Redis server instance
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica-serve-stale-data disabled

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
   - Executes ruby_block to clean Redis config file by removing replica-related directives
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: 5 total resources (3 include_recipe, 1 directory, 1 ruby_block)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (via dependency cookbooks)
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
- **Usage context**: Redis authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/
- /etc/memcached.conf
- /var/log/memcached.log

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**:
- Redis configuration templates rendered by redisio cookbook
- Memcached configuration templates rendered by memcached cookbook

## Pre-flight checks:
```bash
# Service status for memcached
systemctl status memcached
ps aux | grep memcached

# Service status for redis-6379
systemctl status redis-server
ps aux | grep redis-server

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211

# Redis connectivity and authentication for redis-6379
redis-cli -p 6379 ping
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
cat /etc/memcached.conf

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Access.*Uid.*redis.*Gid.*redis'

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

# Performance test
redis-cli -p 6379 -a redis_secure_password_123 --latency -i 1
echo -e "set test 0 0 5\r\nhello\r\nget test\r\nquit" | nc localhost 11211

# Logs
tail -f /var/log/redis/redis-server.log
tail -f /var/log/memcached.log
journalctl -u redis-server -f
journalctl -u memcached -f
```