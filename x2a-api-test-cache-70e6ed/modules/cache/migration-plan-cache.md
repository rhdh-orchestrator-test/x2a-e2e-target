---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The analyzed local recipe includes the external `memcached` recipe, creates `/var/log/redis`, configures one Redis server on port `6379`, includes `redisio`, removes selected replication directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. Redis configuration details, including ownership, password authentication, and directive removal, are reported by the supplied recipe analysis but are not fully verifiable from the structured execution summary. The external recipe implementations are unavailable, so their package names, service names, and detailed configuration must be obtained before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance configured through the external `redisio` cookbook
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication is reported as enabled through `requirepass`; `replicaservestaledata` is reported as explicitly set to `nil`; `/var/log/redis` is reported as a Redis log directory owned by `redis:redis` with mode `0755`. These settings require confirmation against the recipe contents and dependency implementation.

- **Memcached**: External cache dependency included by the cookbook
  - Location/Path: Not available from the supplied cookbook analysis
  - Port/Socket: Not available; do not assume a default
  - Key Config: The external `memcached` cookbook is constrained to version `~> 6.0`, but its package, service name, configuration file, listen address, memory limit, user, group, and lifecycle behavior are unavailable. Inspect the dependency before defining Ansible variables or validation checks.

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

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

The execution tree references the following external recipes, which are not local files:

- `memcached`
- `redisio`
- `redisio::enable`

These recipes must not be represented as local cookbook recipe files in the Ansible migration.

## Module Explanation

