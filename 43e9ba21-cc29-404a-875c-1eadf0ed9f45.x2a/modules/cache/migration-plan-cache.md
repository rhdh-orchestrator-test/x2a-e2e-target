---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook installs the `redis-server` system package and enables and starts the `redis-server` service on supported Ubuntu and CentOS systems. It does not manage Redis configuration files, templates, data directories, users, firewall rules, credentials, or custom resources. The equivalent Ansible migration requires one package task followed by one service task.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: Local Redis cache and in-memory data store
  - Package: `redis-server`
  - Service: `redis-server`
  - Service actions: Enabled at boot and started immediately
  - Port/Socket: No port or socket is explicitly configured. Redis commonly uses TCP port `6379` by default; verify the target distribution's configuration.
  - Key Config: No Redis configuration settings or configuration files are managed by this cookbook.

## File Structure

Only files present in the supplied execution tree are listed.

**Recipes:**
```text
recipes/default.rb
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

The metadata file was examined to identify the cookbook description and supported platforms, but it is not included above because the required file list is restricted to executable `.rb` files shown in the execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs the `redis-server` system package using `package[redis-server]` with the `:install` action.
   - Enables and starts the `redis-server` service using `service[redis-server]` with the `:enable` and `:start` actions.
   - No configuration files, templates, directories, users, firewall rules, notifications, or restart/reload actions are managed.
   - Iterations: None.
   - Custom resources: None.
   - Included recipes: None.
   - Resource counts: one package resource and one service resource.

Execution order:

1. Install package `redis-server`.
2. Enable service `redis-server`.
3. Start service `redis-server`.

## Dependencies

**External cookbook dependencies**: None declared in the available metadata.

**System package dependencies**: `redis-server`

**Service dependencies**: `redis-server`

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

Package and service names may vary by target distribution. The cookbook explicitly uses `redis-server` for both, so the migration should preserve those names where supported and add platform-specific mappings only when required.

## Credentials

**Detection Summary**: 0 credentials detected across the analyzed recipe and metadata.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No data bags, encrypted data bags, Chef Vault items, Conjur variables, CyberArk integrations, secret attributes, environment-variable secrets, hardcoded passwords, API keys, database connection strings, or TLS certificate references were detected. No credentials need to be migrated to Ansible Automation Platform credentials or Ansible Vault.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- No cookbook-created configuration files
- No cookbook-created data directories
- No cookbook-created log files

The package manager may install distribution-owned Redis files, but those files are not explicitly created or managed by this cookbook.

**Service endpoints to check**:

- **redis-server**: TCP port `6379` if the packaged Redis default configuration is unchanged
- **redis-server**: No Unix socket configured by this cookbook
- **redis-server**: No network interfaces configured by this cookbook

**Templates rendered**: None; render count: 0.

## Pre-flight checks:

```bash
# redis-server instance: verify the package is installed
dpkg-query -W -f='${Status} ${Package}\n' redis-server 2>/dev/null || \
rpm -q redis-server

# redis-server instance: verify the service is enabled and running
systemctl is-enabled redis-server
systemctl is-active redis-server
systemctl status redis-server --no-pager

# redis-server instance: verify Redis responds on the default local endpoint
redis-cli -h 127.0.0.1 -p 6379 PING
# Expected output:
# PONG

# redis-server instance: verify server information
redis-cli -h 127.0.0.1 -p 6379 INFO server

# redis-server instance: verify the default listening port when applicable
ss -ltnp | grep ':6379'

# redis-server instance: check recent service logs
journalctl -u redis-server --no-pager -n 50
```

Expected results:

- The `redis-server` package is installed.
- The `redis-server` service is enabled at startup.
- The `redis-server` service is active and running.
- `redis-cli -h 127.0.0.1 -p 6379 PING` returns `PONG`.
- Redis listens on TCP port `6379` if the packaged default configuration is unchanged.
- No package installation or service startup errors appear in the service journal.