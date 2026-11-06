---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The analyzed recipe directly configures one Redis instance, `redis-6379`, on port `6379`, enables authentication, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and invokes the Redis enable recipe. The external dependency recipe implementations are unavailable, so their package names, service resources, templates, and exact Memcached configuration must be verified separately before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-6379**: Redis server configured through `redisio`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with `requirepass`; `replicaservestaledata` set to `nil`; selected replication directives removed after configuration
  - Log Directory: `/var/log/redis`
  - Log Directory Owner/Group: `redis:redis`
  - Log Directory Mode: `0755`
  - Log Directory Creation: Recursive

- **memcached**: Memcached service included through the external `memcached` cookbook
  - Location/Path: Not specified by the analyzed cookbook
  - Port/Socket: Not specified by the analyzed cookbook
  - Key Config: No direct Memcached attributes, ports, templates, packages, or service resources are present in the analyzed recipe
  - Migration Note: Inspect the external dependency cookbook before implementing package, service, binding, or port configuration

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

The metadata file was inspected to identify the cookbook description and dependencies, but it is not included above because the required file structure is restricted to files shown in the execution tree and executable migration inputs.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe with `include_recipe 'memcached'`.
   - The referenced Memcached recipe is unavailable in the supplied execution tree. Do not infer its package name, service name, configuration path, or port.
   - Sets `node.default['redisio']['servers']` to a one-item collection for `redis-6379`:
     - `port`: `'6379'`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` using `directory['/var/log/redis']`:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation enabled
   - Includes the external `redisio` recipe with `include_recipe 'redisio'`.
   - The referenced Redis recipe is unavailable in the supplied execution tree. Its package installation, base configuration, templates, and service resources must be verified separately.
   - Runs `ruby_block['fix_redis_config']`:
     - Operates only when `/etc/redis/6379.conf` exists.
     - Reads the complete configuration file.
     - Removes lines matching:
       - `^replica-serve-stale-data.*$`
       - `^replica-read-only.*$`
       - `^repl-ping-replica-period.*$`
       - `^client-output-buffer-limit.*$`
       - `^replica-priority.*$`
     - Writes the modified content back to `/etc/redis/6379.conf`.
     - Performs no modification when the file does not exist.
   - Includes the external `redisio::enable` recipe with `include_recipe 'redisio::enable'`.
   - The referenced enable recipe is unavailable. Verify the actual Redis service unit before enabling it in Ansible.
   - The recipe contains one configured Redis item, `redis-6379`, on port `6379`.
   - No `.each` loops are present.
   - No templates, custom resources, providers, or static files are shown in the supplied execution tree.
   - No explicit service resource, restart, reload, or notification is present.
   - Ansible should use an idempotent replacement operation for each removed directive and notify a Redis restart handler only if the target implementation requires a restart after configuration changes.

**Visible resources:**

- `directory['/var/log/redis']`
- `ruby_block['fix_redis_config']`

No `group['redis']` resource appears in the supplied execution tree. Do not add a separate group-management operation unless inspection of the external dependency confirms that it is required.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint shown

**System package dependencies**:

- No package names are directly visible in `cookbooks/cache/recipes/default.rb`.
- Package installation is expected to occur in the unavailable `memcached` and `redisio` dependency recipes.
- Verify the dependency implementations and target distribution before selecting package names.

**Service dependencies**:

- Memcached service behavior comes from the unavailable `memcached` dependency.
- Redis installation and service behavior come from the unavailable `redisio` dependency.
- Redis enablement comes from the unavailable `redisio::enable` dependency.
- The configured Redis endpoint is TCP port `6379`.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded literal in the Chef recipe
- **Usage context**: Used as the Redis `requirepass` value for `redis-6379` on port `6379`
- **Migration handling**:
  - Store the value in Ansible Vault or an approved AAP credential or secret integration.
  - Do not commit the literal password to plaintext variables, templates, task files, or defaults.
  - Render the password into Redis configuration with restrictive permissions.
  - Validate authentication without exposing the password in task output, command arguments, or shell history.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate paths, private keys, API tokens, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

The package-managed Redis data directory, service unit, and log file path are not specified by the analyzed cookbook and must be confirmed from the `redisio` dependency or target distribution.

**Service endpoints to check**:

- Redis instance `redis-6379`: TCP `6379`
- Memcached service: Port not specified by the analyzed cookbook
- Unix sockets: None specified
- Network bind address: Not specified

**Templates rendered**:

- None shown in the supplied execution tree

**Configuration transformations to verify**:

- `/etc/redis/6379.conf` exists after Redis configuration.
- The Redis port is configured as `6379`.
- The protected Ansible secret is rendered as the Redis authentication password.
- No lines beginning with the following directives remain:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.

## Pre-flight checks

```bash
# Redis instance: redis-6379
systemctl status redis
systemctl is-enabled redis
ps aux | grep '[r]edis-server'
ss -tlnp | grep ':6379'

# Redis configuration
test -f /etc/redis/6379.conf
grep -E '^(requirepass|port)' /etc/redis/6379.conf

# Verify removed replication directives
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
    echo "Unexpected replication directives remain"
    exit 1
else
    echo "Replication directives were removed"
fi

# Unauthenticated Redis access should be rejected
redis-cli -p 6379 PING

# Authenticated Redis access
REDISCLI_AUTH='RETRIEVE_FROM_PROTECTED_SECRET_STORE' \
  redis-cli -p 6379 PING
# Expected result: PONG

# Redis log directory
stat -c '%U %G %a %n' /var/log/redis
# Expected: redis redis 755 /var/log/redis
ls -lah /var/log/redis

# Redis logs
journalctl -u redis --no-pager -n 100
```

If the Redis dependency uses a different service unit, obtain the exact unit name from the installed package rather than using a wildcard.

```bash
# Memcached service
systemctl status memcached
systemctl is-enabled memcached

# Confirm the port configured by the external memcached dependency
ss -tlnp
```

Do not assume a Memcached port or configuration path until the external `memcached` cookbook has been inspected.