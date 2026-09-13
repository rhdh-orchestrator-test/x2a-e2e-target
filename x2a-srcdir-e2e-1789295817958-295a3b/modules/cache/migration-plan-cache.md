---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts a single Redis instance with default configuration. No custom configuration, templates, or multiple instances - just basic package installation and service management.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Single Redis cache instance with default configuration
  - Location/Path: Default Redis installation paths (/etc/redis/, /var/lib/redis/)
  - Port/Socket: Default Redis port 6379
  - Key Config: Default Redis configuration (no custom settings applied)

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts redis-server service with default configuration
   - Step 3: No files or templates deployed
   - Iterations: None - single Redis instance with default settings

## Dependencies

**External cookbook dependencies**: None
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
- Port 6379 (default Redis port)
- Unix socket /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: None

## Pre-flight checks:
```bash
# Service status for redis-server
systemctl status redis-server
ps aux | grep redis-server

# Redis connectivity and functionality for redis-server
redis-cli ping
redis-cli info server
redis-cli info memory
redis-cli info clients

# Basic Redis operations test for redis-server
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli del test_key

# Configuration validation for redis-server
cat /etc/redis/redis.conf | grep -E 'port|bind|dir|logfile'
redis-cli config get port
redis-cli config get bind
redis-cli config get dir

# Network listening for redis-server
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory and permissions for redis-server
ls -lah /var/lib/redis/
ls -lah /var/run/redis/
df -h /var/lib/redis/

# Memory usage for redis-server
redis-cli info memory | grep used_memory_human
ps aux | grep redis-server | awk '{print $6}'

# Logs for redis-server
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -20
```