---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts redis-server package. Single instance configuration with default Redis settings on port 6379.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: /var/lib/redis (default data directory)
  - Port/Socket: 6379 (default Redis port)
  - Key Config: Default Redis configuration, no custom settings applied

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
   - Step 3: No custom configuration files deployed - uses system defaults
   - Iterations: Single Redis instance with default configuration (no loops)

## Dependencies

**External cookbook dependencies**: None (no dependencies in metadata.rb)
**System package dependencies**: redis-server
**Service dependencies**: redis-server (systemd service)

## Credentials

**Detection Summary**: 0 credentials detected across 1 files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /var/lib/redis/ (Redis data directory)
- /var/log/redis/ (Redis log directory)
- /etc/redis/redis.conf (Redis configuration file)

**Service endpoints to check**:
- Ports listening: 6379 (Redis default port)
- Unix sockets: /var/run/redis/redis-server.sock (if configured)
- Network interfaces: 127.0.0.1:6379 (default localhost binding)

**Templates rendered**: No templates are rendered by this cookbook.

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

# Service performance for redis-server instance
redis-cli info stats
redis-cli info replication
redis-cli info persistence

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -20

# Network listening for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory and permissions for redis-server instance
ls -lah /var/lib/redis/
df -h /var/lib/redis/
ps aux | grep redis | awk '{print $1}' | head -1 | xargs id

# Memory usage for redis-server instance
redis-cli info memory | grep used_memory_human
ps aux | grep redis-server | awk '{print $6}'
cat /proc/$(pgrep redis-server)/status | grep VmRSS
```