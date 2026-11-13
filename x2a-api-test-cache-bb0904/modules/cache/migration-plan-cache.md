---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two caching services: the `memcached` instance using Memcached on TCP and UDP port `11211`, and one Redis server on port `6379`. Memcached is started and enabled through the `memcached_instance` custom resource with 64 MB memory, a wildcard listen address, 1,024 maximum connections, and a 1 MB maximum object size. Redis uses `/run/redis` as its PID directory, creates `/var/log/redis` with Redis ownership, removes five replication-related directives from `/etc/redis/6379.conf`, and is enabled after configuration. Redis authentication currently uses the hardcoded password `redis_secure_password_123`, which must be migrated to Ansible Vault. The Redis recipe and the Memcached provider implementation are unavailable in the supplied execution tree, so the migration must preserve only the explicitly observed behavior.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached caching service
  - Resource: `memcached_instance[memcached]`
  - Memory: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: Attribute-driven; no default value is defined in the supplied attribute file
  - Ulimit: `1024`
  - Experimental options: Empty list
  - Extra CLI options: Empty list
  - Version: `nil`; no explicit Memcached version is configured
  - Actions: Start and enable
  - Service user: Passed as `service_user`; the resolved username is not available in the supplied files

- **`redis`**: Redis caching service
  - Server count: `1`
  - Port: `6379`
  - Password: `redis_secure_password_123` in the source; migrate to Ansible Vault
  - PID directory: `/run/redis`
  - Configuration file: `/etc/redis/6379.conf`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Recursive log directory creation: Enabled
  - Removed directives:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

The Redis configuration is assigned as a one-element collection containing the server on port `6379`. No generic multi-instance loop should be introduced.

## File Structure

The following files are included in the supplied directory listing and execution analysis.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider file was supplied. The `memcached_instance` provider belongs to the external `memcached` cookbook, but its provider path was not provided and must not be fabricated.

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

The following files were listed in the directory but are not shown as executed by the supplied execution tree:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

## Module Explanation

The cookbook performs operations in the following order.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Assigns one Redis server on port `6379` with password `redis_secure_password_123`.
   - Sets `replicaservestaledata` to `nil`.
   - Sets `redisio['base_piddir']` to `/run/redis`.
   - Includes `redisio`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block[fix_redis_config]`.
   - Includes `redisio::enable`.
   - Redis configuration must be completed before the enable/start operation.
   - The `fix_redis_config` block reads `/etc/redis/6379.conf` only when the file exists, removes the five specified directive families, and writes the modified file back to the same path.
   - The equivalent Ansible configuration task must remove complete matching lines:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - The Redis password must be stored in Ansible Vault rather than as plaintext in the playbook.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates exactly one `memcached_instance[memcached]` resource.
   - Configures memory to `64` MB.
   - Configures TCP port `11211`.
   - Configures UDP port `11211`.
   - Configures listen address `0.0.0.0`.
   - Configures maximum connections to `1024`.
   - Passes `service_user` as the service user.
   - Configures maximum object size to `1m`.
   - Reads the `threads` value from `node['memcached']['threads']`; no default is supplied in the available attributes.
   - Sets experimental options to an empty list.
   - Sets extra CLI options to an empty list.
   - Sets the ulimit to `1024`.
   - Starts and enables the `memcached` service.
   - Uses no supplied templates.
   - The provider implementation is external and unavailable; do not infer provider-specific behavior.
   - The Ansible migration must install the platform-appropriate Memcached package after validating the target operating system. The supplied source does not identify a package name.
   - The Memcached configuration must preserve the observed memory, TCP, UDP, listen, maximum connection, object size, and ulimit values.
   - The `threads` value must be explicitly confirmed before being assigned in Ansible.

3. **`redisio`** (`redisio` recipe file unavailable):
   - Is included after the Redis server configuration and PID directory are assigned.
   - Must configure exactly one Redis server on port `6379`.
   - Must configure Redis authentication using the migrated vaulted password.
   - Must use `/run/redis` as the base PID directory.
   - Must ensure the Redis service account exists before creating `/var/log/redis`.
   - Must not infer additional packages, service names, templates, replication behavior, or configuration paths beyond the observed values.

4. **`redisio::enable`** (`redisio::enable` recipe file unavailable):
   - Is included last.
   - Must enable and start the Redis service after the Redis configuration exists, `/var/log/redis` has been created, and the five unwanted directives have been removed from `/etc/redis/6379.conf`.
   - The exact service resource, restart behavior, and provider implementation are unavailable.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No explicit `package` resources are present in the supplied recipes.
- The external `memcached_instance` provider and unavailable `redisio` implementation may require system packages.
- Exact package names are not present in the supplied execution tree and must be validated for the target operating system before migration.

**Supported operating systems**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Service dependencies**:

- The Redis service account must exist before `/var/log/redis` is created with Redis ownership.
- Redis configuration must be created before the Redis service is enabled and started.
- Memcached must be started and enabled.
- Redis must be enabled and started.

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:

- **Provider**: Hardcoded Chef attribute
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Value in source**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in a Chef recipe
- **Usage context**: Redis authentication for the server listening on port `6379`
- **Migration storage**: Ansible Vault variable such as `redis_requirepass`
- **Migration handling**: Pass the vaulted value to the Redis configuration without committing the plaintext password to ordinary variables or playbooks.

No data bags, encrypted data bags, Chef Vault items, CyberArk integrations, Conjur variables, environment-variable secrets, TLS certificate references, database connection strings, API keys, or token attributes were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- The platform-specific Memcached configuration file
- The platform-specific Memcached log path, if configured; `/var/log/memcached` is present as an attribute but is not explicitly created by the supplied recipe

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Unix sockets: None configured or detected

**Templates rendered**:

- None; render count: `0`

**Configuration transformations**:

- Remove matching lines for five directive families from `/etc/redis/6379.conf` when the file exists.
- No Chef templates are rendered.
- No static files are deployed.

## Pre-flight checks:

```bash
# Confirm the service units available on the target system.
systemctl list-unit-files | grep -E '^(memcached|redis|redis-server)'

