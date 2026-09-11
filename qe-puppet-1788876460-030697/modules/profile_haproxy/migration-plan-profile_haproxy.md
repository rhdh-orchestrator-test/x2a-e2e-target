---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that installs HAProxy, configures multiple backends with health checks, manages SSL termination, provides statistics interface, handles firewall rules, and supports automatic service discovery via PuppetDB. Configured with 21-level Hiera hierarchy for environment-specific customization.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 8404 (stats)
  - Key Config: SSL termination, backend health checks, statistics interface

**Backend Services**:
- **webservers**: Primary web application backend (port 8080)
- **api**: API service backend (port 3000) 
- **internal_monitoring**: Internal monitoring backend (port 9090)

## File Structure

```
site-modules/profile_haproxy/
├── manifests/
│   ├── init.pp
│   ├── install.pp
│   ├── config.pp
│   ├── service.pp
│   ├── firewall.pp
│   └── discover.pp
├── templates/
│   ├── haproxy.cfg.erb
│   └── backend.conf.epp
├── data/
│   ├── common.yaml
│   ├── os/
│   │   ├── RedHat.yaml
│   │   └── Debian.yaml
│   ├── environment/
│   │   └── production.yaml
│   ├── datacenter/
│   │   └── dc1_fra.yaml
│   ├── cluster/
│   │   └── haproxy_prod_fra.yaml
│   └── nodes/
│       └── lb01.fra.example.com.yaml
└── lib/
    └── facter/
        └── haproxy_version.rb

site-modules/profile/
└── manifests/
    └── loadbalancer/
        └── haproxy.pp

site-modules/role/
└── manifests/
    └── app_server.pp

site-modules/profile/
└── manifests/
    └── base/
        └── base.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes base profile and load balancer
   - `include profile::base::base`
   - `include profile::loadbalancer::haproxy`

2. **profile::base::base** (`site-modules/profile/manifests/base/base.pp`):
   - Base system configuration
   - Uses facts: `$facts['kernel']`, `$facts['os']['family']`, `$facts['architecture']`

3. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Wrapper class that includes the main haproxy profile
   - `include profile_haproxy`

4. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from 21-level Hiera hierarchy
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - **Conditional**: if discovery_enabled=false (default)
     - `contain profile_haproxy::discover`
     - Sets ordering: `profile_haproxy::install -> profile_haproxy::config -> profile_haproxy::discover ~> profile_haproxy::service`
   - **Default ordering**: `profile_haproxy::install -> profile_haproxy::config ~> profile_haproxy::service`

5. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - **Conditional**: if extra_packages=['haproxy-stats', 'socat'] (RedHat) or ['haproxy', 'socat'] (Debian)
     - `package 'haproxy-stats'` → ensure: `present` (RedHat only)
     - `package 'socat'` → ensure: `present`
   - `group 'haproxy'` → gid: `188`
   - `user 'haproxy'` → uid: `188`, home: `/var/lib/haproxy`, shell: `/sbin/nologin`
   - `file '/etc/haproxy'` → owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → owner: `haproxy`, group: `haproxy`, mode: `0755`
   - **Conditional**: if selinux_enabled=true
     - `exec 'haproxy_selinux_connect'` → command: `setsebool -P haproxy_connect_any 1`

6. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → mode: `0644`
     - Passes: log_server='10.1.1.100', log_facility='local0', log_level='info', global_maxconn=4000, user='haproxy', group='haproxy', ssl_enabled=false, ssl_ciphers='ECDHE+AESGCM:ECDHE+AES256:ECDHE+AES128:!aNULL:!MD5:!DSS', connect_timeout='5s', client_timeout='50s', server_timeout='50s', retries=3, stats_enabled=true, stats_port=8404, stats_uri='/stats', stats_user='admin', stats_password='admin123', backends=hash
   - **Iterations**: `$backends.each` — runs 3 times for: **webservers**, **api**, **internal_monitoring**
     - **webservers**:
       - `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`) → mode: `0644`
         - Passes: backend_name='webservers', balance='roundrobin', port=8080, servers=[{name: 'web01', address: '10.1.1.10', weight: 100}, {name: 'web02', address: '10.1.1.11', weight: 100}], health_check='httpchk', health_interval='5s', ssl_enabled=false
     - **api**:
       - `file '/etc/haproxy/conf.d/api.cfg'` (template `backend.conf.epp`) → mode: `0644`
         - Passes: backend_name='api', balance='leastconn', port=3000, servers=[{name: 'api01', address: '10.1.1.20', weight: 100}, {name: 'api02', address: '10.1.1.21', weight: 100}], health_check='httpchk GET /health', health_interval='10s', ssl_enabled=false
     - **internal_monitoring**:
       - `file '/etc/haproxy/conf.d/internal_monitoring.cfg'` (template `backend.conf.epp`) → mode: `0644`
         - Passes: backend_name='internal_monitoring', balance='roundrobin', port=9090, servers=[{name: 'mon01', address: '10.1.1.30', weight: 100}], health_check='httpchk', health_interval='30s', ssl_enabled=false
   - **Iterations**: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: HTTP error page
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: HTTP error page
   - `file '/etc/haproxy/errors'` → owner: `root`, group: `root`, mode: `0755`
   - **Conditional**: if stick_table_enabled=false
     - Loop runs 0 times (when true, creates `/etc/haproxy/stick-tables.cfg`)

7. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → mode: `0644`, content: systemd override
   - `exec 'haproxy_systemd_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → mode: `0644`, content: logrotate configuration
   - **notifies**: `file[override.conf] ~> exec[haproxy_systemd_reload] ~> service[haproxy]`
   - **notifies**: `file[haproxy.cfg] ~> exec[haproxy_config_check] ~> service[haproxy]`

8. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - **Conditional**: case firewall_provider='ufw'
     - **ufw branch**:
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `ufw --force enable`
     - **firewalld branch**: `exec 'firewalld_reload'` → command: `firewall-cmd --reload`
     - **none branch**: No firewall management
     - **default branch**: `notify 'Unknown firewall provider: ${firewall_provider}'`

9. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`):
   - **Conditional**: if discovery_enabled=false
     - Loop runs 0 times
   - **When discovery_enabled=true**:
     - `@@haproxy::balancermember 'lb01.fra.example.com'` → listening_service: `webservers`, server_names: `lb01.fra.example.com`, ipaddresses: `10.1.1.5`, ports: `8080`, options: `check`
     - `<<| Haproxy::Balancermember | listening_service == 'webservers' |>>`
     - **Iterations**: `$app_servers.each` from PuppetDB query — runs N times for discovered app servers
       - For each discovered server: `haproxy::balancermember 'api-${certname}'`
     - Uses facts: `$facts['networking']['fqdn']`, `$facts['networking']['ip']`, `$facts['puppet_environment']`

## Variables

**Variable Flow Summary**: 24 variables across 8 Hiera levels

### Variable Definitions

**common.yaml (module defaults)** → Migration note: Base defaults for all nodes
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
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::global_maxconn`: `2000` (type: integer)
- `profile_haproxy::client_timeout`: `30s` (type: string)
- `profile_haproxy::server_timeout`: `30s` (type: string)
- `profile_haproxy::connect_timeout`: `5s` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+AES256:ECDHE+AES128:!aNULL:!MD5:!DSS` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::backends`: complex hash with webservers and api backends (type: hash)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::extra_packages`: `['haproxy-stats', 'socat']` (type: array)
- `profile_haproxy::ssl_ciphers`: RedHat-specific cipher suite (type: string)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::extra_packages`: `['socat']` (type: array)
- `profile_haproxy::ssl_ciphers`: Debian-specific cipher suite (type: string)

