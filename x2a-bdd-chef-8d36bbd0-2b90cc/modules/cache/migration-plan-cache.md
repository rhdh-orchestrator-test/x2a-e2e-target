---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the `memcached` instance using the `memcached_instance[memcached]` custom resource on TCP and UDP port `11211`, and one Redis instance on port `6379`. Memcached uses 64 MB of memory, listens on all interfaces, and is started and enabled. Redis uses authentication, a PID directory at `/run/redis`, a log directory at `/var/log/redis`, and removes five replication-related directives from `/etc/redis/6379.conf`. The `redisio` and `redisio::enable` recipe implementations, along with the Memcached custom-resource provider, were unavailable in the supplied execution tree; their package and exact service-unit behavior must be supplied by the migration dependencies.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Resource: `memcached_instance[memcached]`
  - State: Started and enabled
  - Memory allocation: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Worker threads: `node['memcached']['threads']`; no default value is defined in the supplied attributes
  - Experimental options: `[]`
  - Additional CLI options: `[]`
  - Ulimit: `1024`
  - Service user: `service_user`, resolved by the Memcached custom-resource provider
  - Configured logging attribute: `/var/log/memcached`; the supplied recipe does not directly create this path

- **redis-6379**: Redis cache service configured on port `6379`
  - Instance count: One Redis server entry
  - Port: `6379`
  - Authentication: Enabled
  - Password: `redis_secure_password_123`
  - PID directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Log directory owner: `redis`
  - Log directory group: `redis`
  - Log directory mode: `0755`
  - Log directory creation: Recursive
  - Service state: Enabled through `redisio::enable`
  - Post-configuration cleanup: Removes selected replication-related directives from `/etc/redis/6379.conf`
  - Replication: No replica hostnames, replica instances, or replication endpoints configured

The Redis configuration removes these directives when present:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

The `memcached_instance[memcached]` custom resource is used, but no provider file was supplied in the execution tree or directory listing.

**Templates:**
```text
```

No templates are rendered by the listed recipes.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

The unavailable `redisio` and `redisio::enable` recipe files are not listed because they were not present in the supplied directory or execution tree.

## Module Explanation

The cookbook performs operations in the following order.

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe with `include_recipe 'memcached'`.
   - Sets the Redis server configuration before Redis setup:
     - Port: `6379`
     - Password: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
     - Base PID directory: `/run/redis`
   - Includes the Redis dependency recipe with `include_recipe 'redisio'`.
   - The supplied execution tree reports that the `redisio` recipe file is unavailable.
   - Creates `directory[/var/log/redis]` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]`.
   - If `/etc/redis/6379.conf` exists, reads the complete file, removes lines beginning with the five specified replication-related directives, and writes the modified contents back.
   - Includes the Redis enable recipe with `include_recipe 'redisio::enable'`.
   - The supplied execution tree reports that the `redisio::enable` recipe file is unavailable.
   - Declares one `directory` resource, one `ruby_block` resource, and three `include_recipe` operations.
   - Does not directly declare the `group[redis]` resource mentioned by structural analysis. The migration must ensure that the `redis` group exists through the Redis dependency implementation or an explicit prerequisite.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Creates `memcached_instance[memcached]`.
   - Configures memory to `64` MB.
   - Configures TCP and UDP ports to `11211`.
   - Binds to `0.0.0.0`.
   - Configures a maximum of `1024` connections.
   - Configures a maximum object size of `1m`.
   - Uses the resolved `service_user` service account.
   - Passes the configured worker-thread value from `node['memcached']['threads']`.
   - Passes empty experimental and additional CLI option lists.
   - Configures a ulimit of `1024`.
   - Starts the Memcached service.
   - Enables the Memcached service at boot.
   - No `.each` loops are present, and no collection expansion is required.

3. **Redis dependency recipe** (`redisio`; implementation unavailable):
   - Must install and configure the Redis implementation.
   - Must create the Redis service account and `redis` group as required.
   - Must configure the single Redis server entry on port `6379`.
   - Must use `/run/redis` as the base PID directory.
   - Must configure Redis authentication using the vaulted migration credential.
   - Exact package names, generated configuration paths, templates, and service-unit names are unavailable and must be taken from the replacement Redis dependency implementation.

4. **Redis enable recipe** (`redisio::enable`; implementation unavailable):
   - Must enable the Redis service at boot.
   - Must preserve the Redis service state expected by the original cookbook.
   - The exact Redis service unit name is unavailable and must be taken from the replacement Redis dependency implementation.

### Attributes

Memcached defaults:

- `node['memcached']['memory'] = 64`
- `node['memcached']['port'] = 11211`
- `node['memcached']['udp_port'] = 11211`
- `node['memcached']['listen'] = '0.0.0.0'`
- `node['memcached']['maxconn'] = 1024`
- `node['memcached']['max_object_size'] = '1m'`
- `node['memcached']['experimental_options'] = []`
- `node['memcached']['extra_cli_options'] = []`
- `node['memcached']['ulimit'] = 1024`
- `node['memcached']['logfilepath'] = '/var/log/memcached'`
- `node['memcached']['version'] = nil`
- `node['memcached']['threads']` has no default in the supplied attributes

Redis configuration:

- `node['redisio']['servers']` contains exactly one entry:
  - `port`: `'6379'`
  - `requirepass`: `'redis_secure_password_123'`
  - `replicaservestaledata`: `nil`
- `node['redisio']['base_piddir'] = '/run/redis'`

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- No `package` resources are explicitly declared in the supplied recipes.
- Package installation is delegated to the unavailable `memcached_instance` provider and unavailable `redisio` recipes.
- No package name can be verified from the supplied execution tree; package names must be obtained from the dependency implementations rather than invented.

**Service dependencies**:

- Memcached service, started and enabled by `memcached_instance[memcached]`
- Redis service, intended to be enabled by `redisio::enable`; the exact service name is unavailable

## Credentials

**Detection Summary**: 1 hardcoded credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe source
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext attribute assignment
- **Value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the Redis instance listening on port `6379`
- **Ansible migration**: Store the value in Ansible Vault or an AAP credential/secret variable. Do not place it in plaintext role defaults, inventory, or committed variable files.

No data bags, encrypted data bags, Chef Vault items, CyberArk references, Conjur references, AWS Secrets Manager references, environment-variable secret references, TLS certificate paths, private keys, or database connection strings with embedded credentials were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- `/var/log/memcached`, if created by the Memcached dependency
- Memcached service configuration generated by the custom resource
- Redis service configuration generated by the Redis dependency

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the bind address specified by the Redis dependency
- Unix sockets: None configured by the supplied recipes

**Templates rendered**:

- No templates are rendered by the supplied recipes.
- Render count: `0`

**Iterations**:

- No `.each` loops are present.
- The Redis server configuration contains exactly one entry: port `6379`.

## Pre-flight checks

Run these checks after the Ansible role completes.

### Service status

```bash
systemctl status memcached
systemctl status redis
```

Replace `redis` with the exact Redis unit name supplied by the replacement Redis implementation if it differs from `redis.service`.

### Memcached instance: `memcached`

```bash
# Confirm the Memcached process is running
pgrep -a memcached

