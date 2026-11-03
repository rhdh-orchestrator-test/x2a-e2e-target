---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer using Redis and Memcached. The analyzed execution tree confirms inclusion of the external `memcached`, `redisio`, and `redisio::enable` recipes, creation of `/var/log/redis`, and execution of `ruby_block[fix_redis_config]`. Redis port `6379`, the Redis password, the Redis configuration path, the replication directives, dependency version constraints, and detailed resource properties are reported by the source plan but are not verifiable from the supplied structured analysis. These values must be confirmed against the underlying recipe and metadata before implementation. External cookbook package, service, template, and provider details are not available.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Reported Redis cache instance; detailed configuration is unverified from the supplied execution analysis.
  - Location/Path: Redis configuration is reported at `/etc/redis/6379.conf`; unverified
  - Port/Socket: TCP `6379`; unverified
  - Key Config: `requirepass` is reported as `redis_secure_password_123`; `replicaservestaledata` is reported as `nil`; both require source verification
  - Log directory: `/var/log/redis`; directory resource is confirmed, while ownership, group, mode, and Redis log behavior require verification
  - Enablement: `redisio::enable` is included; the resulting service name and exact service behavior are unverified

- **Memcached instance included by the external `memcached` recipe**: The cookbook includes Memcached, but the analyzed files do not identify an exact instance name, package, service, port, socket, configuration path, or template.
  - Location/Path: Not specified
  - Port/Socket: Not specified; conventional port `11211` must not be treated as confirmed
  - Key Config: Must be obtained from the external `memcached` cookbook or explicitly defined in the Ansible role

No `.each` loops are present in the supplied analysis. The reported Redis collection contains one item for port `6379`, but the collection assignment is not represented as an execution-tree resource.

## File Structure

Only the following recipe file is present in the supplied execution tree.

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

The supplied execution tree does not list `metadata.rb`, although dependency information is reported separately in the source plan and requires verification.

## Module Explanation

The cookbook performs operations in the reported source order. Only the recipe inclusions and the two named resources are confirmed by the supplied execution-tree analysis. Redis settings and Ruby block behavior marked as unverified must be confirmed from `cookbooks/cache/recipes/default.rb`.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe. The include is confirmed; the external recipe source is unavailable.
   - Assigns a Redis server collection containing a reported server on port `6379`. This node assignment is source logic, not an execution-tree resource, and requires verification.
   - The reported Redis settings are:
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `directory[/var/log/redis]`. The resource is confirmed; reported owner `redis`, group `redis`, mode `0755`, and recursive creation require verification.
   - Includes the external `redisio` recipe. The include is confirmed; package, service, configuration, template, data-directory, and log behavior are unavailable.
   - Executes `ruby_block[fix_redis_config]`. The resource name is confirmed. Its reported target path `/etc/redis/6379.conf` and removal of the following directives require verification:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Includes `redisio::enable`. The include is confirmed; the resulting Redis service name and enablement behavior require verification.

Ansible implementation requirements:

- Store the reported Redis password in Ansible Vault or an approved secret manager if source verification confirms that it is used.
- Confirm the Redis instance name, configuration path, service name, package, and port before implementing service tasks.
- Incorporate replication-directive removals into the Redis configuration template when possible, preventing a later template task from restoring them.
- If post-processing is required, apply it only after the Redis configuration exists and target `/etc/redis/6379.conf` only after that path is verified.
- Do not invent Memcached package, service, port, socket, or template values.

## Dependencies

**External cookbook dependencies**:

- `memcached` — include confirmed; reported version constraint `~> 6.0` is unverified
- `redisio` — include confirmed; reported unconstrained version is unverified

**System package dependencies**:

- No package resources are present in the analyzed `cache` recipe.
- No exact package names are verified.
- Package installation is delegated to the unavailable external `memcached` and `redisio` implementations.

**Service dependencies**:

- Memcached service from the external `memcached` recipe; exact service name is not specified
- Redis service for the reported `6379` instance from `redisio::enable`; exact service name is not specified

