---
source-path: site-modules/profile_redis_cluster
---

# Migration Plan: profile_redis_cluster

**TLDR**: Redis cluster module that installs and configures Redis server instances with authentication, memory limits, and systemd service management. Uses PuppetDB queries to discover cluster nodes and includes a custom fact for role detection. Configures a default Redis instance on port 6379 with password authentication and memory management policies.

## Service Type and Instances

**Service Type**: Cache / In-Memory Database

**Configured Instances**:
- **default**: Primary Redis instance
  - Location/Path: /etc/redis/redis.conf
  - Port/Socket: 6379
  - Key Config: password auth, 256MB memory limit, allkeys-lru eviction

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
   - PuppetDB Query: Discovers Redis cluster nodes with query `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }`
   - `contain profile_redis_cluster::install`

2. **profile_redis_cluster::install** (`manifests/install.pp`):
   - `contain redis`

3. **redis** (`migration-dependencies/redis/manifests/init.pp`):
   - Inherits from `redis::params`
   - Sets Redis parameters from defaults and overrides
   - `contain redis::preinstall`
   - `contain redis::install`
   - `contain redis::config`
   - `contain redis::service`
   - Iterations: `$instances.each` — Creates redis::instance resources for configured instances (default: 1 instance)
   - Sets ordering: `redis::preinstall -> redis::install -> redis::config ~> redis::service`

4. **redis::preinstall** (`migration-dependencies/redis/manifests/preinstall.pp`):
   - Conditional: if `$redis::manage_repo` (false by default) — skipped
   - Uses facts: `$facts['os']['name']`, `$facts['os']['family']`

5. **redis::install** (`migration-dependencies/redis/manifests/install.pp`):
   - Conditional: if `$redis::manage_package` (true by default):
     - `package 'redis-server'` → ensure: `present`
   - Conditional: if `$redis::dnf_module_stream` (undef by default) — skipped
   - Uses fact: `$facts['os']['family']`

6. **redis::config** (`migration-dependencies/redis/manifests/config.pp`):
   - `file '/etc/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/log/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - `file '/var/lib/redis'` → ensure: `directory`, owner: `redis`, group: `redis`, mode: `0755`
   - Conditional: if `$redis::default_install` (true by default):
     - Creates redis::instance 'default'
   - Conditional: if `$redis::ulimit_managed` (false by default) — skipped
   - Conditional: case `$facts['os']['family']`:
     - **Debian**: `file '/etc/default/redis-server'` → ensure: `present`
     - **default**: no action

7. **redis::instance** (`migration-dependencies/redis/manifests/instance.pp`):
   - `file '/var/log/redis'` → owner: `redis`, group: `redis`, mode: `0755` (conditional, skipped if same as redis::log_dir)
   - `file '/var/lib/redis'` → owner: `redis`, group: `redis`, mode: `0755` (conditional, skipped if same as redis::workdir)
   - Conditional: if `$manage_service_file` (true by default):
     - `systemd::unit_file 'redis.service'` (template `redis.service.epp`) → mode: `0644`
   - `file '/etc/redis/redis.conf'` → owner: `redis`, group: `redis`, mode: `0640`
   - `exec 'copy /etc/redis/redis.conf to /etc/redis/redis.conf'` → creates: `/etc/redis/redis.conf`

8. **redis::service** (`migration-dependencies/redis/manifests/service.pp`):
   - Conditional: if `$redis::service_manage` (true by default):
     - `service 'redis'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`

## Variables

**Variable Flow Summary**: 4 variables across class parameter defaults

### Variable Definitions

**Class parameter defaults (init.pp)** → Migration note: Base defaults defined in class parameters
- `redis_port`: `6379` (type: integer)
- `redis_password`: `test-redis-password` (type: string)
- `maxmemory_mb`: `256` (type: integer)
- `maxmemory_policy`: `allkeys-lru` (type: string)

### Variable Migration Summary

- **Common defaults**: 4 variables from class parameter defaults (base configuration for all nodes)
- **OS-specific variables**: 0 variables
- **Environment-specific variables**: 0 variables
- **Host-specific variables**: 0 variables
- **Encrypted variables**: 1 variable that needs secure storage (redis_password)

### Cross-Level Overrides

No cross-level variable overrides detected in this module.

### Merge Strategy Notes

All variables use default `first` merge strategy - first value found wins, no merging.

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
- redis-server

**Service dependencies**:
- Network target (systemd)
- Network-online target (systemd)

## Puppet Facts Used

- `$facts['os']['name']`: Operating system name for package management
- `$facts['os']['family']`: OS family (Debian/RedHat) for conditional configuration
- `fact('environment')`: Environment name for Hiera lookups

## Template Conversion Notes

**redis.service.epp**: Systemd service template
- **Variables**: ulimit_managed, ulimit, bin_path, redis_file_name, port, instance_title, service_name, service_user, service_timeout_start, service_timeout_stop
- **Ruby logic blocks**: 3 conditional blocks for ulimit and timeout settings
- **Conditional rendering**: Service timeout configuration based on parameter presence
- **Iterations**: None
- **Complex expressions**: Conditional ulimit configuration based on ulimit_managed parameter

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**PuppetDB Queries**:
- `resources[certname] { type = 'Class' and title = 'Profile_redis_cluster' }` - discovers Redis cluster member nodes for cluster formation, migration notes: Replace with Ansible inventory groups or dynamic inventory to identify Redis cluster members

## Checks for the Migration

**Files to verify**:
- `/etc/redis/redis.conf`
- `/etc/systemd/system/redis.service`
- `/var/log/redis/` (directory)
- `/var/lib/redis/` (directory)
- `/etc/default/redis-server` (Debian only)
- `lib/facter/redis_role.rb`

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
redis-cli -p 6379 config get maxmemory-policy

# Configuration validation commands
test -f /etc/redis/redis.conf
test -d /var/log/redis
test -d /var/lib/redis
redis-server --test-config /etc/redis/redis.conf

# Network/connectivity checks
netstat -tlnp | grep :6379
ss -tlnp | grep :6379
```