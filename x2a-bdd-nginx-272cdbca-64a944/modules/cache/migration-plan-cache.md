---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook references the external `memcached` and `redisio` cookbooks and contains one local recipe, `cookbooks/cache/recipes/default.rb`. The supplied execution tree confirms only one `directory` resource and one `ruby_block` resource; the dependency recipes and the underlying attribute, resource-property, and credential details are unavailable for independent validation. The plan therefore identifies the reported Redis configuration and password as requiring source confirmation before implementation. Memcached package, service, port, and configuration details cannot be determined from the supplied files.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Reported Redis instance configured through `node['redisio']['servers']`; details require confirmation from the recipe and attributes source.
  - Location/Path: `/etc/redis/6379.conf` reportedly used by the Redis dependency and local cleanup block; not confirmed by the supplied structured analysis
  - Port/Socket: TCP `6379`, reported but not independently validated
  - Key Config: Reported `requirepass` value, `replicaservestaledata: nil`, and removal of replication-related directives; all require source confirmation
  - Log directory: `/var/log/redis`, reported by the local recipe analysis
  - Reported ownership and mode: `redis:redis`, `0755`; not independently validated

- **Memcached dependency instance**: Referenced by `include_recipe 'memcached'`; the dependency implementation is unavailable.
  - Location/Path: Not available
  - Port/Socket: Not available
  - Key Config: Package, service name, configuration path, and port cannot be determined from the supplied execution tree

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

The metadata file was inspected to identify the cookbook description and dependencies, but it is not listed as an executable migration file.

## Module Explanation

The cookbook performs operations in this order:

1. **Memcached dependency reference** (`cookbooks/cache/recipes/default.rb`):
   - Executes `include_recipe 'memcached'`.
   - The referenced dependency recipe is not present in the supplied execution tree.
   - Memcached package names, service names, configuration files, ports, templates, and handlers cannot be specified until the dependency implementation is inspected.

2. **Redis server attribute configuration** (`cookbooks/cache/recipes/default.rb`):
   - The supplied plan reports an assignment to `node.default['redisio']['servers']` containing one Redis server definition.
   - The reported server configuration is port `6379`, a `requirepass` value of `redis_secure_password_123`, and `replicaservestaledata` set to `nil`.
   - These attribute details are not present in the supplied structured validation and must be confirmed from the recipe before migration.
   - The reported password must be stored in Ansible Vault rather than committed as plaintext.
   - No `.each` loop is shown in the local recipe; the one-item server array is expected to be interpreted by the `redisio` dependency.

3. **Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Confirmed local resource type: `directory`.
   - Reported path: `/var/log/redis`.
   - Reported owner: `redis`.
   - Reported group: `redis`.
   - Reported mode: `0755`.
   - Reported recursive creation: enabled.
   - These properties require confirmation from the actual recipe because the structured validation confirms only the resource and its count.
   - Resource count: `directory`: 1.

4. **Redis dependency recipe reference** (`cookbooks/cache/recipes/default.rb`):
   - Executes `include_recipe 'redisio'`.
   - The referenced dependency recipe is not present in the supplied execution tree.
   - Its package names, service resources, templates, configuration rendering behavior, and restart notifications are unavailable.
   - The dependency is expected to consume the Redis server definition, but this behavior must be verified before implementation.

5. **Redis configuration cleanup** (`cookbooks/cache/recipes/default.rb`):
   - Confirmed local resource type: `ruby_block`.
   - Resource name: `fix_redis_config`.
   - Resource count: `ruby_block`: 1.
   - The supplied plan reports that the block conditionally reads `/etc/redis/6379.conf` and removes:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The file path and directive-removal behavior are not present in the supplied structured validation and must be confirmed from the Ruby block before migration.
   - No explicit service restart or reload notification is confirmed for this resource.
   - If confirmed, the Ansible equivalent should run after the Redis dependency configuration and tolerate a missing configuration file.

