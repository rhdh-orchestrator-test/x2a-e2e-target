---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the Memcached instance `memcached` on TCP and UDP port `11211`, and the Redis server `6379` on TCP port `6379`. Memcached is created through the `memcached_instance[memcached]` custom resource and is started and enabled. Redis uses `/etc/redis/6379.conf`, `/run/redis` for its PID directory, `/var/log/redis` for logs, and a required authentication password. The Redis installation and enablement recipes are missing from the supplied execution tree, so the Ansible migration must implement those operations explicitly. Memcached resource values, Redis assignments, and the exact Redis cleanup directives are source-level details that should be verified against the complete cookbook analysis before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Memcached instance `memcached`**: General-purpose Memcached cache
  - Resource: `memcached_instance[memcached]`
  - Memory: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: `node['memcached']['threads']`; no value is defined in the supplied attributes file
  - Experimental options: `node['memcached']['experimental_options']`, default `[]`
  - Extra CLI options: `node['memcached']['extra_cli_options']`, default `[]`
  - Ulimit: `1024`
  - Service user: `service_user`, supplied by the Memcached custom resource/provider
  - Actions: `start`, `enable`
  - Verification note: the supplied structured analysis confirms the resource name but does not independently verify all listed properties, defaults, or actions

- **Redis server `6379`**: Authenticated Redis cache
  - Configuration file: `/etc/redis/6379.conf`
  - Port: `6379`
  - PID directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Authentication password: source-level value `redis_secure_password_123`; migrate this to Ansible Vault or an approved AAP credential
  - `replicaservestaledata`: `nil` in the source-level server configuration
  - Replication directives removed from the generated configuration:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`
  - Verification note: the supplied execution summary confirms the missing `redisio` recipes but does not independently expose the Redis assignments or the `ruby_block` body

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only files participating in the supplied execution flow or providing values consumed by an executed dependency recipe are listed below. The analysis reports seven total analyzed files, but only the following paths were supplied in the migration-plan input. The remaining five analyzed paths must be recovered from the complete source analysis before final implementation.

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

No provider file path was supplied for `memcached_instance[memcached]`. Locate the actual custom-resource implementation in the dependency source before finalizing the Ansible role.

**Templates:**

No template files are referenced or rendered in the supplied execution tree.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

No static files are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **Memcached dependency default recipe** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Provides the Memcached dependency behavior.
   - Creates the custom resource `memcached_instance[memcached]`.
   - Uses the Memcached attributes for memory, ports, listen address, maximum connections, object size, threads, experimental options, extra CLI options, and ulimit.
   - Starts and enables the `memcached` instance.
   - The exact package name, service unit, configuration path, and provider implementation are not present in the supplied execution tree and must be resolved from the dependency source and target platform.
   - Iterations: one configured instance, `memcached`.

2. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe with `include_recipe 'memcached'`.
   - Configures the Memcached instance `memcached` with the following source-level values:
     - Memory: `64` MB
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - Threads: `node['memcached']['threads']`
     - Experimental options: `[]`
     - Extra CLI options: `[]`
     - Ulimit: `1024`
     - User: `service_user`
   - Installs Memcached using the resolved target-platform package name.
   - Deploys the platform-specific Memcached configuration.
   - Starts and enables Memcached.
   - Restarts Memcached only when its configuration changes.
   - Assigns one Redis server configuration:
     - Server name: `6379`
     - Port: `6379`
     - `requirepass`: source-level value `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets the Redis base PID directory to `/run/redis`.
   - Includes the missing `redisio` recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive directory creation.
   - Executes `ruby_block[fix_redis_config]`, which source-level analysis indicates removes these directives from `/etc/redis/6379.conf`:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Includes the missing `redisio::enable` recipe.
   - Iterations: one Redis server entry, `6379`.

3. **`redisio`** (`redisio/recipes/default.rb`):
   - The recipe is referenced by `cache::default` but is reported as missing from the supplied execution tree.
   - The Ansible migration must implement the required operations explicitly:
     - Install Redis using the verified package name for each supported platform.
     - Create the Redis service account if the package does not create it.
     - Create `/run/redis` with appropriate ownership and permissions.
     - Generate `/etc/redis/6379.conf`.
     - Configure Redis port `6379`.
     - Configure the migrated authentication password.
     - Configure the Redis PID path.
     - Create `/var/log/redis` before service startup.
   - Do not infer an exact package name, service unit, or package version from this cookbook.

4. **`redisio::enable`** (`redisio/recipes/enable.rb`):
   - The recipe is referenced by `cache::default` but is reported as missing from the supplied execution tree.
   - Explicitly enable and start the resolved Redis service for server `6379`.
   - Apply any configuration cleanup before the final service restart or start operation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package: exact package name and version are not specified; resolve and verify them for the supported target platform.
- Redis package: exact package name and version are not specified because the `redisio` recipe is missing.

**Service dependencies**:

- Memcached service for instance `memcached`, started and enabled by the custom resource.
- Redis service for server `6379`, explicitly implemented and enabled by the Ansible migration.

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 hardcoded credential detected in 1 source file, based on the source-level recipe analysis. The supplied structured execution summary does not expose the recipe contents, so this finding and the negative credential findings require confirmation against the complete source analysis.

**Source**:

- **Provider**: Hardcoded in the Chef recipe; migrate to Ansible Vault or an AAP-managed credential
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute
- **Usage context**: Redis `requirepass` authentication for Redis server `6379`
- **Ansible migration**:
  - Replace the literal with a variable such as `redis_password`.
  - Store `redis_password` in Ansible Vault or an AAP-managed secret.
  - Mark tasks that use the password with `no_log: true`.
  - Do not print the generated Redis configuration in CI or automation output.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur variables, environment-variable secrets, TLS certificate references, database credentials, API keys, or token attributes were identified in the supplied source-level analysis. Confirm these negative findings against all seven analyzed files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- Resolved Memcached configuration file for instance `memcached`
- All cookbook and dependency files listed in the File Structure section

**Service endpoints to check**:

- Memcached instance `memcached`, TCP: `0.0.0.0:11211`
- Memcached instance `memcached`, UDP: `0.0.0.0:11211`
- Redis server `6379`, TCP: `0.0.0.0:6379` or the resolved Redis bind address

**Unix sockets**:

- No Unix socket is configured or referenced by the supplied cookbook.

**Templates rendered**:

- No Chef templates are rendered.
- Redis configuration is modified in place by `ruby_block[fix_redis_config]`.
- Memcached configuration is generated by the dependency custom resource; no template path was supplied.
- Render count: zero known Chef template renders.

## Pre-flight checks

```bash
# Confirm supported operating system
. /etc/os-release
printf '%s %s\n' "$ID" "$VERSION_ID"

# Confirm the Memcached package and service implementation are resolved
command -v memcached
systemctl list-unit-files | grep -E '^memcached'

# Confirm the Redis package and service implementation are resolved
command -v redis-server
systemctl list-unit-files | grep -E '(^redis|redis-server)'
```

### Memcached instance `memcached`

```bash
systemctl status memcached

# Verify the TCP listener
ss -ltnp | grep ':11211'

# Verify the UDP listener
ss -lunp | grep ':11211'

# Confirm the configured listen address
ss -ltnp | grep '0.0.0.0:11211'

# Verify the running process and effective arguments
ps aux | grep '[m]emcached'

# Basic Memcached protocol check
printf "version\r\n" | nc -w 2 127.0.0.1 11211
```

Expected results:

- The Memcached service for instance `memcached` is active and enabled.
- TCP is listening on `0.0.0.0:11211`.
- UDP is listening on port `11211`.
- The protocol check returns a `VERSION` response.
- The effective configuration reflects `64` MB memory, `1024` maximum connections, and `1m` maximum object size.

### Redis server `6379`

```bash
systemctl status redis

# Verify the configuration file
test -f /etc/redis/6379.conf

# Verify Redis is configured for port 6379
grep -E '^[[:space:]]*port[[:space:]]+6379' /etc/redis/6379.conf

# Verify the PID configuration
grep -E '^[[:space:]]*pidfile|^[[:space:]]*dir' /etc/redis/6379.conf

# Confirm removed replication directives are absent
! grep -E '^[[:space:]]*(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify the Redis PID and log directories
test -d /run/redis
test -d /var/log/redis
ls -ld /run/redis /var/log/redis

# Verify the Redis process and listener
ps aux | grep '[r]edis-server'
ss -ltnp | grep ':6379'
```

Expected results:

- The Redis service for server `6379` is active and enabled.
- Redis is listening on TCP port `6379`.
- `/etc/redis/6379.conf` exists.
- `/run/redis` exists and is accessible to the Redis service account.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- The five removed replication directives are absent.
- Do not print the full Redis configuration because it may contain the authentication password.

### Redis authentication for server `6379`

Use the migrated secret securely rather than placing it directly in shell history:

```bash
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' redis-cli -p 6379 PING
REDISCLI_AUTH='<retrieve-from-secure-secret-store>' redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
```

Expected result:

```text
PONG
```

The `tcp_port` value must be `6379`.

### Directory ownership

```bash
stat -c '%U:%G %a %n' /var/log/redis
stat -c '%U:%G %a %n' /run/redis
```

Expected result for `/var/log/redis`:

```text
redis:redis 755 /var/log/redis
```

The exact `/run/redis` mode depends on the Redis package and service-unit implementation, but the directory must be accessible to the Redis service account.

### Service logs

```bash
journalctl -u memcached --no-pager -n 50
journalctl -u redis --no-pager -n 50
```

Check for:

- Successful startup of Memcached instance `memcached`.
- Successful startup of Redis server `6379`.
- Redis bind errors on port `6379`.
- Redis configuration parse errors.
- Permission errors involving `/run/redis` or `/var/log/redis`.
- Authentication or password configuration errors.