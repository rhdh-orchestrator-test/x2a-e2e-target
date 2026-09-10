---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: A Redis cluster profile that installs and configures a single Redis instance with authentication, memory limits, and systemd service management. Part of an application server role, uses PuppetDB queries to discover cluster nodes and includes a custom fact for role detection.

## Service Type and Instances

**Service Type**: Application / Cache (part of application server role)

**Configured Instances**:
- **default**: Primary Redis instance
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
   - Entry point class for application server role
   - Contains `profile::cache::redis`

2. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Profile wrapper for Redis cache functionality
   - Contains `profile_redis_cluster`

3. **profile_redis_cluster** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - PuppetDB Query: Discovers Redis cluster nodes with `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
   - `contain profile_redis_cluster::install`

4. **profile_redis_cluster::install** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - `contain redis`

5. **redis** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits `redis::params` for OS-specific defaults
   - `contain redis::preinstall`
   - `contain redis::install`
   - `contain redis::config`
   - `contain redis::service`
   - Sets ordering: `Class['redis::preinstall'] -> Class['redis::install'] -> Class['redis::config'] ~> Class['redis::service']`

6. **redis::preinstall** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Conditional: if `$redis::manage_repo` (default: false) - no repository management
   - Uses facts: `$facts['os']['name']` and `$facts['os']['family']`

7. **redis::install** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Conditional: if `$redis::manage_package` (default: true)
     - `package 'redis-server'` → ensure: `present` (on Debian/Ubuntu)
     - `package 'redis'` → ensure: `present` (on RedHat/CentOS)
   - Conditional: if `$redis::dnf_module_stream` (default: undef) - no DNF module management

8. **redis::config** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - `file '/etc/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/log/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/lib/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - Conditional: if `$redis::default_install` (default: true)
     - **redis::instance 'default'**:
       - `file '/etc/redis/redis.conf.puppet'` (template) → owner: `redis`, group: `redis`, mode: `0640`
       - `exec 'copy /etc/redis/redis.conf.puppet to /etc/redis/redis.conf'` → creates config file
       - Conditional: if `$manage_service_file` (default: true)
         - `systemd::unit_file 'redis-server.service'` (template `redis.service.epp`) → mode: `0644`
   - Conditional: if `$redis::ulimit_managed` (default: false) - no ulimit management
   - Conditional: case `$facts['os']['family']`
     - **Debian**: `file '/etc/default/redis-server'` → content from template

9. **redis::service** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
   - Conditional: if `$redis::service_manage` (default: true)
     - `service 'redis-server'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - Conditional: if `$redis::notify_service` affects service notification behavior

10. **Loop**: `$instances.each` — Loop runs 0 times (no additional instances configured)
    - Instance expansion: Only the default instance is created through `$redis::default_install`
    - Each additional instance would create redis::instance resources with unique names

## Variables

**Variable Flow Summary**: 125+ variables across 2 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)
- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `redis::package_name`: `redis` (type: string)
- `redis::service_name`: `redis` (type: string)
- `redis::config_file`: `/etc/redis.conf` (type: string)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `redis::package_name`: `redis-server` (type: string)
- `redis::service_name`: `redis-server` (type: string)
- `redis::config_file`: `/etc/redis/redis.conf` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from common.yaml (base Redis configuration for all nodes)
- **OS-specific variables**: 6+ variables that vary by operating system family (package names, service names, paths)
- **Environment-specific variables**: 0 variables that vary by deployment environment
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (redis_password) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple levels:
- **redis::package_name**: defined at OS level, merge strategy: first
- **redis::service_name**: defined at OS level, merge strategy: first
- **redis::config_file**: defined at OS level, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- Redis instance parameters use hash merge for complex configuration structures

## Custom Types and Providers

**Custom Fact: redis_role**
- **File**: `lib/facter/redis_role.rb`
- **Purpose**: Determines Redis role (primary/replica) by checking for 'replicaof' directive in `/etc/redis/conf.d/replica.conf`
- **Platform**: Linux-only
- **Migration**: Replace with Ansible custom fact script or setup module extension

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.6.0)
- puppet-redis (version: 11.0.0) - bundled in migration-dependencies
- puppetlabs-apt (version: 9.4.0)

**System package dependencies**:
- redis-server (Debian/Ubuntu)
- redis (RedHat/CentOS)

**Service dependencies**:
- Network target (systemd After=network.target)

## Puppet Facts Used

- `$facts['os']['name']`: Operating system name (Ubuntu, CentOS, etc.)
- `$facts['os']['family']`: OS family (Debian, RedHat, etc.)
- `$facts['os']['release']['major']`: Major OS version for RedHat path decisions
- `fact('environment')`: Puppet environment name

## Template Conversion Notes

**redis.service.epp**: Systemd service template with 10 variables and 3 conditional logic blocks
- Variables: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- Logic: Conditional ulimit setting, optional timeout configurations, runtime directory naming
- Complex expressions: Runtime directory naming based on service_name, conditional LimitNOFILE directive

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Query**: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
- **Purpose**: Discovers all nodes in the Redis cluster for cluster formation
- **Usage**: Stored in `$redis_nodes` variable but not used in current implementation
- **Migration**: Replace with Ansible inventory groups or dynamic inventory scripts for cluster node discovery

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis-server.service`
- `/var/log/redis/`
- `/var/lib/redis/`
- `/etc/default/redis-server` (Debian only)

**Service endpoints to check**:
- Port 6379 (Redis server)

**Templates rendered**:
- `redis.service.epp` → `/etc/systemd/system/redis-server.service` (1 render for default instance)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis-server
systemctl is-enabled redis-server

# Instance-specific checks
redis-cli -p 6379 ping
redis-cli -p 6379 auth test-redis-password
redis-cli -p 6379 info memory

# Configuration validation commands
redis-server --test-memory 256
cat /etc/redis/redis.conf | grep -E "(port|maxmemory|requirepass)"

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```