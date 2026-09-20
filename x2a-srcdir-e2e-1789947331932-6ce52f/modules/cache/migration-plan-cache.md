---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. This is a basic cache service with default configuration, no custom instances or complex setup.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default system paths (/etc/redis/, /var/lib/redis/)
  - Port/Socket: Default Redis port 6379
  - Key Config: Default Redis configuration (no custom settings)

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
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf (default Redis configuration)
- /var/lib/redis/ (Redis data directory)
- /var/log/redis/redis-server.log (Redis log file)

**Service endpoints to check**:
- 6379 (Redis default port)
- /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: 0 templates rendered (uses default Redis configuration)

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

# Service listening
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f

# Data directory and permissions
ls -lah /var/lib/redis/
df -h /var/lib/redis/
ps aux | grep redis | awk '{print $1}'

# Memory usage
redis-cli info memory | grep used_memory_human
free -h
cat /proc/meminfo | grep MemAvailable

# Performance check
redis-cli --latency -h 127.0.0.1 -p 6379
redis-cli eval "return redis.call('ping')" 0
```