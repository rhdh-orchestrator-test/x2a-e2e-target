---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that installs and configures HAProxy with SSL termination, statistics interface, firewall management, and dynamic backend discovery via PuppetDB. Supports multiple backends, health checks, and environment-specific configuration across a 21-level Hiera hierarchy.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 8404 (stats)
  - Key Config: SSL termination, backend health checks, session persistence
- **webservers**: Default backend pool
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: 8080
  - Key Config: Round-robin load balancing, health checks
- **api**: Dynamic backend pool (when discovery enabled)
  - Location/Path: Generated via PuppetDB discovery
  - Port/Socket: Variable per server
  - Key Config: Dynamic server registration

## File Structure

```
site-modules/profile_haproxy/manifests/init.pp
site-modules/profile_haproxy/manifests/install.pp
site-modules/profile_haproxy/manifests/config.pp
site-modules/profile_haproxy/manifests/service.pp
site-modules/profile_haproxy/manifests/firewall.pp
site-modules/profile_haproxy/manifests/discover.pp
site-modules/profile/manifests/loadbalancer/haproxy.pp
site-modules/role/manifests/haproxy.pp
site-modules/profile_haproxy/templates/haproxy.cfg.erb
site-modules/profile_haproxy/templates/backend.conf.epp
site-modules/profile_haproxy/data/common.yaml
site-modules/profile_haproxy/data/os/Debian.yaml
site-modules/profile_haproxy/data/os/RedHat.yaml
site-modules/profile_haproxy/data/environment/production.yaml
site-modules/profile_haproxy/data/environment/staging.yaml
site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml
site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml
site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml
site-modules/profile_haproxy/lib/facter/haproxy_version.rb
data/common.yaml
```

## Module Explanation

The module performs operations in this order:

1. **role::haproxy** (`site-modules/role/manifests/haproxy.pp`):
   - Conditional: if `$facts['kernel'].downcase == 'linux'`
     - `exec 'default'` → command: `/bin/true`
   - `contain ::profile::base::base`
   - `contain ::profile::loadbalancer::haproxy`
   - Ordering: `Class['::profile::base::base'] -> Class['::profile::loadbalancer::haproxy']`

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - `contain profile_haproxy`

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from Hiera lookups with deep merge for backends
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - Conditional: if `$discovery_enabled` (false by default)
     - `contain profile_haproxy::discover`
     - Ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] -> Class['profile_haproxy::discover'] ~> Class['profile_haproxy::service']`
   - Else:
     - Ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] ~> Class['profile_haproxy::service']`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - Conditional: if `!empty($extra_packages)`
     - RedHat: `package 'haproxy-selinux'` → ensure: `present`
     - Debian: `package 'haproxy-doc'` → ensure: `present`, `package 'hatop'` → ensure: `present`
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, shell: `/sbin/nologin`, home: `/var/lib/haproxy`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - Conditional: if `$selinux_enabled` (RedHat: true, Debian: false)
     - `exec 'haproxy_selinux_connect'` → command: `/usr/sbin/setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/errors'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_server, log_facility, log_level, global_maxconn, user, group, ssl_enabled, ssl_ciphers, ssl_min_version, connect_timeout, client_timeout, server_timeout, retries, stats_enabled, stats_port, stats_uri, stats_user, stats_password, ssl_cert_path, backends
   - Iterations: `$backends.each` — runs 1 time for: **webservers**
     - **webservers**: `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
       - Passes: backend_name, balance, port, servers, health_check, health_interval, ssl_enabled, options, cookie, timeout_check, timeout_server
   - Iterations: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: `HTTP/1.0 503 Service Unavailable...`
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: `HTTP/1.0 408 Request Time-out...`
   - Conditional: if `$stick_table_enabled` (production: true, staging: false)
     - `file '/etc/haproxy/conf.d/stick-tables.cfg'` → content: session persistence configuration

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → content: systemd service overrides
   - `exec 'haproxy_systemd_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - `exec 'haproxy_config_check'` → command: `/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `file '/etc/logrotate.d/haproxy'` → content: log rotation configuration
   - Notifies: `file[override.conf] ~> exec[haproxy_systemd_reload] ~> service[haproxy]`

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Conditional: case `$firewall_provider`
     - **firewalld** (RedHat): `exec 'firewalld_reload'` → command: `/bin/firewall-cmd --reload`
     - **ufw** (Debian): 
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `/usr/sbin/ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `/usr/sbin/ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `/usr/sbin/ufw --force enable`
     - **none**: No firewall management
     - **default**: `notify 'Unknown firewall provider: ${firewall_provider}'`

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — only when `$discovery_enabled` is true:
   - `@@haproxy::balancermember[$facts['networking']['fqdn']]` → listening_service: `webservers`, server_names: `$facts['networking']['fqdn']`, ipaddresses: `$facts['networking']['ip']`, ports: `8080`, options: `check`
   - `Haproxy::Balancermember <<| listening_service == 'webservers' |>>`
   - Iterations: `$app_servers.each` — Loop runs 0 times (PuppetDB query returns empty result set)

