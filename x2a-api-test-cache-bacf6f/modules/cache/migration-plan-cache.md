---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached` and `redisio` cookbooks. The local cookbook executes `cache::default`, creates `/var/log/redis`, assigns one Redis server configuration on port `6379`, applies a post-generation cleanup to `/etc/redis/6379.conf`, and invokes `redisio::enable`. The structured execution analysis confirms the directory resource, Ruby block, and missing external recipe references, but does not independently verify the Redis attributes, password, directory properties, Ruby block implementation, or metadata dependency constraints. Those details require source verification before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache service configured through the external `redisio` cookbook
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: `6379`
  - Key Config: Source-reported `requirepass` value `redis_secure_password_123`; source-reported `replicaservestaledata` value `nil`; post-processing reportedly removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority`
  - Verification status: The structured analysis confirms the Redis-related external recipe references but does not expose these attributes or Ruby block details. Verify them from the original recipe before implementation.

- **Memcached instance**: Memcached configuration delegated to the external `memcached` cookbook
  - Location/Path: Not specified by the local cookbook
  - Port/Socket: Not specified by the local cookbook
  - Key Config: Package, service name, bind address, configuration path, and endpoint are unavailable from the supplied execution tree
  - Verification status: Inspect the external `memcached` cookbook version used by the Chef deployment before creating equivalent Ansible configuration.

## File Structure

Only files shown in the supplied execution tree are listed.

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

No templates are shown in the execution tree.

**Attributes:**

```text
```

No attribute files are shown in the execution tree. The Redis configuration is reportedly assigned directly in `cookbooks/cache/recipes/default.rb`, but this requires source verification.

**Files:**

```text
```

No static files deployed by `cookbook_file` or `remote_file` are shown.

The supplied structured analysis does not include `metadata.rb`. Dependency constraints reported from the original plan therefore require verification against the Chef environment.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - Creates `directory[/var/log/redis]`.
   - Attempts to include the external `redisio` recipe.
   - Executes `ruby_block[fix_redis_config]`.
   - Attempts to include the external `redisio::enable` recipe.
   - The structured analysis confirms these resource and recipe references, but the external recipe implementations are not present in the supplied execution tree.

### `memcached` include

The recipe reportedly contains:

```ruby
include_recipe 'memcached'
```

The external recipe is unavailable in the execution tree.

Migration implications:

- Memcached installation and configuration are delegated to the external cookbook.
- No local Memcached package, configuration path, service name, port, socket, or template is available.
- Do not invent Memcached settings.
- Inspect the exact external cookbook version before implementing the Memcached role or its validation checks.

### Redis server attribute assignment

The original plan reports the following source configuration:

```ruby
node.default['redisio']['servers'] = [
  {
    'port' => '6379',
    'requirepass' => 'redis_secure_password_123',
    'replicaservestaledata' => nil
  }
]
```

This source-reported configuration contains one Redis server:

- **Redis server on port `6379`**
  - `port`: `6379`
  - `requirepass`: `redis_secure_password_123`
  - `replicaservestaledata`: `nil`

The structured analysis does not expose these attributes. Confirm them from `cookbooks/cache/recipes/default.rb` before migration. If confirmed, represent the server as one Redis configuration object and store the password in Ansible Vault or an approved secret backend.

### Directory resource: `/var/log/redis`

The structured analysis confirms:

```text
directory[/var/log/redis]
```

The original plan reports these properties:

- Path: `/var/log/redis`
- Owner: `redis`
- Group: `redis`
- Mode: `0755`
- Recursive: `true`

The structured analysis does not confirm the owner, group, mode, or recursive setting. Verify those properties from the recipe before implementation. The confirmed migration requirement is creation of `/var/log/redis`.

The Ansible equivalent, if the source properties are confirmed, is `ansible.builtin.file` with:

```yaml
path: /var/log/redis
state: directory
owner: redis
group: redis
mode: '0755'
recurse: true
```

### `redisio` include

The recipe reportedly contains:

```ruby
include_recipe 'redisio'
```

The external recipe is unavailable in the execution tree.

Migration implications:

- Redis package installation, user creation, configuration generation, service definition, and template rendering are delegated to `redisio`.
- The exact package name, configuration template, data directory, service name, and startup behavior are unavailable.
- Reproduce the behavior of the exact `redisio` cookbook version used by the Chef deployment rather than assuming generic Redis defaults.

### Ruby block: `fix_redis_config`

The structured analysis confirms:

```text
ruby_block[fix_redis_config]
```

The original plan reports that the block modifies:

```text
/etc/redis/6379.conf
```

It reportedly removes complete lines matching:

- `^replica-serve-stale-data.*$`
- `^replica-read-only.*$`
- `^repl-ping-replica-period.*$`
- `^client-output-buffer-limit.*$`
- `^replica-priority.*$`

The target file, matching expressions, file-existence behavior, and write behavior are not exposed by the structured analysis. Verify the Ruby block implementation before migration.

