---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the explicitly named Memcached instance `memcached` on TCP and UDP port `11211`, and a Redis server on port `6379`. The Memcached resource specifies 64 MB of memory, 1024 maximum connections, a `1m` maximum object size, `0.0.0.0` listeners, and a `service_user` account. Source-level details in the supplied plan report Redis authentication, `/run/redis`, `/var/log/redis`, `/etc/redis/6379.conf`, and removal of five replication-related directives; these details are not independently represented in the supplied structured execution summary. The `redisio` and `redisio::enable` recipes are referenced but unavailable, so the Ansible implementation must provide the equivalent Redis installation, configuration, and service-management tasks.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service managed by `memcached_instance[memcached]`
  - Location/Path: Package-specific Memcached configuration; exact path is not exposed
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1024 maximum connections, `1m` maximum object size, `service_user` user, ulimit `1024`, empty experimental and extra CLI option lists, start and enable actions
  - Threads: `node['memcached']['threads']`; no default value was supplied in the analyzed attribute file

- **redis**: Redis server configuration referenced through `redisio`
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP port `6379`
  - Key Config: Password authentication, Redis log directory owned by `redis:redis` with mode `0755`, and removal of five replication-related directives from `/etc/redis/6379.conf`
  - Service: Intended to be enabled and started by `redisio::enable`; the recipe is unavailable

The supplied execution flow contains no `.each` loops or collection iterations.

## File Structure

The following is the complete directory listing supplied for the analyzed execution flow.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

No provider file path was supplied for `memcached_instance[memcached]`. The Ansible implementation must reproduce the observable behavior of the custom resource rather than assume an unavailable Chef provider.

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

The execution tree references `redisio`, `redisio::enable`, and the Memcached custom resource provider, but their corresponding files are not present in the supplied directory listing.

## Module Explanation

The cookbook performs operations in the following order. Redis settings, attribute values, and cleanup directives identified below are source-level details reported in the supplied plan; they are not independently confirmed by the structured execution summary.

1. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates one `memcached_instance[memcached]` custom resource.
   - Configures memory as `64` MB.
   - Configures TCP and UDP ports as `11211`.
   - Listens on `0.0.0.0`.
   - Sets `maxconn` to `1024`.
   - Uses `service_user`.
   - Sets maximum object size to `1m`.
   - Reads threads from `node['memcached']['threads']`; no default value is supplied in the analyzed attribute file.
   - Sets `ulimit` to `1024`.
   - Uses empty `experimental_options` and `extra_cli_options` lists.
   - Starts and enables the Memcached service.
   - Ansible must install the platform-appropriate Memcached package, configure the package-specific service, and restart or reload it only when configuration changes.
   - The exact Memcached configuration path and package name are not exposed and must be selected for the target distribution.

2. **`redisio`** (`cookbooks/cache/recipes/default.rb` includes `redisio`; referenced recipe unavailable):
   - The execution tree reports `redisio` as missing.
   - Source-level details reported in the supplied plan define one Redis server on port `6379`.
   - Source-level details report a Redis password, `/run/redis` as the base PID directory, and `replicaservestaledata` set to `nil`.
   - Ansible must install the platform-appropriate Redis package and create the Redis service account and group as required by the target distribution.
   - Ansible must configure Redis on port `6379`, store the password in Ansible Vault or another approved secret-management system, use `/run/redis` for PID storage where supported, and manage `/etc/redis/6379.conf`.
   - The exact Redis package name, service unit name, and configuration mechanism are not available in the supplied execution tree and must not be invented.

3. **Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Sets owner `redis`.
   - Sets group `redis`.
   - Sets mode `0755`.
   - Applies recursive directory handling.
   - Ansible must ensure the Redis account and group exist before applying ownership.

4. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Targets `/etc/redis/6379.conf`.
   - The supplied plan reports that the block checks whether the file exists, reads it, removes matching complete lines, and writes the result back.
   - The reported directives are:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - These directive details are source-level claims and are not present in the supplied structured execution summary.
   - Ansible should use guarded `lineinfile` removal tasks or an equivalent file-editing task, preserving the no-op behavior when the file is absent.
   - Configuration changes should notify a Redis restart or reload handler according to the target package requirements.

5. **`redisio::enable`** (`cookbooks/cache/recipes/default.rb` includes `redisio::enable`; referenced recipe unavailable):
   - The execution tree reports `redisio::enable` as missing.
   - Its intended purpose is to enable Redis at boot.
   - Ansible must enable and start the actual Redis service unit installed by the target distribution.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- A platform-appropriate Memcached package; the exact package name is not exposed in the supplied files.
