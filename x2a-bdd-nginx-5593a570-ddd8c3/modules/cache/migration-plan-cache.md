---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures a cache layer with one Redis instance on port **6379**, including Redis authentication, creation of `/var/log/redis`, removal of selected replication-related directives from `/etc/redis/6379.conf`, and an attempted Redis service enablement through the external `redisio` cookbook. It also includes the external `memcached` cookbook. The analyzed execution tree contains only `cache::default`; the `memcached`, `redisio`, and `redisio::enable` recipe files are unavailable. Redis installation details, the service name, and Memcached configuration must therefore be confirmed or implemented separately.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis server on port 6379**: Redis cache server configured by `cache::default`
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config:
    - Redis authentication uses `requirepass`; the source-reported value is `redis_secure_password_123` and must be migrated to Ansible Vault or another approved secret store.
    - `replicaservestaledata`: `nil`
    - Log directory: `/var/log/redis`
    - Log directory owner/group: `redis:redis`
    - Log directory mode: `0755`
    - The recipe removes lines beginning with:
      - `replica-serve-stale-data`
      - `replica-read-only`
      - `repl-ping-replica-period`
      - `client-output-buffer-limit`
      - `replica-priority`

The Redis server collection contains one configured item for port `6379`. No `.each` loop is present in the supplied execution tree.

No Memcached instance, port, package, configuration path, or service name is defined in the analyzed cookbook source. The external `memcached` recipe is unavailable.

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

```text
cookbooks/
└── cache/
    └── recipes/
        └── default.rb
```

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

```text
cache::default
├── memcached (recipe file unavailable)
├── directory[/var/log/redis]
├── redisio (recipe file unavailable)
├── ruby_block[fix_redis_config]
└── redisio::enable (recipe file unavailable)
```

### 1. `cache::default` (`cookbooks/cache/recipes/default.rb`)

- Includes the external `memcached` recipe.
  - The referenced recipe is unavailable.
  - No Memcached package, configuration path, port, service name, or template can be derived from the analyzed cookbook.
  - Do not invent Memcached configuration during migration.

- Defines one Redis server configuration:
  - Instance: Redis server on port `6379`
  - `port`: `6379`
  - `requirepass`: source-reported value `redis_secure_password_123`
  - `replicaservestaledata`: `nil`
  - No `.each` loop is present in the supplied execution tree; the single configured item must nevertheless be preserved.

- Creates the Redis log directory with `directory[/var/log/redis]`:
  - Path: `/var/log/redis`
  - Owner: `redis`
  - Group: `redis`
  - Mode: `0755`
  - Recursive creation: enabled
  - Resource count: one directory resource
  - Ansible equivalent: `ansible.builtin.file` with `state: directory`

- Includes the external `redisio` recipe.
  - The referenced recipe is unavailable.
  - The analyzed cookbook does not provide a Redis package name, installation command, template, provider, or service resource.
  - The Ansible role must implement the missing RedisIO behavior explicitly or consume an approved external Redis role or collection.

- Runs `ruby_block[fix_redis_config]`:
  - Target path: `/etc/redis/6379.conf`
  - Checks whether the file exists.
  - Reads the file when present.
  - Removes complete lines matching:
    - `^replica-serve-stale-data.*$`
    - `^replica-read-only.*$`
    - `^repl-ping-replica-period.*$`
    - `^client-output-buffer-limit.*$`
    - `^replica-priority.*$`
  - Writes the modified contents back to the same path.
  - Resource count: one Ruby block
  - Ansible equivalent: one or more `ansible.builtin.replace` tasks, preserving the skip-if-absent behavior.

- Includes `redisio::enable`.
  - The referenced recipe is unavailable.
  - Its service name and enablement behavior cannot be confirmed from the supplied execution tree.
  - After the Redis implementation is selected, enable and start the confirmed service with `ansible.builtin.service` or `ansible.builtin.systemd`.

No restart or reload notification is explicitly defined. The recipe contains no Chef `service`, `notifies`, or `subscribes` resource.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**System package dependencies**:

- None are directly declared in the analyzed execution tree.
- Package names from the unavailable `memcached` and `redisio` recipes cannot be verified and must be confirmed before implementation.

**Service dependencies**:

- `redisio::enable`, recipe unavailable
- Redis service name, unavailable
- Memcached service name, unavailable

## Credentials

**Detection Summary**: 1 credential detected in 1 file based on source inspection.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None
- **Path**: None

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Literal value in source**: `redis_secure_password_123`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in a Chef recipe
- **Usage context**: Redis authentication for the Redis server on port `6379`
- **Migration handling**:
  - Store the password in Ansible Vault or an approved AAP credential or secret mechanism.
  - Do not retain the plaintext value in a normal variable file.
  - Render it with restrictive permissions.
  - Use `no_log: true` for sensitive tasks.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secrets, TLS certificates, database connection strings, or secret attribute namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`

The cookbook does not explicitly create a Redis data directory or log file. Those paths may be created by the unavailable `redisio` dependency and must be confirmed during implementation.

**Service endpoints to check**:

- Redis server on port `6379`
- Unix sockets: none configured or referenced
- Network interface binding: not specified

**Templates rendered**:

- None; no templates are present or rendered.

**Configuration directives to verify for Redis server on port 6379**:

- Redis authentication is configured.
- The following directives are absent from `/etc/redis/6379.conf`:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`

## Pre-flight checks:

```bash
# Confirm the Redis service name selected by the implementation.
systemctl list-unit-files | grep -E '^(redis|redis-server)'

# Redis server on port 6379: service status and enablement.
systemctl status redis
systemctl is-enabled redis
systemctl status redis-server
systemctl is-enabled redis-server

# Redis server on port 6379: configuration file.
test -f /etc/redis/6379.conf
ls -l /etc/redis/6379.conf

# Redis server on port 6379: configuration validation.
redis-server --test-memory 2
redis-cli -p 6379 CONFIG GET port
redis-cli -p 6379 CONFIG GET requirepass

# Redis server on port 6379: authenticated connectivity.
redis-cli -p 6379 -a 'REDACTED_REDIS_PASSWORD' PING
# Expected output: PONG

redis-cli -p 6379 -a 'REDACTED_REDIS_PASSWORD' INFO server
redis-cli -p 6379 -a 'REDACTED_REDIS_PASSWORD' DBSIZE

# Redis server on port 6379: verify removed directives.
if test -f /etc/redis/6379.conf; then
  ! grep -nE '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' \
    /etc/redis/6379.conf
fi

# Redis server on port 6379: log directory ownership and permissions.
test -d /var/log/redis
stat -c '%U %G %a %n' /var/log/redis
# Expected output: redis redis 755 /var/log/redis

# Redis server on port 6379: listening socket.
ss -ltnp | grep ':6379'
lsof -iTCP:6379 -sTCP:LISTEN

# Redis server on port 6379: process and logs.
ps aux | grep '[r]edis-server'
journalctl -u redis --no-pager -n 100
journalctl -u redis-server --no-pager -n 100
```

Use the Redis password through a protected shell mechanism or Ansible Vault during validation. Do not commit it to scripts or expose it in CI/CD output.