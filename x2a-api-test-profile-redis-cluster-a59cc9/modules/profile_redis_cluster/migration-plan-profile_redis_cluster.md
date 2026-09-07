---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: Redis cluster module that installs Redis server with custom configuration, manages authentication, memory limits, and persistence settings. Uses PuppetDB to discover cluster nodes and includes a custom fact to determine Redis role (primary/replica). Configures a single default Redis instance with cluster-ready settings.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database

**Configured Instances**:
- **default**: Primary Redis instance for cluster operation
  - Location/Path: /etc/redis/redis.conf
  - Port/Socket: 6379
  - Key Config: password auth, AOF persistence, 2048MB memory limit, allkeys-lru eviction

## File Structure

```
site-modules/role/manifests/redis_cluster.pp
site-modules/profile/manifests/cache/redis.pp
site-modules/profile_redis_cluster/manifests/init.pp
site-modules/profile_redis_cluster/manifests/install.pp
site-modules/profile_redis_cluster/templates/redis.conf.erb
site-modules/profile_redis_cluster/lib/facter/redis_role.rb
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/params.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp
site-modules/profile_redis_cluster/migration-dependencies/redis/templates/service_templates/redis.service.epp
```

## Module Explanation

The module performs operations in this order:

1. **role::redis_cluster** (`site-modules/role/manifests/redis_cluster.pp`):
   - Entry point class with conditional logic
   - Contains `Exec[default]` resource for initialization
   - Includes `profile::cache::redis`

2. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Intermediate profile class bridging role and profile_redis_cluster
   - Uses `fact('environment')` for environment-specific configuration
   - Includes `profile_redis_cluster`

3. **profile_redis_cluster** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='CHANGEME', maxmemory_mb=2048, maxmemory_policy='allkeys-lru'
   - Contains `profile_redis_cluster::install`

4. **profile_redis_cluster::install** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - Contains `redis`

5. **redis** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits from `redis::params`
   - Contains `redis::preinstall`
   - Contains `redis::install`
   - Contains `redis::config`
   - Contains `redis::service`
   - Sets ordering: `redis::preinstall -> redis::install -> redis::config ~> redis::service`

6. **redis::preinstall** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Conditional: if `$redis::manage_repo` (manages package repository setup)
   - Uses facts: `$facts['os']['name']`, `$facts['os']['family']`

7. **redis::install** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Conditional: if `$redis::manage_package`
     - `package[$redis::package_name]` → ensure: `present`
   - Conditional: if `$redis::dnf_module_stream`
     - Includes `redis::dnfmodule`
       - `package 'redis dnf module'` → ensure: `present`
   - Uses fact: `$facts['os']['family']`

8. **redis::config** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - `file[$redis::config_dir]` → owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::log_dir]` → owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::workdir]` → owner: `redis`, group: `redis`, mode: `0755`
   - Conditional: if `$redis::default_install`
     - **redis::instance 'default'**:
       - `file '/etc/redis/redis.conf'` (template `redis.conf.erb`) → mode: `0644`
         - Passes: redis_port=6379, redis_password='CHANGEME', maxmemory_mb=2048, maxmemory_policy='allkeys-lru'
       - Conditional: if `$manage_service_file`
         - `systemd::unit_file 'redis.service'` (template `redis.service.epp`) → mode: `0644`
           - Passes: ulimit_managed, ulimit, bin_path, redis_file_name, port=6379, instance_title='default', service_name='redis', service_user='redis'
       - `file '/etc/redis/redis.conf.orig'` → source from package
       - `exec 'copy /etc/redis/redis.conf.orig to /etc/redis/redis.conf'` → creates config backup
   - Iterations: `$instances.each` — Loop runs 0 times (no additional instances configured)
   - Conditional: if `$redis::ulimit_managed`
     - Includes `redis::ulimit`
       - Conditional: if `$redis::managed_by_cluster_manager`
         - `file '/etc/security/limits.d/redis.conf'` → sets ulimits
       - `file '/etc/systemd/system/redis.service.d/limit.conf'` → systemd ulimit override
   - Conditional: case `$facts['os']['family']`
     - **Debian branch**: `file '/etc/default/redis-server'` → default configuration
   - **notifies**: `file[redis.conf] ~> service[redis]`

9. **redis::service** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
   - Conditional: if `$redis::service_manage`
     - `service 'redis'` → ensure: `running`, enable: `true`

## Variables

**Variable Flow Summary**: 123+ variables across 2 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_password`: `CHANGEME` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `2048` (type: integer)
- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: Variables accessed via `fact('environment')` for deployment environment configuration
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (redis_password) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_redis_cluster::redis_password**: defined at common level, merge strategy: first
- **profile_redis_cluster::maxmemory_mb**: defined at common level, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- Redis instance parameters (123+ parameters) passed to `redis::instance` defined type require comprehensive Hiera mapping

## Custom Types and Providers

**Custom Fact: redis_role**
- File: `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- Purpose: Determines Redis role (primary/replica) by checking for 'replicaof' directive in `/etc/redis/conf.d/replica.conf`
- Platform: Linux-only
- Migration: Replace with Ansible custom fact script or setup module extension

## Dependencies

**External module dependencies**: 
- puppetlabs-stdlib (9.6.0)
- puppet-redis (11.0.0) 
- puppetlabs-apt (9.4.0)

**System package dependencies**: 
- redis-server package
- systemd (for service management)

**Service dependencies**: 
- Network target (systemd dependency)
- Redis service ordering: preinstall → install → config → service

## Puppet Facts Used

- `$facts['kernel']`: Operating system kernel type (Linux check)
- `$facts['os']['name']`: Operating system name (package management)
- `$facts['os']['family']`: Operating system family (Debian/RedHat logic)
- `$facts['networking']['fqdn']`: Fully qualified domain name (template rendering)
- `fact('environment')`: Puppet environment name (used in profile::cache::redis)

## Template Conversion Notes

**redis.conf.erb**:
- Variables: redis_port, redis_password, maxmemory_mb, maxmemory_policy, facts['networking']['fqdn']
- Logic: Straightforward variable substitution
- Renders: Once for default instance, plus any additional configured instances

**redis.service.epp**:
- Variables: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- Logic: 3 conditional blocks for ulimit and timeout settings
- Renders: Once for default instance, plus any additional configured instances

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**: 
- `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }` → discovers all nodes with Redis cluster class applied
- Used for cluster node discovery and configuration
- Migration notes: Replace with Ansible inventory queries or service discovery mechanism

## Checks for the Migration

**Files to verify**: 
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis.service`
- `/etc/security/limits.d/redis.conf`
- `/var/log/redis/redis-server.log`
- `/var/lib/redis/`
- `/etc/redis/redis.conf.orig`
- `/etc/systemd/system/redis.service.d/limit.conf`

**Service endpoints to check**: 
- Port 6379 (Redis server)

**Templates rendered**: 
- `redis.conf.erb` (1 render for default instance)
- `redis.service.epp` (1 render for default instance)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis
systemctl is-enabled redis

# Instance-specific checks
redis-cli -p 6379 ping
redis-cli -p 6379 -a CHANGEME info replication
redis-cli -p 6379 -a CHANGEME config get maxmemory
redis-cli -p 6379 -a CHANGEME config get maxmemory-policy

# Configuration validation commands
redis-server /etc/redis/redis.conf --test-memory 1
cat /etc/redis/redis.conf | grep -E "(port|requirepass|maxmemory|maxmemory-policy)"

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```