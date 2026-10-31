---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis server on port `6379`, enables Redis authentication with the hardcoded password `redis_secure_password_123`, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and invokes the external `memcached`, `redisio`, and `redisio::enable` recipes. Those dependency recipes are unavailable in the supplied execution tree, so their exact packages, service names, templates, and Memcached settings must be obtained separately. The Redis password must be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Key Config: Authentication enabled through `requirepass`; password must be stored in Ansible Vault
  - Key Config: `replicaservestaledata` explicitly set to `nil`
  - Key Config: The following directives are removed from the generated configuration:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

- **Memcached**: External dependency invoked by the cookbook
  - Location/Path: Not defined in the visible cookbook
  - Port/Socket: Not defined in the visible cookbook
  - Key Config: Exact package, configuration path, service name, port, and settings must be obtained from the external `memcached` cookbook
  - Key Config: No additional Memcached instance or setting may be inferred from this cookbook

The visible recipe configures one Redis entry explicitly. It contains no loop over the Redis server collection.

## File Structure

Only the Ruby recipe shown in the execution tree is included.

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

The cookbook contains `metadata.rb`, but it is metadata rather than an executed recipe file and is not included in the execution-tree file list.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Invokes the external `memcached` recipe.
   - Defines one Redis server on port `6379` with `requirepass` set to the detected hardcoded password and `replicaservestaledata` set to `nil`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Invokes the external `redisio` recipe.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` after Redis configuration generation.
   - Invokes the external `redisio::enable` recipe.
   - No `.each` loops are present; the single Redis instance is implemented explicitly.

   **Execution details:**

   1. **Include `memcached`**
      - Source operation: `include_recipe 'memcached'`
      - The dependency recipe is unavailable in the execution tree.
      - Exact Memcached packages, templates, service resources, ports, and configuration values cannot be determined.
      - Obtain the external `memcached` cookbook before implementing exact parity.

   2. **Define Redis server configuration**
      - Configured instance: Redis server on port `6379`.
      - Set `requirepass` to the detected password, migrated to an Ansible Vault variable.
      - Preserve the explicit `replicaservestaledata: nil` behavior.
      - The external `redisio` cookbook determines the final package, service, user, and generated configuration details.

   3. **Create the Redis log directory**
      - Resource: `directory[/var/log/redis]`
      - Use `ansible.builtin.file`.
      - Set `state: directory`.
      - Set owner to `redis`.
      - Set group to `redis`.
      - Set mode to `'0755'`.
      - Create parent directories as required.
      - Resource count: one directory resource.

   4. **Include `redisio`**
      - Source operation: `include_recipe 'redisio'`
      - The dependency recipe is unavailable in the execution tree.
      - Preserve the Redis server definition for port `6379` and its vaulted password.
      - Obtain the external cookbook to determine the exact Redis package, service resource, configuration template, user, and installation behavior.

   5. **Remove selected Redis directives with `fix_redis_config`**
      - Resource: `ruby_block[fix_redis_config]`
      - Target: `/etc/redis/6379.conf`
      - Check whether the file exists.
      - Remove complete lines matching:
        - `^replica-serve-stale-data.*$`
        - `^replica-read-only.*$`
        - `^repl-ping-replica-period.*$`
        - `^client-output-buffer-limit.*$`
        - `^replica-priority.*$`
      - Write the modified configuration back to `/etc/redis/6379.conf`.
      - Implement with ordered `ansible.builtin.lineinfile` tasks using `state: absent`.
      - Guard the tasks with a file-existence check.
      - Preserve execution after Redis configuration generation.
      - No service notification is declared by the visible recipe; restart or reload behavior must be confirmed from the external `redisio` implementation.
      - Resource count: one Ruby block.

   6. **Include `redisio::enable`**
      - Source operation: `include_recipe 'redisio::enable'`
      - The dependency recipe is unavailable in the execution tree.
      - Enable and start the Redis service defined by the external cookbook.
      - Resolve the exact service name from the external implementation; do not invent a systemd unit name.
      - Preserve this operation after the Redis configuration correction.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint
- `redisio::enable`, provided by the `redisio` cookbook

**System package dependencies**:

- No package resources are present in the visible cookbook.
- Exact package names for Memcached and Redis are unavailable because the dependency recipes are not present.
- Package names must be obtained from the external `memcached` and `redisio` cookbook implementations rather than inferred.

**Service dependencies**:

- Memcached service management is delegated to the external `memcached` recipe.
- Redis installation and service management are delegated to the external `redisio` recipe.
- Redis enablement and startup are delegated to the external `redisio::enable` recipe.
- Exact service names are unavailable in the supplied execution tree.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Detected value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the Redis server on port `6379`
- **Migration handling**:
  - Store the password in Ansible Vault.
  - Reference the vaulted variable from the Redis configuration task or template.
  - Do not commit the plaintext value to the Ansible role or inventory.
  - Prevent validation commands and logs from printing the password.

No data bag, encrypted data bag, Chef Vault item, Conjur variable, CyberArk data bag, environment-variable secret, TLS certificate, private key, API token, or database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

The Redis data directory and explicit Redis log file are not defined in the visible recipe. Obtain them from the external `redisio` cookbook, generated configuration, or target package defaults.

**Service endpoints to check**:

- Redis server on port `6379`
- Memcached endpoint: not defined by the visible cookbook
- Unix sockets: none defined by the visible cookbook

**Network interfaces**:

- No bind address is specified. Verify the generated Redis configuration before assuming loopback or another interface.

**Templates rendered**:

- None shown in the execution tree.
- No template render count can be established from the visible cookbook.

## Pre-flight checks

### Redis server on port 6379

```bash
systemctl status <redis-service-name>
ps aux | grep '[r]edis-server'
```

Replace `<redis-service-name>` with the service name discovered from the external `redisio` implementation.

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Verify that the removed directives are absent as active configuration lines:

```bash
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis replication directives found"
  exit 1
fi
```

Verify the configured port:

```bash
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf
```

Do not print the `requirepass` value in migration logs.

Verify authenticated connectivity without placing the password directly in command history:

```bash
REDISCLI_AUTH='<vaulted-redis-password>' redis-cli -p 6379 PING
```

Expected result:

```text
PONG
```

Verify that unauthenticated access is rejected when authentication is enabled:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication-required error rather than `PONG`.

Verify the listening endpoint:

```bash
ss -tlnp | grep ':6379'
```

Verify the Redis version using the protected password variable:

```bash
REDISCLI_AUTH='<vaulted-redis-password>' \
  redis-cli -p 6379 INFO server | grep '^redis_version:'
```

Verify the log directory:

```bash
stat -c '%A %U %G %n' /var/log/redis
ls -ld /var/log/redis
```

Expected values:

- Owner: `redis`
- Group: `redis`
- Permissions: equivalent to `0755`
- Path: `/var/log/redis`

Check the generated logging configuration:

```bash
grep -E '^(logfile|syslog-enabled)' /etc/redis/6379.conf
```

### Memcached

The visible cookbook does not define a Memcached port, service name, package, or configuration path. Obtain these values from the external `memcached` cookbook before running service-specific checks.

If the dependency confirms the conventional Memcached configuration, verify it with:

```bash
systemctl status memcached
ss -tlnp | grep ':11211'
printf 'stats\r\nquit\r\n' | nc 127.0.0.1 11211
```

Port `11211` is only a conventional default and is not defined by the visible cookbook.

### Redis logs

After resolving the external Redis service name, inspect recent service logs:

```bash
journalctl -u <redis-service-name> --no-pager -n 50
```

Replace `<redis-service-name>` with the exact service name from the external `redisio` implementation.