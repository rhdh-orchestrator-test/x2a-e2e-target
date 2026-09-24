---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that installs and configures HAProxy with SSL termination, statistics interface, backend server pools, firewall rules, and optional service discovery via PuppetDB. Supports multiple OS families with different firewall providers and includes comprehensive logging and health checking.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 9000 (stats)
  - Key Config: SSL termination, backend pools, health checks
- **webservers**: Backend pool for web traffic
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: 8080
  - Key Config: Round-robin balancing, 3 servers
- **api**: Backend pool for API traffic
  - Location/Path: `/etc/haproxy/conf.d/api.cfg`
  - Port/Socket: 3000
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
- `site-modules/profile_haproxy/data/os/RedHat.yaml`
- `site-modules/profile_haproxy/data/os/Debian.yaml`
- `site-modules/profile_haproxy/data/environment/production.yaml`
- `site-modules/profile_haproxy/data/environment/staging.yaml`
- `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml`
- `site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml`
- `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml`

**Custom Components**:
- `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that establishes service architecture
   - `contain profile::loadbalancer::haproxy`

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - `contain profile_haproxy`

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from Hiera lookup with 21-level hierarchy
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - **Conditional**: if discovery_enabled=false (default)
     - Sets ordering: `profile_haproxy::install -> profile_haproxy::config ~> profile_haproxy::service`
   - **Conditional**: if discovery_enabled=true
     - `contain profile_haproxy::discover`
     - Sets ordering: `profile_haproxy::install -> profile_haproxy::config -> profile_haproxy::discover ~> profile_haproxy::service`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - **Conditional**: if extra_packages not empty
     - **RedHat**: `package 'haproxy-systemd-wrapper'` → ensure: `present`
     - **RedHat**: `package 'policycoreutils-python-utils'` → ensure: `present`
     - **Debian**: `package 'hatop'` → ensure: `present`
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, shell: `/sbin/nologin`, home: `/var/lib/haproxy`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - **Conditional**: if selinux_enabled=true (RedHat only)
     - `exec 'haproxy_selinux_connect'` → command: `setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
     - Passes: log_server=127.0.0.1, log_facility=local0, log_level=info, global_maxconn=4096, user=haproxy, group=haproxy, ssl_enabled=false, connect_timeout=5s, client_timeout=30s, server_timeout=30s, retries=3, stats_enabled=true, stats_port=9000, stats_uri=/haproxy-stats, stats_user=admin, stats_password=[encrypted], backends hash
   - **Iterations**: `$backends.each` — runs 2 times for: **webservers**, **api**
     - **webservers**:
       - `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
       - Passes: backend_name=webservers, balance=roundrobin, port=8080, health_check=httpchk GET /health, health_interval=5s, ssl_enabled=false, servers=[{name: web1, address: 10.0.1.10, weight: 100}, {name: web2, address: 10.0.1.11, weight: 100}, {name: web3, address: 10.0.1.12, weight: 100}]
     - **api**:
       - `file '/etc/haproxy/conf.d/api.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
       - Passes: backend_name=api, balance=leastconn, port=3000, health_check=httpchk GET /api/health, health_interval=10s, ssl_enabled=false, servers=[{name: api1, address: 10.0.2.10, weight: 100}, {name: api2, address: 10.0.2.11, weight: 100}]
   - **Iterations**: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: HTTP error page
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: HTTP error page
   - `file '/etc/haproxy/errors'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - **Conditional**: if stick_table_enabled=true
     - `file '/etc/haproxy/conf.d/stick-tables.cfg'` → content: stick table configuration
   - **notifies**: `file[haproxy.cfg] ~> service[haproxy]`, `file[webservers.cfg] ~> service[haproxy]`, `file[api.cfg] ~> service[haproxy]`

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → content: systemd override configuration
   - `exec 'haproxy_systemd_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → content: logrotate configuration
   - **notifies**: `file[override.conf] ~> exec[haproxy_systemd_reload] ~> service[haproxy]`

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - **Conditional**: case firewall_provider
     - **Branch**: firewalld (RedHat)
       - `exec 'firewalld_reload'` → command: `firewall-cmd --reload`
     - **Branch**: ufw (Debian)
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `ufw --force enable`
     - **Branch**: none
       - No firewall configuration
     - **Branch**: default
       - `notify 'Unknown firewall provider'` → message: warning

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — only if discovery_enabled=true:
   - `@@haproxy::balancermember 'node.example.com'` → listening_service: `webservers`, server_names: `node.example.com`, ipaddresses: `10.0.1.100`, ports: `8080`, options: `check`
   - `<<| Haproxy::Balancermember |>>` → collects all exported balancermember resources where listening_service == 'webservers'
   - **Iterations**: `$app_servers.each` — runs based on PuppetDB query results
     - **Instance expansion**: Creates haproxy::balancermember resources for each discovered app server
   - **PuppetDB Query**: Discovers app servers in same environment with Profile::App_server class

## Variables

