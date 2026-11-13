---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: The `cache` cookbook configures one Memcached instance named `memcached` and one Redis instance on port `6379`. Memcached listens on TCP and UDP port `11211`, uses 64 MB of memory, and is started and enabled through the `memcached_instance` custom resource. Redis is configured through the external `redisio` cookbook, uses `/run/redis` for PID files, creates `/var/log/redis`, removes selected replication-related directives from `/etc/redis/6379.conf`, and is enabled at boot. The Redis password is hardcoded in the Chef recipe and must be migrated to Ansible Vault or another approved secret store.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **`memcached`**: Memcached caching service
  - Location/Path: Configuration path is determined by the unavailable custom-resource provider
  - Port/Socket: TCP `11211`, UDP `11211`
  - Key Config: Listen address `0.0.0.0`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; ulimit `1024`; user `service_user`; worker threads sourced from `node['memcached']['threads']`, which has no supplied default; experimental options `[]`; extra CLI options `[]`; version `nil`; actions `start`, `enable`

- **`6379`**: Redis server
  - Location/Path: `/etc/redis/6379.conf`; PID directory `/run/redis`; log directory `/var/log/redis`
  - Port/Socket: TCP `6379`
  - Key Config: Authentication enabled with a vaulted password; log directory owner `redis`, group `redis`, mode `0755`; Redis enabled at boot; selected replication directives removed from the configuration

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb

migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/_package.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/disabled.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/enforcing.rb
migration-dependencies/cookbook_artifacts/selinux-c414582aa5688ac843992facf3b65811abf43d2f/recipes/permissive.rb
```

The following categories contain no supplied files:

- Providers: No provider file is included. The `memcached_instance` provider path is unavailable.
- Templates: No Chef templates are rendered.
- Static files: No files are deployed by `cookbook_file` or `remote_file`.
- Redis recipes: The `redisio` and `redisio::enable` recipe files are referenced but unavailable.

The `_package.rb` and SELinux recipe files appear in the directory listing but are not part of the executed flow.

## Module Explanation

The cookbook performs operations in this order:

1. **`cache::default`** (`cookbooks/cache/recipes/default.rb`):
   - Includes `memcached::default`.
   - Sets the Redis server list to one instance on port `6379`.
   - Sets the Redis password to the hardcoded Chef value, which must be replaced by a vaulted variable.
   - Sets `redisio.base_piddir` to `/run/redis`.
   - Includes the unavailable `redisio` recipe.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]`.
   - Includes the unavailable `redisio::enable` recipe.
   - Resources: one `directory`, one `ruby_block`, two dependency recipe inclusions, and one Redis enable recipe inclusion.
   - Iterations: No `.each` loop. The Redis server collection contains one explicitly configured instance, `6379`.

2. **`memcached::default`** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Declares `memcached_instance['memcached']`.
   - Configures memory `64` MB.
   - Configures TCP port `11211` and UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Sets maximum connections to `1024`.
   - Sets maximum object size to `1m`.
   - Runs under `service_user`.
   - Uses `node['memcached']['threads']`; no default value is supplied.
   - Sets experimental options and extra CLI options to empty lists.
   - Sets ulimit to `1024`.
   - Starts and enables the service.
   - No templates are identified.
   - Iterations: No `.each` loop. The resource is declared once for the instance `memcached`.
   - The provider, package name, service unit name, and configuration path are unavailable from the supplied execution tree.

3. **`redisio`** (`redisio/recipes/default.rb`, unavailable):
   - Intended to configure the single Redis instance on port `6379`.
   - Uses `/run/redis` as the base PID directory.
   - Must produce a Redis configuration with authentication enabled.
   - The exact dependency implementation is unavailable.

4. **Redis log directory resource** (`cookbooks/cache/recipes/default.rb`):
   - Creates `/var/log/redis`.
   - Sets owner `redis`.
   - Sets group `redis`.
   - Sets mode `0755`.
   - Enables recursive creation.

5. **`ruby_block[fix_redis_config]`** (`cookbooks/cache/recipes/default.rb`):
   - Reads `/etc/redis/6379.conf` only when the file exists.
   - Removes lines beginning with `replica-serve-stale-data`.
   - Removes lines beginning with `replica-read-only`.
   - Removes lines beginning with `repl-ping-replica-period`.
   - Removes lines beginning with `client-output-buffer-limit`.
   - Removes lines beginning with `replica-priority`.
   - Preserves unrelated configuration lines.
   - Writes the file only after applying the cleanup.
   - The Ansible implementation must be idempotent and restart or reload Redis only when configuration changes.

6. **`redisio::enable`** (`redisio/recipes/enable.rb`, unavailable):
   - Intended to enable Redis at boot.
   - The Ansible implementation must enable and start the service corresponding to the Redis instance on port `6379`.
   - The exact service unit name must be determined on the target platform.

## Dependencies

**External cookbook dependencies**:

- `memcached`, constrained to `~> 6.0`
- `redisio`, with no version constraint

