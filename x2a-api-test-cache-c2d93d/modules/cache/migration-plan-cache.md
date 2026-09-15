---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes configuration cleanup via ruby_block manipulation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Single instance cache server
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), log directory at /var/log/redis

- **Memcached**: Default memcached instance (configured via external cookbook)
  - Location/Path: Managed by memcached cookbook dependency
  - Port/Socket: Default memcached port (11211)
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
     - Password: 'redis_secure_password_123' (hardcoded)
     - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block[fix_redis_config] to clean up Redis configuration file:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start Redis service
   - Resources: directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: redis-server, memcached (installed via dependency cookbooks)
**Service dependencies**: redis, memcached systemd services (managed by external cookbooks)

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
- **Usage context**: Redis server authentication password for client connections

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration)
- /var/log/redis/ (Redis log directory)
- /var/log/memcached.log (Memcached logs)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (Memcached)
- Unix sockets: None
- Network interfaces: localhost binding (default)

**Templates rendered**: None (configurations managed by external dependency cookbooks)

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
telnet localhost 11211  # then type: stats, quit

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # should return nothing after cleanup
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'  # should show redis:redis ownership

# Redis functionality test
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key  # should return "test_value"
redis-cli -p 6379 -a redis_secure_password_123 del test_key

# Memcached functionality test
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
ps aux | grep -E 'redis|memcached' | awk '{print $2}' | xargs -I {} cat /proc/{}/status | grep VmRSS
```