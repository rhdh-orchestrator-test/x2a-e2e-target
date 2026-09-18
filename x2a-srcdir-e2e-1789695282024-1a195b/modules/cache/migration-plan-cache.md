---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server installation cookbook that installs the redis-server package and ensures the service is enabled and running. This is a minimal cache service setup with no custom configuration or multiple instances.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Single Redis cache instance
  - Location/Path: Default Redis installation paths (/etc/redis/, /var/lib/redis/)
  - Port/Socket: Default Redis port 6379
  - Key Config: Default Redis configuration (no custom settings applied)

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```
recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

**IMPORTANT: Use FULL paths from the File Structure section (e.g., `cookbooks/myapp/recipes/default.rb` not just `recipes/default.rb`)**

1. **default** (`recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts the redis-server service
   - Step 3: No files/templates deployed
   - Iterations: Single Redis instance configuration (no loops)

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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**: 
- /etc/redis/redis.conf
- /var/lib/redis/
- /var/log/redis/redis-server.log

**Service endpoints to check**: 
- Port 6379 (Redis default port)
- Unix socket /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: None

## Pre-flight checks:
```bash
# Service status for redis-server instance
systemctl status redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server
ps aux | grep redis-server

# Redis connectivity and functionality for redis-server instance
redis-cli ping
redis-cli info server | grep redis_version
redis-cli info memory | grep used_memory_human

# Configuration validation for redis-server instance
cat /etc/redis/redis.conf | grep -E 'port|bind|dir|logfile'
redis-cli config get port
redis-cli config get bind

# Network connectivity for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory and permissions for redis-server instance
ls -lah /var/lib/redis/
ls -lah /var/run/redis/
df -h /var/lib/redis/

# Basic functionality test for redis-server instance
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli del test_key

# Log verification for redis-server instance
tail -10 /var/log/redis/redis-server.log
journalctl -u redis-server --no-pager -n 10
```