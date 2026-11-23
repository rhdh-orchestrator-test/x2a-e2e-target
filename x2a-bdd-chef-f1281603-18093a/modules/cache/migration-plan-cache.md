---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` and one Redis server entry, `redisio['servers'][0]`. Memcached is enabled and started on TCP and UDP port `11211`, with 64 MB of memory and a maximum of 1,024 connections. Redis is configured on port `6379`, uses `/run/redis` for its PID directory, stores logs under `/var/log/redis`, and requires an authentication password that must be migrated to Ansible Vault or an approved secret-management system. The Redis installation and enablement recipes are referenced but are not present in the supplied execution tree, so package names and the Redis service unit must be determined from the target platform or selected dependency role.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached cache service
  - Location/Path: Configuration path is not specified by the supplied cookbook
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, maximum 1,024 connections, maximum object size `1m`, `ulimit` `1024`, enabled and started, empty experimental and extra CLI option lists
  - Threads: Sourced from `node['memcached']['threads']`; no default is present in the supplied attributes
  - User: `service_user`; concrete value is not present in the supplied files
  - Version: `nil`; no explicit Memcached version is configured

- **`redisio['servers'][0]`**: Redis server entry
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: `requirepass` is configured from a hardcoded source value in Chef, which must be migrated to a secure Ansible secret
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Log directory creation: Recursive
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Service action: Enablement is referenced through the missing `redisio::enable` recipe
  - Bind address, package name, service name, replica count, and Redis version: Not specified in the supplied files

## File Structure

Only files present in the supplied execution tree or explicitly listed as used are included below. The Redis dependency recipes are referenced but absent and therefore are not listed as available files.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

No provider file is listed in the supplied execution tree. The `memcached_instance[memcached]` custom resource is used, but its provider implementation is not available in the supplied file set.

**Templates:**

No templates are rendered by the supplied recipes.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

No static files are deployed by `cookbook_file` or `remote_file`.

The following files from the directory listing are not part of the execution flow and must not be migrated as executed modules:

- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb`

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Assigns one Redis server entry to `node.default['redisio']['servers'][0]`.
   - Sets the Redis base PID directory to `/run/redis`.
   - Includes the Redis installation/configuration recipe, although its file is not present in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block['fix_redis_config']`, which reads `/etc/redis/6379.conf` when present, removes five replication-related directives, and writes the modified contents back.
   - Includes `redisio::enable`, although its recipe file is not present in the supplied execution tree.
   - Resources shown in the execution tree: `directory['/var/log/redis']` (1), `ruby_block['fix_redis_config']` (1).
   - The structural analysis also references a `group['redis']` resource, but it is not listed as an execution-tree resource. Preserve the required `redis` group ownership behavior without assuming an additional standalone resource.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance['memcached']` exactly once.
   - Starts and enables the `memcached` instance.
   - Configures 64 MB of memory.
   - Configures TCP port `11211` and UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets the maximum connection count to `1024`.
   - Sets the maximum object size to `1m`.
   - Reads the thread count from `node['memcached']['threads']`; no supplied default exists.
   - Passes `service_user` as the service user; the concrete value is unavailable.
   - Sets `ulimit` to `1024`.
   - Sets experimental options to `[]`.
   - Sets extra CLI options to `[]`.
   - Uses no explicit version because the configured version is `nil`.
   - Uses one custom resource: `memcached_instance['memcached']`.
   - The custom resource provider is not included in the supplied file set, and no templates are associated with it.

3. **`redisio`** (`redisio/recipes/default.rb`, referenced but not supplied):
   - The recipe file is not present in the supplied execution tree.
   - The known wrapper behavior is limited to configuring `redisio['servers'][0]` on port `6379`.
   - Uses `/run/redis` as the PID directory.
   - Ensures `/var/log/redis` exists with owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Applies the cleanup to `/etc/redis/6379.conf`.
   - Do not infer Redis package names, repository setup, service unit names, configuration templates, bind addresses, or Redis versions from the missing recipe.

4. **`redisio::enable`** (`redisio/recipes/enable.rb`, referenced but not supplied):
   - The recipe file is not present in the supplied execution tree.
   - Its intended semantic effect is to enable the Redis service.
   - Determine the actual service name from the target operating system or selected Redis dependency role rather than hardcoding an unsupported name.

## Dependencies

**External cookbook dependencies**:

- `memcached`
- `redisio`

The execution tree includes `memcached::default` and references `redisio` and `redisio::enable`. The Redis dependency recipe files are missing.

**System package dependencies**:

- No package resources or verified package names are present in the supplied execution tree.
- Memcached and Redis are configured, but their exact package names are unavailable.
- Do not claim a package name unless it is verified from the selected target distribution or dependency implementation.

**Service dependencies**:

- Memcached is started and enabled through `memcached_instance['memcached']`.
- Redis is intended to be enabled through the missing `redisio::enable` recipe.
- No explicit restart or reload notification is shown.
- `ruby_block['fix_redis_config']` directly rewrites `/etc/redis/6379.conf` without explicitly notifying a service restart or reload.

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded directly in the Chef recipe
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the Redis server configured on port `6379`

The Ansible migration must not preserve this password as plaintext in a committed task or variable file. Store it in Ansible Vault or an approved AAP credential or secret-management integration, then render or pass it to the Redis configuration securely.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database connection strings, or additional credential namespaces were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- The Memcached configuration file selected by the target Ansible package or role

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Redis Unix socket: none specified
- Redis bind address: not specified

**Templates rendered**:

- No Chef templates rendered: `0`
- No Ansible templates are implied by the supplied Chef execution tree; if an Ansible template is selected for Redis configuration, verify its render count independently.

**Configuration mutation**:

`ruby_block['fix_redis_config']` runs once and removes the following directives from `/etc/redis/6379.conf`:

```text
replica-serve-stale-data
replica-read-only
repl-ping-replica-period
client-output-buffer-limit
replica-priority
```

## Pre-flight checks:

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
pgrep -a memcached

# Memcached instance: TCP endpoint 0.0.0.0:11211
printf "version\r\n" | nc -w 2 127.0.0.1 11211
# Expected result: a response beginning with VERSION
ss -ltnp | grep ':11211'

# Memcached instance: UDP endpoint 0.0.0.0:11211
ss -lunp | grep ':11211'

# Memcached instance: configuration behavior
printf "stats\r\n" | nc -w 2 127.0.0.1 11211
# Expected result: statistics including pid, uptime, curr_connections, and limit_maxbytes

# Redis server entry: redisio['servers'][0], port 6379
# Substitute the service unit name supplied by the selected Redis package or role.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>

# Redis configuration file and configured port
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
ss -ltnp | grep ':6379'

# Redis authentication
grep '^requirepass ' /etc/redis/6379.conf
# Expected result: requirepass is populated from the Ansible Vault-backed secret,
# not from a plaintext committed variable.

export REDIS_PASSWORD='<retrieve-from-approved-secret-store>'
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
# Expected result: PONG
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server
# Expected result: Redis server information is returned.

# Redis configuration cleanup
! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
# Expected result: no matching directives are present.

# Redis log directory
stat -c '%A %U %G %n' /var/log/redis
# Expected result: mode 0755, owner redis, group redis

# Redis PID directory
test -d /run/redis
stat -c '%A %U %G %n' /run/redis

# Redis service-name verification
systemctl list-unit-files | grep -Ei 'redis|redis-server'
# Use the verified unit name for the Redis service checks above.
```