**Variable Flow Summary**: 25+ variables across 8 Hiera levels

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
- `profile_haproxy::backends`: `{webservers: {...}, api: {...}}` (type: hash)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::firewall_zone`: `public` (type: string)
- `profile_haproxy::extra_packages`: `[haproxy-systemd-wrapper, policycoreutils-python-utils]` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `[hatop]` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**environment/production.yaml (environment-specific)** → Migration note: Variables that vary by deployment environment (dev, staging, prod)
- `profile_haproxy::global_maxconn`: `8192` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `warning` (type: string)
- `profile_haproxy::client_timeout`: `60s` (type: string)
- `profile_haproxy::server_timeout`: `60s` (type: string)
- `profile_haproxy::stats_enabled`: `false` (type: boolean)

### Variable Migration Summary

- **Common defaults**: 25 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 4 variables (RedHat), 3 variables (Debian) that vary by operating system family
- **Environment-specific variables**: 6 variables (production), 4 variables (staging) that vary by deployment environment
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable (stats_password) that is encrypted and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::global_maxconn**: defined at common, environment, cluster levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common, environment levels, merge strategy: first
- **profile_haproxy::stats_enabled**: defined at common, environment, cluster, node levels, merge strategy: first
- **profile_haproxy::log_server**: defined at common, cluster, datacenter levels, merge strategy: first
- **profile_haproxy::backends**: defined at common, cluster, datacenter, node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (deep merge)
- Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Custom Fact: haproxy_version**
- **File**: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- **Purpose**: Executes `haproxy -v` to extract version number using regex
- **Parameters**: None (fact collection)
- **Returns**: HAProxy version string

## Dependencies

**External module dependencies**:
- `puppetlabs-stdlib` (version: 9.7.0)
- `puppetlabs-concat` (version: 9.0.2)
- `puppetlabs-firewall` (version: 8.1.3)

**System package dependencies**:
- `haproxy` (main package)
- `haproxy-systemd-wrapper` (RedHat only)
- `policycoreutils-python-utils` (RedHat only)
- `hatop` (Debian only)
- `ufw` (Debian firewall)

**Service dependencies**:
- Install → Config → Service (notification chain)
- Config changes notify service restart
- Discovery (if enabled) runs after config, before service

## Puppet Facts Used

- `$facts['networking']['fqdn']`: Fully qualified domain name for service discovery
- `$facts['networking']['ip']`: IP address for service discovery
- `$facts['puppet_environment']`: Environment name for PuppetDB queries
- `$facts['os']['family']`: OS family (RedHat/Debian) for package selection
- Custom fact `haproxy_version`: HAProxy version detection

## Template Conversion Notes

**haproxy.cfg.erb**:
- **Variables**: 19 variables including log_server, global_maxconn, timeouts, SSL settings, stats configuration
- **Ruby logic blocks**: 1 logic block total containing SSL conditional blocks, stats conditional block, backends iteration
- **Complex expressions**: SSL certificate path concatenation, backend inclusion comments

**backend.conf.epp**:
- **Variables**: 10 variables including backend_name, balance method, port, servers array
- **Ruby logic blocks**: Health check conditionals, SSL server options
- **Iterations**: Server array iteration with weight and SSL options

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources**: 
- `@@haproxy::balancermember` exports server information for load balancer discovery with listening_service, server_names, ipaddresses, ports, options → Migration notes: Cross-node data sharing patterns require service discovery mechanism in Ansible

**Resource Collectors**: 
- `<<| Haproxy::Balancermember |>>` collects exported resources where listening_service == 'webservers' → Migration notes: Node discovery requirements need inventory-based solution

**PuppetDB Queries**: 
- Discovers app servers with Profile::App_server class in same environment → Migration notes: Infrastructure data access patterns require dynamic inventory or fact gathering
- Query: `resources[certname, parameters] { type = 'Class' and title = 'Profile::App_server' and certname in resources[certname] { type = 'Class' and title = 'Profile::Base' and parameters.environment = '${facts['puppet_environment']}' } }`

**Host Identity Data**: 
- Per-host PuppetDB data used for node classification and service discovery → Migration notes: Node classification requires group_vars and host_vars structure

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` (main configuration)
- `/etc/haproxy/conf.d/webservers.cfg` (backend configuration)
- `/etc/haproxy/conf.d/api.cfg` (backend configuration)
- `/etc/haproxy/errors/503.http` (error pages)
- `/etc/haproxy/errors/408.http` (error pages)
- `/etc/systemd/system/haproxy.service.d/override.conf` (systemd override)
- `/etc/logrotate.d/haproxy` (log rotation)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 9000 (statistics interface, if stats enabled)
- Backend ports 8080, 3000 (health checks)

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
curl -I http://localhost:8080/health
curl -I http://localhost:3000/api/health

# Configuration validation commands
test -f /etc/haproxy/haproxy.cfg
test -f /etc/haproxy/conf.d/webservers.cfg
test -f /etc/haproxy/conf.d/api.cfg

# Network/connectivity checks
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :9000
```