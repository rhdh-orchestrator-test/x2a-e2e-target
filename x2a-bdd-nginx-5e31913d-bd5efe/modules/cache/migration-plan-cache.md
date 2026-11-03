---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures one Redis instance on TCP port `6379` and includes external `memcached` and `redisio` cookbook dependencies. The supplied execution tree contains only `cookbooks/cache/recipes/default.rb`; dependency recipes, templates, attributes, providers, and static files are unavailable. The recipe creates `/var/log/redis`, configures Redis authentication through a hardcoded password, removes selected replication directives from `/etc/redis/6379.conf`, and includes `redisio::enable`. The Redis password must be moved to Ansible Vault during migration. Memcached settings cannot be determined from the supplied cookbook.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`; no Unix socket configured
  - Key Config:
    - Authentication enabled with `requirepass`
    - Source password: `redis_secure_password_123`
    - `replicaservestaledata` is assigned `nil`
    - Redis log directory: `/var/log/redis`
    - Log directory owner/group: `redis:redis`
    - Log directory mode: `0755`
    - Service enablement delegated to unavailable `redisio::enable`
    - Selected replication directives are removed from the Redis configuration

- **Memcached**: External dependency included by the recipe; no configured instance details are available
  - Location/Path: Not specified
  - Port/Socket: Not specified
  - Key Config:
    - Included recipe: `memcached`
    - Package name, configuration path, listen address, port, service name, and templates are unavailable
    - Do not assume conventional Memcached settings until the external `memcached` cookbook is inspected

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No attribute files are shown in the supplied directory listing or execution tree.

### Files

```text
```

No static files are deployed by `cookbook_file` or `remote_file` resources.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - The `memcached` recipe file is not present in the supplied execution tree.
   - No Memcached package, configuration, service, port, or template can be determined from this cookbook.
   - The Ansible migration should use a dependency role or task include only after the external cookbook is inspected.

2. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Creates the Redis log directory `/var/log/redis`.
   - Uses owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Resource count: one `directory` resource.
   - Ansible equivalent:

     ```yaml
     - name: Create Redis log directory
       ansible.builtin.file:
         path: /var/log/redis
         state: directory
         owner: redis
         group: redis
         mode: '0755'
         recurse: true
     ```

3. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Assigns the Redis server collection with exactly one configured item:

     ```ruby
     node.default['redisio']['servers'] = [
       {
         'port' => '6379',
         'requirepass' => 'redis_secure_password_123',
         'replicaservestaledata' => nil,
       }
     ]
     ```

   - Configures Redis instance **port 6379**:
     - `port`: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - The supplied recipe does not contain a loop over this collection; it assigns the collection for consumption by the external `redisio` cookbook.
   - Store the password in Ansible Vault rather than embedding it in a task or template.
   - Preserve the intended absence of the `replica-serve-stale-data` setting unless the replacement Redis role requires an explicit value.

4. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `redisio` recipe.
   - The `redisio` recipe file is not present in the supplied execution tree.
   - The dependency is expected to install and configure Redis, but the available source does not identify:
     - Redis package name
     - Redis package version
     - Repository configuration
     - Service unit name
     - Configuration template
     - Installation version
   - The known Redis configuration supplied by this cookbook is port `6379`, password authentication, and `replicaservestaledata: nil`.

5. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Executes `ruby_block[fix_redis_config]`.
   - Operates on `/etc/redis/6379.conf`.
   - If the file does not exist, performs no action.
   - If the file exists, reads the complete file and removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Resource count: one `ruby_block` resource.
   - The Chef recipe does not explicitly notify or restart Redis after this block.
   - Ansible should use scoped `ansible.builtin.lineinfile` or `ansible.builtin.replace` tasks and should preserve the conditional behavior when the configuration file is absent.
   - A Redis restart or reload handler should be notified only when configuration changes, according to the behavior required by the replacement Redis role.

6. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include `redisio::enable`.
   - The `redisio::enable` recipe file is not present in the supplied execution tree.
   - The migrated role must enable and start the Redis service for port `6379`.
   - The exact service name is unknown and must be obtained from the external `redisio` implementation.
   - Do not assume `redis`, `redis-server`, `redis@6379`, or another service name without verification.
   - The available Chef recipe contains no explicit service resource.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint shown
- Dependency recipe files are not present in the supplied execution tree.

**System package dependencies**:

- No `package` resources are present in the available recipe.
- The Memcached package name is not specified.
- The Redis package name is not specified.
- The Redis package version is not specified.
- Repository configuration and additional Redis packages are not specified.
- Obtain these values from the external `memcached` and `redisio` implementations or define them explicitly as migration inputs.

**Service dependencies**:

- Redis enablement is delegated to the unavailable `redisio::enable` recipe.
- The exact Redis systemd service name is not available.
- Memcached service details are unavailable.

## Credentials

**Detection Summary**: 1 hardcoded credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: `cookbooks/cache/recipes/default.rb`; ultimately expected in `/etc/redis/6379.conf`

### Redis authentication password

- **Variable**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute assignment
- **Usage context**: Redis `requirepass` authentication for the Redis instance listening on TCP port `6379`
- **Ansible handling**:
  - Move the value to Ansible Vault.
  - Reference the vaulted variable from the Redis configuration template or role variable.
  - Do not commit the literal password to the Ansible repository.
  - Rotate the password during migration if it has been used outside a test environment.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, HashiCorp Vault lookup, AWS Secrets Manager lookup, or environment-variable secret references were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`
