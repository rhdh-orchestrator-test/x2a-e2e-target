---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook provisions one local Redis cache service named `redis-server`. It installs the `redis-server` system package, enables the service at boot, and starts it immediately. No Redis configuration files, templates, credentials, ports, persistence settings, memory limits, custom resources, or data directories are managed by the cookbook.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: Local Redis cache service
  - Package: `redis-server`
  - Service: `redis-server`
  - Actions: Install the package; enable the service at boot; start the service immediately
  - Location/Path: No configuration file or data directory is deployed by this cookbook
  - Port/Socket: No port or Unix socket is explicitly configured. Redis commonly uses TCP port `6379` by package defaults; verify the installed distribution's default.
  - Key Config: No persistence, memory, bind, authentication, or other Redis settings are managed.

## File Structure

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
   - Installs the `redis-server` system package.
   - Enables the `redis-server` service so it starts automatically at boot.
   - Starts the `redis-server` service immediately.
   - Resources used:
     - `package[redis-server]`: action `install`
     - `service[redis-server]`: actions `enable` and `start`
   - Files/templates deployed: None
   - Iterations: None; there are no `.each` loops or collection attributes.
   - Custom resources: None
   - Service restart or reload notifications: None

### Ansible Semantic Equivalent

A suitable Ansible implementation should contain two ordered tasks:

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

The Chef recipe does not manage Redis configuration. The migration should not add configuration templates, users, databases, firewall rules, persistence settings, or memory limits unless they are requirements outside this cookbook.

## Dependencies

**External cookbook dependencies**: None declared in the analyzed metadata.

**System package dependencies**:

- `redis-server`

**Service dependencies**:

- `redis-server`

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The exact Redis package and service behavior may vary by platform. Verify that target Ansible hosts expose the service as `redis-server`; some distributions or package versions may use `redis` instead.

## Credentials

**Detection Summary**: 0 credentials detected across 1 analyzed file.

**Source**:

- **Provider**: None detected
- **URL**: Not applicable
- **Path**: Not applicable

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk integration, Vault attributes, environment-variable secrets, hardcoded passwords, API keys, certificates, private keys, or credential-bearing connection strings were found.

All configuration represented by this cookbook is non-sensitive package and service state.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- No configuration files are created by this cookbook.
- No data directories are explicitly created by this cookbook.
- No log files are explicitly created by this cookbook.
- Redis package-managed files and directories may exist after installation, but their paths are distribution-specific and are not managed directly by the recipe.

**Service endpoints to check**:

- **redis-server**: Redis commonly listens on TCP port `6379`; the cookbook does not explicitly configure this port.
- **redis-server Unix socket**: None configured by this cookbook.
- **redis-server network interfaces**: None configured by this cookbook.

**Templates rendered**:

- None; render count: `0`.

## Pre-flight checks:

### `redis-server` package and service

```bash
# Confirm the package is installed
dpkg-query -W -f='${Package} ${Version}\n' redis-server 2>/dev/null || \
rpm -q redis-server

# Confirm the redis-server service is enabled and running
systemctl is-enabled redis-server
systemctl is-active redis-server
systemctl status redis-server --no-pager
```

Expected results:

- The `redis-server` package is installed.
- `systemctl is-enabled redis-server` reports `enabled`.
- `systemctl is-active redis-server` reports `active`.

If the target distribution uses the service name `redis`, adjust the Ansible service task and all checks consistently.

### `redis-server` Redis health

```bash
# Redis protocol health check
redis-cli -h 127.0.0.1 -p 6379 PING

# Basic server information
redis-cli -h 127.0.0.1 -p 6379 INFO server

# Confirm the installed Redis version
redis-server --version
```

Expected results:

- `redis-cli -h 127.0.0.1 -p 6379 PING` returns `PONG`.
- `INFO server` returns Redis server information.
- `redis-server --version` returns the installed Redis version.

### `redis-server` port verification

Because the cookbook does not configure a port, verify the package default if the service is expected to listen on TCP port `6379`:

```bash
ss -ltnp | grep ':6379'
```

The output should show a Redis process listening on TCP port `6379`. If the distribution uses only a Unix socket, inspect the package-provided Redis configuration and validate that socket instead.

### `redis-server` logs

```bash
# View recent service logs
journalctl -u redis-server --no-pager -n 100

# Follow Redis service logs during validation
journalctl -u redis-server -f
```

Check for startup failures, permission errors, configuration parsing errors, or bind failures.

### `redis-server` basic cache operation

```bash
# Write and read a temporary cache key
redis-cli -h 127.0.0.1 -p 6379 SET migration_healthcheck ok
redis-cli -h 127.0.0.1 -p 6379 GET migration_healthcheck
redis-cli -h 127.0.0.1 -p 6379 DEL migration_healthcheck
```

Expected results:

- `SET` returns `OK`.
- `GET` returns `ok`.
- `DEL` returns `1` when the temporary key is removed.