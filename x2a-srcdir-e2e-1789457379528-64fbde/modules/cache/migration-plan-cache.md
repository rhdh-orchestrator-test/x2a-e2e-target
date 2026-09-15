---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. This is a minimal cache service configuration with no custom configuration, authentication, or clustering - just a basic Redis instance running on default settings.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default Redis configuration (/etc/redis/redis.conf)
  - Port/Socket: Default Redis port 6379
  - Key Config: Default Redis settings (no custom configuration applied)

## File Structure

**Recipes:**
```
cookbooks/cache/recipes/default.rb
```

**Providers:**
```
(None - uses only built-in Chef resources)
```

**Templates:**
```
(None - no custom configuration templates)
```

**Attributes:**
```
(None - no attribute files present)
```

**Files:**
```
(None - no static files deployed)
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Resources used - package (1), service (1)
   - Step 3: Enables and starts redis-server service with default configuration
   - Iterations: No iterations - single Redis instance with default settings

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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. The Redis instance runs with default configuration and no authentication.

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf (default Redis configuration)
- /var/lib/redis/ (Redis data directory)
- /var/log/redis/redis-server.log (Redis log file)

**Service endpoints to check**:
- Port 6379 (default Redis port)
- Unix socket /var/run/redis/redis-server.sock (if enabled in default config)

**Templates rendered**: 0 templates rendered (uses default Redis configuration)

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

# Service logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
journalctl -u redis-server --no-pager -n 50

# Network listening for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory and permissions for redis-server instance
ls -lah /var/lib/redis/
ls -lah /var/log/redis/
ps aux | grep redis | grep -v grep

# Memory usage for redis-server instance
redis-cli info memory | grep used_memory_human
redis-cli info memory | grep used_memory_peak_human
free -h

# Redis performance check for redis-server instance
redis-cli --latency -h 127.0.0.1 -p 6379
redis-cli eval "return redis.call('ping')" 0
```