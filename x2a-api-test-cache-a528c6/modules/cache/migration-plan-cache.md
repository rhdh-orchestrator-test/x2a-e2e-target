---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures cache services through the external `memcached`, `redisio`, and `redisio::enable` recipes. The analyzed entry recipe includes the Memcached recipe, creates `/var/log/redis`, defines one Redis server configuration reported as port `6379`, performs cleanup on `/etc/redis/6379.conf`, and enables Redis. The dependency recipe implementations are unavailable, and several configuration details—including Redis settings, credentials, package names, service names, and Memcached endpoints—must be verified before migration.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance reported as port 6379**: Redis cache service
  - Location/Path: `/etc/redis/6379.conf` — reported by the migration analysis; verify against the recipe
  - Port/Socket: `6379` — reported by the migration analysis; not independently confirmed by the supplied validation summary
  - Key Config: A `requirepass` value, `replicaservestaledata: nil`, and cleanup of selected replication directives are reported but require recipe-level verification
  - Log directory: `/var/log/redis` — directory resource is confirmed; owner, group, mode, and recursive setting require verification
  - Service enablement: `redisio::enable`
  - Post-configuration cleanup: `ruby_block[fix_redis_config]` targets the reported Redis configuration path

- **Memcached**: Memcached cache service
  - Location/Path: Not shown in the supplied analysis
  - Port/Socket: Not specified; obtain from the `memcached` dependency or deployment variables
  - Key Config: Managed by the external `memcached` recipe; package, listen address, memory limit, configuration path, and service name are unavailable

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

No templates are shown in the supplied directory listing or execution analysis.

**Attributes:**
```text
```

No attribute files are shown in the supplied directory listing. Any Redis attributes assigned directly in `cookbooks/cache/recipes/default.rb` must be confirmed from the recipe contents.

**Files:**
```text
```

No static files are shown in the supplied directory listing.

The following dependency recipe files are referenced but not found in the supplied execution tree:

- `memcached`
- `redisio`
- `redisio::enable`

The supplied analysis does not provide complete independent inventories for dependency templates, attributes, or static files.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes the external `memcached` recipe.
   - The Memcached dependency implementation is unavailable, so its package installation, configuration, endpoint, and service behavior cannot be determined.
   - Creates the `directory[/var/log/redis]` resource.
   - The intended owner, group, mode, and recursive behavior are reported in the migration analysis but are not confirmed by the supplied validation summary.
   - Defines a Redis server collection reportedly containing one item for port `6379`.
   - The reported Redis password, `replicaservestaledata` value, and other server attributes require confirmation from the recipe-level analysis.
   - Includes the external `redisio` recipe.
   - Runs `ruby_block[fix_redis_config]`.
   - Includes the external `redisio::enable` recipe.

   **`ruby_block[fix_redis_config]` behavior**:
   - Reported target: `/etc/redis/6379.conf`; verify the path from the recipe.
   - If the target file exists, the block reportedly removes complete lines beginning with:
     - `replica-serve-stale-data`
     - `replica-read-only`
     - `repl-ping-replica-period`
     - `client-output-buffer-limit`
     - `replica-priority`
   - If the target file does not exist, the cleanup operation reportedly makes no change.
   - The visible resource does not confirm an explicit Redis restart or reload notification.

   **Ansible migration actions**:
   - Import the Memcached dependency role or task file first.
   - Create `/var/log/redis` using `ansible.builtin.file` after verifying its required ownership and permissions.
   - Import the Redis installation and configuration tasks.
   - Configure the reported Redis instance only after confirming its port, configuration path, and attributes.
   - Apply the cleanup only when the configuration file exists.
   - Enable and start the verified Redis service after configuration is complete.
   - Notify a restart or reload only when the final configuration changes.

### Iterations

The migration analysis reports exactly one Redis server item:

- **Redis instance reported as port 6379**
  - `port`: `6379` — requires confirmation
  - `requirepass`: reported hardcoded value, requires confirmation
  - `replicaservestaledata`: `nil` — requires confirmation

No `.each` loop is confirmed in the supplied execution tree.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, with no version constraint
- `redisio::enable`, a recipe within the `redisio` dependency

The dependency implementations are not present in the supplied execution tree.

