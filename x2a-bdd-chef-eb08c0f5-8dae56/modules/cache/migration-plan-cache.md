---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance identified as `6379`. Memcached listens on TCP and UDP port `11211` at `0.0.0.0`, uses 64 MB of memory, permits 1024 connections, and is started and enabled. Redis listens on port `6379`, uses `/run/redis` for its PID directory, stores logs under `/var/log/redis`, and requires authentication. The Redis password is hardcoded in the Chef recipe and must be migrated to Ansible Vault or another protected secret store. The `redisio` recipes and the `memcached_instance` provider are unavailable from the supplied execution tree, so their package, service, account, configuration, and runtime details require target-system verification.

## Service Type and Instances

**Service Type**: Cache

The cookbook manages Memcached and Redis cache services.

**Configured Instances**:

- **memcached**: Memcached cache service
  - Package: `memcached`
  - Location/Path: `/var/log/memcached`; runtime path requires provider verification
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1024 maximum connections, maximum object size `1m`, ulimit `1024`, empty experimental and extra CLI option lists
  - Threads: `node['memcached']['threads']`; no value was supplied in the analyzed attributes
  - Service account: `service_user`; concrete username and group require provider verification
  - Startup: Started and enabled through `memcached_instance[memcached]` with actions `[:start, :enable]`

- **6379**: Redis cache service
  - Package: Not determinable because the `redisio` recipe is unavailable
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: Authentication enabled with `requirepass`; log directory owned by `redis:redis` with mode `0755`
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` when present
  - Service account dependency: The Redis setup is expected to create the `redis` account before `/var/log/redis` is created
  - Startup: Intended to be started and enabled through `redisio` and `redisio::enable`; exact service unit requires verification

There are no collection iterations in the supplied execution tree. The Redis server collection contains one configured item: port `6379`.

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

The execution tree identifies `memcached_instance[memcached]` as a custom resource, but does not provide a provider path. The installed Memcached cookbook dependency must be inspected during implementation.

**Templates:**
```text
```

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

The following files were present in the directory listing but are not executed directly by the supplied execution tree:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
selinux dependency: three recipe files, with names not supplied
```

No templates or static files were identified. The supplied analysis reports seven total analyzed files, but does not enumerate all seven files or provide complete contents for the provider and missing Redis dependency.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Sets `node['redisio']['servers']` to one Redis server identified by port `6379`.
   - Sets the Redis password using a hardcoded `requirepass` value.
   - Sets `replicaservestaledata` to `nil`.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio::default`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes `redisio::enable`.
   - Resource counts in the supplied recipe analysis: one directory, one Ruby block, three recipe inclusions, and two Redis-related attribute assignments.
   - The `redisio` and `redisio::enable` recipe files are unavailable, so their package, service, configuration-template, and data-directory resources require verification.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates one custom resource: `memcached_instance[memcached]`.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, and action `[:start, :enable]`.
   - Passes `service_user` as the service user.
   - Passes `node['memcached']['threads']`; no default value was supplied in the analyzed attributes.
   - Passes empty `experimental_options` and `extra_cli_options` lists.
   - The provider path and provider implementation are unavailable. Service account, service group, unit name, configuration path, log path, and runtime path must be verified before implementation.
   - Install the `memcached` package, render equivalent service configuration, and start and enable the service.

3. **`redisio::default`** (referenced dependency recipe; unavailable):
   - Is included after the Redis port, authentication, and PID directory settings are assigned.
   - Expected to install and configure Redis and create the required Redis service account.
   - The exact Redis package, service unit, configuration template, data directory, and service arguments cannot be determined from the supplied execution tree.

4. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Checks whether `/etc/redis/6379.conf` exists.
   - Reads the file when present.
   - Removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified file back.
   - Performs no action when the configuration file does not exist.
   - Ansible should use carefully tested `lineinfile` or `replace` tasks and notify the Redis service when configuration changes.

5. **`redisio::enable`** (referenced dependency recipe; unavailable):
   - Must enable the Redis instance on boot.
   - Must start the Redis instance if it is not running.
   - Must preserve the requested ordering after Redis configuration cleanup.
   - The exact service name must be discovered on the target platform.

## Dependencies

**External cookbook dependencies**:

- `memcached`, used through `memcached::default`
- `redisio`, referenced through `redisio::default` and `redisio::enable`
- The `redisio` recipe content was not supplied.
- The provider implementation for `memcached_instance` was not supplied.

**System package dependencies**:

- `memcached`
- Redis package: not identified because the `redisio` implementation is unavailable

**Service dependencies**:

- Memcached service, started and enabled by `memcached_instance[memcached]`
- Redis service on port `6379`, intended to be installed, started, and enabled through `redisio` and `redisio::enable`; exact unit name requires verification

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Value in Chef source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for instance `6379`

The password must not be copied into Ansible task files or committed in plaintext. Store it in Ansible Vault or an AAP credential/secret-management integration and pass it to the Redis configuration template as a protected variable.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificate references, database credentials, or API tokens were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- Installed `memcached_instance` provider implementation
- Installed `redisio` recipe implementation
- Installed `redisio::enable` recipe implementation
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `6379`: TCP port `6379`
- Redis instance `6379`: no Unix socket specified

**Templates rendered**:

- Chef templates: none supplied or identified
- Memcached templates: unavailable; provider implementation may render or generate configuration
- Redis templates: unavailable; `redisio` implementation may render or generate configuration
- Confirm actual Ansible template render counts after the missing dependencies are inspected

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
```

