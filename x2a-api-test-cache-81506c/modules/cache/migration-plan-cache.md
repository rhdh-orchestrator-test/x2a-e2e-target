---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the Memcached instance `memcached` and one Redis server on port `6379`. Memcached uses the `memcached_instance` custom resource with 64 MB of memory, TCP/UDP port `11211`, a `0.0.0.0` listener, and start/enable actions. Redis is configured with PID directory base `/run/redis`, log directory `/var/log/redis`, and five replication-related directives removed from `/etc/redis/6379.conf`. The Redis password is hardcoded in the Chef recipe and must be migrated to Ansible Vault or another protected secret mechanism. The `redisio` and `redisio::enable` recipes are unavailable in the supplied execution tree, so the Redis package, service name, user/group behavior, and configuration generation must be verified before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: `/var/log/memcached`, `/var/run/memcached`
  - Port/Socket: TCP `0.0.0.0:11211`; UDP `0.0.0.0:11211`
  - Key Config: Package `memcached`; 64 MB memory; maximum 1024 connections; maximum object size `1m`; `ulimit` 1024; experimental and additional CLI options are empty; service is started and enabled through `memcached_instance[memcached]`
  - Version: No explicit version; `node['memcached']['version']` is `nil`
  - Threads: `node['memcached']['threads']`, unresolved because it is not defined in the supplied default attributes
  - Service user/group: Supplied through the unresolved `service_user` and `service_group` helper properties
  - Log directory: `/var/log/memcached`
  - Runtime directory: `/var/run/memcached`

- **redis-6379**: Redis server configured on TCP port `6379`
  - Location/Path: `/etc/redis/6379.conf`, `/run/redis`, `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Key Config: Password currently set to `redis_secure_password_123`; PID directory base `/run/redis`; log directory owned by `redis:redis` with mode `0755`; five replication-related directives removed from the configuration when present
  - Configured collection item: One Redis server entry with port `6379`, `requirepass` set to the detected password, and `replicaservestaledata` set to `nil`
  - Service enablement: Requested through `redisio::enable`, but the recipe and exact service name are unavailable
  - Package: Cannot be determined from the supplied `redisio` files because the dependency recipe is missing

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only files supplied in the execution tree or explicitly used by the analyzed recipes are listed below. No templates or static files were found.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

The `memcached_instance` custom resource is used, but its provider path is not present in the supplied execution tree. Do not invent a provider path; inspect the Memcached cookbook artifact separately if provider-level behavior is required.

**Templates:**
```text
```

No `.erb` templates are rendered by the supplied recipes.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The analysis references an `_package.rb` file within the Memcached artifact, but its complete path and contents are not present in the supplied directory listing. Package, user, group, and filesystem claims attributed to that file must be verified before migration.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`, resolving to `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - The included Memcached recipe invokes the single `memcached_instance[memcached]` resource.
   - Assigns one Redis server configuration entry:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node['redisio']['base_piddir']` to `/run/redis`.
   - Includes the unavailable `redisio` recipe. The supplied execution tree does not establish the Redis package name, package version, service unit, user/group creation, configuration template, or startup behavior.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Removes active lines beginning with the following directives from `/etc/redis/6379.conf`, when the file exists:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Does not explicitly restart or reload Redis after modifying `/etc/redis/6379.conf`.
   - Includes the unavailable `redisio::enable` recipe to request Redis enablement at boot. The exact service name must be discovered from the target environment.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes exactly one custom resource: `memcached_instance[memcached]`.
   - Passes the following values:
     - `memory`: `64`
     - `port`: `11211`
     - `udp_port`: `11211`
     - `listen`: `0.0.0.0`
     - `maxconn`: `1024`
     - `max_object_size`: `1m`
     - `experimental_options`: `[]`
     - `extra_cli_options`: `[]`
     - `ulimit`: `1024`
     - `threads`: unresolved in the supplied attributes
     - `user`: `service_user`, with literal value unresolved
   - Requests actions `start` and `enable`.
   - The custom resource provider is not present in the supplied execution tree.

