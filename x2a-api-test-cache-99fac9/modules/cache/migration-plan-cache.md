---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The local recipe defines one Redis instance named **6379**, configured on TCP port `6379` with authentication, creates `/var/log/redis`, removes selected replication directives from `/etc/redis/6379.conf`, and enables Redis through `redisio::enable`. The referenced dependency recipes are not present in the supplied cookbook, so their package names, service names, ports, and configuration details must be obtained before implementing the Ansible migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance 6379**: Redis cache service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication is enabled with the configured `requirepass` value; `replicaservestaledata` is set to `nil`; selected replication-related directives are removed from the configuration.
  - Log Directory: `/var/log/redis`
  - Log Directory Owner/Group: `redis:redis`
  - Log Directory Mode: `0755`

- **Memcached instance**: Included through the external `memcached` recipe, but no instance name, port, socket, configuration path, or service settings are available because the dependency recipe is missing.
  - Location/Path: Not available
  - Port/Socket: Not available
  - Key Config: Must be obtained from the actual `memcached` dependency or defined explicitly as Ansible role variables. No values should be inferred from this cookbook.

The Redis password is present as plaintext in the source recipe as `redis_secure_password_123`. It must be migrated to Ansible Vault or an approved external secret-management system rather than copied into Ansible source.

## File Structure

```text
cookbooks/cache/
└── recipes/
    └── default.rb
```

### Recipes

```text
cookbooks/cache/recipes/default.rb
```

### Providers

```text
```

No provider files are shown or used.

### Templates

```text
```

No template files are shown or used.

### Attributes

```text
```

No attribute files are shown. Redis configuration is assigned directly in `cookbooks/cache/recipes/default.rb`.

### Files

```text
```

No static files are shown as deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The execution tree reports `memcached Recipe file not found`.
   - Replaces the missing dependency with an explicit Ansible task set or dedicated memcached role only after its package, service, configuration path, port, and memory settings are verified.
   - Assigns one Redis server definition to `node['redisio']['servers']`:
     - Instance name: `6379`
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - The execution tree reports `redisio Recipe file not found`.
   - Replaces the missing dependency with explicit Redis installation and configuration tasks after verifying the target platform’s package and service details.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - If `/etc/redis/6379.conf` exists, removes lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified configuration back to `/etc/redis/6379.conf`.
   - Does nothing when `/etc/redis/6379.conf` does not exist.
   - Includes `redisio::enable`.
   - The execution tree reports `redisio::enable Recipe file not found`.
   - Enables and starts the Redis service only after the actual service unit name is obtained from the Redis package or dependency.
   - Resource counts in the local recipe are:
     - `directory`: 1
     - `ruby_block`: 1
   - The local recipe contains no package resources, service resources, template resources, static file resources, or explicit restart notifications.

The Ansible implementation should preferably manage `/etc/redis/6379.conf` declaratively with a template or equivalent configuration task. If the in-place Chef behavior must be preserved, use explicit replacement tasks for the five directive families and notify the Redis service only when configuration changes.

## Dependencies

**External cookbook dependencies**:

- `memcached`, declared with version constraint `~> 6.0` in the supplied plan; verify the cookbook metadata before implementation.
- `redisio`, declared without a version constraint in the supplied plan; verify the cookbook metadata before implementation.
- The `memcached`, `redisio`, and `redisio::enable` dependency recipes are not present in the supplied execution tree.

**System package dependencies**:

- No package resources are present in the local recipe.
- No exact package names or versions are verified by the supplied cookbook.
- Obtain package names, versions, repositories, and installation requirements from the actual dependencies and target operating system before implementation.

**Service dependencies**:

- Redis service management is intended through `redisio::enable`, but the service unit name is not available.
- Memcached service management is not verifiable because the `memcached` recipe is missing.
- The Redis user and group must exist before `/var/log/redis` ownership is applied.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Chef recipe
  - **URL**: Not applicable
  - **Path**: `cookbooks/cache/recipes/default.rb`
  - **Mechanism**: Direct assignment to `node.default['redisio']['servers'][0]['requirepass']`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the Chef recipe
- **Literal value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for instance `6379` on TCP port `6379`
- **Configuration destination**: `/etc/redis/6379.conf`
- **Target storage**: Ansible Vault variable or approved external secret manager

No data bag, encrypted data bag, Chef Vault, Conjur, CyberArk, environment-variable secret reference, TLS certificate, private key, or database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis instance `6379`: TCP port `6379`
- Memcached: endpoint not determinable from the supplied execution tree
- Unix sockets: none specified
- Bind address: not specified

**Templates rendered**:

- No templates rendered by the local cookbook.

**Configuration transformations**:

For Redis instance `6379`, verify that `/etc/redis/6379.conf` contains the intended port and authentication settings and has no active lines beginning with:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

Before adding memcached-specific checks, obtain its actual service name, port, configuration path, and bind address from the dependency or target host.

## Pre-flight checks

```bash
# Confirm the Redis configuration file exists for instance 6379
test -f /etc/redis/6379.conf

# Confirm the Redis log directory for instance 6379
test -d /var/log/redis
stat -c '%A %U:%G %n' /var/log/redis

# Confirm the Redis user and group exist
getent passwd redis
getent group redis

# Identify the Redis service unit because the local cookbook does not provide its name
systemctl list-unit-files | grep -i redis

# Replace <redis-service-unit> with the verified Redis service unit
systemctl status <redis-service-unit>
systemctl is-enabled <redis-service-unit>
systemctl is-active <redis-service-unit>

# Verify that Redis instance 6379 is listening
ss -ltnp | grep ':6379'
netstat -ltnp 2>/dev/null | grep ':6379'
lsof -nP -iTCP:6379 -sTCP:LISTEN

# Inspect Redis configuration for instance 6379
grep -nE '^(requirepass|port|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Verify the five removed directive families are not active
! grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Test authenticated Redis connectivity for instance 6379
read -s REDIS_PASSWORD
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD

# Expected authenticated response:
# PONG

# Test that unauthenticated access is rejected when authentication is configured
redis-cli -h 127.0.0.1 -p 6379 PING

# Functional test for Redis instance 6379
read -s REDIS_PASSWORD
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" SET chef_migration_test ok
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" GET chef_migration_test
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" DEL chef_migration_test
unset REDIS_PASSWORD

# Check Redis logs for instance 6379
journalctl -u <redis-service-unit> --no-pager -n 100

# Identify whether a memcached service is present
systemctl list-unit-files | grep -i memcached

# Identify a memcached endpoint only after its dependency configuration is verified
ss -ltnp | grep -i memcached
```

Expected Redis results:

- Instance `6379` is active and enabled.
- TCP port `6379` is listening.
- Authenticated `PING` returns `PONG`.
- Unauthenticated access is rejected.
- `/var/log/redis` exists with owner `redis`, group `redis`, and mode `0755`.
- No active lines remain for the five specified replication-related directive families.
- Redis logs contain no configuration parse, authentication, bind, or log-permission errors.

Memcached checks must remain undefined until its actual package, service unit, configuration path, and endpoint are verified.