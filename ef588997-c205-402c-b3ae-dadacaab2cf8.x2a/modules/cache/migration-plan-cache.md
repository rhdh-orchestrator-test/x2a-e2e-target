---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts redis-server package with default configuration. Single instance setup with no custom configuration or iterations.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default system paths (/etc/redis/, /var/lib/redis/)
  - Port/Socket: Default Redis port 6379
  - Key Config: Default Redis configuration (no custom settings)

## File Structure

```
recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts redis-server service with default configuration
   - Step 3: No files or templates deployed
   - Iterations: No iterations - single Redis instance with default settings

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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf
- /var/lib/redis/
- /var/log/redis/redis-server.log

**Service endpoints to check**: 6379 (Redis port)
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

# Service logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
journalctl -u redis-server --no-pager -n 50

# Network listening
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory and permissions
ls -lah /var/lib/redis/
ls -lah /var/log/redis/
ps aux | grep redis | grep -v grep

# Memory usage
redis-cli info memory | grep used_memory_human
free -h
cat /proc/meminfo | grep MemAvailable

# Performance check
redis-cli --latency -i 1
redis-cli info stats | grep -E 'total_commands_processed|total_connections_received'
```