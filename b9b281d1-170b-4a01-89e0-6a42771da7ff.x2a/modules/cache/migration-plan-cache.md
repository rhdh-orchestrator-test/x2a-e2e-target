---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook provisions a local Redis cache on Ubuntu or CentOS. It installs the `redis-server` system package and enables and starts the `redis-server` service. The cookbook defines one service instance, does not configure Redis settings, templates, credentials, ports, persistence paths, or custom resources, and has no external Chef cookbook dependencies.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: Local Redis cache service
  - Package: `redis-server`
  - Package version: Not pinned; the host package manager installs its current candidate version.
  - Service: `redis-server`
  - Service actions: Enable at boot and start immediately.
  - Location/Path: No cookbook-managed configuration, persistence, data, or log paths.
  - Port/Socket: TCP port `6379` is the conventional Redis default, but the cookbook does not explicitly configure or validate it. No Unix socket is configured.
  - Key Config: No Redis settings, configuration files, users, directories, or persistence settings are managed by the cookbook.

**Iterations**: None. The execution tree contains no loops or collection attributes.

## File Structure

Only the recipe shown in the execution tree is used.

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

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs the `redis-server` package using `package[redis-server]` with the `install` action.
   - Enables and starts the `redis-server` service using `service[redis-server]`.
   - No configuration files, templates, static files, users, directories, handlers, notifications, or custom resources are used.
   - No recipes are included.
   - Iterations: None.

## Dependencies

**External cookbook dependencies**: None declared in the available metadata.

**System package dependencies**:

- `redis-server`

**Service dependencies**:

- `redis-server`, enabled and started by the recipe.

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The migration should account for distribution-specific Redis package or service naming if required by the target fleet. The Chef execution tree explicitly uses `redis-server` as both the package and service resource name, so that name is the default migration value.

## Credentials

**Detection Summary**: 0 credentials detected across the analyzed files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, Conjur, CyberArk, vault attributes, environment-variable secrets, hardcoded passwords, API keys, database connection strings, or TLS certificate references are present. No secret-related attributes or templates are used.

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- No configuration files are created by the cookbook.
- Package-managed Redis files and directories are distribution-specific and are not explicitly managed by this cookbook.
- No application-specific data or log paths are configured.

**Service endpoints to check**:

- **redis-server**: Redis TCP port `6379` if the installed package uses the standard default.
- **redis-server**: No Unix socket configured by the cookbook.
- **redis-server**: No network interfaces configured by the cookbook.

**Templates rendered**:

- None; 0 templates rendered.

## Pre-flight checks:

```bash
# Instance: redis-server
# Confirm the package is installed
dpkg-query -W redis-server 2>/dev/null || rpm -q redis-server

# Confirm the service is enabled and running
systemctl is-enabled redis-server
systemctl is-active redis-server
systemctl status redis-server --no-pager

# Confirm Redis responds locally
redis-cli PING
redis-cli INFO server
redis-cli INFO stats

# Inspect the effective Redis port and bind configuration
redis-cli CONFIG GET port
redis-cli CONFIG GET bind

# If the effective port is 6379, confirm Redis is listening
ss -ltnp | grep ':6379'

# Confirm local connectivity on the conventional Redis port
redis-cli -h 127.0.0.1 -p 6379 PING

# Inspect effective data settings and recent service logs
redis-cli CONFIG GET dir
redis-cli CONFIG GET dbfilename
journalctl -u redis-server --no-pager -n 50

# Confirm enablement persists
systemctl is-enabled redis-server
systemctl show redis-server --property=ActiveState,UnitFileState
```

Expected results:

- The package query reports `redis-server` as installed.
- `systemctl is-enabled redis-server` reports `enabled`.
- `systemctl is-active redis-server` reports `active`.
- `redis-cli PING` returns `PONG`.
- `redis-cli INFO server` returns Redis server metadata.
- `redis-cli INFO stats` returns Redis statistics.
- If the effective Redis port is `6379`, `ss` shows a Redis process listening on the expected address and port.
- `systemctl show redis-server` reports `ActiveState=active` and `UnitFileState=enabled`.

If the local connectivity check fails, inspect the effective `bind` and `port` values returned by `redis-cli CONFIG GET`.