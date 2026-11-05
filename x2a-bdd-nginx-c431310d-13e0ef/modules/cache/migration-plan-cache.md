---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The available recipe includes Memcached, assigns one reported Redis server on port `6379`, creates `/var/log/redis`, includes `redisio`, removes selected replication-related directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. The external recipes are not present in the analyzed cookbook tree, so their package names, service names, templates, and detailed configuration must be obtained from the corresponding implementations. Redis settings and the reported hardcoded password require confirmation against the complete recipe source before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Reported Redis instance configured through `node['redisio']['servers']`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Reported `port: '6379'`, `requirepass: 'redis_secure_password_123'`, and `replicaservestaledata: nil`; these values are not present in the supplied structured execution analysis and must be verified against the complete recipe source.
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Configuration cleanup: Remove complete lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` when the configuration file exists.

- **Memcached**: External cache instance included through the `memcached` cookbook
  - Location/Path: Not available from the analyzed cookbook
  - Port/Socket: Not available from the analyzed cookbook
  - Key Config: Package, configuration path, service name, and port must be obtained from the external `memcached` cookbook or its Ansible equivalent.

## File Structure

Only files present in the supplied directory listing and execution analysis are listed.

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

```text
```

No provider files were shown or used.

**Templates:**

```text
```

No template files were shown or rendered.

**Attributes:**

```text
```

No attribute files were shown. Reported Redis settings are assigned directly in `cookbooks/cache/recipes/default.rb`, but those assignments are not present in the supplied structured execution analysis.

**Files:**

```text
```

No static files were shown or deployed.

The following referenced recipes are not included because they were explicitly reported as missing and are not files in the supplied execution tree:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Assigns one reported Redis server configuration to `node.default['redisio']['servers']`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - Runs `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - Includes the external `redisio::enable` recipe.

   **Detailed execution steps:**

   - **Include `memcached`**
     - Chef include: `include_recipe 'memcached'`
     - The referenced recipe is missing from the supplied execution tree.
     - Obtain Memcached package, configuration, service, and port details from the external cookbook or Ansible role.
     - Do not invent these values from the available cookbook.

   - **Set Redis server attributes**
     - The plan reports one Redis server entry with:
       - `port`: `'6379'`
       - `requirepass`: `'redis_secure_password_123'`
       - `replicaservestaledata`: `nil`
     - These assignments and values are not present in the supplied structured execution analysis and must be verified against the complete `cookbooks/cache/recipes/default.rb` source.
     - Store any confirmed password in Ansible Vault rather than plaintext variables or task files.

   - **Create Redis log directory**
     - Resource: `directory[/var/log/redis]`
     - Path: `/var/log/redis`
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation: enabled
     - Ansible equivalent:
       ```yaml
       - name: Create Redis log directory
         ansible.builtin.file:
           path: /var/log/redis
           state: directory
           owner: redis
           group: redis
           mode: '0755'
           recurse: true
       ```

   - **Include `redisio`**
     - Chef include: `include_recipe 'redisio'`
     - The referenced recipe is missing from the supplied execution tree.
     - Its package, template, service, provider, and configuration behavior cannot be verified from the available files.
     - Use the external Redis role or implementation that provides the equivalent functionality.

   - **Run `ruby_block[fix_redis_config]`**
     - Target: `/etc/redis/6379.conf`
     - If the file does not exist, make no change.
     - If the file exists, remove complete lines beginning with:
       - `replica-serve-stale-data`
       - `replica-read-only`
       - `repl-ping-replica-period`
       - `client-output-buffer-limit`
       - `replica-priority`
     - Rewrite the file in place after the substitutions.
     - Ansible may use `ansible.builtin.replace` or a controlled template.
     - Notify a Redis restart or reload only when required by the selected external Redis implementation; the supplied recipe does not explicitly define a restart notification.

   - **Include `redisio::enable`**
     - Chef include: `include_recipe 'redisio::enable'`
     - The referenced recipe is missing from the supplied execution tree.
     - Enable and start Redis using the service name supplied by the selected external Redis implementation.
     - Do not assume a specific systemd unit name.

   **Resource counts for the available recipe:**

   - `directory`: 1
   - `ruby_block`: 1
   - `include_recipe`: 3
     - `memcached`
     - `redisio`
     - `redisio::enable`

   **Iterations:**

   - No `.each` loop or explicit collection iteration is shown in the supplied recipe or execution tree.
   - The reported Redis configuration contains one server entry, but the available recipe does not itself iterate over that collection.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- No packages are directly installed by the available recipe.
