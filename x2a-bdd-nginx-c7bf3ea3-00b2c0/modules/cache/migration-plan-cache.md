---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached uses the `memcached_instance` custom resource with port `11211`, UDP port `11211`, 64 MB of memory, a `0.0.0.0` listener, 1,024 maximum connections, and start/enable actions. Redis uses a hardcoded authentication password, `/run/redis` for its PID directory, `/var/log/redis` for logs, and modifies `/etc/redis/6379.conf` to remove five replication-related directives. The `redisio` implementation recipes are unavailable in the supplied execution tree; package-helper and detailed attribute values should therefore be verified against the source before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Package: `memcached`
  - Package version: `nil` in Chef; the platform package manager selects the version
  - Location/Path: `/var/run/memcached`; logs at `/var/log/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1,024 maximum connections, `1m` maximum object size, `0.0.0.0` listener, ulimit `1024`, empty experimental and extra CLI option lists
  - Threads: `node['memcached']['threads']`; no default value is present in the supplied attributes file
  - Service account: Passed as `service_user`; the literal service-user and group values are not present in the supplied attributes
  - Service actions: Start and enable

- **6379**: Redis server instance
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`
  - Key Config: Authentication enabled with `requirepass`; `replicaservestaledata` explicitly set to `nil`; Redis enabled through `redisio::enable`
  - Authentication password: `redis_secure_password_123` in the Chef recipe; migrate to Ansible Vault
  - Configuration cleanup: Remove the following directives from `/etc/redis/6379.conf` when present:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

There are no collection iterations in the supplied execution tree. The Redis server collection contains exactly one configured server entry: `6379`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Relative paths are from the repository root.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider file path was supplied in the execution tree.

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

The following files were present in the directory listing but are not part of the executed recipe flow and should not be migrated as executed modules:

- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb`

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Sets `node['redisio']['servers']` to one Redis server entry named `6379`.
   - Configures Redis port `6379`, the `requirepass` value, and `replicaservestaledata` as `nil`.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`; the referenced `redisio` recipe was not supplied.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes `redisio::enable`; the referenced `redisio::enable` recipe was not supplied.
   - Ansible must implement the observable Redis behavior without inferring unavailable package names, provider paths, templates, or service-unit names.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance['memcached']`.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listener `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental options, and empty extra CLI options.
   - Passes the configured Memcached service user.
   - Reads the thread count from `node['memcached']['threads']`; no value is supplied in the analyzed attributes.
   - Starts and enables the `memcached` service.
   - No provider path was supplied for `memcached_instance['memcached']`; none should be invented.
   - The Ansible implementation should use explicit package, user/group, directory, configuration, and service tasks while preserving both TCP and UDP settings.

3. **Memcached package and filesystem setup** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - This file is present in the directory listing but is not shown as a separately executed recipe.
   - The supplied plan attributes the following setup to the custom resource’s package helper: package `memcached`, a service group, a locked system service user with home `/nonexistent`, comment `Memcached`, shell `/bin/false`, `/var/log/memcached`, and `/var/run/memcached`.
   - These package-helper details require source verification before being treated as confirmed executed resources.
   - Where implemented, `/var/log/memcached` and `/var/run/memcached` use the Memcached service user and group with mode `0755`.

4. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Operates on `/etc/redis/6379.conf` when the file exists.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - The Ansible equivalent must check for the file, remove only matching lines, preserve all other content, remain idempotent, and notify or restart Redis only when the file changes.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `memcached`
- Redis package: not identifiable from the supplied execution tree because the `redisio` recipe is unavailable

**Service dependencies**:

- Memcached service `memcached`
- Redis service enabled through `redisio::enable`; the target distribution and selected Ansible implementation must determine whether the service is `redis-server`, `redis`, or another platform-specific name

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded Chef attribute value
- **URL**: Not detected
- **Path**: Redis server configuration entry on port `6379`

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Usage context**: Redis client authentication for the Redis instance listening on port `6379`

For the Ansible migration:

- Store the password in Ansible Vault.
- Do not place the plaintext value in ordinary inventory, defaults, or committed task files.
- Pass the vaulted variable into the Redis configuration template or module.
- Use `no_log: true` for tasks where the password could appear in output.
- Verify that unauthenticated Redis clients are rejected and authenticated clients receive a successful response.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, API keys, database connection strings, or additional credential namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/memcached`
- `/var/run/memcached`
- `/var/log/redis`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`; bind address must be confirmed from the selected Redis implementation

**Templates rendered**:

- None; no Chef templates were supplied or rendered

**Memcached configuration to verify**:

- Memory: `64` MB
- TCP port: `11211`
- UDP port: `11211`
- Listen address: `0.0.0.0`
- Maximum connections: `1024`
- Maximum object size: `1m`
- Ulimit: `1024`
- Thread value: supplied from `node['memcached']['threads']` and requires verification

**Redis configuration to verify**:

- Port: `6379`
- Authentication password supplied from Ansible Vault
- PID directory: `/run/redis`
- Log directory: `/var/log/redis`
- Removal of the five specified directives from `/etc/redis/6379.conf`

## Pre-flight checks

```bash
# Verify the Memcached instance named memcached.
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
printf "version\r\n" | nc -w 2 127.0.0.1 11211
ls -ld /var/log/memcached
ls -ld /var/run/memcached
ps -ef | grep '[m]emcached'
systemctl show memcached | grep -E 'LimitNOFILE|LimitNPROC'

# Verify the Redis instance named 6379.
# Use the service name selected by the target distribution.
systemctl status redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server
# If the target system uses redis instead:
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|pidfile)' /etc/redis/6379.conf
ls -ld /run/redis
ls -ld /var/log/redis
ss -ltnp | grep ':6379'

# The unauthenticated request must fail with an authentication error.
redis-cli -p 6379 PING

# Populate REDISCLI_AUTH securely during validation; do not expose the password
# in shell history or committed files.
export REDISCLI_AUTH='redis_secure_password_123'
redis-cli -p 6379 PING
unset REDISCLI_AUTH

# Confirm the five unwanted directives are absent.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Review Redis logs using the applicable service name.
journalctl -u redis-server --no-pager -n 100
journalctl -u redis-server --no-pager | grep -Ei 'error|fatal|warning|authentication'

# Network summary for both named instances.
ss -ltnp | grep -E ':(6379|11211)\b'
ss -lunp | grep ':11211'
```