---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: A Redis cluster management module that configures Redis instances with authentication, memory limits, and cluster discovery via PuppetDB queries. Sets up Redis server with systemd service management, configuration templating, and ulimit handling.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database

**Configured Instances**:
- **default**: Redis server instance
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: password authentication, 256MB memory limit, allkeys-lru eviction policy

## File Structure

```
site-modules/profile_redis_cluster/
├── manifests/
│   ├── init.pp
│   └── install.pp
├── migration-dependencies/
│   └── redis/
│       ├── manifests/
│       │   ├── init.pp
│       │   ├── preinstall.pp
│       │   ├── install.pp
│       │   ├── config.pp
│       │   ├── service.pp
│       │   ├── instance.pp
│       │   ├── ulimit.pp
│       │   └── dnfmodule.pp
│       └── templates/
│           ├── redis.conf.epp
│           └── service_templates/
│               └── redis.service.epp
└── lib/
    └── facter/
        └── redis_role.rb

site-modules/profile/manifests/cache/redis.pp
site-modules/role/manifests/app_server.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes `profile::cache::redis`
   - Establishes the role-based deployment pattern

2. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Includes `profile_redis_cluster` class
   - Uses `fact('environment')` for environment-specific configuration

3. **profile_redis_cluster** (`manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - **PuppetDB Query**: `puppetdb_query("resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }")` → discovers cluster nodes
   - `contain profile_redis_cluster::install`

4. **profile_redis_cluster::install** (`manifests/install.pp`):
   - `contain redis`

5. **redis** (`migration-dependencies/redis/manifests/init.pp`):
   - Inherits from `redis::params`
   - `contain redis::preinstall`
   - `contain redis::install`
   - `contain redis::config`
   - `contain redis::service`
   - Sets ordering: `redis::preinstall -> redis::install -> redis::config ~> redis::service`

6. **redis::preinstall** (`migration-dependencies/redis/manifests/preinstall.pp`):
   - **Conditional**: if `$redis::manage_repo` (default: false) → no repository management
   - Uses facts: `$facts['os']['name']`, `$facts['os']['family']`

7. **redis::install** (`migration-dependencies/redis/manifests/install.pp`):
   - **Conditional**: if `$redis::manage_package` (default: true):
     - `package 'redis-server'` → ensure: `present`
   - **Conditional**: if `$redis::dnf_module_stream` (default: undef) → no DNF module management
   - Uses fact: `$facts['os']['family']`

8. **redis::config** (`migration-dependencies/redis/manifests/config.pp`):
   - `file '/etc/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/log/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/lib/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - **Conditional**: if `$redis::default_install` (default: true):
     - **redis::instance 'default'**:
       - `file '/var/log/redis'` → owner: `redis`, group: `redis`, mode: `0755` (if different from redis::log_dir)
       - `file '/var/lib/redis'` → owner: `redis`, group: `redis`, mode: `0755` (if different from redis::workdir)
       - **Conditional**: if `$manage_service_file` (default: true):
         - `systemd::unit_file 'redis.service'` (template `service_templates/redis.service.epp`) → mode: `0644`
           - Passes: ulimit_managed=true, ulimit=65535, bin_path='/usr/bin', redis_file_name='/etc/redis/redis.conf', port=6379, instance_title='default', service_name='redis', service_user='redis'
       - `file '/etc/redis/redis.conf'` (template `redis.conf.epp`) → owner: `redis`, group: `redis`, mode: `0640`
         - Passes: 123 parameters including port=6379, requirepass='test-redis-password', maxmemory='256mb', maxmemory_policy='allkeys-lru'
       - `exec 'copy /etc/redis/redis.conf to /etc/redis/redis.conf'` → creates: `/etc/redis/redis.conf`
   - **Iterations**: `$instances.each` — Loop runs 0 times (no additional instances configured)
   - **Conditional**: if `$redis::ulimit_managed` (default: true):
     - **redis::ulimit**:
       - **Conditional**: if `$redis::managed_by_cluster_manager` (default: false) → no cluster manager limits
       - `file '/etc/systemd/system/redis.service.d/limit.conf'` → content: `[Service]\nLimitNOFILE=65535`, mode: `0644`
   - **Conditional**: case `$facts['os']['family']`:
     - **Debian**: `file '/etc/default/redis-server'` → content: `ULIMIT=65535`, mode: `0644`
   - Uses fact: `$facts['os']['family']`

9. **redis::service** (`migration-dependencies/redis/manifests/service.pp`):
   - **Conditional**: if `$redis::service_manage` (default: true):
     - `service 'redis'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`

## Variables

**Variable Flow Summary**: 4 variables across 2 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables
- **Environment-specific variables**: 0 variables
- **Host-specific variables**: 0 variables
- **Encrypted variables**: 1 variable that is encrypted (redis_password) and needs secure storage

### Cross-Level Overrides

No variables defined at multiple levels.

### Merge Strategy Notes

All variables use `first` (default) merge strategy - first value found wins, no merging.

## Custom Types and Providers

**Custom Fact: redis_role**
- File: `lib/facter/redis_role.rb`
- Purpose: Determines Redis role by checking for replica configuration
- Migration: Replace with Ansible custom fact script or gathered_facts via setup module

## Dependencies

**External module dependencies**: 
- puppetlabs-stdlib (9.6.0)
- puppet-redis (11.0.0)
- puppetlabs-apt (9.4.0)

**System package dependencies**: 
- redis-server

**Service dependencies**: 
- Network target (systemd)
- Network-online target (systemd)

## Puppet Facts Used

- `$facts['os']['name']`: Operating system name for package management
- `$facts['os']['family']`: OS family (Debian/RedHat) for conditional configuration
- `fact('environment')`: Environment name for cluster discovery

## Template Conversion Notes

**redis.conf.epp**: 123 variables including complex Redis configuration parameters, conditional blocks for replication settings, memory management, persistence options, and security settings. Contains Ruby logic for array processing and conditional rendering.

**service_templates/redis.service.epp**: 10 variables with 3 logic blocks for systemd service configuration, ulimit management, and timeout settings.

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**: `puppetdb_query("resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }")` - discovers all nodes with Redis cluster class for cluster formation, migration notes: Must be replaced with Ansible inventory-based discovery or external service discovery mechanism

## Checks for the Migration

**Files to verify**: 
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis.service`
- `/etc/systemd/system/redis.service.d/limit.conf`
- `/etc/default/redis-server` (Debian only)
- `/var/log/redis/` (directory)
- `/var/lib/redis/` (directory)

**Service endpoints to check**: 
- Port 6379 (Redis server)

**Templates rendered**: 
- `redis.conf.epp` → `/etc/redis/redis.conf` (1 render via redis::instance 'default')
- `service_templates/redis.service.epp` → systemd unit file (1 render via redis::instance 'default')

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis

# Instance-specific checks
redis-cli -p 6379 ping
redis-cli -p 6379 auth test-redis-password

# Configuration validation commands
redis-cli -p 6379 config get maxmemory
redis-cli -p 6379 config get maxmemory-policy

# Network/connectivity checks
netstat -tlnp | grep :6379
redis-cli -p 6379 info memory
```