---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook is a cache module whose structured execution tree contains one local recipe, `cookbooks/cache/recipes/default.rb`, and references the external `memcached`, `redisio`, and `redisio::enable` recipes. The dependency implementations and recipe-content analysis are unavailable, so Redis settings, Memcached settings, package names, service names, templates, credentials, and exact configuration paths cannot be verified from the supplied structured analysis. The reported Redis configuration on port `6379`, `/etc/redis/6379.conf`, `/var/log/redis`, replication-directive cleanup, and hardcoded password require confirmation from the recipe source before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Reported Redis instance on port 6379 — unverified**
  - Location/Path: Reported as `/etc/redis/6379.conf`; requires recipe-content verification
  - Port/Socket: Reported TCP port `6379`; requires recipe-content verification
  - Key Config: The original plan reports password authentication, `/var/log/redis`, and removal of five replication-related directives. These settings are not present in the supplied structured analysis and must be verified before implementation.

- **Memcached instance — configuration unavailable**
  - Location/Path: Not identified
  - Port/Socket: Not identified
  - Key Config: The external `memcached` recipe is missing from the execution tree. Package, configuration, service, and endpoint settings must be obtained from the dependency source.

## File Structure

Only the local recipe is shown in the supplied execution tree. The included dependency recipes are explicitly marked as not found and must not be listed as local executable files.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
None identified.
```

**Templates:**
```text
None identified.
```

**Attributes:**
```text
None identified.
```

**Files:**
```text
None identified.
```

## Module Explanation

The cookbook performs operations in the following execution order. Details not present in the structured analysis are explicitly marked as unverified.

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` recipe file was not found in the supplied execution tree.
   - The dependency's package name, configuration path, service name, port, and templates must be obtained from the dependency source.
   - The original plan reports Redis server configuration assignment, but the structured analysis does not confirm the attribute values.
   - The original plan reports one Redis server on port `6379` with password authentication; these values require recipe-content verification.
   - The execution tree contains `directory[/var/log/redis]`.
   - The directory owner, group, mode, and recursive behavior are not available in the supplied structured analysis.
   - Includes the external `redisio` recipe.
   - The `redisio` recipe file was not found in the supplied execution tree.
   - The dependency is expected to provide Redis installation and configuration, but its package, templates, configuration paths, and service resources must not be inferred.
   - Contains `ruby_block[fix_redis_config]`.
   - The original plan reports that this resource modifies `/etc/redis/6379.conf` and removes the following directives:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The reported path and directive behavior are not present in the supplied structured analysis and require recipe-content verification.
   - Includes the external `redisio::enable` recipe.
   - The `redisio::enable` recipe file was not found in the supplied execution tree.
   - Resolve the actual Redis service name and enablement behavior from the RedisIO dependency before implementing the Ansible service task.
   - No `.each` loops are shown in the supplied execution tree. No loop expansion is required.

### Execution Order Summary

1. Include external `memcached`.
2. Assign Redis configuration if confirmed by recipe-content analysis.
3. Execute `directory[/var/log/redis]`.
4. Include external `redisio`.
5. Execute `ruby_block[fix_redis_config]`.
6. Include external `redisio::enable`.

## Dependencies

**External cookbook dependencies**:

- `memcached` — dependency identified; version constraint not available in the supplied structured analysis
- `redisio` — dependency identified; version constraint not available in the supplied structured analysis

**System package dependencies**:

- Not determinable from the local execution tree.
- Package names must be obtained from the missing `memcached` and `redisio` dependency implementations.
- No package name should be hardcoded until verified.

**Service dependencies**:

- Memcached service: service name unavailable
- Redis service: service name unavailable; managed through the missing `redisio::enable` implementation

## Credentials

**Detection Summary**: 0 credentials independently verified in the supplied structured analysis.

**Source**:

- **Provider**: None verified
- **URL**: None
- **Path**: None

### Reported Redis authentication password — unverified

- **Variable(s)**: Reported as `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: Reported as `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as hardcoded plaintext; requires recipe-content verification
- **Usage context**: Reported as Redis password authentication for the candidate Redis instance on port `6379`
- **Migration requirement**: If confirmed, store the password in Ansible Vault or an AAP credential. Do not commit it to role defaults, group variables, or templates.

No data bags, encrypted data bags, Chef Vault calls, external secret integrations, TLS certificate references, database credentials, API keys, or token references were identified by the supplied structured analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- Candidate `/var/log/redis` directory, if confirmed by recipe-content analysis
- Candidate `/etc/redis/6379.conf`, if confirmed by recipe-content analysis
- Dependency-managed Redis files, after inspecting the `redisio` source
- Dependency-managed Memcached files, after inspecting the `memcached` source

**Service endpoints to check**:

- Candidate Redis TCP port: `6379`, pending verification
- Memcached port: not specified
- Unix sockets: none identified

**Templates rendered**:

- Local cookbook: none identified; render count `0`
- `memcached` dependency templates: unavailable; render count cannot be determined
- `redisio` dependency templates: unavailable; render count cannot be determined

**Restart/reload behavior**:

- The structured analysis identifies `ruby_block[fix_redis_config]` but does not provide its implementation.
- Determine whether Redis configuration changes require restart or reload from the dependency role and verified recipe content.
- Use an Ansible handler only when the resulting configuration changes.

## Pre-flight checks

### Candidate Redis instance on port 6379

The following checks apply only if the reported Redis configuration is confirmed by recipe-content analysis and the dependency service name is resolved:

```bash
# Verify the candidate Redis configuration file
test -f /etc/redis/6379.conf

# Verify the candidate Redis log directory
test -d /var/log/redis
stat -c '%A %U:%G %n' /var/log/redis

# Replace with the service name obtained from the redisio dependency
systemctl status <redis-service-name>

# Verify the reported Redis endpoint
ss -ltnp | grep ':6379'

# Retrieve authentication securely from AAP or Ansible Vault
export REDISCLI_AUTH='<retrieve-securely>'
redis-cli -p 6379 PING
# Expected: PONG

# Verify the candidate configuration cleanup, if confirmed
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected: no matching lines if the reported cleanup behavior is verified
```

Do not place any confirmed Redis password in shell history or committed configuration.

### Memcached instance

The local execution tree does not define a Memcached port, service name, configuration path, or package. After inspecting the external dependency, replace the placeholders with verified values:

```bash
# Replace with the verified dependency service name
systemctl status <memcached-service-name>

# Replace with the verified dependency port
ss -ltnp | grep ':<memcached-port>'

# Confirm service logs
journalctl -u <memcached-service-name> --no-pager -n 100
```

The migration is complete only after the missing dependency implementations and the local recipe contents have been inspected, and all reported Redis and Memcached settings have been verified.