6. **Redis enablement dependency reference** (`cookbooks/cache/recipes/default.rb`):
   - Executes `include_recipe 'redisio::enable'`.
   - The referenced recipe is not present in the supplied execution tree.
   - Its exact service enablement and startup behavior cannot be determined.
   - The actual Redis service name must be identified before adding Ansible service tasks.

### Resource Summary

Confirmed local resources in `cookbooks/cache/recipes/default.rb`:

- `directory`: 1
  - `/var/log/redis` — reported path; properties require confirmation
- `ruby_block`: 1
  - `fix_redis_config` — reported cleanup behavior requires confirmation

Dependency references, in execution order:

1. `memcached`
2. `redisio`
3. `redisio::enable`

The dependency recipe files are unavailable and are not expanded into package, service, template, or handler resources.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint specified

**System package dependencies**:

- Not determinable from the supplied execution tree.
- The local recipe contains no confirmed `package` resource.
- Do not assume package names such as `redis-server` or `memcached` until the missing dependency recipes or target Ansible role requirements are inspected.

**Service dependencies**:

- Redis service behavior is expected to be provided by `redisio::enable`; the service name is unavailable.
- Memcached service behavior is unavailable because the `memcached` recipe is missing.
- No local `service` resource is confirmed.

## Credentials

**Detection Summary**: 1 credential reported in 1 file; the supplied structured validation does not independently confirm the finding.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext Chef attribute assignment
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the reported Redis instance on port `6379`
- **Validation status**: The structured analysis does not include the attribute assignment or credential finding; confirm against the source before migration.
- **Ansible migration recommendation**:
  - Store the password in Ansible Vault.
  - Render it into the Redis configuration with restrictive permissions.
  - Do not commit the plaintext value to the Ansible repository.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings were identified in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf` — reported Redis configuration path; confirm before use
- `/var/log/redis/` — reported Redis log directory; confirm properties before use
- The missing `memcached` dependency recipe
- The missing `redisio` dependency recipe
- The missing `redisio::enable` dependency recipe

**Service endpoints to check**:

- Redis TCP port `6379` — reported; confirm from source and runtime configuration
- Memcached port — not determinable from the supplied execution tree
- Unix sockets — none identified

**Templates rendered**:

- None identified in the supplied execution tree
- Render count: `0` confirmed local templates

## Pre-flight checks

### Redis instance on port 6379

Confirm the actual service name before running service-specific checks:

```bash
systemctl list-unit-files | grep -E 'redis|6379'
systemctl --type=service --all | grep -E 'redis|6379'
```

After identifying the actual Redis service name:

```bash
systemctl status <actual-redis-service-name>
systemctl is-enabled <actual-redis-service-name>
systemctl is-active <actual-redis-service-name>
```

Check the reported Redis endpoint:

```bash
ss -tlnp | grep ':6379'
redis-cli -p 6379 -a '<redis-password-from-vault>' PING
```

Expected response when the reported authentication configuration is confirmed:

```text
PONG
```

Check authentication behavior:

```bash
redis-cli -p 6379 PING
redis-cli -p 6379 -a '<redis-password-from-vault>' PING
```

The unauthenticated command should be rejected only if `requirepass` is confirmed and active. The authenticated command should return `PONG`.

If the configuration path and cleanup behavior are confirmed, validate them with:

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

The targeted directive check should produce no active matching lines only if the reported Ruby block behavior is confirmed.

Check the reported log directory:

```bash
test -d /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis
ls -la /var/log/redis
```

Expected properties, subject to source confirmation:

```text
redis:redis 755 /var/log/redis
```

### Memcached dependency instance

The Memcached service and port are unavailable from the supplied files. Inspect the dependency implementation before adding fixed endpoint checks:

```bash
systemctl list-unit-files | grep memcached
systemctl --type=service --all | grep memcached
ss -tlnp | grep memcached
```

Do not assume a Memcached package, service name, configuration path, or port until the missing dependency recipe confirms them.