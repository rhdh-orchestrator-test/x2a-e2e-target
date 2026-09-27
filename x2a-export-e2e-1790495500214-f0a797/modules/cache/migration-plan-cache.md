---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: A caching services cookbook that configures both memcached and Redis with authentication. It sets up a single Redis instance on port 6379 with password authentication and includes a configuration fix to remove specific replica-related settings from the Redis config file.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Single instance cache server
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication enabled (requirepass), replica settings removed via post-config fix

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
   - Sets Redis server configuration with authentication:
     - Port: 6379
     - Password: redis_secure_password_123
     - Disables replicaservestaledata setting
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fix via ruby_block to remove replica-related settings from /etc/redis/6379.conf:
     - Removes replica-serve-stale-data lines
     - Removes replica-read-only lines
     - Removes repl-ping-replica-period lines
     - Removes client-output-buffer-limit lines
     - Removes replica-priority lines
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: redis-server, memcached (installed via dependency cookbooks)
**Service dependencies**: redis, memcached systemd services

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Inline Recipe Code
  - **URL**: N/A
  - **Path**: N/A

### Database/Cache Authentication Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: Redis server authentication password for client connections

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf (Redis configuration file)
- /var/log/redis/ (Redis log directory)
- /var/log/redis/redis_6379.log (Redis log file)
- /etc/memcached.conf (Memcached configuration file)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (Memcached)

**Templates rendered**:
No templates are rendered by this cookbook directly - configuration is handled by dependency cookbooks (memcached and redisio).

## Pre-flight checks:
```bash
# Service status for Redis Server
systemctl status redis
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
stat /var/log/redis | grep -E 'Access.*Uid.*redis'

# Redis configuration fix verification
grep -c "replica-serve-stale-data" /etc/redis/6379.conf
grep -c "replica-read-only" /etc/redis/6379.conf
grep -c "repl-ping-replica-period" /etc/redis/6379.conf
grep -c "client-output-buffer-limit" /etc/redis/6379.conf
grep -c "replica-priority" /etc/redis/6379.conf

# Performance monitoring
redis-cli -p 6379 -a redis_secure_password_123 info memory
redis-cli -p 6379 -a redis_secure_password_123 info stats
echo "stats" | nc localhost 11211 | grep -E 'bytes|curr_items|total_items'
```