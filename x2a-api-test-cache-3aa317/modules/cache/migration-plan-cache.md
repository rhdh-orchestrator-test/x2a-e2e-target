---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Memcached instance named `memcached` on TCP and UDP port `11211` and one Redis instance named `6379` on TCP port `6379`. Memcached uses 64 MB of memory, 1024 maximum connections, a `0.0.0.0` listener, a `1m` maximum object size, and a `1024` ulimit. The Memcached service account is unresolved because the Chef expression `service_user` has no supplied definition. Redis requires password authentication, uses `/run/redis` for its PID directory, creates `/var/log/redis`, removes five replication-related directives from `/etc/redis/6379.conf`, and is enabled and started. The Redis implementation and `redisio::enable` recipe are missing, so the migration must provide equivalent installation, configuration, and service-management tasks. Redis bind address is undetermined from the supplied Chef files and must be selected explicitly during migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached cache service
  - Location/Path: Target distribution Memcached service configuration; log path `/var/log/memcached`
  - Port/Socket: TCP `11211`; UDP `11211`; listen address `0.0.0.0`
  - Key Config: Memory `64` MB; maximum connections `1024`; maximum object size `1m`; ulimit `1024`; threads read from `node['memcached']['threads']`, with no supplied default; version `nil`; experimental options `[]`; additional CLI options `[]`; actions `start`, `enable`
  - Service user: The Chef resource passes the unresolved expression `service_user`. Its literal value or definition was not supplied and must be determined or explicitly provided during migration.

- **`6379`**: Redis server instance
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; Redis bind address is not specified in the supplied Chef files and must be selected explicitly
  - Key Config: Password authentication enabled; password is hardcoded in the source as `redis_secure_password_123` and must be moved to Ansible Vault or an approved AAP secret mechanism; log directory owner `redis`, group `redis`, mode `0755`, recursive creation; service enabled and started
  - Configuration cleanup: Remove `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`

No `.each` loops or collection iterations are present. The execution flow configures exactly one Memcached instance, `memcached`, and one Redis instance, `6379`.

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

The `memcached_instance` custom resource is used, but no provider file was supplied in the execution tree or directory listing. No provider path should be assumed during migration.

**Templates:**
```text
```

No rendered Chef templates were identified.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` were identified.

**Data bags:**
```text
data_bags/nginx_secrets/site.json
data_bags/nginx_sites/ci.cluster.local.json
data_bags/nginx_sites/status.cluster.local.json
data_bags/nginx_sites/test.cluster.local.json
```

The listed `nginx_*` data bags are present in the analyzed source but are not referenced by the `cache` execution flow. The paths above are the files relevant to the cache execution flow and its identified credential/data-bag references; they do not represent a reconciliation of every file in the reported total analyzed-file count of 11.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the `memcached` dependency, which executes `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Defines one Redis server in `node['redisio']['servers']` with port `6379`, password authentication, and no configured `replicaservestaledata` value.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`; the referenced Redis recipe is missing from the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes the `fix_redis_config` Ruby block after the Redis include. If `/etc/redis/6379.conf` exists, removes complete lines matching:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Includes `redisio::enable`; this recipe is also missing.
   - The Ansible role must supply the missing Redis package installation, user/group handling, configuration, PID directory, service startup, and service enablement for instance `6379`.
   - Redis bind address is not defined by this recipe or by the supplied analysis. The migration must choose and document the target bind address rather than assuming `0.0.0.0`.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates `memcached_instance[memcached]`.
   - Installs and configures Memcached instance `memcached`.
   - Sets memory to `64` MB.
   - Sets TCP port to `11211`.
   - Sets UDP port to `11211`.
   - Sets listen address to `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Sets maximum object size to `1m`.
   - Passes the unresolved Chef expression `service_user` as the service user; the migration must determine or explicitly provide the target account.
   - Reads threads from `node['memcached']['threads']`; no default value is present in the supplied attribute file, so the Ansible role must expose and explicitly resolve this variable.
   - Passes empty experimental-option and additional-CLI-option lists.
   - Sets ulimit to `1024`.
   - Starts and enables the Memcached service.
   - Uses `nil` as the configured Memcached version, meaning no explicit version is specified.
   - Uses `/var/log/memcached` as the configured log path.

## Dependencies

**External cookbook dependencies**:

