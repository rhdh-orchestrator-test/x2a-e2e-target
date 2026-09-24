---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: role_app_server

**TLDR**: A complete application server role that configures Redis cluster caching through a layered profile architecture. The role manages Redis instances with cluster support, authentication, memory management, and systemd service management, using PuppetDB queries for cluster node discovery and custom facts for role detection.

## Service Type and Instances

**Service Type**: Application Server with Cache Layer (Redis Cluster)

**Configured Instances**:
- **redis-default**: Primary Redis cache instance
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: password authentication, 256MB memory limit, allkeys-lru eviction policy

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
   - Entry point for application server configuration
   - `contain profile::cache::redis`

2. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Cache layer profile wrapper
   - `contain profile_redis_cluster`

3. **profile_redis_cluster** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - PuppetDB Query: Discovers Redis cluster nodes via `puppetdb_query()` for cluster formation
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
   - Conditional: if `$redis::manage_repo` (manages package repository)
   - Uses facts: `$facts['os']['name']`, `$facts['os']['family']`

7. **redis::install** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Conditional: if `$redis::manage_package`
     - `package[$redis::package_name]` → ensure: `present`
   - Conditional: if `$redis::dnf_module_stream`
     - **redis::dnfmodule** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`):
       - `package[redis dnf module]` → ensure: `present`
   - Uses fact: `$facts['os']['family']`

8. **redis::config** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - `file[$redis::config_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::log_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::workdir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - Conditional: if `$redis::default_install`
     - **redis::instance[default]** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`):
       - Conditional: if `$log_dir != $redis::log_dir`
         - `file[$log_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
       - Conditional: if `$workdir != $redis::workdir`
         - `file[$workdir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
       - Conditional: if `$manage_service_file`
         - `systemd::unit_file[redis.service]` (template `redis.service.epp`) → mode: `0644`
           - Passes: ulimit_managed, ulimit, bin_path, redis_file_name, port=6379, instance_title='default', service_name='redis', service_user='redis', service_timeout_start, service_timeout_stop
       - `file[/etc/redis/redis.conf]` → mode: `0640`, owner: `redis`, group: `redis`
       - `exec[copy /etc/redis/redis.conf to /etc/redis/redis.conf]` → creates config file
   - Conditional: if `$redis::ulimit_managed`
     - **redis::ulimit** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`):
       - Conditional: if `$redis::managed_by_cluster_manager`
         - `file[/etc/security/limits.d/redis.conf]` → mode: `0644`
       - `file[/etc/systemd/system/redis.service.d/limit.conf]` → mode: `0644`
   - Conditional: case `$facts['os']['family']`
     - Branch: Debian
       - `file[/etc/default/redis-server]` → mode: `0644`
   - Iterations: `$instances.each` — Loop runs 0 times (no additional instances configured based on current configuration)

9. **redis::service** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
   - Conditional: if `$redis::service_manage`
     - `service[redis]` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`

## Variables

**Variable Flow Summary**: 4 variables across 2 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

**Class parameter defaults (init.pp)** → Migration note: Hardcoded class defaults
- `redis_port`: `6379` (type: integer)
- `maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 2 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: 0 variables that vary by deployment environment
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted and needs secure storage (redis_password)

### Cross-Level Overrides

Variables defined at multiple levels:
- **profile_redis_cluster::redis_password**: defined at common.yaml and class defaults, merge strategy: first
- **profile_redis_cluster::maxmemory_mb**: defined at common.yaml and class defaults, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Custom Fact: redis_role**
- **File**: `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`
- **Purpose**: Determines Redis role by checking for replica configuration file and 'replicaof' directive
- **Returns**: 'replica' if found, 'primary' otherwise
- **Migration**: Replace with Ansible custom fact script or gathered_facts via setup module with custom logic in playbook tasks

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.6.0)
- puppet-redis (version: 11.0.0)
- puppetlabs-apt (version: 9.4.0)

**System package dependencies**:
- redis-server package
- systemd for service management

**Service dependencies**:
- Network services (network.target, network-online.target)
- Ordering: preinstall -> install -> config ~> service

## Puppet Facts Used

- `$facts['os']['name']`: Operating system name for package repository management
- `$facts['os']['family']`: Operating system family for conditional configuration (Debian vs others)
- `fact('environment')`: Environment name for cluster node discovery

## Template Conversion Notes

**redis.service.epp**: Systemd service unit file template
- **Variables used**: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- **Ruby logic blocks**: 3 conditional blocks for ulimit and timeout settings
- **Conditional rendering**: LimitNOFILE directive based on ulimit_managed flag
- **Complex expressions**: Conditional rendering of TimeoutStartSec and TimeoutStopSec directives based on service_timeout variables

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**: 1 query in profile_redis_cluster
- **Query**: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
- **Purpose**: Discovers all nodes in the cluster that have the Redis cluster profile applied for cluster formation
- **Migration notes**: Replace with Ansible inventory groups or dynamic inventory scripts to identify cluster members

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis.service`
- `/etc/security/limits.d/redis.conf`
- `/etc/systemd/system/redis.service.d/limit.conf`
- `/etc/default/redis-server` (Debian only)

**Service endpoints to check**:
- Port 6379 (Redis default instance)

**Templates rendered**:
- `redis.service.epp` → `/etc/systemd/system/redis.service` (1 render for default instance)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis

# Instance-specific checks
redis-cli -p 6379 ping

# Configuration validation commands
redis-server --test-config /etc/redis/redis.conf

# Network/connectivity checks
netstat -tlnp | grep :6379
redis-cli -p 6379 info replication
```