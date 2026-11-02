---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a Redis cache instance identified as `6379`, intended to listen on TCP port `6379`, with authentication and Redis log storage under `/var/log/redis`. The directly visible recipe includes the external `memcached`, `redisio`, and `redisio::enable` recipes, creates the Redis log directory, and runs a Ruby configuration-cleanup block. The external recipe implementations are unavailable, so package names, service names, generated configuration behavior, and Memcached settings remain unresolved. A hardcoded Redis password is reported in the source recipe and must be migrated to Ansible Vault or an approved secret-management system.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance `6379`**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf` — reported by the source-level recipe analysis; requires verification because the external `redisio` recipe is unavailable
  - Port/Socket: TCP `6379` — configured in the reported Redis server collection; requires verification
  - Log directory: `/var/log/redis` — directory resource path is confirmed; ownership, permissions, and recursive creation require source-level verification
  - Authentication: Redis `requirepass` is reported as enabled
  - Replica setting: `replicaservestaledata` is reported as `nil`
  - Configuration cleanup: The reported Ruby block removes lines beginning with:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

The source recipe includes `memcached`, but the external recipe file is unavailable. No Memcached instance name, port, socket, configuration path, package, service, or daemon settings can be confirmed.

## File Structure

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files were shown or used by the execution tree.

**Templates:**
```text
```

No template files were shown or rendered by the execution tree.

**Attributes:**
```text
```

No standalone attribute files were shown. The reported Redis server collection is defined inline in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` were shown.

## Module Explanation

The cookbook performs operations in this order:

1. **Include Memcached** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The external recipe file is unavailable.
   - Memcached package names, service name, configuration path, listening endpoint, and daemon settings cannot be confirmed.
   - Do not create Memcached Ansible tasks until the external cookbook implementation is obtained.

2. **Define the Redis server collection** (`cookbooks/cache/recipes/default.rb`):
   - Defines one reported Redis item named `6379`.
   - Reported port: `6379`.
   - Reported authentication setting: `requirepass` with the source value `redis_secure_password_123`.
   - Reported `replicaservestaledata` value: `nil`.
   - No `.each` loops or additional Redis instances were identified.
   - Migrate the password to an Ansible Vault variable such as `vault_redis_password`; do not copy the plaintext value into Ansible defaults or task files.

3. **Create the Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates `directory[/var/log/redis]`.
   - Confirmed path: `/var/log/redis`.
   - The source-level plan reports owner `redis`, group `redis`, mode `0755`, and recursive creation, but the available structured analysis confirms only the resource path.
   - Verify these properties against the source recipe before implementing the Ansible `ansible.builtin.file` task.

4. **Include Redis installation and configuration** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The external recipe file is unavailable.
   - Redis package names and versions, repository configuration, user and group creation, configuration templates, data paths, log paths, bind addresses, and service names cannot be confirmed.
   - Obtain and inspect the external `redisio` cookbook before implementing installation or service tasks.

5. **Remove selected Redis directives** (`cookbooks/cache/recipes/default.rb`):
   - Creates `ruby_block[fix_redis_config]`.
   - The source-level plan reports that it operates on `/etc/redis/6379.conf`.
   - The reported behavior checks for the file, removes complete lines beginning with five replication-related directives, and writes the result back.
   - The available structured analysis confirms the Ruby block resource but does not independently confirm its path, existence check, or directive list.
   - If confirmed from source inspection, implement the behavior with `ansible.builtin.stat` followed by `ansible.builtin.replace`.
   - The Chef block does not explicitly notify or restart Redis.

