---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache services: Memcached and Redis. Memcached is created through the `memcached_instance[memcached]` custom resource and listens on TCP and UDP port `11211`, with 64 MB of memory, a maximum of 1,024 connections, and a 1 MB maximum object size. Redis is configured as one instance on port `6379`, using `/run/redis` for PID files, `/var/log/redis` for logs, and password authentication. The Redis installation and enablement recipes are unavailable in the supplied execution tree and must be implemented or supplied separately in Ansible.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache instance
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `11211`; UDP `11211`
  - Key Config: Binds to `0.0.0.0`; 64 MB memory; maximum 1,024 connections; maximum object size `1m`; service account resolved as `service_user`; startup state is started and enabled; ulimit `1024`; no experimental or additional CLI options; package version is not pinned

- **Redis instance on port 6379**: Redis cache instance configured through `redisio`
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Authentication enabled with a hardcoded password in the Chef source; `replicaservestaledata` is `nil`; installation and enablement recipes are unavailable in the supplied execution tree

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
```

The following recipes are referenced by the execution flow but were not found and cannot be listed as available implementation files:

- `redisio`
- `redisio::enable`

The SELinux recipes shown in the directory listing are not part of the supplied execution flow and are excluded from the migration file list.

**Providers:**
```text
```

No provider file was supplied in the execution tree. The `memcached_instance[memcached]` custom resource is used, but its provider implementation is not present in the listed files.

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

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached recipe.
   - Sets the Redis server collection to one item:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` installation and configuration recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive directory handling.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes the unavailable `redisio::enable` recipe.

   The Redis configuration cleanup block checks `/etc/redis/6379.conf`. When the file exists, it removes complete lines matching:
   - `replica-serve-stale-data`
   - `replica-read-only`
   - `repl-ping-replica-period`
   - `client-output-buffer-limit`
   - `replica-priority`

   The Ansible implementation should check for the file before editing it, remove the matching directives with `ansible.builtin.replace` or an equivalent complete configuration template, and notify or restart Redis only when the configuration changes. The Chef block itself does not declare an explicit service notification.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates the `memcached_instance[memcached]` custom resource.
   - Configures memory to `64`.
   - Configures TCP port `11211`.
   - Configures UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Uses `service_user` as the service user.
   - Sets maximum object size to `1m`.
   - Passes `node['memcached']['threads']`; no default value is defined in the supplied attribute file.
   - Passes empty `experimental_options`.
   - Passes empty `extra_cli_options`.
   - Sets ulimit to `1024`.
   - Requests actions `:start` and `:enable`.

   The custom resource provider is unavailable. The Ansible migration must reproduce its observable behavior rather than translate an unavailable provider directly.

3. **Memcached package resources** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - Installs package `memcached` without pinning a version.
   - Creates the system group `service_group` only when `service_user` is not already present.
   - Creates and locks the system user `service_user` with group `service_group`, home `/nonexistent`, comment `Memcached`, shell `/bin/false`, and disabled home management.
   - Creates `/var/log/memcached` with owner `service_user`, group `service_group`, and mode `0755`.
   - Creates `/var/run/memcached` with owner `service_user`, group `service_group`, and mode `0755`.

   The exact values of `service_user` and `service_group` are not defined in the supplied files. The Ansible implementation must obtain them from the Memcached role or dependency defaults.

4. **`redisio`** (referenced recipe; unavailable):
   - Installs and configures the Redis instance on port `6379`.
   - Uses password authentication.
   - Uses `/run/redis` as the PID directory.
   - Must create the Redis service account required by the `/var/log/redis` directory task.
   - The supplied files do not specify the Redis package name, repository, service unit name, or generated template paths.

5. **`redisio::enable`** (referenced recipe; unavailable):
   - Enables and starts the Redis instance on port `6379`.
   - The Ansible implementation must determine the actual systemd unit name from the selected Redis package or implementation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- `memcached`
- Redis package: not specified because the `redisio` recipe is unavailable

**Service dependencies**:

- Memcached must be installed, configured, enabled, and started.
- Redis must be installed, configured, enabled, and started after its configuration is complete.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected
  - **Source file**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Literal value**: `redis_secure_password_123`
- **Current storage**: Hardcoded Chef attribute assignment
- **Usage context**: Redis authentication for the instance listening on port `6379`
- **Migration handling**: Store the value in Ansible Vault, AAP credentials, or another approved secret-management system. Do not commit the literal password to defaults or ordinary variables files.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secrets, TLS certificates, private keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379`
- Redis Unix socket: none specified

**Templates rendered**:

- None

**Configuration edits performed**:

- `/etc/redis/6379.conf` is modified in place when it exists.
- The following directives must be absent as active configuration lines:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

```bash
# Memcached service status
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Verify the Memcached process
ps aux | grep '[m]emcached'

# Verify Memcached TCP port
ss -tlnp | grep ':11211'
lsof -iTCP:11211 -sTCP:LISTEN

# Verify Memcached UDP port
ss -ulnp | grep ':11211'

# Verify Memcached directories
ls -ld /var/log/memcached
ls -ld /var/run/memcached

# Verify the Memcached service account and ownership
getent passwd service_user
getent group service_group
stat -c '%U:%G %a %n' /var/log/memcached
stat -c '%U:%G %a %n' /var/run/memcached

# Verify the Redis service.
# Replace redis-service-name with the unit selected by the Ansible implementation.
systemctl status redis-service-name
systemctl is-enabled redis-service-name
systemctl is-active redis-service-name

# Verify the Redis process
ps aux | grep '[r]edis-server'

# Verify Redis TCP port
ss -tlnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Verify the Redis configuration
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify Redis PID and log directories
ls -ld /run/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /run/redis
stat -c '%U:%G %a %n' /var/log/redis

# Redis authentication and functional test.
# Retrieve the password from the approved secret store without exposing it.
export REDISCLI_AUTH='<retrieve-from-approved-secret-store>'

redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
redis-cli -p 6379 SET migration_check success
redis-cli -p 6379 GET migration_check
redis-cli -p 6379 DEL migration_check

unset REDISCLI_AUTH

# Verify logs
find /var/log/memcached -maxdepth 1 -type f -print
find /var/log/redis -maxdepth 1 -type f -print

# Verify service-manager logs
journalctl -u memcached --no-pager -n 50
journalctl -u redis-service-name --no-pager -n 50
```

Expected results:

- Memcached is active and enabled.
- Memcached listens on TCP and UDP port `11211`, bound to all interfaces.
- Memcached service directories and service-account ownership are correct.
- Redis is active and enabled using the selected service unit.
- Redis listens on TCP port `6379`.
- `/etc/redis/6379.conf` contains port `6379`.
- The five removed Redis directives are not present as active configuration lines.
- Redis `PING` returns `PONG`.
- The Redis functional test returns `success` and then deletes the temporary key.
- The configuration cleanup is idempotent.