Expected results:

- The service is enabled.
- The service is active and running.

```bash
nc -vz 127.0.0.1 11211
printf "version\r\n" | nc 127.0.0.1 11211
ss -tlpn | grep ':11211'
ss -ulpn | grep ':11211'
```

Expected results:

- TCP port `11211` accepts connections.
- The protocol response includes `VERSION <version>`.
- Memcached listens on TCP and UDP port `11211`.

```bash
ps aux | grep '[m]emcached'
ls -ld /var/log/memcached
```

Verify process arguments include:

- Listen address `0.0.0.0`
- TCP port `11211`
- UDP port `11211`
- Memory `64` MB
- Maximum connections `1024`
- Maximum object size `1m`
- Ulimit `1024`

Verify the service account, service group, unit file, configuration path, `/var/log/memcached`, and `/var/run/memcached` against the installed provider.

### Redis instance `6379`

Use the service name discovered from the target host. If it is `redis-server`, run:

```bash
systemctl status redis-server
systemctl is-enabled redis-server
systemctl is-active redis-server
```

If the deployment uses a port-specific unit, run the equivalent commands for the unit associated with port `6379`.

```bash
ss -tlpn | grep ':6379'
test -f /etc/redis/6379.conf
ls -ld /var/log/redis
ls -ld /run/redis
```

Expected results:

- Redis listens on TCP port `6379`.
- `/etc/redis/6379.conf` exists.
- `/var/log/redis` exists with mode `0755` and ownership `redis:redis`.
- `/run/redis` exists and is used as the Redis PID directory.

Use a protected environment variable for authentication:

```bash
export REDISCLI_AUTH='<retrieve-from-secure-secret-store>'
redis-cli -p 6379 PING
```

Expected result:

```text
PONG
```

Verify the port and authentication state without exposing the password:

```bash
redis-cli -p 6379 CONFIG GET port
redis-cli -p 6379 CONFIG GET requirepass
```

Inspect the relevant configuration settings:

```bash
grep -E '^(port|requirepass|pidfile|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

After migration, the following directives should be absent unless the target Redis version requires an explicitly retained equivalent:

```text
replica-serve-stale-data
replica-read-only
repl-ping-replica-period
client-output-buffer-limit
replica-priority
```

Check Redis logs using the verified service and log configuration:

```bash
journalctl -u redis-server --no-pager -n 50
grep -E '^(logfile|dir|pidfile)' /etc/redis/6379.conf
```

After a configuration change, verify restart behavior and service availability:

```bash
systemctl show redis-server -p ActiveState -p SubState
redis-cli -p 6379 PING
```

Expected result:

```text
PONG
```

Confirm that Redis remains enabled after the configuration change.