---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one local Redis cache instance named `redis-server`. It installs the `redis-server` operating-system package and enables and starts the `redis-server` service. The cookbook contains one recipe, no iterations, custom resources, templates, static files, configured attributes, credentials, or external cookbook dependencies. It does not configure Redis ports, sockets, persistence, authentication, users, directories, or firewall rules.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: Local Redis cache service
  - Package: `redis-server`
  - Service: `redis-server`
  - Service actions: Enable and start
  - Location/Path: No cookbook-managed configuration path
  - Port/Socket: No port or socket is explicitly configured by the cookbook. Redis commonly uses TCP port `6379` through the package default; verify this on the target system.
  - Key Config: Package installation followed by service enablement and startup. No Redis configuration files, persistence directories, authentication, users, bind addresses, or firewall rules are managed.

## File Structure

Only files shown in the supplied execution tree are included.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No custom resources or provider files are used.

**Templates:**
```text
```

No templates are rendered.

**Attributes:**
```text
```

No attribute files are used or listed in the execution tree.

**Files:**
```text
```

No static files are deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **Default recipe** (`cookbooks/cache/recipes/default.rb`):
   - Installs the `redis-server` package with `package[redis-server]` and action `:install`.
   - Enables and starts the `redis-server` service with `service[redis-server]` and actions `:enable` and `:start`.
   - Package installation occurs before service management so the service unit exists before it is enabled and started.
   - Resources used: one package resource and one service resource.
   - Includes: no additional recipes.
   - Custom resources: none.
   - Templates and files deployed: none.
   - Iterations: none; the recipe contains no collection attributes or `.each` loops.
   - Ansible equivalents:
     ```yaml
     - name: Install Redis server
       ansible.builtin.package:
         name: redis-server
         state: present

     - name: Enable and start Redis server
       ansible.builtin.service:
         name: redis-server
         enabled: true
         state: started
     ```

Do not add configuration templates, Redis users, directories, firewall rules, persistence settings, bind addresses, or authentication settings unless they are introduced by a separate migration requirement.

## Dependencies

**External cookbook dependencies**: None declared.

**Supported platforms**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:
- `redis-server`

**Service dependencies**:
- `redis-server`

**Ansible collection dependencies**: `ansible.builtin` modules are sufficient; no external collection is required.

## Credentials

**Detection Summary**: 0 credentials detected across 1 analyzed cookbook file.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No credentials or secrets were detected. No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk integration, vault attributes, secret environment variables, hardcoded passwords, API keys, database connection strings, or TLS certificate references were found.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`

The cookbook does not create or deploy configuration files. Verify package and service state instead:
- Installed Redis package metadata:
  ```bash
  dpkg-query -W redis-server 2>/dev/null || rpm -q redis-server
  ```
- Redis service unit state:
  ```bash
  systemctl is-enabled redis-server
  systemctl is-active redis-server
  ```
- Inspect the target distribution's package-managed Redis configuration only when platform verification requires it; the cookbook does not manage a specific configuration path.

**Service endpoints to check**:
- **redis-server**: TCP port `6379`, only if the installed Redis package uses its standard default listener.
- **redis-server**: No Unix socket configured by this cookbook.

**Templates rendered**: None; render count is 0.

## Pre-flight checks

Run these checks after the Ansible role completes.

### `redis-server` package and service

```bash
# Confirm the Redis package is installed
dpkg-query -W redis-server 2>/dev/null || rpm -q redis-server

# Confirm the redis-server service is enabled at boot
systemctl is-enabled redis-server

# Confirm the redis-server service is running
systemctl is-active redis-server

# Review redis-server service status
systemctl status redis-server --no-pager
```

Expected results:
- The package query reports `redis-server` as installed.
- `systemctl is-enabled redis-server` reports `enabled`.
- `systemctl is-active redis-server` reports `active`.

### `redis-server` health

```bash
# Redis should respond with PONG
redis-cli PING

# Verify Redis server information is available
redis-cli INFO server | grep -E 'redis_version|process_id|uptime_in_seconds'
```

Expected result:
```text
PONG
```

### `redis-server` network listener

The cookbook does not configure a port explicitly. If the platform package uses Redis's standard default listener, verify TCP port `6379`:

```bash
ss -ltnp | grep ':6379'
```

A successful result should show a Redis process listening on TCP port `6379`. If no listener appears, inspect the distribution's Redis configuration and service logs. Do not add listener configuration to the Ansible role unless separately required.

### `redis-server` service logs

```bash
# Review recent Redis service messages
journalctl -u redis-server --no-pager -n 100

# Review errors from the current boot
journalctl -u redis-server -b --no-pager | grep -iE 'error|failed|fatal|warning'
```

### `redis-server` functional cache check

```bash
# Write a temporary key
redis-cli SET migration_check "ok"

# Read the temporary key
redis-cli GET migration_check

# Remove the temporary key
redis-cli DEL migration_check
```

Expected results:
- `SET` returns `OK`.
- `GET` returns `ok`.
- `DEL` returns `1`.