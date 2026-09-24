---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services by creating a Redis log directory and applying configuration fixes to remove deprecated replica settings. It relies on external cookbooks (memcached and redisio) for actual service installation and configuration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-6379**: Redis server instance (configured via redisio cookbook)
  - Location/Path: /etc/redis/6379.conf
  - Port/Socket: 6379
  - Key Config: Password authentication, replica settings cleanup

- **memcached**: Standard memcached installation (configured via memcached cookbook)
  - Location/Path: Default system paths
  - Port/Socket: 11211
  - Key Config: Managed by external cookbook

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes memcached cookbook for memcached installation and configuration
   - Sets Redis server configuration attributes for port 6379 and password authentication
   - Creates Redis log directory /var/log/redis with redis:redis ownership and 0755 permissions
   - Includes redisio cookbook for Redis installation and configuration
   - Applies configuration fixes via ruby_block to remove deprecated replica settings from /etc/redis/6379.conf
   - Includes redisio::enable recipe to start and enable Redis service
   - Resources: directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: memcached (~> 6.0), redisio
**System package dependencies**: memcached, redis-server (installed via dependency cookbooks)
**Service dependencies**: memcached, redis-server systemd services

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Redis Authentication Password
- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb
- **Current storage**: Hardcoded value
- **Usage context**: Redis authentication password for client connections

## Checks for the Migration

**Files to verify**:
- /etc/redis/6379.conf
- /var/log/redis/
- /etc/memcached.conf

**Service endpoints to check**:
- Port 6379 (Redis)
- Port 11211 (memcached)

**Templates rendered**: None (handled by dependency cookbooks)

## Pre-flight checks:
```bash
# Service status for redis-6379
systemctl status redis-server
ps aux | grep redis-server

# Service status for memcached
systemctl status memcached
ps aux | grep memcached

# Redis connectivity and authentication for redis-6379
redis-cli -p 6379 ping
redis-cli -p 6379 -a redis_secure_password_123 ping
redis-cli -p 6379 -a redis_secure_password_123 info server

# Memcached connectivity
echo "stats" | nc localhost 11211
telnet localhost 11211

# Configuration validation for redis-6379
cat /etc/redis/6379.conf | grep requirepass
cat /etc/redis/6379.conf | grep port
cat /etc/redis/6379.conf | grep -E 'replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority'

# Directory permissions
ls -lah /var/log/redis/
stat /var/log/redis | grep -E 'Uid|Gid|Access.*0755'

# Network listening for redis-6379
netstat -tulpn | grep 6379
lsof -i :6379

# Network listening for memcached
netstat -tulpn | grep 11211
lsof -i :11211

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
tail -f /var/log/memcached.log
journalctl -u memcached -f
```