## Variables

**Variable Flow Summary**: 29 variables across 9 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::config_file`: `/etc/haproxy/haproxy.cfg` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::user`: `haproxy` (type: string)
- `profile_haproxy::group`: `haproxy` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_port`: `8404` (type: integer)
- `profile_haproxy::stats_uri`: `/stats` (type: string)
- `profile_haproxy::stats_user`: `admin` (type: string)
- `profile_haproxy::stats_password`: `ENC[PKCS7,encrypted_value]` (type: string)
- `profile_haproxy::global_maxconn`: `4096` (type: integer)
- `profile_haproxy::client_timeout`: `50000ms` (type: string)
- `profile_haproxy::server_timeout`: `50000ms` (type: string)
- `profile_haproxy::connect_timeout`: `5000ms` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::backends`: `{}` (type: hash)
- `profile_haproxy::discovery_enabled`: `false` (type: boolean)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::firewall_zone`: `public` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-selinux']` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-doc', 'hatop']` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**environment/production.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::global_maxconn`: `8192` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `notice` (type: string)
- `profile_haproxy::client_timeout`: `60000ms` (type: string)
- `profile_haproxy::server_timeout`: `60000ms` (type: string)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `100k` (type: string)
- `profile_haproxy::stick_table_expire`: `30m` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::global_maxconn`: `2048` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Datacenter-specific variables for geographic deployment differences
- `profile_haproxy::log_server`: `10.1.0.100` (type: string)
- `profile_haproxy::backends`: `{webservers: {balance: roundrobin, port: 8080, servers: [{name: web01, address: 10.0.1.10, weight: 100}]}}` (type: hash)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: Cluster-specific variables for high-availability configurations
- `profile_haproxy::global_maxconn`: `16384` (type: integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+AES256:ECDHE+AES128:!aNULL:!MD5:!DSS` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::backends`: `{webservers: {servers: [{name: web01, address: 10.0.1.10, weight: 100}, {name: web02, address: 10.0.1.11, weight: 100}]}}` (type: hash)

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Host-specific variables for individual node overrides
- `profile_haproxy::stats_port`: `8405` (type: integer)
- `profile_haproxy::backends`: `{webservers: {servers: [{name: web01, address: 10.0.1.10, weight: 150}, {name: web02, address: 10.0.1.11, weight: 50}]}}` (type: hash)

**data/common.yaml (control-repo overrides)** → Migration note: Control repository level overrides for global settings
- `profile_haproxy::stats_password`: `admin123` (type: string)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)

### Variable Migration Summary

- **Common defaults**: 24 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 7 variables that vary by operating system family
- **Environment-specific variables**: 12 variables that vary by deployment environment (production, staging)
- **Datacenter-specific variables**: 2 variables for geographic deployment differences
- **Cluster-specific variables**: 4 variables for high-availability configurations
- **Host-specific variables**: 2 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::global_maxconn**: defined at common, environment, cluster levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common, environment, control-repo levels, merge strategy: first
- **profile_haproxy::stats_password**: defined at module, control-repo levels, merge strategy: first
- **profile_haproxy::backends**: defined at datacenter, cluster, node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (deep merge) for backends configuration
- Variables using `first` (default) - First value found wins, no merging for scalar values

## Custom Types and Providers

**Custom Fact: haproxy_version**
- **File**: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- **Purpose**: Executes `haproxy -v` to extract version number using regex
- **Parameters**: None (system command execution)
- **Returns**: HAProxy version string for configuration compatibility checks

## Dependencies

**External module dependencies**: 
- `puppetlabs-stdlib` (version: 9.7.0) — standard library functions
- `puppetlabs-concat` (version: 9.0.2) — file concatenation
- `puppetlabs-firewall` (version: 8.1.3) — firewall management

**System package dependencies**:
- `haproxy` — main load balancer package
- `haproxy-selinux` (RedHat only) — SELinux policy module
- `haproxy-doc`, `hatop` (Debian only) — documentation and monitoring tools
- `ufw` (Debian only) — uncomplicated firewall

**Service dependencies**:
- Install → Config → Service (with notification on config changes)
- Discovery (when enabled) → Service (with notification)

## Puppet Facts Used

- `$facts['kernel']` — Operating system kernel (Linux detection for role conditional)
- `$facts['networking']['fqdn']` — Fully qualified domain name (exported resources for service discovery)
- `$facts['networking']['ip']` — Primary IP address (exported resources for backend registration)
- `$facts['puppet_environment']` — Puppet environment name (PuppetDB queries for app server discovery)
- `$facts['os']['family']` — OS family for Hiera hierarchy (RedHat/Debian conditional logic)

## Template Conversion Notes

**haproxy.cfg.erb**:
- **Variables used**: 21 variables including SSL configuration, timeouts, logging, stats, backends
- **Ruby logic blocks**: SSL conditional rendering for HTTPS bindings and cipher configuration, backend iteration for configuration includes
- **Conditional rendering**: SSL certificate paths, HTTPS frontend bindings, cipher suite configuration
- **Iterations**: Backend loop for including configuration files from conf.d directory

**backend.conf.epp**:
- **Variables used**: 10 variables for backend configuration (name, balance, port, servers, health checks, SSL options, timeouts)
- **Ruby logic blocks**: Conditional health check configuration, SSL backend options, server weight assignments
- **Conditional rendering**: Health check intervals, SSL verification settings, cookie persistence
- **Iterations**: Server loop for backend member configuration with individual weights and addresses

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. This module uses PuppetDB for dynamic service discovery and load balancer member registration.

**Exported Resources** (`@@`):
- **Resource type**: `haproxy::balancermember[$facts['networking']['fqdn']]`
- **What it exports**: This node as a load balancer backend member with FQDN, IP address, and port configuration
- **Who collects it**: Other HAProxy nodes in the same environment for service discovery
- **Migration notes**: Cross-node data sharing pattern requires centralized inventory system for dynamic backend registration

**Resource Collectors** (`<<| |>>`):
- **What is collected**: `Haproxy::Balancermember <<| listening_service == 'webservers' |>>`
- **Filter condition**: Resources where listening_service equals 'webservers'
- **Migration notes**: Node discovery requirements need inventory system queries for backend pool membership

**PuppetDB Queries**:
- **Exact query**: Search for nodes with `Profile::App_server` and `Profile::Base` classes in current environment
- **Returned data**: Application server nodes for dynamic backend discovery
- **Migration notes**: Infrastructure data access patterns require inventory system integration for service discovery

**Host Identity Data**:
- **Per-host PuppetDB data**: FQDN, IP address, environment classification used for backend member registration
- **Node classification usage**: Environment-based service discovery and backend pool assignment

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` — main configuration file
- `/etc/haproxy/conf.d/webservers.cfg` — backend configuration
- `/etc/haproxy/errors/503.http` — service unavailable error page
- `/etc/haproxy/errors/408.http` — request timeout error page
- `/etc/systemd/system/haproxy.service.d/override.conf` — systemd service overrides
- `/etc/logrotate.d/haproxy` — log rotation configuration
- `/etc/haproxy/conf.d/stick-tables.cfg` — session persistence configuration (production only)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 8404/8405 (statistics interface)
- Backend servers on port 8080

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# HAProxy instance-specific checks
haproxy -f /etc/haproxy/haproxy.cfg -c
curl -I http://localhost/stats
curl -I http://localhost:8404/stats

# Webservers backend checks
curl -I http://localhost/
nc -zv 10.0.1.10 8080
nc -zv 10.0.1.11 8080

# Configuration validation commands
haproxy -f /etc/haproxy/haproxy.cfg -c -V
test -f /etc/haproxy/conf.d/webservers.cfg
test -d /etc/haproxy/errors

# Network/connectivity checks
ss -tlnp | grep :80
ss -tlnp | grep :443
ss -tlnp | grep :8404
firewall-cmd --list-all || ufw status
```