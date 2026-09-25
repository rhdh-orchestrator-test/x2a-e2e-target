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
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf
- /var/lib/redis/
- /var/log/redis/redis-server.log

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

# Service listening for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Memory and performance for redis-server instance
redis-cli info memory | grep used_memory_human
redis-cli info stats | grep total_commands_processed
free -h
ps aux | grep redis-server | awk '{print $6}'

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -10

# Data directory for redis-server instance
ls -lah /var/lib/redis/
df -h /var/lib/redis/
du -sh /var/lib/redis/*

# Redis persistence check for redis-server instance
redis-cli lastsave
redis-cli bgsave
redis-cli config get save
```