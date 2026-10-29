---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook is intended to configure Memcached and Redis, but the supplied execution tree contains only `cookbooks/cache/recipes/default.rb`. The recipe attempts to include the missing `memcached`, `redisio`, and `redisio::enable` recipes. The available recipe reports one Redis instance on port `6379`, creates `/var/log/redis`, and removes five replication-related directives from `/etc/redis/6379.conf`. The reported Redis password is hardcoded and must be replaced with an Ansible Vault-managed secret. Package names, service names, templates, and other dependency-provided behavior require verification from the missing cookbooks or the target operating system.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-6379**: Redis cache instance
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`; no Unix socket specified
  - Log directory: `/var/log/redis`
  - Key Config:
    - Redis authentication is reported as `requirepass redis_secure_password_123`; replace this plaintext value with an Ansible Vault-managed secret.
    - `replicaservestaledata` is assigned `nil`.
    - The following directives are removed from the configuration when present:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`
    - Bind address is not specified.

**Memcached**:

The recipe attempts to include the external `memcached` recipe, but the supplied execution tree reports:

```text
memcached Recipe file not found
```

No Memcached instance name, package, service, configuration path, port, template, or authentication settings can be confirmed. Do not invent Memcached configuration. Restore and inspect the dependency before migrating Memcached behavior, or explicitly omit Memcached from the migration.

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

No template files are shown in the execution tree.

### Attributes

```text
```

No attribute files are shown in the execution tree. The Redis server collection is reported as being assigned directly in `cookbooks/cache/recipes/default.rb`.

### Files

```text
```

No static files are shown in the execution tree.

## Module Explanation

The supplied execution tree reports this execution order:

```text
cache::default
    ├── memcached Recipe file not found
    ├── [resource] directory[/var/log/redis]
    ├── redisio Recipe file not found
    ├── [resource] ruby_block[fix_redis_config]
    └── redisio::enable Recipe file not found
```

The execution tree confirms the recipe and resource names above. The detailed attribute values, resource properties, and regular expressions below are reported from the supplied plan but require verification against the actual recipe source and dependency implementations.

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Attempts to include the external `memcached` recipe.
   - Assigns one Redis server definition to `node['redisio']['servers']`, reported as:
     - Instance name: `redis-6379`
     - Port: `6379`
     - `requirepass`: `redis_secure_password_123`
     - `replicaservestaledata`: `nil`
   - Creates `/var/log/redis`; the reported owner is `redis`, group is `redis`, mode is `0755`, and recursive creation is enabled. These properties require source verification.
   - Attempts to include the external `redisio` recipe.
   - Defines `ruby_block[fix_redis_config]`, which operates on `/etc/redis/6379.conf`.
   - Attempts to include the external `redisio::enable` recipe.
   - No `.each` loops are present in the supplied recipe analysis.

   **Memcached include**:

   ```ruby
   include_recipe 'memcached'
   ```

   The recipe is missing from the supplied execution tree. Do not create Memcached tasks until its package, service, configuration path, listening port, and settings are confirmed.

   **Redis server collection**:

   The reported assignment is:

   ```ruby
   node.default['redisio']['servers'] = [
     {
       'port' => '6379',
       'requirepass' => 'redis_secure_password_123',
       'replicaservestaledata' => nil,
     }
   ]
   ```

   The Ansible representation should use one explicit instance and retrieve the password from Ansible Vault:

   ```yaml
   redis_instances:
     - name: redis-6379
       port: 6379
       requirepass: "{{ vault_redis_password }}"
       replicaservestaledata: null
   ```

   **Resource: `directory[/var/log/redis]`**:

   The execution tree confirms the directory resource. The reported properties are:

   - Path: `/var/log/redis`
   - Owner: `redis`
   - Group: `redis`
   - Mode: `0755`
   - Recursive creation: enabled

   These properties require verification against the recipe source. The `redis` user and group are expected to be supplied by the missing `redisio` dependency and must exist before this task runs.

   **Redis dependency include**:

   ```ruby
   include_recipe 'redisio'
   ```

   The `redisio` recipe is missing. Its package names, service name, user and group creation, configuration template, data directory, log file, and startup behavior cannot be confirmed from the supplied execution tree.

   **Resource: `ruby_block[fix_redis_config]`**:

   The execution tree confirms the Ruby block resource. The reported behavior is to modify `/etc/redis/6379.conf` when the file exists and remove complete lines matching:

   ```text
   ^replica-serve-stale-data.*$
   ^replica-read-only.*$
   ^repl-ping-replica-period.*$
   ^client-output-buffer-limit.*$
   ^replica-priority.*$
   ```

   These target paths and expressions require verification against the recipe source. Ansible should implement the confirmed behavior with separate `ansible.builtin.lineinfile` tasks only after the configuration file and service name are verified:

   ```yaml
   - name: Remove replica-serve-stale-data from Redis configuration
     ansible.builtin.lineinfile:
       path: /etc/redis/6379.conf
       regexp: '^replica-serve-stale-data.*$'
       state: absent

   - name: Remove replica-read-only from Redis configuration
     ansible.builtin.lineinfile:
       path: /etc/redis/6379.conf
       regexp: '^replica-read-only.*$'
       state: absent

   - name: Remove repl-ping-replica-period from Redis configuration
     ansible.builtin.lineinfile:
       path: /etc/redis/6379.conf
       regexp: '^repl-ping-replica-period.*$'
       state: absent

   - name: Remove client-output-buffer-limit from Redis configuration
     ansible.builtin.lineinfile:
       path: /etc/redis/6379.conf
       regexp: '^client-output-buffer-limit.*$'
       state: absent

   - name: Remove replica-priority from Redis configuration
     ansible.builtin.lineinfile:
       path: /etc/redis/6379.conf
       regexp: '^replica-priority.*$'
       state: absent
   ```

   The original behavior reportedly checks whether the file exists before modifying it. The Ansible role must either perform an existence check or ensure the Redis configuration task runs first. The original recipe does not explicitly show a service restart notification; the migration should restart or reload Redis only after the correct service name is confirmed.

   **Redis enablement include**:

   ```ruby
   include_recipe 'redisio::enable'
   ```

   The recipe is missing. This likely manages service enablement and startup, but the behavior is unconfirmed. After identifying the actual service name, implement the equivalent:

   ```yaml
   - name: Enable and start Redis instance redis-6379
     ansible.builtin.service:
       name: <confirmed-redis-service-name>
       enabled: true
       state: started
   ```

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0` — reported from `metadata.rb`; metadata is not present in the supplied execution-tree listing.
- `redisio`, with no version constraint — reported from `metadata.rb`; metadata is not present in the supplied execution-tree listing.
- Missing recipe references:
  - `memcached`
  - `redisio`
  - `redisio::enable`

**System package dependencies**:

No package resources are present in the available execution tree. Exact Memcached and Redis package names are not verified and must not be assumed.

**Service dependencies**:

- Redis service management is intended to be provided by the missing `redisio::enable` recipe. The exact service name is not available.
- Memcached service management cannot be confirmed because the `memcached` recipe is missing.
- The `redis` user and group are expected to be supplied by the missing Redis dependency, but this is not verified.

## Credentials

**Detection Summary**: 1 hardcoded Redis credential is reported in `cookbooks/cache/recipes/default.rb`; the supplied structured validation does not include an independent credential-scan result.

**Source**:
  - **Provider**: None detected
  - **URL**: Not applicable
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext Chef attribute value
- **Reported value**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for instance `redis-6379` on TCP port `6379`
- **Migration storage**: Store as `vault_redis_password` in Ansible Vault or retrieve it from an approved secret manager.
- **Provider**: None detected; no HashiCorp Vault, CyberArk, AWS Secrets Manager, Chef Vault, encrypted data bag, standard data bag, or environment-variable provider is shown.

No TLS certificate, private key, database connection string, or API token is reported.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

The following dependency-provided paths cannot be confirmed:

- Redis data directory
- Redis log file
- Redis service unit
- Memcached configuration
- Memcached log files

**Service endpoints to check**:

- `redis-6379`: TCP port `6379`
- Unix socket: none specified
- Memcached endpoint: not available until the missing recipe is restored

**Configuration directives to verify**:

- A single Redis `requirepass` directive using the Vault-managed password
- Absence of:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

**Templates rendered**:

- None; no templates are shown in the execution tree.
- Render count: `0`

**Static files deployed**:

- None; no static files are shown in the execution tree.
- Deployment count: `0`

## Pre-flight checks

```bash
# Verify the locally available recipe
test -f cookbooks/cache/recipes/default.rb

