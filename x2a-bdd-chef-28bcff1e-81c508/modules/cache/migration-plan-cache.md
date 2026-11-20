---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: one Memcached instance named `memcached` on TCP and UDP port `11211`, and one Redis instance configured on port `6379`. The execution flow first includes the external `memcached::default` recipe, then configures Redis attributes, includes the unavailable `redisio` recipe, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and includes the unavailable `redisio::enable` recipe. Memcached settings are confirmed by the supplied Memcached recipe and attributes. Redis package, service-unit, provider, and template details must be verified on the target platform.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached in-memory key-value cache
  - Location/Path: `/var/log/memcached`, `/var/run/memcached`
  - Port/Socket: TCP `11211`, UDP `11211`
  - Key Config: Listen address `0.0.0.0`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; ulimit `1024`; experimental options `[]`; additional CLI options `[]`; actions `start` and `enable`
  - Service account: `service_user`
  - Service group: `service_group`
  - Package version: `nil`, using the platform package manager's default version

- **6379**: Redis server configured on port `6379`
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: Password `redis_secure_password_123`; log directory owner `redis`; log directory group `redis`; log directory mode `0755`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` when present

The Redis package name, provider implementation, configuration template, and service resource are unavailable in the supplied execution tree. The migration must verify those details on the target platform.

## File Structure

**Complete analyzed-file inventory:**

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

**Recipes:**

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

The executed recipe flow includes only `cookbooks/cache/recipes/default.rb` and `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`. The `_package.rb` and SELinux recipes are present in the analyzed inventory but are not shown as executed.

**Providers:**

```text
```

No provider file path was supplied for the `memcached_instance` custom resource.

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

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default` before Redis configuration.
   - Sets the Redis server entry for port `6379` with password `redis_secure_password_123` and `replicaservestaledata = nil`.
   - Sets `redisio.base_piddir` to `/run/redis`.
   - Includes `redisio`; the referenced recipe is unavailable in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Runs `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf` when the file exists.
   - Removes lines beginning with `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`.
   - Writes the modified Redis configuration back to `/etc/redis/6379.conf`.
   - Includes `redisio::enable`; the referenced recipe is unavailable.
   - The Redis package name, service name, service resource, and configuration deployment behavior must be determined from the target platform.
   - Confirmed resources in the supplied structured execution tree: `directory[/var/log/redis]` and `ruby_block[fix_redis_config]`.
   - No confirmed `group[redis]` resource appears in the supplied structured execution tree. The Ansible implementation should ensure the `redis` group exists as an ownership prerequisite, but this should not be represented as a confirmed Chef resource.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Configures the exact instance name `memcached`.
   - Installs the confirmed `memcached` package.
   - Configures memory `64` MB.
   - Configures TCP port `11211`.
   - Configures UDP port `11211`.
   - Configures listen address `0.0.0.0`.
   - Configures maximum connections `1024`.
   - Configures maximum object size `1m`.
   - Passes the node-supplied `threads` attribute; no explicit default is shown in the supplied attributes file.
   - Configures `experimental_options` as `[]`.
   - Configures `extra_cli_options` as `[]`.
   - Configures ulimit `1024`.
   - Uses service user `service_user` and service group `service_group`.
   - Creates or manages `/var/log/memcached` and `/var/run/memcached` with mode `0755`.
   - Starts and enables the Memcached service.

No `.each` loops are present in the supplied recipes.

## Dependencies

**External cookbook dependencies**: `memcached`, `redisio`

The `redisio` recipe files are unavailable in the supplied execution tree.

**System package dependencies**: `memcached`

The Redis package name is not identifiable from the supplied files and must be verified on the target platform.

**Service dependencies**:

- Memcached service for instance `memcached`: started and enabled by `memcached_instance[memcached]`
- Redis service for instance `6379`: intended to be enabled by `redisio::enable`; the exact service unit name is unavailable
- Redis group `redis`: required for ownership of `/var/log/redis`; no corresponding Chef group resource is confirmed

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: Redis `requirepass`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded directly in the Chef recipe; source value is `redis_secure_password_123`
- **Usage context**: Redis client authentication for instance `6379`
- **Migration handling**: Store the password in Ansible Vault or an AAP credential/secret integration. Do not place it in a plaintext role default or committed variable file. Render it into the Redis configuration with restrictive permissions.

