---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache instances: `memcached` and `redis`. The entry recipe executes Memcached first, then attempts Redis installation and enablement through unavailable `redisio` recipes. Memcached is intended to listen on TCP and UDP port `11211`; Redis is intended to listen on port `6379` with authentication, `/run/redis` as its PID directory, `/var/log/redis` as its log directory, and post-configuration cleanup of five Redis directives. Redis package and service names must be discovered from the target platform because the supplied `redisio` implementation is unavailable.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Platform-specific Memcached configuration path; the supplied execution tree does not identify the configuration file
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: Package `memcached`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; ulimit `1024`; listen address `0.0.0.0`; log directory `/var/log/memcached`; runtime directory `/var/run/memcached`; service started and enabled
  - Additional Config: `experimental_options` and `extra_cli_options` are empty; the `threads` value is attribute-driven and must be verified because it is not confirmed by the supplied validation summary
  - Account: `service_user` and `service_group` values supplied by the Memcached custom resource; exact names must be verified from the provider or dependency source

- **redis**: Redis cache service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`; no Unix socket identified
  - Key Config: Authentication enabled through `requirepass`; intended PID directory `/run/redis`; log directory `/var/log/redis`
  - Log Directory: `/var/log/redis`, owner `redis`, group `redis`, mode `0755`
  - Password: The source recipe assigns `redis_secure_password_123`; replace it with an Ansible Vault value or AAP credential
  - Configuration Cleanup: Remove `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Implementation Status: Redis package name, service unit name, provider behavior, and configuration template are unavailable in the supplied execution tree and must be verified before migration

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only files identified by the supplied execution tree and directory listing are included. The SELinux recipes and Memcached `_package.rb` are not part of the execution tree and are not executed by this module.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider path was supplied for `memcached_instance`. The Ansible migration must reproduce the observed custom-resource behavior without assuming an unavailable Chef provider file.

**Templates:**
```text
```

No templates are rendered by the recipes in the supplied execution tree.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The structured analysis reports seven analyzed files, but only the three paths above are identified in the supplied directory listing. The remaining four files are not enumerated and must be identified before migration completeness can be confirmed.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`, causing Memcached configuration to execute first.
   - Defines one Redis server configuration for port `6379`.
   - Assigns the Redis password through `node.default['redisio']['servers'][0]['requirepass']`; the literal source value is `redis_secure_password_123` and must not be migrated as plaintext.
   - Sets `redisio.base_piddir` to `/run/redis`.
   - Attempts to include `redisio`; the recipe is unavailable in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`. These ownership and mode details are documented by the source plan but depend on the unavailable Redis implementation and must be verified.
   - Runs `ruby_block[fix_redis_config]` after Redis configuration:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Removes complete lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
     - Writes the modified content back to `/etc/redis/6379.conf`.
   - Attempts to include `redisio::enable`; this recipe is unavailable in the supplied execution tree.
   - The supplied validation does not confirm a `group[redis]` resource. Do not create or document it as an observed Chef resource without additional source evidence.
   - The Redis package and service unit must be discovered from the target platform or restored `redisio` dependency source.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Applies the reported Memcached settings:
     - Memory: `64` MB
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - Ulimit: `1024`
     - Experimental options: empty
     - Additional CLI options: empty
   - Uses the reported log directory `/var/log/memcached` and runtime directory `/var/run/memcached`.
   - Requests actions `start` and `enable`.
   - The supplied execution tree confirms the custom resource but does not enumerate its underlying package, user, group, and directory resources. Those implementation details are inferred from the dependency recipe summary and require verification.
   - The reported dependency behavior includes:
     - Installing package `memcached`, with version from `node['memcached']['version']`; the version is `nil`, meaning the platform package-manager default.
     - Creating a system group represented by `service_group`.
     - Creating a locked system user represented by `service_user`, with home `/nonexistent`, shell `/bin/false`, comment `Memcached`, no managed home, and primary group `service_group`.
     - Creating `/var/log/memcached` and `/var/run/memcached`.
   - The Ansible implementation should explicitly install `memcached`, create the verified service group and locked service user, create both directories with mode `0755`, deploy the platform-appropriate service configuration, and start and enable the Memcached service.
   - Configure the verified equivalent of `-m 64`, `-p 11211`, `-U 11211`, `-l 0.0.0.0`, `-c 1024`, `-I 1m`, `-u`, and the ulimit setting. Add `-t` only after verifying the source `threads` value.

3. **`redisio`** (unavailable recipe; intended execution position after Memcached):
   - Intended to install and configure the Redis instance on port `6379`.
   - Intended to use `/run/redis` as the base PID directory.
   - Exact package, service, provider, and template behavior cannot be derived from the supplied execution tree.

4. **`redisio::enable`** (unavailable recipe; intended final execution position):
   - Intended to enable and possibly start Redis at boot.
   - The exact service resource and service unit name must be discovered on the target platform.
   - Do not assume `redis-server` unless that unit is verified.

## Dependencies

