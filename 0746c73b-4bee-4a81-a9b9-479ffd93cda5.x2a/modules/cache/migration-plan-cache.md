---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This is a simple cache service cookbook that installs and configures Redis as a local caching server. It installs the `redis-server` package and ensures the Redis service is enabled and started on boot. This is a basic single-instance Redis deployment with default configuration, designed as a local dependency for testing purposes.

## Service Type and Instances

**Service Type**: Cache (In-Memory Data Store)

**Configured Instances**:

This cookbook configures a single Redis instance with default settings:

- **redis-server**: Default Redis instance
  - Location/Path: Default system paths (typically /var/lib/redis for data, /etc/redis/redis.conf for config)
  - Port/Socket: Default port 6379 (TCP)
  - Key Config: Uses system default Redis configuration, no custom settings applied

## File Structure

```
recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs Redis server package: redis-server
   - Enables Redis service to start on boot
   - Starts Redis service immediately
   - Resources used: package (1), service (1)
   - Files/templates deployed: None - uses distribution default configuration
   - Iterations: No iterations present - single instance deployment

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)

**System package dependencies**: 
- redis-server (primary package installed)

**Service dependencies**: 
- redis-server (systemd/init.d service managed)

## Credentials

**Detection Summary**: 0 credentials detected across 1 file

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. The Redis instance uses default configuration without authentication. In production environments, you should configure Redis with requirepass authentication and bind to specific interfaces.

**Security Note for Migration**: The default Redis configuration may allow unauthenticated access on localhost. Consider configuring:
- `requirepass` for password authentication
- `bind` directive to limit network interfaces
- `protected-mode` settings
- Firewall rules to restrict access

## Checks for the Migration

**Files to verify**:
- Configuration: /etc/redis/redis.conf (system default)
- Data directory: /var/lib/redis/
- Log file: /var/log/redis/redis-server.log
- PID file: /var/run/redis/redis-server.pid
- Socket: /var/run/redis/redis-server.sock (if unix socket enabled)

**Service endpoints to check**:
- Ports listening: TCP 6379 (default Redis port)
- Unix sockets: /var/run/redis/redis-server.sock (distribution dependent)
- Network interfaces: Typically binds to 127.0.0.1 (localhost) by default

**Templates rendered**:
None - this cookbook uses system default configuration files without customization.

## Pre-flight checks:

```bash
# Service status for redis-server instance
systemctl status redis-server
systemctl is-enabled redis-server
ps aux | grep redis-server

# Redis connectivity and health for redis-server instance
redis-cli ping
redis-cli INFO server
redis-cli INFO memory
redis-cli INFO stats

# Configuration validation
cat /etc/redis/redis.conf | grep -v "^#" | grep -v "^$"
redis-cli CONFIG GET "*"
redis-cli CONFIG GET bind
redis-cli CONFIG GET port
redis-cli CONFIG GET requirepass

# Basic functionality test
redis-cli SET test_key "test_value"
redis-cli GET test_key
redis-cli DEL test_key

# Performance test
redis-cli --intrinsic-latency 100
redis-cli --latency-history

# Logs
tail -f /var/log/redis/redis-server.log
journalctl -u redis-server -f
grep -i error /var/log/redis/redis-server.log | tail -20

# Network listening on port 6379
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379
lsof -U | grep redis

# Process and resource usage
ps aux | grep redis-server
top -p $(pgrep redis-server) -n 1
cat /proc/$(pgrep redis-server)/status | grep -E 'VmRSS|VmSize'

# Data directory
ls -lah /var/lib/redis/
df -h /var/lib/redis/

# Persistence check (if RDB/AOF enabled)
redis-cli LASTSAVE
redis-cli INFO persistence
ls -lh /var/lib/redis/dump.rdb

# Memory statistics
redis-cli MEMORY STATS
redis-cli MEMORY DOCTOR

# Client connections
redis-cli CLIENT LIST
redis-cli INFO clients

# Verify package installation
dpkg -l | grep redis-server
rpm -qa | grep redis
redis-server --version
```