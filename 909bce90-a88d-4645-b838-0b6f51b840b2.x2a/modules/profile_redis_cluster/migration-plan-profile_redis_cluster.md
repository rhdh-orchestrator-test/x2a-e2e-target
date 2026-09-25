---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: A Redis cluster profile module that installs and configures a single Redis instance with authentication, memory limits, and append-only file persistence. Uses PuppetDB queries to discover cluster nodes and includes parameter defaults from a dedicated params class.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database

**Configured Instances**:
- **default**: Primary Redis instance
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: bind=0.0.0.0, password-protected, 256MB memory limit, AOF enabled

## File Structure

**Manifests**:
- `site-modules/profile/manifests/cache/redis.pp`
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

**Templates**:
- `site-modules/profile_redis_cluster/migration-dependencies/redis/templates/redis.conf.epp`
- `site-modules/profile_redis_cluster/migration-dependencies/redis/templates/service_templates/redis.service.epp`

**Custom Components**:
- `site-modules/profile_redis_cluster/lib/facter/redis_role.rb`

## Module Explanation

The module performs operations in this order:

1. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - Contains profile_redis_cluster class
   - Uses fact('environment') for environment detection

2. **profile_redis_cluster** (`site-modules/profile_redis_cluster/manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - Executes PuppetDB query: `puppetdb_query("resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }")` to discover cluster nodes
   - Contains profile_redis_cluster::install

3. **profile_redis_cluster::install** (`site-modules/profile_redis_cluster/manifests/install.pp`):
   - Declares redis class with parameters: bind='0.0.0.0', port=6379, requirepass='test-redis-password', maxmemory='256mb', appendonly=true, appendfsync='everysec', manage_package=true

4. **redis** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/init.pp`):
   - Inherits 123 parameters from redis::params
   - Contains redis::preinstall, redis::install, redis::config, redis::service
   - Manages default instance via $default_install=true
   - Iterations: $instances.each loop runs 0 times (no additional instances configured beyond default)
   - Ordering: redis::preinstall -> redis::install -> redis::config
   - Notification: redis::config ~> redis::service (if notify_service=true)

5. **redis::params** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/params.pp`):
   - Provides parameter defaults inherited by redis class
   - Sets OS-specific package names and paths

6. **redis::preinstall** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/preinstall.pp`):
   - Conditional repository management (skipped when manage_repo=false)
   - Uses facts: $facts['os']['name'], $facts['os']['family']

7. **redis::install** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/install.pp`):
   - Installs redis-server package when manage_package=true
   - Handles DNF module streams when configured
   - Uses fact: $facts['os']['family']

8. **redis::config** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/config.pp`):
   - Creates directories: /etc/redis, /var/log/redis, /var/lib/redis with redis ownership
   - Manages default instance via redis::instance when default_install=true
   - Manages ulimit configuration when ulimit_managed=true
   - OS-specific configuration for Debian family

9. **redis::instance** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/instance.pp`):
   - Renders redis.conf.epp template to /etc/redis/redis.conf with 85+ variables
   - Conditionally renders redis.service.epp when manage_service_file=true
   - Manages systemd drop-in for limits when ulimit_managed=true
   - Creates backup and exec resources for configuration management

10. **redis::ulimit** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/ulimit.pp`):
    - Creates /etc/security/limits.d/redis.conf for user limits
    - Creates /etc/systemd/system/redis.service.d/limit.conf for systemd limits

11. **redis::service** (`site-modules/profile_redis_cluster/migration-dependencies/redis/manifests/service.pp`):
    - Manages redis service when service_manage=true
    - Ensures running state and enabled on boot

## Variables

**Variable Flow Summary**: 4 variables across 1 Hiera level plus class parameter defaults

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)

**Class parameter defaults (profile_redis_cluster::init)** → Migration note: Hardcoded defaults in manifest
- `redis_port`: `6379` (type: integer)
- `maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 2 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: 0 variables that vary by deployment environment
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (redis_password) and needs secure storage

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
- puppetlabs-stdlib (9.6.0)
- puppet-redis (11.0.0)
- puppetlabs-apt (9.4.0)

**System package dependencies**:
- redis-server (from OS package manager)

**Service dependencies**:
- Network availability (systemd After=network.target)

## Puppet Facts Used

- `$facts['os']['name']` → Operating system name (Ubuntu, CentOS, etc.)
- `$facts['os']['family']` → OS family (Debian, RedHat, etc.)
- `fact('environment')` → Puppet environment name

## Template Conversion Notes

**redis/redis.conf.epp** (85+ variables, 20+ logic blocks):
- **Complex conditionals**: TLS settings, cluster configuration, active defragmentation
- **Array processing**: bind addresses, modules, ACLs, save intervals
- **Boolean conversion**: Uses `bool2str()` function for yes/no values
- **Sensitive data handling**: Password parameters can be Sensitive[String] type

**redis/service_templates/redis.service.epp** (10 variables, 3 logic blocks):
- **Systemd service template**: ExecStart, User, Group, LimitNOFILE
- **Conditional sections**: Timeout settings, ulimit management
- **Variable interpolation**: Service name, binary path, config file path

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**:
- `puppetdb_query("resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }")` → discovers all nodes with this profile for cluster formation, migration notes: Replace with Ansible inventory groups or dynamic inventory scripts for node discovery

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis.service.d/limit.conf`
- `/etc/security/limits.d/redis.conf`
- `/var/log/redis/redis.log`
- `/var/lib/redis/dump.rdb`
- `/etc/redis/redis.conf.orig`

**Service endpoints to check**:
- Port 6379 (Redis server)

**Templates rendered**:
- `redis/redis.conf.epp` → `/etc/redis/redis.conf` (1 render)
- `redis/service_templates/redis.service.epp` → systemd service file (conditional render when manage_service_file=true)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis
redis-cli ping
redis-cli info memory
redis-cli config get requirepass

# Instance-specific checks
redis-cli -p 6379 ping
redis-cli -p 6379 -a test-redis-password ping

# Configuration validation commands
redis-server --test-config /etc/redis/redis.conf
cat /etc/redis/redis.conf | grep -E "(bind|port|requirepass|maxmemory)"

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```