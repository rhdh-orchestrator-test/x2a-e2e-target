---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile::loadbalancer::haproxy

**TLDR**: Comprehensive HAProxy load balancer module with SSL termination, statistics interface, firewall management, service discovery via PuppetDB, and multi-backend configuration. Manages 2 backends (webservers, api) with health checks, supports both firewalld and ufw, includes systemd service overrides, and provides automatic server discovery through exported resources.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: /etc/haproxy/haproxy.cfg
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 9000/9001 (stats)
  - Key Config: SSL termination, 2 backends, health checks
- **webservers backend**: Web application servers
  - Location/Path: /etc/haproxy/conf.d/webservers.cfg
  - Port/Socket: 8080 (backend servers)
  - Key Config: roundrobin, 3 servers, httpchk health
- **api backend**: API application servers
  - Location/Path: /etc/haproxy/conf.d/api.cfg
  - Port/Socket: 3000 (backend servers)
  - Key Config: leastconn, 2 servers, httpchk health

## File Structure

```
site-modules/role/manifests/app_server.pp
site-modules/profile/manifests/loadbalancer/haproxy.pp
site-modules/profile/templates/loadbalancer/haproxy/haproxy.cfg.erb
site-modules/profile/templates/loadbalancer/haproxy/backend.conf.epp
site-modules/profile/data/common.yaml
site-modules/profile/data/nodes/lb01.fra.example.com.yaml
site-modules/profile/data/cluster/haproxy_prod_fra.yaml
site-modules/profile/data/environment/production.yaml
site-modules/profile/data/environment/staging.yaml
site-modules/profile/data/datacenter/dc1_fra.yaml
site-modules/profile/data/os/RedHat.yaml
site-modules/profile/data/os/Debian.yaml
site-modules/profile/lib/facter/haproxy_version.rb
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes the HAProxy profile
   - `include profile::loadbalancer::haproxy`
   - Sets up application server role with load balancer functionality

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Sets class parameters from 21-level Hiera hierarchy
   - `package 'haproxy'` → ensure: `present`
   - **Conditional**: if extra_packages=['haproxy-stats', 'rsyslog'] (RedHat) or ['haproxy-doc'] (Debian)
     - `package 'haproxy-stats'` → ensure: `present` (RedHat only)
     - `package 'rsyslog'` → ensure: `present` (RedHat only)
     - `package 'haproxy-doc'` → ensure: `present` (Debian only)
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, shell: `/sbin/nologin`, home: `/var/lib/haproxy`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - **Conditional**: if selinux_enabled=true (RedHat only)
     - `exec 'haproxy_selinux_connect'` → command: `setsebool -P haproxy_connect_any 1`
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_server=127.0.0.1, log_facility=local0, log_level=info, global_maxconn=4096, user=haproxy, group=haproxy, ssl_enabled=false, ssl_ciphers=ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256, connect_timeout=5s, client_timeout=30s, server_timeout=30s, retries=3, stats_enabled=true, stats_port=9000, stats_uri=/haproxy-stats, stats_user=admin, stats_password=[encrypted], ssl_cert_path=/etc/ssl/certs, backends=hash
   - **Iterations**: `$backends.each` — runs 2 times for: **webservers**, **api**
     - **webservers**:
       - `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
         - Passes: backend_name=webservers, balance=roundrobin, port=8080, health_check=httpchk GET /health, health_interval=5s, ssl_enabled=false
         - Servers: web1 (10.0.1.10:8080 weight 100), web2 (10.0.1.11:8080 weight 100), web3 (10.0.1.12:8080 weight 100)
     - **api**:
       - `file '/etc/haproxy/conf.d/api.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
         - Passes: backend_name=api, balance=leastconn, port=3000, health_check=httpchk GET /api/health, health_interval=10s, ssl_enabled=false
         - Servers: api1-fra (10.100.2.10:3000 weight 200), api2-fra (10.100.2.11:3000 weight 100)
   - **Iterations**: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: HTTP error page
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: HTTP error page
   - `file '/etc/haproxy/errors'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → owner: `root`, group: `root`, mode: `0644`
   - `exec 'haproxy_systemd_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → owner: `root`, group: `root`, mode: `0644`
   - **Conditional**: case firewall_provider
     - **firewalld** (RedHat):
       - `exec 'firewalld_reload'` → command: `firewall-cmd --reload`
     - **ufw** (Debian):
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `ufw --force enable`
   - **Conditional**: if discovery_enabled=false (not executed by default):
     - `@@haproxy::balancermember[$facts['networking']['fqdn']]` → listening_service: `webservers`, server_names: `$facts['networking']['fqdn']`, ipaddresses: `$facts['networking']['ip']`, ports: `8080`, options: `check`
     - `<<| Haproxy::Balancermember <| listening_service == 'webservers' |>` → collects exported resources
     - **Iterations**: `$app_servers.each` — Loop runs 0 times (app_servers from PuppetDB query is empty by default)
   - **notifies**: `file[override.conf] ~> exec[haproxy_systemd_reload] ~> service[haproxy]`
   - **notifies**: `file[haproxy.cfg] ~> exec[haproxy_config_check] ~> service[haproxy]`

## Variables

**Variable Flow Summary**: 25 variables across 8 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile::loadbalancer::haproxy::package_name`: `haproxy` (type: string)
- `profile::loadbalancer::haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile::loadbalancer::haproxy::config_file`: `/etc/haproxy/haproxy.cfg` (type: string)
- `profile::loadbalancer::haproxy::service_name`: `haproxy` (type: string)
- `profile::loadbalancer::haproxy::user`: `haproxy` (type: string)
- `profile::loadbalancer::haproxy::group`: `haproxy` (type: string)
- `profile::loadbalancer::haproxy::global_maxconn`: `4096` (type: integer)
- `profile::loadbalancer::haproxy::client_timeout`: `30s` (type: string)
- `profile::loadbalancer::haproxy::server_timeout`: `30s` (type: string)
- `profile::loadbalancer::haproxy::connect_timeout`: `5s` (type: string)
- `profile::loadbalancer::haproxy::retries`: `3` (type: integer)
- `profile::loadbalancer::haproxy::ssl_enabled`: `false` (type: boolean)
- `profile::loadbalancer::haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile::loadbalancer::haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile::loadbalancer::haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256` (type: string)
- `profile::loadbalancer::haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile::loadbalancer::haproxy::stats_enabled`: `true` (type: boolean)
- `profile::loadbalancer::haproxy::stats_port`: `9000` (type: integer)
- `profile::loadbalancer::haproxy::stats_uri`: `/haproxy-stats` (type: string)
- `profile::loadbalancer::haproxy::stats_user`: `admin` (type: string)
- `profile::loadbalancer::haproxy::stats_password`: `[encrypted]` (type: string)
- `profile::loadbalancer::haproxy::log_server`: `127.0.0.1` (type: string)
- `profile::loadbalancer::haproxy::log_facility`: `local0` (type: string)
- `profile::loadbalancer::haproxy::log_level`: `info` (type: string)
- `profile::loadbalancer::haproxy::backends`: `hash with webservers and api backends` (type: hash)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile::loadbalancer::haproxy::firewall_provider`: `firewalld` (type: string)
- `profile::loadbalancer::haproxy::extra_packages`: `['haproxy-stats', 'rsyslog']` (type: array)
- `profile::loadbalancer::haproxy::selinux_enabled`: `true` (type: boolean)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile::loadbalancer::haproxy::firewall_provider`: `ufw` (type: string)
- `profile::loadbalancer::haproxy::extra_packages`: `['haproxy-doc']` (type: array)
- `profile::loadbalancer::haproxy::selinux_enabled`: `false` (type: boolean)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Datacenter-specific variables, loaded based on datacenter classification
- `profile::loadbalancer::haproxy::log_server`: `10.100.1.5` (type: string)

