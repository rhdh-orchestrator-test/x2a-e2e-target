---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: Simple Redis cache server cookbook that installs redis-server package and ensures the service is enabled and running. Single instance with default configuration, no custom settings or iterations.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:
- **redis-server**: Default Redis cache instance
  - Location/Path: Default system paths (/etc/redis/, /var/lib/redis/)
  - Port/Socket: Default Redis port 6379
  - Key Config: Default Redis configuration, no custom settings applied

## File Structure

```
recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs Redis server package: redis-server
   - Enables and starts redis-server service
   - Resources: package (1), service (1)
   - No iterations: Single Redis instance with default configuration
   - No custom configuration: Uses system default Redis settings

## Dependencies

**External cookbook dependencies**: None (no dependencies in metadata.rb)
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

**Service endpoints to check**:
- Ports listening: 6379 (default Redis port)
- Unix sockets: /var/run/redis/redis-server.sock (if configured)
- Network interfaces: localhost (default binding)

**Templates rendered**:
No templates are rendered by this cookbook.

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

# Service functionality
redis-cli info stats
redis-cli info replication
redis-cli lastsave

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -10

# Network listening
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Data directory and permissions
ls -lah /var/lib/redis/
ls -lah /etc/redis/
ps aux | grep redis | grep -v grep
id redis

# Memory usage
redis-cli info memory | grep used_memory_human
free -h
cat /proc/$(pgrep redis-server)/status | grep VmRSS

# Performance check
redis-cli --latency -h localhost -p 6379
redis-cli eval "return redis.call('ping')" 0
```