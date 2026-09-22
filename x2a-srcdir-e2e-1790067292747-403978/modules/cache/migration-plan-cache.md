---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. Single instance configuration with default Redis settings on port 6379.

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
   - Step 3: Resources used - package (1), service (1)
   - Iterations: No iterations - single Redis instance with default configuration

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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf (default)
- /var/lib/redis
- /var/log/redis/redis-server.log
- /var/run/redis/redis-server.pid

**Service endpoints to check**: 6379 (Redis default port)
**Templates rendered**: No templates are rendered by this cookbook

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis-server
systemctl is-enabled redis-server
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

# Service performance
redis-cli info stats
redis-cli info replication
redis-cli client list

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -20

# Data directory and permissions
ls -lah /var/lib/redis/
df -h /var/lib/redis/
ps aux | grep redis | awk '{print $1}' | head -1 | xargs id

# Memory usage
redis-cli info memory | grep used_memory_human
ps aux | grep redis-server | awk '{print $6}' | head -1
cat /proc/$(pgrep redis-server)/status | grep VmRSS
```