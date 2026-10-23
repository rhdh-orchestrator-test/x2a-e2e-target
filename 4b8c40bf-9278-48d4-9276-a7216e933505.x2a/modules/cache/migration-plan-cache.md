---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This is a minimal Redis cache server cookbook that installs the `redis-server` package and ensures the Redis service is enabled and running. It's a simple local dependency cookbook designed for testing purposes with no custom configuration, templates, or multiple instances - just a basic Redis installation with default settings.

## Service Type and Instances

**Service Type**: Cache (Redis in-memory data store)

**Configured Instances**:

This cookbook configures a **single Redis instance** using system package defaults:

- **redis-server (default instance)**:
  - Installation: Via system package manager (apt on Ubuntu, yum on CentOS)
  - Configuration: Uses distribution default configuration (typically `/etc/redis/redis.conf`)
  - Port: Default Redis port 6379 (from package default configuration)
  - Socket: May use Unix socket depending on distribution defaults
  - Service Management: Systemd service `redis-server` (Ubuntu) or `redis` (CentOS)
  - Data Directory: Distribution default (typically `/var/lib/redis`)
  - Log Location: Distribution default (typically `/var/log/redis`)
  - Key Config: All configuration comes from distribution package defaults - no custom settings applied

## File Structure

**Recipes:**
```
recipes/default.rb
```

**Providers:**
```
(None - no custom resources or providers used)
```

**Templates:**
```
(None - no templates deployed)
```

**Attributes:**
```
(None - no attribute files present)
```

**Files:**
```
(None - no static files deployed)
```

## Module Explanation

The cookbook performs a minimal Redis installation in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs the `redis-server` package from system repositories
     - Package: redis-server
     - Action: install
   - Enables and starts the Redis service
     - Service: redis-server
     - Actions: enable (on boot), start (immediate)
   - Resources: package (1), service (1)
   - No iterations: Single instance installation only
   - No templates: Uses distribution default configuration
   - No custom configuration: Relies entirely on package defaults

**Key Characteristics**:
- Extremely minimal implementation - only 2 Chef resources total
- No configuration management - accepts all distribution defaults
- No tuning or optimization applied
- Designed as a simple local dependency for testing environments
- Service name may vary by platform: `redis-server` on Ubuntu/Debian, `redis` on RHEL/CentOS

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)

**System package dependencies**: 
- `redis-server` (Ubuntu/Debian) or `redis` (RHEL/CentOS) - Redis in-memory cache server

**Service dependencies**: 
- `redis-server.service` (Ubuntu/Debian systemd unit)
- `redis.service` (RHEL/CentOS systemd unit)

## Credentials

**Detection Summary**: 0 credentials detected across 1 file

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. The cookbook uses the default Redis installation which typically ships with no authentication enabled (requirepass not set). This is appropriate for testing/development environments but should be secured for production use during Ansible migration.

**Security Note for Migration**: 
When migrating to Ansible, consider implementing Redis authentication via `requirepass` directive in redis.conf and managing the password through Ansible Vault or AAP credentials. The default installation leaves Redis open without authentication on localhost.

## Checks for the Migration

**Files to verify**:
- Configuration: `/etc/redis/redis.conf` (Ubuntu/Debian) or `/etc/redis.conf` (RHEL/CentOS)
- Data directory: `/var/lib/redis/` (typically contains dump.rdb if persistence enabled)
- Log file: `/var/log/redis/redis-server.log` (Ubuntu/Debian) or `/var/log/redis/redis.log` (RHEL/CentOS)
- PID file: `/var/run/redis/redis-server.pid` (location varies by distribution)
- Unix socket: `/var/run/redis/redis-server.sock` (if enabled in default config)

**Service endpoints to check**:
- Port listening: TCP 6379 (default Redis port)
- Unix socket: May be `/var/run/redis/redis-server.sock` or `/tmp/redis.sock` depending on distribution defaults
- Network interface: Typically binds to 127.0.0.1 (localhost only) in default configuration

**Templates rendered**:
- **None**: This cookbook does not deploy any templates. All configuration comes from the `redis-server` package defaults.

## Pre-flight checks:

