---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis server configuration on port `6379`. Memcached is started and enabled through the `memcached_instance` custom resource with 64 MB of memory, TCP and UDP port `11211`, a `0.0.0.0` listen address, 1,024 maximum connections, a `1m` maximum object size, and a provider-defined service user. Redis is configured with password authentication, PID directory `/run/redis`, log directory `/var/log/redis`, and a post-configuration cleanup that removes selected replication-related directives from `/etc/redis/6379.conf`. The referenced `redisio` recipes and the `memcached_instance` provider are unavailable from the supplied execution tree; package names, service names, provider behavior, and generated Memcached configuration paths must therefore be recovered before implementation.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache instance
  - Location/Path: Provider-defined configuration path; unavailable in the supplied execution tree
  - Port/Socket: TCP `11211`, UDP `11211`
  - Listen address: `0.0.0.0`
  - Memory: `64` MB
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Threads: Attribute-backed; no concrete value is defined in the supplied attributes
  - Ulimit: `1024`
  - User: `service_user`
  - Experimental options: Empty list
  - Extra CLI options: Empty list
  - Actions: `start`, `enable`

- **redis-6379**: Redis server configuration represented by port `6379`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: `6379`
  - Password authentication: `requirepass`, sourced from a vaulted Ansible variable in the migration
  - PID directory: `/run/redis`
  - Log directory: `/var/log/redis`
  - Service account: `redis`
  - Replica-related value: `replicaservestaledata: nil`
  - Enablement: Requested through the unavailable `redisio::enable` recipe

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

The execution tree identifies `memcached_instance[memcached]` as a custom resource but does not provide a provider path. No provider file is included in the supplied execution tree.

**Templates:**
```text
```

No templates are rendered by the analyzed recipes.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by the analyzed recipes.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Assigns one Redis server configuration item for port `6379`.
   - Assigns `/run/redis` as the Redis PID directory.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Removes selected replication-related directives from `/etc/redis/6379.conf` when the file exists.
   - Includes the unavailable `redisio::enable` recipe.
   - No `.each` loops are present; the Redis server collection contains exactly one item, port `6379`.

   Redis configuration assigned by the recipe:
   ```ruby
   node.default['redisio']['servers'] = [
     {
       'port' => '6379',
       'requirepass' => 'redis_secure_password_123',
       'replicaservestaledata' => nil,
     }
   ]
   ```

   Redis PID directory assignment:
   ```ruby
   node.default['redisio']['base_piddir'] = '/run/redis'
   ```

   Redis recipe dependency:
   - Included recipe: `redisio`
   - Status: Recipe file unavailable in the supplied execution tree
   - Do not infer package names, templates, service names, directories, or provider behavior.
   - Recover the original `redisio` cookbook or treat the Redis implementation as an unresolved dependency.

   Redis log directory resource:
   - Resource: `directory[/var/log/redis]`
   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive: `true`
   - The `redis` account must exist before this task runs; its creation is expected from the unavailable `redisio` implementation.

   Redis configuration cleanup resource:
   - Resource: `ruby_block[fix_redis_config]`
   - File: `/etc/redis/6379.conf`
   - Runs only when the file exists.
   - Removes complete lines matching:
     ```text
     ^replica-serve-stale-data.*$
     ^replica-read-only.*$
     ^repl-ping-replica-period.*$
     ^client-output-buffer-limit.*$
     ^replica-priority.*$
     ```
   - The Ansible implementation should use `ansible.builtin.replace` or a controlled configuration template.
   - Matching lines must be removed rather than replaced with empty values.
   - Redis should be notified or restarted only when the resulting file changes, unless the recovered `redisio` implementation specifies another handler.
   - This cleanup must run after the Redis recipe generates `/etc/redis/6379.conf`.

   Redis enablement:
   - Included recipe: `redisio::enable`
   - Status: Recipe file unavailable in the supplied execution tree
   - Implement service enablement only after recovering the service name created by the Redis installation.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes `memcached_instance[memcached]`.
   - Requests actions `start` and `enable`.
   - Configures memory to `64` MB.
   - Configures TCP port `11211` and UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Runs under `service_user`.
   - Sets maximum object size to `1m`.
   - Leaves threads attribute-backed because no concrete value is defined in the supplied attributes.
   - Keeps experimental options empty.
   - Keeps extra CLI options empty.
   - Sets the service ulimit to `1024`.
   - No `.each` loops are present; the custom resource is invoked exactly once for the named instance `memcached`.
   - The provider path is unavailable. Recover the provider before documenting exact package names, configuration paths, systemd unit behavior, or service-user creation.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint shown

