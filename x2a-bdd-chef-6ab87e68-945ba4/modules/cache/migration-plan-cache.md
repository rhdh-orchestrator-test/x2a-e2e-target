---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook configures two cache services: the Memcached instance `memcached` on TCP/UDP port `11211` and the Redis instance `redis` on TCP port `6379`. Memcached is started and enabled through the `memcached_instance` custom resource. Redis is configured through the external `redisio` cookbook with password authentication, a `/run/redis` PID directory, a `/var/log/redis` log directory, and cleanup of five replication-related directives from `/etc/redis/6379.conf`. The Redis implementation files were not supplied, so exact Redis package, service, template, and provider names must be determined from the target platform.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **memcached**: Memcached cache service
  - Location/Path: Memcached package configuration path selected by the target operating system
  - Port/Socket: TCP `11211`, UDP `11211`
  - Key Config: Listen on `0.0.0.0`; memory `64` MB; maximum connections `1024`; maximum object size `1m`; user `service_user`; ulimit `1024`; experimental and extra CLI options empty; actions `start` and `enable`
  - Worker threads: Sourced from `node['memcached']['threads']`; no value is defined in the supplied attributes file and must not be guessed

- **redis**: Redis cache service
  - Location/Path: `/etc/redis/6379.conf`
  - Port/Socket: TCP `6379`
  - Key Config: Password authentication enabled; PID base directory `/run/redis`; log directory `/var/log/redis`; log directory owner and group `redis:redis`; log directory mode `0755`; recursive directory creation
  - Post-configuration cleanup: Removes `replica-serve-stale-data`, `replica-read-only`, `repl-ping-replica-period`, `client-output-buffer-limit`, and `replica-priority` directives when present

The Redis configuration contains one server entry on port `6379`. No Redis replica instances or Redis iteration collection are configured.

## File Structure

The following is the complete directory and file listing supplied for the cookbook and its dependency.

**Recipes:**
```text
cookbooks/cache/recipes/default.rb
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb
```

**Providers:**
```text
```

The `memcached_instance[memcached]` custom resource is used, but no provider file path was supplied. Its equivalent must be implemented directly with Ansible tasks and a service definition.

**Templates:**
```text
```

No rendered templates are present in the supplied execution tree.

**Attributes:**
```text
migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb
```

**Files:**
```text
```

No static files deployed through `cookbook_file` or `remote_file` are present.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Includes the Memcached dependency recipe `memcached::default`, resolved from `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`.
   - Configures one Redis server entry with port `6379`.
   - Sets Redis password authentication.
   - Sets the Redis PID base directory to `/run/redis`.
   - Includes the external `redisio` installation and configuration recipe. Its source file was not available in the supplied execution tree.
   - Creates `/var/log/redis` recursively with owner `redis`, group `redis`, and mode `0755`.
   - Executes `ruby_block[fix_redis_config]` against `/etc/redis/6379.conf`.
   - Removes lines matching the following patterns when the configuration file exists:
     - `^replica-serve-stale-data.*$`
     - `^replica-read-only.*$`
     - `^repl-ping-replica-period.*$`
     - `^client-output-buffer-limit.*$`
     - `^replica-priority.*$`
   - Includes `redisio::enable` to enable Redis at boot. Its source file and exact service name were not available.
   - Resources: `directory[/var/log/redis]` and `ruby_block[fix_redis_config]`.

2. **default** (`migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`):
   - Invokes the custom resource `memcached_instance[memcached]`.
   - Starts and enables the `memcached` instance.
   - Configures memory `64` MB.
   - Configures TCP port `11211` and UDP port `11211`.
   - Binds to `0.0.0.0`.
   - Configures maximum connections `1024`.
   - Configures maximum object size `1m`.
   - Uses user `service_user`.
   - Passes `node['memcached']['threads']`, whose value is undefined in the supplied defaults.
   - Sets ulimit `1024`.
   - Passes empty `experimental_options` and `extra_cli_options` collections.

3. **redisio** (referenced by `cookbooks/cache/recipes/default.rb`; source path unavailable):
   - Must provide Redis on port `6379`.
   - Must enable password authentication.
   - Must use `/run/redis` as the PID base directory.
   - Must create or use `/var/log/redis`.
   - Must provide the Redis configuration represented by `/etc/redis/6379.conf`.
   - Exact package, template, provider, and service implementation details cannot be derived from the supplied files.

4. **redisio::enable** (referenced by `cookbooks/cache/recipes/default.rb`; source path unavailable):
   - Must enable the Redis service at boot.
   - The exact Redis service name must be determined from the target operating system and installed package.

### Observable attribute values

The supplied Memcached attributes define:

- `node['memcached']['version']`: `nil`
- `node['memcached']['memory']`: `64`
- `node['memcached']['port']`: `11211`
- `node['memcached']['udp_port']`: `11211`
- `node['memcached']['listen']`: `0.0.0.0`
- `node['memcached']['maxconn']`: `1024`
- `node['memcached']['max_object_size']`: `1m`
- `node['memcached']['experimental_options']`: `[]`
- `node['memcached']['extra_cli_options']`: `[]`
- `node['memcached']['ulimit']`: `1024`
- `node['memcached']['logfilepath']`: `/var/log/memcached`

The cache recipe defines:

- One Redis server entry on port `6379`
- Redis password authentication
- `replicaservestaledata`: `nil`
- `node['redisio']['base_piddir']`: `/run/redis`

## Dependencies

**External cookbook dependencies**:

- `memcached`, version constraint `~> 6.0`
- `redisio`, no version constraint

**Supported platforms declared in metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- A platform-equivalent Memcached package
- A platform-equivalent Redis server package

