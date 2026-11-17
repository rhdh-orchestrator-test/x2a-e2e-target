---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the `memcached` instance on TCP and UDP port `11211`, and one Redis instance named `6379` on TCP port `6379`. Memcached is started and enabled through the `memcached_instance` custom resource. Redis uses `/run/redis` for its PID directory, creates `/var/log/redis` with `redis:redis` ownership and mode `0755`, removes selected replication directives from `/etc/redis/6379.conf`, and is enabled through `redisio::enable`. The Redis recipes and Memcached provider implementation are not included in the supplied execution tree, so their exact package names, configuration paths, provider paths, and service unit names must be resolved during Ansible implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Platform-specific Memcached configuration path; not exposed by the supplied provider
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: `64` MB memory, `1024` maximum connections, `1m` maximum object size, `1024` ulimit, empty experimental and extra CLI option lists, start and enable actions
  - Worker threads: Referenced through `node['memcached']['threads']`, but no concrete default is supplied
  - Version: `nil`; no explicit version is pinned
  - User: Supplied through `service_user`; the concrete value is not present in the supplied files

- **6379**: Redis server instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`
  - Key Config: `requirepass` set to the protected Redis password, PID directory `/run/redis`, log directory `/var/log/redis`
  - Log directory ownership and mode: `redis:redis`, `0755`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` directives when present
  - Actions: Configure and enable Redis through `redisio` and `redisio::enable`

The Redis server collection contains exactly one item:

- Port: `6379`
- `requirepass`: `redis_secure_password_123`
- `replicaservestaledata`: `nil`

No additional Redis instances are configured.

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

The `memcached_instance[memcached]` custom resource is used, but no provider file path was supplied in the execution tree or directory listing.

**Templates:**
```text
```

No templates are rendered by the supplied execution flow.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The supplied analysis reports seven analyzed files. Three are migration inputs listed above: one cache recipe, one dependency recipe, and one attributes file. The remaining four are present in the supplied directory listing but are not executed or referenced by the supplied execution tree: `recipes/_package.rb` and three SELinux recipes. Their full filenames were not exposed in the supplied plan, so they are intentionally excluded from migration inputs.

## Module Explanation

The cookbook performs operations in this order:

1. **cache::default** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Assigns one Redis server with port `6379`, `requirepass` set to the configured password, and `replicaservestaledata` set to `nil`.
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`; the referenced recipe is not present in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - Includes `redisio::enable`; the referenced recipe is not present in the supplied execution tree.

   Redis configuration cleanup removes matching lines when `/etc/redis/6379.conf` exists:

   - `^replica-serve-stale-data.*$`
   - `^replica-read-only.*$`
   - `^repl-ping-replica-period.*$`
   - `^client-output-buffer-limit.*$`
   - `^replica-priority.*$`

   The original Chef resource does not explicitly notify or restart Redis after modifying the file. The Ansible implementation should preserve that behavior unless the selected Redis package requires a restart.

2. **memcached::default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates exactly one custom resource: `memcached_instance[memcached]`.
   - Starts and enables the `memcached` instance.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, and ulimit `1024`.
   - Passes `service_user` as the service user.
   - Passes empty `experimental_options` and `extra_cli_options` lists.
   - References `node['memcached']['threads']`; no concrete default thread count is supplied.
   - Requires the platform-appropriate Memcached package and service implementation to be resolved because the provider is not supplied.

3. **Redis attribute defaults and configuration inputs** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`):
   - Defines Memcached defaults:
     - `version`: `nil`
     - `memory`: `64`
     - `port`: `11211`
     - `udp_port`: `11211`
     - `listen`: `0.0.0.0`
     - `maxconn`: `1024`
     - `max_object_size`: `1m`
     - `experimental_options`: `[]`
     - `extra_cli_options`: `[]`
     - `ulimit`: `1024`
     - `logfilepath`: `/var/log/memcached`
   - Does not define a concrete `threads` value.
   - The Ansible implementation must preserve the platform default or require an explicit migration variable rather than inventing a thread count.

4. **redisio** (recipe path not supplied):
   - Intended to install and configure Redis for instance `6379`.
   - Exact package names, configuration templates, provider paths, and service unit names are unresolved from the supplied files.

5. **redisio::enable** (recipe path not supplied):
   - Intended to enable the Redis service after configuration.
   - The exact Redis service unit name must be discovered on the target system.

## Dependencies

**External cookbook dependencies**:

- `memcached`
  - Provides `memcached::default`
  - Provides the `memcached_instance[memcached]` custom resource
- `redisio`
  - Referenced by `include_recipe 'redisio'`
  - Recipe source is not present in the supplied execution tree
- `redisio::enable`
  - Referenced after Redis configuration
  - Recipe source is not present in the supplied execution tree

**System package dependencies**:

- Memcached package: exact package name is not exposed by the supplied provider
- Redis package: exact package name is not exposed by the supplied `redisio` recipes
- Resolve both package names against the target operating system and selected Ansible roles; do not infer them from the wrapper cookbook

**Service dependencies**:

- Memcached service for instance `memcached`
- Redis service for instance `6379`
- Exact Redis systemd unit name is not supplied

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext recipe value
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis authentication through the `requirepass` configuration setting
- **Ansible storage**: Move the value to Ansible Vault or an approved external secret manager. Do not commit it to role defaults, `group_vars`, `host_vars`, or templates in plaintext. Ensure validation commands do not print the password.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate paths, private keys, database connection strings, or API tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- `/var/log/memcached`
- The platform-specific Memcached configuration file discovered during implementation

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`, with the actual bind address confirmed from the deployed configuration

**Templates rendered**:

- None; zero Chef templates are rendered by the supplied execution flow

**Unix sockets**:

- None configured or referenced

## Pre-flight checks:

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

printf "version\r\n" | nc -w 2 127.0.0.1 11211
printf "stats\r\n" | nc -w 2 127.0.0.1 11211
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'

# Verify Memcached configuration and log path
ls -ld /var/log/memcached
ls -ld /var/log/memcached/*
# Inspect the platform-specific configuration file and verify:
# memory 64 MB, TCP port 11211, UDP port 11211,
# listen address 0.0.0.0, max connections 1024,
# maximum object size 1m, and ulimit 1024

# Redis instance: 6379
systemctl list-unit-files | grep -E '^redis|redis-server'
# Substitute the confirmed unit name below
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

ss -tlnp | grep ':6379'
redis-cli -h 127.0.0.1 -p 6379 -a '<vault-supplied-password>' PING
# Expected result: PONG

redis-cli -h 127.0.0.1 -p 6379 PING
# Expected result: authentication-required error

# Redis configuration
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|pidfile|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify port 6379 and pidfile configuration.
# Do not expose the password in command output or migration logs.
# Confirm these directives are absent:
# replica-serve-stale-data
# replica-read-only
# repl-ping-replica-period
# client-output-buffer-limit
# replica-priority

# Redis log directory
stat -c '%A %U %G %n' /var/log/redis
# Expected: mode 0755, owner redis, group redis

# Redis PID directory
stat -c '%A %U %G %n' /run/redis
# Confirm that /run/redis exists and is writable by the Redis service account.

# Redis logs; substitute the confirmed service unit name
journalctl -u redis --no-pager -n 100
find /var/log/redis -maxdepth 1 -type f -print
```