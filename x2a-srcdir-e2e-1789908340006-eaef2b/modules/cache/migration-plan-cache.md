---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs and starts the redis-server package. This is a minimal cache implementation with default Redis configuration, providing a basic in-memory data store service on the standard Redis port 6379.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: /var/lib/redis (default Redis data directory)
  - Port/Socket: 6379 (default Redis port)
  - Key Config: Default Redis configuration from package installation

## File Structure

```
cookbooks/cache/recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs Redis server package (redis-server)
   - Step 2: Enables and starts redis-server service with systemd
   - Step 3: Uses default Redis configuration from package installation
   - Resources used: package (1), service (1)
   - Iterations: None - single Redis instance with default configuration

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

No credentials or secrets were detected in this cookbook. All configuration values use Redis defaults with no authentication configured.

## Checks for the Migration

**Files to verify**:
- cookbooks/cache/recipes/default.rb
- /etc/redis/redis.conf (default Redis configuration)
- /var/lib/redis/ (Redis data directory)
- /var/log/redis/redis-server.log (Redis log file)

**Service endpoints to check**:
- 6379 (Redis default port)
- /var/run/redis/redis-server.sock (if configured)

**Templates rendered**: None - uses package default configuration

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

# Service performance for redis-server instance
redis-cli info stats | grep -E 'total_connections_received|total_commands_processed|keyspace_hits|keyspace_misses'
redis-cli info memory | grep -E 'used_memory_human|used_memory_peak_human'

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -10

# Network listening for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory for redis-server instance
ls -lah /var/lib/redis/
df -h /var/lib/redis/
du -sh /var/lib/redis/*

# Process resources for redis-server instance
ps aux | grep redis-server
top -p $(pgrep redis-server) -n 1
cat /proc/$(pgrep redis-server)/status | grep -E 'VmRSS|VmSize'
```