---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache services: a Memcached instance named `memcached` and a Redis server configured on port `6379`. Memcached is configured for 64 MB of memory, TCP and UDP port `11211`, `0.0.0.0` binding, 1,024 maximum connections, 1 MB maximum objects, and start/enable actions. Redis uses `/run/redis` as its base PID directory, creates `/var/log/redis`, enables password authentication, and removes five replication-related directives from `/etc/redis/6379.conf`. Redis installation and enablement recipes, and the Memcached custom-resource provider, are not present in the supplied execution tree; their package, service, generated configuration, and provider behavior must therefore be verified during implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: In-memory key/value cache
  - Package: `memcached`
  - Version: No explicit version pin (`nil`)
  - Memory: `64` MB
  - Location/Path: `/var/log/memcached`, `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: Maximum connections `1024`; maximum object size `1m`; ulimit `1024`; actions are start and enable
  - Account: `service_user:service_group`
  - Threads: `node['memcached']['threads']`; no default is defined in the supplied attributes file
  - Experimental options: `[]`
  - Additional CLI options: `[]`
  - Configuration and service-unit paths: Not confirmed because the `memcached_instance` provider is not supplied

- **redis**: Redis in-memory data store/cache
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket identified
  - Key Config: Password authentication enabled; password source value is `redis_secure_password_123`; log directory owner/group `redis:redis`; log directory mode `0755`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Service state: Redis enablement is requested through `redisio::enable`, but that recipe is not present in the supplied execution tree
  - Bind address: Not specified in the supplied recipe
  - Package name and exact service name: Not confirmed because the `redisio` recipes are missing

## File Structure

The supplied analysis accounts for seven inventory files: three analyzed source files and four additional files present in the directory listing but not shown as executed.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider file path was supplied in the execution tree. The `memcached_instance[memcached]` resource is a custom resource, but its provider implementation is not listed among the files available for this migration analysis.

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

No static files are deployed by `cookbook_file` or `remote_file` resources.

The following files appear in the directory listing but are not shown as executed in the supplied execution tree:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

The supplied execution tree does not include the `redisio` recipe files or the Memcached custom-resource provider implementation.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached recipe.
   - Sets the Redis server collection to one server entry on port `6379`.
   - Sets `redisio.base_piddir` to `/run/redis`.
   - Includes the Redis installation/configuration recipe.
   - Creates `/var/log/redis`.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes the Redis enablement recipe.
   - The analyzed resources directly declared by this recipe are:
     - `directory[/var/log/redis]`
     - `ruby_block[fix_redis_config]`
   - No `group[redis]` resource is identified in the supplied execution tree. A `redis` group is an inferred prerequisite for the declared directory ownership, not a confirmed Chef resource.

   Redis values assigned by this recipe are:
   - Port: `6379`
   - Password: `redis_secure_password_123`
   - `replicaservestaledata`: `nil`
   - Base PID directory: `/run/redis`

   The Redis directory is configured with:
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled

   `ruby_block[fix_redis_config]` is confirmed as an analyzed resource. The supplied validation information describes its intended source-derived behavior as:
   - Target file: `/etc/redis/6379.conf`
   - No modification when the file does not exist
   - Removal of complete lines matching:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - In-place rewrite of the file when it exists

   The exact target-file and directive behavior should be verified against the Ruby block source before implementation because the execution summary itself confirms only the existence of the Ruby block.

   The recipe references the following unavailable recipes:
   - `redisio`: installation and configuration; recipe file not found
   - `redisio::enable`: service enablement; recipe file not found

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes one custom resource: `memcached_instance[memcached]`
   - The confirmed resource count is one `memcached_instance` resource.
   - Source-derived settings associated with the custom resource are:
     - Memory: `64`
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - User: `service_user`
     - Maximum object size: `1m`
     - Threads: `node['memcached']['threads']`, with no supplied default
     - Experimental options: `[]`
     - Additional CLI options: `[]`
     - Ulimit: `1024`
     - Actions: start and enable
   - These individual values are source-derived but cannot be fully verified from the supplied structured execution summary because the custom-resource provider is unavailable.
   - The Ansible migration should implement the custom resource as explicit package, account, directory, configuration, and service tasks only after provider behavior is verified.

3. **Memcached package and account setup** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - This file appears in the directory listing but is not shown as executed in the supplied execution tree.
   - Source-derived operations requiring provider or source verification are:
     - Install package `memcached` with no explicit version pin.
     - Create system group `service_group` unless the `service_user` account already exists.
     - Create locked system user `service_user`.
     - Set the user home to `/nonexistent`.
     - Set the user shell to `/bin/false`.
     - Set the user comment to `Memcached`.
     - Disable home-directory management.
     - Create `/var/log/memcached` with owner `service_user:service_group` and mode `0755`.
     - Create `/var/run/memcached` with owner `service_user:service_group` and mode `0755`.
   - These operations must not be treated as confirmed execution-tree resources until the custom-resource provider and package recipe are inspected.

4. **Redis installation/configuration dependency** (`redisio`, recipe unavailable):
   - The cookbook expects Redis installation and configuration to occur before Redis log-directory creation and service enablement.
   - The package name, configuration-generation behavior, service name, and provider resources cannot be determined from the supplied files.

5. **Redis enablement dependency** (`redisio::enable`, recipe unavailable):
   - The cookbook expects Redis to be enabled after configuration and cleanup.
   - The exact service name cannot be determined from the supplied files.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- `memcached`
- Redis package name not confirmed because the `redisio` recipe is unavailable

**Service dependencies**:
- Memcached service is started and enabled by `memcached_instance[memcached]`.
- Redis is intended to be enabled by `redisio::enable`.
- Redis service name is not confirmed.
- The inferred `redis` system account/group must exist before `/var/log/redis` can be owned by `redis:redis`.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Not applicable; hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext recipe value
- **Usage context**: Redis password authentication for the Redis instance listening on port `6379`

The Ansible migration must store this secret in Ansible Vault or an approved AAP credential/secret mechanism rather than a normal variables file. The Redis configuration should reference the vaulted variable.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificates, private keys, API keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb`
- `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- The Memcached custom-resource provider implementation, if available
- The `redisio` installation/configuration and enablement recipes, if available

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Redis Unix socket: none identified
- Redis bind address: not specified

**Templates rendered**:
- None; zero Chef templates are shown as rendered

## Pre-flight checks

### Memcached instance: `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
```

Expected result: the Memcached service is active and enabled, and the process runs with the configured Memcached account.

```bash
printf "version\r\n" | nc -w 2 127.0.0.1 11211
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
```

Expected result:
- TCP port `11211` is listening.
- UDP port `11211` is bound.
- The Memcached command returns `VERSION ...`.

```bash
ps -ef | grep '[m]emcached'
```

Verify:
- Memory: `64` MB
- TCP port: `11211`
- UDP port: `11211`
- Listen address: `0.0.0.0`
- Maximum connections: `1024`
- Maximum object size: `1m`
- Ulimit: `1024`

```bash
stat -c '%A %U:%G %n' /var/log/memcached
stat -c '%A %U:%G %n' /var/run/memcached
```

Expected result:
- Both directories exist.
- Both directories have mode `0755`.
- Both directories are owned by `service_user:service_group`.

### Redis instance: `redis`

Use the service name provided by the target Redis package. If the service is named `redis`, run:

```bash
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
```

Expected result: the Redis service is active and enabled.

```bash
ss -ltnp | grep ':6379'
```

Expected result: a Redis process is listening on TCP port `6379`.

Test authenticated access without placing the password directly in shell history:

```bash
read -s REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD
```

Expected result:

```text
PONG
```

Verify that unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result:

```text
NOAUTH Authentication required.
```

Validate the Redis configuration:

```bash
grep -E '^(port|requirepass|dir|pidfile|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Verify:
- Port is `6379`.
- Password authentication is configured through the vaulted Ansible secret.
- The following directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

Check Redis directories:

```bash
stat -c '%A %U:%G %n' /var/log/redis
stat -c '%A %U:%G %n' /run/redis
```

Expected result:
- `/var/log/redis` exists with mode `0755`.
- `/var/log/redis` is owned by `redis:redis`.
- `/run/redis` exists and is used as the Redis PID directory.

Check Redis logs using the confirmed target service name:

```bash
journalctl -u redis --lines 50 --no-pager
```

If the target configuration writes to a file, verify the exact configured log path. The supplied cookbook does not identify a Redis log filename.

### Migration idempotence

Run the Ansible playbook twice and verify that:

- `/var/log/redis` is unchanged on the second run.
- `/etc/redis/6379.conf` is not repeatedly modified.
- Redis is not unnecessarily restarted.
- Memcached is not unnecessarily restarted.
- The Redis password remains sourced from Ansible Vault or an approved secret mechanism.
