---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook references the `memcached` and `redisio` cookbooks and directly executes `cookbooks/cache/recipes/default.rb`. The supplied execution-tree analysis confirms inclusion of `memcached`, `redisio`, and `redisio::enable`, plus one `directory` resource and one `ruby_block`. The Redis port, configuration path, log-directory properties, cleanup directives, and hardcoded password described in the original plan are not validated by the supplied structured analysis and must be confirmed against the source recipe before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379** *(source-reported; not validated by the supplied structured analysis)*
  - Location/Path: `/etc/redis/6379.conf` *(unverified)*
  - Port/Socket: TCP port `6379` *(unverified)*
  - Key Config: Redis server settings are reportedly assigned through `node['redisio']['servers']`; the exact assignment and configuration values require confirmation from `cookbooks/cache/recipes/default.rb`.
  - Log directory: `/var/log/redis` *(the directory resource is validated; ownership and mode are unverified)*
  - Reported owner/group: `redis:redis` *(unverified)*
  - Reported mode: `0755` *(unverified)*

- **Memcached instance** *(dependency referenced; no instance-specific configuration validated)*
  - Location/Path: Not specified
  - Port/Socket: Not specified
  - Key Config: Package, service, port, configuration path, and runtime settings are delegated to the unavailable `memcached` dependency recipe.

## File Structure

Only the recipe shown in the supplied execution tree is listed. Referenced dependency recipes are unavailable and are not included as cookbook files.

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

## Module Explanation

The cookbook performs operations in the following exact execution order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` recipe.
     - Execution-tree status: `memcached` recipe file not found.
   - Defines Redis server configuration through `node['redisio']['servers']`.
     - One Redis item for port `6379` is reported by the original plan, but the exact assignment is not present in the supplied structured analysis and must be verified.
     - The reported `requirepass` value and `replicaservestaledata` setting are unverified.
   - Creates `directory[/var/log/redis]`.
     - This resource is confirmed by the structured analysis.
     - The reported owner `redis`, group `redis`, mode `0755`, and recursive setting require source confirmation.
   - Includes the `redisio` recipe.
     - Execution-tree status: `redisio` recipe file not found.
   - Executes `ruby_block[fix_redis_config]`.
     - The existence of this resource is confirmed.
     - Its reported file path, matching patterns, rewrite behavior, and missing-file behavior are not described in the supplied structured analysis and require source confirmation.
   - Includes `redisio::enable`.
     - Execution-tree status: `redisio::enable` recipe file not found.

**Execution-tree resource count:**

- `directory`: 1
- `ruby_block`: 1
- `include_recipe` operations: 3
  - `memcached`
  - `redisio`
  - `redisio::enable`

No independently confirmed `.each` loop contents are available in the structured analysis. The original plan reports one Redis server item, named **Redis server on port 6379**, which must be verified against the source recipe before implementation.

### Ansible implementation guidance

A semantically equivalent Ansible role should preserve the confirmed and source-reported execution order:

1. Integrate or invoke the Memcached dependency role if that dependency is available.
2. Define the Redis server settings for port `6379` after confirming the source assignment.
3. Create `/var/log/redis` with the source-confirmed owner, group, mode, and recursion settings.
4. Integrate or invoke the Redis installation and configuration dependency role.
5. Apply the Redis configuration cleanup only after confirming the `ruby_block` implementation.
6. Enable the Redis service through the equivalent Redis service-management task.

The unavailable dependency recipes must be inspected before adding package names, service names, templates, or additional configuration tasks. Do not create a Redis template based solely on the supplied execution-tree analysis.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- None confirmed in the supplied cookbook execution tree.
- Package names must be obtained from the unavailable `memcached` and `redisio` dependency recipes before migration.

**Service dependencies**:

- Memcached service management is delegated to the unavailable `memcached` recipe.
- Redis service installation, configuration, and enablement are delegated to the unavailable `redisio` and `redisio::enable` recipes.
- Redis TCP port `6379` is reported by the original plan but is not validated by the supplied structured analysis.

## Credentials

**Detection Summary**: No credentials were identified by the supplied structured analysis. The original plan’s claim of one hardcoded Redis password is unverified.

**Source**:

- **Provider**: None validated
- **URL**: None detected
- **Path**: `cookbooks/cache/recipes/default.rb` must be inspected to confirm or reject the reported credential claim.

### Reported Redis authentication password

- **Variable**: Reported as `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as a hardcoded plaintext Chef attribute assignment; not validated
- **Value currently reported**: `redis_secure_password_123`; not validated
- **Usage context**: Reported Redis authentication for the server on port `6379`; not validated
- **Ansible migration**: If confirmed in the source recipe, store the password in Ansible Vault, AAP credentials, or another protected secret backend. Do not place it in plaintext in `defaults/main.yml`, an unencrypted variables file, or a committed template.

No validated `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret reference, TLS certificate, private key, database connection string, or external vault URL was identified.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf` *(reported; unverified)*
- `/var/log/redis` *(directory resource confirmed)*

**Service endpoints to check**:

- Redis TCP port `6379` *(reported; unverified)*
- Unix sockets: none specified
- Memcached port: not specified
- Network interface binding: not specified

**Templates rendered**:

- None confirmed
- Render count: `0`

**Static files deployed**:

- None

## Pre-flight checks

```bash
# Confirm the migrated recipe and dependency roles are available
test -f cookbooks/cache/recipes/default.rb
```

```bash
# Redis server status for the reported Redis server on port 6379
systemctl status redis
systemctl status redis-server
```

Use the service name that exists on the target operating system. The supplied cookbook does not expose the service name because service management is delegated to the unavailable `redisio` dependency.

```bash
# Verify the Redis process associated with the reported port
ps aux | grep '[r]edis-server'
ss -ltnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN
```

```bash
# Verify the reported Redis configuration path
test -f /etc/redis/6379.conf
```

```bash
# Verify the confirmed Redis log-directory resource
test -d /var/log/redis
stat -c '%A %U:%G %n' /var/log/redis
```

The expected ownership, group, and mode must be confirmed from the source recipe before treating `redis:redis` and `0755` as required values.

```bash
# If the source recipe confirms the reported cleanup behavior,
# verify that the cleanup directives are absent
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected result after confirmed cleanup:
# no matching lines
```

```bash
# Test Redis connectivity if port 6379 and Redis authentication
# are confirmed by the source recipe
read -s REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD
# Expected output:
# PONG
```

```bash
# Check Redis runtime information after connectivity is confirmed
read -s REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO clients
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO memory
unset REDIS_PASSWORD
```

```bash
# Check recent Redis logs using the service name available on the target
journalctl -u redis --since "15 minutes ago"
journalctl -u redis-server --since "15 minutes ago"
```

Memcached is referenced but unavailable in the supplied execution tree. Its package name, service name, port, configuration path, and health-check command must be confirmed from the actual `memcached` dependency before adding Memcached-specific migration or validation tasks.