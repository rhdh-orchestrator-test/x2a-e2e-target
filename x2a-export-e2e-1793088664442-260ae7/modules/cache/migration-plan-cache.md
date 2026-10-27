---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services using the external `memcached` and `redisio` cookbooks. The supplied recipe defines one Redis instance on port **6379**, enables Redis authentication with a hardcoded password, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and enables Redis. The external dependency recipes are not present in the supplied execution tree, so their package names, templates, service names, Memcached settings, and exact Redis installation details must be obtained separately.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Authenticated Redis cache service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with `requirepass`; `replicaservestaledata` set to `nil`; replication-related directives removed by a configuration workaround
  - Log Directory: `/var/log/redis`
  - Log Directory Owner/Group: `redis:redis`
  - Log Directory Mode: `0755`

- **Memcached**: External cache service included through the `memcached` cookbook
  - Location/Path: Not available in the supplied execution tree
  - Port/Socket: Not specified
  - Key Config: Package, configuration path, service name, port, startup parameters, and authentication settings are defined by the unavailable external dependency

No Redis replicas or additional Redis ports are configured in the supplied recipe.

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

No provider files are shown in the execution tree.

### Templates

```text
```

No templates are shown as rendered.

### Attributes

```text
```

No attribute files are shown. The Redis server collection is assigned directly in `cookbooks/cache/recipes/default.rb`.

### Files

```text
```

No static files deployed by `cookbook_file` or `remote_file` are shown.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The external Memcached recipe is not present in the supplied execution tree.
   - Memcached package names, configuration files, service names, listening port, and startup parameters cannot be determined from this cookbook alone.
   - Sets `node.default['redisio']['servers']` to one Redis server definition:
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Includes the external `redisio` recipe.
   - The external Redis installation and configuration resources are not present in the supplied execution tree.
   - Modifies `/etc/redis/6379.conf` when the file exists.
   - Removes complete lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Does not explicitly notify or restart Redis after modifying the configuration.
   - Includes the external `redisio::enable` recipe.
   - Enables the Redis service associated with port `6379`; the exact service unit name must be determined from the external dependency or target operating system.

### External Recipes in Execution Order

2. **`memcached`** (`external dependency; source unavailable):
   - Provides the intended Memcached installation and service behavior.
   - Its package names, configuration files, service name, port, and startup parameters are not available from the supplied files.

3. **`redisio`** (`external dependency; source unavailable):
   - Provides the intended Redis installation and configuration behavior.
   - Its package names, templates, service names, and installation paths are not available from the supplied files.

4. **`redisio::enable`** (`external dependency; source unavailable):
   - Enables the Redis service associated with the configured port `6379`.
   - The exact systemd unit name is not available from the supplied files.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint shown

**System package dependencies**:

- No package resources are visible in the supplied execution tree.
- Package installation is expected to be performed by the external `memcached` and `redisio` cookbooks.
- No exact package names are confirmed by the supplied cookbook.

**Service dependencies**:

- Redis instance configured for TCP port `6379`
- Memcached service provided by the external `memcached` cookbook
- Exact systemd unit names are not available from the supplied files

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext value
- **Current value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the instance listening on port `6379`
- **Ansible handling**:
  - Store the password in Ansible Vault, such as a variable named `redis_password`.
  - Do not commit the plaintext value to `group_vars`, `host_vars`, or a template.
  - Use the vaulted variable when rendering `/etc/redis/6379.conf`.
  - Verify that unauthenticated commands are rejected and authenticated commands succeed.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, private keys, API tokens, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis/`
- `/etc/redis/6379.conf`

The Redis configuration file is expected to be created by the external `redisio` dependency and then modified by the `fix_redis_config` workaround.

**Service endpoints to check**:

- Redis instance on port `6379`
- Memcached endpoint: not specified in the supplied cookbook
- Unix sockets: none specified
- Network bind address: not specified

**Templates rendered**:

- None

**Redis configuration directives to verify**:

The following directives must not remain in `/etc/redis/6379.conf`:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

Redis authentication must be configured using the password stored in Ansible Vault.

## Pre-flight checks

```bash
# Redis instance: verify the configuration file exists
test -f /etc/redis/6379.conf

# Redis instance: verify the log directory and ownership
stat -c '%A %U %G %n' /var/log/redis
# Expected:
# drwxr-xr-x redis redis /var/log/redis

# Redis instance: identify installed and active Redis service units
systemctl list-units --type=service --all | grep -E 'redis|redis-server'

# Redis instance: verify that TCP port 6379 is listening
ss -ltnp | grep ':6379'
# Expected: a Redis process listening on TCP port 6379

# Redis instance: verify the configured port
grep -E '^[[:space:]]*port[[:space:]]+6379([[:space:]]|$)' \
  /etc/redis/6379.conf

# Redis instance: authenticate and verify a successful ping
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_ANSIBLE_VAULT>' PING
# Expected: PONG

# Redis instance: verify unauthenticated access is rejected
redis-cli -p 6379 PING
# Expected: an authentication error such as:
# NOAUTH Authentication required.

# Redis instance: verify removed directives are absent
grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
# Expected: no output

# Redis instance: validate configuration using the installed Redis binary
redis-server /etc/redis/6379.conf --test-memory 2

# Redis instance: inspect service status and recent logs
systemctl status <REDIS_SERVICE_UNIT>
journalctl -u <REDIS_SERVICE_UNIT> --no-pager -n 100
# Replace <REDIS_SERVICE_UNIT> with the unit installed by redisio.
```

### Memcached Checks

The supplied cookbook does not define a Memcached port or service unit. Obtain both values from the external `memcached` cookbook before migration validation.

```bash
# Memcached instance: verify the service is enabled and running
systemctl status <MEMCACHED_SERVICE_UNIT>

# Memcached instance: verify the configured TCP port is listening
ss -ltnp | grep ':<MEMCACHED_PORT>'

# Memcached instance: verify a version request succeeds
printf 'version\r\n' | nc 127.0.0.1 <MEMCACHED_PORT>
```

Replace `<MEMCACHED_SERVICE_UNIT>` and `<MEMCACHED_PORT>` with values obtained from the external dependency configuration.