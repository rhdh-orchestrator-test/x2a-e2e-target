---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: Memcached and Redis. Memcached is managed through the `memcached_instance[memcached]` custom resource and is configured for TCP and UDP port `11211`. Redis is intended as one instance on port `6379`, with authentication, PID directory `/run/redis`, log directory `/var/log/redis`, and removal of selected replication-related directives from `/etc/redis/6379.conf`. The supplied execution tree does not contain the `redisio` or `redisio::enable` recipes, nor the Memcached custom-resource provider, so the Ansible migration must confirm the target package and service implementations before deployment.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Package: `memcached`
  - Package version: `node['memcached']['version']`; default reported as `nil`, so Chef does not specify a concrete version
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config:
    - Memory: `64` MB
    - Maximum connections: `1024`
    - Maximum object size: `1m`
    - Threads: `node['memcached']['threads']`; referenced but no default is supplied in the provided attributes file
    - File descriptor limit: `1024`
    - Service user/group: `service_user` / `service_group`
    - Experimental options: none
    - Additional CLI options: none
    - Actions: start and enable
    - Reported filesystem setup: `/var/log/memcached` and `/var/run/memcached` owned by `service_user:service_group`, mode `0755`
    - The exact custom-resource provider implementation is not present and must be confirmed before assuming additional behavior

- **6379**: Redis cache service
  - Package: Not determinable from the supplied execution tree; the `redisio` recipe is missing
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; bind address is not determinable from the supplied `redisio` implementation
  - Key Config:
    - Authentication enabled
    - Password is hardcoded in the Chef recipe as `redis_secure_password_123`; migrate it to Ansible Vault or another approved secret store
    - Log directory owner/group: `redis:redis`
    - Log directory mode: `0755`
    - Remove lines matching:
      - `^replica-serve-stale-data.*$`
      - `^replica-read-only.*$`
      - `^repl-ping-replica-period.*$`
      - `^client-output-buffer-limit.*$`
      - `^replica-priority.*$`
    - Redis installation/configuration is requested through `redisio`
    - Redis enablement is requested through `redisio::enable`
    - Both Redis recipes are absent from the supplied execution tree

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

The execution tree identifies `memcached_instance[memcached]` as a custom resource, but no provider file is included in the supplied execution tree. Do not invent a provider path.

**Templates:**
```text
```

No templates are rendered by the analyzed recipes.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The following files appear in the directory listing but are not in the execution tree and are not part of the active migration flow:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

The SELinux recipes must not be migrated unless another execution path explicitly includes them.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` recipe.
   - Sets `node['redisio']['servers']` to one Redis item:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the `redisio` recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Executes `ruby_block[fix_redis_config]` to edit `/etc/redis/6379.conf` when the file exists.
   - Includes `redisio::enable`.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares `memcached_instance[memcached]`.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, file descriptor limit `1024`, empty experimental options, and empty additional CLI options.
   - References `node['memcached']['threads']`, whose default is not supplied in the provided attributes file.
   - Requests actions `start` and `enable`.
   - The custom-resource provider is not present in the supplied execution tree.
   - The reported dependency setup installs package `memcached`, creates or uses `service_user` and `service_group`, and manages `/var/log/memcached` and `/var/run/memcached`; these details require confirmation against the unavailable provider/package implementation.

3. **`redisio`** (requested by `cookbooks/cache/recipes/default.rb`; implementation missing):
   - Intended to install and configure the Redis instance named `6379`.
   - Intended to configure password authentication and PID base directory `/run/redis`.
   - The Redis package, provider, exact service resource, bind configuration, and service unit name cannot be derived from the supplied execution tree.
   - The Ansible migration must select and document a supported Redis implementation for the target operating system.

4. **Redis log directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Sets owner `redis`, group `redis`, mode `0755`, with recursive directory creation.

5. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Removes complete lines matching `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Does not show a service restart or reload notification.
   - The Ansible implementation should use idempotent `ansible.builtin.replace` tasks or a controlled template and must not add replacement values unless separately defined.

