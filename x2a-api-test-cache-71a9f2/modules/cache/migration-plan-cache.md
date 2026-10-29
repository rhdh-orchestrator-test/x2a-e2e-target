---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis instance on port `6379`, enables Redis authentication, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and attempts to include Memcached, Redis, and the Redis enable recipes. The referenced dependency recipes are unavailable in the supplied execution tree, so only `cache::default` is directly executable from the analyzed cookbook. Memcached endpoint and package details must be obtained from the restored dependency or a separately defined Ansible role.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Authenticated Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` is set to `redis_secure_password_123`; `replicaservestaledata` is assigned `nil`
  - Log directory: `/var/log/redis`
  - Log directory owner/group: `redis:redis`
  - Log directory mode: `0755`
  - Replication directives removed:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

No Memcached port, socket, configuration path, service name, or instance settings are available in the analyzed cookbook. The Ansible implementation must not invent Memcached endpoint values.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are present in the execution tree.

**Templates:**
```text
```

No templates are rendered by the analyzed recipe.

**Attributes:**
```text
```

No attribute files are present in the execution tree. The Redis server collection is assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in the following order. The Redis server assignment is recipe logic and is not represented as a separate resource in the supplied structured execution tree.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - Assigns one Redis server configuration to `node['redisio']['servers']`.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled.
   - Attempts to include the external `redisio` recipe.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - Attempts to include `redisio::enable`.

   **Execution details:**

   - **Memcached dependency inclusion**
     - Executes `include_recipe 'memcached'`.
     - The recipe is unavailable: `memcached Recipe file not found`.
     - No Memcached package, service, port, template, or configuration resource is present in the supplied execution tree.

   - **Redis server assignment**
     - Defines exactly one Redis configuration item:
       ```ruby
       {
         'port' => '6379',
         'requirepass' => 'redis_secure_password_123',
         'replicaservestaledata' => nil
       }
       ```
     - The Ansible implementation should represent this as one Redis instance with integer port `6379`.
     - The password must be moved to Ansible Vault, an AAP credential, or another approved secret-management system.

   - **Redis log directory**
     - Uses one `directory` resource for `/var/log/redis`.
     - Sets owner to `redis`.
     - Sets group to `redis`.
     - Sets mode to `0755`.
     - Enables recursive creation.

   - **Redis dependency inclusion**
     - Executes `include_recipe 'redisio'`.
     - The recipe is unavailable: `redisio Recipe file not found`.
     - No Redis package installation, service declaration, configuration template, or Redis user creation is present in the supplied execution tree.

   - **Redis configuration cleanup**
     - Uses one `ruby_block` resource named `fix_redis_config`.
     - Checks whether `/etc/redis/6379.conf` exists.
     - Removes lines matching:
       ```text
       ^replica-serve-stale-data.*$
       ^replica-read-only.*$
       ^repl-ping-replica-period.*$
       ^client-output-buffer-limit.*$
       ^replica-priority.*$
       ```
     - Rewrites the file in place.
     - The Ansible implementation should use `ansible.builtin.replace` or a controlled template, conditionally applying the change only when the file exists.

   - **Redis enablement**
     - Executes `include_recipe 'redisio::enable'`.
     - The recipe is unavailable: `redisio::enable Recipe file not found`.
     - The intended result is for Redis to start and be enabled at boot.
     - The exact systemd unit name must be determined from the target operating system and installed Redis package.

   **Authoritative resource execution sequence:**

   1. Attempt `include_recipe 'memcached'`; recipe unavailable.
   2. Create `directory[/var/log/redis]`.
   3. Attempt `include_recipe 'redisio'`; recipe unavailable.
   4. Execute `ruby_block[fix_redis_config]`.
   5. Attempt `include_recipe 'redisio::enable'`; recipe unavailable.

   The Redis server assignment occurs as recipe logic but is not shown as a separate resource in the structured execution tree.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`, according to cookbook metadata
- `redisio`, with no version constraint, according to cookbook metadata

**System package dependencies**:

- None are explicitly shown in the execution tree.
- The target operating system’s Redis package must be identified before implementation.
- No Memcached package can be identified from the supplied cookbook analysis.

**Service dependencies**:

- Redis is intended to be configured and enabled through `redisio` and `redisio::enable`, but both recipes are unavailable.
- Memcached is intended to be included through `memcached`, but that recipe is unavailable.
- No exact service unit names are available from the analyzed files.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded literal
- **Literal value currently present**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on port `6379`

The Ansible migration must move this value into Ansible Vault, an AAP credential, or another approved secret-management integration. It must not be committed in plaintext to role defaults, inventory, templates, or variable files.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

Dependency-owned files that cannot be asserted from the analyzed cookbook:

- Redis systemd unit path
- Memcached configuration path
- Memcached log path
- Redis package-specific data directory
- Redis package-specific log file

**Service endpoints to check**:

- Redis TCP port: `6379`
- Redis Unix socket: none specified
- Memcached port: not specified

**Templates rendered**:

- None; render count: `0`

**Configuration transformations to verify**:

`/etc/redis/6379.conf` must not contain active lines beginning with:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Redis instance: service status
systemctl status redis
systemctl status redis-server

# Redis instance: confirm the verified service unit is enabled
systemctl is-enabled redis
systemctl is-enabled redis-server

# Redis instance: verify the TCP endpoint
ss -tlnp | grep ':6379'
netstat -tlnp | grep ':6379'

# Redis instance: unauthenticated access should require authentication
redis-cli -p 6379 PING

# Redis instance: authenticated connectivity
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' \
  redis-cli -p 6379 PING

# Redis instance: verify authentication configuration without exposing the password
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' \
  redis-cli -p 6379 CONFIG GET requirepass

# Redis instance: verify configuration file and required port
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Redis instance: verify removed directives are absent as active configuration lines
! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Redis instance: verify log directory ownership and permissions
test -d /var/log/redis
stat -c '%U %G %a %n' /var/log/redis
sudo -u redis test -w /var/log/redis

# Redis instance: inspect runtime and replication state
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' \
  redis-cli -p 6379 INFO server

REDISCLI_AUTH='<retrieve-from-secure-secret-store>' \
  redis-cli -p 6379 INFO replication

# Memcached dependency: execute only after its service and port are defined
systemctl status <verified-memcached-service>
ss -tlnp | grep ':<verified-memcached-port>'
```

Expected Redis results:

- The verified Redis service is active and enabled.
- Redis listens on TCP port `6379`.
- Unauthenticated `PING` returns an authentication-required error.
- Authenticated `PING` returns `PONG`.
- `/etc/redis/6379.conf` exists and configures port `6379`.
- The five specified replication-related directive families have no active lines.
- `/var/log/redis` exists with ownership `redis:redis` and mode `0755`.
- The Redis password is not exposed in migration logs or command output.

Memcached validation must wait until the missing dependency supplies a verified service name and port.