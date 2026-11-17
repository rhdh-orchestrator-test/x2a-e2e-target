---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the Memcached instance `memcached` on TCP and UDP port `11211`, and one Redis server on port `6379`. Memcached is managed through the `memcached_instance[memcached]` custom resource and is started and enabled. Redis receives a hardcoded authentication password, uses `/run/redis` for its PID directory, creates `/var/log/redis`, removes five replication-related directives from `/etc/redis/6379.conf`, and is enabled through the unavailable `redisio::enable` recipe. The supplied execution tree does not include the Redis dependency implementation, Memcached provider, exact package resources, or the complete seven-file analysis inventory; these items must be resolved before finalizing the Ansible role.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached cache service
  - Location/Path: Configuration path is provided by the unavailable Memcached custom-resource provider
  - Port/Socket: TCP `11211`; UDP `11211`
  - Key Config: Listen address `0.0.0.0`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; ulimit `1024`; user `service_user`; experimental options empty; extra CLI options empty
  - Worker threads: Supplied by `node['memcached']['threads']`; this attribute is not present in the supplied `attributes/default.rb` and must be resolved from the dependency implementation
  - Actions: Start and enable

- **Redis server on port `6379`**: Redis cache and data service
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled; password source value is `redis_secure_password_123`; log directory owner `redis`; group `redis`; mode `0755`; recursive creation
  - Post-configuration cleanup: Remove `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Service enablement: Delegated to the unavailable `redisio::enable` recipe
  - Redis configuration: One server entry with port `6379`, `requirepass`, and `replicaservestaledata` set to `nil`

The Memcached values and resource actions are source-derived from the supplied migration plan but are not independently verifiable from the available structured analysis. Confirm them against the dependency attributes and provider before implementation.

## File Structure

The supplied execution-relevant directory listing is:

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**

No provider file was listed. The `memcached_instance` custom resource is used, but its provider implementation is unavailable.

**Templates:**

No templates are rendered by the supplied execution flow.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

No static files are deployed by the supplied execution flow.

The structured analysis reports seven files analyzed, but only the three paths above are identified. The four omitted paths must be enumerated and reconciled before migration sign-off.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe.
   - Configures the Redis node attributes.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis`.
   - Runs `ruby_block[fix_redis_config]`.
   - Includes the unavailable `redisio::enable` recipe.
   - No `.each` loops were identified; the Redis configuration contains exactly one server entry, port `6379`.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates the custom resource `memcached_instance[memcached]`.
   - Invokes the `start` and `enable` actions.
   - Configures TCP port `11211`, UDP port `11211`, listen address `0.0.0.0`, memory `64` MB, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, user `service_user`, empty experimental options, and empty extra CLI options.
   - Reads the worker-thread value from `node['memcached']['threads']`; the supplied attributes file does not define this value.
   - Uses a provider that is not present in the supplied execution tree.
   - The exact package name, configuration path, service unit, and provider behavior remain unresolved.

3. **Redis attribute configuration** (`cookbooks/cache/recipes/default.rb`):
   - Sets `node.default['redisio']['servers']` to one Redis entry:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.

4. **`redisio`** (`redisio` dependency recipe referenced by `cookbooks/cache/recipes/default.rb`):
   - The recipe is unavailable in the supplied execution tree.
   - Its package installation, Redis user and group creation, configuration generation, service name, PID-directory creation, and password rendering must be resolved before implementation.
   - Confirm whether it creates `/etc/redis/6379.conf`.

5. **Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Creates `directory[/var/log/redis]`.
   - Uses owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Must run after the Redis dependency has created the `redis` account.
   - The Ansible equivalent is an idempotent directory task.

6. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Operates on `/etc/redis/6379.conf` only when the file exists.
   - Removes every line matching `^replica-serve-stale-data.*$`.
   - Removes every line matching `^replica-read-only.*$`.
   - Removes every line matching `^repl-ping-replica-period.*$`.
   - Removes every line matching `^client-output-buffer-limit.*$`.
   - Removes every line matching `^replica-priority.*$`.
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - The Ansible implementation should use five `ansible.builtin.lineinfile` tasks with `state: absent`, conditional on the configuration file existing.
   - Restart or reload Redis only when a cleanup task changes the file, using the service behavior confirmed from `redisio`.

7. **`redisio::enable`** (`redisio::enable` dependency recipe referenced by `cookbooks/cache/recipes/default.rb`):
   - The recipe is unavailable in the supplied execution tree.
   - Intended to enable the Redis service at boot.
   - The exact Redis service name and service resource must be resolved before adding the Ansible service task.
   - Preserve the Chef order: Redis setup, log directory creation, configuration cleanup, then service enablement.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- Memcached package: unresolved; the package resource is not present in the supplied execution tree.
