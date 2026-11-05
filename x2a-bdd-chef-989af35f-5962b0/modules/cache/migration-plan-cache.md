---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The local recipe includes Memcached, defines one Redis server on port `6379` with password authentication, creates `/var/log/redis`, removes five replication-related directives from `/etc/redis/6379.conf`, and enables Redis. The dependency recipe implementations are unavailable, so Memcached’s package, service name, configuration path, port, and bind address must be confirmed before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache instance managed by `redisio`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication is enabled. The source defines `requirepass` as `redis_secure_password_123` and sets `replicaservestaledata` to `nil`.
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Post-processing: Removes active lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` when the configuration file exists.
  - Service name: Defined by the unavailable `redisio` dependency; confirm before implementation.

- **Memcached**: Memcached cache instance provided by the external `memcached` cookbook
  - Location/Path: Not available from the supplied source
  - Port/Socket: Not specified by the supplied source
  - Key Config: Package, configuration path, bind address, port, and service name are defined by the unavailable dependency recipe and must be confirmed before migration.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are shown in the execution tree.

**Templates:**
```text
```

No templates are shown in the execution tree.

**Attributes:**
```text
```

No attribute files are shown in the execution tree. Redis configuration is assigned inline in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The included `memcached` and `redisio` dependency recipe files are unavailable and are not listed as local files.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The dependency implementation is unavailable. Obtain its package names, configuration files, service name, bind address, port, and enablement behavior before implementing the Memcached Ansible tasks.
   - Defines exactly one Redis server:
     - Instance: Redis server on port `6379`
     - Port: `6379`
     - Password authentication: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `directory[/var/log/redis]` recursively with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
   - Includes the external `redisio` recipe.
   - The dependency is expected to consume the Redis server definition and create the Redis installation and configuration. Its package and service behavior are unavailable from the supplied execution tree.
   - Executes `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Does not explicitly notify or restart Redis after modifying the file.
   - Includes `redisio::enable`.
   - The dependency is expected to enable Redis at boot. Confirm the generated service name before creating the Ansible service task.
   - Iterations: No `.each` loop is present. The Redis server collection contains exactly one item: Redis server on port `6379`.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package names are declared directly in the local recipe.
- The `memcached` and `redisio` dependency implementations are unavailable, so package names cannot be confirmed from the supplied source.
- Do not infer package names solely from cookbook names.

**Service dependencies**:

- Memcached service behavior is defined by the unavailable `memcached` recipe.
- Redis service enablement is defined by the unavailable `redisio::enable` recipe.
- Exact service names are unavailable and must be confirmed from the dependency implementations or generated service units.

**Platform support**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded inline recipe value
- **Usage context**: Redis `requirepass` authentication for the Redis server on port `6379`
- **Migration handling**: Store the password in Ansible Vault, preferably as:
  ```yaml
  redis_password: "{{ vault_redis_password }}"
  ```
  Render or manage the Redis configuration with the vaulted value. Avoid exposing the password in command arguments where possible.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, cloud secret-manager references, environment-variable secrets, TLS certificates, private keys, or database connection strings were detected in the available source.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

The Redis data directory, package-managed configuration directories, and exact log file paths must be confirmed from the `redisio` dependency.

**Service endpoints to check**:

- Redis server on port `6379`
- Memcached: port not specified by the supplied source
- Unix sockets: none specified
- Network bind address: not specified

**Configuration directives to verify in `/etc/redis/6379.conf`**:

The following directives must not remain as active configuration lines:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

**Templates rendered**:

- None shown in the execution tree; render count: `0`

## Pre-flight checks

```bash
# Redis service discovery and status
systemctl list-units --type=service | grep -i redis
systemctl list-unit-files | grep -i redis
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Redis configuration and endpoint
test -f /etc/redis/6379.conf
ss -tlnp | grep ':6379'
grep -nE '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf
! grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Redis authentication and connectivity
redis-cli -p 6379 PING
redis-cli -p 6379 -a '<redis-password-from-vault>' PING
redis-cli -p 6379 -a '<redis-password-from-vault>' INFO server
redis-cli -p 6379 -a '<redis-password-from-vault>' INFO replication

# Redis log directory
test -d /var/log/redis
stat -c '%U %G %a %n' /var/log/redis

# Redis logging destination and recent logs
grep -E '^[[:space:]]*logfile[[:space:]]+' /etc/redis/6379.conf
journalctl -u redis --no-pager -n 50

# Memcached dependency and service discovery
# Confirm the package, service name, configuration path, bind address, and port
systemctl list-units --type=service | grep -i memcached
systemctl list-unit-files | grep -i memcached
systemctl status <confirmed-memcached-service>
systemctl is-enabled <confirmed-memcached-service>
systemctl is-active <confirmed-memcached-service>

# Memcached endpoint and configuration
grep -E '(^|[[:space:]])(-p|port)[[:space:]]' <confirmed-memcached-config>
ss -tlnp | grep '<confirmed-memcached-port>'

# Memcached protocol check using the confirmed endpoint
printf 'version\r\nquit\r\n' | nc <confirmed-memcached-host> <confirmed-memcached-port>
```