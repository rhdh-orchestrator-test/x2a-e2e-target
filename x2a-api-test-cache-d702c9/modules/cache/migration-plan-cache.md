---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. The Memcached instance is created through the `memcached_instance[memcached]` custom resource and is started and enabled. Redis is configured with a password, runtime PID directory `/run/redis`, log directory `/var/log/redis`, and post-processing that removes five replication-related directives from `/etc/redis/6379.conf`. The available execution tree does not include the `redisio` implementation or the Memcached provider, so package names, service-unit names, provider behavior, and some resource values must be verified from the complete source inventory before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Provider-specific configuration path is not available from the supplied execution tree
  - Port/Socket: TCP `11211`; UDP `11211`
  - Key Config: Listen address `0.0.0.0`, memory `64` MB, maximum connections `1024`, maximum object size `1m`, ulimit `1024`, empty experimental and extra CLI options, start and enable actions
  - Threads: Uses `node['memcached']['threads']`; no value is present in the supplied attribute analysis and must be verified
  - Version: `nil`; no explicit version configured
  - User: `service_user`, resolved by the Memcached provider

- **6379**: Redis server
  - Location/Path: Configuration `/etc/redis/6379.conf`; runtime PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Password `redis_secure_password_123` as reported in the source recipe; `replicaservestaledata` set to `nil`
  - Log directory: Owner `redis`, group `redis`, mode `0755`, recursive creation
  - Service state: Enabled through `redisio::enable`; exact service-unit name is unavailable
  - Configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`

The Memcached values and Redis values above are based on the stated recipe and attribute references, but the corresponding file contents are not included in the supplied structured analysis. They must be confirmed against the complete seven-file inventory before implementation.

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

The `memcached_instance` custom resource has a provider, but its provider path was not supplied in the execution tree or directory listing. Locate the provider in the dependency artifact before implementing provider-specific behavior.

**Templates:**

```text
```

No rendered templates were supplied.

**Attributes:**

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**

```text
```

No static files were deployed by the supplied execution flow.

The directory listing also contains Memcached `_package.rb` and SELinux recipe files, but they are not executed or referenced by the supplied execution tree and are therefore excluded from the migration file list. The stated analysis count is seven files; the complete inventory must be reconciled before migration so that no analyzed provider, template, or static file is omitted.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached default recipe:
     ```ruby
     include_recipe 'memcached'
     ```
   - Configures one Redis server collection item:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Sets the Redis PID base directory to `/run/redis`.
   - Includes the Redis installation and configuration recipe:
     ```ruby
     include_recipe 'redisio'
     ```
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf` when the file exists.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Includes the Redis enable recipe:
     ```ruby
     include_recipe 'redisio::enable'
     ```
   - The supplied execution tree reports both `redisio` and `redisio::enable` as unavailable. Package names, service names, user and group creation, data directories, templates, and provider behavior must be obtained from the missing dependency or verified on the target platform.
   - The Redis configuration cleanup should be implemented with conditional `ansible.builtin.lineinfile` tasks and should notify the Redis 6379 service handler when changes occur.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates exactly one custom resource:
     ```text
     memcached_instance[memcached]
     ```
   - Configures the `memcached` instance with the following reported properties:
     - Memory: `64`
     - TCP port: `11211`
     - UDP port: `11211`
     - Listen address: `0.0.0.0`
     - Maximum connections: `1024`
     - User: `service_user`
     - Maximum object size: `1m`
     - Threads: `node['memcached']['threads']`; value unresolved
     - Experimental options: empty list
     - Extra CLI options: empty list
     - Ulimit: `1024`
     - Actions: `start` and `enable`
   - Uses the Memcached dependency attributes file:
     ```text
     migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
     ```
   - Defines `version` as `nil` and `logfilepath` as `/var/log/memcached`.
   - The `logfilepath` attribute is not passed by the default recipe to the custom resource. Do not assume it affects service configuration unless the provider consumes it independently.
   - The provider path, package name, configuration path, service-unit name, and command-line rendering must be located and verified before implementation.

3. **`redisio`** (`redisio/recipes/default.rb`, unavailable):
   - The referenced recipe is not present in the supplied execution tree.
   - Do not infer the Redis package name, package version, service name, configuration template, Redis user/group behavior, data directory, or provider implementation from the available files.

4. **`redisio::enable`** (`redisio/recipes/enable.rb`, unavailable):
   - The referenced enable recipe is not present in the supplied execution tree.
   - The Ansible migration must explicitly enable and start the Redis instance named `6379` after the exact service-unit name is verified.

No collection loops requiring expansion were identified. The Redis server collection contains the single explicit item `6379`, and the Memcached recipe creates the single explicit resource `memcached`.

## Dependencies

**External cookbook dependencies**:

- `memcached`
- `redisio`
- `redisio::enable`

The available Memcached recipe is:

