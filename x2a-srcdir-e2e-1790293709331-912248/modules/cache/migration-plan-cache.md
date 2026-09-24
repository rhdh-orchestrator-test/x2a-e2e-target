---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. This is a minimal cache service setup with no custom configuration, providing basic Redis functionality on the default port 6379.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default Redis installation paths (/etc/redis/, /var/lib/redis/)
  - Port/Socket: 6379 (default Redis port)
  - Key Config: Default Redis configuration (no custom settings applied)

## File Structure

**Recipes:**
```
cookbooks/cache/recipes/default.rb
```

**Providers:**
```
[None - uses only standard Chef resources]
```

**Templates:**
```
[None - no templates used]
```

**Attributes:**
```
[None - no attribute files present]
```

**Files:**
```
[None - no static files deployed]
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts redis-server service
   - Resources used: package (1), service (1)
   - Files/templates deployed: None - uses system defaults
   - Iterations: No iterations - single Redis instance with default configuration

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)
**System package dependencies**: redis-server
**Service dependencies**: redis-server (systemd service)

## Credentials

**Detection Summary**: 0 credentials detected across 1 file

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. The cookbook uses default Redis configuration without authentication.

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf (default Redis configuration)
- /var/lib/redis/ (Redis data directory)
- /var/log/redis/redis-server.log (Redis log file)

**Service endpoints to check**:
- Ports listening: 6379 (Redis default port)
- Unix sockets: /var/run/redis/redis-server.sock (if configured)
- Network interfaces: 127.0.0.1:6379 (default localhost binding)

**Templates rendered**: None - no templates are rendered by this cookbook

## Pre-flight checks:
```bash
# Service status for redis-server instance
systemctl status redis-server
ps aux | grep redis-server

# Redis connectivity and functionality for redis-server instance
redis-cli ping
redis-cli info server
redis-cli info memory
redis-cli info clients

# Basic Redis operations test for redis-server instance
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli del test_key

# Configuration validation for redis-server instance
cat /etc/redis/redis.conf | grep -E 'port|bind|dir|logfile'
redis-cli config get port
redis-cli config get bind
redis-cli config get dir

# Service auto-start verification for redis-server instance
systemctl is-enabled redis-server

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f

# Network listening for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory and permissions for redis-server instance
ls -lah /var/lib/redis/
ls -lah /var/run/redis/
df -h /var/lib/redis/

# Memory usage for redis-server instance
redis-cli info memory | grep used_memory_human
free -h
cat /proc/meminfo | grep MemAvailable

# Performance check for redis-server instance
redis-cli --latency -h 127.0.0.1 -p 6379
redis-cli eval "return redis.call('ping')" 0
```