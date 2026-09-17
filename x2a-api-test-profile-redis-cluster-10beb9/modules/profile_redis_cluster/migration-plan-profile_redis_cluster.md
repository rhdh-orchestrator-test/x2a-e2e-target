---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: Redis cluster module that installs and configures Redis instances with cluster support, authentication, and memory management. Uses PuppetDB queries to discover cluster nodes and configures Redis with custom memory limits and authentication passwords.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database (Redis Cluster)

**Configured Instances**:
- **default**: Primary Redis instance
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: password authentication, memory limit 256MB, allkeys-lru eviction policy

## File Structure

```
site-modules/profile/manifests/cache/redis.pp
site-modules/profile_redis_cluster/manifests/init.pp
site-modules/profile_redis_cluster/manifests/install.pp
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
site-modules/profile_redis_cluster/lib/facter/redis_role.rb
```

## Module Explanation

The module performs operations in this order:

1. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Contains profile_redis_cluster class

2. **profile_redis_cluster** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - Executes PuppetDB query to discover cluster nodes with Profile_redis_cluster class
   - Contains profile_redis_cluster::install

3. **profile_redis_cluster::install** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - Contains redis class

4. **redis** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits parameters from redis::params
   - Contains redis::preinstall, redis::install, redis::config, redis::service
   - Processes instances parameter (default: empty hash, no additional instances)
   - Sets ordering: redis::preinstall -> redis::install -> redis::config
   - Sets notification: redis::config ~> redis::service

5. **redis::preinstall** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Conditionally manages repository if manage_repo is true (default: false, skipped)
   - Uses facts: os.name, os.family

6. **redis::install** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Installs redis-server package if manage_package is true (default: true)
   - Conditionally manages DNF module stream if specified (default: undef, skipped)
   - Uses fact: os.family

7. **redis::config** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - Creates directories: /etc/redis, /var/log/redis, /var/lib/redis (owner: redis, group: redis, mode: 0755)
   - Configures default instance if default_install is true (default: true)
   - Creates redis::instance 'default' with 123 parameters
   - Manages OS-specific configuration files based on os.family

8. **redis::instance** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`):
   - Creates systemd unit file redis-server.service using redis.service.epp template
   - Creates /etc/redis/redis.conf configuration file (owner: redis, group: redis, mode: 0640)
   - Creates exec resource for configuration copying (refreshonly: true)

9. **redis::service** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
   - Manages redis-server service if service_manage is true (default: true)
   - Ensures service is running and enabled

## Variables

**Variable Flow Summary**: 4 variables across 2 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

**Class parameter defaults (init.pp)** → Migration note: Hard-coded class defaults
- `redis_port`: `6379` (type: integer)
- `maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 2 variables from common.yaml (base Redis configuration)
- **OS-specific variables**: 0 variables
- **Environment-specific variables**: 0 variables
- **Host-specific variables**: 0 variables
- **Encrypted variables**: 1 variable that needs secure storage (redis_password)

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
- redis-server

**Service dependencies**:
- redis::preinstall -> redis::install -> redis::config
- redis::config ~> redis::service

## Puppet Facts Used

- **facts['os']['name']**: Operating system name for repository configuration
- **facts['os']['family']**: Operating system family for package management and configuration paths

## Template Conversion Notes

**redis.service.epp** (systemd service template):
- **Variables used**: service_name, user, group, working_directory, exec_start, pid_file, limit_nofile, limit_memlock, private_tmp
- **Ruby logic blocks**: 3 conditional blocks for service configuration
- **Conditional rendering**: Service file path construction, resource limit handling
- **Iterations**: None
- **Complex expressions**: Service file path construction, resource limit handling

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**: 1 query
- **Query**: `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
- **Purpose**: Discovers all nodes in the Redis cluster for cluster configuration
- **Migration**: Replace with Ansible inventory groups or dynamic inventory scripts to identify Redis cluster members

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis-server.service`
- `/etc/default/redis-server`
- `/var/log/redis/` (directory)
- `/var/lib/redis/` (directory)

**Service endpoints to check**:
- Port 6379 (Redis server)

**Templates rendered**:
- `redis.service.epp` → `/etc/systemd/system/redis-server.service` (1 render for default instance)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis-server

# Instance-specific checks
redis-cli ping
redis-cli auth test-redis-password

# Configuration validation commands
redis-cli info memory
redis-cli config get maxmemory
redis-cli config get maxmemory-policy

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```