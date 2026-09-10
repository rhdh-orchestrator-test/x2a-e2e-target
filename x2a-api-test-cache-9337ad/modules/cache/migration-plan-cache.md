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
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)
- /etc/memcached.conf (Memcached configuration, managed by dependency)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (Memcached)

**Templates rendered**:
- No templates rendered directly by this cookbook (handled by dependencies)

## Pre-flight checks:
```bash
# Service status
systemctl status redis
systemctl status memcached
ps aux | grep redis-server
ps aux | grep memcached

# Redis connectivity and authentication
redis-cli -p 6379 ping  # Should fail without auth
redis-cli -p 6379 -a redis_secure_password_123 ping  # Should return PONG
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
memcstat --servers=localhost:11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'  # Should return nothing
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid'  # Should show redis:redis ownership

# Redis configuration cleanup verification
grep -c "replica-serve-stale-data" /etc/redis/6379.conf  # Should be 0
grep -c "replica-read-only" /etc/redis/6379.conf  # Should be 0
grep -c "repl-ping-replica-period" /etc/redis/6379.conf  # Should be 0
grep -c "client-output-buffer-limit" /etc/redis/6379.conf  # Should be 0
grep -c "replica-priority" /etc/redis/6379.conf  # Should be 0

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Performance and memory usage
redis-cli -p 6379 -a redis_secure_password_123 info memory
redis-cli -p 6379 -a redis_secure_password_123 info stats
echo "stats" | nc localhost 11211 | grep -E 'bytes|curr_items|total_items'

# Data persistence (Redis)
redis-cli -p 6379 -a redis_secure_password_123 lastsave
ls -lah /var/lib/redis/

# Logs
tail -f /var/log/redis/redis-server.log
tail -f /var/log/memcached.log
journalctl -u redis -f
journalctl -u memcached -f
```