6. **`enable`** (`redisio::enable`, requested by `cookbooks/cache/recipes/default.rb`; implementation missing):
   - Intended to enable Redis at boot.
   - The exact Redis service unit name must be confirmed on the target platform before enabling it.

There are no collection iterations or `.each` loops in the supplied execution tree. The Redis configuration contains exactly one item, `6379`.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- `memcached`
- Redis package: not determinable because the `redisio` recipe is missing

**Service dependencies**:
- Memcached is intended to be started and enabled by `memcached_instance[memcached]`.
- Redis is intended to be configured by `redisio` and enabled by `redisio::enable`, but both recipe implementations are unavailable.
- The exact Redis service unit name must be confirmed on the target platform.

## Credentials

**Detection Summary**: 1 credential detected in 1 file. The supplied validation summary does not independently expose the credential-detection result, so this count should be confirmed during source review.

**Source**:
- **Provider**: Hardcoded
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in a Chef recipe
- **Usage context**: Redis authentication for instance `6379`
- **Migration handling**: Store in Ansible Vault or another approved secret store. Do not place the literal value in `defaults/main.yml`, plaintext variables, or a configuration file committed to source control.

No data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur calls, environment-variable secrets, TLS certificate references, or database connection strings were reported.

## Checks for the Migration

**Files to verify**:
- `/var/log/memcached`
- `/var/run/memcached`
- `/var/log/redis`
- `/etc/redis/6379.conf`
- `/run/redis`

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`; bind address depends on the selected Redis implementation
- Unix sockets: none specified

**Templates rendered**:
- None

**Configuration edits performed**:
- Edit `/etc/redis/6379.conf` in place when it exists.
- Confirm the following directive families are absent after migration:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

ss -tlnp | grep ':11211'
printf "version\r\n" | nc -w 2 127.0.0.1 11211

ss -ulnp | grep ':11211'

ls -ld /var/log/memcached /var/run/memcached
stat -c '%U:%G %a %n' /var/log/memcached /var/run/memcached
```

Verify:
- `memcached` is enabled and active.
- TCP port `11211` is listening.
- UDP port `11211` is listening if UDP support is enabled.
- Memory is `64` MB.
- Maximum connections are `1024`.
- Maximum object size is `1m`.
- Listen address is `0.0.0.0`.
- File descriptor limit is `1024`.
- The service account and directory ownership match the migrated configuration.

### Redis instance `6379`

First confirm the platform-specific Redis service unit because `redisio` and `redisio::enable` are missing. Then substitute that unit name in the following checks:

```bash
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

ss -tlnp | grep ':6379'
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
```

Expected result:

```text
PONG
```

Use an environment variable or protected shell mechanism for `REDIS_PASSWORD`; do not place the password directly in shell history.

Verify authentication is required:

```bash
redis-cli -p 6379 PING
```

The unauthenticated request should be rejected with an authentication error.

Validate the configuration and directories:

```bash
test -f /etc/redis/6379.conf
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

ls -ld /run/redis /var/log/redis
stat -c '%U:%G %a %n' /run/redis /var/log/redis
```

Expected result:
- `/etc/redis/6379.conf` exists.
- No prohibited directive lines are returned.
- `/run/redis` exists and is used as the PID directory.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.

Review logs using the confirmed service unit:

```bash
journalctl -u redis --no-pager -n 100
find /var/log/redis -maxdepth 1 -type f -ls
```

Replace `redis` with the exact target service unit if necessary.

### Combined network verification

```bash
ss -tlnp | grep -E ':(6379|11211)\b'
ss -ulnp | grep ':11211'
```

Expected result:
- Redis instance `6379` listens on TCP port `6379`.
- Memcached instance `memcached` listens on TCP port `11211`.
- Memcached listens on UDP port `11211` if UDP is enabled by the migrated configuration.