# Confirm unresolved cookbook dependencies before migration
test -f cookbooks/memcached/recipes/default.rb || echo "memcached recipe is unavailable"
test -f cookbooks/redisio/recipes/default.rb || echo "redisio recipe is unavailable"
test -f cookbooks/redisio/recipes/enable.rb || echo "redisio::enable recipe is unavailable"

# Verify the Redis configuration file for instance redis-6379
test -f /etc/redis/6379.conf

# Verify the Redis log directory for instance redis-6379
stat -c '%A %U:%G %n' /var/log/redis
# Expected only after source verification: directory owned by redis:redis with mode 0755

# Verify the Redis user and group required by instance redis-6379
getent passwd redis
getent group redis

# Replace with the service name confirmed from the redisio dependency
systemctl status <confirmed-redis-service-name>
systemctl is-enabled <confirmed-redis-service-name>
systemctl is-active <confirmed-redis-service-name>

# Verify that instance redis-6379 is listening on TCP port 6379
ss -ltnp | grep ':6379'

# Verify Redis authentication and connectivity for instance redis-6379
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' PING
# Expected: PONG

# Verify Redis server information for instance redis-6379
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' INFO server

# Verify the configured authentication directive
grep -E '^[[:space:]]*requirepass[[:space:]]+' /etc/redis/6379.conf
# Expected: one requirepass directive using the Vault-managed password

# Verify that the five cleanup directives are absent from instance redis-6379
if grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected removed Redis directives remain"
  exit 1
else
  echo "Redis cleanup directives are absent"
fi

# Verify recent Redis logs for instance redis-6379
journalctl -u <confirmed-redis-service-name> --since "15 minutes ago" --no-pager

# Verify the Redis process for instance redis-6379
pgrep -a redis-server
```

Memcached has no valid pre-flight endpoint check because its recipe, service name, configuration path, and port are unavailable. Once the `memcached` cookbook is restored, add checks using its verified service, port, configuration file, and health command.