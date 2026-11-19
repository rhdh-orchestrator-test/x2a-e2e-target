---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis server on port `6379`. Memcached is started and enabled through the `memcached_instance` custom resource. Redis uses a hardcoded password, `/run/redis` for its PID directory, `/var/log/redis` for logs, and an in-place cleanup of replication-related directives in `/etc/redis/6379.conf`. The `redisio` and `redisio::enable` recipes and the `memcached_instance` provider are unavailable from the supplied execution tree, so the Ansible migration must explicitly implement their required behavior and verify the target platform’s package names and service unit names.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Platform-specific Memcached configuration path; no path is specified in the supplied files
  - Port/Socket: TCP `11211`, UDP `11211`, listening on `0.0.0.0`
  - Key Config: `64` MB memory, `1024` maximum connections, `1m` maximum object size, service user `service_user`, ulimit `1024`, empty experimental and extra CLI option lists, start and enable actions
  - Threads: Sourced from `node['memcached']['threads']`; no default value is available in the supplied attributes information
  - Attributes: `node['memcached']['version']` is `nil`; `node['memcached']['logfilepath']` is `/var/log/memcached`. These attributes are not directly passed by the shown recipe to `memcached_instance`.

- **redis-6379**: Redis server configured on port `6379`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`; no Unix socket configuration is visible in the supplied cache recipe
  - Key Config: Password `redis_secure_password_123`, PID directory `/run/redis`, log directory `/var/log/redis`
  - Log Directory: Owner `redis`, group `redis`, mode `0755`, recursive creation enabled
  - Configuration Cleanup: Removes complete lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` when present
  - Redis implementation caveat: The unavailable `redisio` recipes must be checked separately for additional socket or service configuration.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

```text
```

No provider file is available in the supplied file list for `memcached_instance`.

**Templates:**

```text
```

No templates are rendered by the supplied recipes.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

**Referenced but unavailable recipe files:**

- `redisio`
- `redisio::enable`

The validation data reports seven analyzed files in total, but the remaining four files are not identified in the supplied material. They cannot be added to the directory listing without inventing paths or filenames.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe before Redis operations.
   - Assigns one Redis server configuration item for port `6379`.
   - Sets the Redis base PID directory to `/run/redis`.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes the `fix_redis_config` Ruby block.
   - Includes the unavailable `redisio::enable` recipe.

   **Redis configuration item:**
   - `redis-6379`: port `6379`, password assigned as `requirepass`, and `replicaservestaledata` set to `nil`
   - No Redis `.each` loop is present; the supplied recipe assigns one server item directly.

   **Unavailable `redisio` recipe:**
   - Intended to install and configure Redis and create the Redis service account.
   - Exact package names, configuration templates, service name, and service actions are unavailable.
   - The Ansible implementation must select and verify these values for the target platform.

   **Directory resource:**
   - Creates `/var/log/redis`.
   - Uses owner `redis`, group `redis`, mode `0755`, and recursive creation.

   **Ruby block `fix_redis_config`:**
   - Checks whether `/etc/redis/6379.conf` exists.
   - Reads the file only when it exists.
   - Removes lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Does not explicitly show a service notification.

   **Unavailable `redisio::enable` recipe:**
   - Intended to enable Redis at boot.
   - The Ansible implementation must identify the actual Redis unit created by the selected package or replacement role and enable that unit.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares the custom resource `memcached_instance['memcached']`.
   - Starts and enables the `memcached` instance.
   - Configures memory `64` MB.
   - Configures TCP port `11211`.
   - Configures UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Configures maximum connections `1024`.
   - Uses service user `service_user`.
   - Configures maximum object size `1m`.
   - Sources threads from `node['memcached']['threads']`, whose default is not available in the supplied attributes information.
   - Uses empty experimental and extra CLI option lists.
   - Configures ulimit `1024`.
   - The provider is unavailable, so the Ansible migration must reproduce the observable behavior explicitly.

   **Ansible implementation requirements for `memcached`:**
   - Install the platform-appropriate Memcached package after resolving the target distribution.
   - Create or configure the `service_user` service account.
   - Configure the Memcached bind address, TCP port, UDP port, memory, maximum connections, maximum object size, thread value, and ulimit.
   - Start the Memcached service.
   - Enable the Memcached service at boot.
   - Restart Memcached only when its configuration changes.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint shown

