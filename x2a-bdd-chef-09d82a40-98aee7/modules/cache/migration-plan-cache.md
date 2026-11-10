---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook manages two cache instances: the exact Memcached instance `memcached` and one Redis server instance on port `6379`. The plan confirms the Memcached custom-resource invocation and Redis-related execution order, while Memcached defaults, Redis authentication details, and provider behavior require verification against the source files because the supplied structured analysis does not confirm them. Redis configuration cleanup targets `/etc/redis/6379.conf`, and no templates or static files are rendered or deployed.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service managed by `memcached_instance[memcached]`
  - Location/Path: `/var/log/memcached`; runtime path `/var/run/memcached`
  - Port/Socket: TCP `11211`; UDP `11211`
  - Key Config: The recipe passes memory `64`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental and extra CLI option arrays, and an unresolved `threads` attribute. These values require confirmation from the attributes file and custom-resource provider. The custom resource requests `:start` and `:enable`.

- **Redis server on port 6379**: Single Redis server instance
  - Location/Path: Configuration `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket configured or detected
  - Key Config: The source plan reports `requirepass` set to `redis_secure_password_123`, but the supplied structured analysis does not independently confirm the value. The log directory is owned by `redis:redis` with mode `0755`. Five replication-related directives are removed from the Redis configuration when present.

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

The `memcached_instance` custom resource is used, but its provider file was not included in the supplied execution tree or available file list. No provider path is assumed.

**Templates:**
```text
```

No templates are rendered.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The structured analysis reports seven analyzed files but supplies paths for only the two recipes and one attributes file listed above. The remaining four analyzed files must be identified before migration completeness can be confirmed.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency through `include_recipe 'memcached'`.
   - Sets the Redis server configuration to one entry on port `6379`.
   - Sets the Redis base PID directory to `/run/redis`.
   - The source plan reports a Redis password of `redis_secure_password_123`; this value requires confirmation from the recipe analysis and must be migrated through Ansible Vault or an AAP secret integration.
   - Sets `replicaservestaledata` to `nil`.
   - Includes the unavailable `redisio` recipe after the Memcached dependency.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Defines `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, removes active lines for:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The migration should implement the configuration cleanup idempotently with `ansible.builtin.lineinfile` or an equivalent module and must not fail solely because `/etc/redis/6379.conf` is absent.
   - Includes the unavailable `redisio::enable` recipe last so Redis is enabled and started after configuration and cleanup.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes exactly one custom resource: `memcached_instance[memcached]`.
   - Passes the following properties:
     - `memory`: `node['memcached']['memory']`, reported as `64`
     - `port`: `node['memcached']['port']`, reported as `11211`
     - `udp_port`: `node['memcached']['udp_port']`, reported as `11211`
     - `listen`: `node['memcached']['listen']`, reported as `0.0.0.0`
     - `maxconn`: `node['memcached']['maxconn']`, reported as `1024`
     - `user`: dependency cookbook `service_user`
     - `max_object_size`: `node['memcached']['max_object_size']`, reported as `1m`
     - `threads`: `node['memcached']['threads']`; no default is confirmed in the supplied attributes analysis
     - `experimental_options`: `node['memcached']['experimental_options']`, reported as `[]`
     - `extra_cli_options`: `node['memcached']['extra_cli_options']`, reported as `[]`
     - `ulimit`: `node['memcached']['ulimit']`, reported as `1024`
     - `action`: `[:start, :enable]`
   - The supplied analysis confirms the custom-resource invocation but does not include the provider implementation.
   - Package installation, service-account and group creation, command-line configuration, service management, and exact provider behavior require verification against the missing provider and dependency source before implementation.
   - No `.each` loops are present. The only Memcached iteration item is the explicitly named instance `memcached`.

The Redis `redisio` and `redisio::enable` recipe files were not found in the supplied execution tree. Their package names, service unit name, and provider behavior must be verified on the target platform.

## Dependencies

**External cookbook dependencies**: `memcached`, `redisio`, `redisio::enable`

**System package dependencies**:
- `memcached` is the only explicitly identified package name; installation behavior requires confirmation from the dependency/provider source.
- The Redis package name is not confirmed because the `redisio` recipe is unavailable.

