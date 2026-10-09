---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: A comprehensive HAProxy load balancer module that installs and configures HAProxy with SSL termination, statistics interface, firewall management, service discovery via PuppetDB, and dynamic backend configuration through Hiera data. Supports multiple environments with different security and performance settings.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 9000 (stats)
  - Key Config: SSL termination, backend pools, health checks
- **webservers backend**: Primary application backend
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: 8080 (backend servers)
  - Key Config: Round-robin balancing, 3 servers
- **api backend**: API service backend
  - Location/Path: `/etc/haproxy/conf.d/api.cfg`
  - Port/Socket: 3000 (backend servers)
  - Key Config: Least-connection balancing, 2 servers

## File Structure

**Manifests**:
- `site-modules/profile_haproxy/manifests/init.pp`
- `site-modules/profile_haproxy/manifests/install.pp`
- `site-modules/profile_haproxy/manifests/config.pp`
- `site-modules/profile_haproxy/manifests/service.pp`
- `site-modules/profile_haproxy/manifests/firewall.pp`
- `site-modules/profile_haproxy/manifests/discover.pp`
- `site-modules/profile/manifests/loadbalancer/haproxy.pp`
- `site-modules/role/manifests/app_server.pp`

**Templates**:
- `site-modules/profile_haproxy/templates/haproxy.cfg.erb`
- `site-modules/profile_haproxy/templates/backend.conf.epp`

**Data Files**:
- `site-modules/profile_haproxy/data/common.yaml`
- `site-modules/profile_haproxy/data/environment/production.yaml`
- `site-modules/profile_haproxy/data/environment/staging.yaml`
- `site-modules/profile_haproxy/data/os/Debian.yaml`
- `site-modules/profile_haproxy/data/os/RedHat.yaml`
- `site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml`
- `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml`
- `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml`

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point role class that includes the HAProxy profile
   - `include profile::loadbalancer::haproxy`

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Wrapper class that includes the main HAProxy profile
   - `include profile_haproxy`

3. **profile_haproxy** (`manifests/init.pp`):
   - Sets class parameters from Hiera lookup with 21-level hierarchy
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - **Conditional**: if discovery_enabled=false (default)
     - `contain profile_haproxy::discover`
   - **Ordering**: `Class[install] -> Class[config] ~> Class[service]`
   - **Ordering**: `Class[install] -> Class[config] -> Class[discover] ~> Class[service]` (when discovery enabled)

