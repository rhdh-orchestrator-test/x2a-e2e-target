---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: A Redis cluster management module that installs and configures Redis instances with cluster support, authentication, memory management, and systemd service integration. Uses PuppetDB queries to discover cluster nodes and includes a custom fact for role detection.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database (Redis Cluster)

**Configured Instances**:
- **default**: Primary Redis instance
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: cluster-enabled, authentication, memory limits

## File Structure

```
site-modules/role/manifests/app_server.pp
site-modules/profile/manifests/cache/redis.pp
site-modules/profile_redis_cluster/manifests/init.pp
site-modules/profile_redis_cluster/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/templates/service_templates/redis.service.epp
site-modules/profile_redis_cluster/lib/facter/redis_role.rb
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes the cache profile
   - `contain profile::cache::redis`

2. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Intermediate profile class that bridges role and specific Redis implementation
   - `contain profile_redis_cluster`

3. **profile_redis_cluster** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - PuppetDB Query: Discovers Redis cluster nodes with query `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
   - `contain profile_redis_cluster::install`

4. **profile_redis_cluster::install** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - `contain redis`

5. **redis** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits from `redis::params` for OS-specific defaults
   - `contain redis::preinstall`
   - `contain redis::install`
   - `contain redis::config`
   - `contain redis::service`
   - Sets ordering: `redis::preinstall -> redis::install -> redis::config ~> redis::service`

6. **redis::preinstall** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Conditional: if `$redis::manage_repo` (manages package repositories)
   - Uses facts: `$facts['os']['name']`, `$facts['os']['family']`

7. **redis::install** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Conditional: if `$redis::manage_package`
     - `package[$redis::package_name]` → ensure: `present`
   - Conditional: if `$redis::dnf_module_stream`
     - **redis::dnfmodule** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`):
       - `package[redis dnf module]` → provider: `dnfmodule`
   - Uses fact: `$facts['os']['family']`

8. **redis::config** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - `file[$redis::config_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::log_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::workdir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - Conditional: if `$redis::default_install`
     - **redis::instance[default]** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`):
       - Conditional: if `$log_dir != $redis::log_dir`
         - `file[$log_dir]` → ensure: `directory`, owner: `redis`, group: `redis`
       - Conditional: if `$workdir != $redis::workdir`
         - `file[$workdir]` → ensure: `directory`, owner: `redis`, group: `redis`
       - Conditional: if `$manage_service_file`
         - `systemd::unit_file[${service_name}.service]` → content from template `redis.service.epp`
       - Conditional: if `$ulimit_managed`
         - `systemd::manage_dropin[${service_name}-90-limits.conf]`
       - `file[$redis_file_name_orig]` → content from Redis configuration template
       - `exec[copy ${redis_file_name_orig} to ${redis_file_name}]` → creates final config file
   - Conditional: if `$redis::ulimit_managed`
     - **redis::ulimit** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`):
       - Conditional: if `$redis::managed_by_cluster_manager`
         - `file[/etc/security/limits.d/redis.conf]` → content: ulimit configuration
       - `file[/etc/systemd/system/${redis::service_name}.service.d/limit.conf]` → content: systemd limits
   - Conditional: case `$facts['os']['family']`
     - Branch Debian: `file[/etc/default/redis-server]` → content: Debian-specific defaults
   - Iterations: `$instances.each` — Loop execution depends on `$instances` parameter value

9. **redis::service** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
   - Conditional: if `$redis::service_manage`
     - `service[$redis::service_name]` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`

## Variables

**Variable Flow Summary**: 4 variables across class parameter defaults

### Variable Definitions

**Class parameter defaults (init.pp)** → Migration note: Default values defined in class parameters
- `redis_port`: `6379` (type: integer)
- `redis_password`: `test-redis-password` (type: string)
- `maxmemory_mb`: `256` (type: integer)
- `maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from class parameter defaults
- **OS-specific variables**: 0 variables
- **Environment-specific variables**: 0 variables
- **Host-specific variables**: 0 variables
- **Encrypted variables**: 1 variable needing secure storage (redis_password)

### Cross-Level Overrides

No cross-level overrides detected - all variables use class parameter defaults with first merge strategy.

### Merge Strategy Notes

All variables use `first` (default) merge strategy - first value found wins, no merging.

## Custom Types and Providers

**Custom Fact: redis_role**
- File: `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- Purpose: Determines Redis role (primary/replica) by checking for 'replicaof' directive in `/etc/redis/conf.d/replica.conf`
- Platform: Linux-only
- Migration: Replace with Ansible custom fact script or setup module extension

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.6.0)
- puppet-redis (version: 11.0.0)
- puppetlabs-apt (version: 9.4.0)

**System package dependencies**:
- redis-server package
- systemd (for service management)

**Service dependencies**:
- Network services (network.target, network-online.target)
- Ordering: preinstall → install → config → service

## Puppet Facts Used

- `$facts['os']['name']`: Operating system name for package management
- `$facts['os']['family']`: OS family (Debian, RedHat, etc.) for conditional logic
- `$facts['environment']`: Environment name for Hiera hierarchy
- `$trusted.certname`: Node certificate name for Hiera hierarchy

## Template Conversion Notes

**redis.service.epp**: Systemd service unit file template
- Variables: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- Logic blocks: 3 conditional blocks for ulimit and timeout settings
- Render count: 1 per Redis instance (default: 1)

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Query**: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
- Purpose: Discovers all nodes in the Redis cluster for cluster configuration
- Migration notes: Replace with Ansible inventory groups or dynamic inventory scripts for cluster member discovery
- Usage: Populates `$redis_nodes` variable for cluster member discovery

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf` (main configuration)
- `/etc/systemd/system/redis.service` (systemd unit file)
- `/etc/security/limits.d/redis.conf` (ulimits)
- `/var/log/redis/` (log directory)
- `/var/lib/redis/` (data directory)

**Service endpoints to check**:
- Port 6379 (Redis default port)
- Redis cluster bus port (16379)

**Templates rendered**:
- `redis.service.epp` → `/etc/systemd/system/redis.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis

# Instance-specific checks
redis-cli ping

# Configuration validation commands
redis-cli cluster nodes

# Network/connectivity checks
netstat -tlnp | grep 6379
netstat -tlnp | grep 16379
```