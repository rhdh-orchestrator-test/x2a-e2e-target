---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This is a simple Redis cache cookbook that installs the Redis server package and ensures the service is enabled and running. It has no configuration customization.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis server instance
  - Location/Path: Default system paths
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
   - Enables and starts the Redis server service
   - Resources: package (1), service (1)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: redis-server
**Service dependencies**: redis-server

## Credentials

**Detection Summary**: 0 credentials detected across 0 files

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf (default Redis configuration)
- /var/log/redis/redis-server.log

**Service endpoints to check**:
- Ports listening: 6379 (default Redis port)
- Unix sockets: /var/run/redis/redis-server.sock (default Redis socket)
- Network interfaces: 127.0.0.1 (default Redis binding)

**Templates rendered**:
No templates are rendered by this cookbook.

## Pre-flight checks:
```bash
# Service status
systemctl status redis-server
ps aux | grep redis-server

# Redis connectivity
redis-cli ping  # Should return "PONG"
redis-cli info server | grep redis_version
redis-cli info clients | grep connected_clients

# Configuration validation
cat /etc/redis/redis.conf | grep -E 'port|bind|daemonize|logfile'

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
```