- `memcached`, executed from `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `redisio`, referenced by `cache::default`, but its recipe file is missing
- `redisio::enable`, referenced by `cache::default`, but its recipe file is missing

**System package dependencies**:

- Memcached package: `memcached`
- Redis server package: `redis-server` on Debian-family systems or `redis` on common RHEL-family systems; select the package appropriate to the target distribution
- No package versions are specified by the supplied Chef files

**Service dependencies**:

- Memcached service for instance `memcached`
- Redis service serving port `6379`; the exact service name is distribution-dependent and is not present in the supplied files

## Credentials

**Detection Summary**: 2 credential-related sources detected across the analyzed source:

1. One hardcoded Redis password in `cookbooks/cache/recipes/default.rb`
2. One encrypted data bag item in `data_bags/nginx_secrets/site.json`

The encrypted data bag is not referenced by the cache execution flow. The three `nginx_sites` data bags contain configuration data, not credentials, and are not used by this cookbook flow.

**Source**:

- **Provider**: Internal Chef data bag and hardcoded recipe value
- **URL**: None detected
- **Path**:
  - Redis password: `node.default['redisio']['servers'][0]['requirepass']`
  - Encrypted data bag: `nginx_secrets/site`

### Redis authentication password

- **Variable(s)**: `requirepass` for Redis server port `6379`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe as `redis_secure_password_123`
- **Usage context**: Redis password authentication for instance `6379`
- **Migration handling**: Store the password in Ansible Vault or another approved AAP secret mechanism. Do not reproduce the plaintext password in committed variables or validation commands.

### Encrypted data bag token

- **Variable(s)**: `token`
- **Source file(s)**: `data_bags/nginx_secrets/site.json`
- **Current storage**: Encrypted Chef data bag item
- **Data bag/item**: `nginx_secrets/site`
- **Encrypted fields**: `id` and `token`
- **Usage context**: No usage found in the `cache` execution flow
- **Migration handling**: Do not include this value in the cache role unless another migration dependency consumes it. If required elsewhere, store the decrypted value in Ansible Vault or an AAP credential rather than copying the Chef encrypted payload.

No TLS certificate, private key, database connection string, environment-variable secret, Chef Vault lookup, CyberArk integration, Conjur lookup, or HashiCorp Vault lookup was detected in the supplied cache execution flow.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/run/redis`
- Target-distribution Memcached service configuration file
- Target-distribution Redis service configuration and unit files

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `6379`: TCP port `6379` on the explicitly selected migration bind address
- Unix sockets: None configured or identified

**Templates rendered**:

- None; no Chef templates were identified
- Render count: `0`

**Configuration edits**:

Remove these directives from `/etc/redis/6379.conf`:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
printf "version\r\n" | nc -w 2 127.0.0.1 11211
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
ps auxww | grep '[m]emcached'
ls -ld /var/log/memcached

# Confirm the effective Memcached settings:
# memory 64 MB, TCP/UDP port 11211, listen 0.0.0.0,
# max connections 1024, maximum object size 1m, and ulimit 1024.
# Also verify the explicitly selected service account because the Chef
# expression service_user has no supplied literal definition.

# Redis instance: 6379
# Replace REDIS_SERVICE_NAME with the service name selected for the target OS.
systemctl status "$REDIS_SERVICE_NAME"
systemctl is-enabled "$REDIS_SERVICE_NAME"
systemctl is-active "$REDIS_SERVICE_NAME"
ss -ltnp | grep ':6379'
ps auxww | grep '[r]edis-server'

# Populate REDISCLI_AUTH from Ansible Vault or an approved AAP credential.
export REDISCLI_AUTH="$REDIS_PASSWORD"
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep '^redis_version:'
unset REDISCLI_AUTH

# Redis configuration and paths
grep -E '^(port|requirepass|pidfile)' /etc/redis/6379.conf
stat -c '%A %U %G %n' /var/log/redis
ls -ld /run/redis
journalctl -u "$REDIS_SERVICE_NAME" --no-pager -n 100

# The following command must return no matching lines:
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Combined endpoint verification
ss -ltnp | grep -E ':(6379|11211)\b'
ss -lunp | grep ':11211'
```

Expected results:

- Memcached instance `memcached` is active and enabled, with TCP and UDP listeners on port `11211`.
- Memcached responds to the `version` request.
- Effective Memcached settings match the configured values.
- Redis instance `6379` is active and enabled, with a listener on TCP port `6379` at the explicitly selected bind address.
- Redis authentication succeeds using the protected `REDIS_PASSWORD` value and returns `PONG`.
- `/var/log/redis` has mode `0755`, owner `redis`, and group `redis`.
- `/run/redis` exists and is usable by the Redis service account.
- The five prohibited Redis directives are absent from `/etc/redis/6379.conf`.
- Redis and Memcached logs show no startup failures, authentication errors, port conflicts, or configuration parse errors.