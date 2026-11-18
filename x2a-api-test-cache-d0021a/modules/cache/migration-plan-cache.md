---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook directly executes one Memcached custom resource named `memcached` and directly creates a Redis log directory and configuration-cleanup block. Memcached is intended to listen on TCP and UDP port `11211` at `0.0.0.0`, with the analyzed configuration values listed below, although the supplied validation data does not include the contents of the attributes file that defines those defaults. The cookbook also contains source-level Redis inputs for one intended instance on port `6379`, including a hardcoded authentication password, `/run/redis` as the PID directory, and cleanup of selected directives from `/etc/redis/6379.conf`; however, both `redisio` and `redisio::enable` are missing from the execution tree. Redis package, service, configuration, and enablement behavior must therefore be verified before migration. The Memcached package and account resources are present in an analyzed `_package.rb` file but are not confirmed reachable from the supplied execution flow.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Confirmed custom-resource instance; package and account setup is observed only in an analyzed dependency file whose reachability is unconfirmed.
  - Package: `memcached`
  - Package version: `node['memcached']['version']`; the default value is not verifiable from the supplied validation data.
  - Location/Path: Log directory `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: Memory `64` MB, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental and extra CLI option lists
  - Threads: `node['memcached']['threads']`; no supplied default was validated
  - Service account: `service_user`, intended as a locked system user with shell `/bin/false`
  - Service group: `service_group`, intended as a system group
  - Actions: Start and enable

- **redis-6379**: Intended Redis configuration target; not confirmed as an executed or deployed service because the required `redisio` recipes are missing.
  - Package: Not identified; confirm the target operating system and Redis implementation
  - Location/Path: Intended PID directory `/run/redis`; intended log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`
  - Key Config: Authentication password is assigned in source as `redis_secure_password_123`; intended configuration path `/etc/redis/6379.conf`
  - Log directory ownership: `redis:redis`
  - Log directory mode: `0755`
  - Configuration directives to remove:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`
  - Service action: Intended to be enabled through `redisio::enable`; actual service name is unknown

## File Structure

**MANDATORY: Preserve this section from the original plan.**

### Recipes

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
```

The following files are present in the directory listing but are not reachable from the supplied `cache` execution flow and are not migration inputs:

```text
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

### Providers

```text
```

No provider file path was supplied. The provider implementation for `memcached_instance[memcached]` is unavailable.

### Templates

```text
```

No rendered templates were identified.

### Attributes

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

The supplied validation data does not include the contents of this file. Memcached defaults such as `64`, `1024`, `1m`, and `1024` must be verified against the source file before being treated as confirmed defaults.

### Files

```text
```

No `cookbook_file`, `remote_file`, or deployed static file was identified.

### Data Bags

No data bag is referenced by the reachable `cache` execution flow. The repository-level `nginx_secrets/site` data bag is unrelated and must not be migrated.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` dependency recipe.
   - Assigns one source-level Redis server configuration for port `6379`.
   - Assigns `/run/redis` as the Redis base PID directory.
   - Attempts to include the missing `redisio` recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block[fix_redis_config]`, which conditionally edits `/etc/redis/6379.conf`.
   - Attempts to include the missing `redisio::enable` recipe.
   - The Redis port, password, PID path, configuration path, directory settings, and directive-removal patterns are source-level observations requiring verification because the Redis dependency implementation is unavailable.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates the custom resource `memcached_instance[memcached]`.
   - Passes memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, and service actions `start` and `enable`, subject to verification of the analyzed attribute file.
   - Passes service user `service_user`, empty experimental options, empty extra CLI options, and the unresolved `node['memcached']['threads']` value.
   - The custom-resource provider is not present in the supplied provider tree.

3. **`memcached::_package`** (`migration-dependencies/cookbooks/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - This file is analyzed but is not confirmed reachable from the supplied `memcached::default` execution flow.
   - If the custom-resource provider or another reachable recipe invokes it, it installs package `memcached` without an explicit version unless one is supplied.
   - If invoked, it creates system group `service_group`, creates and locks system user `service_user`, creates `/var/log/memcached` with mode `0755`, and creates `/var/run/memcached` with mode `0755`.
   - These package, account, and directory resources must not be counted as executed behavior until reachability is confirmed.