```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

The `redisio` and `redisio::enable` recipe files are unavailable in the supplied execution tree. The cookbook metadata file was not supplied, so additional metadata-declared dependencies cannot be confirmed.

**System package dependencies**:

- Memcached package name: not exposed; verify from the Memcached provider
- Redis package name: not exposed; verify from the `redisio` implementation or target platform
- Package versions: no explicit versions verified
- Required service manager: verify whether the target uses systemd
- Required service accounts: verify creation of `service_user`, `redis`, and the Redis group

No package name or version should be added to the Ansible role until verified from the complete source inventory or target platform.

**Service dependencies**:

- Memcached instance `memcached`
- Redis instance `6379`
- The exact Memcached and Redis service-unit names are unavailable from the supplied analysis.

## Credentials

**Detection Summary**: 1 credential reported in 1 source file; detection requires confirmation against the complete recipe analysis.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected
- **Source file**: `cookbooks/cache/recipes/default.rb`

### Redis Authentication Password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for instance `6379`
- **Migration handling**: Move the password to Ansible Vault or an AAP credential/secret variable. Do not commit the literal value to role defaults, plaintext group variables, templates, or shell commands.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, or environment-variable secret reference was identified in the supplied files.

No TLS certificate, private key, database connection string, API token, or additional credential was reported.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- Memcached configuration path, after provider verification
- Redis data directory, after `redisio` verification
- The missing Memcached provider, if present in the complete seven-file inventory
- The missing `redisio` and `redisio::enable` implementation files, if present outside the supplied execution tree

**Service endpoints to check**:

- Memcached instance `memcached`, TCP `0.0.0.0:11211`
- Memcached instance `memcached`, UDP `0.0.0.0:11211`
- Redis instance `6379`, TCP port `6379`
- Redis Unix socket: none specified
- Redis bind address: not specified

**Templates rendered**:

- No templates were supplied or shown as rendered.
- Render count: `0` verified templates.

**Configuration transformations**:

For Redis instance `6379`, remove the following directives from `/etc/redis/6379.conf`:

1. `replica-serve-stale-data`
2. `replica-read-only`
3. `repl-ping-replica-period`
4. `client-output-buffer-limit`
5. `replica-priority`

## Pre-flight checks

```bash
# Verify the target service manager
command -v systemctl
```

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'

nc -vz 127.0.0.1 11211
printf 'version\r\n' | nc 127.0.0.1 11211

ps -ef | grep '[m]emcached'
```

Verify that instance `memcached`:

- Is enabled and active.
- Listens on TCP port `11211`.
- Listens on UDP port `11211` when UDP support is enabled by the provider.
- Uses listen address `0.0.0.0`.
- Uses `64` MB of memory.
- Allows `1024` maximum connections.
- Uses maximum object size `1m`.
- Uses ulimit `1024`.
- Uses the correct `service_user`.
- Uses the expected provider-specific configuration and command-line syntax.

Replace `memcached` with the exact verified service-unit name if the provider uses a different unit.

### Redis instance `6379`

Replace `<redis-6379-service>` with the exact service-unit name obtained from the `redisio` implementation.

```bash
systemctl status <redis-6379-service>
systemctl is-enabled <redis-6379-service>
systemctl is-active <redis-6379-service>

ss -ltnp | grep ':6379'
nc -vz 127.0.0.1 6379
```

Verify that instance `6379`:

- Is enabled and active.
- Listens on TCP port `6379`.
- Uses `/run/redis` as the runtime PID directory.
- Uses `/var/log/redis` as the log directory.
- Uses the protected Redis password.
- Does not contain the five removed directives in its final configuration.

### Redis authentication for instance `6379`

Use the Ansible Vault-managed password rather than placing it directly in shell history:

```bash
redis-cli -p 6379 -a '<redis-password-from-secret-store>' PING
```

Expected result:

```text
PONG
```

Verify that unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result:

- Redis returns an authentication error rather than `PONG`.

### Redis configuration for instance `6379`

```bash
grep -E '^(requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Verify:

- `requirepass` is supplied through the protected Ansible secret mechanism.
- `replica-serve-stale-data` is absent.
- `replica-read-only` is absent.
- `repl-ping-replica-period` is absent.
- `client-output-buffer-limit` is absent.
- `replica-priority` is absent.

Check the Redis runtime directory:

```bash
ls -ld /run/redis
find /run/redis -maxdepth 1 -type f -ls
```

Check the Redis log directory:

```bash
ls -ld /var/log/redis
find /var/log/redis -maxdepth 1 -type f -ls
```

Verify that `/var/log/redis`:

- Exists.
- Is owned by `redis`.
- Has group `redis`.
- Has mode `0755`.

Check Redis logs:

```bash
journalctl -u <redis-6379-service> --no-pager -n 100
```

Check for:

- Successful startup.
- Successful bind to port `6379`.
- No configuration parse errors.
- No authentication configuration errors.
- No permission errors for `/run/redis` or `/var/log/redis`.

### Combined network verification

```bash
ss -ltnp | grep -E ':(6379|11211)\b'
ss -lunp | grep ':11211'
```

Expected result:

- Redis instance `6379` listens on TCP port `6379`.
- Memcached instance `memcached` listens on TCP port `11211`.
- Memcached instance `memcached` listens on UDP port `11211` when UDP support is enabled.