# Confirm Memcached status and enablement for the named memcached instance.
systemctl status memcached
systemctl is-enabled memcached

# Confirm Redis status and enablement for the named redis instance.
systemctl status redis || systemctl status redis-server
systemctl is-enabled redis || systemctl is-enabled redis-server

# Validate the Memcached TCP endpoint for memcached.
ss -tlnp | grep ':11211'

# Validate the Memcached UDP endpoint for memcached.
ss -ulnp | grep ':11211'

# Confirm Memcached responds on the named memcached instance.
printf "version\r\n" | nc -w 2 127.0.0.1 11211

# Inspect the platform-specific Memcached configuration.
grep -E '(^-m |^memcached_memory|memory|^-p |^-U |^-l |^-c |^-t )' /etc/memcached.conf

# Validate the Redis configuration file for the named redis instance.
test -f /etc/redis/6379.conf && echo "Redis configuration exists"
grep -E '^(port|requirepass|pidfile|dir|logfile)' /etc/redis/6379.conf

# Confirm the five unwanted Redis directive families are absent.
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis directives remain"
  exit 1
else
  echo "Unwanted Redis directives are absent"
fi

# Validate the Redis endpoint for the named redis instance.
ss -tlnp | grep ':6379'

# Confirm unauthenticated Redis access is rejected.
redis-cli -p 6379 PING

# Confirm authenticated Redis access using the Ansible Vault value.
REDISCLI_AUTH='<redis-password-from-Ansible-Vault>' redis-cli -p 6379 PING

# Inspect Redis server information using the vaulted password.
REDISCLI_AUTH='<redis-password-from-Ansible-Vault>' redis-cli -p 6379 INFO server

# Validate Redis log directory ownership and mode.
stat -c '%A %U %G %n' /var/log/redis
find /var/log/redis -maxdepth 1 -type f -print

# Validate the Redis PID directory.
ls -ld /run/redis

# Validate Memcached and Redis processes individually.
ps aux | grep '[m]emcached'
ps aux | grep '[r]edis-server'

# Review service logs for the named instances.
journalctl -u memcached --no-pager -n 50
journalctl -u redis --no-pager -n 50 || journalctl -u redis-server --no-pager -n 50

# Validate all configured endpoints together.
ss -tlnp | grep -E ':(6379|11211)'
ss -ulnp | grep ':11211'
```

Expected final endpoint and directory state:

- `memcached` listens on TCP `11211` and UDP `11211`.
- `memcached` uses 64 MB memory, listen address `0.0.0.0`, and 1,024 maximum connections.
- `redis` listens on TCP port `6379`.
- Redis authentication succeeds only with the vaulted password.
- `/var/log/redis` exists with mode `0755`, owner `redis`, and group `redis`.
- `/run/redis` exists for Redis PID handling.
