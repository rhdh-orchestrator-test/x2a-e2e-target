---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures a Memcached instance named `memcached` and a Redis instance identified as `6379`. The supplied source-level plan specifies Memcached on TCP/UDP port `11211` and Redis on TCP port `6379`, with Redis authentication, `/run/redis` for PID files, `/var/log/redis` for logs, and removal of five replication-related directives. The Redis installation and enablement behavior depends on the missing `redisio` and `redisio::enable` recipes and must be validated during migration. The Redis password must be migrated from hardcoded Chef storage to Ansible Vault.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: In-memory key-value cache
  - Location/Path: Platform-specific Memcached configuration path; not specified by the supplied Chef files
  - Port/Socket: TCP `11211`; UDP `11211`; listen address `0.0.0.0`
  - Key Config: Memory `64` MB, maximum connections `1024`, maximum object size `1m`, service user `service_user`, ulimit `1024`, empty experimental and additional CLI option lists, start and enable actions
  - Validation status: The custom resource and source-level values are present in the supplied plan but should be confirmed against the detailed recipe and attribute files

- **`6379`**: Redis cache/data-store instance
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket configured or referenced
  - Key Config: Password authentication using the migrated Vault variable, Redis log directory owned by `redis:redis` with mode `0755`, and removal of the following directives from `/etc/redis/6379.conf`:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`
  - Validation status: The Redis server collection, password, PID directory, port, and directive cleanup are source-level details requiring confirmation against the detailed recipe because the supplied execution summary only confirms the missing `redisio` and `redisio::enable` includes

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only files shown as executed or used by the supplied execution tree and structured analysis are listed below. The `redisio` recipe files are not listed because the execution tree reports them as missing.

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

No provider file path was supplied. The `memcached_instance[memcached]` custom resource is used, but its provider implementation is not included in the supplied file set.

**Templates:**

No templates are rendered by the supplied recipes or execution tree.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

No static files are deployed by `cookbook_file` or `remote_file` resources.

**Analyzed-file inventory note:** The structured analysis reports seven analyzed files, while only the three migration-relevant paths above are identified in the supplied plan. Four additional analyzed files are not named in the source material and must be reconciled before migration sign-off.

## Module Explanation

The cookbook performs operations in the following order.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached recipe.
   - Assigns a one-item Redis server collection containing the instance `6379`.
   - Sets the Redis base PID directory to `/run/redis`.
   - Includes the missing `redisio` recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block['fix_redis_config']` against `/etc/redis/6379.conf`.
   - Includes the missing `redisio::enable` recipe.

   The one Redis collection item is:

   - **`6379`**: Port `6379`, password authentication, password `redis_secure_password_123` in the original Chef source, and `replicaservestaledata` set to `nil`.

   The Ansible implementation should store the password in Ansible Vault rather than plaintext. Because the `redisio` recipes are absent, Redis package installation, service-account creation, exact service unit, and complete service configuration are inferred migration requirements rather than behavior confirmed by the supplied execution tree.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Configures instance **`memcached`** with the following source-level values:
     - Memory: `64` MB
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Service user: `service_user`
     - Maximum object size: `1m`
     - Threads: `node['memcached']['threads']`; no explicit default is present in the supplied attribute file
     - Experimental options: `[]`
     - Additional CLI options: `[]`
     - Ulimit: `1024`
     - Actions: start and enable
   - The values above must be confirmed against the detailed recipe and attributes analysis before implementation sign-off.
   - The custom resource provider path is not supplied and must not be inferred.

3. **Missing `redisio` recipe**:
   - Execution-tree status: Recipe file not found.
   - The Ansible role must explicitly implement the required Redis behavior only after validating the source-level Redis assignments.
   - Expected migration tasks include installing the distribution-appropriate Redis package, managing instance `6379`, creating `/run/redis`, managing `/etc/redis/6379.conf`, and configuring the Redis service.

