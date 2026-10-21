---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache service consisting of one Redis instance and an externally provided Memcached instance. The entry recipe includes Memcached, defines one Redis server on port `6379`, creates `/var/log/redis`, includes the external Redis configuration recipe, removes five replication-related directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. The Memcached and Redis implementation recipes are external and unavailable in the analyzed cookbook, so their package names, service names, templates, and Memcached port require verification from the selected Ansible roles. The Redis password reported in the source must be stored in Ansible Vault.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server**
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config:
    - Authentication is configured through `requirepass`.
    - The source reports the password as `redis_secure_password_123`; this value must be replaced with an Ansible Vault variable.
    - `replicaservestaledata` is set to `nil`.
    - Log directory: `/var/log/redis`
    - Log directory owner: `redis`
    - Log directory group: `redis`
    - Log directory mode: `0755`
    - Five directives are removed after Redis configuration:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`
    - Service enablement is requested through `redisio::enable`.

- **Memcached**
  - Location/Path: Not available in the analyzed cookbook
  - Port/Socket: Not specified in the analyzed cookbook
  - Key Config:
    - The external `memcached` recipe is included before Redis setup.
    - Package name, service name, configuration path, bind address, and port require verification from the selected Ansible Memcached role.
    - No Memcached values should be inferred from this cookbook.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

No provider files are shown in the execution tree.

**Templates:**
```text
```

No templates are shown as rendered or referenced.

**Attributes:**
```text
```

No attribute files are shown. The Redis server collection is assigned directly in `cookbooks/cache/recipes/default.rb`.

**Files:**
```text
```

No static files are shown as deployed.

The following external recipes are referenced but are not present in the cookbook file tree:

- `memcached`
- `redisio`
- `redisio::enable`

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The Memcached recipe is unavailable in the analyzed execution tree.
   - The Memcached role or task file must execute before Redis setup.
   - Assigns one Redis server definition to `node['redisio']['servers']`:
     - Port: `6379`
     - Authentication attribute: `requirepass`
     - Reported source password: `redis_secure_password_123`
     - Replica stale-data setting: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe after creating the Redis log directory.
   - The Redis role or task file must consume the single Redis instance definition and generate `/etc/redis/6379.conf`.
   - Executes `ruby_block['fix_redis_config']` after Redis configuration:
     - Checks whether `/etc/redis/6379.conf` exists.
     - Reads the file when present.
     - Removes complete lines beginning with:
       - `replica-serve-stale-data`
       - `replica-read-only`
       - `repl-ping-replica-period`
       - `client-output-buffer-limit`
       - `replica-priority`
     - Writes the modified content back to `/etc/redis/6379.conf`.
     - Makes no change when the file does not exist.
   - Includes the external `redisio::enable` recipe after configuration cleanup.
   - Requests that Redis be enabled at boot.
   - Resource counts:
     - `directory`: 1
     - `ruby_block`: 1

The Redis server definition should be represented in Ansible as one instance:

```yaml
redisio_servers:
  - port: 6379
    requirepass: "{{ vault_redis_password }}"
    replicaservestaledata: null
```

The reported password, resource properties, Ruby block behavior, and exact Redis attributes require source-level verification because they are not present in the supplied structured analysis.

## Dependencies

**External cookbook dependencies**:

- `memcached`, reported with version constraint `~> 6.0`; verify against `metadata.rb`
- `redisio`, reported without a version constraint; verify against `metadata.rb`

**System package dependencies**:

- No package resources are present in the analyzed execution tree.
- Package names must be obtained from the selected Ansible Memcached and Redis implementations.
- No package name, including `memcached` or `redis-server`, is asserted as installed by this cookbook.

**Service dependencies**:

- Memcached configuration and service behavior are delegated to the external `memcached` recipe.
- Redis installation and configuration are delegated to the external `redisio` recipe.
- Redis boot enablement is delegated to `redisio::enable`.
- Exact service names are unavailable from the analyzed cookbook and must be obtained from the selected Ansible roles.

## Credentials

**Detection Summary**: 1 credential reported in 1 file; source-level verification is required because the supplied structured analysis does not include credential data.

**Source**:
  - **Provider**: Hardcoded in Chef source, according to the migration plan; migrate to Ansible Vault
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported as a hardcoded plaintext value
- **Reported current value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the Redis instance listening on TCP port `6379`
- **Migration handling**:
  - Create an encrypted variable named `vault_redis_password`.
  - Reference it from the Redis server definition.
  - Do not commit the plaintext value to role defaults, task files, group variables, or templates.
  - Use `no_log: true` on tasks that could expose the password.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificate references, private keys, API keys, or database connection strings were reported.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`

**Service endpoints to check**:

- Redis server: TCP port `6379`
- Memcached: port not specified by the analyzed cookbook
- Unix sockets: none specified
- Network interface binding: not specified

**Configuration directives to verify**:

- `/etc/redis/6379.conf` uses port `6379`.
- Redis authentication is configured without exposing the password.
- The following directives are absent from `/etc/redis/6379.conf` after cleanup:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- None shown; render count: `0`

**Static files deployed**:

- None shown; deployment count: `0`

## Pre-flight checks

```bash
# Verify the Redis log directory
test -d /var/log/redis
stat -c '%A %U %G %n' /var/log/redis

# Expected directory values:
# Permissions: drwxr-xr-x
# Owner: redis
# Group: redis
# Path: /var/log/redis

# Verify the Redis configuration file
test -f /etc/redis/6379.conf
grep -E '^port ' /etc/redis/6379.conf

# Verify the Redis port
ss -ltnp | grep ':6379'
nc -zv 127.0.0.1 6379

# Use the vaulted password through an environment variable.
# Do not place the password directly in shell history.
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING

# Expected result:
# PONG

# Verify Redis functionality
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET migration_check success
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET migration_check
redis-cli -p 6379 -a "$REDIS_PASSWORD" DEL migration_check

# Expected results:
# OK
# "success"
# (integer) 1

# Verify that the five unwanted directives were removed
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis replication directives remain"
  exit 1
else
  echo "Redis cleanup directives are absent"
fi

# Replace <redis-service-name> with the service name provided by the selected Redis role.
systemctl status <redis-service-name>
systemctl is-enabled <redis-service-name>
ps aux | grep '[r]edis'
journalctl -u <redis-service-name> --no-pager -n 100
```

Memcached is a separately named configured instance. After selecting the external Ansible Memcached role, verify its documented service name and port:

```bash
systemctl status <memcached-service-name>
systemctl is-enabled <memcached-service-name>
ss -ltnp | grep '<memcached-port>'
```

Do not substitute a Memcached service name or port that is not provided by the selected implementation.