**System package dependencies**:

- No package names are specified by the supplied executed recipes.
- The unavailable `memcached_instance` provider and `redisio` recipes are expected to install or configure the required packages.
- Do not assert unverified package names. Resolve and verify the platform-specific Memcached and Redis package names before implementation.

**Service dependencies**:

- Memcached service for instance `memcached`
- Redis service for instance `redis-6379`
- Redis service account and `redis` group required by `/var/log/redis`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded credential
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `requirepass` within `node['redisio']['servers']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for instance `redis-6379` on port `6379`
- **Ansible migration storage**: Ansible Vault, an AAP credential, or another approved secret backend
- **Handling requirements**: Use protected configuration-file permissions and `no_log: true` for tasks that handle the password. Do not expose the password in playbooks, defaults files, command output, or logs.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk/Conjur integration, environment-variable secrets, TLS certificate references, or database connection strings with embedded credentials were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- The platform-specific Memcached configuration file
- The Memcached service unit or init-script path
- The Redis service unit or init-script path

**Service endpoints to check**:

- Instance `memcached`: TCP `0.0.0.0:11211`
- Instance `memcached`: UDP `0.0.0.0:11211`
- Instance `redis-6379`: TCP `6379`
- Unix socket: No socket configuration is visible in the supplied cache recipe; inspect the unavailable Redis implementation separately.

**Templates rendered**:

- None; render count `0`

**Configuration mutation performed by Chef**:

- `/etc/redis/6379.conf` is edited in place when it exists.
- Five directive patterns are removed when present.

## Pre-flight checks

### Instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
```

Use the actual unit name if the target distribution creates a different Memcached service unit.

```bash
grep -E '(^|[[:space:]])-m[[:space:]]+64|memory|11211|0\.0\.0\.0|maxconn|threads|ulimit' /etc/memcached.conf
```

Verify the effective settings:

- Memory: `64` MB
- TCP port: `11211`
- UDP port: `11211`
- Listen address: `0.0.0.0`
- Maximum connections: `1024`
- Maximum object size: `1m`
- Ulimit: `1024`

```bash
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211
```

Expected result: a response beginning with `VERSION`.

```bash
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
```

Expected results: TCP and UDP listeners on port `11211`.

### Instance `redis-6379`

```bash
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
```

Use the actual versioned or instance-specific unit name if the selected Redis package creates one.

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Verify:

- `port 6379` is present.
- Redis authentication is configured from the approved secret store.
- The following directives are absent after migration:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

Do not print the password in command output or migration logs.

```bash
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_SECRET_STORE>' PING
```

Expected result:

```text
PONG
```

```bash
ss -tlnp | grep ':6379'
```

Expected result: a Redis listener on TCP port `6379`.

```bash
stat -c '%A %U %G %n' /var/log/redis
```

Expected result:

- Owner: `redis`
- Group: `redis`
- Mode: `0755`

```bash
stat -c '%A %U %G %n' /run/redis
```

Confirm that `/run/redis` exists and is used by the Redis instance for PID management.

### Service logs

```bash
journalctl -u memcached --no-pager -n 50
journalctl -u redis --no-pager -n 50
```

Check for:

- Memcached startup errors
- Redis configuration parse errors
- Redis authentication or permission errors
- Binding failures on ports `11211` and `6379`

### Network summary

```bash
ss -tlnp | grep -E ':(11211|6379)'
ss -ulnp | grep ':11211'
```

Expected listeners:

- TCP `11211`: instance `memcached`
- UDP `11211`: instance `memcached`
- TCP `6379`: instance `redis-6379`