**environment/production.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment (dev, staging, prod)
- `profile::loadbalancer::haproxy::global_maxconn`: `16384` (type: integer)
- `profile::loadbalancer::haproxy::client_timeout`: `60s` (type: string)
- `profile::loadbalancer::haproxy::server_timeout`: `60s` (type: string)
- `profile::loadbalancer::haproxy::ssl_enabled`: `true` (type: boolean)
- `profile::loadbalancer::haproxy::stats_enabled`: `true` (type: boolean)
- `profile::loadbalancer::haproxy::log_level`: `warning` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment (dev, staging, prod)
- `profile::loadbalancer::haproxy::stats_enabled`: `true` (type: boolean)
- `profile::loadbalancer::haproxy::log_level`: `debug` (type: string)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: Cluster-specific variables for grouped node configurations
- `profile::loadbalancer::haproxy::global_maxconn`: `32768` (type: integer)
- `profile::loadbalancer::haproxy::ssl_ciphers`: `ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305` (type: string)
- `profile::loadbalancer::haproxy::ssl_min_version`: `TLSv1.3` (type: string)

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Host-specific variables for individual host overrides
- `profile::loadbalancer::haproxy::stats_enabled`: `true` (type: boolean)
- `profile::loadbalancer::haproxy::stats_port`: `9001` (type: integer)

### Variable Migration Summary

