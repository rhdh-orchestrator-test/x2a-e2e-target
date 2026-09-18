---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server installation cookbook that installs the redis-server package and ensures the service is enabled and started. This is a minimal cache implementation with default Redis configuration.

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
   - Step 3: Resources used - package (1), service (1)
   - Iterations: No iterations - single Redis instance with default settings

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)
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
- /etc/redis/redis.conf (default Redis configuration)
- /var/lib/redis/ (Redis data directory)
- /var/log/redis/redis-server.log (Redis log file)
- cookbooks/cache/recipes/default.rb

**Service endpoints to check**:
- Port 6379 (default Redis port)
- Unix socket /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: 0 templates (uses system default Redis configuration)

## Pre-flight checks:
```bash
# Service status for redis-server instance
systemctl status redis-server
ps aux | grep redis-server

# Redis connectivity and functionality for redis-server instance
redis-cli ping  # should return PONG
redis-cli info server | grep redis_version
redis-cli info memory | grep used_memory_human

# Basic Redis operations test for redis-server instance
redis-cli set test_key "test_value"
redis-cli get test_key  # should return "test_value"
redis-cli del test_key
redis-cli get test_key  # should return (nil)

# Configuration validation for redis-server instance
cat /etc/redis/redis.conf | grep -E 'port|bind|dir|logfile'
redis-cli config get port  # should return 6379
redis-cli config get bind  # should show bind addresses

# Service performance for redis-server instance
redis-cli info stats | grep -E 'total_connections_received|total_commands_processed'
redis-cli info clients | grep connected_clients

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -10

# Network listening for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory and permissions for redis-server instance
ls -lah /var/lib/redis/
df -h /var/lib/redis/
ps aux | grep redis | grep -v grep | awk '{print $1}'  # should show redis user

# Memory usage for redis-server instance
redis-cli info memory | grep -E 'used_memory|maxmemory'
cat /proc/$(pgrep redis-server)/status | grep VmRSS
```