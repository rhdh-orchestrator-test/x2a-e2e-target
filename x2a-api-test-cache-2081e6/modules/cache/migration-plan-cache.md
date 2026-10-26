---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer containing Memcached and one Redis instance on port `6379`. The local recipe is `cookbooks/cache/recipes/default.rb`; it invokes the external `memcached`, `redisio`, and `redisio::enable` recipes, none of which are present in the supplied execution tree. Redis uses password authentication, creates `/var/log/redis`, manages `/etc/redis/6379.conf`, and removes five replication-related directive families. The Redis password must be migrated from the hardcoded Chef value into Ansible Vault or an approved secret provider.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication enabled; `replicaservestaledata` explicitly set to `nil`; replication-related directives removed after configuration; log directory `/var/log/redis` owned by `redis:redis` with mode `0755`

- **Memcached**: Memcached cache service included through the external `memcached` cookbook
  - Location/Path: Defined by the external cookbook; unavailable locally
  - Port/Socket: Not specified in the supplied execution tree
  - Key Config: Package name, configuration path, service name, port, and restart behavior must be obtained from the selected Memcached implementation. The dependency version constraint is `~> 6.0`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only the local recipe shown in the execution tree is listed. The dependency recipe files are referenced by `include_recipe`, but are not local cookbook files.

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

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe before Redis configuration.
   - The `memcached` dependency recipe is not present in the supplied execution tree.
   - The Ansible migration must invoke the selected Memcached role or collection implementation.
   - Memcached package, configuration path, service name, port, and restart behavior must be confirmed from that implementation rather than inferred from the local recipe.

2. **default — Redis server definition** (`cookbooks/cache/recipes/default.rb`):
   - Assigns exactly one Redis server to `node.default['redisio']['servers']`.
   - Configured item:
     - Port: `'6379'`
     - `requirepass`: `'redis_secure_password_123'`
     - `replicaservestaledata`: `nil`
   - The Ansible implementation must represent one Redis instance named **Redis port 6379**.
   - The Redis password must be stored in Ansible Vault or an approved secret provider and must not be committed as plaintext.
   - Preserve the explicit null or unset value for `replicaservestaledata` when supported by the target Redis role.

3. **default — Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Uses owner `redis`.
   - Uses group `redis`.
   - Uses mode `0755`.
   - Creates parent directories as needed.
   - Resource count: one `directory` resource.

4. **default — Redis dependency** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe after defining the Redis server collection and creating the log directory.
   - The `redisio` dependency recipe is not present in the supplied execution tree.
   - The Ansible Redis implementation must consume the Redis port `6379` definition.
   - It must generate or manage `/etc/redis/6379.conf`.
   - It must install and configure Redis according to the selected implementation.
   - The exact package and service resource behavior must be confirmed from the selected implementation.

5. **default — Redis configuration cleanup** (`cookbooks/cache/recipes/default.rb`):
   - Executes the `ruby_block` resource `fix_redis_config`.
   - Operates on `/etc/redis/6379.conf`.
   - If the file exists, removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Does nothing when the configuration file is absent.
   - The Ansible equivalent should remove matching directive lines idempotently and safely handle a missing file.
   - Resource count: one `ruby_block` resource.
   - No service notification is attached to the Chef resource. The Ansible implementation must explicitly determine whether Redis requires a restart or reload after the file changes.

6. **default — Redis enablement** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio::enable` recipe after Redis configuration cleanup.
   - The `redisio::enable` dependency recipe is not present in the supplied execution tree.
   - Enables the Redis service for **Redis port 6379** at boot.
   - Starts the service after configuration has been deployed and corrected.
   - The exact systemd service name must be confirmed from the selected Redis implementation and target operating system.

**Execution order**:

1. Invoke the Memcached implementation.
2. Define exactly one Redis server item: **Redis port 6379**.
3. Create `/var/log/redis` with owner `redis`, group `redis`, and mode `0755`.
4. Invoke the Redis installation and configuration implementation.
5. Remove the five specified directive families from `/etc/redis/6379.conf` when the file exists.
6. Enable and start the Redis service for **Redis port 6379**.
7. Restart or reload Redis through an explicit handler if the target implementation requires it.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`; recipe file not found locally
- `redisio`, with no version constraint shown; recipe file not found locally
- `redisio::enable`; recipe file not found locally