4. **profile_haproxy::install** (`manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - **Conditional**: if extra_packages=[] (empty array from Hiera)
     - Loop runs 0 times
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, home: `/var/lib/haproxy`, shell: `/bin/false`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - **Conditional**: if selinux_enabled=true (RedHat systems)
     - `exec 'haproxy_selinux_connect'` → command: `setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_server=127.0.0.1, log_facility=local0, log_level=info, global_maxconn=4096, user=haproxy, group=haproxy, ssl_enabled=false, ssl_ciphers, connect_timeout=5s, client_timeout=30s, server_timeout=30s, retries=3, stats_enabled=true, stats_port=9000, stats_uri=/haproxy-stats, stats_user=admin, stats_password=test-haproxy-password, backends hash
   - **Iterations**: `$backends.each` — runs 2 times for: **webservers**, **api**
     - **webservers**:
       - `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
         - Passes: backend_name=webservers, balance=roundrobin, port=8080, health_check=httpchk GET /health, health_interval=5s, ssl_enabled=false, servers=[{name: web1, address: 10.0.1.10, weight: 100}, {name: web2, address: 10.0.1.11, weight: 100}, {name: web3, address: 10.0.1.12, weight: 100}]
     - **api**:
       - `file '/etc/haproxy/conf.d/api.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
         - Passes: backend_name=api, balance=leastconn, port=3000, health_check=httpchk GET /api/health, health_interval=10s, ssl_enabled=false, servers=[{name: api1, address: 10.0.2.10, weight: 100}, {name: api2, address: 10.0.2.11, weight: 100}]
   - **Iterations**: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: static error page
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: static error page
   - `file '/etc/haproxy/errors'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - **Conditional**: if stick_table_enabled=false (default)
     - No stick table configuration created
   - **notifies**: `file[haproxy.cfg] ~> service[haproxy]`, `file[webservers.cfg] ~> service[haproxy]`, `file[api.cfg] ~> service[haproxy]`

6. **profile_haproxy::service** (`manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → owner: `root`, group: `root`, mode: `0644`, content: systemd overrides
   - `exec 'haproxy_systemd_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → owner: `root`, group: `root`, mode: `0644`, content: logrotate configuration
   - **notifies**: `file[override.conf] ~> exec[haproxy_systemd_reload] ~> service[haproxy]`

7. **profile_haproxy::firewall** (`manifests/firewall.pp`):
   - **Conditional**: case firewall_provider=none (from environment Hiera)
     - **branch none**: Firewall management disabled via Hiera

8. **profile_haproxy::discover** (`manifests/discover.pp`) — only if discovery_enabled=true:
   - **Exported resource**: `@@haproxy::balancermember[$facts['networking']['fqdn']]` → listening_service: `webservers`, server_names: `$facts['networking']['fqdn']`, ipaddresses: `$facts['networking']['ip']`, ports: `8080`, options: `check`
   - **Collector**: `Haproxy::Balancermember <| listening_service == 'webservers' |>`
   - **PuppetDB query**: discovers app servers in same environment
   - **Iterations**: `$app_servers.each` — creates dynamic backend members based on PuppetDB results
   - **Facts used**: `$facts['networking']['fqdn']`, `$facts['networking']['ip']`, `$facts['puppet_environment']`

## Variables

**Variable Flow Summary**: 24 variables across 8 Hiera levels

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
- `profile_haproxy::stats_password`: `test-haproxy-password` (type: string)
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
- `profile_haproxy::firewall_provider`: `none` (type: string)
- `profile_haproxy::extra_packages`: `[]` (type: array)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

**environment/production.yaml (production overrides)** → Migration note: Production-specific variables, loaded for production environment
- `profile_haproxy::global_maxconn`: `16384` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `warning` (type: string)
- `profile_haproxy::client_timeout`: `60s` (type: string)
- `profile_haproxy::server_timeout`: `60s` (type: string)
- `profile_haproxy::stats_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `200k` (type: string)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

### Variable Migration Summary

- **Common defaults**: 28 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 1 variable that varies by operating system family
- **Environment-specific variables**: 8 variables that vary by deployment environment (dev, staging, prod)
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::global_maxconn**: defined at common and environment levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common and environment levels, merge strategy: first
- **profile_haproxy::log_level**: defined at common and environment levels, merge strategy: first
- **profile_haproxy::client_timeout**: defined at common and environment levels, merge strategy: first
- **profile_haproxy::server_timeout**: defined at common and environment levels, merge strategy: first
- **profile_haproxy::stats_enabled**: defined at common and environment levels, merge strategy: first
- **profile_haproxy::stick_table_enabled**: defined at common and environment levels, merge strategy: first
- **profile_haproxy::backends**: defined at common, datacenter, and node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (deep merge) for backends configuration
- Variables using `first` (default) - First value found wins, no merging for most configuration parameters

## Dependencies

**External module dependencies**:
- `puppetlabs-stdlib` (version: 9.7.0) - standard library functions
- `puppetlabs-concat` (version: 9.0.2) - file concatenation (not actively used)
- `puppetlabs-firewall` (version: 8.1.3) - firewall management

**System package dependencies**:
- `haproxy` - main load balancer package
- `ufw` - Ubuntu firewall (conditional on OS)

**Service dependencies**:
- Install → Config → Service ordering
- Config changes notify service restart
- Firewall rules applied after service configuration

## Puppet Facts Used

- `$facts['networking']['fqdn']` - fully qualified domain name for service discovery
- `$facts['networking']['ip']` - IP address for backend member registration
- `$facts['puppet_environment']` - environment name for PuppetDB queries
- `$facts['os']['family']` - OS family for package/service name selection

## Template Conversion Notes

**haproxy.cfg.erb**:
- Variables: 19 template variables including timeouts, SSL settings, backend configuration
- Ruby logic: SSL conditional blocks, stats conditional block, backend iteration
- Complex expressions: SSL certificate path construction, backend loop with name references

**backend.conf.epp**:
- Variables: 10 parameters including backend name, balance method, server list
- Ruby logic: Health check conditionals, server iteration with weight/SSL options
- Complex expressions: Server configuration string construction with conditional SSL parameters

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources** (`@@`): 
- `@@haproxy::balancermember[$facts['networking']['fqdn']]` - exports current node as backend member with listening_service=webservers, server_names=FQDN, ipaddresses=IP, ports=8080, options=check. Migration notes: Replace with Ansible service discovery using dynamic inventory or consul/etcd integration

**Resource Collectors** (`<<| |>`): 
- `Haproxy::Balancermember <| listening_service == 'webservers' |>` - collects all webserver backend members. Migration notes: Replace with Ansible template generation using dynamic inventory data or external service discovery

**Host Identity Data**: Per-host PuppetDB data includes FQDN and IP address used for backend member registration and cross-node service discovery patterns

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` - main configuration file
- `/etc/haproxy/conf.d/webservers.cfg` - webservers backend configuration
- `/etc/haproxy/conf.d/api.cfg` - API backend configuration
- `/etc/haproxy/errors/503.http` - custom error page
- `/etc/haproxy/errors/408.http` - custom error page
- `/etc/systemd/system/haproxy.service.d/override.conf` - systemd overrides
- `/etc/logrotate.d/haproxy` - log rotation configuration

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 9000 (statistics interface, if stats enabled)
- Backend servers on ports 8080 and 3000

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/api.cfg` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
haproxy -f /etc/haproxy/haproxy.cfg -c

# Instance-specific checks
curl -I http://localhost/health
curl http://localhost:9000/haproxy-stats

# Configuration validation commands
test -f /etc/haproxy/haproxy.cfg
test -f /etc/haproxy/conf.d/webservers.cfg
test -f /etc/haproxy/conf.d/api.cfg

# Network/connectivity checks
nc -zv localhost 80
nc -zv localhost 443
nc -zv localhost 9000
nc -zv 10.0.1.10 8080
nc -zv 10.0.1.11 8080
nc -zv 10.0.1.12 8080
nc -zv 10.0.2.10 3000
nc -zv 10.0.2.11 3000
```