4. **`redisio`** (missing dependency recipe):
   - The expected recipe file was not found.
   - No Redis package, service, configuration template, or service name can be confirmed from the supplied execution tree.

5. **`redisio::enable`** (missing dependency recipe):
   - The expected recipe file was not found.
   - The intended behavior is Redis service enablement, but the platform-specific service name must be identified during migration.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- `memcached`
- Redis package: not identified because the reachable `redisio` implementation is missing

**Service dependencies**:
- Memcached: intended to start and enable
- Redis instance `redis-6379`: intended to start and enable, but not confirmed because `redisio` and `redisio::enable` are missing

**Supported platforms**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: None. No data bag, Chef Vault, environment-variable, or external secret provider is used. The literal is assigned directly in `cookbooks/cache/recipes/default.rb`.
  - **URL**: None
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for intended instance `redis-6379` on port `6379`
- **Migration storage**: Ansible Vault or an approved external secret-management provider
- **Required handling**: Do not retain the literal password in a production playbook, shell history, or migration documentation

No TLS certificate, private key, embedded database connection string, encrypted data bag, or additional secret was detected in the reachable cache execution flow.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/var/log/memcached`
- `/var/run/memcached`
- `/var/log/redis`
- `/etc/redis/6379.conf`, if the Redis implementation creates it
- `/run/redis`, if the Redis implementation creates it

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Intended Redis TCP: port `6379`

**Templates rendered**:
- None identified
- Render count: `0`

**Memcached values to verify**:
- Listen address `0.0.0.0`
- TCP port `11211`
- UDP port `11211`
- Memory `64` MB, subject to attribute-file verification
- Maximum connections `1024`, subject to attribute-file verification
- Maximum object size `1m`, subject to attribute-file verification
- Ulimit `1024`, subject to attribute-file verification

**Redis values to verify**:
- Port `6379`
- Authentication enabled
- PID directory `/run/redis`
- Log directory `/var/log/redis`
- Log directory ownership `redis:redis`
- Log directory mode `0755`
- Absence of the five selected directive families from `/etc/redis/6379.conf`

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'
```

Expected result: the Memcached service is active and enabled.

```bash
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211
printf "stats\r\nquit\r\n" | nc -w 2 127.0.0.1 11211
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
```

Expected result: Memcached responds, exposes TCP port `11211`, and exposes UDP port `11211`.

```bash
stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached
systemctl show memcached | grep -E 'LimitNOFILE|TasksMax'
cat /proc/$(pgrep -xo memcached)/limits
```

Verify the directories exist with mode `0755`, expected service ownership, and effective limits compatible with ulimit `1024`.

### Redis intended instance `redis-6379`

First identify the platform-specific service name because the `redisio` implementation is missing:

```bash
systemctl list-unit-files | grep -i redis
systemctl status redis
systemctl status redis-server
```

After the Redis package and service have been explicitly identified and migrated:

```bash
ss -tlnp | grep ':6379'
redis-cli -p 6379 -a '<retrieve-from-Ansible-Vault>' PING
```

Expected result: the Redis service is active and `redis-cli` returns:

```text
PONG
```

Do not place the literal Chef password in the command line or shell history.

```bash
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|dir|pidfile)' /etc/redis/6379.conf
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

The configuration should show the intended Redis settings. The final command should return no matching directive lines if the source-level cleanup behavior has been reproduced.

```bash
stat -c '%A %U:%G %n' /var/log/redis
test -d /run/redis
ls -ld /run/redis
```

Verify `/var/log/redis` has mode `0755` and ownership `redis:redis`, and verify `/run/redis` exists if retained as the target PID directory.

Use the actual discovered service name:

```bash
journalctl -u redis --no-pager -n 50
journalctl -u redis-server --no-pager -n 50
```

Check that the selected Redis service starts without configuration or authentication errors.