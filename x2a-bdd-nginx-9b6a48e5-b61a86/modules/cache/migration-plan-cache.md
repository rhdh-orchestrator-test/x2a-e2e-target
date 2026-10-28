---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook includes the external `memcached` recipe, assigns one Redis server on port **6379**, creates `/var/log/redis`, invokes the external `redisio` recipe, removes selected replication-related directives from `/etc/redis/6379.conf`, and invokes `redisio::enable`. The Redis settings, password, configuration path, directory properties, and directive-removal behavior are derived from direct inspection of `cookbooks/cache/recipes/default.rb`; they are not confirmed by the supplied structured analysis. The external cookbook implementations are unavailable, so their package names, service names, templates, and Memcached configuration require separate verification.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **Redis instance on port 6379**: Redis cache server configured by the local recipe
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with `requirepass`; the source contains the plaintext value `redis_secure_password_123`. The `replicaservestaledata` value is unset/null. These settings require verification against the recipe source and external `redisio` cookbook.
  - Log directory: `/var/log/redis`
  - Post-processing: Removes the following directives from `/etc/redis/6379.conf` when present:
    - `replica-serve-stale-data`
    - `replica-read-only`
    - `repl-ping-replica-period`
    - `client-output-buffer-limit`
    - `replica-priority`

- **Memcached instance**: The local recipe includes the external `memcached` recipe, but no Memcached instance name, port, configuration path, bind address, package, or service name can be confirmed because the dependency implementation is unavailable.

## File Structure

Only files shown by the supplied execution tree and directory listing are included.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

The following external cookbook files are referenced but are not present in the supplied execution tree:

- `memcached` recipe — not found
- `redisio` recipe — not found
- `redisio::enable` recipe — not found

## Module Explanation

The cookbook performs operations in this order:

1. **`memcached`** (`external cookbook: memcached/recipes/default.rb`, implementation unavailable):
   - Includes the external Memcached recipe before Redis configuration.
   - The package name, service name, configuration path, port, bind address, and templates cannot be determined locally.
   - These values must be obtained by inspecting the external `memcached` cookbook.
   - No local resources or templates are available for this recipe.

2. **Redis server collection assignment** (`cookbooks/cache/recipes/default.rb`):
   - Assigns one Redis server entry with port `6379`.
   - Assigns `requirepass` to the source value `redis_secure_password_123`; migrate this value to an Ansible Vault variable.
   - Assigns `replicaservestaledata` as unset/null.
   - Preserve the generated configuration path `/etc/redis/6379.conf`, subject to verification against the external `redisio` cookbook.
   - The collection contains one actual item: Redis port `6379`.

3. **`directory[/var/log/redis]`** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Direct source inspection indicates owner `redis`, group `redis`, mode `0755`, and recursive creation.
   - Use `ansible.builtin.file` with `state: directory`.
   - The `redis` user and group are expected to be created by the external `redisio` dependency; no local user or group resources are present.
   - Resource count: one `directory`.

4. **`redisio`** (`external cookbook: redisio/recipes/default.rb`, implementation unavailable):
   - Invokes the external Redis installation and configuration recipe after creating `/var/log/redis`.
   - The dependency may install Redis and render `/etc/redis/6379.conf`, but its package resources, service resources, templates, and exact service name cannot be confirmed locally.
   - Do not add package or service tasks until the external cookbook is inspected.

5. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Sets the target file to `/etc/redis/6379.conf`.
   - Checks whether the file exists before processing it.
   - Reads the file and removes lines matching:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Writes the modified content back to `/etc/redis/6379.conf`.
   - Implement with `ansible.builtin.replace` tasks or controlled configuration rendering.
   - Preserve the missing-file guard and notify a Redis restart or reload only when changes are made.
   - Resource count: one `ruby_block`.

6. **`redisio::enable`** (`external cookbook: redisio/recipes/enable.rb`, implementation unavailable):
   - Invokes the external Redis enable recipe last.
   - Enable and start the Redis service only after confirming the service name and behavior from the external `redisio` cookbook.
   - The exact systemd unit name cannot be determined from the supplied execution tree.

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint shown

**System package dependencies**:

- None declared by the local recipe.
- Package names cannot be verified because the external `memcached` and `redisio` implementations are unavailable.

**Service dependencies**:

