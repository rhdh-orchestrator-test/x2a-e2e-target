---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache services: the Memcached instance named `memcached` and the Redis listener on port `6379`. Memcached uses the `memcached_instance` custom resource with source-reported defaults of 64 MB memory, TCP/UDP port `11211`, binding to `0.0.0.0`, 1,024 maximum connections, a `1m` maximum object size, and a `1024` ulimit. Redis uses `/run/redis` for PID files, creates `/var/log/redis` with `redis:redis` ownership and mode `0755`, configures password authentication, removes five unsupported replication-related directives from `/etc/redis/6379.conf`, and enables Redis through the unavailable `redisio::enable` recipe. Detailed values from the dependency attributes and unavailable Redis cookbook must be verified against the source implementations before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: In-memory key/value cache
  - Location/Path: Service configuration path is provider-dependent; the dependency attribute defines `/var/log/memcached` as the log path
  - Port/Socket: TCP `11211`, UDP `11211`
  - Key Config: Bind address `0.0.0.0`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; service user `service_user`; ulimit `1024`; experimental options `[]`; extra CLI options `[]`; start and enable actions
  - Threads: `node['memcached']['threads']`; not defined in the supplied attributes content
  - Version: Unspecified; `node['memcached']['version']` defaults to `nil`

- **Redis listener on port 6379**: In-memory data store and cache
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication enabled; password is source-reported as `redis_secure_password_123` and must be migrated to Ansible Vault or another approved secret mechanism; Redis log directory owner `redis`, group `redis`, mode `0755`; Redis enablement delegated to unavailable `redisio::enable`
  - Configuration cleanup: Remove active lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Bind address: Not explicitly established by the supplied `cache` recipe; verify the effective Redis dependency configuration before migration

No collection iteration or `.each` loop is present in the supplied recipe content. There are no repeated collection items to expand.

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

No provider file path was supplied. The `memcached_instance` custom resource is used, but its provider implementation is not available in the analyzed files.

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

The following files are present in the directory listing but are not executed by the supplied execution tree and must not be migrated as active recipe flow:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe with `include_recipe 'memcached'`.
   - Execution continues to `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Assigns one Redis server configuration for port `6379`.
   - Sets the source-reported Redis password value and `replicaservestaledata` to `nil`.
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` recipe. Its package installation, service-account creation, configuration rendering, and service setup cannot be verified from the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Does not create `/etc/redis/6379.conf` when the file does not already exist.
   - Does not explicitly notify Redis to restart or reload after modifying the configuration.
   - Includes the unavailable `redisio::enable` recipe, whose intended behavior is to enable Redis at boot. The actual service unit name must be determined from the selected Redis implementation.
   - Resources in the supplied execution flow:
     1. `include_recipe 'memcached'`
     2. Redis attribute assignments
     3. `include_recipe 'redisio'`
     4. `directory[/var/log/redis]`
     5. `ruby_block[fix_redis_config]`
     6. `include_recipe 'redisio::enable'`

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates one `memcached_instance[memcached]` custom resource.
   - Configures memory `64` MB.
   - Configures TCP port `11211`.
   - Configures UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Sets the service user to `service_user`.
   - Sets maximum object size to `1m`.
   - Uses the `node['memcached']['threads']` value; this is not defined in the supplied attributes content.
   - Uses empty experimental and extra CLI option lists.
   - Sets the ulimit to `1024`.
   - Applies `:start` and `:enable` actions.
   - The custom-resource provider, package name, configuration-file path, and service-unit name are not present in the supplied execution tree and must be determined from the selected Memcached implementation.
   - The analyzed attributes source reports the following defaults, which require source verification before migration:
     - `node['memcached']['version'] = nil`
     - `node['memcached']['memory'] = 64`
     - `node['memcached']['port'] = 11211`
     - `node['memcached']['udp_port'] = 11211`
     - `node['memcached']['listen'] = '0.0.0.0'`
     - `node['memcached']['maxconn'] = 1024`
     - `node['memcached']['max_object_size'] = '1m'`
     - `node['memcached']['experimental_options'] = []`
     - `node['memcached']['extra_cli_options'] = []`
     - `node['memcached']['ulimit'] = 1024`
     - `node['memcached']['logfilepath'] = '/var/log/memcached'`
   - `logfilepath` is not passed explicitly to `memcached_instance[memcached]`; it is an available dependency default, not proof that this cookbook explicitly configures a log file.

## Dependencies

**External cookbook dependencies**:

