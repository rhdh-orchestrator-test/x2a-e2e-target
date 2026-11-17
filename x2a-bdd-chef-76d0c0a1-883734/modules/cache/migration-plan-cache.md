---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Memcached instance named `memcached` through the `memcached_instance[memcached]` custom resource and one Redis instance on port `6379`. The Redis configuration uses `/run/redis` as its PID/runtime directory, creates `/var/log/redis`, removes five replication-related directives from `/etc/redis/6379.conf`, and enables the Redis service. Memcached attribute values and dependency implementation details require verification because they are not present in the supplied structured analysis. The Redis password must be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached service managed by the `memcached_instance[memcached]` custom resource.
  - Location/Path: Dependency cookbook resource; exact configuration path is not exposed.
  - Port/Socket: TCP and UDP port values are supplied through `node['memcached']`; the structured analysis does not verify their values.
  - Key Config: Resource action is `[:start, :enable]`. Memory, listen address, connection limits, object size, threads, options, user, and ulimit are dependency/resource inputs whose default values require verification from the dependency cookbook.

- **Redis instance on port `6379`**: Redis cache server.
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`; no Unix socket is specified.
  - Key Config: Password is assigned through `requirepass`; store the migrated value in Ansible Vault. PID/runtime directory is `/run/redis`. Redis configuration cleanup removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`. The Redis service is enabled through `redisio::enable`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

No provider file path was supplied in the execution tree for `memcached_instance[memcached]`. Do not invent a provider path; inspect the dependency cookbook separately if provider-level behavior is required.

**Templates:**

No templates are referenced by the supplied execution tree or analyzed recipe content.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

No static files are deployed by the analyzed recipes.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Assigns a one-item Redis server collection containing the Redis instance on port `6379`.
   - Assigns the Redis password through `requirepass`; the source value is hardcoded and must be replaced with an Ansible Vault variable.
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes the Redis installation/configuration recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Executes `ruby_block[fix_redis_config]` to conditionally update `/etc/redis/6379.conf`.
   - Removes complete lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
   - Does not explicitly restart or reload Redis after modifying the configuration.
   - Includes the Redis enablement recipe.

   **Redis collection iteration:**
   - Redis server collection count: `1`
   - Configured item: port `6379`
   - `replicaservestaledata`: `nil`

   The source entries `redisio` and `redisio::enable` were not supplied in the execution tree. Do not assume exact Redis package names, templates, provider behavior, or service unit names until that dependency is inspected.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Requests actions `start` and `enable`.
   - Passes Memcached settings from `node['memcached']`, including memory, TCP and UDP ports, listen address, maximum connections, service user, maximum object size, threads, experimental options, additional CLI options, and ulimit.
   - The supplied structured analysis does not verify the default values for these attributes.
   - No template is rendered by the analyzed recipe.
   - Package installation, user/group creation, service-file creation, log directory creation, and runtime directory creation are not shown in the supplied structured analysis and must be verified separately from the dependency provider.