- A platform-appropriate Redis package; the exact package name is not exposed in the supplied files.
- Package-provided or explicitly managed service accounts and units for Memcached and Redis.

No package names can be verified from the supplied execution tree. Do not substitute unverified package names.

**Service dependencies**:

- Memcached must be enabled and started for `memcached_instance[memcached]`.
- Redis must be enabled and started as the equivalent of the unavailable `redisio::enable` recipe.
- Redis account and group setup must precede ownership of `/var/log/redis`.

## Credentials

**Detection Summary**: The supplied plan reports 1 credential in 1 file; the structured validation summary does not independently include the credential-detection result.

**Source**:
  - **Provider**: Hardcoded in Chef recipe, as reported by the supplied plan
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Value reported in source**: `redis_secure_password_123`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef attribute value
- **Usage context**: Redis client authentication for the Redis server on port `6379`
- **Ansible migration**: Store the password in Ansible Vault, an AAP credential, or another approved secret-management integration. Do not commit the literal password to the Ansible role or inventory.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur calls, environment-variable secrets, TLS certificate references, database connection strings, or API tokens were identified in the supplied plan.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- Redis PID location under `/run/redis`
- The Memcached configuration file selected by the target distribution package
- Any Memcached service unit or init configuration created by the package

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the bind address configured by the target distribution
- Unix sockets: none specified

**Templates rendered**:

- Chef templates rendered: `0`
- Ansible templates required: implementation-dependent; no source template was supplied

**Configuration cleanup operations**:

- Remove reported `replica-serve-stale-data` lines from `/etc/redis/6379.conf`.
- Remove reported `replica-read-only` lines from `/etc/redis/6379.conf`.
- Remove reported `repl-ping-replica-period` lines from `/etc/redis/6379.conf`.
- Remove reported `client-output-buffer-limit` lines from `/etc/redis/6379.conf`.
- Remove reported `replica-priority` lines from `/etc/redis/6379.conf`.

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
```

Expected result: Memcached is enabled and active.

```bash
printf "version\r\n" | nc -w 2 127.0.0.1 11211
```

Expected result: a response beginning with `VERSION`.

```bash
ss -lunp | grep ':11211'
ss -ltnp | grep ':11211'
```

Expected result: Memcached has UDP and TCP listeners on port `11211`.

```bash
ps aux | grep '[m]emcached'
systemctl show memcached | grep -E 'User=|LimitNOFILE='
```

Verify that:

- The process runs as the intended service account.
- The connection limit is `1024` or is reflected in the package-specific service configuration.
- Memory allocation is `64 MB`.
- The listener address is `0.0.0.0`.
- Maximum object size is `1m`.
- The configured ulimit is `1024`, where exposed by the service manager.

### Redis instance `redis`

Use the actual service unit installed by the target distribution:

```bash
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
```

Expected result: Redis is enabled and active.

```bash
ss -ltnp | grep ':6379'
```

Expected result: Redis is listening on port `6379`.

Unauthenticated access should be rejected:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication error or equivalent refusal.

Authenticated access should succeed using the migrated secret:

```bash
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_ANSIBLE_VAULT>' PING
```

Expected result:

```text
PONG
```

Avoid placing the real password directly in shell history during operational testing.

```bash
grep -E '^(port|requirepass|pidfile)' /etc/redis/6379.conf
```

Verify that:

- `port` is `6379`.
- Authentication uses the migrated secret.
- The PID configuration points under `/run/redis`, where supported by the installed Redis package.

Check the reported cleanup directives:

```bash
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result: no matching lines, if these source-level cleanup requirements are confirmed for the deployed configuration.

```bash
ls -ld /var/log/redis
ls -ld /run/redis
```

Verify that:

- `/var/log/redis` exists with mode `0755`.
- `/var/log/redis` is owned by `redis:redis`.
- `/run/redis` exists and is usable by the Redis service.

```bash
journalctl -u redis --no-pager -n 100
```

If the distribution writes Redis logs to a file instead of journald, inspect the exact log file configured by the installed package.

### Combined service verification

```bash
ps aux | grep '[r]edis-server'
ps aux | grep '[m]emcached'
systemctl --type=service --state=running | grep -E 'memcached|redis'
```

Expected result: both named cache instances are running, Memcached is reachable on TCP and UDP port `11211`, and Redis is reachable on port `6379` only after authentication.