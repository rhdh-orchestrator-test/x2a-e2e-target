---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: Redis cluster management module that installs Redis server, configures cluster nodes with authentication, and manages systemd services. Uses PuppetDB queries to discover cluster members and creates Redis instances with custom configuration files and service units.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database (Redis Cluster)

**Configured Instances**:
- **default**: Primary Redis instance
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: password authentication, memory limit 256MB, LRU eviction policy

## File Structure

```
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

1. **profile_redis_cluster** (`manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - PuppetDB Query: Discovers cluster nodes with `Profile_redis_cluster` class
   - `contain profile_redis_cluster::install`

2. **profile_redis_cluster::install** (`manifests/install.pp`):
   - `contain redis`

3. **redis** (`migration-dependencies/redis/manifests/init.pp`):
   - Inherits from `redis::params`
   - `contain redis::preinstall`
   - `contain redis::install`
   - `contain redis::config`
   - `contain redis::service`
   - Iterations: `$instances.each` — Loop runs once per instance in `$instances` hash (currently empty by default)
   - Sets ordering: `redis::preinstall -> redis::install -> redis::config`
   - Sets notification: `redis::config ~> redis::service`

4. **redis::preinstall** (`migration-dependencies/redis/manifests/preinstall.pp`):
   - Conditional: if `$redis::manage_repo` (manages package repository)
   - Uses facts: `$facts['os']['name']`, `$facts['os']['family']`

5. **redis::install** (`migration-dependencies/redis/manifests/install.pp`):
   - Conditional: if `$redis::manage_package`
     - `package[$redis::package_name]` → ensure: `present`
   - Conditional: if `$redis::dnf_module_stream`
     - Includes `redis::dnfmodule`
       - `package 'redis dnf module'` → ensure: `present`
   - Uses fact: `$facts['os']['family']`

6. **redis::config** (`migration-dependencies/redis/manifests/config.pp`):
   - `file[$redis::config_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::log_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::workdir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - Conditional: if `$redis::default_install`
     - redis::instance 'default':
       - Conditional: if log_dir != redis::log_dir
         - `file[$log_dir]` → ensure: `directory`, owner: `redis`, group: `redis`
       - Conditional: if workdir != redis::workdir
         - `file[$workdir]` → ensure: `directory`, owner: `redis`, group: `redis`
       - Conditional: if `$manage_service_file`
         - `systemd::unit_file[${service_name}.service]` (template `redis.service.epp`)
           - Passes: ulimit_managed, ulimit, bin_path, redis_file_name, port=6379, instance_title='default', service_name, service_user, service_timeout_start, service_timeout_stop
       - `file[$redis_file_name_orig]` → Redis configuration file
       - `exec[copy ${redis_file_name_orig} to ${redis_file_name}]` → Configuration deployment
   - Conditional: if `$redis::ulimit_managed`
     - Includes `redis::ulimit`
       - Conditional: if `$redis::managed_by_cluster_manager`
         - `file '/etc/security/limits.d/redis.conf'` → ulimit configuration
       - `file '/etc/systemd/system/${redis::service_name}.service.d/limit.conf'` → systemd ulimit override
   - Conditional: case `$facts['os']['family']`
     - Debian: `file '/etc/default/redis-server'` → Debian-specific defaults
   - Uses fact: `$facts['os']['family']`

7. **redis::service** (`migration-dependencies/redis/manifests/service.pp`):
   - Conditional: if `$redis::service_manage`
     - `service[$redis::service_name]` → ensure: `running`, enable: `true`

## Variables

**Variable Flow Summary**: 4 variables across 2 Hiera levels

### Variable Definitions

**Class parameter defaults (init.pp)** → Migration note: Default values defined in class parameters
- `redis_port`: `6379` (type: integer)
- `redis_password`: `test-redis-password` (type: string)
- `maxmemory_mb`: `256` (type: integer)
- `maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from class parameter defaults (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: 0 variables that vary by deployment environment
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 1 variable that needs secure storage (redis_password)

### Cross-Level Overrides

Variables defined at multiple levels:
- **redis_password**: defined at class defaults, merge strategy: first
- **maxmemory_mb**: defined at class defaults, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Custom Fact: redis_role**
- File: `lib/facter/redis_role.rb`
- Purpose: Determines Redis role (primary/replica) by checking for 'replicaof' directive in `/etc/redis/conf.d/replica.conf`
- Platform: Linux-only
- Migration: Replace with Ansible custom fact script or use `setup` module with custom logic in playbook tasks

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
- Ordering: preinstall -> install -> config ~> service

## Puppet Facts Used

- `$facts['os']['name']`: Operating system name for repository management
- `$facts['os']['family']`: OS family for package management and configuration paths
- `$trusted.certname`: Node certificate name for Hiera hierarchy
- `$facts.environment`: Environment name for Hiera hierarchy
- Custom fact `redis_role`: Redis instance role determination

## Template Conversion Notes

**redis.service.epp**: Systemd service unit template
- **Variables used**: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- **Ruby logic blocks**: 3 conditional blocks for ulimit and timeout configuration
- **Conditional rendering**: Ulimit configuration based on `ulimit_managed` parameter
- **Iterations**: None
- **Complex expressions**: Conditional ulimit and timeout rendering based on parameters

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**: Cluster node discovery
- **Query**: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
- **Returned data**: List of certnames for nodes with Profile_redis_cluster class
- **Migration notes**: Replace with Ansible inventory groups or dynamic inventory scripts to discover Redis cluster members

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis.service`
- `/etc/security/limits.d/redis.conf`
- `/etc/systemd/system/redis.service.d/limit.conf`
- `/var/log/redis/`
- `/var/lib/redis/`

**Service endpoints to check**:
- Port 6379 (Redis default instance)

**Templates rendered**:
- `redis.service.epp` → `/etc/systemd/system/redis.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis
systemctl is-enabled redis

# Instance-specific checks
redis-cli -p 6379 ping
redis-cli -p 6379 info replication
redis-cli -p 6379 config get maxmemory

# Configuration validation commands
redis-server /etc/redis/redis.conf --test-memory 1

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```