3. **Redis dependency recipes**:
   - `redisio` is referenced but its recipe file was not supplied.
   - `redisio::enable` is referenced but its recipe file was not supplied.
   - Observable inputs and effects are the Redis server definition on port `6379`, the Redis password, `/run/redis`, `/var/log/redis`, `/etc/redis/6379.conf`, and Redis service enablement.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0` — reported in the source metadata but not verifiable from the supplied structured analysis.
- `redisio`, no version constraint specified — reported in the source metadata but not verifiable from the supplied structured analysis.

**System package dependencies**:

- No system package installation is verified by the supplied structured analysis.
- The exact Redis package is unavailable because the `redisio` dependency recipe was not supplied.
- Do not add package tasks until the dependency cookbooks and target platform are verified.

**Service dependencies**:

- Memcached service: started and enabled through `memcached_instance[memcached]`; exact unit name requires verification.
- Redis service for port `6379`: enabled through `redisio::enable`; exact unit name requires verification.
- No explicit Redis restart or reload is declared by `cache::default`.

**Supported platforms**:

- Ubuntu `>= 18.04` — reported in source metadata but not verifiable from the supplied structured analysis.
- CentOS `>= 7.0` — reported in source metadata but not verifiable from the supplied structured analysis.

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: Redis configuration for server port `6379`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef node attribute assignment
- **Usage context**: Redis client authentication; passed through the Redis configuration generated by `redisio`
- **Migration storage**: Store as an Ansible Vault variable such as `redis_password` and reference it from the Redis configuration.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, secret-related environment variables, database connection strings, TLS certificates, private keys, API tokens, or other credentials were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- `/var/log/memcached` if created by the dependency implementation
- `/var/run/memcached` if created by the dependency implementation
- The Memcached configuration file discovered from the dependency provider or installed package
- The Redis service unit discovered from the installed `redisio` implementation

**Service endpoints to check**:

- Memcached TCP endpoint: configured value from the verified dependency attributes; the commonly expected value is `0.0.0.0:11211`, but this is not verified by the supplied structured analysis.
- Memcached UDP endpoint: configured value from the verified dependency attributes; the commonly expected value is `0.0.0.0:11211`, but this is not verified by the supplied structured analysis.
- Redis TCP endpoint: `127.0.0.1:6379` or the configured Redis listener on port `6379`
- Redis Unix socket: none specified
- Redis PID/runtime directory: `/run/redis`

**Templates rendered**:

- None. Render count: `0`.

**Resource summary**:

- `cookbooks/cache/recipes/default.rb`:
  - `include_recipe 'memcached'`: 1
  - `include_recipe 'redisio'`: 1
  - `directory[/var/log/redis]`: 1
  - `ruby_block[fix_redis_config]`: 1
  - `include_recipe 'redisio::enable'`: 1
- `memcached::default`:
  - `memcached_instance[memcached]`: 1

## Pre-flight checks:

```bash
# Confirm the discovered service units before running service checks.
systemctl list-unit-files | grep -E 'memcached|redis|redis-server'

# Memcached instance: memcached
# Substitute the verified unit name if it differs from memcached.
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Verify the Memcached TCP endpoint after confirming the configured port.
printf "version\r\n" | nc -w 2 127.0.0.1 11211
ss -ltnp | grep ':11211'
ps aux | grep '[m]emcached'

# Verify the Memcached UDP endpoint after confirming the configured port.
ss -lunp | grep ':11211'

# Verify the effective Memcached configuration after locating its config or
# service definition. Confirm verified dependency values for memory, ports,
# listen address, maximum connections, object size, threads, options, user,
# and ulimit.
systemctl cat memcached
systemctl show memcached --property=User,LimitNOFILE

# Verify dependency-created Memcached directories if present.
test -d /var/log/memcached && stat -c '%A %U:%G %n' /var/log/memcached
test -d /var/run/memcached && stat -c '%A %U:%G %n' /var/run/memcached

# Redis instance: port 6379
# Replace the placeholder with the service unit discovered on the target host.
systemctl status <redis-6379-service-unit>
systemctl is-enabled <redis-6379-service-unit>
systemctl is-active <redis-6379-service-unit>

# Verify Redis TCP connectivity.
ss -ltnp | grep ':6379'
ps aux | grep '[r]edis'

# An unauthenticated request should be rejected because requirepass is configured.
redis-cli -p 6379 PING

# Use the Ansible Vault value or another protected source; do not expose the
# password in shell history.
read -s REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD

# Expected authenticated response:
# PONG

# Verify the Redis configuration file and key settings.
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|dir|pidfile)' /etc/redis/6379.conf

# Verify that the five removed directives are not active.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify Redis directories.
stat -c '%A %U:%G %n' /var/log/redis
stat -c '%A %U:%G %n' /run/redis

# Verify Redis logging and startup diagnostics.
grep -E '^(logfile|syslog-enabled|syslog-ident)' /etc/redis/6379.conf
journalctl -u <redis-6379-service-unit> --no-pager -n 50
```