---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a Redis instance on port `6379` and includes external `memcached` and `redisio` dependencies. The local recipe creates `/var/log/redis`, defines Redis authentication and server settings, removes selected replication-related directives from `/etc/redis/6379.conf`, and attempts to enable Redis. The dependency recipe implementations are unavailable, so their package names, service names, templates, ports, and startup behavior require confirmation before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-6379**: Redis cache server configured through `redisio`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is configured; `replicaservestaledata` is set to `nil`; selected replication directives are removed after configuration
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Authentication password in source: `redis_secure_password_123`  
    This must be migrated to Ansible Vault or an approved secret mechanism.

- **memcached**: External Memcached dependency included by the cookbook
  - Location/Path: Not determinable from the supplied execution tree
  - Port/Socket: Not determinable from the supplied execution tree
  - Key Config: The external `memcached` recipe is included, but its implementation is unavailable. Package, service, configuration path, and port require confirmation from the dependency cookbook.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

```text
None shown in the execution tree.
```

**Templates:**

```text
None shown in the execution tree.
```

**Attributes:**

```text
None shown in the execution tree.
```

**Files:**

```text
None shown in the execution tree.
```

The following dependency recipe paths are referenced conceptually but are not files in the supplied execution tree:

- `memcached` — recipe file not found
- `redisio` — recipe file not found
- `redisio::enable` — recipe file not found

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - The `memcached` dependency recipe is unavailable in the analyzed execution tree; its package, service, port, configuration path, and settings cannot be asserted locally.
   - Assigns one Redis server definition to `node.default['redisio']['servers']`:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation enabled
   - Attempts to include the external `redisio` recipe.
   - Runs `ruby_block[fix_redis_config]`.
   - Attempts to include `redisio::enable`.

   **Resource: `directory[/var/log/redis]`**
   - Creates `/var/log/redis`.
   - Uses owner `redis`, group `redis`, and mode `0755`.
   - Recursive creation is enabled.
   - Resource count: `directory` (1).

   **Resource: `ruby_block[fix_redis_config]`**
   - Targets `/etc/redis/6379.conf`.
   - Does nothing when the configuration file is absent.
   - Reads the file when it exists.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Rewrites the modified content to `/etc/redis/6379.conf`.
   - Resource count: `ruby_block` (1).
   - The Ansible equivalent should be idempotent and should not fail when the file is absent.

   **Include: `memcached`**
   - External dependency recipe.
   - Recipe file unavailable in the execution tree.

   **Include: `redisio`**
   - External dependency recipe.
   - Recipe file unavailable in the execution tree.
   - Package installation, configuration rendering, Redis service creation, and startup behavior cannot be determined locally.

   **Include: `redisio::enable`**
   - External dependency recipe.
   - Recipe file unavailable in the execution tree.
   - Exact service name, enablement behavior, startup behavior, and notification ordering require confirmation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package resources are present in `cookbooks/cache/recipes/default.rb`.
- Package names from the unavailable `memcached` and `redisio` dependency recipes are not verified and must be confirmed before migration.

**Service dependencies**:

- Redis is intended to be enabled through `redisio::enable`.
- The exact Redis systemd service name is not available from the supplied files.
- No local Chef `service` resource is present.
- Memcached service behavior and service name are unavailable because the dependency recipe is missing.

## Credentials

**Detection Summary**: 1 hardcoded credential documented in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected
  - **Secret location**: `node.default['redisio']['servers'][0]['requirepass']`

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis `requirepass` authentication for `redis-6379`
- **Migration handling**:
  - Store the password in Ansible Vault or an approved AAP credential/secrets mechanism.
  - Do not copy the plaintext value into a normal role variable.
  - Use `no_log: true` for tasks that handle the secret.
  - Ensure rendered Redis configuration and task output do not expose the password.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database connection strings, or additional credential namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- `redis-6379`: TCP port `6379`
- `memcached`: Port not determinable from the supplied execution tree
- Unix sockets: None specified
- Network interface binding: Not specified

**Configuration directives to verify in `/etc/redis/6379.conf`**:

- `replica-serve-stale-data` is absent
- `replica-read-only` is absent
- `repl-ping-replica-period` is absent
- `client-output-buffer-limit` is absent
- `replica-priority` is absent

**Templates rendered**:

- None rendered by the analyzed local cookbook
- Render count: `0`

## Pre-flight checks

```bash
# Confirm the cookbook recipe is present
test -f cookbooks/cache/recipes/default.rb

# Identify Redis-related service units before selecting the Ansible service name
systemctl list-unit-files | grep -E 'redis|redis-server'

# Check the commonly used Redis service names
systemctl status redis-server
systemctl status redis

# Confirm the Redis process for instance redis-6379
pgrep -a redis-server

# Confirm the Redis configuration file for instance redis-6379
test -f /etc/redis/6379.conf && echo "Redis configuration exists"

# Verify the configured port for instance redis-6379
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' \
  /etc/redis/6379.conf

# Verify unwanted directives are absent for instance redis-6379
grep -E '^[[:space:]]*(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf \
  && echo "Unexpected directive found" \
  || echo "Unwanted directives are absent"

# Verify the Redis log directory for instance redis-6379
stat -c '%A %U:%G %n' /var/log/redis

# Expected directory properties:
# drwxr-xr-x redis:redis /var/log/redis

# Authenticate without placing the plaintext password in command history
REDISCLI_AUTH='<redis-password-from-vault>' redis-cli -p 6379 PING

# Expected response:
# PONG

# Check Redis server information for instance redis-6379
REDISCLI_AUTH='<redis-password-from-vault>' redis-cli -p 6379 INFO server

# Verify the running Redis port for instance redis-6379
REDISCLI_AUTH='<redis-password-from-vault>' redis-cli -p 6379 CONFIG GET port

# Expected port value:
# 6379

# Verify that instance redis-6379 is listening on TCP port 6379
ss -ltnp | grep ':6379'

# Inspect the configured Redis log destination
grep -E '^[[:space:]]*logfile[[:space:]]+' /etc/redis/6379.conf

# Inspect logs for the discovered Redis service
journalctl -u redis-server --no-pager -n 50
journalctl -u redis --no-pager -n 50

# Memcached validation requires the external cookbook or target distribution
# defaults to be inspected first. Do not assume a service name or port.
systemctl list-unit-files | grep -i memcached
systemctl status memcached
ss -ltnp | grep -i memcached
```