## Credentials

**Detection Summary**: 1 credential finding reported in 1 recipe file, but the finding is unverified by the supplied structured analysis.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe, as reported; requires verification
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`; reported and unverified
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value, as reported and unverified
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication through the Redis `requirepass` configuration
- **Ansible migration**:
  - Store the confirmed password in Ansible Vault or an approved external secret manager.
  - Do not place it in ordinary role defaults, committed variable files, or unprotected rendered configuration.
  - Use `no_log: true` for tasks that could expose the value.

No data bag, Chef Vault, Conjur, CyberArk, environment-variable secret, TLS certificate, private key, or database connection string is confirmed by the supplied analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf` — reported path, unverified
- Redis data directory — not specified
- Redis log file — not specified
- Memcached configuration path — not specified

**Service endpoints to check**:

- Redis instance on TCP port `6379` — reported, unverified
- Memcached instance — port not specified
- Unix sockets — none specified
- Network bind address — not specified

**Configuration directives to verify**:

- Redis port configuration for `6379`
- Redis authentication through `requirepass`
- Absence of active lines beginning with:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- None shown in the supplied execution tree.
- Redis and Memcached templates from external dependencies are not present in the analyzed file set.
- Confirm the external implementations before assigning render counts; no template render count is verified.

## Pre-flight checks

### Source and dependency verification

```bash
# Confirm the recipe contents and resource properties.
sed -n '1,240p' cookbooks/cache/recipes/default.rb

# Confirm dependency metadata if metadata.rb is available.
test -f cookbooks/cache/metadata.rb && sed -n '1,240p' cookbooks/cache/metadata.rb

# Confirm the external cookbook implementations are available.
find cookbooks -path '*/recipes/memcached.rb' -o -path '*/recipes/redisio.rb' -o -path '*/recipes/enable.rb'
```

### Redis instance on port 6379

```bash
# Replace redis with the verified service name if it differs.
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

ps aux | grep '[r]edis-server'
ss -tlnp | grep ':6379'
```

Expected result:

- The verified Redis service is enabled and active.
- A Redis process is running for the `6379` instance.
- TCP port `6379` is listening.

### Redis configuration

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result:

- The configuration file exists if source verification confirms this path.
- The file configures Redis on port `6379`.
- Authentication is configured if the reported password is confirmed.
- No active lines match the five reported replication directives.

### Redis authentication

```bash
export REDISCLI_AUTH='<retrieve-from-Ansible-Vault-or-approved-secret-store>'

redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'

unset REDISCLI_AUTH
```

Expected result:

- `PING` returns `PONG`.
- `tcp_port` reports `6379`.
- Authentication behavior matches the verified Redis configuration.

### Redis log directory

```bash
stat -c '%A %U %G %n' /var/log/redis
ls -la /var/log/redis
```

Expected result:

- `/var/log/redis` exists.
- Reported expected permissions are `0755`.
- Reported expected owner and group are `redis:redis`.
- These ownership and permission expectations must be confirmed against the recipe before enforcement.

### Memcached instance

The external cookbook must supply the exact service name and port before these checks are executed.

```bash
# Replace placeholders with values verified from the external memcached cookbook.
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>

ss -tlnp | grep ':<memcached-port>'
printf 'version\r\n' | nc 127.0.0.1 <memcached-port>
```

Expected result:

- The verified Memcached service is enabled and active.
- The verified Memcached port is listening.
- The text protocol returns a version response.

### Final Ansible idempotence check

```bash
ansible-playbook -i inventory cache.yml --check
ansible-playbook -i inventory cache.yml
ansible-playbook -i inventory cache.yml
```

Expected result:

- The second normal run reports no unnecessary changes.
- The Redis `6379` instance remains enabled and active.
- `/var/log/redis` retains the verified ownership, group, and mode.
- Confirmed removed directive patterns do not reappear in the verified Redis configuration file.