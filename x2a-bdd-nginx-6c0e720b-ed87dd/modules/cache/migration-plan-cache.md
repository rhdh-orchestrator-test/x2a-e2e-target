---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook contains one analyzed recipe, `cookbooks/cache/recipes/default.rb`, which references the external `memcached`, `redisio`, and `redisio::enable` recipes. The confirmed execution tree contains one Redis log-directory resource and one Redis configuration cleanup `ruby_block`. A Redis instance on port `6379`, its password, configuration path, and cleanup directives are reported by the supplied recipe analysis but require confirmation against the underlying recipe because they are not present in the structured analysis summary. No Memcached package, service, port, configuration, or templates can be determined from the supplied source.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis_6379**: Reported Redis instance configured through the recipe; source confirmation is required.
  - Location/Path: `/etc/redis/6379.conf` (reported; not independently confirmed by the structured analysis)
  - Port/Socket: TCP port `6379` (reported; not independently confirmed by the structured analysis)
  - Key Config: Redis authentication through `requirepass` and `replicaservestaledata` set to `nil` are reported recipe-level settings requiring source confirmation.
  - Log Directory: `/var/log/redis`
  - Configuration Cleanup: The recipe analysis reports removal of replication-related directives from the Redis configuration. The exact target file and regular expressions require source confirmation.

**Memcached** is referenced by the recipe, but its recipe file is missing from the supplied execution tree. No Memcached instance name, port, package, configuration path, service name, or template can be safely derived.

## File Structure

Only files shown in the supplied execution tree are listed.

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

## Module Explanation

The cookbook performs operations in the following order:

1. **cache::default** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - Creates the `/var/log/redis` directory.
   - Attempts to include the external `redisio` recipe.
   - Executes `ruby_block[fix_redis_config]`.
   - Attempts to include the external `redisio::enable` recipe.
   - The execution tree confirms one `directory` resource and one `ruby_block` resource.

2. **Include Memcached** (`cookbooks/cache/recipes/default.rb`):
   - Calls `include_recipe 'memcached'`.
   - The referenced Memcached recipe file is missing from the supplied execution tree.
   - Package names, configuration paths, service names, ports, templates, and handlers are unavailable.
   - Migrate this dependency only after a separately available Memcached role or task collection is identified.

3. **Create the Redis log directory** (`cookbooks/cache/recipes/default.rb`):
   - Uses `directory[/var/log/redis]`.
   - Creates `/var/log/redis`.
   - The resource count is one `directory` resource.
   - Owner, group, mode, and recursive settings reported in the original plan require confirmation against the underlying recipe because they are not present in the structured analysis summary.

   A migration task may be used only after confirming the original resource properties:

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

4. **Include RedisIO** (`cookbooks/cache/recipes/default.rb`):
   - Calls `include_recipe 'redisio'`.
   - The referenced `redisio` recipe file is missing from the supplied execution tree.
   - The original plan reports one Redis configuration entry named `redis_6379`, using port `6379`, `requirepass`, and `replicaservestaledata: nil`.
   - These attribute values are recipe-level claims requiring confirmation against the source.
   - Package installation, configuration deployment, and service management cannot be determined because the `redisio` recipe is missing.

   Reported migration variable structure:

   ```yaml
   redis_instances:
     - name: redis_6379
       port: 6379
       password: "{{ vault_redis_password }}"
       replica_serve_stale_data: null
   ```

5. **Remove Redis replication directives** (`cookbooks/cache/recipes/default.rb`):
   - Uses `ruby_block[fix_redis_config]`.
   - The resource count is one `ruby_block`.
   - The original plan reports that the block checks `/etc/redis/6379.conf`, reads the file, removes five directive patterns, and writes the result back.
   - The target path and exact patterns require confirmation against the underlying recipe because they are not present in the structured analysis summary.
   - Reported patterns are:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - The original Chef resource does not explicitly notify or restart Redis. Ansible migration must not add an automatic restart unless separately required and approved.

   If the reported target and patterns are confirmed, the equivalent Ansible tasks are:

   ```yaml
   - name: Remove unsupported Redis replication directives
     ansible.builtin.replace:
       path: /etc/redis/6379.conf
       regexp: '^replica-serve-stale-data.*$\n?'
       replace: ''

   - name: Remove replica read-only directive
     ansible.builtin.replace:
       path: /etc/redis/6379.conf
       regexp: '^replica-read-only.*$\n?'
       replace: ''

   - name: Remove replica ping period directive
     ansible.builtin.replace:
       path: /etc/redis/6379.conf
       regexp: '^repl-ping-replica-period.*$\n?'
       replace: ''

   - name: Remove client output buffer limit directive
     ansible.builtin.replace:
       path: /etc/redis/6379.conf
       regexp: '^client-output-buffer-limit.*$\n?'
       replace: ''

   - name: Remove replica priority directive
     ansible.builtin.replace:
       path: /etc/redis/6379.conf
       regexp: '^replica-priority.*$\n?'
       replace: ''
   ```

