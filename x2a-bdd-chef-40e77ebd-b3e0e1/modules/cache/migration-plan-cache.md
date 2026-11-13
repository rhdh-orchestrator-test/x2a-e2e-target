---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the Memcached instance `memcached` on TCP and UDP port `11211`, and one Redis instance on port `6379`. Memcached is installed, configured, started, and enabled through the external `memcached` cookbook and its `memcached_instance[memcached]` resource. Redis is configured with PID directory `/run/redis`, log directory `/var/log/redis`, and a hardcoded authentication password, followed by cleanup of selected replication directives in `/etc/redis/6379.conf`. The `redisio` and `redisio::enable` recipes are unavailable, so the Redis package name and service unit must be confirmed before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: `/var/run/memcached`, `/var/log/memcached`
  - Port/Socket: TCP `11211`, UDP `11211`
  - Key Config: Listen address `0.0.0.0`, memory `64` MB, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental and additional CLI options
  - Resource: `memcached_instance[memcached]`
  - Actions: `start`, `enable`
  - User: Dependency-defined `service_user`
  - Threads: Value from `node['memcached']['threads']`; no explicit default was provided

- **Redis 6379**: Redis cache service
  - Location/Path: Configuration `/etc/redis/6379.conf`, PID directory `/run/redis`, log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: `requirepass` set to `redis_secure_password_123`; `replicaservestaledata` set to `nil`
  - Log directory ownership: `redis:redis`
  - Log directory mode: `0755`
  - Log directory creation: Recursive
  - Service enablement: Requested through `redisio::enable`
  - Redis package, service unit, user/group behavior, and binary path: Not confirmed because the dependency recipes are unavailable

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider file path was supplied for `memcached_instance[memcached]`. It is an external custom resource whose observable behavior must be reproduced in Ansible.

**Templates:**
```text
```

No rendered templates are present in the supplied execution tree.

**Attributes:**
```text
```

Memcached defaults were inspected from the dependency artifact, but the relevant attribute file is not included in the execution-tree listing.

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` are present.

The `redisio` and `redisio::enable` recipe files were reported as not found and are not available in the supplied execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Assigns Redis server configuration for the single Redis item on port `6379`.
   - Sets the Redis base PID directory to `/run/redis`.
   - Includes the external `redisio` recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Removes selected directives from `/etc/redis/6379.conf` when the file exists.
   - Includes the external `redisio::enable` recipe.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates the `memcached_instance[memcached]` custom resource.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental options, and empty additional CLI options.
   - Passes the Memcached threads value from `node['memcached']['threads']`.
   - Uses the dependency-defined `service_user`.
   - Starts and enables the Memcached service.
   - Installs the confirmed system package `memcached`.
   - Creates the Memcached system group and locked system user.
   - Configures the system user with home `/nonexistent` and shell `/bin/false`.
   - Creates `/var/log/memcached` and `/var/run/memcached` with mode `0755`.
   - Deploys or applies the equivalent Memcached service configuration through the external custom resource.
   - Iterations: None; the recipe creates exactly one named instance, `memcached`.

3. **redisio** (`redisio/recipes/default.rb`):
   - Intended to install and configure the Redis instance on port `6379`.
   - Intended to use `/run/redis` as the base PID directory.
   - Expected to generate `/etc/redis/6379.conf`.
   - Exact package name, service unit, user/group behavior, configuration-generation mechanism, directory creation, and restart behavior are unavailable because the recipe was not found.
   - No supplied recipe path is available for this module.

4. **redisio::enable** (`redisio/recipes/enable.rb`):
   - Intended to enable the Redis service at boot.
   - Exact service unit name and implementation are unavailable because the recipe was not found.
   - No supplied recipe path is available for this module.

5. **ruby_block `fix_redis_config`** (`cookbooks/cache/recipes/default.rb`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Removes complete lines beginning with `replica-serve-stale-data`.
   - Removes complete lines beginning with `replica-read-only`.
   - Removes complete lines beginning with `repl-ping-replica-period`.
   - Removes complete lines beginning with `client-output-buffer-limit`.
   - Removes complete lines beginning with `replica-priority`.
   - Preserves all other configuration content.
   - Writes the file only after applying the content transformation.
   - Has no explicit Chef notification or subscription; do not add an unconditional Redis restart.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, version unconstrained in metadata

**System package dependencies**:

- `memcached` — confirmed by the supplied Memcached dependency recipe
- Redis package — not confirmed because the `redisio` recipe is unavailable

**Service dependencies**:

- Memcached service, managed by `memcached_instance[memcached]`
- Redis service, intended to be enabled by `redisio::enable`; exact unit name is unavailable

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute assignment
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the instance listening on port `6379`
- **Migration handling**: Store the value in Ansible Vault under a variable such as `redis_password`; do not commit it in plaintext defaults. Render it with restrictive permissions, preferably mode `0600` when the complete Redis configuration contains the password.

No data bag, Chef Vault, CyberArk, Conjur, cloud secret manager, environment-variable secret, TLS certificate, private key, database connection string, or additional hardcoded token was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/run/memcached`
- `/var/log/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Redis bind address: not explicitly configured; confirm the generated Redis configuration
- Unix sockets: none explicitly configured

**Templates rendered**:

- None; no templates are present in the supplied execution tree

**Configuration cleanup to verify**:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Confirm the target platform and available package metadata
cat /etc/os-release
command -v apt-get || command -v dnf || command -v yum

# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
printf "version\r\n" | nc -w 2 127.0.0.1 11211
ps -eo user,group,pid,cmd | grep '[m]emcached'
ls -ld /var/log/memcached
ls -ld /var/run/memcached

# Expected Memcached results:
# - The memcached service is enabled and active.
# - TCP and UDP listeners exist on port 11211.
# - The version command returns VERSION <version>.
# - The process runs as the intended non-root service account.
# - Both directories exist with mode 0755 and service-account ownership.

# Redis instance: Redis 6379
# Confirm the missing redisio service unit before replacing the placeholder.
systemctl list-unit-files | grep -i redis
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>
test -f /etc/redis/6379.conf
test -d /run/redis
test -d /var/log/redis
ls -ld /run/redis
ls -ld /var/log/redis
ss -ltnp | grep ':6379'

# Use the vaulted password through an environment variable.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server

# Redis configuration and authentication
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf
grep -E '^requirepass[[:space:]]+' /etc/redis/6379.conf

# The following command should return no lines after cleanup.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Redis directory ownership and permissions
stat -c '%A %U:%G %n' /run/redis /var/log/redis
# Expected: /var/log/redis is owned by redis:redis with mode 0755.

# Redis runtime PID files
find /run/redis -maxdepth 1 -type f -ls

# Redis logging destination and recent service messages
grep -E '^(logfile|syslog-enabled|syslog-ident|loglevel)' /etc/redis/6379.conf
journalctl -u <redis-service-unit> --no-pager -n 50
```

