---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook manages one Memcached instance named `memcached` and one Redis server on port `6379`. The supplied source analysis identifies the Memcached custom resource, Redis directory creation, Redis configuration cleanup, and missing `redisio` recipes. Memcached defaults, package preparation, Redis server values, and the hardcoded Redis password are based on source inspection and require confirmation against the dependency/provider implementations before migration. The Ansible migration must preserve the verified execution order, move the Redis password to Ansible Vault, and avoid inventing unavailable package or service names.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Resource: `memcached_instance[memcached]`
  - Package: `memcached` (source-level package reference)
  - Location/Path: `/var/log/memcached`; `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1024 maximum connections, `1m` maximum object size, `1024` ulimit, empty experimental and additional CLI option lists
  - Service actions: `start`, `enable`
  - Validation status: The custom resource is present in the execution tree. Its property values, provider behavior, package preparation, account names, and generated service configuration require dependency/provider verification.

- **6379**: Redis server
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: Password `redis_secure_password_123` is assigned in the Chef recipe; five replication-related directive patterns are removed from the configuration when the file exists
  - Log directory: Owner `redis`, group `redis`, mode `0755`, recursive creation enabled
  - Service actions: Intended to be enabled through `redisio::enable`
  - Validation status: Redis assignments and cleanup patterns are based on source inspection. The `redisio` and `redisio::enable` recipes are missing from the supplied execution tree, so the Redis package and exact service unit are unverified.

## File Structure

```text
cookbooks/cache/recipes/default.rb

migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/
├── attributes/
│   └── default.rb
└── recipes/
    ├── default.rb
    └── _package.rb

migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/
└── recipes/
    ├── disabled.rb
    ├── enforcing.rb
    └── permissive.rb
```

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
```

**Providers:**
```text
```

No provider file path is available for `memcached_instance[memcached]`.

**Templates:**
```text
```

No templates are referenced.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No `cookbook_file` or `remote_file` deployment is shown.

The SELinux recipes are present in the supplied directory listing but are not included in the execution tree and are excluded from the executed migration scope.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency through `include_recipe 'memcached'`.
   - Assigns Redis server settings in source code: port `6379`, password `redis_secure_password_123`, and PID directory `/run/redis`.
   - Defines one Redis server entry, port `6379`, based on source inspection.
   - Includes the Redis dependency through `include_recipe 'redisio'`.
   - The `redisio` recipe is missing from the supplied execution tree; Redis package installation, templates, service naming, and provider behavior are unverified.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation enabled, based on source inspection.
   - Executes `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Includes `redisio::enable`.
   - The `redisio::enable` recipe is missing from the supplied execution tree. The Ansible role must discover the actual Redis unit before enabling and starting it.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates the custom resource `memcached_instance[memcached]`.
   - Source inspection associates the resource with:
     - Memory: `64`
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - Threads: `node['memcached']['threads']`
     - Ulimit: `1024`
     - Empty experimental options
     - Empty additional CLI options
     - `service_user` account
     - Actions `start` and `enable`
   - These properties and lifecycle effects require confirmation from the unavailable custom resource provider.
   - The migration must not invent a provider path or assume provider behavior that is not confirmed.

3. **Memcached package preparation recipe** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - This recipe is present in the directory listing but is not shown as executed by the supplied execution tree.
   - Source inspection indicates package `memcached`, a service group and locked system user, `/var/log/memcached`, and `/var/run/memcached`.
   - The package version is sourced from `node['memcached']['version']`, whose source-level default is `nil`.
   - The service account is configured with system-account properties, `/nonexistent` home, `Memcached` comment, and `/bin/false` shell.
   - These operations are unverified as executed and must be confirmed against dependency analysis before being treated as migration requirements.
   - The `node['memcached']['threads']` value is referenced by the recipe but is not confirmed by the supplied structured analysis. The migration must make an explicit value decision.

4. **SELinux recipes**:
   - `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb`
   - `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb`
   - `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb`
   - These recipes are not included in the execution tree and are not migrated as executed components of `cache`.

## Dependencies

**External cookbook dependencies**:

- `memcached`
- `redisio`

Exact dependency versions and metadata declarations are unavailable.

**System package dependencies**:

- `memcached` (source-level package reference)
- Redis package: not identified; determine it from the target platform and the missing `redisio` dependency

**Service dependencies**:

- Memcached service lifecycle is intended to be managed by `memcached_instance[memcached]`; exact unit and provider behavior require verification.
- Redis is intended to be enabled by `redisio::enable`; exact unit name and package implementation require verification.

## Credentials

**Detection Summary**: 1 credential detected by source inspection in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`; migrated variable such as `redis_password`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the Chef recipe
- **Value currently present**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis server on port `6379`
- **Migration handling**:
  - Store the migrated value in Ansible Vault.
  - Do not commit the plaintext password to role defaults, task files, templates, or unencrypted variables.
  - Use `no_log: true` for tasks that may expose the password.
  - Apply restrictive permissions to any rendered Redis configuration containing the password.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, database connection strings, or additional hardcoded tokens were identified by source inspection.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `6379`
- Redis Unix socket: none specified
- Redis bind address: not specified

**Templates rendered**:

- None identified; render count: `0`

**Configuration transformations**:

- Apply Redis cleanup to `/etc/redis/6379.conf` only when the file exists.
- Confirm the following directives are absent after migration:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- Notify Redis only when the configuration changes.

## Pre-flight checks

```bash
# Confirm required commands and discover service units
command -v systemctl
command -v ss
command -v nc
systemctl list-unit-files | grep -E '^(memcached|redis)'

# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'
ss -tlnp | grep ':11211'
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
systemctl cat memcached
systemctl show memcached --property=User,ExecStart,LimitNOFILE
test -d /var/log/memcached && stat -c '%A %U:%G %n' /var/log/memcached
test -d /var/run/memcached && stat -c '%A %U:%G %n' /var/run/memcached

# Verify Memcached UDP endpoint with a Memcached-aware diagnostic client
# Confirm UDP port 11211 is bound when UDP support is required.

# Redis instance: port 6379
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
ss -tlnp | grep ':6379'

# Substitute the discovered Redis unit name for <redis-unit>
systemctl status <redis-unit>
systemctl is-enabled <redis-unit>
systemctl is-active <redis-unit>
ps aux | grep '[r]edis-server'
journalctl -u <redis-unit> --since "-10 minutes" --no-pager

# Verify Redis authentication without exposing the password in shell history.
# Supply the vaulted password through a protected credential mechanism.
redis-cli -p 6379 -a '<password-from-Ansible-Vault>' PING

# Redis directories
test -d /var/log/redis && stat -c '%A %U:%G %n' /var/log/redis
test -d /run/redis && stat -c '%A %U:%G %n' /run/redis
```

Expected results:

- The `memcached` instance is active and enabled.
- Memcached listens on TCP port `11211` and, where required, UDP port `11211`.
- Memcached uses the validated service account and configured resource values.
- Redis listens on TCP port `6379`.
- Redis authentication returns `PONG`.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- The five specified Redis directive patterns are absent from `/etc/redis/6379.conf`.
- The Redis password is not exposed in normal command output or logs.

The migration must also create a non-empty `ansible/Makefile` with a default `all` target that invokes `ansible-playbook`. This requirement must be preserved in both `INPUT-AGENTS.md` and `EXPORT-AGENTS.md`.