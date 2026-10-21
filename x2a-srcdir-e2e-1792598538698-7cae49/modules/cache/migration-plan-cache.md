---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a single local Redis cache service. It installs the unpinned `redis-server` package and enables and starts the `redis-server` service. The cookbook does not deploy configuration files, templates, attributes, credentials, custom resources, data directories, or static files. Redis commonly listens on TCP port `6379`, but that port is not configured by the cookbook and must be verified on the target system.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: Local Redis cache service
  - Location/Path: No cookbook-managed data or configuration path
  - Port/Socket: TCP `6379` is the common platform default; no port or Unix socket is configured by the cookbook
  - Key Config: Package `redis-server`; version not pinned; service enabled and started; no Redis configuration file deployed or modified

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

`metadata.rb` was analyzed for cookbook metadata but is excluded from the migration file list because the supplied file-structure rules require listing only executable recipe files shown in the execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs the `redis-server` package using `package[redis-server]` with action `:install`.
   - The package version is not specified or pinned.
   - Enables and starts the `redis-server` service using `service[redis-server]` with actions `:enable` and `:start`.
   - No configuration files, templates, static files, or data directories are created or deployed.
   - No notifications, handlers, service restarts, or reloads are defined.
   - Iterations: None. There are no `.each` loops or resource collections to expand.
   - Custom resources: None.
   - Resources: one package resource and one service resource.
   - Templates rendered: None.

The semantic Ansible task sequence is:

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

The cookbook does not specify a package version, repository, Redis configuration, bind address, authentication, or persistence settings. The migration must not add those settings unless they are provided as separate requirements.

## Dependencies

**External cookbook dependencies**: None declared in the analyzed metadata.

**System package dependencies**:

- `redis-server`
  - Version: Not pinned
  - Installation action: `install`

**Service dependencies**:

- `redis-server`
  - Enabled at boot
  - Started during convergence

**Platform support declared by metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The cookbook uses the package name `redis-server` exactly. If the target operating system uses a different repository package name, handle it through an explicit platform-specific Ansible variable only after confirming the target platform’s package naming. Do not silently add additional packages or repositories.

## Credentials

**Detection Summary**: 0 credentials detected across 1 analyzed recipe file.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk integration, Vault attributes, secret environment variables, hardcoded passwords, tokens, API keys, database connection strings, or TLS certificate references were detected.

No credentials need to be configured in Ansible Automation Platform for this cookbook’s behavior.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- No cookbook-managed configuration, template, static, or data files

**Service endpoints to check**:

- `redis-server` on TCP port `6379`, subject to the installed package’s default configuration
- Unix socket: None configured by the cookbook
- Network interface or bind address: None configured by the cookbook

**Templates rendered**:

- None

Verify that:

- The `redis-server` package is installed.
- The `redis-server` service is enabled.
- The `redis-server` service is running.
- No unexpected configuration files were introduced by the Ansible role beyond those created by the operating system package.
- Redis accepts local connections and supports basic write, read, and delete operations.

Package-managed Redis paths are distribution-dependent and are not specified by this cookbook. Do not hardcode configuration or data paths without confirming them on the target operating system.

## Pre-flight checks:

```bash
# Confirm the redis-server package is installed
dpkg-query -W -f='${Package} ${Version}\n' redis-server 2>/dev/null || \
rpm -q redis-server

# Confirm the redis-server service is enabled
systemctl is-enabled redis-server

# Confirm the redis-server service is active
systemctl is-active redis-server

# Review the redis-server service status
systemctl status redis-server --no-pager

# Redis instance health check: expected output is PONG
redis-cli -h 127.0.0.1 -p 6379 PING

# Inspect Redis server and persistence information
redis-cli -h 127.0.0.1 -p 6379 INFO server
redis-cli -h 127.0.0.1 -p 6379 INFO persistence

# Confirm a process is listening on the common Redis TCP port
ss -ltnp | grep ':6379'

# Inspect recent redis-server service logs
journalctl -u redis-server --no-pager -n 100

# Follow redis-server service logs during validation
journalctl -u redis-server -f

# Validate basic write, read, and delete operations for the redis-server instance
redis-cli -h 127.0.0.1 -p 6379 SET migration_check success
redis-cli -h 127.0.0.1 -p 6379 GET migration_check
redis-cli -h 127.0.0.1 -p 6379 DEL migration_check
```

Expected results for the `redis-server` instance:

- `redis-server` is installed.
- `systemctl is-enabled redis-server` reports `enabled`.
- `systemctl is-active redis-server` reports `active`.
- `redis-cli -h 127.0.0.1 -p 6379 PING` returns `PONG`.
- Redis server information commands return data without a connection failure.
- A Redis process is listening on TCP port `6379` if the package default configuration is unchanged.
- The basic write, read, and delete checks return:

```text
OK
"success"
(integer) 1
```

If `redis-cli` is not available in the target package set, use an equivalent Redis client or verify the package-provided client package before adding it as a migration dependency.