---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: Comprehensive HAProxy load balancer module that installs and configures HAProxy with SSL termination, statistics interface, firewall rules, service discovery via PuppetDB, and multiple backend configurations. Supports both RedHat and Debian systems with OS-specific packages and firewall providers.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 9000 (stats)
  - Key Config: SSL termination, session persistence, health checks
- **webservers backend**: Web application servers
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: 8080
  - Key Config: Round-robin balancing, HTTP health checks
- **api backend**: API servers
  - Location/Path: `/etc/haproxy/conf.d/api.cfg`
  - Port/Socket: 3000
  - Key Config: Least-connection balancing, API health checks

## File Structure

**Manifests**:
- `site-modules/profile_haproxy/manifests/init.pp`
- `site-modules/profile_haproxy/manifests/install.pp`
- `site-modules/profile_haproxy/manifests/config.pp`
- `site-modules/profile_haproxy/manifests/service.pp`
- `site-modules/profile_haproxy/manifests/firewall.pp`
- `site-modules/profile_haproxy/manifests/discover.pp`
- `site-modules/profile/manifests/loadbalancer/haproxy.pp`
- `site-modules/role/manifests/haproxy.pp`

**Templates**:
- `site-modules/profile_haproxy/templates/haproxy.cfg.erb`
- `site-modules/profile_haproxy/templates/backend.conf.epp`

**Data Files**:
- `site-modules/profile_haproxy/data/common.yaml`
- `site-modules/profile_haproxy/data/environment/production.yaml`
- `site-modules/profile_haproxy/data/environment/staging.yaml`
- `site-modules/profile_haproxy/data/os/RedHat.yaml`
- `site-modules/profile_haproxy/data/os/Debian.yaml`
- `site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml`
- `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml`
- `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml`

**Custom Components**:
- `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`

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
   - Else ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] ~> Class['profile_haproxy::service']`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - Conditional: if `!empty($extra_packages)`
     - `package 'haproxy-systemd-wrapper'` → ensure: `present` (RedHat only)
     - `package 'policycoreutils-python-utils'` → ensure: `present` (RedHat only)
     - `package 'hatop'` → ensure: `present` (Debian only)
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, shell: `/sbin/nologin`, home: `/var/lib/haproxy`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - Conditional: if `$selinux_enabled` (true on RedHat, false on Debian)
     - `exec 'haproxy_selinux_connect'` → command: `/usr/sbin/setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
   - Iterations: `$backends.each` — runs 2 times for: **webservers**, **api**
     - **webservers**: `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`)
     - **api**: `file '/etc/haproxy/conf.d/api.cfg'` (template `backend.conf.epp`)
   - Iterations: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: HTTP error page
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: HTTP error page
   - `file '/etc/haproxy/errors'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - Conditional: if `$stick_table_enabled` (true in production)
     - `file '/etc/haproxy/conf.d/stick-tables.cfg'` → content: session persistence configuration

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → content: systemd service overrides
   - `exec 'haproxy_systemd_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → content: log rotation configuration

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Case statement: `$firewall_provider`
     - **firewalld** (RedHat): `exec 'firewalld_reload'` → command: `/bin/firewall-cmd --reload`
     - **ufw** (Debian):
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `/usr/sbin/ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `/usr/sbin/ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `/usr/sbin/ufw --force enable`
     - **none**: Firewall management disabled
     - **default**: `notify 'Unknown firewall provider: ${firewall_provider}'`

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — only if `$discovery_enabled` is true:
   - `@@haproxy::balancermember '$facts['networking']['fqdn']'` → listening_service: `webservers`, server_names: `$facts['networking']['fqdn']`, ipaddresses: `$facts['networking']['ip']`, ports: `8080`, options: `check`
   - `<<| Haproxy::Balancermember <| listening_service == 'webservers' |>` → collects exported resources
   - PuppetDB Query: discovers app servers in same environment
   - Iterations: `$app_servers.each` — runs for discovered servers
     - For each server: `haproxy::balancermember 'api-${certname}'` → adds to API backend

## Variables

