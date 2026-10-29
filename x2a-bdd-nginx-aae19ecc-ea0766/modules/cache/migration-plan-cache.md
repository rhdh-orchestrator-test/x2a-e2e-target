---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures Memcached and one Redis instance through the external `memcached` and `redisio` cookbooks. The local recipe creates `/var/log/redis`, defines Redis on port `6379` with password authentication, removes five replication-related directive patterns from `/etc/redis/6379.conf`, and enables Redis. The dependency recipes are absent from the supplied execution tree, so Memcached package, port, configuration, and service details, as well as Redis package and service-unit details, must be obtained from the selected Ansible roles or the original dependency cookbooks. Source-level Redis settings and credential details require manual verification against `cookbooks/cache/recipes/default.rb`.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server configured by `redisio`**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication through `requirepass`; source-reported password is `redis_secure_password_123` and must be moved to Ansible Vault; Redis log directory is `/var/log/redis`, owned by `redis:redis` with mode `0755`; `replicaservestaledata` is source-reported as `nil`; five replication-related directive patterns are removed after configuration generation.
  - Service Name: Not available from the supplied `redisio` dependency analysis

- **Memcached**: Memcached cache instance referenced by the local recipe
  - Location/Path: Not available because the external `memcached` recipe is missing
  - Port/Socket: Not available from the supplied local execution tree
  - Key Config: Must be obtained from the selected Ansible Memcached role or the source `memcached` cookbook
  - Package: Not available from the supplied local execution tree
  - Service Name: Not available from the supplied local execution tree