# Confirm TCP port 11211 is listening
ss -tlnp | grep ':11211'

# Confirm UDP port 11211 is listening
ss -ulnp | grep ':11211'

# Confirm Memcached is bound to all interfaces
ss -tlnp | grep '0.0.0.0:11211'

# Query Memcached statistics
printf "stats\r\nquit\r\n" | nc 127.0.0.1 11211

# Verify the configured memory and connection limits
printf "stats settings\r\nquit\r\n" | nc 127.0.0.1 11211 | \
  grep -E 'maxbytes|maxconns'

# Verify the service is enabled
systemctl is-enabled memcached
```

Expected results include TCP and UDP listeners on port `11211`, a TCP bind of `0.0.0.0:11211`, and statistics showing the configured resource limits.

### Redis instance: `redis-6379`

```bash
# Confirm the Redis process is running
pgrep -a redis

# Confirm Redis is listening on port 6379
ss -tlnp | grep ':6379'

# Verify the Redis PID directory
ls -ld /run/redis

# Verify the Redis log directory and ownership
ls -ld /var/log/redis
stat -c '%U %G %a %n' /var/log/redis

# Verify Redis configuration exists
test -f /etc/redis/6379.conf

# Confirm removed replication directives are absent
grep -nE \
  '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf
```

The final `grep` must produce no output.

Use the Redis password from the Ansible Vault-backed variable:

```bash
read -r REDIS_PASSWORD
redis-cli -h 127.0.0.1 -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD
```

Expected output:

```text
PONG
```

Verify that unauthenticated access is rejected:

```bash
redis-cli -h 127.0.0.1 -p 6379 PING
```

The request should fail with an authentication error.

### Redis configuration validation

```bash
grep -nE \
  '^(port|requirepass|dir|pidfile|replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

systemctl is-enabled redis
```

Replace `redis` with the exact Redis unit name supplied by the replacement implementation if necessary.

### Logs

```bash
journalctl -u memcached --no-pager -n 100
journalctl -u redis --no-pager -n 100
```

If Redis writes a dedicated log file under `/var/log/redis`, verify the exact path from the generated Redis configuration.

### Resource and connectivity checks

```bash
# Confirm Memcached TCP connectivity
nc -zv 127.0.0.1 11211

# Confirm Redis TCP connectivity
nc -zv 127.0.0.1 6379

# Confirm Redis log-directory capacity
df -h /var/log/redis

# Confirm Redis runtime-directory capacity
df -h /run/redis
```

The migration is complete only when the `memcached` instance is enabled and reachable on TCP and UDP port `11211`, the `redis-6379` instance is enabled and reachable on port `6379`, Redis authentication succeeds with the vaulted password, and all five unwanted replication-related directives are absent from `/etc/redis/6379.conf`.