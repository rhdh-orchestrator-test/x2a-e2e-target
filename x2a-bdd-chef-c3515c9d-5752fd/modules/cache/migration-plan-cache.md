---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the explicitly named Memcached instance `memcached` on TCP/UDP port `11211`, and one Redis server on port `6379`. The Memcached instance is started and enabled through `memcached_instance[memcached]`. Redis is configured with a hardcoded password, `/run/redis` as its PID directory, `/var/log/redis` as its log directory, and cleanup of selected replication directives in `/etc/redis/6379.conf`. The `redisio` and `redisio::enable` recipe files are unavailable, so the Redis package, exact service name, templates, and installation details must be validated on the target platform.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: `/var/log/memcached`; `/var/run/memcached` if required by the target distribution
  - Port/Socket: TCP `11211`; UDP `11211`; listen address `0.0.0.0`
  - Key Config: Memory `64` MB; maximum connections `1024`; maximum object size `1m`; ulimit `1024`; empty experimental and extra CLI options; worker threads use `node['memcached']['threads']`, which is not defined in the supplied attributes
  - Package: `memcached`
  - Service account: `service_user`; exact resolved username is unavailable
  - State: Started and enabled

- **redis-6379**: Redis server configured by the `redisio` attributes
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Password `redis_secure_password_123`; log directory owner `redis`, group `redis`, mode `0755`; replication-related directives removed from the configuration
  - Removed directives: `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Package: Not determinable because the `redisio` recipe is unavailable
  - Service: Enabled by `redisio::enable`; exact service resource and service name are unavailable
  - State: Intended to be enabled; active state must be validated after migration

The Memcached configuration is one explicitly named custom-resource instance, `memcached`. The Redis server configuration is one item in the `cache::default` Redis server array, with port `6379`. No `.each` loops are present in the supplied recipes.

## File Structure

Only files shown in the supplied execution tree are listed below. The referenced Redis recipe files are unavailable and are not added as available files.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider path for `memcached_instance` was supplied.

**Templates:**
```text
```

No templates are rendered by the supplied recipes.

**Attributes:**
```text
```

No attribute file path was included in the supplied execution-tree file list. The Memcached and Redis values described in this plan are reported configuration values, but their attribute-file sources were not supplied for independent verification.

**Files:**
```text
```

No `cookbook_file` or `remote_file` resources are shown.

## Module Explanation

The cookbook performs operations in the following order.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached recipe with `include_recipe 'memcached'`.
   - Sets the Redis server configuration for port `6379`.
   - Sets the Redis password to `redis_secure_password_123`.
   - Sets the Redis PID directory to `/run/redis`.
   - Includes the Redis installation/configuration recipe with `include_recipe 'redisio'`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes the `ruby_block['fix_redis_config']` resource.
   - Includes the Redis enablement recipe with `include_recipe 'redisio::enable'`.
   - Resources shown:
     - `directory['/var/log/redis']`
     - `ruby_block['fix_redis_config']`
   - No explicit Chef `group['redis']` resource is shown. Redis ownership and group availability must be validated from the unavailable `redisio` implementation or created explicitly in Ansible if required.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes the single custom resource `memcached_instance['memcached']`.
   - Configures the `memcached` instance with:
     - Memory: `64` MB
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - Worker threads: `node['memcached']['threads']`, undefined in the supplied attributes
     - Ulimit: `1024`
     - Experimental options: empty list
     - Extra CLI options: empty list
     - User: `service_user`
   - Requests actions `:start` and `:enable`.
   - The custom-resource provider implementation was not supplied, so no provider path or provider-specific template name may be inferred.
   - The Ansible implementation should install the verified `memcached` package, configure the named instance, create required directories and service-account resources for the target distribution, and start and enable the Memcached service.

3. **`redisio` recipe** (`redisio/recipes/default.rb`, unavailable):
   - **Execution-tree status**: Recipe file not found.
   - Is intended to install and configure the Redis server on port `6379`.
   - Receives the Redis server configuration containing:
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Receives `base_piddir` set to `/run/redis`.
   - The Redis package name, service name, configuration templates, data directory, log file, and user/group creation cannot be determined from the supplied files.
   - The Ansible implementation must isolate these values as role variables and validate the package and service names for the target operating system.

4. **`redisio::enable`** (`redisio/recipes/enable.rb`, unavailable):
   - **Execution-tree status**: Recipe file not found.
   - Is included after Redis log-directory creation and configuration cleanup.
   - Its intended purpose is to enable the Redis service at boot.
   - The Ansible implementation should enable the resolved Redis service after configuration is installed and repaired.

### Redis configuration repair

The `ruby_block['fix_redis_config']` resource checks whether `/etc/redis/6379.conf` exists.

- If the file does not exist, no modification occurs.
- If the file exists, complete lines beginning with the following directives are removed:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

The Ansible equivalent should use an idempotent `replace` or `lineinfile` operation. A Redis restart or reload should occur only when required by the target service implementation and only when the configuration changes.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint shown

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `memcached`
- Redis package: not determinable because the `redisio` recipe is unavailable and must be validated for the target platform

**Service dependencies**:

- `memcached`: started and enabled by `memcached_instance['memcached']`
- Redis on port `6379`: enabled by the unavailable `redisio::enable` recipe

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute value
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the server listening on port `6379`

The Ansible migration must not retain this plaintext password in role defaults or an ordinary variables file. Store it in Ansible Vault or an AAP credential/secret integration and pass it to the Redis configuration template as a protected variable.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret, TLS certificate, private key, API token, or database connection string was detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

The Redis data directory and exact Redis log file are unavailable because the `redisio` recipe is missing.

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `redis-6379`: TCP port `6379`
- Redis Unix socket: none specified

**Templates rendered**:

- Chef templates: none shown; render count `0`
- Ansible templates: configuration templates will be required for Memcached and Redis, but exact names and contents must be designed and validated during migration

## Pre-flight checks

```bash
# Confirm the target operating system and available package metadata
cat /etc/os-release
command -v apt-cache >/dev/null && apt-cache policy memcached redis-server
command -v yum >/dev/null && yum info memcached redis
command -v dnf >/dev/null && dnf info memcached redis

