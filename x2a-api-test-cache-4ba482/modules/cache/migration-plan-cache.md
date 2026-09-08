---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Cache service cookbook that configures both memcached and Redis caching services. Deploys a single Redis instance on port 6379 with authentication and includes memcached via external cookbook dependency. Contains hardcoded Redis password requiring credential management migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server (port 6379)**: Primary Redis cache instance
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Authentication enabled with password, custom configuration cleanup via ruby_block

- **Memcached**: Caching service via external cookbook dependency
  - Location/Path: Managed by memcached cookbook
  - Port/Socket: Default memcached port (11211)
  - Key Config: Standard memcached configuration

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached service setup
   - Configures Redis server attributes inline:
     - Port: 6379
     - Authentication: requirepass set to 'redis_secure_password_123'
     - Replica configuration: replicaservestaledata set to nil
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Executes ruby_block 'fix_redis_config' to clean up Redis configuration:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines  
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: Redis server, memcached (via external cookbooks)
**Service dependencies**: redis-server, memcached systemd services

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None
  - **Path**: None

### Database/Cache Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis server authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)
- /var/log/redis/redis_6379.log (Redis log file)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (memcached)

**Templates rendered**:
- No templates in this cookbook (handled by external dependencies)

## Pre-flight checks:
```bash
# Service status
systemctl status redis_6379
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
cat /etc/redis/6379.conf | grep -E 'port|bind'
# Verify cleaned config (should NOT contain these lines)
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority' | wc -l  # should be 0

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Access.*Uid.*redis.*Gid.*redis'

# Logs
tail -f /var/log/redis/redis_6379.log
journalctl -u redis_6379 -f
tail -f /var/log/memcached.log
journalctl -u memcached -f

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis-server
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Memory usage
redis-cli -p 6379 -a redis_secure_password_123 info memory
echo "stats" | nc localhost 11211 | grep bytes

# Performance testing
redis-cli -p 6379 -a redis_secure_password_123 --latency -i 1
redis-cli -p 6379 -a redis_secure_password_123 set test_key "test_value"
redis-cli -p 6379 -a redis_secure_password_123 get test_key  # should return "test_value"
redis-cli -p 6379 -a redis_secure_password_123 del test_key
```