```bash
# Service status - check systemd service for redis-server default instance
systemctl status redis-server  # Ubuntu/Debian
systemctl status redis         # RHEL/CentOS
systemctl is-enabled redis-server  # Verify enabled on boot
systemctl is-active redis-server   # Verify currently running

# Process verification for redis-server default instance
ps aux | grep redis-server
pgrep -a redis

# Redis connectivity and health for redis-server default instance
redis-cli ping  # Should return "PONG"
redis-cli info server | grep redis_version
redis-cli info stats | grep total_connections_received
redis-cli info memory | grep used_memory_human

# Basic functionality test for redis-server default instance
redis-cli SET test_key "test_value"
redis-cli GET test_key  # Should return "test_value"
redis-cli DEL test_key
redis-cli DBSIZE  # Show number of keys

# Configuration file location and content
# Ubuntu/Debian
cat /etc/redis/redis.conf | grep -E '^port|^bind|^requirepass|^dir|^logfile'
test -f /etc/redis/redis.conf && echo "Config file exists"

# RHEL/CentOS
cat /etc/redis.conf | grep -E '^port|^bind|^requirepass|^dir|^logfile'
test -f /etc/redis.conf && echo "Config file exists"

# Network listening verification for redis-server default instance on port 6379
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379
lsof -U | grep redis  # Unix socket if configured

# Data and log directories for redis-server default instance
ls -lah /var/lib/redis/
ls -lah /var/log/redis/
df -h /var/lib/redis  # Check disk space for data

# Check Redis is responding on expected interface for redis-server default instance
redis-cli -h 127.0.0.1 -p 6379 ping  # Localhost
timeout 2 redis-cli -h 0.0.0.0 -p 6379 ping 2>/dev/null || echo "Not listening on all interfaces (expected for default config)"

# Persistence verification for redis-server default instance (if RDB enabled in defaults)
redis-cli LASTSAVE  # Unix timestamp of last successful save
ls -lh /var/lib/redis/dump.rdb  # RDB snapshot file if persistence enabled

# Performance and resource checks for redis-server default instance
redis-cli info stats | grep -E 'instantaneous_ops_per_sec|keyspace_hits|keyspace_misses'
redis-cli info clients | grep connected_clients
redis-cli --latency  # Check latency (Ctrl+C to stop)

# Memory usage for redis-server default instance
redis-cli info memory | grep -E 'used_memory_human|used_memory_peak_human|maxmemory'
ps aux | grep redis-server | grep -v grep | awk '{print $6}'  # RSS memory in KB

# Logs verification for redis-server default instance
# Ubuntu/Debian
tail -50 /var/log/redis/redis-server.log
journalctl -u redis-server -n 50 --no-pager

# RHEL/CentOS  
tail -50 /var/log/redis/redis.log
journalctl -u redis -n 50 --no-pager

# Check for errors in logs
grep -i error /var/log/redis/*.log | tail -20

# Package verification
dpkg -l | grep redis  # Ubuntu/Debian
rpm -qa | grep redis  # RHEL/CentOS
redis-server --version

# Security check for redis-server default instance - verify authentication status
redis-cli CONFIG GET requirepass  # Should show if password is set (default: empty/no password)
redis-cli INFO | grep "# Server"  # Server info accessible without auth means no password

# Connection limits and configuration for redis-server default instance
redis-cli CONFIG GET maxclients
redis-cli CONFIG GET timeout
redis-cli CONFIG GET tcp-keepalive

# Verify service restarts properly for redis-server default instance
systemctl restart redis-server  # Ubuntu/Debian
sleep 2
redis-cli ping  # Should return "PONG" after restart
```

**Expected Results**:
- Service status: `active (running)` and `enabled`
- Redis ping: Returns `PONG`
- Port 6379: Listening on 127.0.0.1 (localhost)
- Process: Single `redis-server` process running as redis user
- Default config: No authentication (requirepass empty), persistence may vary by distribution
- Memory: Typically starts with ~2-5MB RSS memory for empty instance
- Logs: Should show successful startup with "Ready to accept connections" message

**Platform Differences to Note**:
- **Ubuntu/Debian**: Service name `redis-server`, config at `/etc/redis/redis.conf`
- **RHEL/CentOS**: Service name `redis`, config at `/etc/redis.conf`
- Package versions and default configurations may differ between distributions
- Socket locations and log paths vary by distribution