- Redis data directory: not specified
- Memcached configuration: not specified
- Memcached log path: not specified

**Service endpoints to check**:

- Redis instance on TCP port `6379`
- Redis Unix socket: none configured or referenced
- Memcached endpoint: not specified; inspect the external dependency before testing

**Templates rendered**:

- None; no templates are shown or rendered by the supplied execution tree.

**Configuration transformations**:

The `ruby_block[fix_redis_config]` resource removes these directives from `/etc/redis/6379.conf`:

- `replica-serve-stale-data`
- `replica-read-only`
- `repl-ping-replica-period`
- `client-output-buffer-limit`
- `replica-priority`

## Pre-flight checks

### Redis instance on port 6379

```bash
# Replace with the exact service name discovered from the redisio dependency.
systemctl status <actual-redis-service-name>
systemctl is-enabled <actual-redis-service-name>
systemctl is-active <actual-redis-service-name>

test -f /etc/redis/6379.conf
grep -E '^(port|requirepass)' /etc/redis/6379.conf

! grep -E '^replica-serve-stale-data' /etc/redis/6379.conf
! grep -E '^replica-read-only' /etc/redis/6379.conf
! grep -E '^repl-ping-replica-period' /etc/redis/6379.conf
! grep -E '^client-output-buffer-limit' /etc/redis/6379.conf
! grep -E '^replica-priority' /etc/redis/6379.conf
```

Validate connectivity and authentication:

```bash
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_ANSIBLE_VAULT>' PING
```

Expected result:

```text
PONG
```

Verify unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result: an authentication-required error rather than `PONG`.

Check Redis server information and port:

```bash
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_ANSIBLE_VAULT>' INFO server
redis-cli -p 6379 -a '<REDIS_PASSWORD_FROM_ANSIBLE_VAULT>' CONFIG GET port
```

Expected port value:

```text
6379
```

Check the TCP listener:

```bash
ss -tlnp | grep ':6379'
netstat -tlnp 2>/dev/null | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN
```

Verify the Redis log directory:

```bash
ls -ld /var/log/redis
stat -c '%U %G %a %n' /var/log/redis
```

Expected values:

```text
Owner: redis
Group: redis
Mode: 0755
```

Check Redis logs using the service name discovered from the external dependency:

```bash
journalctl -u <actual-redis-service-name> --no-pager -n 100
```

The exact Redis log file is not defined in the available cookbook. Inspect the installed service configuration before checking file-based logs.

### Memcached dependency

Memcached is included, but no Memcached instance, port, service name, or configuration path is defined by the supplied cookbook. Inspect the external `memcached` cookbook before executing service checks.

If the dependency is confirmed to configure the conventional TCP port `11211`, use:

```bash
systemctl status memcached
ss -tlnp | grep ':11211'
printf 'version\r\n' | nc 127.0.0.1 11211
```

These checks are conditional. Port `11211` is not established by the supplied cookbook.