**External cookbook dependencies**: `memcached`; `redisio`  
`redisio` and `redisio::enable` are unavailable in the supplied execution tree.

**System package dependencies**: `memcached`  
No Redis package name is confirmed by the supplied source.

**Service dependencies**:
- `memcached`: intended to be started and enabled by `memcached_instance[memcached]`
- `redis`: intended to be enabled by `redisio::enable`; exact service unit name is unavailable

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Literal value in source**: `redis_secure_password_123`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Usage context**: Redis authentication through the `requirepass` setting for the Redis instance on port `6379`
- **Migration requirement**: Store the password in Ansible Vault or an AAP credential. Do not commit the literal value to role defaults, variables, templates, or task files.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, or database connection strings were detected in the supplied files.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/var/log/memcached`
- `/var/run/memcached`
- `/var/log/redis`
- `/run/redis`
- `/etc/redis/6379.conf`
- The platform-specific Memcached service configuration file
- The platform-specific Redis service configuration file

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the verified configured listen address
- Redis Unix socket: none configured or identified

**Templates rendered**:
- None; render count `0`

**Configuration transformations**:
- `ruby_block[fix_redis_config]` modifies `/etc/redis/6379.conf` once when the file exists.
- The transformation removes five Redis directives rather than rendering a template.
- No Memcached template is present in the supplied execution tree.

## Pre-flight checks

### Memcached instance: `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'
```

```bash
grep -R -E '11211|0\.0\.0\.0|1024|64|1m' \
  /etc/memcached.conf /etc/sysconfig/memcached /etc/default/memcached 2>/dev/null

ls -ld /var/log/memcached
ls -ld /var/run/memcached
```

Verify the following individually:

- Package `memcached` is installed.
- The service is enabled and active.
- Memory is `64` MB.
- TCP port is `11211`.
- UDP port is `11211`.
- Listen address is `0.0.0.0`.
- Maximum connections are `1024`.
- Maximum object size is `1m`.
- The verified service user and group are configured.
- `/var/log/memcached` and `/var/run/memcached` exist with mode `0755`.

```bash
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211
printf "stats\r\nquit\r\n" | nc -w 2 127.0.0.1 11211 | \
  grep -E 'STAT version|STAT limit_maxbytes|STAT curr_connections'

ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
nc -zv 127.0.0.1 11211
```

Expected results:

- The protocol check returns a `VERSION` response.
- `limit_maxbytes` corresponds to approximately `64 MB`.
- TCP port `11211` is listening and accepts connections.
- UDP port `11211` is listening if supported by the target platform.

### Redis instance: `redis`

First identify the Redis service unit because `redisio::enable` is unavailable:

```bash
systemctl list-unit-files | grep -E 'redis|redis-server'
systemctl list-units --type=service | grep -E 'redis|redis-server'
```

After identifying the actual unit, substitute it for `<redis-service>`:

```bash
systemctl status <redis-service>
systemctl is-enabled <redis-service>
systemctl is-active <redis-service>
ps aux | grep '[r]edis-server'
```

Verify Redis configuration:

```bash
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|dir|pidfile|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

ls -ld /run/redis
ls -ld /var/log/redis
```

Verify the following individually:

- Redis listens on port `6379`.
- `requirepass` is present and supplied through Ansible Vault or an AAP credential.
- `/run/redis` is used for the PID path where applicable.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755` if those values are confirmed for the target Redis implementation.
- The following directives are absent after cleanup:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

Test Redis authentication without placing the password in shell history:

```bash
read -rs REDIS_PASSWORD
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 PING
unset REDIS_PASSWORD
```

Expected result:

```text
PONG
```

Verify unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication-required error when `requirepass` is active.

Check the Redis endpoint and logs:

```bash
ss -ltnp | grep ':6379'
nc -zv 127.0.0.1 6379
journalctl -u <redis-service> --no-pager -n 100
```

If Redis logs to a file instead of journald, identify the configured log path from `/etc/redis/6379.conf` before reading it.

### Runtime directories and ownership

```bash
stat -c '%A %U %G %n' /var/log/memcached
stat -c '%A %U %G %n' /var/run/memcached
stat -c '%A %U %G %n' /var/log/redis
stat -c '%A %U %G %n' /run/redis
```

Expected results:

- `/var/log/memcached` exists with mode `0755`.
- `/var/run/memcached` exists with mode `0755`.
- `/var/log/redis` has owner `redis`, group `redis`, and mode `0755` if confirmed by the target Redis implementation.
- `/run/redis` exists and is usable by the Redis service account.

### Migration-specific idempotence checks

Run the Ansible role twice and verify:

```bash
systemctl is-active memcached
ss -ltnp | grep ':11211'
ss -ltnp | grep ':6379'

grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

The second run should produce no configuration changes when:

- Memcached is installed, started, and enabled.
- Redis is installed, started, and enabled using the verified service unit.
- Required directories have the correct ownership and modes.
- The five Redis directives have already been removed.
- The Redis password matches the vaulted or AAP-managed value.
