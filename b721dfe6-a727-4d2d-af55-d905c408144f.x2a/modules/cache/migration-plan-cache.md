---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook installs the `redis-server` package and enables and starts the `redis-server` service. It configures one local Redis instance using distribution package defaults, with no custom configuration files, templates, iterations, credentials, providers, or external cookbook dependencies. Redis uses the default TCP port `6379`.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: Local Redis cache service
  - Package: `redis-server`
  - Service: `redis-server`
  - Actions: Install the package; enable the service at boot; start the service immediately
  - Location/Path: Package-managed locations; commonly `/etc/redis/redis.conf` and `/var/lib/redis`
  - Port/Socket: TCP `6379`; no Unix socket configured or referenced
  - Key Config: Uses the operating system package's default Redis configuration. No custom configuration, authentication, bind address, or persistence settings are managed by the cookbook.

There are no collection attributes or `.each` iterations in the execution tree.

## File Structure

Only the recipe shown in the execution tree is included.

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

```text
None
```

**Templates:**

```text
None
```

**Attributes:**

```text
None
```

**Files:**

```text
None
```

`metadata.rb` was inspected for service identification and dependency information, but it is not listed here because the execution-tree file requirements permit only the `.rb` recipe files shown in the tree.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs the Redis server package:
     - Resource: `package[redis-server]`
     - Action: `:install`
     - Package name: `redis-server`
   - Enables and starts the Redis service:
     - Resource: `service[redis-server]`
     - Actions: `:enable`, `:start`
   - Resources: one `package` resource and one `service` resource
   - Iterations: None
   - Include recipes: None
   - Custom resources: None
   - Templates or static files: None
   - Restart or reload notifications: None

The equivalent implementation must preserve this order:

1. Install the `redis-server` package.
2. Enable the `redis-server` service.
3. Start the `redis-server` service.

The cookbook does not manage a Redis configuration file, so no configuration template should be added unless intentionally extending the Chef behavior.

## Dependencies

**External cookbook dependencies**: None declared in the inspected metadata.

**System package dependencies**:

- `redis-server`

**Service dependencies**:

- `redis-server`

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

Distribution-specific package and service naming may need to be handled if the target platform does not expose the exact `redis-server` package or service name. The Chef cookbook explicitly uses `redis-server` for both.

## Credentials

**Detection Summary**: No credentials detected across the analyzed cookbook files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk integration, secret attributes, environment-variable secrets, hardcoded passwords, API keys, database connection strings, or TLS certificate references were found.

No credentials or secrets are required for the migration. Redis authentication is not configured by this cookbook.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/redis.conf`, if provided by the target distribution package
- `/var/lib/redis`, if provided by the target distribution package
- Redis logs in the `redis-server` systemd journal or the distribution-specific package log

The cookbook directly manages only `cookbooks/cache/recipes/default.rb`. The Redis configuration, data, and log paths are package-managed defaults and may vary by distribution.

**Service endpoints to check**:

- **redis-server**: TCP port `6379`
- **redis-server**: Unix socket not configured or referenced
- **redis-server**: Bind address not configured by the cookbook; use the package default, commonly loopback

**Templates rendered**:

- None; render count: `0`

## Pre-flight checks

### redis-server instance

```bash
# Service status
systemctl status redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server

# Redis responsiveness
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server
redis-cli -p 6379 INFO persistence

# TCP listener
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'

# Debian or Ubuntu package verification
dpkg-query -W -f='${Package} ${Status}\n' redis-server

# RPM-based package verification
rpm -q redis-server

# Package-provided configuration validation
test -f /etc/redis/redis.conf && echo "Redis configuration exists"
grep -E '^(bind|port|protected-mode|dir)' /etc/redis/redis.conf

# Data directory verification
test -d /var/lib/redis && ls -ld /var/lib/redis
du -sh /var/lib/redis

# Logs
journalctl -u redis-server --no-pager -n 50
```

Expected results:

- `redis-server` is enabled and active.
- `redis-cli -p 6379 PING` returns `PONG`.
- Redis responds to `INFO server` and `INFO persistence`.
- Redis listens on TCP port `6379`, commonly on `127.0.0.1:6379` or `[::1]:6379` when the package defaults to loopback-only binding.
- On Debian or Ubuntu, the package status includes `redis-server install ok installed`.
- The package-provided configuration exists where applicable and uses port `6379` unless the distribution package has a different default.
- The data directory is available where provided by the package.
- Logs show successful startup without bind, permission, or configuration parsing errors.

The cookbook does not create or override the Redis configuration, data directory, log configuration, bind address, or authentication settings.