**System package dependencies**:

- No concrete package resource is present in the supplied executable recipes.
- The Memcached package is hidden inside the unavailable `memcached_instance` provider.
- Redis package names are hidden inside the unavailable `redisio` recipes.
- Exact package names must be recovered from the original cookbook implementations and must not be inferred.

**Service dependencies**:

- Memcached is started and enabled through `memcached_instance[memcached]`.
- Redis is expected to be enabled through the unavailable `redisio::enable` recipe.
- The exact Redis service unit name is unavailable.
- The Redis service account `redis` must exist before `/var/log/redis` is created.
- Redis configuration generation must complete before `/etc/redis/6379.conf` is cleaned.

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded recipe attribute assignment
- **Usage context**: Redis `requirepass` authentication for the Redis server configured on port `6379`
- **Migration handling**: Store the password in Ansible Vault or an approved AAP credential/secret-management integration. Do not commit the literal value to plaintext Ansible variables or place it directly in shell history.

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secrets, TLS certificates, private keys, database connection strings, or additional hardcoded credentials were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/run/redis`
- `/var/log/redis`
- Recovered Memcached configuration path from the `memcached_instance` provider

**Service endpoints to check**:

- Memcached instance `memcached`, TCP `0.0.0.0:11211`
- Memcached instance `memcached`, UDP `0.0.0.0:11211`
- Redis instance `redis-6379`, TCP port `6379`
- Redis PID directory `/run/redis`
- Redis log directory `/var/log/redis`

**Templates rendered**:

- No templates rendered by the supplied execution tree: `0`
- Redis and Memcached templates must be added to validation only after the unavailable cookbook implementations are recovered.

## Pre-flight checks

### Memcached instance `memcached`

```bash
# Service status; confirm the recovered provider-defined unit if different
systemctl status memcached

# Verify the Memcached process and service user
pgrep -a memcached
ps -o pid,user,args -C memcached

# Verify TCP listening on 0.0.0.0:11211
ss -ltnp | grep ':11211'

# Verify UDP listening on 0.0.0.0:11211
ss -lunp | grep ':11211'

# Basic Memcached protocol check
printf "version\r\n" | nc -w 2 127.0.0.1 11211

# Expected response includes:
# VERSION <version>

# Verify service enablement
systemctl is-enabled memcached

# Verify the recovered provider-defined configuration path
test -f /path/recovered-from-memcached-provider
```

Confirm that instance `memcached`:

- Runs under `service_user`.
- Listens on TCP and UDP port `11211`.
- Uses 64 MB of memory.
- Allows 1,024 connections.
- Uses maximum object size `1m`.
- Uses ulimit `1024`.
- Has empty experimental and extra CLI option lists.

### Redis instance `redis-6379`

```bash
# Verify the Redis configuration file
test -f /etc/redis/6379.conf

# Verify port and authentication configuration
grep -E '^(port|requirepass)' /etc/redis/6379.conf

# Verify cleaned directives are absent
if grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf; then
  echo "Unexpected replication directives remain"
  exit 1
else
  echo "Redis configuration cleanup passed"
fi

# Verify Redis PID and log directories
ls -ld /run/redis
ls -ld /var/log/redis

# Verify ownership and permissions
stat -c '%U:%G %a %n' /var/log/redis

# Verify Redis is listening on port 6379
ss -ltnp | grep ':6379'

# Replace redis-server with the recovered redisio service unit if necessary
systemctl status redis-server
systemctl is-enabled redis-server

# Use the vaulted password through an environment variable
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 PING
# Expected result:
# PONG

# Authenticated Redis information check
REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli -p 6379 INFO server | \
  grep -E 'redis_version|tcp_port|process_id'
```

### Redis configuration cleanup

```bash
# Confirm the target file exists
test -f /etc/redis/6379.conf

# Confirm all cleaned directives are absent
grep -Eq '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf \
  && { echo "Unexpected replication directives remain"; exit 1; } \
  || echo "Redis configuration cleanup passed"
```

### Logs and service diagnostics

```bash
# Redis log directory contents
find /var/log/redis -maxdepth 1 -type f -ls

# Redis service journal; replace the unit name if recovery identifies another name
journalctl -u redis-server --no-pager -n 100

# Memcached service journal
journalctl -u memcached --no-pager -n 100
```

The exact Redis and Memcached log filenames are unavailable from the supplied cookbook analysis. Use service journals unless the recovered providers identify exact log files.