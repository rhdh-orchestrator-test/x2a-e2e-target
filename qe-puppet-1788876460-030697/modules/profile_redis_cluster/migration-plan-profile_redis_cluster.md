---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: A Redis cluster management module that installs and configures Redis instances with cluster discovery via PuppetDB queries. Sets up Redis with authentication, memory limits, and systemd service management. Uses a dependency module for Redis installation and configuration.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database (Redis Cluster)

**Configured Instances**:
- **default**: Primary Redis instance
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: password authentication, 256MB memory limit, allkeys-lru eviction policy

## File Structure

```
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

1. **role::app_server** (`manifests/roles/app_server.pp`):
   - Entry point class that includes profile::cache::redis

2. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Profile wrapper that contains profile_redis_cluster class

3. **profile_redis_cluster** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - **PuppetDB Query**: Discovers Redis cluster nodes by querying for all nodes with `Profile_redis_cluster` class
   - `contain profile_redis_cluster::install`

4. **profile_redis_cluster::install** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - `contain redis` (dependency module)

5. **redis** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits from `redis::params` for OS-specific defaults
   - `contain redis::preinstall`
   - `contain redis::install`
   - `contain redis::config`
   - `contain redis::service`
   - Sets ordering: `redis::preinstall -> redis::install -> redis::config ~> redis::service`

6. **redis::preinstall** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - **Conditional**: if `$redis::manage_repo` (manages package repository setup)
   - Uses facts: `$facts['os']['name']`, `$facts['os']['family']`

7. **redis::install** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - **Conditional**: if `$redis::manage_package`
     - `package[$redis::package_name]` → ensure: `present`
   - **Conditional**: if `$redis::dnf_module_stream`
     - Includes `redis::dnfmodule` for DNF module management
       - `package 'redis dnf module'` → ensure: `present`
   - Uses fact: `$facts['os']['family']`

8. **redis::config** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - `file[$redis::config_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::log_dir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file[$redis::workdir]` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - **Conditional**: if `$redis::default_install`
     - **redis::instance 'default'** (123 parameters):
       - **Conditional**: if `$log_dir != $redis::log_dir`
         - `file[$log_dir]` → ensure: `directory`, owner: `redis`, group: `redis`
       - **Conditional**: if `$workdir != $redis::workdir`
         - `file[$workdir]` → ensure: `directory`, owner: `redis`, group: `redis`
       - **Conditional**: if `$manage_service_file`
         - `systemd::unit_file '${service_name}.service'` (template `redis.service.epp`) → mode: `0644`
           - Passes: ulimit_managed, ulimit, bin_path, redis_file_name, port=6379, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
       - `file[$redis_file_name_orig]` → Redis configuration file
       - `exec 'copy ${redis_file_name_orig} to ${redis_file_name}'` → Configuration file deployment
   - **Conditional**: if `$redis::ulimit_managed`
     - Includes `redis::ulimit`:
       - **Conditional**: if `$redis::managed_by_cluster_manager`
         - `file '/etc/security/limits.d/redis.conf'` → ulimit configuration
       - `file '/etc/systemd/system/${redis::service_name}.service.d/limit.conf'` → systemd ulimit override
   - **Conditional**: case `$facts['os']['family']`
     - **Branch Debian**: `file '/etc/default/redis-server'` → Debian-specific defaults
     - **Branch default**: No additional configuration

9. **redis::service** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
   - **Conditional**: if `$redis::service_manage`
     - `service[$redis::service_name]` → ensure: `running`, enable: `true`

   - Iterations: `$instances.each` — Loop runs 0 times (no additional instances configured)

## Variables

**Variable Flow Summary**: 2 variables across 1 Hiera level

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

### Variable Migration Summary

- **Common defaults**: 2 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: 0 variables that vary by deployment environment
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 0 variables that are encrypted (passwords are in plaintext)

### Cross-Level Overrides

No variables defined at multiple levels.

### Merge Strategy Notes

All variables use `first` (default) merge strategy - first value found wins, no merging.

## Custom Types and Providers

**Custom Fact: redis_role**
- File: `lib/facter/redis_role.rb`
- Purpose: Determines Redis role (primary/replica) by checking for 'replicaof' directive in `/etc/redis/conf.d/replica.conf`
- Platform: Linux-only
- Migration: Replace with Ansible custom fact script or setup module extension

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.6.0)
- puppet-redis (version: 11.0.0) - bundled in migration-dependencies
- puppetlabs-apt (version: 9.4.0)

**System package dependencies**:
- redis-server package
- systemd for service management

**Service dependencies**:
- Network services (network.target, network-online.target)
- Ordering: preinstall → install → config → service

## Puppet Facts Used

- `$facts['os']['name']`: Operating system name for package management
- `$facts['os']['family']`: OS family (Debian, RedHat) for conditional configuration
- `$facts['environment']`: Environment context for configuration
- `$trusted.certname`: Node certificate name for PuppetDB queries

## Template Conversion Notes

**redis.service.epp**: Systemd service unit template
- **Variables used**: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- **Logic blocks**: 3 conditional blocks for ulimit and timeout settings
- **Render count**: 1 per Redis instance (default: 1)
- **Complex expressions**: Conditional ulimit and timeout configuration

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**: Cluster node discovery
- **Query**: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
- **Purpose**: Finds all nodes running the Redis cluster profile for cluster formation
- **Migration notes**: Replace with Ansible inventory groups or dynamic inventory scripts for node discovery

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf` - Redis configuration
- `/etc/systemd/system/redis.service` - Systemd service unit
- `/etc/security/limits.d/redis.conf` - Process limits (if ulimit_managed)
- `/var/log/redis/` - Log directory
- `/var/lib/redis/` - Data directory

**Service endpoints to check**:
- Port 6379 (Redis default port)
- Redis authentication with password 'test-redis-password'

**Templates rendered**:
- `redis.service.epp` → `/etc/systemd/system/redis.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis

# Instance-specific checks
redis-cli ping
redis-cli info memory
redis-cli config get maxmemory

# Configuration validation commands
redis-server --test-config /etc/redis/redis.conf

# Network/connectivity checks
netstat -tlnp | grep :6379
```