4. **`directory['/var/log/redis']`** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis` recursively.
   - Sets owner `redis`.
   - Sets group `redis`.
   - Sets mode `0755`.
   - The Ansible equivalent should use `ansible.builtin.file` with `state: directory`.

5. **`ruby_block['fix_redis_config']`** (`cookbooks/cache/recipes/default.rb`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Reads the complete file when present.
   - Removes lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Does nothing when the file does not exist.
   - The Ansible implementation should use an idempotent template or replacement tasks.

6. **Missing `redisio::enable` recipe**:
   - Execution-tree status: Recipe file not found.
   - The Ansible role must determine the target distribution’s Redis unit name and enable and start the service after configuration.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**System package dependencies**:

- Memcached package: `memcached`
- Redis package: `redis-server` on Debian-family systems or `redis` on Fedora/RHEL-family systems
- Redis client utilities: commonly provided by `redis-tools` on Debian-family systems or the distribution’s Redis package on Fedora/RHEL-family systems

Package names must be selected according to the supported target distribution.

**Service dependencies**:

- Memcached service for instance `memcached`
- Redis service for instance `6379`
- Exact Redis systemd unit name is not available because the `redisio` recipes are missing

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: Chef recipe attribute assignment
  - **URL**: None detected
  - **Path**: `cookbooks/cache/recipes/default.rb`
  - **Storage method**: Hardcoded plaintext in the Chef recipe; migrate to Ansible Vault

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`; Ansible destination variable such as `redis_password`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Configured value**: `redis_secure_password_123`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis `requirepass` authentication for instance `6379`
- **Ansible storage**: Ansible Vault variable or external secret-management integration
- **Provider**: Chef recipe attribute assignment

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, database connection strings, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- The selected platform-specific Memcached configuration file
- The selected Redis systemd unit or service definition

**Service endpoints to check**:

- Instance `memcached`: TCP `0.0.0.0:11211`
- Instance `memcached`: UDP `0.0.0.0:11211`
- Instance `6379`: TCP port `6379`
- Instance `6379`: no configured Unix socket
- Instance `6379`: PID directory `/run/redis`

**Templates rendered**:

- Chef templates rendered: `0`
- Ansible templates rendered: implementation-dependent; if `/etc/redis/6379.conf` is managed by a template, verify exactly one rendered Redis configuration template for instance `6379`

## Pre-flight checks:

```bash
# Confirm required packages are available on the target distribution.
# Debian-family example:
apt-cache policy memcached redis-server redis-tools

# Fedora/RHEL-family example:
dnf info memcached redis

# Verify the Memcached service for instance memcached.
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Verify Memcached TCP endpoint for instance memcached.
ss -ltnp | grep ':11211'

# Verify Memcached UDP endpoint for instance memcached.
ss -lunp | grep ':11211'

# Verify the Memcached protocol for instance memcached.
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Inspect the platform-specific Memcached configuration for instance memcached.
# Confirm memory 64 MB, TCP/UDP port 11211, listen address 0.0.0.0,
# maximum connections 1024, maximum object size 1m, and ulimit 1024.

# Identify the Redis service unit for instance 6379.
systemctl list-unit-files | grep -i redis
systemctl --type=service | grep -i redis

# Replace <redis-service-unit> with the selected unit for instance 6379.
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>

# Verify the Redis TCP endpoint for instance 6379.
ss -ltnp | grep ':6379'

# Verify authenticated Redis connectivity for instance 6379.
redis-cli -p 6379 -a '<redis-password>' PING

# Expected result:
# PONG

# Verify authentication enforcement for instance 6379.
redis-cli -p 6379 PING

# Expected result:
# Authentication is required.

# Verify Redis configuration for instance 6379.
grep -E '^(port|requirepass|pidfile|dir)' /etc/redis/6379.conf

# Confirm the five Chef cleanup directives are absent for instance 6379.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Expected result:
# No matching configuration lines are returned.

# Verify the Redis log directory for instance 6379.
stat -c '%A %U %G %n' /var/log/redis

# Expected:
# Owner redis, group redis, mode 0755.

# Verify the Redis PID directory for instance 6379.
stat -c '%A %U %G %n' /run/redis
ls -la /run/redis

# Verify service logs for both named instances.
journalctl -u <redis-service-unit> --no-pager -n 100
journalctl -u memcached --no-pager -n 100

# Check for successful startup, permission errors, configuration parse errors,
# and authentication failures.
```