- Redis service for the instance on port `6379`; exact service unit name requires external `redisio` inspection.
- Memcached service is included; exact service unit name requires external `memcached` inspection.

## Credentials

**Detection Summary**: 1 credential detected by direct inspection of 1 file. The supplied structured analysis does not include credential-detection output, so this finding should be verified against the source.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: `cookbooks/cache/recipes/default.rb`

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded plaintext Chef node attribute
- **Literal value in source**: `redis_secure_password_123`
- **Usage context**: Redis `requirepass` authentication for the Redis instance on port `6379`
- **Ansible migration**:
  - Store the replacement value in Ansible Vault, for example:
    ```yaml
    redis_requirepass: "..."
    ```
  - Render or pass the Vault value as the Redis `requirepass`.
  - Do not commit the literal password to the Ansible repository.
  - Rotate the exposed Chef password if it has been used in a real environment.

No data bag, Chef Vault, CyberArk, Conjur, AWS Secrets Manager, HashiCorp Vault, environment-variable secret, TLS certificate, private key, or database connection string was detected in the supplied files.

## Checks for the Migration

**Files to verify**:

- `/etc/redis/6379.conf`
- `/var/log/redis`

**Service endpoints to check**:

- Redis TCP port `6379`
- Unix sockets: none identified
- Memcached endpoint: unavailable from the supplied local source

**Templates rendered**:

- Local templates: none
- External `memcached` templates: unavailable
- External `redisio` templates: unavailable
- Confirm exact external render counts after inspecting both dependency cookbooks

**Configuration checks**:

- Confirm `/etc/redis/6379.conf` exists.
- Confirm Redis listens on port `6379`.
- Confirm authentication is configured without exposing the password in command output.
- Confirm the following directives are absent:
  - `replica-serve-stale-data`
  - `replica-read-only`
  - `repl-ping-replica-period`
  - `client-output-buffer-limit`
  - `replica-priority`
- Confirm `/var/log/redis` is owned by `redis:redis` with mode `0755`.
- Inspect the external cookbooks to verify package names, service names, templates, and Memcached settings.

## Pre-flight checks

### Redis instance on port 6379

```bash
# Replace redis-server with the service unit confirmed from the redisio cookbook.
systemctl status redis-server
ps aux | grep '[r]edis-server'

ss -tlnp | grep ':6379'
test -f /etc/redis/6379.conf
```

### Redis authentication on port 6379

Do not place the password directly in shell history:

```bash
REDISCLI_AUTH='<vault-supplied-password>' redis-cli -p 6379 PING
```

Expected result:

```text
PONG
```

Confirm unauthenticated access is rejected:

```bash
redis-cli -p 6379 PING
```

Expected result should indicate that authentication is required rather than returning `PONG`.

### Redis configuration for port 6379

```bash
grep -E '^(port|requirepass)' /etc/redis/6379.conf

! grep -E '^replica-serve-stale-data' /etc/redis/6379.conf
! grep -E '^replica-read-only' /etc/redis/6379.conf
! grep -E '^repl-ping-replica-period' /etc/redis/6379.conf
! grep -E '^client-output-buffer-limit' /etc/redis/6379.conf
! grep -E '^replica-priority' /etc/redis/6379.conf
```

Validate the configuration using the command documented by the external Redis dependency. A common example is:

```bash
redis-server /etc/redis/6379.conf --test-memory 2
```

Do not start a second Redis process with this command on a production host.

### Redis log directory

```bash
stat -c '%A %U:%G %n' /var/log/redis
ls -ld /var/log/redis
```

Expected values:

```text
drwxr-xr-x redis:redis /var/log/redis
```

### Redis logs

```bash
grep -E '^(logfile|syslog-enabled|syslog-ident)' /etc/redis/6379.conf
journalctl -u redis-server --no-pager -n 50
```

Replace `redis-server` with the service unit confirmed by the external `redisio` cookbook. If Redis uses file-based logging, inspect the path returned by the `logfile` setting.

### Memcached

The Memcached dependency must be inspected before verification tasks are written. Confirm the following values:

- Installed package name
- Service unit name
- Listening port
- Bind address
- Configuration file
- Authentication or SASL settings, if any

Do not assume a Memcached port, package, configuration path, or service name from the local cookbook alone.