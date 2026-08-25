---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This is a simple Redis cache service cookbook that installs the Redis server package and ensures the service is enabled and running. It has no custom configurations or multiple instances.

## Service Type and Instances

**Service Type**: Cache (Redis)

**Configured Instances**:
- **redis-server**: Default Redis server instance
  - Location/Path: Default system paths (/etc/redis, /var/lib/redis)
  - Port/Socket: Default Redis port (6379)
  - Key Config: Uses default Redis configuration

## File Structure

```
recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs Redis server package
   - Enables and starts the Redis service
   - Resources: package (1), service (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: redis-server
**Service dependencies**: redis-server (systemd service)

## Credentials

**Detection Summary**: 0 credentials detected across 0 files

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf (default Redis configuration)
- /var/lib/redis (data directory)
- /var/log/redis/redis-server.log (log file)

**Service endpoints to check**:
- Ports listening: 6379 (default Redis port)
- Unix sockets: /var/run/redis/redis-server.sock (if configured)
- Network interfaces: Default is 127.0.0.1 (localhost only)

**Templates rendered**:
None - this cookbook uses the default Redis configuration

## Pre-flight checks:
```bash
# Service status
systemctl status redis-server
ps aux | grep redis

# Redis connectivity
redis-cli ping  # Should return "PONG"
redis-cli info server  # Check Redis version and uptime
redis-cli info clients  # Check connected clients

# Configuration validation
cat /etc/redis/redis.conf | grep -E 'port|bind|maxmemory'

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

# Basic functionality test
redis-cli set test_key "Hello Redis"
redis-cli get test_key  # Should return "Hello Redis"
redis-cli del test_key
```