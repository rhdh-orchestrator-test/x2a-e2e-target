---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` on TCP and UDP port `11211`, with 64 MB of memory, 1,024 maximum connections, a `0.0.0.0` listen address, and service enablement; and one Redis instance on port `6379`, using `/run/redis` for its PID base directory and `/var/log/redis` for logs. Redis requires authentication, removes five replication-related directive families from `/etc/redis/6379.conf`, and is enabled after configuration cleanup. The Redis password is hardcoded in the Chef recipe and must be migrated to approved secret storage.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Configuration path is provider- and platform-dependent; no provider path was supplied.
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`; no Unix socket configured.
  - Key Config: `64` MB memory, `1m` maximum object size, `1024` maximum connections, ULimit `1024`, service action `start` and `enable`. Threads, experimental options, and extra CLI options are sourced from node attributes without defined values in the analyzed attributes file. Version is `nil`. The service user is supplied through the unresolved Chef expression `service_user`.

- **6379**: Redis server
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID base directory `/run/redis`; log directory `/var/log/redis`.
  - Port/Socket: TCP port `6379`; no Unix socket configured or referenced.
  - Key Config: Authentication required using the configured Redis password; log directory owner `redis`, group `redis`, mode `0755`, created recursively. The following directive families are removed from the Redis configuration: `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`. Redis is enabled after configuration cleanup.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

### Recipes

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

### Providers

```text
```

No provider file was supplied for `memcached_instance`. The execution tree identifies it as a custom resource, but does not provide a provider path.

### Templates

```text
```

No rendered templates were identified.

### Attributes

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

### Files

```text
```

No static files deployed by `cookbook_file` or `remote_file` were identified.

## Module Explanation

The cookbook performs operations in this order:

1. **Cache entry recipe** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` dependency recipe.
   - Sets `node.default['redisio']['servers']` to one Redis server definition:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes the `redisio` recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Runs the `ruby_block['fix_redis_config']` cleanup when `/etc/redis/6379.conf` exists.
   - Includes `redisio::enable` last.
   - Resources used: `directory['/var/log/redis']` and `ruby_block['fix_redis_config']`.
   - No `.each` loops are present.

2. **Memcached dependency recipe** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares one `memcached_instance` custom resource named `memcached`.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ULimit `1024`, and actions `start` and `enable`.
   - Passes `service_user` as the service user expression.
   - Sources threads, experimental options, and extra CLI options from node attributes.
   - The dependency provider implementation is not included, so package names, generated unit paths, and configuration locations must be verified on the target platform.
   - Iteration expansion: one explicit instance, `memcached`.

3. **Redis dependency recipe** (`redisio`):
   - Referenced by the entry recipe but not present in the supplied execution tree.
   - Intended to configure Redis server instance `6379`.
   - Uses `/run/redis` as the base PID directory.
   - The migration must provide the Redis package, service, configuration, and authentication through the selected Ansible role or collection.
   - Package names, service names, templates, and generated configuration paths must be verified on the target operating system.

4. **Redis log directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Sets owner `redis`, group `redis`, mode `0755`, and `recursive true`.
   - Resource count: `directory['/var/log/redis']`: `1`.
   - The `redis` service account must exist before the directory is created.

5. **Redis configuration cleanup resource** (`cookbooks/cache/recipes/default.rb`):
   - Declares `ruby_block['fix_redis_config']`.
   - Processes `/etc/redis/6379.conf` only when the file exists.
   - Removes lines matching:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified configuration back.
   - Resource count: `ruby_block['fix_redis_config']`: `1`.
   - The Chef resource does not declare an explicit service notification. The Ansible implementation should use idempotent edits and restart or reload Redis only when the file changes.

6. **Redis enable recipe** (`redisio::enable`):
   - Referenced by the entry recipe but not present in the supplied execution tree.
   - Enables the Redis service after configuration and cleanup.
   - The exact service unit name must be discovered on the target platform; do not assume `redis`, `redis-server`, or `redis@6379`.

## Dependencies

**External cookbook dependencies**: `memcached`, `redisio`. The Memcached dependency recipe is present in the supplied execution tree. The `redisio` and `redisio::enable` recipes are referenced but unavailable.

**System package dependencies**: Memcached and Redis packages are required, but exact distribution-specific package names are not exposed by the analyzed recipes and must be verified for the target operating system. Memcached installation is encapsulated by `memcached_instance`; Redis installation is encapsulated by the unavailable `redisio` recipe.

**Service dependencies**: Memcached must be started and enabled. Redis must be configured and enabled after the Redis service account exists and the configuration cleanup is complete. The `redis` service account is required before `/var/log/redis` is created.

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:
  - **Provider**: None detected; the password is embedded directly in the recipe.
  - **URL**: None detected.
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute. Literal value: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for instance `6379`.

The password must be moved to Ansible Vault, an AAP credential, or another approved secret-management integration. It must not remain in plaintext in playbooks, role defaults, inventory, or a rendered configuration repository.

No data bag, encrypted data bag, Chef Vault, Conjur, CyberArk, environment-variable secret reference, TLS certificate, private key, or database connection credential was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- Memcached configuration file generated by the selected Ansible implementation
- Memcached service unit provided by the target operating system
- Redis service unit provided by the target operating system

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `6379`: TCP port `6379`
- Redis instance `6379`: no Unix socket

**Templates rendered**: None identified; `0` Chef templates were rendered. The cookbook uses a custom Memcached resource and an unavailable Redis dependency recipe rather than explicitly referenced `.erb` files.

## Pre-flight checks

```bash
# Verify the target operating system and package names before installation.
cat /etc/os-release

# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

printf "version\r\n" | nc -w 2 127.0.0.1 11211
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'

# Verify Memcached settings using the configuration path selected for the target platform.
grep -E '(^|[[:space:]])(-m[[:space:]]+64|64)([[:space:]]|$)' /etc/memcached.conf
grep -E '(^|[[:space:]])(-p[[:space:]]+11211|11211)([[:space:]]|$)' /etc/memcached.conf
grep -E '(^|[[:space:]])(-U[[:space:]]+11211|11211)([[:space:]]|$)' /etc/memcached.conf
grep -E '(^|[[:space:]])(-c[[:space:]]+1024|1024)([[:space:]]|$)' /etc/memcached.conf

# Redis instance: 6379
systemctl list-unit-files | grep -E 'redis'
systemctl status <verified-redis-service-name>
systemctl is-enabled <verified-redis-service-name>
systemctl is-active <verified-redis-service-name>

# Use an approved secret-injection mechanism; do not expose the password in shell history.
export REDISCLI_AUTH='<password-from-Ansible-Vault>'
redis-cli -h 127.0.0.1 -p 6379 PING
unset REDISCLI_AUTH

# Expected Redis response:
# PONG

# Validate Redis configuration and removed directive families.
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify Redis log directory ownership and mode.
stat -c '%A %U %G %n' /var/log/redis
# Expected:
# drwxr-xr-x redis redis /var/log/redis

# Verify Redis instance 6379 network and process state.
ss -tlnp | grep ':6379'
ps -ef | grep '[r]edis'
ls -ld /run/redis
find /run/redis -maxdepth 1 -type f -ls

# Verify Redis logs using the discovered service name.
journalctl -u <verified-redis-service-name> -n 100 --no-pager
ls -lah /var/log/redis

# Run the migration twice to verify idempotence.
ansible-playbook -i inventory cache.yml
ansible-playbook -i inventory cache.yml
```

The second Ansible run should report no changes to `/var/log/redis`, Redis configuration cleanup, Memcached configuration, Redis enablement, or Memcached enablement. The Redis password must remain protected by Ansible Vault or the selected AAP credential mechanism throughout both runs.