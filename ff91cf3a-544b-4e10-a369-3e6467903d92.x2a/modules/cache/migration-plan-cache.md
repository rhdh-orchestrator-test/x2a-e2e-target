---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This is a minimal cache cookbook that installs and configures Redis server as a simple caching service. It installs the redis-server package and ensures the service is enabled and started. This is a local dependency cookbook used for testing purposes with a single Redis instance on default configuration.

## Service Type and Instances

**Service Type**: Cache (Redis in-memory data store)

**Configured Instances**:

- **redis-server**: Single Redis instance using distribution default configuration
  - Location/Path: System service managed by systemd/init
  - Port/Socket: Port 6379, Unix socket at /var/run/redis/redis-server.sock (if configured)
  - Key Config: Uses distribution default configuration without custom templates

## File Structure

```
recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Step 1: Installs redis-server package from distribution repositories
   - Step 2: Enables and starts the redis-server service using system init/systemd
   - Step 3: No custom configuration templates or files deployed (relies on distribution defaults)
   - Resources: package (1), service (1)
   - Iterations: None - single instance with no loops

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)

**System package dependencies**: redis-server

**Service dependencies**: redis-server (systemd/init service)

## Credentials

**Detection Summary**: 0 credentials detected across 1 file

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. The Redis instance uses default configuration without authentication. In production environments, Redis should be configured with requirepass authentication, but this cookbook does not implement any security configuration.

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf (distribution default, not managed by cookbook)
- /var/lib/redis/ (default Redis data persistence location)
- /var/log/redis/redis-server.log
- /var/run/redis/redis-server.pid
- /var/run/redis/redis-server.sock (if Unix socket enabled)

**Service endpoints to check**:
- Port 6379 (default Redis port)
- Unix socket /var/run/redis/redis-server.sock (if enabled)
- Network interface 127.0.0.1 (typically localhost binding)

**Templates rendered**: None

## Pre-flight checks:

```bash
# Service status for redis-server instance
systemctl status redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server
ps aux | grep redis-server

# Redis connectivity and health for redis-server instance
redis-cli ping
redis-cli info server
redis-cli info stats
redis-cli info replication
redis-cli info memory

# Configuration validation for redis-server instance
cat /etc/redis/redis.conf | grep -E '^[^#]' | grep -v '^$'
redis-cli CONFIG GET port
redis-cli CONFIG GET bind
redis-cli CONFIG GET requirepass
redis-cli CONFIG GET maxmemory
redis-cli CONFIG GET maxmemory-policy

# Basic functionality test for redis-server instance
redis-cli SET test_key "test_value"
redis-cli GET test_key
redis-cli DEL test_key
redis-cli DBSIZE

# Performance check for redis-server instance
redis-cli --intrinsic-latency 10
redis-cli --latency -h 127.0.0.1 -p 6379

# Logs for redis-server instance
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
journalctl -u redis-server --no-pager -n 100

# Network listening for redis-server instance
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379
lsof -U | grep redis

# Process and resource verification for redis-server instance
pgrep redis-server
cat /var/run/redis/redis-server.pid
ps -p $(cat /var/run/redis/redis-server.pid) -o pid,ppid,cmd,etime,%cpu,%mem,rss

# Data directory for redis-server instance
ls -lah /var/lib/redis/
df -h /var/lib/redis/
du -sh /var/lib/redis/*

# Memory usage for redis-server instance
redis-cli INFO memory | grep used_memory_human
free -h
cat /proc/$(pgrep redis-server)/status | grep -E 'VmRSS|VmSize'

# Connection count for redis-server instance
redis-cli CLIENT LIST | wc -l
redis-cli INFO clients

# Verify Redis persistence for redis-server instance
redis-cli BGSAVE
redis-cli LASTSAVE
ls -lh /var/lib/redis/dump.rdb

# Security check for redis-server instance
redis-cli AUTH test_password 2>&1 | grep "ERR Client sent AUTH"
redis-cli INFO server | grep tcp_port
```