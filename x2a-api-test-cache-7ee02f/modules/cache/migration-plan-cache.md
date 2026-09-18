---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis with authentication. It installs both services via external cookbook dependencies, creates a Redis log directory, configures Redis on port 6379 with password authentication, and applies configuration fixes to remove specific Redis replica settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **memcached**: Standard memcached service
  - Location/Path: Default system installation (via memcached cookbook)
  - Port/Socket: 11211
  - Key Config: Standard memcached configuration

- **redis**: Redis server with authentication
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
   - Sets Redis server configuration with port 6379 and password authentication
     - Password: 'redis_secure_password_123'
     - Removes replicaservestaledata setting (set to nil)
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fixes via ruby_block to remove specific Redis settings:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines  
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: directory (1), ruby_block (1) - external cookbook resources not counted

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (installed via external cookbooks)
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
- **Current storage**: Hardcoded
- **Usage context**: Redis server authentication password for client connections

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/6379.conf
- /var/log/redis/
- /var/log/redis/redis_6379.log

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: 0 (configuration handled by external cookbooks)

## Pre-flight checks:
```bash
# Service status - memcached instance
systemctl status memcached
ps aux | grep memcached
netstat -tulpn | grep 11211
ss -tlnp | grep memcached
lsof -i :11211

# Service status - redis instance
systemctl status redis-server
ps aux | grep redis-server
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Redis connectivity and authentication
redis-cli -p 6379 ping  # Should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # Should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211  # Should connect successfully

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # Should return no results after fix

# Directory and permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid|Access.*0755'

# Logs
tail -f /var/log/redis/redis_6379.log
journalctl -u redis-server -f
journalctl -u memcached -f

# Memory usage and performance
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes
redis-cli -p 6379 -a redis_secure_password_123 --latency -i 1
echo -e "set test_key 0 0 5\r\nhello\r\nget test_key\r\nquit" | nc localhost 11211
```