- Package installation is delegated to the missing `memcached` and `redisio` recipes.
- Exact package names are not available from the analyzed cookbook and must be obtained from the selected external implementations.

**Service dependencies**:

- Memcached service behavior is delegated to the missing `memcached` recipe.
- Redis service configuration and enablement are delegated to the missing `redisio` and `redisio::enable` recipes.
- Redis configuration path used by the available recipe: `/etc/redis/6379.conf`.

## Credentials

**Detection Summary**: 1 reported credential in 1 file; the value is not present in the supplied structured execution analysis and requires verification.

**Source**:

- **Provider**: Reported as hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext value
- **Value reported**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the reported Redis instance on port `6379`
- **Validation status**: The supplied structured execution analysis does not contain this assignment or value. Confirm it against the complete recipe before migration.
- **Migration handling**:
  - Store the confirmed value in an encrypted Ansible Vault variable.
  - Do not commit it to `defaults/main.yml`, task files, templates, or inventory.
  - Render or pass it to Redis configuration through a protected variable.
  - Use restrictive permissions if the password is written to `/etc/redis/6379.conf`.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, database credentials, or external secret-manager URLs were detected in the analyzed files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- Redis service unit or service name supplied by the external Redis implementation
- Memcached configuration file supplied by the external Memcached implementation
- Memcached service unit supplied by the external Memcached implementation

**Service endpoints to check**:

- Redis TCP port: `6379`
- Memcached port: Obtain from the external `memcached` implementation before writing a validation check.
- Unix sockets: None specified.
- Network interfaces: None specified; binding behavior is delegated to the missing Redis and Memcached recipes.

**Templates rendered**:

- None in the analyzed cookbook.
- External cookbook template count and paths must be obtained from the selected Ansible implementations.

**Configuration cleanup to verify**:

The following directives must not remain in `/etc/redis/6379.conf` after migration:

```text
replica-serve-stale-data
replica-read-only
repl-ping-replica-period
client-output-buffer-limit
replica-priority
```

## Pre-flight checks

```bash
# Verify the Redis configuration file.
test -f /etc/redis/6379.conf

# Verify the Redis port configuration without exposing credentials.
grep -E '^port[[:space:]]+6379([[:space:]]|$)' /etc/redis/6379.conf

# Verify that removed directives are absent.
! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)([[:space:]]|$)' /etc/redis/6379.conf

# Verify the Redis log directory.
stat -c '%A %U %G %n' /var/log/redis
# Expected: drwxr-xr-x redis redis /var/log/redis

# Use the service name supplied by the external Redis implementation.
systemctl status <verified-redis-service>
systemctl is-enabled <verified-redis-service>
systemctl is-active <verified-redis-service>

# Verify Redis is listening on TCP port 6379.
ss -ltnp | grep ':6379'

# Use a protected credential mechanism; do not place the password directly
# in shell history or the process command line.
redis-cli -p 6379 --askpass PING
redis-cli -p 6379 --askpass INFO server

# Verify unauthenticated access is rejected when Redis authentication is enabled.
redis-cli -p 6379 PING

# Inspect the Redis process and recent service logs.
pgrep -a redis
journalctl -u <verified-redis-service> --since "15 minutes ago"

# Verify the individually named Memcached instance using externally verified values.
systemctl status <verified-memcached-service>
systemctl is-enabled <verified-memcached-service>
systemctl is-active <verified-memcached-service>
ss -ltnp | grep ':<verified-memcached-port>'
```

Expected Redis results:

- `/etc/redis/6379.conf` exists.
- Redis listens on TCP port `6379`.
- The five removed directives are absent.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- Authenticated Redis `PING` returns `PONG` when authentication is confirmed.
- Unauthenticated `PING` fails with an authentication-required error when authentication is enabled.

Memcached service and port checks must remain based on values verified from the external `memcached` implementation rather than values invented from this cookbook.