---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures caching services through the external `memcached` and `redisio` cookbooks. The analyzed recipe includes Memcached, creates `/var/log/redis`, defines one Redis instance on port `6379` with password authentication, applies Redis configuration through `redisio`, removes five replication-related directives from `/etc/redis/6379.conf`, and enables Redis through `redisio::enable`. The dependency recipes are unavailable, so their package names, service names, templates, and exact Memcached settings must be confirmed separately before completing the Ansible migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Log directory: `/var/log/redis`
  - Key Config: Password authentication using the secret-managed equivalent of `redis_secure_password_123`; `replicaservestaledata` is set to `nil`
  - Post-configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`

- **Memcached dependency instance**: Memcached service included through the external `memcached` recipe
  - Location/Path: Not available in the supplied cookbook
  - Port/Socket: Not specified
  - Key Config: Package, service name, configuration path, listening port, authentication, and startup options must be obtained from the `memcached` dependency implementation or confirmed target-platform defaults

Supported platforms identified by the cookbook metadata are Ubuntu `>= 18.04` and CentOS `>= 7.0`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are shown or used by the supplied execution tree.

**Templates:**
```text
```

No templates are shown or rendered by the supplied execution tree.

**Attributes:**
```text
```

No attribute files are shown. The Redis configuration is assigned inline in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe first.
   - Defines one Redis server entry with port `6379`, password authentication, and `replicaservestaledata` set to `nil`.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Includes the external `redisio` recipe to apply the Redis server configuration.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` when the file exists.
   - Includes `redisio::enable` to enable Redis at boot and start the service.

### Included dependency recipes

- **memcached** (`external dependency; source unavailable`):
  - Included before the Redis log directory is created.
  - Its package installation, configuration, service name, listening port, and startup options are not present in the supplied execution tree.
  - The equivalent Ansible Memcached implementation must be supplied only after the dependency behavior is confirmed.

- **redisio** (`external dependency; source unavailable`):
  - Included after `/var/log/redis` is created.
  - Applies the single Redis server definition:
    - Redis server on port `6379`
    - Password authentication
    - `replicaservestaledata: nil`
  - The dependency is expected to create or manage `/etc/redis/6379.conf`, but its package names, templates, and service names are unavailable.

- **redisio::enable** (`external dependency; source unavailable`):
  - Included after Redis configuration cleanup.
  - Enables the Redis service at boot and ensures it is started.
  - The exact systemd unit name must be confirmed from the source dependency or target operating system.

### Redis server collection iteration

The recipe defines one server collection item and therefore runs one Redis configuration iteration:

- **Redis server on port `6379`**
  - Port: `6379`
  - Password: `redis_secure_password_123` in the source cookbook; migrate through approved secret storage
  - `replicaservestaledata`: `nil`

### Directory resource

The recipe creates:

```ruby
directory '/var/log/redis'
```

Configuration:

- Owner: `redis`
- Group: `redis`
- Mode: `0755`
- Recursive creation: enabled

Ansible equivalent: `ansible.builtin.file` with `state: directory`.

### Redis configuration cleanup

The recipe executes `ruby_block[fix_redis_config]` against:

```text
/etc/redis/6379.conf
```

Behavior:

1. Checks whether `/etc/redis/6379.conf` exists.
2. Makes no change if the file does not exist.
3. Reads the file when it exists.
4. Removes complete lines beginning with:
   - `replica-serve-stale-data`
   - `replica-read-only`
   - `repl-ping-replica-period`
   - `client-output-buffer-limit`
   - `replica-priority`
5. Writes the modified contents back to the same path.

Ansible should use `ansible.builtin.replace` or controlled configuration rendering while preserving the no-failure behavior when the file is absent. The supplied recipe does not declare a service notification.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, any version
- `redisio::enable`, a recipe within `redisio`

**System package dependencies**:

No package names are directly declared or verifiable in the supplied cookbook. Package names must be obtained from the missing dependency recipes or selected and verified for the target distribution. Do not assume that `redis-server` or `memcached` is installed by `cookbooks/cache/recipes/default.rb`.

**Service dependencies**:

- Memcached service behavior is provided by the unavailable `memcached` recipe.
- Redis server configuration is provided by the unavailable `redisio` recipe.
- Redis enablement and startup are provided by the unavailable `redisio::enable` recipe.
- Exact systemd unit names are not present in the analyzed files.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in a Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded inline Chef attribute
- **Detected value**: `redis_secure_password_123`
- **Usage context**: Redis password authentication for the Redis server on port `6379`

The migrated value must be stored in Ansible Vault, AAP credentials, or another approved secret-management system. It must not be placed directly in Ansible tasks or committed variable files. The secret-managed value must be passed to the Redis configuration and preserve password authentication behavior.

No Chef data bags, encrypted data bags, Chef Vault items, CyberArk integrations, Conjur variables, environment-variable secrets, TLS certificates, private keys, database connection strings, or additional credentials were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis server on port `6379`
- Memcached dependency endpoint: port not specified
- Unix sockets: none specified
- Network bind address: not specified

**Templates rendered**:

- None; no templates are shown or rendered by the supplied execution tree

**Configuration directives to verify**:

- Redis port: `6379`
- Redis password authentication: enabled through the migrated secret
- Removed when present:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks:

Confirm the exact Redis and Memcached service names and the Memcached port from the dependency implementations or target operating system before running service checks.

### Redis server on port 6379

```bash
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
```

If the target system uses an instance-specific Redis unit, replace `redis` with the confirmed unit corresponding to port `6379`.

Validate the Redis configuration file:

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected results:

- `/etc/redis/6379.conf` exists.
- The configuration identifies port `6379`.
- Password authentication is configured with the secret-managed value.
- The five removed directives are absent after cleanup when they existed before migration.

Validate the configuration using the supported command for the installed Redis version:

```bash
redis-server /etc/redis/6379.conf --test-memory 2
```

Use the target distribution’s supported Redis validation command if this command is not appropriate for the installed version.

Test authenticated connectivity without placing the password directly in shell history:

```bash
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 PING
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 INFO server
```

Expected results:

- `PING` returns `PONG`.
- `INFO server` returns Redis server information.

Verify that unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication error rather than `PONG`.

Verify the Redis listener:

```bash
ss -tlnp | grep ':6379'
netstat -tulpn 2>/dev/null | grep ':6379'
lsof -nP -iTCP:6379 -sTCP:LISTEN
```

Verify the Redis log directory:

```bash
test -d /var/log/redis
stat -c '%U %G %a %n' /var/log/redis
ls -la /var/log/redis
```

Expected ownership and permissions:

```text
redis redis 755 /var/log/redis
```

Check Redis logs using the confirmed service unit:

```bash
journalctl -u redis --no-pager -n 100
journalctl -u redis --no-pager -n 100 | grep -Ei 'error|fatal|fail|warning'
```

### Memcached dependency instance

The supplied cookbook does not identify the Memcached service name, package, configuration path, port, or socket. After confirming those values from the `memcached` dependency implementation, run:

```bash
systemctl status <confirmed-memcached-service>
systemctl is-enabled <confirmed-memcached-service>
systemctl is-active <confirmed-memcached-service>
ss -tlnp | grep ':<confirmed-memcached-port>'
```

Do not hardcode a Memcached port or service name until it has been verified.

### Execution order verification

Confirm that the migrated tasks preserve this order:

1. Include or implement Memcached dependency setup.
2. Create `/var/log/redis`.
3. Apply the Redis server configuration for the Redis server on port `6379`.
4. Remove the selected directives from `/etc/redis/6379.conf`.
5. Enable and start Redis through the equivalent of `redisio::enable`.