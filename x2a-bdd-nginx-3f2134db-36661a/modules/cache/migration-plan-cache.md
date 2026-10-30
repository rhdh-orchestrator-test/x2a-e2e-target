---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This Chef cookbook contains one analyzed local recipe, `cache::default`, which includes the external `memcached`, `redisio`, and `redisio::enable` recipes and declares one `directory` resource and one `ruby_block` resource. The supplied structured analysis confirms only the resource names, the three includes, and the local cookbook file path. Redis ports, credentials, configuration paths, directory properties, Ruby block behavior, and dependency versions require verification from the complete recipe and metadata sources before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis**: Redis setup and enablement are referenced through the external `redisio` and `redisio::enable` recipes.
  - Location/Path: Not verified
  - Port/Socket: Port `6379` is claimed by the unverified source plan but is not confirmed by the structured analysis
  - Key Config: Redis server definition, authentication settings, configuration path, and replication directives require verification

- **Memcached**: Memcached setup is referenced through the external `memcached` recipe.
  - Location/Path: Not verified
  - Port/Socket: Not established by the analyzed execution tree
  - Key Config: Package, service, configuration path, listener settings, and instance-specific values require verification

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

### Recipes

```text
cookbooks/cache/recipes/default.rb
```

### Providers

```text
None
```

### Templates

```text
None
```

### Attributes

```text
None
```

### Files

```text
None
```

The following included files are referenced by the recipe but are not present in the execution tree or directory listing:

- `memcached` recipe: not found
- `redisio` recipe: not found
- `redisio::enable` recipe: not found

## Module Explanation

The cookbook performs operations in the following execution order. The structured analysis confirms the local recipe, three dependency includes, one `directory` resource, and one `ruby_block` resource. Details not confirmed by that analysis are explicitly marked for verification.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - Declares `directory[/var/log/redis]`.
   - Includes the external `redisio` recipe.
   - Declares `ruby_block[fix_redis_config]`.
   - Includes the external `redisio::enable` recipe.
   - No `.each` loops or collection iterations are shown in the analyzed execution tree.

   ### 1.1 Include `memcached`

   - Chef statement: `include_recipe 'memcached'`
   - The included recipe is not available in the analyzed cookbook path.
   - Migrate this behavior through an external Ansible role or collection only after verifying:
     - Package name
     - Service name
     - Configuration path
     - Listener port or socket
     - Runtime and health-check behavior
   - The claimed dependency version `~> 6.0` requires verification against `metadata.rb`.

   ### 1.2 Create the Redis log directory

   - Resource: `directory[/var/log/redis]`
   - Confirmed path: `/var/log/redis`
   - Owner, group, mode, and recursive-creation settings are not confirmed by the structured analysis and must be verified from the recipe source.
   - Do not assume `redis:redis`, `0755`, or recursive creation until verified.

   ### 1.3 Include `redisio`

   - Chef statement: `include_recipe 'redisio'`
   - The included recipe is not available in the analyzed cookbook path.
   - Redis installation and configuration behavior must be represented by an external Ansible role or equivalent implementation after inspecting the actual dependency.
   - Redis instance names, ports, authentication settings, configuration paths, and package or service names require verification.

   ### 1.4 Apply `ruby_block[fix_redis_config]`

   - Resource: `ruby_block[fix_redis_config]`
   - The resource name is confirmed.
   - The target configuration file, matching expressions, conditional behavior, and write-back behavior are not exposed by the structured analysis.
   - The claimed target `/etc/redis/6379.conf` and the following removals require verification before implementation:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Do not implement equivalent Ansible `replace` or `lineinfile` tasks until the Ruby block contents and target path are confirmed.

   ### 1.5 Include `redisio::enable`

   - Chef statement: `include_recipe 'redisio::enable'`
   - The included recipe is not available in the analyzed cookbook path.
   - Use the selected external Redis role to enable and start the Redis service after verifying its service and instance behavior.

## Dependencies

**External cookbook dependencies**:

- `memcached` — dependency is referenced; claimed version constraint `~> 6.0` requires verification in `metadata.rb`
- `redisio` — dependency is referenced; claimed absence of a version constraint requires verification in `metadata.rb`
- `redisio::enable` — included recipe referenced by the local recipe; dependency implementation is unavailable

**System package dependencies**:

- No package resources are present in the supplied execution tree.
- Package names for Memcached and Redis are not available in the analyzed files and must not be inferred.

**Service dependencies**:

- `memcached` — external recipe referenced; service name and behavior require verification
- `redisio` — external recipe referenced for Redis setup
- `redisio::enable` — external recipe referenced for Redis enablement and start behavior
- Exact systemd service names are not available in the analyzed execution tree.

## Credentials

**Detection Summary**: One claimed hardcoded Redis credential is unverified; no credential finding is confirmed by the supplied structured analysis.

**Source**:

- **Provider**: Claimed hardcoded value in `cookbooks/cache/recipes/default.rb`; requires verification
- **URL**: None confirmed
- **Path**: None confirmed

### Redis authentication password

- **Variable(s)**: Claimed `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: Claimed `cookbooks/cache/recipes/default.rb`
- **Current storage**: Claimed hardcoded plaintext value; requires verification
- **Claimed current value**: `redis_secure_password_123`
- **Usage context**: Claimed Redis password authentication for a Redis instance on port `6379`; port and usage require verification
- **Migration handling**:
  - If confirmed, move the value to Ansible Vault.
  - Reference it through a vaulted variable such as `redis_password`.
  - Do not commit the plaintext value to the Ansible repository.

No secret-provider references are confirmed by the supplied structured analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `metadata.rb`, if present
- `/var/log/redis`, if confirmed by the recipe
- `/etc/redis/6379.conf`, only if the Ruby block target is confirmed

**Service endpoints to check**:

- Redis instance claimed on TCP port `6379`; verify before testing
- Memcached endpoint: Not established
- Unix sockets: None identified
- Network interface binding: Not specified

**Templates rendered**:

- None confirmed
- Render count: `0`

**Resources to verify**:

- `directory[/var/log/redis]`: `1`
- `ruby_block[fix_redis_config]`: `1`

**Configuration changes to verify**:

- Confirm whether Redis server definitions are configured.
- Confirm whether Redis listens on port `6379`.
- Confirm whether Redis password authentication is configured.
- Confirm whether `/etc/redis/6379.conf` exists.
- Confirm whether the five claimed replication-related directives are removed.
- Confirm the actual Memcached package, service, configuration, and listener settings.

## Pre-flight checks

### Local recipe and dependency verification

```bash
test -f cookbooks/cache/recipes/default.rb
test -f metadata.rb
grep -nE "include_recipe|directory|ruby_block|redisio|memcached" cookbooks/cache/recipes/default.rb
```

Verify the complete recipe and metadata before implementing any unconfirmed settings.

### Redis instance claimed as port 6379

The port and instance configuration require verification before these checks are treated as authoritative.

```bash
ss -tlnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN
```

If port `6379` is confirmed and password authentication is configured, test with a vaulted password:

```bash
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server
```

### Redis service

Identify the service name from the selected external Redis role before running:

```bash
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
systemctl is-active <redis-service-name>
```

### Redis configuration

Only run these checks if the recipe confirms `/etc/redis/6379.conf` as the target path:

```bash
test -f /etc/redis/6379.conf
grep -nE '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Verify the actual configured port, authentication settings, and any confirmed directive removals.

### Redis log directory

```bash
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis
```

Verify ownership, permissions, and recursive-creation behavior against the recipe source before asserting expected values.

### Memcached instance

The Memcached port, service name, configuration path, and health command are not established. After selecting and configuring the external Ansible equivalent, run its documented checks, including:

```bash
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
systemctl is-active <memcached-service-name>
ss -tlnp
```

Use only the verified service name, port, and configuration path from the selected dependency implementation.