**System package dependencies**:

- No package resources or verified package names are present in the supplied execution tree.
- Package names must be selected and verified for the target Ubuntu or CentOS platform during implementation.
- Package names must not be inferred from the unavailable Chef providers.

**Service dependencies**:

- Memcached service for instance `memcached`
- Redis service for instance `6379`
- The exact Redis service unit name is unavailable because the `redisio` recipes are missing.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 hardcoded credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded Chef recipe assignment
- **URL**: None detected
- **Path**: Redis instance configuration on port `6379`

### Redis authentication password

- **Variable**: `node.default['redisio']['servers'][0]['requirepass']`
- **Source file**: `cookbooks/cache/recipes/default.rb`, line 8
- **Current storage**: Hardcoded plaintext in the Chef recipe
- **Value detected**: `redis_secure_password_123`
- **Usage context**: Redis client authentication for port `6379`
- **Migration storage**: Ansible Vault variable such as `redis_requirepass`
- **Migration usage**: Reference the vaulted variable from the Redis configuration template or role variables

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secrets, TLS certificate paths, private keys, or database connection strings were detected. The Memcached configuration contains no detected credentials.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/var/log/redis`
- `/etc/redis/6379.conf`
- `/run/redis`
- The Memcached configuration file selected by the target Ansible implementation
- `ansible/Makefile`
- `INPUT-AGENTS.md`
- `EXPORT-AGENTS.md`

**Service endpoints to check**:

- Memcached instance `memcached`: TCP `0.0.0.0:11211`
- Memcached instance `memcached`: UDP `0.0.0.0:11211`
- Redis instance `6379`: TCP port `6379`
- Unix sockets: None specified
- Redis bind address: Not specified in the supplied recipe

**Templates rendered**:

- Chef templates: None
- Ansible templates: Redis configuration template, if used; render count must be verified during implementation
- Memcached template: Determined by the selected Ansible implementation

**Iterations expanded**:

- Memcached: one instance named `memcached`
- Redis: one instance on port `6379`
- No `.each` loops are present.

## Pre-flight checks

### Memcached instance `memcached`

```bash
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
```

Use the discovered unit name if the target platform does not use `memcached`.

```bash
printf "version\r\n" | nc -w 2 127.0.0.1 11211
ss -ltnp | grep ':11211'
ss -lunp | grep ':11211'
```

Expected results:

- The TCP endpoint returns a response beginning with `VERSION`.
- TCP port `11211` is listening.
- UDP port `11211` is listening.
- The effective configuration specifies:
  - Memory: `64` MB
  - TCP port: `11211`
  - UDP port: `11211`
  - Listen address: `0.0.0.0`
  - Maximum connections: `1024`
  - Maximum object size: `1m`
  - Ulimit: `1024`
  - User: `service_user`, where supported by the target package

The exact Memcached configuration path depends on the target platform because the Chef custom-resource provider is unavailable.

### Redis instance `6379`

```bash
systemctl status redis
systemctl is-enabled redis
systemctl is-active redis
```

Use the discovered port-specific unit name if the target package provides one.

```bash
ss -ltnp | grep ':6379'
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|pidfile)' /etc/redis/6379.conf
```

Verify that:

- Redis listens on TCP port `6379`.
- Authentication uses the vaulted password.
- The PID path is under `/run/redis`.
- `/etc/redis/6379.conf` exists.

Confirm that the unwanted directives are absent:

```bash
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf
```

Expected result: no matching output.

Test authenticated connectivity without exposing the password in shell history:

```bash
read -s REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
unset REDIS_PASSWORD
```

Expected result:

```text
PONG
```

### Redis directories and logs

```bash
stat -c '%A %U %G %n' /var/log/redis
```

Expected result:

```text
drwxr-xr-x redis redis /var/log/redis
```

```bash
stat -c '%A %U %G %n' /run/redis
```

Verify that `/run/redis` exists and is writable by the Redis service account.

```bash
journalctl -u redis --since "10 minutes ago" --no-pager
```

Check for startup failures, authentication errors, permission errors, and port-binding errors. Substitute the discovered port-specific unit name when applicable.

### Redis functional validation

```bash
read -s REDIS_PASSWORD
redis-cli -p 6379 -a "$REDIS_PASSWORD" SET migration_check "ok"
redis-cli -p 6379 -a "$REDIS_PASSWORD" GET migration_check
redis-cli -p 6379 -a "$REDIS_PASSWORD" DEL migration_check
unset REDIS_PASSWORD
```

Expected results:

- `SET` returns `OK`.
- `GET` returns `ok`.
- `DEL` returns `1`.

### Migration project requirements

The generated Ansible project must preserve the FLPATH-4982 BDD Makefile requirement in both `INPUT-AGENTS.md` and `EXPORT-AGENTS.md`.

The migration must create a non-empty `ansible/Makefile` containing a default `all` target that invokes `ansible-playbook`:

```makefile
.PHONY: all

all:
	ansible-playbook -i inventory site.yml
```