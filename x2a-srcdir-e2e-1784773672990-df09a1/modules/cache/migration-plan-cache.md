---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This is a simple cache cookbook that installs and enables Redis server. It has a single instance with default configuration and no customization.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis server instance
  - Location/Path: Default system paths (/etc/redis, /var/lib/redis)
  - Port/Socket: Default Redis port (6379)
  - Key Config: Default Redis configuration

## File Structure

```
recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs Redis server package
   - Enables and starts the Redis server service
   - Resources: package (1), service (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: redis-server
**Service dependencies**: redis-server

## Credentials

**Detection Summary**: 0 credentials detected across 1 file

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf
- /var/lib/redis
- /var/log/redis/redis-server.log

**Service endpoints to check**:
- Ports listening: 6379
- Unix sockets: /var/run/redis/redis-server.sock (if configured)
- Network interfaces: Default (0.0.0.0 or 127.0.0.1 depending on default configuration)

**Templates rendered**:
None - this cookbook uses the default Redis configuration

## Pre-flight checks:
```bash
# Service status
systemctl status redis-server
ps aux | grep redis

# Redis connectivity
redis-cli ping  # Should return "PONG"
redis-cli info server | grep redis_version
redis-cli info clients | grep connected_clients

# Configuration validation
cat /etc/redis/redis.conf | grep -E 'port|bind|daemonize|pidfile'

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f

# Network listening
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directories
ls -lah /var/lib/redis/
df -h /var/lib/redis/

# Memory usage
ps aux | grep redis-server | awk '{print $2}' | xargs -I {} cat /proc/{}/status | grep VmRSS
redis-cli info memory | grep used_memory_human
```