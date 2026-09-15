---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: Redis cluster module that installs and configures Redis server with cluster support, authentication, and memory management. Uses PuppetDB queries to discover cluster nodes and includes a custom fact for role detection. Configures a single default Redis instance with cluster capabilities through a role-profile pattern with kernel validation.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database (Redis Cluster)

**Configured Instances**:
- **default**: Primary Redis instance with cluster support
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: cluster_enabled=false, maxmemory=256MB, password authentication

## File Structure

```
site-modules/role/manifests/redis_cluster.pp
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

1. **role::redis_cluster** (`site-modules/role/manifests/redis_cluster.pp`):
   - **Kernel validation**: Checks `$facts['kernel'] == 'Linux'` before proceeding
   - Sets class ordering: `Class['::profile::base::base'] -> Class['::profile::cache::redis']`
   - `contain profile::cache::redis`

2. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Uses `fact('environment')` for environment-specific configuration
   - `contain profile_redis_cluster`

3. **profile_redis_cluster** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - **PuppetDB Query**: Discovers cluster nodes with `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
   - `contain profile_redis_cluster::install`

4. **profile_redis_cluster::install** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - `contain redis`

5. **redis** (`migration-dependencies/redis/manifests/init.pp`):
   - Sets 123 parameters with defaults: port=6379, bind=['127.0.0.1'], maxmemory=undef, maxmemory_policy=undef, requirepass=undef, cluster_enabled=false, default_install=true, instances={}
   - `inherits redis::params`
   - `contain redis::preinstall`
   - `contain redis::install`
   - `contain redis::config`
   - `contain redis::service`
   - **Iterations**: `$instances.each |$key, $values|` — Loop runs 0 times (instances={})
     - *Instance expansion*: Since instances is empty, only the default instance is created via `$default_install=true`
   - Sets ordering: `redis::preinstall -> redis::install -> redis::config`
   - **Conditional notification**: if `$notify_service=true` → `redis::config ~> redis::service`

6. **redis::preinstall** (`migration-dependencies/redis/manifests/preinstall.pp`):
   - **Conditional**: if `$manage_repo=false` — skips repository management
   - Uses facts: `$facts['os']['name']`, `$facts['os']['family']`

7. **redis::install** (`migration-dependencies/redis/manifests/install.pp`):
   - **Conditional**: if `$manage_package=true`:
     - `package 'redis-server'` → ensure: `installed` (package_name from params)
   - **Conditional**: if `$dnf_module_stream=undef` — skips DNF module configuration
   - Uses fact: `$facts['os']['family']`

8. **redis::config** (`migration-dependencies/redis/manifests/config.pp`):
   - `file '/etc/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/log/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/lib/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0750`
   - **Conditional**: if `$default_install=true`:
     - **redis::instance 'default'**:
       - `file '/var/log/redis'` → owner: `redis`, group: `redis`, mode: `0755` (log_dir check)
       - `file '/var/lib/redis'` → owner: `redis`, group: `redis`, mode: `0750` (workdir check)
       - **Conditional**: if `$manage_service_file=false` — skips systemd unit file creation
       - `file '/etc/redis/redis.conf.orig'` (template `redis/redis.conf.epp`) → mode: `0640`, owner: `redis`, group: `redis`
       - `exec 'copy /etc/redis/redis.conf.orig to /etc/redis/redis.conf'` → creates: `/etc/redis/redis.conf`
   - **Conditional**: if `$ulimit_managed=true`:
     - **redis::ulimit**:
       - **Conditional**: if `$managed_by_cluster_manager=false`:
         - `file '/etc/systemd/system/redis.service.d/limit.conf'` → content with LimitNOFILE=65536
   - **Conditional**: case `$facts['os']['family']`:
     - **Debian**: `file '/etc/default/redis-server'` → template with environment variables
   - Uses fact: `$facts['os']['family']`

9. **redis::service** (`migration-dependencies/redis/manifests/service.pp`):
   - **Conditional**: if `$service_manage=true`:
     - `service 'redis'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`

## Variables

**Variable Flow Summary**: 4 variables across 1 Hiera level

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

**Manifest defaults (profile_redis_cluster::init)** → Migration note: Hard-coded defaults in class definition
- `redis_port`: `6379` (type: integer)
- `maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 2 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: 0 variables that vary by deployment environment (dev, staging, prod)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage (redis_password)

### Cross-Level Overrides

No cross-level overrides detected.

### Merge Strategy Notes

Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Custom Fact: redis_role**
- **File**: `lib/facter/redis_role.rb`
- **Purpose**: Determines Redis role (primary/replica) by checking for 'replicaof' directive in `/etc/redis/conf.d/replica.conf`
- **Platform**: Linux-only
- **Migration**: Replace with Ansible custom fact script or setup module extension

## Dependencies

**External module dependencies**:
- `puppetlabs-stdlib` (version: 9.6.0)
- `puppet-redis` (version: 11.0.0) 
- `puppetlabs-apt` (version: 9.4.0)

**System package dependencies**:
- `redis-server` (from redis module)

**Service dependencies**:
- `redis::preinstall -> redis::install -> redis::config`
- `redis::config ~> redis::service` (notification)
- `Class['::profile::base::base'] -> Class['::profile::cache::redis']`

## Puppet Facts Used

- `$facts['kernel']`: Operating system kernel type (Linux validation check)
- `$facts['os']['name']`: Operating system name (repository configuration)
- `$facts['os']['family']`: Operating system family (Debian/RedHat package handling)
- `fact('environment')`: Puppet environment name (environment-specific configuration)

## Template Conversion Notes

**redis.service.epp**: Systemd service unit template
- **Variables**: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- **Logic blocks**: 3 conditional blocks for ulimit and timeout settings
- **Render count**: 0 (manage_service_file=false by default)

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**: 
- **Query**: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
- **Purpose**: Discovers all nodes in the cluster that have the profile_redis_cluster class applied
- **Migration notes**: Replace with Ansible inventory groups or dynamic inventory scripts for cluster node discovery

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf` (main configuration)
- `/etc/redis/redis.conf.orig` (template source)
- `/var/log/redis/redis.log` (log file)
- `/var/lib/redis/dump.rdb` (data persistence)
- `/etc/systemd/system/redis.service.d/limit.conf` (ulimit configuration)
- `/etc/default/redis-server` (Debian environment file)

**Service endpoints to check**:
- `127.0.0.1:6379` (Redis server port)

**Templates rendered**:
- `redis.conf.epp` → `/etc/redis/redis.conf.orig` (1 render)
- `redis.service.epp` → systemd unit (0 renders - manage_service_file=false)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis
redis-cli ping

# Instance-specific checks
redis-cli -p 6379 ping
redis-cli -p 6379 auth test-redis-password

# Configuration validation commands
redis-cli config get maxmemory
redis-cli config get maxmemory-policy
redis-cli info memory

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```