**environment/production.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::global_maxconn`: `4000` (type: integer)
- `profile_haproxy::client_timeout`: `50s` (type: string)
- `profile_haproxy::server_timeout`: `50s` (type: string)
- `profile_haproxy::log_level`: `notice` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Datacenter-specific variables for geographic deployment differences
- `profile_haproxy::log_server`: `10.1.1.100` (type: string)
- `profile_haproxy::backends`: datacenter-specific server addresses (type: hash)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: Cluster-specific variables for service group configuration
- `profile_haproxy::global_maxconn`: `6000` (type: integer)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (type: string)
- `profile_haproxy::backends`: adds internal_monitoring backend (type: hash)

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Individual host overrides for specific node configuration
- `profile_haproxy::stats_port`: `8405` (type: integer)
- `profile_haproxy::backends`: node-specific server weights (type: hash)

**common.yaml (environment-level overrides)** → Migration note: Environment-level defaults that override module defaults
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::stats_password`: `admin123` (type: string)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::extra_packages`: `[]` (type: array)
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

### Variable Migration Summary

- **Common defaults**: 24 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 4 variables that vary by operating system family (RedHat vs Debian)
- **Environment-specific variables**: 5 variables that vary by deployment environment (dev, staging, prod)
- **Datacenter-specific variables**: 2 variables for geographic deployment differences
- **Cluster-specific variables**: 3 variables for service group configuration
- **Host-specific variables**: 2 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::package_name**: defined at module and environment levels, merge strategy: first
- **profile_haproxy::stats_password**: defined at module and environment levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at module and environment levels, merge strategy: first
- **profile_haproxy::extra_packages**: defined at OS and environment levels, merge strategy: first
- **profile_haproxy::global_maxconn**: defined at module, environment, and cluster levels, merge strategy: first
- **profile_haproxy::backends**: defined at module, datacenter, cluster, and node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `hash` merge - Hash values from multiple levels are merged (shallow merge)
- Variables using `deep` merge - Hash values are recursively merged (deep merge)
- Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Custom Fact: haproxy_version**
- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Function: Executes `haproxy -v` to extract version number
- Usage: Version detection for compatibility checks
- Migration: Replace with `ansible.builtin.package_facts` or `ansible.builtin.command`

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.7.0)
- puppetlabs-concat (version: 9.0.2)
- puppetlabs-firewall (version: 8.1.3)

**System package dependencies**:
- haproxy (main package)
- haproxy-stats (RedHat only)
- socat (socket utilities)
- ufw (Ubuntu firewall)

**Service dependencies**:
- install → config → service (standard ordering)
- config changes notify service restart
- systemd daemon-reload before service operations

## Puppet Facts Used

- `$facts['kernel']`: OS kernel detection (Linux) - used in `site-modules/profile/manifests/base/base.pp`
- `$facts['networking']['fqdn']`: Fully qualified domain name for service discovery - used in `site-modules/profile_haproxy/manifests/discover.pp`
- `$facts['networking']['ip']`: IP address for load balancer member registration - used in `site-modules/profile_haproxy/manifests/discover.pp`
- `$facts['puppet_environment']`: Environment name for PuppetDB queries - used in `site-modules/profile_haproxy/manifests/discover.pp`
- `$facts['os']['family']`: OS family (RedHat/Debian) for package selection - used in `site-modules/profile/manifests/base/base.pp`
- `$facts['architecture']`: CPU architecture - used in `site-modules/profile/manifests/base/base.pp`
- `$facts['os']['name']`: OS distribution name
- `$facts['os']['release']['full']`: Full OS release version
- `$facts['os']['release']['major']`: Major OS release version
- `$facts['virtual']`: Virtualization detection
- `$facts['is_virtual']`: Container detection

## Template Conversion Notes

**haproxy.cfg.erb**:
- Variables: 19 template variables including SSL settings, timeouts, logging
- Ruby logic: 1 logic block with SSL conditional blocks, stats conditional block, backend iteration
- Complex expressions: SSL cipher configuration, backend loop with name extraction

**backend.conf.epp**:
- Variables: 10 variables including backend name, balance method, server list
- Ruby logic: Health check conditionals, server iteration with weight/SSL options
- Complex expressions: Server configuration string building with conditional SSL

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources**:
- `@@haproxy::balancermember` exports load balancer member configuration with listening_service, server_names, ipaddresses, ports, options - migration notes: requires cross-node data sharing for dynamic backend member registration

**Resource Collectors**:
- `Haproxy::Balancermember <| listening_service == 'webservers' |>` collects web server members - migration notes: requires node discovery for automatic backend configuration

**PuppetDB Queries**:
- Queries for app servers in same environment with Profile::App_server class - migration notes: requires infrastructure data access for service discovery
- Query: `query_nodes("Class[Profile::App_server] and environment=${facts['puppet_environment']}")` - migration notes: dynamic backend member discovery based on class assignment

**Host Identity Data**:
- Per-host PuppetDB data used for FQDN and IP address extraction for backend member registration - migration notes: requires node classification data for load balancer configuration

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` (main configuration)
- `/etc/haproxy/conf.d/webservers.cfg` (backend configuration)
- `/etc/haproxy/conf.d/api.cfg` (API backend configuration)
- `/etc/haproxy/conf.d/internal_monitoring.cfg` (monitoring backend)
- `/etc/haproxy/errors/503.http` (error pages)
- `/etc/haproxy/errors/408.http` (error pages)
- `/etc/systemd/system/haproxy.service.d/override.conf` (systemd override)
- `/etc/logrotate.d/haproxy` (log rotation)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 8404/8405 (statistics interface)
- Backend ports: 8080 (webservers), 3000 (api), 9090 (monitoring)

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/*.cfg` (3 renders)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# Instance-specific checks
curl -s http://localhost:8404/stats | grep -E "(webservers|api|internal_monitoring)"
curl -s http://localhost:8405/stats | grep -E "(webservers|api|internal_monitoring)"

# Configuration validation commands
haproxy -f /etc/haproxy/haproxy.cfg -c
haproxy -f /etc/haproxy/conf.d/webservers.cfg -c
haproxy -f /etc/haproxy/conf.d/api.cfg -c
haproxy -f /etc/haproxy/conf.d/internal_monitoring.cfg -c

# Network/connectivity checks
nc -zv localhost 80
nc -zv localhost 443
nc -zv localhost 8404
nc -zv localhost 8405
nc -zv 10.1.1.10 8080
nc -zv 10.1.1.11 8080
nc -zv 10.1.1.20 3000
nc -zv 10.1.1.21 3000
nc -zv 10.1.1.30 9090
```