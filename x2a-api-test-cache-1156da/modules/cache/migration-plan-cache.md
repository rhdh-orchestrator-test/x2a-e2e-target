---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The locally analyzed recipe configures one Redis instance on port `6379`, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and attempts to enable Redis. It also attempts to include Memcached, but the referenced recipe is unavailable in the supplied execution tree. Redis authentication is currently hardcoded and must be migrated to Ansible Vault or another protected secret source.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis listener on port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Redis authentication enabled through `requirepass`; `replicaservestaledata` is explicitly unset; selected replication directives are removed after configuration generation
  - Log directory: `/var/log/redis`
  - Service enablement: Attempted through the unavailable `redisio::enable` recipe

No Redis replication peers, additional Redis ports, databases, or Unix sockets are configured locally.

- **Memcached**: External cache service inclusion only
  - Location/Path: Not available
  - Port/Socket: Not available
  - Key Config: The recipe attempts to include `memcached`, but the `memcached` recipe is not present in the supplied execution tree
  - Package, service, configuration path, and template: Cannot be determined from the supplied cookbook

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

The following files are not present in the supplied directory listing or execution tree:

- `recipes/memcached.rb`
- `recipes/redisio.rb`
- `recipes/enable.rb`
- Any dependency cookbook recipe or provider
- Any template or static file

## Module Explanation

The cookbook performs operations in this order:

1. **cache::default** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - The execution tree reports `memcached Recipe file not found`.
   - Does not locally install or configure Memcached.
   - Requires the target Ansible implementation to determine whether Memcached should be installed and configured separately.
   - Defines one Redis server entry:
     - Port: `6379`
     - Authentication password: currently hardcoded as `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Attempts to include the external `redisio` recipe.
   - The execution tree reports `redisio Recipe file not found`.
   - The external `redisio` implementation is expected to consume the Redis server definition and generate `/etc/redis/6379.conf`.
   - Executes `ruby_block[fix_redis_config]` after the Redis recipe inclusion:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Removes complete lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - In Ansible, implement this with separate `ansible.builtin.lineinfile` tasks using `state: absent`, conditioned on the configuration file existing.
     - The supplied Chef recipe does not explicitly notify a service restart or reload.
   - Attempts to include `redisio::enable`.
   - The execution tree reports `redisio::enable Recipe file not found`.
   - The Ansible migration must enable and start the Redis service after configuration generation and cleanup, using the service name resolved from the target distribution or external `redisio` implementation.
   - No `.each` loops are present in the supplied recipe.

## Dependencies

**External cookbook dependencies**:

- `memcached (~> 6.0)`
- `redisio`

**System package dependencies**:

- No local `package` resources are present.
- Exact package names cannot be verified from the supplied files.
- Package installation is expected to be handled by the external `memcached` and `redisio` implementations or by the target Ansible roles.

**Service dependencies**:

- Redis service enablement is attempted through the unavailable `redisio::enable` recipe.
- Memcached service management is attempted indirectly through the unavailable `memcached` recipe.
- Exact service unit names cannot be determined from the supplied files.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Current value in Chef**: `redis_secure_password_123`
- **Usage context**: Redis client authentication through the `requirepass` setting for the Redis listener on port `6379`
- **Ansible handling**:
  - Store the password in Ansible Vault, such as a vaulted variable named `redis_password`.
  - Use the vaulted variable when rendering or configuring `/etc/redis/6379.conf`.
  - Do not place the password in public inventory, role defaults, Git-managed unencrypted variables, command-line arguments, or unencrypted templates.
  - Avoid exposing the password in logs or validation output.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis TCP port `6379`
- No Redis Unix socket is configured locally.
- No Memcached endpoint can be identified from the supplied cookbook files.

**Templates rendered**:

- None. No template files are present in the supplied execution tree.

**Static files deployed**:

- None.

**Configuration transformations to verify**:

- `/etc/redis/6379.conf` exists after Redis configuration generation.
- The Redis configuration contains the equivalent of `port 6379`.
- Redis authentication remains configured through a securely supplied password.
- No active lines beginning with the following directives remain:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.

## Pre-flight checks

Run these checks after the Ansible role completes.

### Redis instance on port 6379

Confirm the service name from the target distribution or external `redisio` implementation, then run:

```bash
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>
```

Expected result:

- The Redis service is active.
- The Redis service is enabled at boot.

Verify the listener:

```bash
ss -tlnp | grep ':6379'
```

Expected result:

- A Redis process is listening on TCP port `6379`.

Verify unauthenticated access is rejected:

```bash
redis-cli -h 127.0.0.1 -p 6379 PING
```

Expected result:

- The command is rejected with an authentication error, assuming unauthenticated access is not otherwise permitted.

Verify authenticated access using a protected shell variable:

```bash
REDISCLI_AUTH='<vaulted-password>' redis-cli -h 127.0.0.1 -p 6379 PING
```

Expected result:

```text
PONG
```

Validate the Redis configuration:

```bash
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Verify individually:

- `port 6379` is present, or the equivalent configuration is active.
- A Redis password is configured without exposing its value.
- No active lines beginning with the five removed directives remain.
- If removed directives are commented rather than deleted, they are inactive and cannot affect runtime behavior.

Validate the log directory:

```bash
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis
```

Expected result:

```text
drwxr-xr-x redis redis /var/log/redis
```

Run an operational Redis command:

```bash
REDISCLI_AUTH='<vaulted-password>' redis-cli -h 127.0.0.1 -p 6379 INFO server
```

Expected result:

- Redis returns server information successfully for the listener on port `6379`.

Review service logs:

```bash
journalctl -u <redis-service-name> --no-pager -n 100
```

Check for:

- Configuration parse errors
- Authentication errors caused by malformed configuration
- Failure to bind port `6379`
- Permission errors writing under `/var/log/redis`

### Memcached dependency

The cookbook attempts to include Memcached, but the `memcached` recipe is unavailable and no Memcached configuration is present. No exact endpoint or service check can be specified from the supplied source.

Before finalizing the Ansible migration, obtain the external Memcached recipe or deployment specification and verify:

- Installed package name
- Service unit name
- Listening port
- Bind address
- Configuration file path
- Authentication or SASL settings, if applicable
- Memcached service status and connectivity individually