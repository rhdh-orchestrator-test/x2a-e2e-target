---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures Memcached and Redis through the external `memcached` and `redisio` cookbooks. The local recipe creates `/var/log/redis`, defines one Redis server on port `6379` with password authentication, removes five replication-related directives from `/etc/redis/6379.conf`, and enables Redis through `redisio::enable`. The dependency recipes are unavailable, so their packages, service names, templates, configuration paths, and Memcached endpoint cannot be confirmed from the supplied execution tree.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached instance included through the external `memcached` cookbook
  - Location/Path: Dependency-owned; not determinable from the supplied execution tree
  - Port/Socket: Not determinable from the supplied execution tree
  - Key Config: Package, service name, configuration path, listen address, and endpoint require verification from the `memcached` dependency

- **Redis server on port 6379**: Redis cache instance configured through the external `redisio` cookbook
  - Location/Path: `/etc/redis/6379.conf`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Redis password authentication enabled with `requirepass`; password is currently hardcoded as `redis_secure_password_123`; Redis service enabled through `redisio::enable`
  - Configuration cleanup removes:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

The supplied recipe contains no collection iterations or `.each` loops. It defines one Redis server with port `6379`.

## File Structure

The execution tree reports one analyzed recipe file. Dependency recipes are unavailable and are not listed as local files.

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

`metadata.rb` was inspected for service description and cookbook dependencies, but it is not included in the execution-tree file list. No local provider, template, static file, or attribute file was supplied.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The `memcached` dependency recipe is unavailable.
   - Its package, service name, configuration path, listen address, and port must be obtained before migration.
   - Assigns one Redis server definition:
     - Port: `6379`
     - Authentication password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - The `redisio` dependency recipe is unavailable.
   - The dependency is expected to install and configure Redis, create required users and groups, deploy `/etc/redis/6379.conf`, and manage the Redis service; these behaviors require verification.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - If the file exists, removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - If the file does not exist, the cleanup block performs no action.
   - Includes `redisio::enable` after configuration cleanup.
   - The `redisio::enable` dependency recipe is unavailable; its exact service unit name requires verification.
   - Directly visible local resources:
     - `directory[/var/log/redis]`: 1
     - `ruby_block[fix_redis_config]`: 1

2. **memcached** (`external cookbook: memcached`):
   - Included by `cookbooks/cache/recipes/default.rb`.
   - Dependency recipe unavailable.
   - Package installation, configuration deployment, service management, and endpoint are unknown.
   - No local `.each` iterations are present.

3. **redisio** (`external cookbook: redisio`):
   - Included by `cookbooks/cache/recipes/default.rb`.
   - Dependency recipe unavailable.
   - Expected to configure one Redis server on port `6379` using the locally assigned server definition.
   - Package name, Redis service name, data directory, log file, user/group creation, and template behavior require verification.
   - No local `.each` iterations are present.

4. **enable** (`external cookbook: redisio::enable`):
   - Included after Redis configuration cleanup.
   - Enables the Redis service at boot.
   - Exact service unit name and enablement implementation require verification.

## Dependencies

**External cookbook dependencies**:

- `memcached`, reported version constraint `~> 6.0`; verify against `metadata.rb`
- `redisio`, reported without a version constraint; verify against `metadata.rb`

**System package dependencies**:

- No local `package` resources are present.
- No package names can be confirmed from the supplied execution tree.
- Packages installed by `memcached` and `redisio` require dependency-source verification.
- No package names are invented or treated as confirmed.

**Service dependencies**:

- Memcached service: included through `memcached`; service name unavailable
- Redis service: enabled through `redisio::enable`; exact service unit name unavailable
- Redis TCP endpoint: port `6379`

## Credentials

**Detection Summary**: 1 credential identified by source-level inspection in 1 file; credential confirmation is not present in the supplied structured validation data.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Value**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis server on port `6379`

The Ansible migration should store this value in Ansible Vault, an AAP credential, or another approved secret-management system. It must not be placed in committed defaults or exposed in task output. Tasks handling the secret should use `no_log: true`.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, environment-variable secret reference, TLS certificate, private key, or embedded database connection string was detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

Dependency-owned paths requiring verification:

- Redis data directory
- Redis log file
- Memcached configuration file
- Memcached log file

**Service endpoints to check**:

- Redis TCP port `6379`
- Memcached endpoint: unavailable; obtain from the `memcached` dependency
- Unix sockets: none specified
- Network interfaces: none specified

**Templates rendered**:

- Local templates: 0
- Dependency templates: unknown; inspect the unavailable `memcached` and `redisio` cookbooks

## Pre-flight checks

### Redis server on port 6379

```bash
# Discover the Redis service unit if it is not named redis
systemctl list-unit-files --type=service | grep -Ei 'redis'

# Check the discovered Redis service status and enablement
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>

# Verify Redis is listening on TCP port 6379
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'

# Verify the Redis configuration file
test -f /etc/redis/6379.conf
ls -l /etc/redis/6379.conf

# Verify the configured port
grep -E '^port[[:space:]]+6379$' /etc/redis/6379.conf

# Verify password authentication without printing the password
grep -E '^requirepass[[:space:]]+' /etc/redis/6379.conf >/dev/null \
  && echo "Redis requirepass is configured"

# Verify the five cleanup directives are absent
! grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Verify authenticated access
redis-cli -p 6379 -a "$REDIS_PASSWORD" --no-auth-warning PING
# Expected output: PONG

# Verify unauthenticated access is rejected
redis-cli -p 6379 PING
# Expected result: authentication error

# Check recent Redis logs using the discovered service unit
journalctl -u <redis-service-unit> --since "-15 minutes" --no-pager
```

### Redis log directory

```bash
# Verify the directory exists
test -d /var/log/redis
ls -ld /var/log/redis

# Verify expected ownership and mode
stat -c '%U %G %a %n' /var/log/redis
# Expected: redis redis 755 /var/log/redis

# Verify the Redis user can write to the directory
sudo -u redis test -w /var/log/redis
```

### memcached

```bash
# Discover the Memcached service unit
systemctl list-unit-files --type=service | grep -Ei 'memcached'

# Check the discovered service status and enablement
systemctl status <memcached-service-unit>
systemctl is-enabled <memcached-service-unit>

# Obtain the configured Memcached endpoint from the dependency implementation
# Do not assume a package, configuration path, service name, or port.

# After the endpoint is confirmed, verify it with the dependency-specific check.
```

