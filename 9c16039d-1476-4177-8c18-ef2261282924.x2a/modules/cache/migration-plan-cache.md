---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. This is a minimal cache implementation with default Redis configuration, providing a basic in-memory data store service on the standard Redis port 6379.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: /var/lib/redis
  - Port/Socket: 6379
  - Key Config: Default Redis configuration, no custom settings applied

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
**Service dependencies**: redis-server systemd service

## Credentials

**Detection Summary**: No credentials detected across 1 file

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values use Redis defaults with no authentication configured.

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /var/lib/redis (Redis data directory)
- /etc/redis/redis.conf (default configuration)
- /var/log/redis/redis-server.log
- /var/run/redis/redis-server.pid

**Service endpoints to check**: 6379 (Redis default port)
**Templates rendered**: None - uses default Redis configuration

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis-server
ps aux | grep redis-server

# Instance-specific checks for redis-server
redis-cli ping
redis-cli info server
redis-cli info memory
redis-cli info clients

# Configuration validation commands
cat /etc/redis/redis.conf | grep -E 'port|bind|dir|logfile'
redis-cli config get port
redis-cli config get bind
redis-cli config get dir

# Network/connectivity checks
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Basic Redis operations test
redis-cli set test_key "test_value"
redis-cli get test_key
redis-cli del test_key

# Service functionality
redis-cli info stats
redis-cli info replication
redis-cli client list

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -20

# Memory and performance
redis-cli info memory | grep used_memory_human
redis-cli info stats | grep total_commands_processed
top -p $(pgrep redis-server) -n 1

# Data persistence
ls -lah /var/lib/redis/
redis-cli lastsave
redis-cli info persistence

# Security check (default has no auth)
redis-cli auth "password" 2>&1 | grep "no password"
redis-cli config get requirepass
```