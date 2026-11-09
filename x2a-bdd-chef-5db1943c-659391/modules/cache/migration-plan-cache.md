---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures a Redis cache instance on TCP port `6379` and includes Memcached as an external dependency. The local recipe sets Redis authentication, uses `/run/redis` for PID files, creates `/var/log/redis` with Redis ownership and mode `0755`, removes selected replication-related directives from `/etc/redis/6379.conf`, and enables Redis through the external `redisio` cookbook. The Memcached and RedisIO implementations are not present in the analyzed cookbook tree, so their packages, service names, ports, and configuration paths must be validated separately.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance configured through the external `redisio` cookbook
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - PID directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Service account: `redis`
  - Log directory mode: `0755`
  - Authentication: `requirepass` set to `redis_secure_password_123`
  - Key Config:
    - `port`: `6379`
    - `replicaservestaledata`: `nil`
    - Removes `replica-serve-stale-data`
    - Removes `replica-read-only`
    - Removes `repl-ping-replica-period`
    - Removes `client-output-buffer-limit`
    - Removes `replica-priority`

- **Memcached dependency**: External dependency referenced by the recipe
  - Location/Path: Not available in the local execution tree
  - Port/Socket: Not defined in the analyzed files
  - Key Config: The `memcached` recipe is included, but its implementation is unavailable. Do not infer a package, port, configuration path, or service name from the dependency name alone.

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

The cookbook metadata file was inspected to identify dependencies, but it is not listed here because the supplied execution-tree file list contains only `cookbooks/cache/recipes/default.rb`.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe before configuring Redis.
   - The local execution tree does not contain the `memcached` recipe implementation.
   - Preserve this as the first dependency stage in Ansible.
   - Obtain the intended Memcached package, service, port, and configuration behavior from the external cookbook or target platform requirements before adding Memcached tasks.
   - Iterations: None.

2. **`default` — Redis attribute configuration** (`cookbooks/cache/recipes/default.rb`):
   - Sets `node.default['redisio']['servers']` to one Redis server entry.
   - Configures the Redis server on port `6379`.
   - Sets `requirepass` to the hardcoded source value `redis_secure_password_123`.
   - Sets `replicaservestaledata` to `nil`.
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - In Ansible, represent the `nil` value according to the target Redis role’s semantics and do not convert it to the string `"nil"`.
   - Store the Redis password in Ansible Vault, an AAP credential, or another approved secret backend.
   - Iterations: None.

3. **`default` — Include RedisIO** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The local execution tree does not contain the `redisio` recipe implementation.
   - The external dependency is expected to install Redis and provide its base configuration and service account.
   - In Ansible, install and configure Redis before creating the Redis-owned log directory.
   - Do not assume package names or a service unit name without validating the target distribution and Redis implementation.
   - Iterations: None.

4. **`default` — Create the Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Uses recursive directory creation.
   - Sets owner to `redis`.
   - Sets group to `redis`.
   - Sets mode to `0755`.
   - The `redis` user and group are expected to be provided by the external Redis dependency; no local `user` or `group` resources are present.
   - Ansible equivalent: `ansible.builtin.file` with `state: directory`.
   - Resource count: one `directory` resource.
   - Iterations: None.

5. **`default` — Remove selected Redis configuration directives** (`cookbooks/cache/recipes/default.rb`):
   - Executes `ruby_block[fix_redis_config]`.
   - Operates on `/etc/redis/6379.conf`.
   - If the file exists, reads the complete file and removes matching complete lines.
   - Removes lines matching `^replica-serve-stale-data.*$`.
   - Removes lines matching `^replica-read-only.*$`.
   - Removes lines matching `^repl-ping-replica-period.*$`.
   - Removes lines matching `^client-output-buffer-limit.*$`.
   - Removes lines matching `^replica-priority.*$`.
   - Writes the modified contents back to `/etc/redis/6379.conf`.
   - In Ansible, use explicit `ansible.builtin.lineinfile` tasks with `state: absent`.
   - Preserve the Chef behavior when the file does not exist by using an existence check, conditional execution, or equivalent non-failing behavior.
   - The Chef resource does not declare a service notification; restart or reload Redis only when required by the target implementation.
   - Resource count: one `ruby_block` resource.
   - Iterations: None.

