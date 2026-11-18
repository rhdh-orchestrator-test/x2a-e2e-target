---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures two cache services: the Memcached instance `memcached` and a Redis instance on port `6379`. Memcached is created through the `memcached_instance` custom resource with 64 MB memory, TCP/UDP port `11211`, a `0.0.0.0` listen address, and a 1024-connection limit. Redis is configured with password authentication, a `/run/redis` PID directory, a `/var/log/redis` log directory, and cleanup of replication-related directives in `/etc/redis/6379.conf`. The Redisio recipes and the Memcached custom-resource provider are absent from the supplied execution tree, so their package, template, service, and provider implementation details must be verified separately before producing a fully equivalent Ansible role.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache server
  - Instance resource: `memcached_instance[memcached]`
  - Memory: `64` MB
  - Location/Path: Provider-dependent configuration and service paths
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: `node['memcached']['threads']`; no explicit default is present in the supplied attribute file
  - Experimental options: `[]`
  - Extra CLI options: `[]`
  - Ulimit: `1024`
  - User: `service_user`
  - Actions: start and enable
  - Version: `nil`; no explicit Memcached version is selected

- **Redis on port 6379**: Redis cache server
  - Location/Path: `/etc/redis/6379.conf`
  - Port: `6379`
  - Password authentication: enabled through the configured `requirepass` value
  - PID directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Log directory creation: recursive
  - Configuration cleanup removes:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`
  - No additional Redis ports or replication instances are specified

The Redis port, password, PID directory, log directory settings, and cleanup directives are source-derived details from `cookbooks/cache/recipes/default.rb`; they should be reverified against the complete source because they are not present in the supplied structured execution summary.

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

No provider file path was supplied for `memcached_instance`. The custom-resource provider is expected to be inside the Memcached dependency, but its implementation is not present in the execution tree or directory listing.

**Templates:**
```text
```

No templates are shown as rendered.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file` resources.

The structured analysis reports seven analyzed files, while only the three concrete paths above are identified in the supplied plan. The four additional analyzed file paths must be obtained from the source inventory before migration completion.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe using `include_recipe 'memcached'`.
   - Resolves the Memcached recipe to `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Defines one Redis server entry:
     - Port: `'6379'`
     - `requirepass`: `'redis_secure_password_123'`
     - `replicaservestaledata`: `nil`
   - Sets `node.default['redisio']['base_piddir']` to `/run/redis`.
   - Includes `redisio`; the referenced Redisio recipe is not present in the supplied execution tree.
   - Creates `directory[/var/log/redis]` with:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation enabled
   - Executes `ruby_block[fix_redis_config]`.
   - The Ruby block checks whether `/etc/redis/6379.conf` exists, removes lines beginning with the five replication-related directives, and writes the modified contents back to the same file.
   - If `/etc/redis/6379.conf` does not exist, the Ruby block makes no change.
   - Includes `redisio::enable`; the referenced enable recipe is not present in the supplied execution tree.
   - Does not provide enough source evidence to determine Redis package names, templates, service unit names, user/group creation, data-directory behavior, or restart notifications.
   - Resource counts represented by the supplied execution tree:
     - `directory`: 1
     - `ruby_block`: 1
     - `include_recipe`: Memcached, Redisio, and Redisio enable
   - A separate `group['redis']` resource appears in an inconsistent structural note but is not present in the authoritative execution tree or supplied recipe source and must not be added solely from that note.

2. **Memcached dependency default recipe** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates exactly one custom resource: `memcached_instance[memcached]`.
   - Applies actions `[:start, :enable]`.
   - Passes the following values:
     - Memory: `node['memcached']['memory']` → `64`
     - TCP port: `node['memcached']['port']` → `11211`
     - UDP port: `node['memcached']['udp_port']` → `11211`
     - Listen address: `node['memcached']['listen']` → `0.0.0.0`
     - Maximum connections: `node['memcached']['maxconn']` → `1024`
     - User: `service_user`
     - Maximum object size: `node['memcached']['max_object_size']` → `1m`
     - Threads: `node['memcached']['threads']`
     - Experimental options: `node['memcached']['experimental_options']` → `[]`
     - Extra CLI options: `node['memcached']['extra_cli_options']` → `[]`
     - Ulimit: `node['memcached']['ulimit']` → `1024`
   - The provider path and implementation are not present in the supplied file structure.
   - No `.each` loops are present; the single configured item is `memcached`.

3. **`redisio`** (referenced by `cookbooks/cache/recipes/default.rb`):
   - The recipe file is missing from the supplied execution tree.
   - Package names, repository configuration, service names, configuration templates, Redis user/group creation, data-directory behavior, and service notifications cannot be determined from the supplied files.

4. **`redisio::enable`** (referenced by `cookbooks/cache/recipes/default.rb`):
   - The recipe file is missing from the supplied execution tree.
   - The exact Redis service unit and enablement behavior must be obtained from the Redisio cookbook source or confirmed on the target platform.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No direct `package` resources are present in the supplied executed recipes.
- Memcached package: not verified; installation is encapsulated by the missing custom-resource provider.
- Redis package: not verified; installation is encapsulated by the missing Redisio recipes.
- No package name may be hardcoded until the missing provider and Redisio source are supplied or the target operating-system package mapping is confirmed.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Service dependencies**:

- `memcached_instance[memcached]` requests start and enable actions.
- Redis enablement is requested through `redisio::enable`, but the service unit name is unavailable because the recipe is missing.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded secret
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded directly in the recipe
- **Value currently present**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance on port `6379`
- **Migration handling**: Store the password in Ansible Vault or an external secret manager, reference it through a vaulted variable such as `redis_password`, and prevent it from appearing in task output.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, AWS secret reference, environment-variable secret, TLS certificate, private key, database connection string, or additional credential namespace was detected in the supplied files.

The credential finding is source-derived from `cookbooks/cache/recipes/default.rb`; the supplied structured execution summary does not independently report the password and should be updated or rechecked during source verification.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- Memcached configuration and service files once the custom-resource provider implementation is obtained
- The four additional analyzed file paths missing from the supplied inventory

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: port `6379`
- Unix sockets: none specified

**Templates rendered**:

- No templates rendered according to the supplied file structure; render count: `0`

**Configuration mutations**:

- `ruby_block[fix_redis_config]` performs one conditional cleanup of `/etc/redis/6379.conf`.
- The cleanup runs only when the file exists.
- No explicit Chef service restart or reload notification is present in the supplied recipes.

## Pre-flight checks

```bash
# Memcached instance: memcached

systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached

# If the custom provider creates a differently named unit, identify and use
# that exact unit instead of assuming "memcached".
systemctl list-unit-files | grep -i memcached
systemctl list-units --type=service | grep -i memcached

# Memcached TCP connectivity
printf "version\r\n" | nc -w 2 127.0.0.1 11211

# Expected response begins with:
# VERSION

# Memcached TCP listener
ss -ltnp | grep ':11211'

# Expected result: a TCP listener on port 11211 bound according to the
# configured listen address 0.0.0.0.

# Memcached UDP listener
ss -lunp | grep ':11211'

# Expected result: a UDP listener on port 11211.

# Memcached process and settings
ps aux | grep '[m]emcached'

# Verify the process uses service_user and reflects:
# - 64 MB memory
# - maximum 1024 connections
# - maximum object size 1m
# - ulimit 1024
# The exact command-line representation depends on the missing provider.


# Redis instance on port 6379

# Identify the Redis service unit because redisio and redisio::enable are missing.
systemctl list-unit-files | grep -i redis
systemctl list-units --type=service | grep -i redis

# Replace <redis-service-unit> with the verified unit name.
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>

# Redis TCP listener
ss -ltnp | grep ':6379'

# Expected result: a Redis listener on port 6379.

# Redis authenticated operation
# Supply REDIS_PASSWORD from Ansible Vault or the external secret manager.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server

# Expected results:
# PONG
# Redis server information

# Redis unauthenticated access
redis-cli -p 6379 PING

# Expected result: an authentication error.


# Redis configuration

test -f /etc/redis/6379.conf

grep -nE '^(requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Verify the configured password mechanism and confirm these directives are absent:
# - replica-serve-stale-data
# - replica-read-only
# - repl-ping-replica-period
# - client-output-buffer-limit
# - replica-priority


# Redis directories

stat -c '%A %U:%G %n' /var/log/redis
stat -c '%A %U:%G %n' /run/redis
ls -ld /var/log/redis /run/redis

# Expected results:
# - /var/log/redis exists
# - /var/log/redis is owned by redis:redis
# - /var/log/redis has mode 0755
# - /run/redis exists if created by the Redis implementation


# Redis logs

grep -nE '^(logfile|syslog-enabled|dir|pidfile)' /etc/redis/6379.conf
journalctl -u <redis-service-unit> --no-pager -n 100

# Use the active configuration to identify the exact Redis log location.


# Network summary

ss -ltnp | grep -E ':(6379|11211)\b'
ss -lunp | grep ':11211'

# Expected listeners:
# - Redis TCP 6379
# - Memcached TCP 11211
# - Memcached UDP 11211
```