6. **Enable Redis** (`cookbooks/cache/recipes/default.rb`):
   - Calls `include_recipe 'redisio::enable'`.
   - The referenced recipe file is missing from the supplied execution tree.
   - The Redis service name and service resource are not confirmed.
   - Enablement and startup must be implemented only after confirming the target operating system and service unit.

   Example requiring platform confirmation:

   ```yaml
   - name: Enable and start Redis
     ansible.builtin.service:
       name: redis
       enabled: true
       state: started
   ```

## Dependencies

**External cookbook dependencies**:

- `memcached` is referenced by `include_recipe`; version constraint is not confirmed by the supplied execution tree.
- `redisio` is referenced by `include_recipe`; version constraint is not confirmed by the supplied execution tree.
- `redisio::enable` is referenced by `include_recipe`; the recipe file is missing.

**System package dependencies**:

- None are confirmed.
- No `package` resources are present in the supplied execution tree.
- Package names delegated to the missing `memcached` and `redisio` recipes cannot be determined.

**Service dependencies**:

- Redis enablement is referenced through the missing `redisio::enable` recipe.
- No explicit Chef `service` resource is confirmed.
- Memcached service management cannot be determined.

## Credentials

**Detection Summary**: One Redis password is reported in one cookbook recipe file, but the credential occurrence is not independently confirmed by the structured analysis summary.

**Source**:
  - **Provider**: Hardcoded in Chef recipe, as reported
  - **URL**: None detected
  - **Path**: None detected

### Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext, as reported
- **Reported literal value**: `redis_secure_password_123`
- **Usage context**: Redis authentication for the reported instance listening on port `6379`
- **Validation status**: Confirm the variable and literal value against the underlying recipe before migration.

Store the replacement value in Ansible Vault:

```yaml
vault_redis_password: "replace-with-secure-value"
```

Reference it from the Redis configuration:

```yaml
redis_password: "{{ vault_redis_password }}"
```

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secrets, TLS certificates, private keys, or database connection strings were detected in the supplied source.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis/`
- `/etc/redis/6379.conf` (reported Redis path; confirm before use)

**Service endpoints to check**:

- Redis instance `redis_6379`: TCP port `6379` (reported; confirm before use)
- Unix sockets: none shown
- Network interface binding: not shown

**Templates rendered**:

- None

**Resources to verify**:

- `directory[/var/log/redis]`: one resource
- `ruby_block[fix_redis_config]`: one resource
- `memcached` recipe: missing
- `redisio` recipe: missing
- `redisio::enable` recipe: missing

**Configuration modifications**:

- The original plan reports that `/etc/redis/6379.conf` is modified by removing five replication-related directive patterns.
- Confirm the target path and patterns against the recipe before implementation.
- No template resource for the Redis configuration is shown.

## Pre-flight checks:

```bash
# Confirm the analyzed cookbook recipe
test -f cookbooks/cache/recipes/default.rb
sed -n '1,240p' cookbooks/cache/recipes/default.rb

# Confirm the Redis log directory
ls -ld /var/log/redis
stat -c '%U %G %a %n' /var/log/redis

# Confirm the reported Redis 6379 configuration path
test -f /etc/redis/6379.conf
ls -l /etc/redis/6379.conf

# Confirm the Redis service unit before using service commands
systemctl list-unit-files | grep -Ei 'redis|redis-server'

# After confirming the platform-specific service name, check Redis instance redis_6379
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis

# Verify the reported Redis 6379 endpoint
ss -ltnp | grep ':6379'
# Alternative:
netstat -ltnp 2>/dev/null | grep ':6379'

# Authenticate using the Ansible Vault value rather than a plaintext production secret
redis-cli -p 6379 -a '<redis-password>' PING

# Expected result:
# PONG

# Verify the reported Redis instance port
redis-cli -p 6379 -a '<redis-password>' INFO server | grep -E 'redis_version|tcp_port'

# Check authentication and port directives after confirming the configuration path
grep -nE '^requirepass|^port' /etc/redis/6379.conf

# If the five cleanup patterns are confirmed in the source, verify they are absent
grep -nE \
  '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
  /etc/redis/6379.conf

# Review Redis logs after confirming the service unit name
journalctl -u redis --no-pager -n 50

# Verify the Redis log directory contents
ls -lah /var/log/redis
```

Memcached pre-flight validation is blocked until an external Memcached recipe or role is supplied. No cookbook-derived Memcached package, service, configuration path, or port should be assumed.