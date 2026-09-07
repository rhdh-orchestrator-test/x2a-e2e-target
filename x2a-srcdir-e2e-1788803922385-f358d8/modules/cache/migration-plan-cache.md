---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. This is a minimal cache implementation with default Redis configuration, providing a basic in-memory data store service.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis instance
  - Location/Path: Default Redis configuration (/etc/redis/redis.conf)
  - Port/Socket: 6379 (Redis default port)
  - Key Config: Default Redis settings, no custom configuration applied

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts redis-server service with systemd
   - Step 3: No files/templates deployed - uses default configuration
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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. The cookbook uses default Redis configuration without authentication.

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf (default Redis configuration)
- /var/lib/redis/ (Redis data directory)
- /var/log/redis/redis-server.log (Redis log file)

**Service endpoints to check**:
- Ports listening: 6379 (Redis default port)
- Unix sockets: /var/run/redis/redis-server.sock (if enabled in config)
- Network interfaces: 127.0.0.1 (Redis default bind address)

**Templates rendered**: No templates are rendered by this cookbook

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
cat /etc/redis/redis.conf | grep -E 'port|bind|maxmemory'
redis-cli config get port
redis-cli config get bind
redis-cli config get maxmemory

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
ls -lah /var/run/redis/
df -h /var/lib/redis/

# Memory usage for redis-server instance
redis-cli info memory | grep used_memory_human
ps aux | grep redis-server | awk '{print $6}'

# Performance check for redis-server instance
redis-cli --latency -i 1
redis-cli info stats | grep -E 'total_commands_processed|instantaneous_ops_per_sec'
```