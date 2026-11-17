---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook provides a cache layer with one Memcached instance named `memcached` and one Redis server configured on port `6379`. The Memcached resource is configured for TCP and UDP port `11211`, listener `0.0.0.0`, 64 MB memory, 1,024 maximum connections, and startup and enablement. Redis is intended to use password authentication, `/run/redis` for its PID directory, `/var/log/redis` for logs, and a cleanup step for replication-related directives in `/etc/redis/6379.conf`. The Redis configuration details and credential value are reported by the source plan but are not independently confirmed by the supplied execution-tree summary. The referenced `redisio` and `redisio::enable` recipes are missing and must be implemented directly in Ansible or supplied as dependencies.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached cache service
  - Location/Path: `/var/log/memcached`; runtime directory `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: 64 MB memory, 1,024 maximum connections, maximum object size `1m`, ulimit `1024`, start and enable actions, empty experimental and extra CLI option lists
  - Service account: `service_user` and `service_group` from the dependency cookbook context; exact names are not available in the supplied files
  - Threads: The recipe references `node['memcached']['threads']`, but this attribute is absent from the supplied defaults; define and document an explicit Ansible value

- **Redis server on port `6379`**: Redis cache service
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Password authentication, `requirepass` reported as `redis_secure_password_123`, and `replicaservestaledata` reported as `nil`
  - Service enablement: Intended through `redisio::enable`; the recipe is missing from the supplied execution tree
  - Configuration cleanup: Remove `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` directives from `/etc/redis/6379.conf`
  - Verification status: The supplied execution-tree summary confirms the Redis recipe inclusions, log directory resource, and cleanup block, but does not independently expose the Redis assignments, password, or cleanup implementation details

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

No provider file is included in the supplied execution tree. The `memcached_instance` custom resource is used, but its provider implementation is not available in the analyzed file set.

**Templates:**

```text
```

No templates are rendered by the supplied execution tree.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The supplied analysis references seven analyzed files but identifies only the three files listed above. The remaining four files are not named in the supplied inventory and must be identified before the migration inventory can be considered complete.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Assigns one Redis server configuration for port `6379`, including the reported `requirepass` and `replicaservestaledata` values.
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`, which is not present in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`; if the file exists, removes complete lines beginning with the five specified replication-related directives and writes the result back.
   - Includes `redisio::enable`, which is not present in the supplied execution tree.
   - The source summary does not verify a Chef `group['redis']` resource. Redis account and group creation is an Ansible implementation requirement inferred from service ownership, not a confirmed analyzed Chef resource.
   - Referenced resources: `include_recipe` for `memcached`, `redisio`, and `redisio::enable`; `directory[/var/log/redis]`; `ruby_block[fix_redis_config]`.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Starts and enables the `memcached` instance.
   - Passes memory `64`, TCP port `11211`, UDP port `11211`, listener `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental options, and empty extra CLI options.
   - Passes `node['memcached']['threads']`, which is not defined in the supplied attribute file.
   - Passes `service_user` as the service user; the resolved service user and group names are not available in the supplied files.
   - The custom resource provider and any provider-specific templates are not included in the supplied execution tree.

3. **default attributes** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`):
   - Defines Memcached defaults:
     - Version: `nil`
     - Memory: `64`
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - Maximum object size: `1m`
     - Experimental options: `[]`
     - Extra CLI options: `[]`
     - Ulimit: `1024`
     - Log path: `/var/log/memcached`
   - Does not define `node['memcached']['threads']`.
   - These attribute values are reported in the source plan but are not independently present in the supplied structured execution-tree summary.

## Dependencies

**External cookbook dependencies**: `memcached` is referenced and its dependency recipe is present in the supplied execution tree. `redisio` and `redisio::enable` are referenced but missing. No `metadata.rb` was supplied for `cookbooks/cache`, so declared dependency metadata cannot be independently verified.

**System package dependencies**: `memcached`; a Redis package is implied, but its exact package name and version are not present in the supplied execution tree and must be selected for the target platform.

**Service dependencies**: Memcached service for instance `memcached`, enabled and started by `memcached_instance[memcached]`; Redis service for port `6379`, intended to be enabled and started by `redisio::enable`.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef attribute assignment
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis server listening on port `6379`
- **Migration requirement**: Store the value in Ansible Vault or an approved AAP secret mechanism. Do not place the plaintext password in role files, generated templates, task output, or source control. Tasks using the password must use `no_log: true`.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, private keys, API tokens, or database connection strings were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

**Service endpoints to check**:

- Memcached instance `memcached` TCP: `0.0.0.0:11211`
- Memcached instance `memcached` UDP: `0.0.0.0:11211`
- Redis server on port `6379`: TCP `:6379`
- Redis Unix socket: none specified

**Templates rendered**: None in the supplied execution tree. The Ansible implementation must generate equivalent Memcached and Redis configuration using native tasks or explicitly created templates.

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps aux | grep '[m]emcached'
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211
ls -ld /var/log/memcached
ls -ld /var/run/memcached
systemctl show memcached | grep -E 'LimitNOFILE|User|Group'
```

Expected results:

- The `memcached` service is active and enabled.
- A Memcached process is running for instance `memcached`.
- TCP and UDP port `11211` are listening.
- The Memcached response contains a `VERSION ...` line.
- `/var/log/memcached` and `/var/run/memcached` exist with mode `0755`.
- The service uses the intended service account and the configured file descriptor behavior is consistent with ulimit `1024`.

### Redis server on port `6379`

Use the service unit that exists on the target distribution:

```bash
systemctl status redis
systemctl status redis-server
systemctl is-enabled redis
systemctl is-enabled redis-server
ps aux | grep '[r]edis-server'
ss -tlnp | grep ':6379'
```

Expected results:

- The Redis service for port `6379` is active and enabled.
- A Redis process is running with configuration for port `6379`.
- Redis listens on TCP port `6379`.

Verify authentication with the vaulted password:

```bash
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server
redis-cli -p 6379 PING
```

Expected results:

- Authenticated `PING` returns `PONG`.
- Authenticated `INFO server` returns Redis server information.
- Unauthenticated access returns an authentication-required error.

Verify the configuration and cleanup:

```bash
grep -E '^(port|requirepass|pidfile|dir|logfile)' /etc/redis/6379.conf
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result:

- Redis configuration contains the expected port, password configuration, PID, directory, and log settings.
- The second command produces no matching lines.

Verify directories and logs:

```bash
ls -ld /var/log/redis
ls -ld /run/redis
stat -c '%U %G %a %n' /var/log/redis
journalctl -u redis --no-pager -n 100
journalctl -u redis-server --no-pager -n 100
```

Expected results:

- `/var/log/redis` exists and is owned by `redis:redis` with mode `0755`.
- `/run/redis` exists or is created by the Redis service.
- Logs show successful startup on port `6379`, no permission errors, no authentication configuration errors, and no configuration parsing failures.

### Credential storage

```bash
ansible-vault view group_vars/cache/vault.yml
```

Confirm that:

- The Redis password is stored in Ansible Vault or an approved secret backend.
- The plaintext password is absent from the role, generated configuration templates, task output, and source control.
- Tasks using the password have `no_log: true`.