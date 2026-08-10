---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This is a simple cache cookbook that installs and enables Redis server as a caching solution. It installs the redis-server package and ensures the service is enabled and running.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis server instance
  - Location/Path: Default system paths for Redis
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

**External cookbook dependencies**: None specified in metadata.rb
**System package dependencies**: redis-server
**Service dependencies**: redis-server

## Credentials

**Detection Summary**: 0 credentials detected across 2 files

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf (default Redis configuration file)
- /var/lib/redis (default Redis data directory)
- /var/log/redis/redis-server.log (default Redis log file)

**Service endpoints to check**:
- Ports listening: 6379 (default Redis port)
- Unix sockets: /var/run/redis/redis-server.sock (if configured to use Unix socket)
- Network interfaces: Default is 127.0.0.1 (localhost only)

**Templates rendered**:
No templates are rendered in this cookbook.

## Pre-flight checks:
```bash
# Service status
systemctl status redis-server
ps aux | grep redis

# Redis connectivity
redis-cli ping  # Should return "PONG"
redis-cli info server  # Should show Redis server information

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

# Memory usage
redis-cli info memory
ps aux | grep redis-server | awk '{print $2}' | xargs -I {} cat /proc/{}/status | grep VmRSS
```