**Variable Flow Summary**: 25+ variables across 8 Hiera levels with deep merge for backends hash

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::config_file`: `/etc/haproxy/haproxy.cfg` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::user`: `haproxy` (type: string)
- `profile_haproxy::group`: `haproxy` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_port`: `9000` (type: integer)
- `profile_haproxy::stats_uri`: `/haproxy-stats` (type: string)
- `profile_haproxy::stats_user`: `admin` (type: string)
- `profile_haproxy::stats_password`: `[encrypted]` (type: string)
- `profile_haproxy::global_maxconn`: `4096` (type: integer)
- `profile_haproxy::client_timeout`: `30s` (type: string)
- `profile_haproxy::server_timeout`: `30s` (type: string)
- `profile_haproxy::connect_timeout`: `5s` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::backends`: complex hash with webservers and api backends (type: hash)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::extra_packages`: `[haproxy-systemd-wrapper, policycoreutils-python-utils]` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `[hatop]` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**environment/production.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::global_maxconn`: `16384` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `warning` (type: string)
- `profile_haproxy::client_timeout`: `60s` (type: string)
- `profile_haproxy::server_timeout`: `60s` (type: string)
- `profile_haproxy::stats_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)

### Variable Migration Summary

- **Common defaults**: 25 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family (3 per OS)
- **Environment-specific variables**: 7 variables that vary by deployment environment (production), 5 variables (staging)
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::global_maxconn**: defined at common, environment, cluster levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common, environment levels, merge strategy: first
- **profile_haproxy::backends**: defined at common, environment, node levels, merge strategy: deep
- **profile_haproxy::stats_enabled**: defined at common, environment levels, merge strategy: first
- **profile_haproxy::log_level**: defined at common, environment levels, merge strategy: first

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (deep merge) for backends configuration
- Variables using `first` (default) - First value found wins, no merging for most configuration parameters

## Custom Types and Providers

**Custom Fact: haproxy_version**
- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Purpose: Executes `haproxy -v` to extract version number using regex
- Usage: Version-specific configuration decisions
- Migration: Replace with Ansible setup module or custom fact script

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.7.0)
- puppetlabs-concat (version: 9.0.2)
- puppetlabs-firewall (version: 8.1.3)

**System package dependencies**:
- haproxy (main package)
- haproxy-systemd-wrapper (RedHat only)
- policycoreutils-python-utils (RedHat only)
- hatop (Debian only)
- ufw (Debian firewall)

**Service dependencies**:
- install → config → service (with notification)
- install → config → discover → service (when discovery enabled)

## Puppet Facts Used

- `$facts['kernel']`: OS kernel type (Linux detection)
- `$facts['networking']['fqdn']`: Fully qualified domain name for service discovery
- `$facts['networking']['ip']`: IP address for load balancer member registration
- `$facts['puppet_environment']`: Environment name for PuppetDB queries
- `$facts['os']['family']`: OS family (RedHat/Debian) for package selection
- Custom fact `haproxy_version`: HAProxy version for configuration decisions

## Template Conversion Notes

**haproxy.cfg.erb**:
- Variables: 19 variables including SSL settings, timeouts, backend references
- Ruby logic: SSL conditional blocks, stats conditional block, backend iteration
- Complex expressions: SSL certificate path construction, backend loop rendering

**backend.conf.epp**:
- Variables: 10 variables for backend configuration
- Logic: Server iteration, health check configuration
- Expressions: Server weight and address formatting

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources** (`@@`): 
- Resource type: `haproxy::balancermember`
- What it exports: Current node as load balancer member with FQDN, IP, and port
- Who collects it: Other HAProxy nodes in the same environment
- Migration notes: Cross-node data sharing pattern requires centralized service registry or configuration management database

**Resource Collectors** (`<<| |>`):
- What is collected: `Haproxy::Balancermember <| listening_service == 'webservers' |>`
- Filter condition: `listening_service == 'webservers'`
- Migration notes: Node discovery requirements need replacement with inventory-based backend configuration

**PuppetDB Queries**:
- Exact query: `resources[certname, parameters] { type = 'Class' and title = 'Profile::App_server' and certname in resources[certname] { type = 'Class' and title = 'Profile::Base' and parameters.environment = '${facts['puppet_environment']}' } }`
- Returned data: App servers with Profile::App_server class in same environment
- Migration notes: Infrastructure data access patterns require inventory system or service discovery mechanism

**Host Identity Data**:
- Per-host PuppetDB data: `$facts['networking']['fqdn']` and `$facts['networking']['ip']` for node classification
- Usage: Service discovery and backend member registration
- Migration notes: Node classification needs inventory-based host identification

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` (main configuration)
- `/etc/haproxy/conf.d/webservers.cfg` (backend configuration)
- `/etc/haproxy/conf.d/api.cfg` (backend configuration)
- `/etc/haproxy/errors/503.http` (error pages)
- `/etc/haproxy/errors/408.http` (error pages)
- `/etc/systemd/system/haproxy.service.d/override.conf` (systemd overrides)
- `/etc/logrotate.d/haproxy` (log rotation)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 9000 (statistics interface, if enabled)
- Backend ports 8080, 3000 (health checks)

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/api.cfg` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# Instance-specific checks
haproxy -f /etc/haproxy/haproxy.cfg -c
curl -I http://localhost/health
curl http://localhost:9000/haproxy-stats

# Configuration validation commands
test -f /etc/haproxy/haproxy.cfg
test -f /etc/haproxy/conf.d/webservers.cfg
test -f /etc/haproxy/conf.d/api.cfg

# Network/connectivity checks
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :9000
```