6. **Enable Redis** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio::enable` recipe.
   - The external recipe file is unavailable.
   - The exact Redis service name and enabled/running behavior cannot be confirmed.
   - Determine the service name from the external cookbook or target system before using `ansible.builtin.service`.

## Dependencies

**External cookbook dependencies**:

- `memcached` — the source plan reports version constraint `~> 6.0`; this metadata claim requires verification because `metadata.rb` analysis was not included in the available validation
- `redisio` — no version constraint reported
- `redisio::enable` — included recipe from `redisio`

**System package dependencies**:

- No package names are confirmed in the supplied execution tree.
- Memcached package names are unavailable because the external `memcached` recipe is missing.
- Redis package names and versions are unavailable because the external `redisio` recipe is missing.
- Do not invent package names or versions in the Ansible implementation.

**Service dependencies**:

- Redis service behavior is provided by the unavailable `redisio::enable` recipe.
- The Redis service name, enablement state, and startup behavior are unresolved.
- No directly visible service resource exists in `cookbooks/cache/recipes/default.rb`.
- Memcached service behavior is unresolved because its external recipe is unavailable.

## Credentials

**Detection Summary**: 1 reported credential in 1 file; the finding is based on source-level recipe content and is not independently represented in the available structured validation summary.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis Authentication Password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Reported current value**: `redis_secure_password_123`
- **Usage context**: Redis authentication through the `requirepass` configuration setting
- **Migration storage**: Ansible Vault or an approved external secret provider
- **Recommended Ansible variable**: `vault_redis_password`

No additional credential mechanisms are reported in the supplied source analysis. Claims about the absence of data bags, encrypted data bags, external secret integrations, certificates, private keys, API tokens, or environment-variable secrets should be confirmed against the complete source tree.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf` — reported Redis configuration path; verify against `redisio`
- `/var/log/redis` — confirmed directory resource path

The following remain unresolved until the external recipes are inspected:

- Redis data directory
- Redis log file
- Redis PID file
- Redis systemd unit name
- Memcached configuration path
- Memcached log path
- Memcached service name

**Service endpoints to check**:

- Redis TCP port `6379` — reported configuration; verify after deployment
- Unix sockets: None referenced by the visible recipe
- Network bind address: Not specified in the visible recipe
- Memcached endpoint: Unknown

**Templates rendered**:

- None shown or rendered by the supplied execution tree
- Render count: `0`

**Iterations**:

- Redis server collection item: `6379`
- No additional collection items or `.each` iterations were identified.

## Pre-flight checks

```bash
# Confirm the available recipe and dependency implementations
test -f cookbooks/cache/recipes/default.rb
find cookbooks -path '*memcached*' -o -path '*redisio*'

# Identify the actual Redis service name supplied by redisio
systemctl list-unit-files | grep -E 'redis|6379'

# Replace this placeholder with the confirmed service name
systemctl status <confirmed-redis-service-name>
```

### Redis instance `6379`

```bash
# Verify the reported configuration path
test -f /etc/redis/6379.conf

# Verify the reported port
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' \
  /etc/redis/6379.conf

# Verify authentication is configured without printing the password
grep -E '^[[:space:]]*requirepass[[:space:]]+' \
  /etc/redis/6379.conf

# Verify the reported cleanup directives are absent
grep -E '^[[:space:]]*(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Verify the log directory path
test -d /var/log/redis

# Verify ownership and permissions if those properties are confirmed from source
stat -c '%U %G %a %n' /var/log/redis

# Verify the Redis listener
ss -ltnp | grep ':6379'

# Test authenticated Redis access using the Ansible Vault value
redis-cli -p 6379 -a '<redis-password-from-vault>' PING

# Expected output:
# PONG

# Confirm unauthenticated access is rejected
redis-cli -p 6379 PING

# Expected result:
# NOAUTH Authentication required.

# Test authenticated write, read, and delete operations
redis-cli -p 6379 -a '<redis-password-from-vault>' SET migration_check chef_to_ansible
redis-cli -p 6379 -a '<redis-password-from-vault>' GET migration_check
redis-cli -p 6379 -a '<redis-password-from-vault>' DEL migration_check

# Expected GET output:
# chef_to_ansible
```

### Redis logs

```bash
# Identify the configured Redis log file, if any
grep -E '^[[:space:]]*logfile[[:space:]]+' /etc/redis/6379.conf

# Inspect the configured log file after identifying its path
tail -n 50 <configured-redis-log-file>

# If Redis logs to systemd instead
journalctl -u <confirmed-redis-service-name> -n 50 --no-pager
```

### Memcached

The external `memcached` recipe is unavailable. Do not assume a Memcached port, socket, package, configuration path, or service name. After obtaining the dependency implementation, add endpoint and service checks based on its actual configuration.