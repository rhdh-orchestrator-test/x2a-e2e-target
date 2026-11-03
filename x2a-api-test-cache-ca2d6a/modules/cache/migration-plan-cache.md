---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook is intended to configure cache services through the external `memcached` and `redisio` cookbooks. The only analyzed local recipe is `cookbooks/cache/recipes/default.rb`. It attempts to include Memcached, creates `/var/log/redis`, configures a source-declared Redis instance on port `6379`, applies a source-declared cleanup to `/etc/redis/6379.conf`, and attempts to enable Redis. The `memcached`, `redisio`, and `redisio::enable` recipes are not present in the analyzed execution tree. Resource properties, Redis attributes, credential details, and Ruby block behavior require verification against the source files or external cookbook implementations.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Source-declared Redis server configured through the external `redisio` cookbook.
  - Location/Path: `/etc/redis/6379.conf`; source-declared log directory `/var/log/redis`
  - Port/Socket: TCP `6379`; no Unix socket or bind address is specified in the analyzed source
  - Key Config: Source declares `requirepass` and `replicaservestaledata`; the exact attribute values and generated configuration require source-level verification. A Ruby block is reported as targeting five Redis directives for removal, but its exact behavior is not confirmed by the structured analysis.
  - Service: Intended to be enabled through `redisio::enable`; the service name and startup behavior are unverified.

- **Memcached dependency**: The local recipe attempts to include the external `memcached` cookbook, but its recipe is missing from the analyzed tree.
  - Location/Path: Not available
  - Port/Socket: Not available
  - Key Config: Package, service, configuration path, bind address, memory limit, and authentication settings must be obtained from the external cookbook before migration.

## File Structure

The analyzed execution tree contains one local recipe. External dependency recipes are reported as missing and are not included.

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

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - The execution tree reports `memcached Recipe file not found`.
   - No local Memcached package, service, configuration, or endpoint implementation is available.
   - Creates the source-declared directory `/var/log/redis`; ownership, group, mode, and recursive behavior require verification from the recipe source.
   - Assigns the source-declared Redis server configuration for port `6379`, including a `requirepass` value and `replicaservestaledata`; the exact assignment and credential value require source-level verification.
   - Attempts to include the external `redisio` recipe.
   - The execution tree reports `redisio Recipe file not found`.
   - Executes `ruby_block[fix_redis_config]`.
   - The structured analysis confirms the Ruby block resource exists but does not verify its target path, conditional behavior, regular expressions, write-back behavior, or service notification. The source-level plan claims that it edits `/etc/redis/6379.conf` and removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Any Ansible replacement task must be ordered after Redis configuration generation and must be based on verified source behavior.
   - Attempts to include `redisio::enable`.
   - The execution tree reports `redisio::enable Recipe file not found`; the exact service name and enablement behavior require verification from the external cookbook.

There are no analyzed `.each` loops or collection iterations. The source-level plan claims one Redis server item on port `6379`, but that count requires verification because the structured analysis does not include the Redis attribute assignment.

## Dependencies

**External cookbook dependencies**:

- `memcached ~> 6.0`
- `redisio` with no version constraint

**System package dependencies**:

- No local `package` resources are analyzed.
- Package names for Memcached and Redis are not available from the supplied execution tree and must be obtained from the external cookbook implementations.
- Do not invent package names in the Ansible migration.

**Service dependencies**:

- Memcached service behavior depends on the missing external `memcached` recipe.
- Redis installation and configuration depend on the missing external `redisio` recipe.
- Redis enablement depends on the missing `redisio::enable` recipe.
- Exact Redis and Memcached service names are unverified.

## Credentials

**Detection Summary**: One Redis credential is claimed by the source-level migration plan, but credential detection is not represented in the supplied structured analysis. Verify the finding against `cookbooks/cache/recipes/default.rb`.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe, according to the source-level plan
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: Source-level plan identifies `node['redisio']['servers'][0]['requirepass']`; exact variable assignment requires verification.
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as a hardcoded plaintext Chef attribute assignment; verify in the recipe source.
- **Usage context**: Intended for Redis client authentication through the `requirepass` configuration directive.
- **Migration handling**:
  - Store the password in Ansible Vault, for example as `redis_password`.
  - Do not place it in public role defaults or plaintext tasks.
  - Protect generated Redis configuration files containing the password.
  - Avoid exposing the password through task output or logs.

No data bag, encrypted data bag, Chef Vault item, Conjur variable, CyberArk secret, TLS certificate, private key, or database connection string is identified in the supplied content.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis` — source-declared path requiring resource-property verification
- `/etc/redis/6379.conf` — source-declared path requiring Ruby block verification

**Service endpoints to check**:

- Redis TCP port `6379`, if confirmed by the Redis attribute assignment
- No Unix socket confirmed
- No bind address or network interface confirmed
- Memcached endpoint must be obtained from the external `memcached` cookbook

**Templates rendered**:

- No local templates are present.
- No template render counts are available.

**Static files deployed**:

- No `cookbook_file` or `remote_file` resources are present in the analyzed tree.

## Pre-flight checks

### Redis instance on port 6379

Confirm the Redis service name from the external `redisio` implementation before running service checks:

```bash
systemctl status <confirmed-redis-service-name>
systemctl is-enabled <confirmed-redis-service-name>
systemctl is-active <confirmed-redis-service-name>
```

Check the source-declared endpoint:

```bash
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'
ps aux | grep '[r]edis'
```

If authentication is confirmed and the migrated secret is available:

```bash
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
```

Expected result:

```text
PONG
```

Verify configuration only after confirming the configuration path and directives in the source:

```bash
grep -E '^(port|requirepass|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

If the source confirms the reported cleanup behavior, verify that the following directives are absent:

```bash
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Verify the source-declared port if confirmed:

```bash
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf
```

Do not print the complete configuration file because it may contain the Redis password.

If the source confirms `/var/log/redis` and its expected properties:

```bash
ls -ld /var/log/redis
stat -c '%U %G %a %n' /var/log/redis
```

Inspect the configured Redis log path without broadly displaying the configuration:

```bash
grep -E '^[[:space:]]*logfile[[:space:]]+' /etc/redis/6379.conf
```

Then inspect the confirmed log and service:

```bash
tail -n 100 <confirmed-redis-log-file>
journalctl -u <confirmed-redis-service-name> --no-pager -n 100
```

### Memcached dependency

The Memcached recipe is missing, so no endpoint or service command can be verified from this cookbook. After inspecting the external `memcached ~> 6.0` cookbook, add checks using its confirmed values:

```bash
systemctl status <confirmed-memcached-service-name>
systemctl is-enabled <confirmed-memcached-service-name>
systemctl is-active <confirmed-memcached-service-name>
ss -ltnp | grep ':<confirmed-memcached-port>'
```

Do not assume the Memcached package name, service name, port, configuration path, bind address, memory limit, or authentication settings from the supplied source.