# Confirm the Memcached package and service
command -v memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# Verify the named Memcached instance: memcached
ps aux | grep '[m]emcached'
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Verify a basic Memcached set/get operation
{
  printf "set migration_test 0 60 5\r\nhello\r\nget migration_test\r\nquit\r\n"
} | nc -w 2 127.0.0.1 11211

# Verify Memcached directories and effective limits
ls -ld /var/log/memcached
ls -ld /var/run/memcached
systemctl show memcached | grep -E 'LimitNOFILE|ExecStart'

# Verify the effective Memcached settings:
# memory 64 MB, TCP port 11211, UDP port 11211,
# listen address 0.0.0.0, max connections 1024,
# max object size 1m, and ulimit 1024.

# Discover the actual Redis package and service names
systemctl list-unit-files | grep -i redis
systemctl list-units --type=service | grep -i redis

# Replace redis below with the resolved service name
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Verify the Redis instance redis-6379
ss -tlnp | grep ':6379'

# Use the protected password from Ansible Vault or an AAP credential.
redis-cli -h 127.0.0.1 -p 6379 -a '<redis_password>' PING

# Confirm unauthenticated access is rejected
redis-cli -h 127.0.0.1 -p 6379 PING

# Verify Redis configuration
grep -E '^(port|requirepass|dir|pidfile|logfile)' /etc/redis/6379.conf
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify Redis directories and ownership
ls -ld /run/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis

# Verify Redis authenticated connectivity
redis-cli -h 127.0.0.1 -p 6379 -a '<redis_password>' SET migration_test success
redis-cli -h 127.0.0.1 -p 6379 -a '<redis_password>' GET migration_test

# Review service logs; replace redis with the resolved Redis service name
journalctl -u memcached --no-pager -n 50
journalctl -u redis --no-pager -n 50

# Verify Redis log files without assuming a specific filename
find /var/log/redis -maxdepth 1 -type f -print
```

Expected results:

- The `memcached` instance is active and enabled.
- Memcached listens on TCP and UDP port `11211`, bound to `0.0.0.0`.
- Memcached responds to the version and set/get tests.
- The effective Memcached configuration contains memory `64` MB, maximum connections `1024`, maximum object size `1m`, and ulimit `1024`.
- The Redis service corresponding to instance `redis-6379` is active and enabled.
- Redis listens on TCP port `6379`.
- Authenticated Redis `PING` returns `PONG`.
- Unauthenticated Redis access is rejected.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- `/run/redis` exists and is used as the PID directory, or the target platform-specific equivalent is explicitly validated.
- No active configuration lines remain for the five removed replication-related directives.
