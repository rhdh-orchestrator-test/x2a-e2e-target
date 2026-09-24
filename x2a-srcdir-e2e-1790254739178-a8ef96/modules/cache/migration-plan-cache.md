---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts redis-server package with default configuration. Single instance setup with no custom configuration or templates.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default system paths (/etc/redis/, /var/lib/redis/)
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
   - Step 3: Resources used - package (1), service (1)
   - Iterations: No iterations - single Redis instance with system defaults

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
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf
- /var/lib/redis/
- /var/log/redis/redis-server.log

**Service endpoints to check**: 
- Port 6379 (default Redis port)
- Unix socket /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: None - uses system default configuration

## Pre-flight checks:
```bash
# Service status for redis-server instance
systemctl status redis-server
ps aux | grep redis-server

# Redis connectivity and functionality for redis-server instance
redis-cli ping
redis-cli info server | grep redis_version
redis-cli config get bind
redis-cli config get port

# Basic Redis operations test for redis-server instance
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli del test_key
redis-cli dbsize

# Configuration validation for redis-server instance
cat /etc/redis/redis.conf | grep -E '^bind|^port|^dir|^logfile'
redis-cli config get "*" | grep -E 'bind|port|dir|logfile'

# Service auto-start verification for redis-server instance
systemctl is-enabled redis-server

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
redis-cli --latency -h 127.0.0.1 -p 6379
redis-cli info stats | grep -E 'total_commands_processed|instantaneous_ops_per_sec'

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -10
```