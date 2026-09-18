---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: A Redis cache server module that installs and configures a single Redis instance with authentication, memory limits, and append-only file persistence. Uses PuppetDB to discover cluster nodes but only configures a standalone Redis server with basic security settings.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database

**Configured Instances**:
- **default**: Single Redis instance
  - Location/Path: /var/lib/redis
  - Port/Socket: 6379
  - Key Config: bind=0.0.0.0, requirepass=test-redis-password, maxmemory=256mb, appendonly=true

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
```

## Module Explanation

The module performs operations in this order:

1. **profile_redis_cluster** (`manifests/init.pp`):
   - Sets class parameters: redis_port=6379, redis_password='test-redis-password', maxmemory_mb=256, maxmemory_policy='allkeys-lru'
   - Contains profile_redis_cluster::install

2. **profile_redis_cluster::install** (`manifests/install.pp`):
   - Declares redis class with parameters: bind='0.0.0.0', port=6379, requirepass='test-redis-password', maxmemory='256mb', appendonly=true, appendfsync='everysec', manage_package=true

3. **redis** (`migration-dependencies/redis/manifests/init.pp`):
   - Sets 123 class parameters with defaults
   - Contains redis::preinstall, redis::install, redis::config, redis::service
   - Iterations: $instances.each loop runs 0 times (empty hash)
   - Sets ordering: redis::preinstall -> redis::install -> redis::config
   - Conditional notification: if notify_service=true → redis::config ~> redis::service

4. **redis::preinstall** (`migration-dependencies/redis/manifests/preinstall.pp`):
   - Conditional repository management based on manage_repo parameter
   - Uses facts: $facts['os']['name'], $facts['os']['family']

5. **redis::install** (`migration-dependencies/redis/manifests/install.pp`):
   - Conditional package installation: if manage_package=true → package 'redis' ensure installed
   - Conditional DNF module management based on dnf_module_stream parameter
   - Uses fact: $facts['os']['family']

6. **redis::config** (`migration-dependencies/redis/manifests/config.pp`):
   - Creates directories: /etc/redis, /var/log/redis, /var/lib/redis with redis ownership
   - Conditional default instance creation: if default_install=true → redis::instance 'default'
   - Conditional ulimit management: if ulimit_managed=true → redis::ulimit
   - OS-specific configuration: case $facts['os']['family'] for Debian-specific files
   - Uses fact: $facts['os']['family']

7. **redis::instance** (`migration-dependencies/redis/manifests/instance.pp`):
   - Creates configuration file /etc/redis/redis.conf from template redis.conf.epp
   - Executes copy command to ensure configuration file exists
   - Conditional directory and service file management based on parameters

8. **redis::ulimit** (`migration-dependencies/redis/manifests/ulimit.pp`):
   - Conditional systemd limit configuration: if managed_by_cluster_manager=false
   - Creates /etc/systemd/system/redis.service.d/limit.conf with LimitNOFILE=65536

9. **redis::service** (`migration-dependencies/redis/manifests/service.pp`):
   - Conditional service management: if service_manage=true → service 'redis' ensure running, enable true

## Variables

**Variable Flow Summary**: 4 variables across class parameter defaults

### Variable Definitions

**Class parameter defaults (init.pp)**:
- `profile_redis_cluster::redis_port`: `6379` (type: integer)
- `profile_redis_cluster::redis_password`: `test-redis-password` (type: string)
- `profile_redis_cluster::maxmemory_mb`: `256` (type: integer)
- `profile_redis_cluster::maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from class parameter defaults
- **OS-specific variables**: 0 variables
- **Environment-specific variables**: 0 variables
- **Host-specific variables**: 0 variables
- **Encrypted variables**: 1 variable needing secure storage (redis_password)

### Cross-Level Overrides

No cross-level variable definitions detected.

### Merge Strategy Notes

All variables use default merge strategy (first value found wins).

## Custom Types and Providers

**Custom Facts**:
- **redis_role** (`lib/facter/redis_role.rb`): Determines Redis role by checking for replica configuration file and 'replicaof' directive. Returns 'master', 'slave', or 'unknown' based on configuration analysis.

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.6.0)
- puppet-redis (version: 11.0.0)
- puppetlabs-apt (version: 9.4.0)

**System package dependencies**:
- redis (managed by redis::install)

**Service dependencies**:
- redis::preinstall -> redis::install -> redis::config
- redis::config ~> redis::service (notification relationship)

## Puppet Facts Used

- **$facts['os']['name']**: Operating system name (used in redis::preinstall for repository management)
- **$facts['os']['family']**: Operating system family (used in redis::install and redis::config for OS-specific configuration)

## Template Conversion Notes

**redis.conf.epp**:
- Variables used: All Redis configuration parameters including bind, port, requirepass, maxmemory, appendonly, appendfsync
- Logic blocks: Conditional rendering based on parameter values
- Render count: 1 (renders to /etc/redis/redis.conf)

**redis.service.epp**:
- Variables used: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- Logic blocks: 3 conditional blocks for ulimit management and timeout settings
- Render count: 0 (template not used since manage_service_file=false)

## Checks for the Migration

**Files to verify**:
- /etc/redis/redis.conf
- /etc/systemd/system/redis.service.d/limit.conf
- /etc/default/redis-server (Debian only)
- /var/lib/redis/ (directory)
- /var/log/redis/ (directory)

**Service endpoints to check**:
- Redis server on port 6379
- Redis authentication with password 'test-redis-password'

**Templates rendered**:
- redis.conf.epp → /etc/redis/redis.conf (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status redis

# Instance-specific checks
redis-cli -p 6379 -a test-redis-password ping

# Configuration validation commands
redis-cli -p 6379 -a test-redis-password info memory
redis-cli -p 6379 -a test-redis-password config get maxmemory

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```