If confirmed, implement the cleanup with idempotent `ansible.builtin.replace` tasks after Redis configuration generation. Preserve the behavior that a missing configuration file does not create one. Do not add an unconditional service restart unless the target Redis implementation requires it.

### `redisio::enable` include

The recipe reportedly concludes with:

```ruby
include_recipe 'redisio::enable'
```

The external recipe is unavailable in the execution tree.

Migration implications:

- Redis is intended to be enabled and managed by the external cookbook.
- The exact service name and start behavior are unavailable.
- Apply `enabled: true` and the required running state only after confirming the target package and service layout.

## Dependencies

**External cookbook dependencies**:

- `memcached`, reportedly constrained to `~> 6.0`; verify against `metadata.rb`
- `redisio`, reportedly without a version constraint; verify against `metadata.rb`
- External recipe files reported as unavailable:
  - `memcached`
  - `redisio`
  - `redisio::enable`

**System package dependencies**:

- No local `package` resources are confirmed.
- No exact package names can be derived from the supplied execution tree.
- Do not assume package names such as `redis-server` or `memcached` without verifying the external cookbook and target operating system.

**Service dependencies**:

- Redis, through `redisio`; exact service name unavailable
- Memcached, through `memcached`; exact service name unavailable

## Credentials

**Detection Summary**: 1 hardcoded Redis credential reported in 1 recipe file; the structured analysis does not independently confirm the credential.

**Source**:

- **Provider**: Hardcoded in Chef recipe, according to the original plan
- **URL**: None detected
- **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext Chef attribute assignment
- **Value in source**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for the Redis instance on port `6379`
- **Verification status**: The supplied structured analysis does not expose recipe contents or credential findings. Confirm the value from the original recipe before migration.
- **Ansible migration**:
  - Store the confirmed value in Ansible Vault or an approved secret-management integration.
  - Do not commit the plaintext value to `defaults/main.yml`, `vars/main.yml`, or source-controlled generated configuration.
  - Render it into the Redis configuration with restrictive permissions.
  - Use the vaulted variable for authenticated Redis checks.

No data bag, Chef Vault, CyberArk, Conjur, environment-variable secret reference, TLS certificate reference, or database credential was identified in the supplied analysis.

## Checks for the Migration

**Files to verify**:

- `/var/log/redis`
- `/etc/redis/6379.conf`

The Redis data directory and exact log file are not specified by the supplied execution analysis.

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Memcached instance: endpoint not specified
- Unix sockets: none specified
- Network bind address: not specified

**Templates rendered**:

- No local templates are shown in the execution tree.
- Redis and Memcached templates, if any, are provided by missing external cookbooks and require dependency inspection.
- Local template render count: `0` confirmed.

**Resource and change behavior**:

- `directory[/var/log/redis]` is confirmed.
- `ruby_block[fix_redis_config]` is confirmed.
- The Redis configuration target and five removed directive families require source verification.
- Redis enablement is delegated to the missing `redisio::enable` recipe.
- No explicit service notification from the Ruby block is confirmed.

## Pre-flight checks

```bash
# Verify the Redis log directory
stat -c '%A %U:%G %n' /var/log/redis
# Expected after source verification: mode 755 and owner/group redis:redis

# Verify the Redis configuration file for the named Redis instance
test -f /etc/redis/6379.conf
echo $?
# Expected: 0 if the source-reported Redis configuration is confirmed

# Verify the Redis configuration does not contain removed directives.
# Run this check only after confirming the Ruby block expressions.
if grep -En '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
    echo "Unexpected removed Redis directives found"
    exit 1
else
    echo "Removed Redis directives are absent"
fi

# Verify the Redis service for the named Redis instance.
# Replace redis-service-name with the service name from the verified redisio implementation.
systemctl is-enabled redis-service-name
systemctl is-active redis-service-name

# Verify the named Redis instance is listening on TCP port 6379
ss -ltnp | grep ':6379'
# Expected: a Redis process listening on TCP port 6379

# Verify authenticated connectivity to the Redis instance
redis-cli -p 6379 -a '<retrieve-from-Ansible-Vault>' PING
# Expected: PONG

# Verify the Redis instance identity and port
redis-cli -p 6379 -a '<retrieve-from-Ansible-Vault>' INFO server | grep -E '^(redis_version|tcp_port):'
# Expected after source verification: tcp_port:6379

# Verify authentication is required for the named Redis instance
redis-cli -p 6379 PING
# Expected after source verification: an authentication-required error

# Verify the source-reported Redis configuration entries
grep -En '^(port|requirepass)' /etc/redis/6379.conf
# Expected after source verification: port 6379 and the configured password directive
```

### Memcached verification

The local cookbook does not specify a Memcached port, service name, package, configuration path, or socket. Inspect the external `memcached` cookbook version used by the Chef deployment before adding Memcached-specific checks.

Do not use an assumed Memcached port or service name as an equivalent of this cookbook without verified dependency information.