Do not invent Memcached package, port, configuration, or service values. Redis package and service-unit names are also unconfirmed because the `redisio` dependency recipes are unavailable.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
```

**Providers:**

```text
None
```

**Templates:**

```text
None
```

**Attributes:**

```text
None
```

**Files:**

```text
None
```

The following dependency recipe files are referenced by the local recipe but are missing from the supplied cookbook:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Defines one Redis server with source-reported port `6379`, password authentication, and `replicaservestaledata` set to `nil`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - Runs `ruby_block[fix_redis_config]`.
   - Includes the external `redisio::enable` recipe.
   - No `.each` loops were identified.

   **Execution details:**

   1. **Include Memcached**
      - Executes `include_recipe 'memcached'`.
      - The dependency recipe is missing from the supplied execution tree.
      - Migration must use a separate Ansible Memcached role or task include.
      - Package name, port, configuration path, and service name require verification from the selected implementation.

   2. **Configure the Redis server definition**
      - Source-reported assignment:
        ```ruby
        node.default['redisio']['servers'] = [
          {
            'port' => '6379',
            'requirepass' => 'redis_secure_password_123',
            'replicaservestaledata' => nil
          }
        ]
        ```
      - This defines exactly one Redis instance on port `6379`.
      - The assignment and values require manual verification against `cookbooks/cache/recipes/default.rb`, because the structured analysis does not expose the recipe contents.
      - Store the Redis password in Ansible Vault rather than plaintext.
      - Preserve the intended `replicaservestaledata` value of `nil`, subject to the selected Redis role’s behavior.
      - Generate `/etc/redis/6379.conf` if matching the Chef layout.

   3. **Create the Redis log directory**
      - Resource: `directory[/var/log/redis]`
      - Creates `/var/log/redis` recursively.
      - Sets owner to `redis`.
      - Sets group to `redis`.
      - Sets mode to `0755`.
      - Ensure the Redis user and group exist before applying ownership.

   4. **Include Redis**
      - Executes `include_recipe 'redisio'`.
      - The dependency recipe is missing from the supplied execution tree.
      - Use a Redis Ansible role or explicit tasks to install and configure Redis.
      - The local recipe does not provide a confirmed package resource, service resource, or configuration template.

   5. **Remove selected Redis configuration directives**
      - Resource: `ruby_block[fix_redis_config]`
      - Targets `/etc/redis/6379.conf`.
      - If the file exists, removes lines matching the following source-reported patterns:
        ```text
        ^replica-serve-stale-data.*$
        ^replica-read-only.*$
        ^repl-ping-replica-period.*$
        ^client-output-buffer-limit.*$
        ^replica-priority.*$
        ```
      - The target path, patterns, and behavior require manual source verification because they are not exposed in the structured analysis.
      - Run cleanup after the Redis role generates the configuration.
      - Preserve conditional behavior when the file does not exist.
      - Use scoped Ansible `replace` tasks, one per directive, and notify a restart or reload only when a change occurs.
      - Do not introduce an unconditional service restart.

   6. **Enable Redis**
      - Executes `include_recipe 'redisio::enable'`.
      - The dependency recipe is missing from the supplied execution tree.
      - Enable and start the Redis service associated with port `6379`.
      - Determine the actual service unit name from the selected Ansible role and target platform.

## Dependencies

**External cookbook dependencies**:

- `memcached` version constraint `~> 6.0`
- `redisio` with no version constraint

**System package dependencies**:

- No packages are installed directly by the local recipe.
- No package names are confirmed because the external dependency recipes are missing.
- Obtain package names from the selected Ansible Memcached and Redis implementations rather than inferring them from this cookbook.

**Service dependencies**:

- Memcached service: referenced through the missing `memcached` recipe; service name unavailable.
- Redis service for port `6379`: referenced through the missing `redisio` and `redisio::enable` recipes; service name unavailable.

## Credentials

**Detection Summary**: 1 source-reported credential in 1 file; detection requires manual verification.

**Source**:
  - **Provider**: Hardcoded in a Chef recipe
  - **URL**: None detected
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Source-reported hardcoded plaintext Chef node attribute assignment
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on TCP port `6379`
- **Verification status**: The structured analysis does not expose the assignment or credential-detection result; verify against the recipe source before migration.

Migration requirements:

- Store the password in Ansible Vault, such as the variable `redis_password`.
- Do not place the plaintext value in ordinary `group_vars`, `host_vars`, or committed defaults.
- Render the secret with restrictive permissions, typically mode `0600` where compatible with the selected Redis role.
- Confirm that Redis clients use the migrated secret.
- No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, database connection strings, API keys, or token attributes were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- Memcached configuration path: unavailable until the external dependency implementation is selected

**Service endpoints to check**:

- Redis TCP port `6379`
- Memcached port: unavailable from the supplied cookbook analysis
- Unix sockets: none identified

**Templates rendered**:

- None; no local templates are present or referenced.
- Render count: `0`

**Configuration post-processing**:

Verify that `/etc/redis/6379.conf` does not contain active lines matching:

```text
^replica-serve-stale-data.*$
^replica-read-only.*$
^repl-ping-replica-period.*$
^client-output-buffer-limit.*$
^replica-priority.*$
```

## Pre-flight checks:

```bash
# Redis instance: service status and enablement
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>
ps aux | grep '[r]edis'

# Redis instance: configuration and process
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Redis instance: authentication and connectivity
export REDISCLI_AUTH='<retrieve-securely-from-ansible-vault-or-approved-secret-store>'
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
redis-cli -p 6379 CONFIG GET port
unset REDISCLI_AUTH

# Redis instance: listening port
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'
lsof -nP -iTCP:6379 -sTCP:LISTEN

# Redis instance: log directory
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis
find /var/log/redis -maxdepth 1 -type f -print

# Redis instance: logs
journalctl -u <redis-service-name> --no-pager -n 100

# Memcached instance: service status
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>

# Memcached instance: endpoint
ss -ltnp | grep ':<memcached-port>'
```

Expected results:

- The Redis service for port `6379` is enabled and active.
- Redis is running with `/etc/redis/6379.conf`.
- Redis responds with `PONG` and reports TCP port `6379`.
- Redis listens on TCP port `6379`.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- The five source-reported directives have no active matching lines.
- Redis logs contain no configuration, authentication, port-binding, or permission errors.
- Memcached checks must be populated with the actual service name, port, and configuration path from the selected Ansible implementation before validation.