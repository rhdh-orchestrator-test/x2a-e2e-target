---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook invokes the external `memcached`, `redisio`, and `redisio::enable` recipes. The local execution tree confirms one `directory` resource for `/var/log/redis`, one `ruby_block` resource, and no local templates, providers, attributes, or files. The source plan reports one Redis instance on port `6379`, Redis authentication, and removal of five replication-related directives from `/etc/redis/6379.conf`; these Redis details and the reported password require verification against `cookbooks/cache/recipes/default.rb` before migration. Memcached configuration, packages, ports, and service details are unavailable because its dependency recipe is not present.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Reported Redis instance configured through the external `redisio` cookbook; source details require verification.
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: `6379/TCP`
  - Key Config:
    - Reported authentication password: `redis_secure_password_123`; migrate to Ansible Vault or an approved secret backend.
    - Reported `replicaservestaledata` value: `nil`.
    - Reported post-configuration removal of:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`
    - All Redis settings above require confirmation from the recipe source before implementation.

  - Log directory: `/var/log/redis`
  - Reported owner: `redis`
  - Reported group: `redis`
  - Reported mode: `0755`
  - Reported recursive creation: `true`
  - Ownership, mode, and recursive behavior require source verification.

- **Memcached dependency instance**: Intended cache service invoked through the external `memcached` cookbook.
  - Location/Path: Not available from the analyzed files.
  - Port/Socket: Not specified.
  - Key Config: Package, service name, configuration path, and runtime settings must be obtained from the external `memcached` cookbook version used by the Chef environment.
  - Recipe status: Referenced as `memcached`, but the recipe is not present in the local execution tree.

## File Structure

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
None
```

**Templates:**
```text
None
```

**Attributes:**
```text
None
```

**Files:**
```text
None
```

The following referenced recipes are external dependencies and are not local cookbook files:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The local execution tree reports that the `memcached` recipe file is unavailable.
   - Any Memcached package, service, configuration, port, or template behavior must be obtained from the external dependency before migration.
   - Assigns one reported Redis server definition through `node.default['redisio']['servers']`.
   - The reported Redis definition contains:
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - These Redis server-definition values are not confirmed by the supplied structured validation summary and must be verified in the recipe source.
   - Creates `directory[/var/log/redis]`.
   - The reported directory settings are:
     - Owner: `redis`
     - Group: `redis`
     - Mode: `0755`
     - Recursive creation: `true`
   - These directory properties require source verification.
   - Includes the external `redisio` recipe.
   - The local execution tree reports that the `redisio` recipe file is unavailable.
   - The missing dependency may install Redis, render `/etc/redis/6379.conf`, and create the Redis service; those actions are not confirmed in the local recipe.
   - Executes `ruby_block[fix_redis_config]`.
   - The reported Ruby block operates on `/etc/redis/6379.conf` when the file exists.
   - The reported cleanup removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - The target path and cleanup directives require confirmation from the recipe source.
   - Includes the external `redisio::enable` recipe as the final invocation.
   - The local execution tree reports that the `redisio::enable` recipe file is unavailable.
   - The exact Redis service unit and enablement behavior must be obtained from the external dependency.

   - Confirmed local resource count:
     - `directory`: 1
     - `ruby_block`: 1
     - `include_recipe` calls: `memcached`, `redisio`, `redisio::enable`
   - No `.each` loops are present in the supplied execution tree.
   - No local providers, templates, attributes, or files are present.
   - No `group['redis']` resource is confirmed by the supplied structured analysis.

## Dependencies

**External cookbook dependencies**:

- `memcached`, constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- No package names are confirmed by the local cookbook.
- Package installation is delegated to the unavailable external dependency recipes.
- Obtain and verify package names from the exact `memcached` and `redisio` cookbook versions before implementation.

**Service dependencies**:

