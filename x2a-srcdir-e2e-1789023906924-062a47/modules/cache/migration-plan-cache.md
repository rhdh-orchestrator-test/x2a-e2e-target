---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. This is a minimal cache service setup with no custom configuration, providing basic Redis functionality on the default port 6379.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default Redis installation paths (/etc/redis/, /var/lib/redis/)
  - Port/Socket: 6379 (default Redis port)
  - Key Config: Default Redis configuration (no custom settings applied)

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
   - Iterations: Single Redis instance with default configuration (no loops)

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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf
- /var/lib/redis/
- /var/log/redis/redis-server.log

**Service endpoints to check**:
- 6379 (Redis default port)
- /var/run/redis/redis-server.sock

**Templates rendered**: 0 templates rendered

## Pre-flight checks:
```bash
# Service status commands
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

# Network/connectivity checks
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data and log directories
ls -lah /var/lib/redis/
ls -lah /var/log/redis/
df -h /var/lib/redis/

# Memory usage and performance
redis-cli info memory | grep used_memory_human
redis-cli info stats | grep total_commands_processed
free -h

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
```