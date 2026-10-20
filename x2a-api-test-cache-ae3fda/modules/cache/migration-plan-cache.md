---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two caching services: memcached and Redis. It deploys a single Redis instance on port 6379 with password authentication (`redis_secure_password_123`) and includes a workaround to remove certain replica-related configuration directives from the generated Redis config file. The memcached service is configured via an external dependency cookbook without custom attributes.

## Service Type and Instances

**Service Type**: Cache (Multiple cache engines: Memcached and Redis)

**Configured Instances**:

- **memcached**: Memory object caching system
  - Configuration: Default configuration from memcached cookbook
  - Port/Socket: Port 11211 (default memcached port)
  - Key Config: No custom attributes set, uses memcached cookbook defaults

- **redis (port 6379)**: In-memory data structure store
  - Location/Path: Configuration at /etc/redis/6379.conf, logs at /var/log/redis
  - Port/Socket: Port 6379
  - Key Config: 
    - Authentication enabled with password: `redis_secure_password_123`
    - Custom config cleanup: Removes replica-serve-stale-data, replica-read-only, repl-ping-replica-period, client-output-buffer-limit, and replica-priority directives
    - Service user: redis
    - Service group: redis

## File Structure

**MANDATORY: List of files actually used in this cookbook:**

**Recipes:**
```
cookbooks/cache/recipes/default.rb
```

**Providers:**
```
(None - uses external cookbook resources only)
```

**Templates:**
```
(None - this cookbook has no templates; templates are provided by dependency cookbooks memcached and redisio)
```

**Attributes:**
```
(None - attributes are set inline in the recipe)
```

**Files:**
```
(None)
```

## Module Explanation

The cookbook performs operations in this order:

**IMPORTANT: This cookbook orchestrates two caching services through dependency cookbooks.**

1. **default** (`cookbooks/cache/recipes/default.rb`):
   
   a. **Memcached Installation** (via `include_recipe 'memcached'`):
      - Installs and configures memcached service using external memcached cookbook (version ~> 6.0)
      - No custom attributes are set; uses memcached cookbook defaults
      - Resources: include_recipe (1)
   
   b. **Redis Attribute Configuration** (inline):
      - Sets node attributes for Redis server configuration:
        - `node.default['redisio']['servers']` array with 1 server configuration:
          - Port: 6379
          - Password authentication: `requirepass` = 'redis_secure_password_123'
          - Clears `replicaservestaledata` attribute (set to nil)
   
   c. **Redis Log Directory Creation**:
      - Creates directory: /var/log/redis
      - Owner: redis
      - Group: redis
      - Mode: 0755
      - Recursive creation enabled
      - Resources: directory (1)
   
   d. **Redis Installation** (via `include_recipe 'redisio'`):
      - Installs and configures Redis using external redisio cookbook
      - Uses the server attributes set earlier (port 6379 with password)
      - Resources: include_recipe (1)
   
   e. **Redis Configuration Cleanup** (ruby_block):
      - Name: fix_redis_config
      - Target file: /etc/redis/6379.conf
      - Purpose: Removes specific configuration lines that may conflict or are unwanted:
        - Removes lines starting with: `replica-serve-stale-data`
        - Removes lines starting with: `replica-read-only`
        - Removes lines starting with: `repl-ping-replica-period`
        - Removes lines starting with: `client-output-buffer-limit`
        - Removes lines starting with: `replica-priority`
      - This is a post-processing workaround (marked as "HACK" in source)
      - Resources: ruby_block (1)
   
   f. **Redis Service Enablement** (via `include_recipe 'redisio::enable'`):
      - Enables and starts the Redis service
      - Resources: include_recipe (1)

**Total Resources**: include_recipe (3), directory (1), ruby_block (1)

## Dependencies

**External cookbook dependencies**: 
- memcached (version ~> 6.0) - Installs and configures memcached
- redisio - Installs and configures Redis server

**System package dependencies**: 
- memcached - Memory object caching daemon
- redis-server - Redis in-memory data store (installed via redisio cookbook)

**Service dependencies**: 
- memcached.service (or memcached via init)
- redis6379.service (or redis_6379 via init - naming depends on redisio cookbook implementation)

## Credentials

**Detection Summary**: 1 credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Redis Authentication Password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: cookbooks/cache/recipes/default.rb (line 7)
- **Current storage**: Hardcoded string in recipe
- **Usage context**: Redis server authentication password. All clients connecting to Redis on port 6379 must authenticate using this password via the AUTH command. The hardcoded value is `redis_secure_password_123`.

**Security Note**: This password should be externalized to a secrets management system (HashiCorp Vault, Ansible Vault, AAP Credentials, etc.) in the Ansible migration. The password is currently visible in plain text in the recipe file.

## Checks for the Migration

**Files to verify**:
- `/etc/redis/6379.conf` - Redis configuration file (should exist and contain requirepass directive, should NOT contain removed replica directives)
- `/var/log/redis/` - Redis log directory (owner: redis, group: redis, mode: 0755)
- `/etc/memcached.conf` - Memcached configuration file (location may vary by distribution)
- `/var/run/redis/redis_6379.pid` - Redis PID file (if running)
- `/var/lib/redis/6379/` - Redis data directory (typical location)

