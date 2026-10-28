---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook references the external `memcached`, `redisio`, and `redisio::enable` recipes, none of which are present in the supplied execution tree. The local recipe includes Memcached first, creates `/var/log/redis`, assigns Redis configuration through a reported `redisio['servers']` collection, includes Redis, runs `ruby_block[fix_redis_config]`, and then enables Redis. The execution analysis confirms the recipe inclusions, directory resource, Ruby block, execution order, and absence of local supporting files, but does not independently verify the Redis instance values, configuration path, credential, resource properties, or dependency version constraints. These details must be confirmed before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Memcached**
  - Purpose: External Memcached cache service
  - Location/Path: Not confirmed in the supplied analysis
  - Port/Socket: Not explicitly configured; the conventional port `11211` is unverified
  - Key Config: Managed by the missing external `memcached` recipe; package name, service name, bind address, and configuration path are not confirmed

- **Redis instance `6379`**
  - Purpose: External Redis cache service
  - Location/Path: The plan reports `/etc/redis/6379.conf`; this path is not confirmed by the supplied structured analysis
  - Port/Socket: The plan reports TCP port `6379`; this value is not confirmed by the supplied structured analysis
  - Key Config: The plan reports a Redis server assignment with authentication and `replicaservestaledata` unset; these values require confirmation from the recipe implementation
  - Log directory: `/var/log/redis` is confirmed as a directory resource; owner, group, mode, and recursive behavior are not confirmed by the supplied analysis

The supplied execution tree does not show an explicit `.each` loop over the Redis server collection. The plan reports one Redis item named `6379`, but the assignment and its values must be verified against the recipe source.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

No local providers, templates, attribute files, or static files are present in the supplied execution tree. The referenced `memcached`, `redisio`, and `redisio::enable` recipes are external dependencies and are not local files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe first.
   - The referenced Memcached recipe is not present in the supplied execution tree.
   - Package name, service name, configuration path, port, and bind address are not available from the local recipe analysis.
   - The migration must supply or include an equivalent Memcached implementation before proceeding with Redis tasks.

2. **default** (`cookbooks/cache/recipes/default.rb`):
   - Assigns the Redis server collection according to the migration plan:
     - Redis instance name: `6379`
     - Reported port: `6379`
     - Reported authentication setting: `requirepass`
     - Reported `replicaservestaledata` value: `nil`
   - These node attribute assignments are not present in the supplied structured analysis and must be verified before being treated as confirmed requirements.
   - If confirmed, migrate the password to Ansible Vault rather than retaining a hardcoded value.
   - No `.each` loop is confirmed in the supplied execution tree.

3. **default** (`cookbooks/cache/recipes/default.rb`):
   - Creates `directory[/var/log/redis]`.
   - The path is confirmed by the resource analysis.
   - The reported owner `redis`, group `redis`, mode `0755`, and recursive creation behavior require confirmation from the resource properties.

4. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio` recipe.
   - The referenced Redis recipe is not present in the supplied execution tree.
   - The missing dependency is expected to provide Redis installation and primary configuration, but its package name, service name, configuration path, and service behavior are not confirmed.

5. **default** (`cookbooks/cache/recipes/default.rb`):
   - Executes `ruby_block[fix_redis_config]`.
   - The Ruby block is confirmed by the execution analysis.
   - The plan reports that it edits `/etc/redis/6379.conf` and removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The target path and directive list are not confirmed by the supplied structured analysis and must be verified against the Ruby block implementation.
   - If confirmed, the Ansible implementation should preserve all other configuration content and perform no action when the target file is absent.
   - No explicit service notification is confirmed.

6. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `redisio::enable` recipe.
   - The referenced enablement recipe is not present in the supplied execution tree.
   - The Ansible implementation should enable and start the Redis service only after its configuration is available, using the service name supplied by the selected Redis implementation.

## Dependencies

**External cookbook dependencies**: `memcached`; `redisio`. The `redisio::enable` recipe is also referenced. Version constraints are not confirmed by the supplied analysis.

**System package dependencies**: No package resources or verified package names are present in the local cookbook analysis. Package names must be obtained from the selected Memcached and Redis implementations before writing Ansible package tasks.

**Service dependencies**: Memcached service management is delegated to the missing `memcached` recipe. Redis installation, configuration, and enablement are delegated to the missing `redisio` and `redisio::enable` recipes. Exact service names are not confirmed.

## Credentials

**Detection Summary**: 0 credentials confirmed in the available structured analysis. The plan reports one possible hardcoded Redis credential, but that claim is unverified.

**Source**:
  - **Provider**: No secrets provider detected. The reported hardcoded Chef recipe value requires source verification.
  - **URL**: None confirmed
  - **Path**: `cookbooks/cache/recipes/default.rb` is the reported source path; the credential assignment is not confirmed by the supplied analysis

### Possible Redis authentication password

- **Variable**: Reported as `node['redisio']['servers'][0]['requirepass']`; unverified
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`; unverified
- **Current storage**: Reported as a hardcoded recipe value; unverified
- **Usage context**: Reported Redis client authentication for instance `6379`; unverified
- **Migration handling**: If confirmed in the recipe, store the password in Ansible Vault, for example as `vault_redis_password`, and reference it from the Redis configuration.