No data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur variables, environment-variable secrets, TLS certificate paths, private keys, API keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `6379`: TCP port `6379`
- Redis instance `6379`: no Unix socket specified

**Templates rendered**:

- None detected; rendered count: `0`

**Configuration mutations**:

- `/etc/redis/6379.conf` is edited in place when present.
- The five specified Redis directives must be absent after convergence.

## Pre-flight checks:

### Memcached instance `memcached`

```bash
# Verify package installation
rpm -q memcached 2>/dev/null || dpkg-query -W memcached

# Verify service state
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Verify the Memcached process
pgrep -a memcached

# Verify TCP listening on port 11211
ss -ltnp | grep ':11211'
lsof -nP -iTCP:11211 -sTCP:LISTEN

# Verify UDP listening on port 11211
ss -lunp | grep ':11211'

# Verify runtime and log directories
ls -ld /var/run/memcached
ls -ld /var/log/memcached

# Verify Memcached connectivity
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
printf 'stats\r\n' | nc -w 2 127.0.0.1 11211

# Inspect service configuration and recent logs
systemctl cat memcached
journalctl -u memcached --no-pager -n 50

# Verify directory ownership and permissions
stat -c '%U:%G %a %n' /var/run/memcached
stat -c '%U:%G %a %n' /var/log/memcached
```

Expected results:

- Package `memcached` is installed.
- Service `memcached` is enabled and active.
- TCP and UDP port `11211` are listening on `0.0.0.0`.
- The `version` command returns a Memcached version.
- The `stats` command returns Memcached statistics.
- Runtime and log directories exist with the expected permissions.

### Redis instance `6379`

```bash
# Confirm the platform-specific Redis service name
systemctl list-unit-files | grep -E '^redis(-server)?\.service'

# Replace redis.service with the confirmed unit name
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Verify the Redis process
pgrep -a redis

# Verify Redis is listening on port 6379
ss -ltnp | grep ':6379'
lsof -nP -iTCP:6379 -sTCP:LISTEN

# Verify the configuration file exists
test -f /etc/redis/6379.conf
ls -l /etc/redis/6379.conf

# Verify Redis directories
ls -ld /run/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /run/redis
stat -c '%U:%G %a %n' /var/log/redis

# Verify authentication and Redis availability
redis-cli -p 6379 -a 'redis_secure_password_123' PING
redis-cli -p 6379 -a 'redis_secure_password_123' INFO server

# Verify that unwanted directives were removed
if grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf; then
  echo "Unexpected Redis directives remain"
  exit 1
fi
```

Expected results:

- Redis is enabled and active under the confirmed platform-specific unit name.
- Redis listens on port `6379`.
- `redis-cli` authentication succeeds and `PING` returns `PONG`.
- `INFO server` returns Redis server information.
- No unwanted replication-related directives remain in `/etc/redis/6379.conf`.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.

### Redis logs and configuration

```bash
# Use the confirmed Redis service unit name
journalctl -u redis --no-pager -n 100

# Inspect the configured Redis log files
find /var/log/redis -maxdepth 1 -type f -ls

# Verify configuration ownership and permissions
stat -c '%U:%G %a %n' /etc/redis/6379.conf

# Confirm the password directive without exposing the password in migration logs
grep -n '^requirepass' /etc/redis/6379.conf
```

The exact Redis log filename must be taken from the deployed Redis configuration because the cookbook only confirms creation of `/var/log/redis`, not a specific log file.

### Package and connectivity validation

```bash
# Confirm Memcached is reachable
nc -vz 127.0.0.1 11211

# Confirm Redis is reachable
nc -vz 127.0.0.1 6379

# Confirm Redis group ownership prerequisite
getent group redis
```

Use masked or secret-aware validation in Ansible Automation Platform so the Redis password is not displayed in normal migration output.