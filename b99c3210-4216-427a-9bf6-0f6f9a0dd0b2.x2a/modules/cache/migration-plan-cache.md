---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts a single Redis instance using default configuration. This is a minimal cache service with no custom configuration, templates, or multiple instances.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default Redis installation paths (/etc/redis/, /var/lib/redis/)
  - Port/Socket: Default Redis port 6379
  - Key Config: Uses system default Redis configuration

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts redis-server service with default configuration
   - Step 3: No files/templates deployed - uses distribution defaults
   - Iterations: Single Redis instance with default settings (no loops)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: redis-server
**Service dependencies**: redis-server systemd service

## Credentials

**Detection Summary**: 0 credentials detected across 1 file

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. The cookbook uses default Redis configuration without authentication.

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf
- /var/lib/redis/
- /var/log/redis/redis-server.log

**Service endpoints to check**: 
- 6379 (default Redis port)
- /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: None

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

# Network connectivity for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f

# Data directory for redis-server instance
ls -lah /var/lib/redis/
df -h /var/lib/redis/

# Memory usage for redis-server instance
redis-cli info memory | grep used_memory_human
ps aux | grep redis-server | awk '{print $6}'

# Performance check for redis-server instance
redis-cli --latency -i 1
redis-cli info stats | grep -E 'total_commands_processed|instantaneous_ops_per_sec'
```