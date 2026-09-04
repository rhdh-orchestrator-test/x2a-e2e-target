---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts redis-server service. Single instance configuration with default Redis settings on port 6379.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: /var/lib/redis (default data directory)
  - Port/Socket: 6379 (default Redis port)
  - Key Config: Default Redis configuration, no custom settings applied

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts redis-server service
   - Step 3: No files/templates deployed - uses system defaults
   - Iterations: No iterations - single Redis instance with default configuration

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: redis-server
**Service dependencies**: redis-server (systemd service)

## Credentials

**Detection Summary**: 0 credentials detected across 1 files

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
- Port 6379 (Redis default port)
- Unix socket: /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: None

## Pre-flight checks:
```bash
# Service status
systemctl status redis-server
ps aux | grep redis-server

# Redis connectivity and functionality
redis-cli ping
redis-cli info server
redis-cli info memory
redis-cli info clients

# Basic Redis operations test
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli del test_key

# Configuration validation
cat /etc/redis/redis.conf | grep -E 'port|bind|dir|logfile'
redis-cli config get port
redis-cli config get bind
redis-cli config get dir

# Service listening
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f

# Data directory
ls -lah /var/lib/redis/
df -h /var/lib/redis/

# Memory usage
redis-cli info memory | grep used_memory_human
ps aux | grep redis-server | awk '{print $6}'

# Performance check
redis-cli --latency -i 1
redis-cli info stats | grep -E 'total_commands_processed|instantaneous_ops_per_sec'
```