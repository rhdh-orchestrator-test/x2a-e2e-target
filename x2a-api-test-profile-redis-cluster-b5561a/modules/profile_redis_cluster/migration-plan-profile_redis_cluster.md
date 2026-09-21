---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: Redis cluster module that installs and configures Redis instances with cluster support, authentication, and memory management. Uses PuppetDB queries to discover cluster nodes and includes a custom fact for role detection. Configures a default Redis instance with cluster settings, authentication, and memory limits.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database (Redis Cluster)

**Configured Instances**:
- **default**: Primary Redis instance
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: cluster-enabled, authentication, memory limits

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
│       │   ├── dnfmodule.pp
│       │   └── params.pp
│       └── templates/
│           ├── redis.conf.epp
│           └── service_templates/
│               └── redis.service.epp
└── lib/
    └── facter/
        └── redis_role.rb
```

## Module Explanation

The module performs operations in this order:

1. **profile_redis_cluster** (`manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - **PuppetDB Query**: Discovers Redis cluster nodes using `puppetdb_query()` for nodes with `Profile_redis_cluster` class
   - `contain profile_redis_cluster::install`

2. **profile_redis_cluster::install** (`manifests/install.pp`):
   - `contain redis`

3. **redis** (`migration-dependencies/redis/manifests/init.pp`):
   - Sets Redis parameters from class defaults and Hiera overrides
   - `contain redis::preinstall`
   - `contain redis::install` 
   - `contain redis::config`
   - `contain redis::service`
   - **Ordering**: `redis::preinstall -> redis::install -> redis::config ~> redis::service`

4. **redis::preinstall** (`migration-dependencies/redis/manifests/preinstall.pp`):
   - **Conditional**: if `$redis::manage_repo` (default: true)
   - **OS Detection**: Uses `$facts['os']['name']` and `$facts['os']['family']` for repository setup

5. **redis::install** (`migration-dependencies/redis/manifests/install.pp`):
   - **Conditional**: if `$redis::manage_package` (default: true)
     - `package 'redis'` → ensure: `present`
   - **Conditional**: if `$redis::dnf_module_stream` (default: undef)
     - **redis::dnfmodule**: Manages DNF module streams for RHEL/CentOS

6. **redis::config** (`migration-dependencies/redis/manifests/config.pp`):
   - `file '/etc/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/log/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/lib/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - **Conditional**: if `$redis::default_install` (default: true)
     - **redis::instance 'default'**:
       - `file '/etc/redis/redis.conf'` (template `redis/redis.conf.epp`) → mode: `0640`, owner: `redis`, group: `redis`
         - Passes: port=6379, requirepass='test-redis-password', maxmemory='256mb', maxmemory_policy='allkeys-lru', cluster_enabled=false, bind=['127.0.0.1'], protected_mode=true, daemonize=false, supervised='auto', databases=16, save_db_to_disk=true, appendonly=false, log_level='notice'
       - `systemd::unit_file 'redis.service'` (template `redis/service_templates/redis.service.epp`) → mode: `0644`
         - Passes: service_name='redis', service_user='redis', bin_path='/usr/bin', redis_file_name='/etc/redis/redis.conf', port=6379, ulimit_managed=false
       - `exec 'copy /etc/redis/redis.conf.puppet to /etc/redis/redis.conf'` → creates: `/etc/redis/redis.conf`
   - **Iterations**: `$instances.each` — Loop runs for additional instances if configured (currently 0 additional instances)
   - **Conditional**: case `$facts['os']['family']`
     - **Debian**: `file '/etc/default/redis-server'` → content from template

7. **redis::service** (`migration-dependencies/redis/manifests/service.pp`):
   - **Conditional**: if `$redis::service_manage` (default: true)
     - `service 'redis'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`

## Variables

**Variable Flow Summary**: 4 variables across 1 Hiera level

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: 0 variables that vary by deployment environment
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (redis_password) and needs secure storage

### Cross-Level Overrides

No variables defined at multiple levels.

### Merge Strategy Notes

All variables use `first` (default) merge strategy - First value found wins, no merging.

## Custom Types and Providers

**Custom Fact: redis_role**
- **File**: `lib/facter/redis_role.rb`
- **Purpose**: Determines Redis role by checking for replica configuration file and 'replicaof' directive
- **Returns**: 'replica' if found, 'primary' otherwise
- **Migration**: Replace with Ansible custom fact script or gathered via setup module

## Dependencies

**External module dependencies**: 
- puppetlabs-stdlib (9.6.0)
- puppet-redis (11.0.0) 
- puppetlabs-apt (9.4.0)

**System package dependencies**: 
- redis (from package manager)

**Service dependencies**: 
- systemd (for service management)
- Network services (for cluster communication)

## Puppet Facts Used

- `$facts['os']['name']` - Operating system name for repository configuration
- `$facts['os']['family']` - OS family (Debian/RedHat) for package management
- `fact('environment')` - Environment name for configuration context

## Template Conversion Notes

**redis.conf.epp**: 
- **Variables**: 123 parameters including port, requirepass, maxmemory, cluster settings, TLS configuration, replication settings
- **Logic blocks**: Conditional rendering for TLS settings, cluster configuration, replication setup
- **Complex expressions**: Boolean to string conversion, array joins for bind addresses, conditional includes

**redis.service.epp**:
- **Variables**: 10 parameters including service_name, service_user, bin_path, redis_file_name, port, ulimit settings
- **Logic blocks**: 3 conditional blocks for ulimit management, timeout settings
- **Iterations**: None

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**: 
- Query: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
- **Purpose**: Discovers all nodes in the Redis cluster for configuration
- **Migration**: Replace with Ansible inventory groups or dynamic inventory scripts for cluster node discovery

## Checks for the Migration

**Files to verify**: 
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis.service`
- `/var/log/redis/`
- `/var/lib/redis/`
- `site-modules/profile_redis_cluster/manifests/init.pp`
- `site-modules/profile_redis_cluster/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/dnfmodule.pp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/params.pp`
- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`

**Service endpoints to check**: 
- Port 6379 (Redis default instance)
- Redis cluster bus port (16379)

**Templates rendered**: 
- `redis.conf.epp` → `/etc/redis/redis.conf` (1 render for default instance)
- `redis.service.epp` → `/etc/systemd/system/redis.service` (1 render for default instance)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis
systemctl is-enabled redis

# Instance-specific checks
redis-cli -p 6379 ping
redis-cli -p 6379 cluster nodes
redis-cli -p 6379 info memory

# Configuration validation commands
redis-server --test-config /etc/redis/redis.conf
cat /etc/redis/redis.conf | grep -E "(port|requirepass|maxmemory)"

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```