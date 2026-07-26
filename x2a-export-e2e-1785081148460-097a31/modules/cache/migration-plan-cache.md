---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two caching services: Memcached and Redis. It sets up a single Redis instance with authentication on port 6379 and includes Memcached configuration from a dependency cookbook. The cookbook applies a configuration fix for Redis by removing certain replication-related settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis 6379**: Primary Redis instance
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Authentication enabled with password 'redis_secure_password_123'

- **Memcached**: Default Memcached instance
  - Location/Path: Default from memcached cookbook
  - Port/Socket: Default (likely 11211)
  - Key Config: Default from memcached cookbook

## File Structure

```
cookbooks/cache/recipes/default.rb
cookbooks/cache/metadata.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached recipe from external dependency
   - Sets Redis configuration attributes:
     - port: 6379
     - requirepass: redis_secure_password_123
     - replicaservestaledata: nil
   - Creates Redis log directory at /var/log/redis
     - Owner: redis
     - Group: redis
     - Mode: 0755
     - Recursive: true
   - Resources: directory (1)
   - Includes redisio recipe from external dependency
   - Executes ruby_block to fix Redis configuration:
     - Removes replication-related settings from /etc/redis/6379.conf:
       - replica-serve-stale-data
       - replica-read-only
       - repl-ping-replica-period
       - client-output-buffer-limit
       - replica-priority
   - Resources: ruby_block (1)
   - Includes redisio::enable recipe from external dependency

## Dependencies

**External cookbook dependencies**:
- memcached (~> 6.0)
- redisio

**System package dependencies**:
- Redis server (installed by redisio cookbook)
- Memcached server (installed by memcached cookbook)

**Service dependencies**:
- redis@6379 (systemd service managed by redisio cookbook)
- memcached (systemd service managed by memcached cookbook)

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
- **Usage context**: Redis server authentication password used to secure Redis instance

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf
- /var/log/redis/
- /etc/memcached.conf (likely path from memcached cookbook)

**Service endpoints to check**:
- Ports listening: 6379 (Redis), 11211 (likely Memcached default)
- Unix sockets: None specified
- Network interfaces: Default (likely 0.0.0.0 or 127.0.0.1)

**Templates rendered**:
- None directly in this cookbook (Redis config is managed by redisio cookbook)

## Pre-flight checks:

```bash
# Redis Service status
systemctl status redis@6379
ps aux | grep redis

# Redis connectivity
redis-cli -h localhost -p 6379 ping
redis-cli -h localhost -p 6379 -a 'redis_secure_password_123' ping
redis-cli -h localhost -p 6379 -a 'redis_secure_password_123' info server

# Redis configuration validation
grep requirepass /etc/redis/6379.conf
grep -v "replica-serve-stale-data\|replica-read-only\|repl-ping-replica-period\|client-output-buffer-limit\|replica-priority" /etc/redis/6379.conf

# Redis logs
tail -f /var/log/redis/redis_6379.log

# Memcached Service status
systemctl status memcached
ps aux | grep memcached

# Memcached connectivity
echo stats | nc localhost 11211
memcached-tool localhost:11211 stats

# Memcached configuration
cat /etc/memcached.conf

# Memcached logs
journalctl -u memcached -f

# Network listening
netstat -tulpn | grep 6379
netstat -tulpn | grep 11211
ss -tlnp | grep redis
ss -tlnp | grep memcached
lsof -i :6379
lsof -i :11211

# Resource usage
ps aux | grep redis-server
ps aux | grep memcached
```