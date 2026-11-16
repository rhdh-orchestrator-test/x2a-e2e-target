---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and requests one Redis instance on port `6379` through the external `memcached` and `redisio` cookbooks. Memcached uses 64 MB of memory, TCP/UDP port `11211`, listens on `0.0.0.0`, permits 1,024 connections, and is enabled and started. Redis uses `/run/redis` as its PID directory, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and is requested to start at boot. The `redisio` recipe implementation is unavailable, so its package name, service unit, templates, and provider behavior must be determined on the target platform. The Redis password must be migrated from the hardcoded Chef value into Ansible Vault or an AAP credential.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached caching service
  - Location/Path: `/var/log/memcached`, `/var/run/memcached`
  - Port/Socket: TCP `11211`, UDP `11211`
  - Key Config: `64` MB memory, listen address `0.0.0.0`, maximum `1024` connections, maximum object size `1m`, ulimit `1024`, empty experimental and extra CLI option lists
  - Package: `memcached`, with no pinned version
  - Service action: Start and enable
  - Service account: Uses the `service_user` and `service_group` values from the Memcached custom resource context; concrete names are not defined in the supplied files
  - Runtime directory: `/var/run/memcached`

- **Redis server on port 6379**: Redis caching service
  - Location/Path: `/etc/redis/6379.conf`, `/var/log/redis`, `/run/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication enabled, PID directory `/run/redis`, replication-related directives removed from the configuration
  - Password: Chef source contains `redis_secure_password_123`; migrate this value to Ansible Vault or an AAP credential
  - Service action: Enablement requested through `redisio::enable`; actual service unit is unresolved because the Redis recipes are unavailable
  - Package: Not determinable from the supplied execution tree

No collection iteration is present. The Memcached custom resource explicitly creates the `memcached` instance, and the Redis configuration explicitly contains one server entry for port `6379`.

## File Structure

```text
Recipes:
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb

Providers:
No provider file paths supplied.

Templates:
No template file paths supplied.

Attributes:
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

Files:
No static file paths supplied.
```

No provider file path is supplied for `memcached_instance[memcached]`. No rendered ERB templates or static files are listed.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached::default` recipe.
   - Assigns one Redis server configuration entry for port `6379`.
   - Sets the Redis password, replication setting, and base PID directory.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis` with owner `redis`, group `redis`, and mode `0755`.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` when the file exists.
   - Includes the unavailable `redisio::enable` recipe to request Redis enablement at boot.
   - Redis assignments:
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
     - `base_piddir`: `/run/redis`

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares `memcached_instance[memcached]`.
   - Starts and enables the explicitly named `memcached` instance.
   - Configures memory `64` MB, TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, maximum connections `1024`, maximum object size `1m`, empty experimental options, empty extra CLI options, and ulimit `1024`.
   - Reads the Memcached defaults from `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`.
   - Uses an attribute-driven thread value; no explicit thread value is defined in the supplied attributes.
   - The provider implementation is not included in the supplied execution tree.