- Redis package: unresolved; the `redisio` recipe is unavailable.
- Do not infer package names solely from cookbook names. Confirm the actual package names for Ubuntu and CentOS targets from the dependency implementations.

**Service dependencies**:

- `memcached_instance[memcached]` starts and enables Memcached.
- `redisio` provides Redis installation and initial configuration, but its implementation is unavailable.
- `redisio::enable` provides Redis enablement, but its implementation is unavailable.
- The Redis service name is unresolved.
- The Memcached service unit and exact provider behavior require confirmation.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file, based on the supplied source plan. The structured analysis does not contain credential findings, so this count and the absence of additional credential mechanisms must be confirmed against all analyzed files.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal source value**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute assignment
- **Usage context**: Redis authentication for the server on port `6379`
- **Migration handling**: Store the value in Ansible Vault or an AAP credential/secret-management integration. Do not retain it as a plaintext role variable or template value.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret, TLS certificate, TLS private key, database connection string, API token, or additional credential reference was identified in the supplied files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`
- Memcached configuration file generated by the dependency provider; exact path unresolved
- Memcached service unit or init configuration; exact path unresolved
- Redis service unit or init configuration; exact path unresolved
- All four files omitted from the reported seven-file analysis inventory

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance on port `6379`: TCP `*:6379`
- Unix sockets: None configured or referenced

**Templates rendered**:

- No templates rendered
- Render count: `0`

**Configuration transformations**:

- `/etc/redis/6379.conf` is conditionally modified.
- The following five directive families are removed:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks

```bash
# Confirm the target platform before selecting package names.
cat /etc/os-release
```

### Memcached instance `memcached`

```bash
# Replace the unit name only after confirming the Memcached provider implementation.
systemctl status memcached.service

# Confirm the Memcached process is running.
pgrep -a memcached

# Verify the TCP listener for instance memcached.
ss -ltnp | grep ':11211'

# Verify the UDP listener for instance memcached.
ss -lunp | grep ':11211'

# Basic Memcached protocol check.
printf "version\r\n" | nc -w 2 127.0.0.1 11211

# Expected output includes:
# VERSION <version>

# Verify memory and connection settings.
printf "stats settings\r\n" | nc -w 2 127.0.0.1 11211 | grep -E 'limit_maxbytes|maxconns'

# Expected values:
# limit_maxbytes approximately 67108864
# maxconns 1024
```

### Redis instance on port `6379`

```bash
# Identify the Redis process.
pgrep -a redis

# Verify the Redis listener.
ss -ltnp | grep ':6379'

# Confirm the Redis configuration exists.
test -f /etc/redis/6379.conf && echo "Redis configuration exists"

# Confirm the PID directory exists.
test -d /run/redis && ls -ld /run/redis

# Confirm the log directory ownership and mode.
stat -c '%A %U %G %n' /var/log/redis
# Expected:
# drwxr-xr-x redis redis /var/log/redis
```

### Redis authentication and configuration

```bash
# Obtain this value from Ansible Vault or an AAP-injected secret.
export REDISCLI_AUTH='<retrieve-from-Ansible-Vault-or-AAP-secret>'

# Verify authentication and availability.
redis-cli -p 6379 PING
# Expected:
# PONG

# Verify the Redis server and configured port.
redis-cli -p 6379 INFO server | grep -E 'redis_version|tcp_port'
redis-cli -p 6379 CONFIG GET port
# Expected port:
# 6379

unset REDISCLI_AUTH
```

### Redis configuration cleanup

```bash
# These commands should produce no output after migration.
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf || true

# Confirm that authentication is configured without printing its value.
grep -Eq '^requirepass[[:space:]]+' /etc/redis/6379.conf \
  && echo "Redis requirepass is configured"

# Confirm the configured port.
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf
```

### Redis service enablement

```bash
# Replace the placeholder only after resolving the redisio::enable implementation.
systemctl is-enabled <resolved-redis-service-name>
systemctl is-active <resolved-redis-service-name>
```

Expected results:

```text
enabled
active
```

### Service logs

```bash
# Redis log directory.
ls -lah /var/log/redis

# Discover Redis log files until the dependency implementation identifies the exact filename.
find /var/log/redis -maxdepth 1 -type f -print

# Memcached service logs.
journalctl -u memcached.service --no-pager -n 50
```

The final Ansible validation must replace unresolved service names, package names, configuration paths, and Redis log filenames with values confirmed from the missing dependency implementations.