6. **`default` — Enable RedisIO** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio::enable` recipe.
   - The local execution tree does not contain the `redisio::enable` recipe implementation.
   - Enables Redis at boot and starts it according to the external cookbook behavior.
   - Validate the target service unit before defining the final Ansible service task.
   - Iterations: None.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- No package resources are present in the local recipe.
- No verified package names are available from the analyzed files.
- Package requirements must be resolved from the missing `memcached` and `redisio` implementations and the target operating system.
- Do not claim a specific package name for either service based only on this cookbook.

**Service dependencies**:

- Redis is enabled through the missing `redisio::enable` recipe.
- The exact Redis systemd service name is not available in the analyzed files.
- Memcached service management is unavailable because the `memcached` recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis authentication for the Redis server listening on TCP port `6379`
- **Migration handling**:
  - Store the password in Ansible Vault, an AAP credential, or another approved secret backend.
  - Do not place the plaintext value in `defaults/main.yml`, committed inventory, or rendered logs.
  - Pass the protected variable to the Redis configuration task that manages `/etc/redis/6379.conf`.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur calls, environment-variable secrets, TLS certificate references, API keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`

**Service endpoints to check**:

- Redis server on TCP port `6379`
- No Redis Unix socket path is defined by the local recipe.
- No Memcached port is available from the analyzed files.

**Configuration directives to verify**:

The Redis configuration must contain the configured authentication setting and must not contain active lines matching:

- `^replica-serve-stale-data.*$`
- `^replica-read-only.*$`
- `^repl-ping-replica-period.*$`
- `^client-output-buffer-limit.*$`
- `^replica-priority.*$`

**Templates rendered**:

- None; render count: `0`

**Static files deployed**:

- None

## Pre-flight checks:

### Redis server on port 6379

Discover the service unit because the local cookbook does not expose the external `redisio` service name:

```bash
systemctl list-units --type=service | grep -E 'redis|redis-server'
systemctl status redis
systemctl status redis-server
```

Use only the service unit that exists on the target system.

Verify the Redis configuration file and key settings:

```bash
test -f /etc/redis/6379.conf
grep -nE '^(bind|port|requirepass|dir|pidfile)' /etc/redis/6379.conf
```

Verify that the selected directives have been removed:

```bash
! grep -nE '^replica-serve-stale-data.*$' /etc/redis/6379.conf
! grep -nE '^replica-read-only.*$' /etc/redis/6379.conf
! grep -nE '^repl-ping-replica-period.*$' /etc/redis/6379.conf
! grep -nE '^client-output-buffer-limit.*$' /etc/redis/6379.conf
! grep -nE '^replica-priority.*$' /etc/redis/6379.conf
```

Test authenticated connectivity without placing the password directly in command history:

```bash
export REDISCLI_AUTH='<retrieve-from-approved-secret-store>'
redis-cli -p 6379 PING
```

Expected result:

```text
PONG
```

Verify the Redis port and process:

```bash
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
ps aux | grep '[r]edis'
ss -tlnp | grep ':6379'
```

The reported TCP port and listening socket must be `6379`.

Verify Redis directories and ownership:

```bash
stat -c '%A %U %G %n' /var/log/redis
stat -c '%A %U %G %n' /run/redis
stat -c '%A %U %G %n' /etc/redis/6379.conf
```

Expected `/var/log/redis` properties:

- Owner: `redis`
- Group: `redis`
- Mode: `0755`

Inspect the configured log destination and applicable service logs:

```bash
grep -nE '^(logfile|syslog-enabled|dir|pidfile)' /etc/redis/6379.conf
journalctl -u redis --no-pager -n 50
journalctl -u redis-server --no-pager -n 50
```

Retain only the journal command for the service unit that exists on the target host.

### Memcached dependency

The local cookbook does not provide a Memcached instance name, port, package, configuration path, or service resource. Validate the external dependency separately before finalizing Memcached tasks:

```bash
systemctl list-units --type=service | grep memcached
```

Do not add a Memcached port check or package assertion until the missing `memcached` recipe has been inspected or the target platform requirements have been explicitly defined.