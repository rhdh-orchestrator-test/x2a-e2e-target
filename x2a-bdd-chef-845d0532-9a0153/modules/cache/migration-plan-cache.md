---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Memcached instance named `memcached` and one Redis instance named `6379`. Memcached is started and enabled through the `memcached_instance` custom resource with 64 MB memory, TCP/UDP port `11211`, listen address `0.0.0.0`, and a maximum of 1,024 connections. Redis is configured on port `6379` with the hardcoded password `redis_secure_password_123`, PID directory `/run/redis`, and log directory `/var/log/redis`; selected replication-related directives are removed from `/etc/redis/6379.conf` before Redis is enabled. The `redisio` dependency recipes and the Memcached provider implementation are unavailable from the supplied execution tree, so package names, service unit names, provider-specific paths, and exact dependency behavior must be verified separately.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached caching service
  - Location/Path: Provider-specific configuration path is unavailable
  - Port/Socket: TCP `11211`; UDP `11211`
  - Key Config: Listen address `0.0.0.0`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; user `service_user`; ULimit `1024`; empty experimental and extra CLI option lists; actions `start` and `enable`
  - Threads: Value comes from `node['memcached']['threads']`; no value is defined in the supplied attributes file
  - Version: `nil`; no explicit Memcached version is selected

- **6379**: Redis server
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP port `6379`; no Unix socket specified
  - Key Config: `requirepass` set to `redis_secure_password_123`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Log Directory: `/var/log/redis`, owner `redis`, group `redis`, mode `0755`, created recursively
  - Removed Directives: `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Service State: Enabled through `redisio::enable`
  - Dependency Status: Redis installation and enablement recipes are unavailable in the supplied execution tree

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

No provider file path was supplied. The `memcached_instance` provider implementation is unavailable from the supplied file list.

**Templates:**

```text
```

No templates are shown as rendered or referenced in the supplied analysis.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file` resources in the supplied execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Assigns one Redis server configuration for instance `6379`.
   - Sets the Redis base PID directory to `/run/redis`.
   - Includes the unavailable `redisio` installation/configuration recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Executes `ruby_block['fix_redis_config']` against `/etc/redis/6379.conf`.
   - Includes the unavailable `redisio::enable` recipe.
   - Redis configuration assignment:
     ```ruby
     node.default['redisio']['servers'] = [
       {
         'port' => '6379',
         'requirepass' => 'redis_secure_password_123',
         'replicaservestaledata' => nil,
       }
     ]
     ```
   - The `replicaservestaledata` value is unset or equivalent to the Chef `nil` value.
   - Resources identified in the supplied execution tree:
     - `directory['/var/log/redis']`
     - `ruby_block['fix_redis_config']`
   - No separate `group['redis']` resource is confirmed in the supplied execution tree. Whether the Redis dependency creates the `redis` group is unresolved.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates one custom resource: `memcached_instance['memcached']`.
   - Configures memory `64`, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, user `service_user`, ULimit `1024`, empty experimental options, and empty extra CLI options.
   - Uses the undefined attribute value for `threads`.
   - Starts and enables the `memcached` instance.
   - The provider implementation, package name, configuration path, and service unit name are unavailable and must be verified before implementation.
   - Iterations: one custom-resource instance, `memcached`.

3. **redisio** (`redisio/recipes/default.rb`, unavailable):
   - The execution tree reports `redisio Recipe file not found`.
   - The Redis package name, package version, service unit, configuration template, service user and group creation, configuration directory creation, and restart behavior are unresolved.
   - The wrapper-visible requirements are Redis port `6379`, password `redis_secure_password_123`, PID directory `/run/redis`, log directory `/var/log/redis`, and configuration file `/etc/redis/6379.conf`.

4. **redisio::enable** (`redisio/recipes/enable.rb`, unavailable):
   - The execution tree reports `redisio::enable Recipe file not found`.
   - The intended behavior is to enable the Redis service at boot.
   - The actual Redis systemd unit name must be verified on the target distribution.
   - Iterations: one Redis server configuration item, instance `6379`.

### Redis configuration cleanup

The `ruby_block['fix_redis_config']` operation:

1. Checks whether `/etc/redis/6379.conf` exists.
2. Reads the complete file.
3. Removes lines beginning with `replica-serve-stale-data`.
4. Removes lines beginning with `replica-read-only`.
5. Removes lines beginning with `repl-ping-replica-period`.
6. Removes lines beginning with `client-output-buffer-limit`.
7. Removes lines beginning with `replica-priority`.
8. Writes the modified content back to `/etc/redis/6379.conf`.