Exact package names are not present in the supplied execution tree and must be verified against the target operating system. Do not infer package names from the unavailable `redisio` implementation.

**Service dependencies**:

- `memcached`: started and enabled by `memcached_instance[memcached]`
- `redis`: configured by `redisio` and enabled by `redisio::enable`; exact service name must be verified on the target host

## Credentials

**Detection Summary**: 1 credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### Redis authentication password

- **Variable(s)**: `node['redisio']['servers'][0]['requirepass']`
- **Source file(s)**: `cookbooks/cache/recipes/default.rb`
- **Current storage**: Hardcoded Chef node attribute value
- **Usage context**: Configures Redis `requirepass` authentication for the `redis` instance on port `6379`
- **Migration storage**: Move the password to Ansible Vault, such as `group_vars/cache/vault.yml`, using a variable named `redis_password`
- **Security requirement**: Do not store the literal password in committed Ansible variables or diagnostic output

No data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur variables, HashiCorp Vault references, AWS Secrets Manager references, environment-variable secrets, TLS certificates, private keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/recipes/default.rb`
- `migration-dependencies/cookbook_artifacts/memcached-7992788f1a376defb902059063f5295e37d281cb/attributes/default.rb`
- `/etc/redis/6379.conf`
- `/var/log/redis`
- `/run/redis`
- The target operating system’s Memcached configuration file
- The target operating system’s Memcached service unit or init configuration
- The target operating system’s Redis service unit or init configuration

**Service endpoints to check**:

- Memcached TCP: `0.0.0.0:11211`
- Memcached UDP: `0.0.0.0:11211`
- Redis TCP: `0.0.0.0:6379` or the effective Redis bind address

**Templates rendered**: None identified; `0` rendered templates.

**Unix sockets**: None configured.

**Configuration mutations**:

- `/etc/redis/6379.conf` is modified by removing five replication-related directive patterns.

## Pre-flight checks

```bash
# Memcached instance: memcached
systemctl status memcached
systemctl is-enabled memcached
systemctl is-active memcached
ss -tlnp | grep ':11211'
ss -ulnp | grep ':11211'
nc -vz 127.0.0.1 11211
printf "stats\r\nquit\r\n" | nc 127.0.0.1 11211
ps aux | grep '[m]emcached'

# Verify Memcached configuration values using the target platform's configuration path
grep -E '(^|\s)(-m|memory|64|11211|-l|0\.0\.0\.0|-c|1024)' /etc/memcached.conf

# Redis instance: redis
systemctl status redis
systemctl status redis-server
systemctl is-enabled redis
systemctl is-enabled redis-server
ss -tlnp | grep ':6379'
nc -vz 127.0.0.1 6379

# Use the Ansible Vault-managed password through the environment
redis-cli -p 6379 -a "$REDIS_PASSWORD" PING
redis-cli -p 6379 -a "$REDIS_PASSWORD" INFO server | head -20
redis-cli -p 6379 PING

# Redis configuration
test -f /etc/redis/6379.conf
grep -E '^(port|requirepass|dir|pidfile|logfile|bind)' /etc/redis/6379.conf
grep -E '^port\s+6379$' /etc/redis/6379.conf
grep -E '^requirepass\s+' /etc/redis/6379.conf
grep -E '^(replica-serve-stale-data|replica-read-only|repl-ping-replica-period|client-output-buffer-limit|replica-priority)' /etc/redis/6379.conf

# Redis directories
stat -c '%A %U %G %n' /var/log/redis
stat -c '%A %U %G %n' /run/redis
ls -lah /var/log/redis
ls -lah /run/redis

# Redis logs; use the service name that exists on the target host
journalctl -u redis --no-pager -n 50
journalctl -u redis-server --no-pager -n 50
find /var/log/redis -maxdepth 1 -type f -print
```

Expected results:

- `memcached` is active and enabled.
- Memcached listens on TCP and UDP port `11211`.
- Memcached reports a valid `STAT` response.
- Memcached uses 64 MB memory, maximum connections `1024`, maximum object size `1m`, listen address `0.0.0.0`, and ulimit `1024` where exposed.
- `redis` is active and enabled at boot.
- Redis listens on TCP port `6379`.
- Authenticated Redis access returns `PONG`.
- Unauthenticated Redis access returns an authentication-required error.
- `/var/log/redis` exists with ownership `redis:redis` and mode `0755`.
- `/run/redis` exists or is created by the Redis service.
- No active lines matching the five removed replication-related directive patterns remain in `/etc/redis/6379.conf`.
- Redis remains active after configuration cleanup.

## Migration Requirements

The Ansible migration must preserve the following execution order:

1. Install and configure Memcached.
2. Start and enable the `memcached` service.
3. Install and configure Redis.
4. Create `/run/redis` and `/var/log/redis` with required ownership and permissions.
5. Apply Redis authentication using an Ansible Vault variable.
6. Remove the five unwanted Redis directive patterns from `/etc/redis/6379.conf`.
7. Restart or reload Redis only when its configuration changes.
8. Enable and start the Redis service.

Use `ansible.builtin.package` for verified platform-specific packages, `ansible.builtin.file` for Redis directories, `ansible.builtin.template` or `ansible.builtin.lineinfile` for Redis configuration, `ansible.builtin.replace` for directive cleanup, and `ansible.builtin.service` for service management.

The generated project must preserve the FLPATH-4982 BDD requirement in both `INPUT-AGENTS.md` and `EXPORT-AGENTS.md`:

- Create a non-empty `ansible/Makefile`.
- Define a default `all` target.
- The default target must invoke `ansible-playbook`.

A compliant Makefile is:

```make
.PHONY: all

all:
	ansible-playbook -i inventory site.yml
```