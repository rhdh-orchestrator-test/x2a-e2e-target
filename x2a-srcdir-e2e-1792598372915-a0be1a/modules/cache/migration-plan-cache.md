---
source-path: cookbooks/cache
---

# Migration Plan: cache

**TLDR**: This cookbook provisions a local Redis cache service on supported Ubuntu or CentOS systems. It installs the `redis-server` system package and enables and starts the `redis-server` service. The cookbook contains one recipe, no loops, templates, custom resources, configuration overrides, credentials, or external cookbook dependencies.

## Service Type and Instances

**Service Type**: Cache

**Configured Instances**:

- **redis-server**: System-level Redis cache service
  - Package: `redis-server`
  - Service: `redis-server`
  - Service actions: Enabled at boot and started immediately
  - Location/Path: Package-managed and platform-dependent
  - Port/Socket: TCP port `6379` is the standard expected port; no port or socket is explicitly configured by the cookbook
  - Key Config: No configuration files, data paths, log paths, or network interfaces are managed by this cookbook

**Iterations**: None. The recipe contains no collection attributes and no `.each` loops.

## File Structure

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

The `metadata.rb` file was inspected for service identification and platform support, but it is not an executed recipe and is not included in the executable file list.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/cache/recipes/default.rb`):
   - Installs the `redis-server` package.
   - Enables the `redis-server` service at boot.
   - Starts the `redis-server` service immediately.
   - Resources used:
     - `package` (1)
     - `service` (1)
   - Files or templates deployed: None
   - Iterations: None

The equivalent migration behavior is:

1. Install the `redis-server` package without a version constraint.
2. Enable the `redis-server` service.
3. Start the `redis-server` service.

No included recipes, conditional branches, custom resources, providers, configuration files, handlers, or rendered templates are present.

## Dependencies

**External cookbook dependencies**: None listed in the available metadata.

**System package dependencies**:

- `redis-server`

**Service dependencies**:

- `redis-server`

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The Chef cookbook explicitly uses the `redis-server` service name. The migration should use that name unless platform testing demonstrates that the target distribution provides a different Redis unit name.

## Credentials

**Detection Summary**: 0 credentials detected across the analyzed recipe and metadata.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No data bags, encrypted data bags, Chef Vault items, Conjur or CyberArk references, vault attributes, secret environment variables, database connection strings, hardcoded passwords, API keys, tokens, or TLS certificate references were found.

No credentials or secrets need to be configured in AAP for this cookbook migration.

## Checks for the Migration

**Files to verify**:

- `cookbooks/cache/recipes/default.rb`
- `metadata.rb`
- Package-managed Redis configuration location: Platform-dependent and not managed by this cookbook
- Package-managed Redis data and log locations: Platform-dependent and not managed by this cookbook

**Service endpoints to check**:

- **redis-server**: TCP port `6379`, unless the package-provided configuration has been customized
- Unix sockets: None configured by this cookbook
- Network interfaces: None configured by this cookbook

**Templates rendered**:

- None (0)

**Service restart/reload behavior**:

- None defined. The cookbook only installs the package and enables and starts the service. It does not manage Redis configuration or trigger restart or reload handlers.

## Pre-flight checks:

```bash
# Verify the redis-server package is installed
dpkg-query -W -f='${Status}\n' redis-server 2>/dev/null || \
rpm -q redis-server

# Verify the redis-server service is enabled at boot
systemctl is-enabled redis-server

# Verify the redis-server service is running
systemctl is-active redis-server

# Inspect the redis-server service status
systemctl status redis-server --no-pager

# Verify the redis-server instance responds
redis-cli -h 127.0.0.1 -p 6379 PING

# Display Redis server information
redis-cli -h 127.0.0.1 -p 6379 INFO server

# Verify a basic Redis write/read operation
redis-cli -h 127.0.0.1 -p 6379 SET chef_migration_check ok
redis-cli -h 127.0.0.1 -p 6379 GET chef_migration_check
redis-cli -h 127.0.0.1 -p 6379 DEL chef_migration_check

# Verify the redis-server instance is listening on the expected port
ss -ltnp | grep ':6379'

# Alternative listening-port check
netstat -ltnp 2>/dev/null | grep ':6379'

# Identify the Redis process
ps -ef | grep '[r]edis-server'

# Check effective Redis configuration
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET bind
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET port
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET dir
redis-cli -h 127.0.0.1 -p 6379 CONFIG GET dbfilename

# Review recent redis-server logs
journalctl -u redis-server --no-pager -n 100

# Review redis-server errors from the current boot
journalctl -u redis-server -b --priority=err --no-pager
```

Expected results:

- The package query reports `redis-server` as installed.
- `systemctl is-enabled redis-server` reports `enabled`.
- `systemctl is-active redis-server` reports `active`.
- The Redis health check returns `PONG`.
- The write/read test returns `OK`, then `ok`, and the cleanup returns `1`.
- The effective Redis `port` configuration normally reports `6379`.
- The effective Redis `dir` configuration identifies the package-managed data directory, which should exist and be writable by the Redis service account.