3. **Memcached package setup** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`):
   - Installs package `memcached` at `node['memcached']['version']`; the supplied default is `nil`, so no version is pinned.
   - Creates the system group represented by `service_group` unless the service user already exists.
   - Creates the locked system user represented by `service_user` with:
     - `manage_home`: `false`
     - `gid`: `service_group`
     - `home`: `/nonexistent`
     - `comment`: `Memcached`
     - `shell`: `/bin/false`
   - Creates `/var/log/memcached` owned by `service_user:service_group` with mode `0755`.
   - Creates `/var/run/memcached` owned by `service_user:service_group` with mode `0755`.
   - The supplied execution tree does not show this recipe as an independent include, but its resources define the Memcached dependency behavior to preserve where required.

4. **Redis configuration and enablement** (`cookbooks/cache/recipes/default.rb`):
   - Requests Redis setup through `redisio`.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Modifies `/etc/redis/6379.conf` only when the file exists.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Requests Redis enablement through `redisio::enable`.
   - The `redisio` and `redisio::enable` recipe files are unavailable. Do not infer the Redis package, service unit, configuration template, or provider implementation.

5. **SELinux recipes**:
   - `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb`
   - `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb`
   - `migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb`
   - These recipes are present in the dependency tree, but no invocation is shown in the supplied `cache` execution flow.

## Dependencies

**External cookbook dependencies**:
- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:
- `memcached`
- Redis package: unresolved because the `redisio` recipe is unavailable

**System users and groups**:
- `service_user` and `service_group` for Memcached; concrete names are unresolved
- `redis:redis` for `/var/log/redis`

**Service dependencies**:
- Memcached is started and enabled by `memcached_instance[memcached]`
- Redis enablement is requested through the unavailable `redisio::enable` recipe

**Supported platforms**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded Chef recipe; no Vault, CyberArk, AWS Secrets Manager, Chef Vault, data bag, Conjur, or environment-variable provider detected
  - **URL**: Not applicable
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Literal value**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe
- **Usage context**: Password authentication for the Redis instance on port `6379`
- **Migration storage**: Ansible Vault or an AAP-supported credential
- **Migration variable**: Use a variable such as `redis_password`; do not embed the literal password in Ansible tasks, templates, or shell commands

No other credentials, secrets, private keys, API keys, TLS certificate references, or secret-provider integrations were detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/var/log/memcached`
- `/var/run/memcached`
- `/var/log/redis`
- `/etc/redis/6379.conf`, if created by the selected Redis implementation
- `/run/redis`, if used by the selected Redis implementation

**Service endpoints to check**:
- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`

**Templates rendered**:
- None; no ERB templates are listed or rendered

**Configuration transformations**:
- Remove `replica-serve-stale-data`
- Remove `replica-read-only`
- Remove `repl-ping-replica-period`
- Remove `client-output-buffer-limit`
- Remove `replica-priority`

## Pre-flight checks

```bash
# Memcached package, account, and directories
rpm -q memcached 2>/dev/null || dpkg-query -W -f='${Status} ${Version}\n' memcached
getent passwd <service_user>
getent group <service_group>
ls -ld /var/log/memcached /var/run/memcached

# Memcached service: instance memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
systemctl cat memcached

# Memcached TCP and UDP endpoints: 0.0.0.0:11211
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
printf "version\r\nquit\r\n" | nc -w 2 127.0.0.1 11211

# Verify Memcached effective settings
ps -ef | grep '[m]emcached'
# Confirm memory 64 MB, TCP/UDP port 11211, listen address 0.0.0.0,
# maximum connections 1024, maximum object size 1m, and ulimit 1024.

# Redis service discovery: instance on port 6379
systemctl list-unit-files | grep -i redis
systemctl list-units --all | grep -i redis

# Replace <redis-service-unit> with the service unit identified above.
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>

# Redis TCP endpoint: port 6379
ss -tlnp | grep ':6379'

# Use a protected prompt, environment variable, or AAP-injected secret.
redis-cli -p 6379 -a '<redis_password>' PING

# Redis configuration and directories
test -f /etc/redis/6379.conf && \
  grep -E '^(port|requirepass|pidfile)' /etc/redis/6379.conf
ls -ld /run/redis
ls -ld /var/log/redis
journalctl -u <redis-service-unit> --no-pager -n 50

# Confirm the five removed directive families are absent.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Combined network and process check
ss -tulpn | grep -E ':(11211|6379)\b'
ps -ef | grep -E '[m]emcached|[r]edis-server'
```

Expected results:

- The `memcached` service is enabled and active.
- Memcached listens on TCP and UDP port `11211`.
- The Memcached protocol responds with a `VERSION` line.
- Memcached uses the configured memory, connection, listen, object-size, and ulimit values.
- The Redis service identified on the target host is enabled and active.
- Redis listens on port `6379` and authenticated `PING` returns `PONG`.
- `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- `/run/redis` exists when required by the selected Redis implementation.
- The five specified Redis directive families are absent from `/etc/redis/6379.conf`.