- Memcached service management is delegated to the external `memcached` recipe.
- Redis installation and configuration are delegated to the external `redisio` recipe.
- Redis enablement and startup are delegated to `redisio::enable`.
- Exact service unit names are not available from the local execution tree.

## Credentials

**Detection Summary**: 1 reported credential in 1 file; the credential finding requires confirmation against the recipe source.

**Source**:
  - **Provider**: Hardcoded Chef node attribute, as reported
  - **URL**: None detected
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext value in the recipe
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the reported instance on port `6379`
- **Migration handling**:
  - Verify the credential exists in the source recipe.
  - Store it in Ansible Vault, AAP credential injection, or an approved external secret provider.
  - Do not commit the plaintext value in defaults, variables, templates, or tasks.
  - Use the secret variable when rendering or configuring Redis authentication.
  - Prefer `REDISCLI_AUTH` for `redis-cli` validation to avoid exposing the password in command arguments.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, database credentials, API keys, or token files were confirmed.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf` — reported Redis path; verify source usage
- `/var/log/redis` — confirmed local directory resource path
- Memcached configuration path — unavailable until the external recipe is inspected
- Redis service unit or init script — unavailable until the external recipe is inspected
- Redis data directory — not specified

**Service endpoints to check**:

- Redis: `6379/TCP`, reported and requiring source verification
- Memcached: Not specified; obtain the port from the external `memcached` cookbook
- Unix sockets: None explicitly confirmed

**Templates rendered**:

- Local templates: 0
- External `redisio` templates: Unknown; inspect the dependency
- External `memcached` templates: Unknown; inspect the dependency

## Pre-flight checks

### Source and dependency verification

```bash
test -f cookbooks/cache/recipes/default.rb
grep -nE "memcached|redisio|6379|requirepass|replicaservestaledata|fix_redis_config|/etc/redis/6379.conf|/var/log/redis" \
  cookbooks/cache/recipes/default.rb
```

Verify the exact external cookbook versions and inspect their package, template, configuration, and service resources before implementing the Ansible role.

### Redis instance: reported port 6379

Verify the reported configuration file:

```bash
test -f /etc/redis/6379.conf
```

Verify the reported port if the source confirms this instance:

```bash
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' /etc/redis/6379.conf
```

Check the listening endpoint:

```bash
ss -ltnp | grep ':6379'
```

Verify authentication without exposing the password:

```bash
export REDISCLI_AUTH='<retrieve-from-approved-secret-store>'
redis-cli -p 6379 PING
unset REDISCLI_AUTH
```

Expected output:

```text
PONG
```

Check unauthenticated access behavior:

```bash
redis-cli -p 6379 PING
```

The command should fail or report that authentication is required when authentication is enabled.

If the source confirms the reported cleanup behavior, verify the five directives are absent:

```bash
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

Expected output: no matches.

Verify the reported log directory properties:

```bash
stat -c '%A %U %G %n' /var/log/redis
test -d /var/log/redis
```

Expected result, if confirmed by the source:

```text
drwxr-xr-x redis redis /var/log/redis
```

Check Redis processes:

```bash
pgrep -a redis-server
```

Identify and verify the actual service unit supplied by `redisio`:

```bash
systemctl list-unit-files | grep -Ei 'redis'
```

Then run the status check for the verified unit:

```bash
systemctl status <verified-redis-service-unit>
```

### Memcached dependency instance

Do not guess the Memcached package, service name, configuration path, or port. First inspect the external `memcached` cookbook and record its exact values. Then run checks using those verified values:

```bash
systemctl status <verified-memcached-service-unit>
test -f <verified-memcached-config-path>
ss -ltnp | grep ':<verified-memcached-port>'
```

### Log destination

If Redis is configured with a file log, verify the configured destination:

```bash
grep -E '^[[:space:]]*logfile[[:space:]]+' /etc/redis/6379.conf
```

If the verified Redis service uses journald, inspect it with the exact service unit:

```bash
journalctl -u <verified-redis-service-unit> --no-pager -n 50
```