**Service endpoints to check**:
- **Memcached**:
  - Port listening: 11211 (default)
  - Network interface: localhost or 0.0.0.0 (depends on memcached cookbook defaults)
- **Redis**:
  - Port listening: 6379
  - Network interface: localhost or 0.0.0.0 (depends on redisio cookbook defaults)
  - Unix socket: May also listen on /var/run/redis/redis_6379.sock (depends on redisio configuration)

**Templates rendered**:
- No templates in this cookbook directly; templates rendered by dependency cookbooks:
  - memcached cookbook: Likely renders /etc/memcached.conf or equivalent
  - redisio cookbook: Renders /etc/redis/6379.conf (1 time for the single Redis instance)

## Pre-flight checks

```bash
# ============================================================================
# MEMCACHED SERVICE CHECKS
# ============================================================================

# Service status
systemctl status memcached
ps aux | grep memcached | grep -v grep

# Port listening check
netstat -tulpn | grep 11211
ss -tlnp | grep memcached
lsof -i :11211

# Memcached connectivity and version
echo "version" | nc localhost 11211
printf "stats\r\n" | nc localhost 11211 | head -20

# Memory stats
echo "stats" | nc localhost 11211 | grep -E 'bytes|curr_items|get_hits|get_misses'

# Configuration file
cat /etc/memcached.conf
# Or on some systems:
cat /etc/sysconfig/memcached

# Logs
journalctl -u memcached -n 50 --no-pager
tail -f /var/log/memcached.log  # if file-based logging

# ============================================================================
# REDIS SERVICE CHECKS - Instance on port 6379
# ============================================================================

# Service status
systemctl status redis6379
# Or depending on service naming:
systemctl status redis_6379
systemctl status redis@6379
ps aux | grep redis-server | grep 6379

# Port listening check
netstat -tulpn | grep 6379
ss -tlnp | grep redis
lsof -i :6379

# Redis connectivity with authentication
redis-cli -p 6379 PING
# Expected: (error) NOAUTH Authentication required.

redis-cli -p 6379 -a redis_secure_password_123 PING
# Expected: PONG

redis-cli -p 6379 -a redis_secure_password_123 INFO server
redis-cli -p 6379 -a redis_secure_password_123 INFO replication

# Verify Redis version and configuration
redis-cli -p 6379 -a redis_secure_password_123 CONFIG GET requirepass
# Expected: 1) "requirepass" 2) "redis_secure_password_123"

redis-cli -p 6379 -a redis_secure_password_123 CONFIG GET port
# Expected: 1) "port" 2) "6379"

# Configuration file validation
cat /etc/redis/6379.conf

# Verify password is set
grep "^requirepass" /etc/redis/6379.conf
# Expected: requirepass redis_secure_password_123

# Verify removed directives are NOT present (the ruby_block cleanup)
grep "^replica-serve-stale-data" /etc/redis/6379.conf
# Expected: (no output - should be removed)

grep "^replica-read-only" /etc/redis/6379.conf
# Expected: (no output - should be removed)

grep "^repl-ping-replica-period" /etc/redis/6379.conf
# Expected: (no output - should be removed)

grep "^client-output-buffer-limit" /etc/redis/6379.conf
# Expected: (no output - should be removed)

grep "^replica-priority" /etc/redis/6379.conf
# Expected: (no output - should be removed)

# Log directory permissions
ls -ld /var/log/redis
# Expected: drwxr-xr-x ... redis redis ... /var/log/redis

stat /var/log/redis | grep -E 'Access: \(0755'
# Expected: Access: (0755/drwxr-xr-x)

# Data directory check
ls -la /var/lib/redis/6379/

# Redis logs
tail -f /var/log/redis/redis_6379.log
# Or:
tail -f /var/log/redis/6379.log
journalctl -u redis6379 -f

# Check for errors in logs
grep -i error /var/log/redis/*.log | tail -20

# Memory usage
redis-cli -p 6379 -a redis_secure_password_123 INFO memory | grep used_memory_human

# Redis persistence check (RDB/AOF)
redis-cli -p 6379 -a redis_secure_password_123 CONFIG GET save
redis-cli -p 6379 -a redis_secure_password_123 CONFIG GET appendonly

# ============================================================================
# COMBINED CHECKS
# ============================================================================

# All cache services running
systemctl status memcached redis6379
ps aux | grep -E 'memcached|redis-server' | grep -v grep

# All ports listening
netstat -tulpn | grep -E '11211|6379'
ss -tlnp | grep -E 'memcached|redis'

# Process counts
echo "Memcached processes: $(ps aux | grep memcached | grep -v grep | wc -l)"  # should show 1
echo "Redis processes: $(ps aux | grep redis-server | grep 6379 | wc -l)"  # should show 1

# Test basic caching operations
# Memcached set/get test
printf "set test_key 0 60 5\r\nvalue\r\n" | nc localhost 11211
printf "get test_key\r\n" | nc localhost 11211

# Redis set/get test
redis-cli -p 6379 -a redis_secure_password_123 SET test_key "test_value"
# Expected: OK
redis-cli -p 6379 -a redis_secure_password_123 GET test_key
# Expected: "test_value"
redis-cli -p 6379 -a redis_secure_password_123 DEL test_key
# Expected: (integer) 1
```