**System package dependencies**:

- Memcached package: not determinable from the supplied local recipe; confirm from the selected Ansible implementation and target distribution
- Redis package: not determinable from the supplied local recipe; confirm from the selected Ansible implementation and target distribution

No unverified package names should be added to the migration.

**Service dependencies**:

- Memcached service: provided by the external `memcached` implementation; exact service name unavailable
- Redis service for **Redis port 6379**: provided and enabled by the external `redisio::enable` implementation; exact service name unavailable

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis password authentication for **Redis port 6379**
- **Migration handling**:
  - Move the value to Ansible Vault or the approved organizational secret provider.
  - Reference the protected variable from the Redis configuration role or template.
  - Do not commit the literal password to the Ansible repository.
  - Supply the password securely during authentication tests without printing it.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur calls, environment-variable secrets, TLS certificate references, or database connection credentials were detected.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

The external Memcached and Redis implementations may create additional files, but their paths are unavailable in the supplied execution tree.

**Service endpoints to check**:

- Redis port for **Redis port 6379**: TCP `6379`
- Memcached port: not specified by the available cookbook data
- Unix sockets: none specified
- Network bind address: not specified

**Templates rendered**:

- Local cookbook templates: none
- Known local template render count: `0`
- External Redis templates: unavailable and require separate audit
- External Memcached templates: unavailable and require separate audit

## Pre-flight checks

### Redis port 6379

Confirm the service name supplied by the selected Redis implementation:

```bash
systemctl status <redis-service-for-port-6379>
systemctl is-enabled <redis-service-for-port-6379>
systemctl is-active <redis-service-for-port-6379>
```

Expected result: the Redis service for **Redis port 6379** is enabled and active.

Check the endpoint:

```bash
ss -ltnp | grep ':6379'
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 PING
```

Expected result:

```text
PONG
```

Verify authentication is enforced:

```bash
redis-cli -p 6379 PING
```

Expected result: Redis reports that authentication is required.

Verify authenticated access:

```bash
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 PING
```

Expected result:

```text
PONG
```

Validate the Redis configuration:

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf
```

Confirm that:

- The configured port is `6379`.
- Password authentication is enabled.
- The password is not exposed in migration logs or command output.

Confirm the cleanup directives are absent:

```bash
if test -f /etc/redis/6379.conf; then
  ! grep -E '^replica-serve-stale-data' /etc/redis/6379.conf
  ! grep -E '^replica-read-only' /etc/redis/6379.conf
  ! grep -E '^repl-ping-replica-period' /etc/redis/6379.conf
  ! grep -E '^client-output-buffer-limit' /etc/redis/6379.conf
  ! grep -E '^replica-priority' /etc/redis/6379.conf
fi
```

Validate the log directory:

```bash
stat -c '%A %U:%G %n' /var/log/redis
```

Expected result:

```text
drwxr-xr-x redis:redis /var/log/redis
```

Review Redis logs:

```bash
journalctl -u <redis-service-for-port-6379> --no-pager -n 100
```

Check for successful startup, absence of configuration parse errors, absence of `/var/log/redis` permission errors, and successful authentication configuration.

### Memcached

Obtain the Memcached service name and port from the selected Ansible Memcached implementation before running endpoint checks.

```bash
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>
ss -ltnp | grep ':<memcached-port>'
```

Perform the implementation-appropriate Memcached health check against the confirmed endpoint. Do not assume a Memcached port or service name that is not defined by the dependency implementation.