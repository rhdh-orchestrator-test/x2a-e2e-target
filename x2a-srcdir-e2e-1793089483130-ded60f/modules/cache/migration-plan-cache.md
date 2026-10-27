---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one local Redis cache service. It installs the `redis-server` system package and enables and starts the `redis-server` service. No cookbook-managed configuration files, templates, attributes, custom resources, iterations, credentials, ports, sockets, or external cookbook dependencies are present. The equivalent Ansible implementation requires one package task followed by one service task.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: Local Redis cache service
  - Package: `redis-server`
  - Service: `redis-server`
  - Service state: Enabled and started
  - Port/Socket: No port or socket is explicitly configured by the cookbook. Redis commonly uses TCP port `6379` through the package default configuration.
  - Configuration path: No configuration path is explicitly managed by the cookbook.
  - Data path: No data directory is explicitly managed by the cookbook.

## File Structure

Only the recipe shown in the execution tree is included. `metadata.rb` was examined for service identification and dependency information but is not included below because the required file listing is restricted to `.rb` files shown in the execution tree.

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
   - Installs the operating-system package `redis-server` using the Chef `package` resource with action `:install`.
   - Enables and starts the `redis-server` service using the Chef `service` resource with actions `:enable` and `:start`.
   - Does not deploy templates or static files.
   - Does not define conditional branches, custom resources, providers, or `.each` iterations.
   - Resource execution order:
     1. `package[redis-server]`
     2. `service[redis-server]`

Equivalent Ansible tasks:

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

## Dependencies

**External cookbook dependencies**: None listed in `cookbooks/cache/metadata.rb`.

**System package dependencies**:

- `redis-server`

**Service dependencies**:

- `redis-server`

The metadata supports Ubuntu version `18.04` or later and CentOS version `7.0` or later. The recipe does not contain platform-specific branching.

## Credentials

**Detection Summary**: 0 credentials detected across 2 analyzed files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No data bags, encrypted data bags, Chef Vault items, Conjur variables, CyberArk integrations, secret-related attributes, environment-variable secrets, hardcoded passwords, API keys, database connection strings, or TLS certificate references were found. No credentials need to be migrated to Ansible Automation Platform credential objects or Ansible Vault.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `cookbooks/cache/metadata.rb`
- Package-managed Redis configuration files, if created by the target distribution
- Package-managed Redis data directory, if created by the target distribution
- Package-managed Redis log destination, if created by the target distribution

The cookbook does not explicitly create configuration, data, or log files. Do not add file-management tasks unless managing these paths is an external migration requirement.

**Service endpoints to check**:

- `redis-server` TCP port `6379` as the conventional Redis default
- `redis-server` Unix socket: None configured by the cookbook
- `redis-server` network interfaces: None configured by the cookbook

Port `6379` is a Redis default and is not configured by this cookbook. Confirm the actual listener from the installed Redis configuration.

**Templates rendered**: None

**Static files deployed**: None

## Pre-flight checks:

```bash
# Verify that the redis-server package is installed
dpkg-query -W -f='${Status}\n' redis-server 2>/dev/null || rpm -q redis-server

# Verify that the redis-server service is enabled
systemctl is-enabled redis-server

# Verify that the redis-server service is running
systemctl is-active redis-server
systemctl status redis-server --no-pager

# Verify that the redis-server instance responds
redis-cli PING

# Confirm redis-server information
redis-cli INFO server

# Verify the conventional redis-server TCP listener
ss -ltnp | grep ':6379'

# Verify local connectivity to the redis-server instance
redis-cli -h 127.0.0.1 -p 6379 SET migration_check success
redis-cli -h 127.0.0.1 -p 6379 GET migration_check
redis-cli -h 127.0.0.1 -p 6379 DEL migration_check

# Review redis-server service logs
journalctl -u redis-server --no-pager -n 100

# Review redis-server service state and exit status
systemctl show redis-server --property=ActiveState,SubState,ExecMainStatus
```

Expected results:

- The `redis-server` package is installed.
- `systemctl is-enabled redis-server` reports `enabled`.
- `systemctl is-active redis-server` reports `active`.
- `redis-cli PING` returns `PONG`.
- `redis-server` returns server information through `redis-cli INFO server`.
- If the package uses its default TCP configuration, port `6379` is listening.
- The local connectivity check returns `OK`, `success`, and `1` for `SET`, `GET`, and `DEL`, respectively.
- Service logs contain no unexpected startup or runtime failures.

No additional Redis configuration, passwords, ACLs, databases, users, firewall rules, persistence settings, replication, custom ports, Unix sockets, data directories, log rotation, or additional instances are defined by this cookbook.