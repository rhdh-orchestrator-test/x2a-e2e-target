---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures dual caching services - memcached and Redis. It sets up a single Redis instance on port 6379 with authentication and includes memcached via dependency. The cookbook performs configuration cleanup on Redis config files to remove replica-related settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **Redis Server**: Primary Redis instance with authentication
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: requirepass='redis_secure_password_123', replica settings removed

- **Memcached**: Default memcached instance via dependency cookbook
  - Location/Path: Managed by memcached cookbook dependency
  - Port/Socket: 11211
  - Key Config: Default memcached configuration

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration inline with port 6379 and authentication
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Performs configuration cleanup via ruby_block to remove replica-related settings from /etc/redis/6379.conf
     - Removes: replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, replica-priority
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: redis-server, memcached (via dependency cookbooks)
**Service dependencies**: redis, memcached systemd services

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
- **Usage context**: Redis authentication password for port 6379 instance

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf
- /var/log/redis/
- /etc/memcached.conf

**Service endpoints to check**:
- 6379 (Redis)
- 11211 (Memcached)

**Templates rendered**: None

## Pre-flight checks:
```bash
# Service status
systemctl status redis
systemctl status memcached
ps aux | grep redis-server
ps aux | grep memcached

# Redis connectivity and authentication
redis-cli -p 6379 ping
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server
redis-cli -p 6379 -a redis_secure_password_123 config get requirepass

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211

# Configuration validation
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'
ls -lah /var/log/redis/
cat /etc/memcached.conf

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid|Access'
```