3. **Memcached custom-resource package and filesystem operations** (provider implementation not supplied):
   - The referenced Memcached artifact reportedly contains a `package[memcached]` resource with version `node['memcached']['version']`; the resolved default version is `nil`.
   - The referenced implementation reportedly creates a system group using `service_group`, unless the service user already exists.
   - The referenced implementation reportedly creates and locks a system user using `service_user`, with home `/nonexistent`, shell `/bin/false`, comment `Memcached`, and group `service_group`.
   - Creates `/var/log/memcached` with mode `0755`, owned by the Memcached service user and group.
   - Creates `/var/run/memcached` with mode `0755`, owned by the Memcached service user and group.
   - These nested operations must be verified against the actual custom-resource provider before being treated as confirmed migration requirements.

## Dependencies

**External cookbook dependencies**: `memcached`, `redisio`, and `redisio::enable`

- The Memcached dependency is represented by `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
- The `redisio` and `redisio::enable` recipe files are unavailable in the supplied execution tree.
- The `memcached_instance` provider is also unavailable in the supplied execution tree.

**System package dependencies**: `memcached`; the Redis package name and version are not determinable from the supplied files

**Service dependencies**: Memcached service; Redis service with an unverified unit name

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Literal value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the server configured on port `6379`
- **Migration requirement**: Store the password in Ansible Vault, an AAP credential, or another protected secret mechanism. Do not commit the literal value to role defaults, group variables, or templates.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur variables, HashiCorp Vault references, AWS Secrets Manager references, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings were detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- The Memcached custom-resource provider and referenced `_package.rb`, if available
- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`
- `/var/log/memcached`
- `/var/run/memcached`

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `redis-6379`: TCP port `6379`
- Unix sockets: none specified

**Redis configuration directives to verify**:

The Redis configuration must not contain active lines beginning with:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

**Templates rendered**: None; 0 templates rendered by the supplied recipes

## Pre-flight checks:

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
rpm -q memcached 2>/dev/null || dpkg-query -W memcached
ss -ltnup | grep ':11211'
ps -ef | grep '[m]emcached'
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
printf 'stats\r\n' | nc -w 2 127.0.0.1 11211 | grep -E 'STAT (max_connections|threads|limit_maxbytes)'
ls -ld /var/log/memcached
ls -ld /var/run/memcached

# Expected Memcached results:
# - The memcached service is active and enabled.
# - Package memcached is installed.
# - TCP and UDP listeners exist on port 11211.
# - The process uses the intended service account.
# - The protocol check returns a VERSION response.
# - /var/log/memcached and /var/run/memcached exist with mode 0755.
# - Both directories are owned by the configured Memcached service user and group.

# Redis instance: redis-6379
# Identify the service unit because redisio::enable is unavailable.
systemctl list-unit-files | grep -E 'redis|redis-server'
systemctl list-units --type=service | grep -E 'redis|redis-server'

# Replace the placeholder only after verifying the actual Redis service name.
systemctl status <verified-redis-service-name>
systemctl is-enabled <verified-redis-service-name>
systemctl is-active <verified-redis-service-name>
ss -ltnp | grep ':6379'
ls -ld /run/redis
ls -ld /var/log/redis

# Redis authentication and query; do not expose the password in shell history.
read -rsp 'Redis password: ' REDISCLI_AUTH; export REDISCLI_AUTH; echo
redis-cli -p 6379 PING
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
unset REDISCLI_AUTH

# Expected Redis results:
# - The verified Redis service is active and enabled.
# - Redis listens on TCP port 6379.
# - /run/redis exists.
# - /var/log/redis is owned by redis:redis with mode 0755.
# - Authentication succeeds and PING returns PONG.
# - INFO reports redis_version and tcp_port:6379.

# Verify Redis configuration cleanup.
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Expected result:
# - No output is returned for active lines matching the five removed directives.

# Review logs for both named instances.
journalctl -u <verified-redis-service-name> --no-pager -n 100
journalctl -u memcached --no-pager -n 100

# Check for startup failures, authentication errors, bind failures,
# permission errors, and configuration parse errors.

# Endpoint summary.
ss -ltnp | grep -E ':(6379|11211)\b'
ss -lunp | grep ':11211'
```