The cookbook performs operations in the following order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe before Redis log-directory creation.
   - Creates `/var/log/redis`; ownership `redis:redis`, mode `0755`, and recursive creation are reported by the recipe analysis but are not present in the structured execution summary and must be verified.
   - Sets the Redis server collection to one configured item:
     - Redis server on port `6379`
     - `requirepass` set to the reported hardcoded value `redis_secure_password_123`
     - `replicaservestaledata` set to `nil`
   - Includes the external `redisio` recipe to install and configure Redis.
   - Runs `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - Includes the external `redisio::enable` recipe to enable Redis.
   - No `.each` loops are present in the supplied recipe analysis; the single Redis server item is listed explicitly above.

   ### External `memcached` inclusion
   - Chef operation: `include_recipe 'memcached'`
   - The execution tree reports that the recipe file is unavailable.
   - Migration equivalent: invoke a dependency role or included task file for Memcached.
   - Do not invent package names, service names, ports, configuration paths, bind addresses, or memory settings.
   - Preserve execution order before Redis log-directory creation.

   ### Redis log directory
   - Reported path: `/var/log/redis`
   - Reported owner: `redis`
   - Reported group: `redis`
   - Reported mode: `0755`
   - Reported recursive creation: enabled
   - The structured execution summary identifies `directory[/var/log/redis]` but does not independently confirm these properties.
   - Ensure the `redis` group exists before applying ownership, using the Redis dependency role or an explicit group task after confirming dependency behavior.
   - No separate `group[redis]` resource is confirmed in the supplied execution tree.

   ### Redis server configuration
   - Reported configuration:
     ```yaml
     redisio_servers:
       - port: 6379
         requirepass: "{{ vault_redis_requirepass }}"
         replicaservestaledata: null
     ```
   - Store the password in Ansible Vault, AAP credentials, or an approved secret-management system.
   - The external `redisio` implementation must provide or confirm the Redis package, service name, binary path, data directory, configuration template, and startup behavior.
   - Do not assume a package or service name.

   ### `ruby_block[fix_redis_config]`
   - Target path: `/etc/redis/6379.conf`
   - The recipe analysis reports the following behavior:
     - Check whether the file exists.
     - Read the file.
     - Remove complete lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Write the modified content back to the same file.
   - The structured execution summary identifies the resource but does not expose its implementation. Confirm these regular expressions and file-handling semantics against `cookbooks/cache/recipes/default.rb`.
   - Preserve the no-op behavior when `/etc/redis/6379.conf` does not exist.
   - Do not add an automatic service restart unless required by the confirmed Redis dependency behavior.

   Suggested Ansible implementation after confirming the recipe:
   ```yaml
   - name: Check whether Redis configuration exists
     ansible.builtin.stat:
       path: /etc/redis/6379.conf
     register: redis_config_file_stat

   - name: Remove unsupported Redis replication directives
     ansible.builtin.replace:
       path: /etc/redis/6379.conf
       regexp: '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority).*$'
       replace: ''
     when: redis_config_file_stat.stat.exists
   ```

   ### External `redisio` inclusion
   - Chef operation: `include_recipe 'redisio'`
   - The execution tree reports that the recipe file is unavailable.
   - Migration equivalent: invoke the Redis installation and configuration role after the Redis server variables are defined.
   - Obtain package names, service names, versions, paths, and startup behavior from the actual `redisio` cookbook or target Ansible role.

   ### External `redisio::enable` inclusion
   - Chef operation: `include_recipe 'redisio::enable'`
   - The execution tree reports that the recipe file is unavailable.
   - Migration equivalent: enable the exact Redis service identified by the dependency implementation.
   - The supplied execution tree establishes enablement but does not confirm that the service is started.
   - Do not add a start action until the external recipe behavior is verified.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version `~> 6.0`
- `redisio`, version constraint not shown

**System package dependencies**:

- No package resources are confirmed in the supplied execution tree.
- Package names for Memcached and Redis are unavailable because the external recipe files are not included.
- Inspect the dependency implementations for Ubuntu `>= 18.04` and CentOS `>= 7.0` before adding package tasks.
- Do not substitute generic or guessed package names.

**Service dependencies**:

- Redis service managed by the external `redisio` dependency; exact service name is unavailable.
- Memcached service potentially managed by the external `memcached` dependency; exact service name and lifecycle behavior are unavailable.
- The `redis` group may be required for log-directory ownership, but no `group[redis]` resource is confirmed in the supplied execution tree.

## Credentials

**Detection Summary**: 1 credential is reported in `cookbooks/cache/recipes/default.rb`; the supplied structured analysis does not independently expose the recipe content or verify the finding.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe, according to the supplied recipe analysis
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext value
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Configures Redis `requirepass` authentication for the Redis server on port `6379`.
- **Migration storage**: Ansible Vault, AAP credentials, or another approved secret-management system
- **Migration variable**: `redis_requirepass: "{{ vault_redis_requirepass }}"`

Verify the reported password against the recipe contents before migration. Do not place the plaintext value in committed defaults, task files, `group_vars`, or `host_vars`.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, Conjur variable, CyberArk data bag, environment-variable secret reference, TLS certificate, private key, or database connection string was detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis server on TCP port `6379`
- Memcached endpoint: unavailable until the `memcached` cookbook version `~> 6.0` is inspected
- Unix sockets: None identified
- Network interface binding: Not specified

**Configuration checks**:

- Confirm the Redis instance on port `6379` is configured.
- Confirm Redis authentication is enabled if the reported `requirepass` setting is verified.
- Confirm `/var/log/redis` exists with the verified owner, group, and mode.
- Confirm the following directives are absent from `/etc/redis/6379.conf` if the `ruby_block` implementation is verified:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- Inspect the external Memcached dependency and record its package, service, port, configuration file, bind address, and memory allocation before creating Memcached checks.

**Templates rendered**:

- None. No template files are present or referenced in the supplied execution tree.

**Static files deployed**:

- None.

## Pre-flight checks

```bash
# Verify the local recipe is available for source confirmation
test -f cookbooks/cache/recipes/default.rb

# Verify the Redis configuration file for the port 6379 instance
test -f /etc/redis/6379.conf

# Verify the Redis log directory
stat -c '%A %U:%G %n' /var/log/redis
# Expected after confirmation: drwxr-xr-x redis:redis /var/log/redis

# Verify removed Redis directives for the port 6379 instance
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected after confirmed migration: no output

# Verify Redis is listening on TCP port 6379
ss -ltnp | grep ':6379'
# Expected: a Redis process listening on TCP port 6379

# Verify authenticated Redis access
redis-cli -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning PING
# Expected: PONG

# Verify unauthenticated access is rejected when password authentication is confirmed
redis-cli -p 6379 PING
# Expected: an authentication-required error

# Verify the configured Redis port
redis-cli -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning CONFIG GET port
# Expected value: 6379

# Verify Redis authentication configuration
redis-cli -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning CONFIG GET requirepass
# Expected: requirepass is configured

# Verify Redis server information
redis-cli -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning INFO server
```

Use the exact Redis service unit name obtained from the `redisio` dependency:

```bash
systemctl status <redis-service-name>
journalctl -u <redis-service-name> --no-pager -n 50
```

Memcached pre-flight checks cannot be completed safely until the external `memcached` cookbook version `~> 6.0` has been inspected. After inspection, add checks for the exact Memcached package, service unit, configuration file, listening port, bind address, and memory allocation. Do not use a guessed endpoint or service name.