**System package dependencies**:

- No package names or versions are confirmed in the supplied cookbook analysis.
- Obtain package names from the actual `memcached` and `redisio` dependency implementations and the target operating system.
- Do not invent package names or versions.

**Service dependencies**:

- Memcached service managed by the `memcached` dependency
- Redis service managed by the `redisio` dependency
- Redis enablement managed by `redisio::enable`
- Exact systemd unit names are unavailable and must be verified before migration.

## Credentials

**Detection Summary**: 0 credentials independently confirmed by the supplied validation summary; 1 potential hardcoded Redis credential is reported by the migration plan and requires recipe-level verification.

**Source**:
  - **Provider**: Hardcoded in Chef recipe, reported but unverified
  - **URL**: None detected
  - **Path**: None detected

### Potential Redis Authentication Password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']` — reported, unverified
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Reported hardcoded plaintext Chef attribute assignment; verify from the recipe
- **Reported value**: `redis_secure_password_123` — do not treat as confirmed until recipe-level analysis verifies it
- **Usage context**: Reported Redis `requirepass` authentication for the instance described as port `6379`
- **Migration handling**:
  - Store the confirmed value in Ansible Vault.
  - Do not commit plaintext credentials.
  - Restrict permissions on any generated configuration containing the password.
  - Prevent the secret from appearing in task output.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, secret environment variables, TLS certificate references, private keys, or database connection strings are confirmed in the supplied analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/var/log/redis/` — resource path confirmed
- `/etc/redis/6379.conf` — reported by the migration analysis; verify from the recipe and dependency implementation

**Service endpoints to check**:

- Redis TCP port `6379` — reported; verify before use
- Memcached port — not specified; obtain from the dependency or deployment variables
- Unix sockets — none referenced in the supplied analysis

**Templates rendered**:

- 0 templates are shown in the supplied directory listing or execution analysis.
- Dependency template rendering is unavailable and must be verified from the dependency cookbooks.

## Pre-flight checks

```bash
# Confirm the migrated recipe and dependency implementations
test -f cookbooks/cache/recipes/default.rb

# Redis configuration path reported by the migration analysis
test -f /etc/redis/6379.conf

# Redis authentication configuration, if confirmed for the target deployment
grep -E '^[[:space:]]*requirepass[[:space:]]+' /etc/redis/6379.conf

# Verify that reported cleanup directives are absent, if the cleanup behavior
# is confirmed from the recipe
if grep -Eq '^[[:space:]]*(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf; then
  echo "Unexpected Redis directives remain"
  exit 1
fi

# Redis endpoint reported by the migration analysis
ss -tlnp | grep ':6379'

# Authenticate using the Redis password retrieved from Ansible Vault.
# Do not place the plaintext password in shell history or source control.
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' PING

# Verify Redis responsiveness
redis-cli -p 6379 -a '<redis-password-from-ansible-vault>' INFO server

# Redis log directory; confirm the expected values only after recipe-level
# analysis verifies them
stat -c '%U:%G %a %n' /var/log/redis

# Replace with the service unit verified from the redisio dependency
systemctl status <verified-redis-service-name>
systemctl is-enabled <verified-redis-service-name>
systemctl is-active <verified-redis-service-name>
journalctl -u <verified-redis-service-name> --no-pager -n 50
```

### Memcached checks

```bash
# Replace both placeholders with values verified from the memcached dependency
systemctl status <verified-memcached-service-name>
systemctl is-enabled <verified-memcached-service-name>
systemctl is-active <verified-memcached-service-name>
ss -tlnp | grep ':<verified-memcached-port>'
```

### Ansible idempotence checks

```bash
ansible-playbook -i inventory cache.yml
ansible-playbook -i inventory cache.yml --check
ansible-playbook -i inventory cache.yml
```

Verify that:

- `/var/log/redis` has the ownership and mode confirmed from the recipe.
- `/etc/redis/6379.conf` is not repeatedly rewritten.
- Reported cleanup directives do not reappear if the cleanup behavior is confirmed.
- The verified Redis service remains enabled and active.
- The verified Memcached service remains enabled and active.
- The Redis password is sourced from Ansible Vault and is not printed in task output.