No Vault, CyberArk, AWS Secrets Manager, data bag, encrypted data bag, TLS certificate, private key, API key, or environment-variable secret integration is confirmed by the available structured results.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf` if the reported Redis configuration path is confirmed
- The Memcached configuration path supplied by the selected external implementation

**Service endpoints to check**:

- Redis instance `6379`: TCP port `6379` only if confirmed by the recipe or generated configuration
- Memcached: port not configured in the local cookbook; verify the dependency configuration before using the conventional port `11211`
- Unix sockets: none confirmed
- Bind addresses: not specified; verify generated Redis and Memcached configuration

**Configuration directives to verify**:

- Redis port `6379`, if the reported value is confirmed
- Redis authentication configuration, if the reported password assignment is confirmed
- Absence of `replica-serve-stale-data`
- Absence of `replica-read-only`
- Absence of `repl-ping-replica-period`
- Absence of `client-output-buffer-limit`
- Absence of `replica-priority`

These directive checks apply only if the reported Ruby block implementation is confirmed.

**Templates rendered**:

- None. No local templates are listed.
- Render count: `0` confirmed local templates.

## Pre-flight checks:

```bash
# Confirm the local recipe and its external recipe references
test -f cookbooks/cache/recipes/default.rb
grep -nE "include_recipe ['\"](memcached|redisio|redisio::enable)" \
  cookbooks/cache/recipes/default.rb

# Verify the Redis log directory resource after migration
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis

# Redis instance 6379 checks, if the instance and configuration path are confirmed
test -f /etc/redis/6379.conf
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' \
  /etc/redis/6379.conf

# Do not print the Redis password while checking for the directive
grep -Eq '^[[:space:]]*requirepass[[:space:]]+[^[:space:]]+' \
  /etc/redis/6379.conf

# Verify reported cleanup directives are absent, if the Ruby block behavior is confirmed
! grep -Eq '^[[:space:]]*replica-serve-stale-data' /etc/redis/6379.conf
! grep -Eq '^[[:space:]]*replica-read-only' /etc/redis/6379.conf
! grep -Eq '^[[:space:]]*repl-ping-replica-period' /etc/redis/6379.conf
! grep -Eq '^[[:space:]]*client-output-buffer-limit' /etc/redis/6379.conf
! grep -Eq '^[[:space:]]*replica-priority' /etc/redis/6379.conf

# Identify the Redis package and service supplied by the selected implementation
dpkg -l | grep -E 'redis|redis-server' || rpm -qa | grep -E 'redis|redis-server'
systemctl list-unit-files | grep -E 'redis|redis-server'

# Replace the unit name after identifying the implementation
systemctl status redis-server --no-pager
ss -ltnp | grep ':6379'
journalctl -u redis-server --no-pager -n 50

# Test Redis authentication without placing a password in the command history
redis-cli -p 6379 PING
redis-cli -p 6379 --askpass PING

# Identify the Memcached package and service supplied by the dependency
dpkg -l | grep memcached || rpm -qa | grep memcached
systemctl list-unit-files | grep memcached
systemctl status memcached --no-pager

# Verify the Memcached port only after confirming the dependency configuration
ss -ltnp | grep ':11211'
printf 'version\r\n' | nc -w 2 127.0.0.1 11211
journalctl -u memcached --no-pager -n 50

# Validate configuration using the commands supplied by the selected
# Redis and Memcached implementations.
```