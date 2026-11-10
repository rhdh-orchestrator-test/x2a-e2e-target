---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services. The explicitly named Memcached instance `memcached` uses the external `memcached` cookbook and is configured for 64 MB of memory, TCP/UDP port `11211`, listener `0.0.0.0`, 1024 maximum connections, 1 MB maximum object size, and ulimit `1024`. Redis is configured as a single server on port `6379`, with PID directory `/run/redis`, log directory `/var/log/redis`, and password authentication. The Redis configuration file `/etc/redis/6379.conf` is modified to remove five replication-related directive families. The supplied execution tree does not contain the `redisio` dependency recipes or provider implementation, so Redis package and service-unit details must be resolved for the target operating system rather than inferred.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service managed by the external `memcached` cookbook
  - Package: `memcached`
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached` if created by the external implementation
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`; no Unix socket
  - Key Config: 64 MB memory, 1024 maximum connections, 1 MB maximum object size, ulimit `1024`, start and enable actions
  - Threads: `node['memcached']['threads']`; no explicit default is present in the supplied attributes
  - Experimental options: `node['memcached']['experimental_options']`, default empty list
  - Extra CLI options: `node['memcached']['extra_cli_options']`, default empty list
  - User/group: `service_user`; resolved account name is not present in the supplied structured data

- **Redis server on port 6379**: Redis cache service configured through `redisio`
  - Package: Not determinable from the supplied execution tree; resolve for the target distribution
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket configured
  - Key Config: Password authentication, password source value `redis_secure_password_123` in the source recipe, and removal of five replication-related directive families
  - Service action: The wrapper invokes `redisio::enable`; the exact service unit is not supplied
  - Replica stale-data setting: `replicaservestaledata` explicitly assigned `nil`

The detailed Redis settings, Memcached defaults, and credential detection are reported by the supplied plan content. The validation notes indicate that these details are not independently represented in the structured-analysis summary and should be confirmed against the source files before implementation.

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

No provider file path was supplied for `memcached_instance`. The resource is implemented by the external `memcached` cookbook dependency.

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

No `cookbook_file` or `remote_file` resources, and no deployed static files, are shown.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Assigns one Redis server definition to `node['redisio']['servers']`:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Assigns `node['redisio']['base_piddir']` to `/run/redis`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Checks whether `/etc/redis/6379.conf` exists.
   - When the Redis configuration exists, removes lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified Redis configuration back to `/etc/redis/6379.conf`.
   - Includes `redisio::enable`.
   - The supplied execution tree reports that `redisio::enable` is missing; implement Redis service enablement only after the target service unit is confirmed.
   - Iterations: none.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes exactly one custom resource: `memcached_instance[memcached]`.
   - Configures instance `memcached` with:
     - Memory: `64`
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - Threads: `node['memcached']['threads']`
     - Experimental options: empty list by default
     - Extra CLI options: empty list by default
     - Ulimit: `1024`
     - User: `service_user`
   - Requests actions `start` and `enable`.
   - The external provider path and internal provider resources are not supplied.
   - The observable Ansible result should install and configure the `memcached` package, enable the service, and start the service.
   - Iterations: none; the only Memcached instance is explicitly named `memcached`.

3. **`redisio` dependency recipes**:
   - The wrapper includes the base Redis dependency through the `redisio` cookbook.
   - The supplied execution tree does not contain the dependency recipe implementation.
   - Redis package installation, generated configuration resources, and the exact service unit must not be inferred from the supplied tree.

4. **`redisio::enable`**:
   - Invoked by `cookbooks/cache/recipes/default.rb`.
   - The recipe file is missing from the supplied execution tree.
   - Represent its intended result as an explicit Redis service enable/start operation after the target distribution and service unit are confirmed.
   - Iterations: none.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- `memcached`
- Redis package name: unresolved from the supplied execution tree and must be selected for the target distribution

**Service dependencies**:

- Memcached service, managed by `memcached_instance[memcached]`
- Redis service, intended to be enabled through `redisio::enable`; exact service unit unresolved

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal source value**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded directly in the Chef recipe
- **Usage context**: Redis authentication for the server listening on port `6379`

The Ansible migration must not commit this password directly in a role or playbook. Store it in Ansible Vault or an approved AAP credential/secret mechanism, then render or apply it with appropriate file permissions.

No data bag, Chef Vault, Conjur, CyberArk, environment-variable secret reference, TLS certificate, private key, database connection string, or additional credential was detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/run/redis`
- `/var/run/memcached` if created by the external Memcached implementation
- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `:6379`
- Unix sockets: none configured

**Templates rendered**:

- None; render count `0`

**Configuration transformations**:

- `/etc/redis/6379.conf` is modified in place when it exists.
- Five named directive families are removed.
- No configuration template is rendered.

## Pre-flight checks:

```bash
# Verify the Memcached package
rpm -q memcached 2>/dev/null || dpkg-query -W memcached

# Verify the Memcached service
systemctl status memcached
systemctl is-enabled memcached
pgrep -a memcached

# Verify Memcached TCP and UDP listeners
ss -ltnp | grep '0.0.0.0:11211'
ss -lunp | grep ':11211'

# Confirm Memcached process arguments
ps -ef | grep '[m]emcached'

# Test Memcached statistics
printf "stats\r\nquit\r\n" | nc 127.0.0.1 11211

# Test a Memcached write and read
printf "set migration_check 0 60 5\r\nhello\r\nget migration_check\r\nquit\r\n" \
  | nc 127.0.0.1 11211

# Verify the Redis configuration exists
test -f /etc/redis/6379.conf && echo "Redis configuration exists"

# Confirm Redis port configuration
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' /etc/redis/6379.conf

# Confirm the Redis PID or runtime directory configuration
grep -E '^[[:space:]]*pidfile|^[[:space:]]*dir' /etc/redis/6379.conf

# Confirm removed Redis directives are absent
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || true

# Replace <redis-service-name> with the service unit resolved for the target OS
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
pgrep -a redis

# Verify Redis TCP listener
ss -ltnp | grep ':6379'

# Test Redis authentication without exposing the password
REDISCLI_AUTH='FROM-ANSIBLE-VAULT-OR-AAP-SECRET' redis-cli -p 6379 PING
redis-cli -p 6379 PING

# Verify Redis directories
stat -c '%A %U:%G %n' /var/log/redis
stat -c '%A %U:%G %n' /run/redis

# Inspect recent Redis service logs
journalctl -u <redis-service-name> --no-pager -n 50

# Final service and endpoint summary
systemctl --no-pager --type=service --state=running | grep -E 'memcached|redis'
ss -ltnp | grep -E ':(6379|11211)\b'
ss -lunp | grep ':11211'
```

Expected results:

- `memcached` is installed, active, and enabled.
- Memcached listens on TCP port `11211` and UDP port `11211` when UDP remains enabled by the target service configuration.
- Memcached uses 64 MB memory and a maximum of 1024 connections.
- The Memcached statistics request returns `STAT` lines.
- The Memcached write returns `STORED`, and the read returns `VALUE migration_check`.
- Redis is active and enabled under the confirmed target service unit.
- Redis listens on TCP port `6379`.
- An authenticated Redis `PING` returns `PONG`.
- An unauthenticated Redis request returns an authentication error.
- `/var/log/redis` exists with owner `redis:redis` and mode `0755`.
- `/run/redis` exists as the configured PID directory.
- The five removed Redis directive families are absent as active configuration lines.
- Redis logs show successful startup without configuration errors.