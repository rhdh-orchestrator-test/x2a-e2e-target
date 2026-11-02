---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook includes the external `memcached`, `redisio`, and `redisio::enable` recipes, but those dependency recipes are unavailable. The verified local execution tree contains one directory resource, `directory[/var/log/redis]`, and one Ruby block, `ruby_block[fix_redis_config]`. Redis port `6379`, Redis authentication, configuration paths, cleanup directives, package names, and service names are reported in the plan but are not confirmed by the available structured analysis and must be verified before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Reported recipe-local Redis configuration; details require verification from the complete recipe analysis or `redisio` dependency.
  - Location/Path: Reported `/etc/redis/6379.conf`; unverified
  - Port/Socket: Reported TCP `6379`; unverified
  - Key Config: Reported `requirepass` value `redis_secure_password_123` and `replicaservestaledata: nil`; unverified
  - Authentication: Reported hardcoded Redis password; unverified
  - Log directory: Reported `/var/log/redis`, owner `redis`, group `redis`, mode `0755`, recursive creation; only the directory resource itself is verified

- **Memcached**: External recipe inclusion is verified, but instance configuration is unavailable.
  - Location/Path: Not available
  - Port/Socket: Not specified by the verified local cookbook data
  - Key Config: Package, service name, bind address, port, memory allocation, and configuration path require inspection of the `memcached` dependency

## File Structure

Only the local recipe shown in the execution tree is included. Dependency recipes are referenced by the cookbook but are explicitly reported as missing and must not be invented.

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

The supplied execution tree contains one analyzed file:

```text
cookbooks/cache/recipes/default.rb
```

The following referenced recipe files are **not present** and therefore are not listed as usable cookbook files:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The verified execution tree specifies the following local recipe flow. Dependency recipe behavior is unavailable and is not expanded with assumed resources.

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe. The recipe file is missing from the supplied execution tree.
   - References the external `redisio` recipe. The recipe file is missing from the supplied execution tree.
   - Creates `directory[/var/log/redis]`. The resource existence is verified; owner, group, mode, and recursive settings are reported but require confirmation from the complete resource analysis.
   - Runs `ruby_block[fix_redis_config]`. The resource existence is verified; its target path and file transformations require confirmation from the complete block analysis.
   - Includes `redisio::enable`. The recipe file is missing from the supplied execution tree and its service behavior is unavailable.

### Dependency and configuration details requiring verification

The following details are reported by the original plan but are not confirmed by the available structured validation:

- Assignment of `node['redisio']['servers']`
- A single Redis server on port `6379`
- Redis configuration path `/etc/redis/6379.conf`
- Redis password `redis_secure_password_123`
- `replicaservestaledata` set to `nil`
- Removal of the following directives:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- Redis user and group creation
- Redis package, configuration, and service resources
- Memcached package, configuration, and service resources

These details must be confirmed before being implemented in Ansible. No `.each` loops are present in the verified local recipe analysis.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, version constraint not shown
- `redisio::enable`, referenced recipe within `redisio`

**System package dependencies**:

- No package resources are verified in the local recipe.
- Memcached and Redis package names are unavailable because the dependency recipes are missing.

**Service dependencies**:

- Memcached service: referenced but unavailable for inspection
- Redis service: referenced through `redisio` and `redisio::enable`; exact service name unavailable

## Credentials

**Detection Summary**: 0 credentials verified by the supplied structured analysis; 1 hardcoded Redis credential is reported but unverified.

**Source**:

- **Provider**: Reported hardcoded Chef recipe value; unverified
- **URL**: None detected
- **Path**: None detected
- **Data bags or vaults**: None detected
- **Environment variables**: None detected

### Redis authentication password

- **Variable**: Reported `node['redisio']['servers'][0]['requirepass']`
- **Literal value**: Reported `redis_secure_password_123`; unverified
- **Source file**: Reported `cookbooks/cache/recipes/default.rb`; file is verified, assignment is not
- **Current storage**: Reported plaintext Chef attribute assignment; unverified
- **Usage context**: Reported Redis server authentication for the instance on port `6379`; unverified

If confirmed, migrate the password to Ansible Vault rather than storing it in role defaults or task files:

```yaml
redis_requirepass: !vault |
  ...
```

No verified references to data bags, encrypted data bags, Chef Vault, Conjur, CyberArk, Vault URLs, TLS certificates, private keys, database connection strings, or environment-variable secrets were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis` — reported directory path, resource existence verified
- `/etc/redis/6379.conf` — reported Redis configuration path, unverified
- Memcached configuration path — unavailable
- Memcached log path — unavailable

**Service endpoints to check**:

- Redis TCP port `6379` — reported, unverified
- Memcached TCP port — not specified
- Unix sockets — none verified
- Network bind address — not specified

**Templates rendered**:

- None present or referenced in the supplied execution tree
- Render count: `0`

**Configuration transformations to verify**:

If the Redis configuration cleanup is confirmed, verify that `/etc/redis/6379.conf` contains no active lines beginning with:

```text
replica-serve-stale-data
replica-read-only
repl-ping-replica-period
client-output-buffer-limit
replica-priority
```

## Pre-flight checks

The following checks distinguish verified local resources from reported dependency behavior. Replace placeholders only after obtaining the missing dependency details.

### Local recipe and Redis log directory

```bash
# Verify the analyzed local recipe is present
test -f cookbooks/cache/recipes/default.rb

# Verify the reported Redis log directory
test -d /var/log/redis

# If ownership and permissions are confirmed by the complete resource analysis:
stat -c '%A %U %G %n' /var/log/redis
```

### Redis instance: port 6379

The Redis port and configuration path are reported but unverified.

```bash
# Run only after confirming the Redis configuration path
test -f /etc/redis/6379.conf

# Run only after confirming the Redis service name
systemctl status <redis-service-name>

# Run only after confirming that Redis listens on TCP port 6379
ss -ltnp | grep ':6379'

# Check the Redis process
pgrep -a redis
```

If the reported password and configuration are confirmed, validate authentication without exposing the password in shell history:

```bash
# Supply the vaulted password through a protected mechanism
redis-cli -p 6379 --askpass PING

# Expected result after authentication:
# PONG
```

If the reported cleanup behavior is confirmed, validate the directives:

```bash
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis replication directive remains"
  exit 1
fi
```

### Memcached instance

The local cookbook does not provide a verified memcached port, service name, configuration path, or bind address.

```bash
# Replace placeholders after inspecting the memcached dependency
systemctl status <memcached-service-name>
ss -ltnp | grep ':<memcached-port>'
```

Perform a memcached protocol check only after the dependency supplies the exact endpoint.

### General service and host checks

```bash
# Replace the service placeholder after dependency inspection
journalctl -u <redis-service-name> --no-pager -n 100

# Redis process and listening socket
ps -ef | grep '[r]edis'
lsof -iTCP:6379 -sTCP:LISTEN

# Disk space for the reported Redis paths
df -h /var/log/redis /etc/redis
```

### Migration implementation order

1. Obtain the complete behavior of the `memcached` dependency.
2. Obtain the complete behavior of the `redisio` and `redisio::enable` dependencies.
3. Confirm whether the local recipe assigns one Redis instance on port `6379`.
4. Confirm the Redis configuration path, authentication value, and cleanup directives.
5. Confirm the Redis user and group requirements for `/var/log/redis`.
6. Recreate only verified package, configuration, and service behavior in Ansible.
7. Store any confirmed Redis credential in Ansible Vault.
8. Validate every confirmed instance, endpoint, configuration file, and service individually.