The Ansible implementation should use a scoped `replace` task or equivalent `lineinfile` tasks, conditional on the file existing, while preserving unrelated configuration. Restart behavior must be verified because no explicit Redis restart notification is shown in the supplied execution tree.

## Dependencies

**External cookbook dependencies**:

- `memcached`, constrained to `~> 6.0`
- `redisio`, unconstrained

**System package dependencies**:

- Memcached package: exact package name is not exposed by the supplied execution tree and must be verified for Ubuntu `>= 18.04` and CentOS `>= 7.0`.
- Redis package: exact package name is not exposed because the `redisio` recipe is unavailable and must be verified for Ubuntu `>= 18.04` and CentOS `>= 7.0`.

**Service dependencies**:

- Memcached service for instance `memcached`; exact unit name must be confirmed from the unavailable provider.
- Redis service for instance `6379`; exact unit name must be confirmed from the unavailable `redisio` recipes.

## Credentials

**Detection Summary**: 1 credential detected in 1 file based on the supplied recipe content.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef attribute assignment
- **Usage context**: Redis server authentication through the `requirepass` configuration directive
- **Migration storage**: Store as an Ansible Vault variable, such as `redis_password`, and render it without committing the plaintext value to the role or inventory.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, database connection strings, or other credentials were identified in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`
- Memcached configuration path, after the provider is identified
- Redis log file path, after the package and service configuration are identified

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `6379`: TCP `0.0.0.0:6379`
- Redis instance `6379`: no Unix socket specified

**Templates rendered**:

- None identified
- Render count: `0` confirmed templates; dependency templates unavailable for inspection

**Iterations and render counts**:

- Memcached custom resource: one instance, `memcached`
- Redis server configuration: one item, `6379`
- No recipe-level `.each` loop is shown.
- No rendered template is present in the supplied file structure.

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
```

Use the verified service unit name if it differs from `memcached`.

```bash
ss -tlnp | grep ':11211'
nc -vz 127.0.0.1 11211
```

Expected result: TCP port `11211` is listening.

```bash
ss -ulnp | grep ':11211'
```

Expected result: UDP port `11211` is listening.

Verify the effective Memcached configuration contains:

```text
memory: 64 MB
TCP port: 11211
UDP port: 11211
listen address: 0.0.0.0
maximum connections: 1024
maximum object size: 1m
ulimit: 1024
```

### Redis instance `6379`

```bash
systemctl status redis
systemctl status redis-server
systemctl is-enabled redis
systemctl is-enabled redis-server
```

Retain only the verified Redis service unit name after identifying it on the target host.

```bash
ss -tlnp | grep ':6379'
nc -vz 127.0.0.1 6379
```

Expected result: Redis is listening on TCP port `6379`.

```bash
export REDISCLI_AUTH='<retrieve-from-secure-secret-store>'
redis-cli -p 6379 PING
unset REDISCLI_AUTH
```

Expected result:

```text
PONG
```

Verify the Redis configuration:

```bash
grep -E '^(port|requirepass|dir|pidfile)' /etc/redis/6379.conf
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

The second command should return no matching lines after the configuration cleanup has executed, assuming those directives were originally present.

Verify PID and log directories:

```bash
ls -ld /run/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis
```

Expected log-directory result:

```text
redis:redis 755 /var/log/redis
```

Verify the Redis process and logs using the actual service unit:

```bash
ps aux | grep '[r]edis'
journalctl -u <verified-redis-service-unit> --no-pager -n 50
```

### Combined network verification

```bash
ss -tlnp | grep -E ':(6379|11211)\b'
ss -ulnp | grep ':11211'
```

Expected listeners:

- Redis instance `6379`: TCP `6379`
- Memcached instance `memcached`: TCP `11211`
- Memcached instance `memcached`: UDP `11211`

### Configuration-change behavior

After changing `/etc/redis/6379.conf`, verify that the Redis service is running with the updated configuration:

```bash
systemctl restart <verified-redis-service-unit>
export REDISCLI_AUTH='<retrieve-from-secure-secret-store>'
redis-cli -p 6379 CONFIG GET requirepass
redis-cli -p 6379 PING
unset REDISCLI_AUTH
```

Verify whether the Ansible configuration task must notify a Redis restart. The supplied Chef execution tree does not expose an explicit restart notification.