- **Common defaults**: 25 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 3 variables that vary by operating system family
- **Environment-specific variables**: 6 variables that vary by deployment environment (dev, staging, prod)
- **Host-specific variables**: 2 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile::loadbalancer::haproxy::stats_password**: defined at common and environment levels, merge strategy: first
- **profile::loadbalancer::haproxy::ssl_enabled**: defined at common, environment, and production levels, merge strategy: first
- **profile::loadbalancer::haproxy::global_maxconn**: defined at common, environment, and cluster levels, merge strategy: first
- **profile::loadbalancer::haproxy::backends**: defined at common, datacenter, and node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `hash` merge - Hash values from multiple levels are merged (shallow merge)
- Variables using `deep` merge - Hash values are recursively merged (deep merge)
- Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Custom Fact: haproxy_version**
- File: `site-modules/profile/lib/facter/haproxy_version.rb`
- Purpose: Executes `haproxy -v` to extract version number
- OS Restriction: Linux only
- Parameters: None
- Returns: HAProxy version string

## Dependencies

**External module dependencies**: 
- puppetlabs-stdlib (version: 9.7.0)
- puppetlabs-concat (version: 9.0.2)
- puppetlabs-firewall (version: 8.1.3)

**System package dependencies**:
- haproxy (main package)
- haproxy-stats, rsyslog (RedHat family)
- haproxy-doc (Debian family)
- ufw (Debian firewall)

**Service dependencies**:
- install → config → service (standard ordering)
- config changes notify service restart
- systemd daemon-reload before service operations

## Puppet Facts Used

- `$facts['networking']['fqdn']`: Fully qualified domain name for service discovery
- `$facts['networking']['ip']`: IP address for service discovery
- `$facts['puppet_environment']`: Environment name for PuppetDB queries
- `$facts['os']['family']`: OS family for package/firewall selection
- Custom fact `haproxy_version`: HAProxy version detection

## Template Conversion Notes

**haproxy.cfg.erb**:
- Variables: 19 variables including timeouts, SSL config, stats config, logging
- Ruby logic: SSL conditional blocks, stats conditional block, backends iteration
- Conditional rendering: SSL configuration blocks based on ssl_enabled flag
- Iterations: Backend configuration loop
- Complex expressions: SSL cipher configuration, backend inclusion comments

**backend.conf.epp**:
- Variables: 10 variables for backend configuration
- Ruby logic: Health check conditionals, server iteration with weight/SSL options
- Conditional rendering: Health check configuration based on health_check parameter
- Iterations: Server configuration loop with dynamic parameters
- Complex expressions: Dynamic server line generation with conditional SSL parameters

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources** (`@@`): 
- `@@haproxy::balancermember[$facts['networking']['fqdn']]` exports server information for load balancer discovery, migration notes about cross-node data sharing patterns require centralized service registry

**Resource Collectors** (`<<| |>`): 
- `Haproxy::Balancermember <| listening_service == 'webservers' |>` collects web servers for backend configuration, migration notes about node discovery requirements need service discovery mechanism

**PuppetDB Queries**: 
- Discovers app servers with Profile::App_server class in same environment for dynamic backend population, migration notes about infrastructure data access patterns require inventory management system

**Host Identity Data**: 
- Per-host PuppetDB data includes FQDN and IP address used for node classification and service registration

## Checks for the Migration

**Files to verify**:
- /etc/haproxy/haproxy.cfg
- /etc/haproxy/conf.d/webservers.cfg
- /etc/haproxy/conf.d/api.cfg
- /etc/haproxy/errors/503.http
- /etc/haproxy/errors/408.http
- /etc/systemd/system/haproxy.service.d/override.conf
- /etc/logrotate.d/haproxy

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 9000/9001 (statistics interface)
- Backend servers on ports 8080, 3000

**Templates rendered**:
- haproxy.cfg.erb (1 render with 19 variables)
- backend.conf.epp (2 renders for webservers and api backends)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
haproxy -f /etc/haproxy/haproxy.cfg -c

# Instance-specific checks
curl -s http://localhost:9000/haproxy-stats
curl -s http://localhost:9001/haproxy-stats
curl -s http://10.0.1.10:8080/health
curl -s http://10.0.1.11:8080/health
curl -s http://10.0.1.12:8080/health
curl -s http://10.100.2.10:3000/api/health
curl -s http://10.100.2.11:3000/api/health

# Configuration validation commands
haproxy -f /etc/haproxy/haproxy.cfg -c
test -f /etc/haproxy/conf.d/webservers.cfg
test -f /etc/haproxy/conf.d/api.cfg

# Network/connectivity checks
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :9000
netstat -tlnp | grep :9001
```