**Service dependencies**:
- Memcached service associated with `memcached_instance[memcached]`; exact service-management behavior requires provider verification.
- Redis service managed by `redisio::enable`; exact service unit name requires verification because the recipe is unavailable.

## Credentials

**Detection Summary**: 1 credential reported in 1 file; the supplied structured analysis does not independently confirm the finding.

**Source**:
  - **Provider**: Hardcoded, according to the source plan
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: Redis `requirepass` value; the source plan does not assign it to a named variable
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as hardcoded in the recipe
- **Usage context**: Redis authentication for the server on port `6379`
- **Reported source value**: `redis_secure_password_123`

The password must be independently confirmed from `cookbooks/cache/recipes/default.rb` before migration. It must not be committed to plaintext Ansible variables; store it in Ansible Vault or an AAP credential/secret integration and render it with restrictive permissions.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk/Conjur integrations, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings were confirmed.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`
- `/run/redis`

The structured analysis reports four additional analyzed files whose paths are not supplied. Identify and include those files before final migration sign-off.

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the configured Redis listen address
- Redis Unix socket: none configured or detected

**Templates rendered**:
- None; render count `0`

**Configuration edits performed**:
- `/etc/redis/6379.conf` is conditionally edited to remove five specified directives.

## Pre-flight checks

### Memcached instance: `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ps auxww | grep '[m]emcached'
```

Expected result: the Memcached service is enabled and active.

Verify the reported configuration values where the platform exposes them:

```bash
ps auxww | grep '[m]emcached'
```

Check for:
- Memory: `64` MB
- TCP port: `11211`
- UDP port: `11211`
- Listen address: `0.0.0.0`
- Maximum connections: `1024`
- Maximum object size: `1m`
- Ulimit: `1024`

The exact command-line representation depends on the target distribution and the unavailable custom-resource provider.

Test TCP connectivity:

```bash
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211
```

Expected result: a response beginning with `VERSION`.

Test UDP connectivity:

```bash
printf "version\r\n" | nc -u -w 2 127.0.0.1 11211
```

Expected result: a UDP Memcached version response. If the target `nc` implementation does not display UDP responses reliably, verify the listener with `ss` and a Memcached-aware client.

Verify both listeners:

```bash
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
```

Expected result:
- TCP listener on port `11211`
- UDP listener on port `11211`

### Redis instance: server on port `6379`

Determine the platform-specific Redis service unit:

```bash
systemctl status redis
systemctl status redis-server
systemctl is-enabled redis || systemctl is-enabled redis-server
systemctl is-active redis || systemctl is-active redis-server
ps aux | grep '[r]edis-server'
```

Expected result: one Redis service unit is active and enabled.

Verify the Redis configuration and port:

```bash
test -d /run/redis
ls -ld /run/redis
ss -tlnp | grep ':6379'
```

Expected result: `/run/redis` exists and Redis listens on TCP port `6379`.

If the password finding is confirmed and securely supplied by the migration:

```bash
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
```

Expected result:

```text
PONG
```

Verify unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication error such as:

```text
NOAUTH Authentication required.
```

Verify the Redis log directory:

```bash
test -d /var/log/redis
ls -ld /var/log/redis
stat -c '%U:%G %a %n' /var/log/redis
```

Expected result:

```text
redis:redis 755 /var/log/redis
```

Verify configuration cleanup:

```bash
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result: no matching active configuration lines are returned.

Validate the Redis configuration using the target platform’s service validation or restart procedure:

```bash
systemctl restart redis || systemctl restart redis-server
systemctl is-active redis || systemctl is-active redis-server
```

Review service logs:

```bash
journalctl -u redis --no-pager -n 50
journalctl -u redis-server --no-pager -n 50
```

Use the unit present on the target system and verify there are no startup, authentication, configuration, or permission errors.

### Combined endpoint verification

```bash
ss -tlnp | grep -E ':(6379|11211)\b'
ss -ulnp | grep ':11211'
```

Expected result:
- Redis TCP listener: `6379`
- Memcached TCP listener: `11211`
- Memcached UDP listener: `11211`