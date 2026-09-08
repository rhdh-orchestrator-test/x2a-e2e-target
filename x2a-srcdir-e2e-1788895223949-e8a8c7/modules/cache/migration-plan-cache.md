---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. This is a minimal cache service configuration with no custom instances, templates, or complex configuration - just a basic Redis installation for caching functionality.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default Redis configuration (/etc/redis/redis.conf)
  - Port/Socket: Default Redis port 6379
  - Key Config: Standard Redis server installation with default settings

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
[None - no custom templates deployed]
```

**Attributes:**
```
[None - no custom attributes defined]
```

**Files:**
```
[None - no static files deployed]
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts redis-server service with default configuration
   - Step 3: No files/templates deployed - uses system defaults
   - Iterations: Single Redis instance with default configuration (no loops)

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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. The cookbook uses default Redis configuration without authentication or custom security settings.

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf (default Redis configuration)
- /var/lib/redis/ (Redis data directory)
- /var/log/redis/redis-server.log (Redis log file)

**Service endpoints to check**:
- Port 6379 (default Redis port)
- Unix socket: /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: 0 templates (uses system default Redis configuration files)

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

# Basic cache operations test for redis-server instance
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli del test_key

# Configuration validation for redis-server instance
cat /etc/redis/redis.conf | grep -E 'port|bind|maxmemory'
redis-cli config get port
redis-cli config get bind
redis-cli config get maxmemory

# Service performance for redis-server instance
redis-cli info stats | grep -E 'total_commands_processed|instantaneous_ops_per_sec'
redis-cli info memory | grep -E 'used_memory_human|maxmemory_human'

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -10

# Network listening for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory for redis-server instance
ls -lah /var/lib/redis/
df -h /var/lib/redis/
redis-cli dbsize

# Process and memory usage for redis-server instance
ps aux | grep redis-server
top -p $(pgrep redis-server) -n 1
cat /proc/$(pgrep redis-server)/status | grep -E 'VmRSS|VmSize'
```