---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook provides a minimal local Redis cache setup for Ubuntu and CentOS. It installs the `redis-server` package, enables the `redis-server` service at boot, and starts it. The cookbook does not manage Redis configuration files, data directories, log files, credentials, templates, custom resources, or additional instances. Redis commonly listens on TCP port `6379` by the platform package default, but the cookbook does not explicitly configure a port.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: Local Redis in-memory key-value cache and data store
  - Package: `redis-server`
  - Service: `redis-server`
  - Service actions: Enable and start
  - Location/Path: No cookbook-managed configuration path
  - Port/Socket: TCP port `6379` is the common package default; no port or Unix socket is explicitly configured by the cookbook
  - Key Config: No Redis configuration settings are managed by the cookbook

## File Structure

Only the recipe shown in the execution tree is used.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

None.

**Templates:**

None.

**Attributes:**

None.

**Files:**

None.

The cookbook metadata identifies the cookbook as `cache`, version `1.0.0`, with the description `Simple cache cookbook - local dependency`. It supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. `metadata.rb` is metadata and is not an executed recipe file.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs the `redis-server` system package using `package[redis-server]` with action `:install`.
   - Enables and starts the `redis-server` service using `service[redis-server]` with actions `:enable` and `:start`.
   - Does not specify a package version, repository, configuration file, restart, reload, or service notification.
   - Does not define loops, conditional branches, included recipes, custom resources, users, groups, directories, files, templates, or execute resources.
   - No `.each` iterations are present.

**Execution order:**

1. Install package `redis-server`.
2. Enable and start service `redis-server`.

## Dependencies

**External cookbook dependencies**: None declared or shown.

**System package dependencies**: `redis-server`

**Service dependencies**: `redis-server`

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The Chef cookbook explicitly uses `redis-server` for both the package and service. The Ansible migration should account for package or service naming differences if a target distribution does not expose the same names.

## Credentials

**Detection Summary**: 0 credentials detected across 1 executed recipe.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No credentials or secrets were detected in this cookbook. There are no data bag lookups, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, secret-related attributes, environment-variable secrets, hardcoded passwords, database connection strings, or TLS certificate references.

No Redis authentication configuration is managed. If authentication is required during migration, it must be added as a separate requirement and stored with Ansible Vault or the organization’s configured secret-management system.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- No cookbook-managed configuration files
- No cookbook-managed data directories
- No cookbook-managed log files

Package and service verification commands:

```bash
dpkg -s redis-server 2>/dev/null || rpm -q redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server
systemctl status redis-server --no-pager
```

**Service endpoints to check**:

- **redis-server**: TCP port `6379` if the platform package retains its standard default configuration
- **redis-server**: No Unix socket configured by the cookbook
- **redis-server**: No network interface configured by the cookbook

**Templates rendered**: None; 0 templates rendered.

## Pre-flight checks

Run these checks after applying the Ansible role.

### `redis-server` package and service

```bash
# Verify that the redis-server package is installed
dpkg -s redis-server 2>/dev/null || rpm -q redis-server

# Verify that the redis-server service is enabled at boot
systemctl is-enabled redis-server

# Verify that the redis-server service is running
systemctl is-active redis-server

# Review redis-server service status
systemctl status redis-server --no-pager
```

Expected results:

- The package query reports that `redis-server` is installed.
- `systemctl is-enabled redis-server` returns `enabled`.
- `systemctl is-active redis-server` returns `active`.

### `redis-server` Redis health

```bash
# Verify that redis-server responds to a ping on the conventional port
redis-cli -p 6379 PING

# Verify that redis-server reports server information
redis-cli -p 6379 INFO server

# Verify basic set/get cache behavior
redis-cli -p 6379 SET chef_migration_check ok
redis-cli -p 6379 GET chef_migration_check

# Remove the temporary validation key
redis-cli -p 6379 DEL chef_migration_check
```

Expected results:

- `PING` returns `PONG`.
- `INFO server` returns Redis server information.
- `SET` returns `OK`.
- `GET` returns `ok`.
- `DEL` reports removal of the temporary key.

If the target operating system or external configuration uses a non-default port, obtain the active port from the Redis configuration or service command line before running these checks. The cookbook does not set or override the port.

### `redis-server` network listener

```bash
# Check whether redis-server is listening on the conventional Redis port
ss -ltnp | grep ':6379'

# Alternative process and socket check
netstat -ltnp 2>/dev/null | grep ':6379'
```

Expected result:

- A Redis process is listening on TCP port `6379` if the platform package retains its standard default configuration.

### `redis-server` logs and diagnostics

```bash
# Review recent redis-server service logs
journalctl -u redis-server --no-pager -n 100

# Follow redis-server service logs during troubleshooting
journalctl -u redis-server -f
```

The migration should not add configuration-file validation because this cookbook does not deploy or modify a Redis configuration file.