- `memcached`, constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package resources are declared directly by the analyzed recipes.
- Memcached and Redis packages are expected to be installed by the external `memcached` and `redisio` cookbooks.
- Exact package names are not specified in the supplied execution tree and must be verified from the selected dependency implementations.
- Do not infer or introduce unverified package names during migration.

**Service dependencies**:

- Memcached must be started and enabled.
- Redis must be enabled through the unavailable `redisio::enable` behavior.
- The Redis service-unit name is not specified.
- The Memcached service-unit name is not specified by the supplied custom-resource provider.

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext recipe value
- **Usage context**: Redis password authentication for the Redis listener on port `6379`
- **Migration requirement**: Store the password in Ansible Vault or another approved AAP secret mechanism. Do not place the plaintext value in committed role variables, rendered templates, command-line arguments, shell history, CI logs, or task output.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings with embedded credentials were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- `/var/log/memcached`, if created by the selected Memcached implementation
- The actual Memcached configuration file created by the selected provider
- The actual Redis service unit and configuration files created by the selected dependency implementation

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`; effective bind address must be verified from the installed Redis configuration

**Configuration checks**:

- Confirm `/etc/redis/6379.conf` exists when Redis is provisioned.
- Confirm the Redis configuration contains port `6379`.
- Confirm password authentication is enabled without exposing the password.
- Confirm no active lines begin with:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- Confirm `/var/log/redis` has owner `redis`, group `redis`, and mode `0755`.
- Confirm `/run/redis` is used as the Redis PID directory.
- Confirm Memcached uses TCP and UDP port `11211`, binding `0.0.0.0`, memory `64` MB, maximum connections `1024`, maximum object size `1m`, and ulimit `1024`.

**Templates rendered**:

- None

**Template render count**:

- No `.erb` templates rendered by the supplied recipes.

## Pre-flight checks

```bash
# Identify the installed Memcached service unit.
systemctl list-unit-files | grep -i memcached

# Replace memcached with the actual discovered unit if necessary.
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Confirm the Memcached process and TCP/UDP listeners.
ps aux | grep '[m]emcached'
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'

# Confirm the Memcached statistics endpoint.
printf "stats\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Inspect the actual service command line and provider-created configuration.
systemctl show memcached --property=ExecStart
grep -E '(^|[[:space:]])(-m[[:space:]]+64|-p[[:space:]]+11211|-U[[:space:]]+11211|-l[[:space:]]+0\.0\.0\.0|-c[[:space:]]+1024)' \
  /etc/memcached.conf /etc/sysconfig/memcached 2>/dev/null

# Verify the Memcached log path if it is created by the selected implementation.
test -e /var/log/memcached && tail -n 50 /var/log/memcached
```

```bash
# Redis instance on port 6379: locate the actual service unit.
systemctl list-unit-files | grep -Ei 'redis|redis-server'
systemctl status redis
systemctl status redis-server

# Confirm the Redis process and listener.
ps aux | grep '[r]edis-server'
ss -ltnp | grep ':6379'

# Supply the Redis password through a protected mechanism.
# REDIS_PASSWORD must not be printed, committed, or exposed in CI output.
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379 PING
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -h 127.0.0.1 -p 6379 INFO server | \
  grep -E 'redis_version|tcp_port'

# Confirm authentication is required without credentials.
redis-cli -h 127.0.0.1 -p 6379 PING

# Verify the Redis port and authentication-related settings.
grep -E '^(port|requirepass|masterauth)[[:space:]]' /etc/redis/6379.conf

# Verify that the five unsupported directives were removed.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || true
```

```bash
# Verify the Redis PID directory.
ls -ld /run/redis
stat -c '%U:%G %a %n' /run/redis

# Verify the Redis log directory.
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis

# Expected Redis log-directory ownership and mode:
# redis:redis and 755
```

```bash
# Verify Redis enablement using the actual discovered unit.
systemctl is-enabled redis
systemctl is-active redis

# If the platform uses redis-server instead:
systemctl is-enabled redis-server
systemctl is-active redis-server
```

```bash
# Confirm the Redis configuration file exists and remains unchanged when absent.
test -f /etc/redis/6379.conf

# The command should return no matching active configuration lines.
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || true
```

```bash
# Inspect service logs using the actual installed unit names.
journalctl -u memcached --no-pager -n 50
journalctl -u redis --no-pager -n 50
journalctl -u redis-server --no-pager -n 50

# Inspect files in the Redis log directory.
find /var/log/redis -maxdepth 1 -type f -print
```