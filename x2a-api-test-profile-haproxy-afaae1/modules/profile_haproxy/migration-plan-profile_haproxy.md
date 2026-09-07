---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that installs and configures HAProxy with SSL termination, statistics interface, firewall rules, and service discovery via PuppetDB. Supports multiple backends with health checks, stick tables for session persistence, and environment-specific configurations across a 21-level Hiera hierarchy.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 8404 (stats)
  - Key Config: SSL termination, session persistence, health checks
- **webservers**: Primary backend pool
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: 8080
  - Key Config: Round-robin balancing, health checks
- **api**: API backend pool
  - Location/Path: `/etc/haproxy/conf.d/api.cfg`
  - Port/Socket: 3000
  - Key Config: Least connections balancing
- **monitoring**: Monitoring backend pool (cluster-specific)
  - Location/Path: `/etc/haproxy/conf.d/monitoring.cfg`
  - Port/Socket: 9090
  - Key Config: Health check disabled

## File Structure

```
site-modules/role/manifests/haproxy.pp
site-modules/profile/manifests/loadbalancer/haproxy.pp
site-modules/profile_haproxy/manifests/init.pp
site-modules/profile_haproxy/manifests/install.pp
site-modules/profile_haproxy/manifests/config.pp
site-modules/profile_haproxy/manifests/service.pp
site-modules/profile_haproxy/manifests/firewall.pp
site-modules/profile_haproxy/manifests/discover.pp
site-modules/profile_haproxy/templates/haproxy.cfg.erb
site-modules/profile_haproxy/templates/backend.conf.epp
site-modules/profile_haproxy/data/common.yaml
site-modules/profile_haproxy/data/environment/production.yaml
site-modules/profile_haproxy/data/environment/staging.yaml
site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml
site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml
site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml
site-modules/profile_haproxy/data/os/Debian.yaml
site-modules/profile_haproxy/data/os/RedHat.yaml
site-modules/profile_haproxy/lib/facter/haproxy_version.rb
```

## Module Explanation

The module performs operations in this order:

1. **role::haproxy** (`site-modules/role/manifests/haproxy.pp`):
   - Entry point class that includes the profile
   - `include profile::loadbalancer::haproxy`
   - Conditional based on `$facts['kernel']` for Linux systems

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Wrapper class that includes the main profile
   - `include profile_haproxy`
   - Uses `fact('environment')` for environment-specific logic

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from 21-level Hiera hierarchy
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - Conditional: if discovery_enabled=true
     - `contain profile_haproxy::discover`
     - Sets ordering: `profile_haproxy::install -> profile_haproxy::config -> profile_haproxy::discover ~> profile_haproxy::service`
   - Default ordering: `profile_haproxy::install -> profile_haproxy::config ~> profile_haproxy::service`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - Iterations: `$extra_packages.each` — runs 1 time for: **hatop** (Debian) or **haproxy-selinux** (RedHat)
     - **hatop**: `package 'hatop'` → ensure: `present` (Debian)
     - **haproxy-selinux**: `package 'haproxy-selinux'` → ensure: `present` (RedHat)
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, shell: `/sbin/nologin`, home: `/var/lib/haproxy`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - Conditional: if selinux_enabled=true (RedHat)
     - `exec 'haproxy_selinux_connect'` → command: `setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
   - Iterations: `$backends.each` — runs 3 times for: **webservers**, **api**, **monitoring**
     - **webservers**:
       - `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
     - **api**:
       - `file '/etc/haproxy/conf.d/api.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
     - **monitoring**:
       - `file '/etc/haproxy/conf.d/monitoring.cfg'` (template `backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
   - Iterations: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: HTTP error page
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: HTTP error page
   - `file '/etc/haproxy/errors'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - Conditional: if stick_table_enabled=true (production/staging)
     - `file '/etc/haproxy/conf.d/stick-tables.cfg'` → content: stick table configuration for session persistence

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → content: systemd service overrides
   - `exec 'haproxy_systemd_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → content: log rotation configuration

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Conditional: case firewall_provider
     - **Branch firewalld** (RedHat):
       - `exec 'firewalld_reload'` → command: `firewall-cmd --reload`
     - **Branch ufw** (Debian):
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `ufw --force enable`
     - **Branch none**: Firewall management disabled via Hiera
     - **Branch default**: `notify 'Unknown firewall provider: ${firewall_provider}'`

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — Conditional: if discovery_enabled=true
   - Exported resource: `@@haproxy::balancermember[lb01.fra.example.com]` → listening_service: `webservers`, server_names: `lb01.fra.example.com`, ipaddresses: `10.1.1.5`, ports: `8080`, options: `check`
   - Collector: `Haproxy::Balancermember <| listening_service == 'webservers' |>` → collects exported resources
   - Iterations: `$app_servers.each` — Variable iteration count based on PuppetDB query results
     - Instance expansion: Creates `haproxy::balancermember["api-${certname}"]` for each discovered app server

## Variables

**Variable Flow Summary**: 24 variables across 8 Hiera levels with deep merge for backends hash

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
- `profile_haproxy::stats_password`: `[ENCRYPTED]` (type: string)
- `profile_haproxy::global_maxconn`: `4000` (type: integer)
- `profile_haproxy::client_timeout`: `30s` (type: string)
- `profile_haproxy::server_timeout`: `30s` (type: string)
- `profile_haproxy::connect_timeout`: `5s` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+AES256:!aNULL:!MD5` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `notice` (type: string)
- `profile_haproxy::backends`: complex hash with webservers and api backends (type: hash)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `['hatop']` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::firewall_zone`: `public` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-selinux']` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

**environment/production.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::global_maxconn`: `10000` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::client_timeout`: `50s` (type: string)
- `profile_haproxy::server_timeout`: `50s` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `100k` (type: string)
- `profile_haproxy::stick_table_expire`: `30m` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::global_maxconn`: `2000` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Datacenter-specific variables for geographic deployment differences
- `profile_haproxy::log_server`: `rsyslog.fra.example.com` (type: string)
- `profile_haproxy::backends`: datacenter-specific server addresses (type: hash)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: Cluster-specific variables for high-performance production clusters
- `profile_haproxy::global_maxconn`: `15000` (type: integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+AES256:ECDHE+AES128:!aNULL:!MD5:!DSS` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (type: string)
- `profile_haproxy::backends`: adds monitoring backend (type: hash)

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Host-specific variables for individual node overrides
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_port`: `8404` (type: integer)
- `profile_haproxy::backends`: node-specific server weights (type: hash)

### Variable Migration Summary

- **Common defaults**: 24 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 4 variables that vary by operating system family
- **Environment-specific variables**: 9 variables that vary by deployment environment (production, staging)
- **Datacenter-specific variables**: 2 variables that vary by geographic location
- **Cluster-specific variables**: 4 variables for high-performance production clusters
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::global_maxconn**: defined at common, environment, cluster levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common, environment levels, merge strategy: first
- **profile_haproxy::backends**: defined at common, datacenter, cluster, node levels, merge strategy: deep
- **profile_haproxy::stats_enabled**: defined at common, environment, node levels, merge strategy: first
- **profile_haproxy::log_level**: defined at common, environment levels, merge strategy: first

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (deep merge) for backends configuration
- Variables using `first` (default) - First value found wins, no merging for most scalar values

## Custom Types and Providers

**Custom Fact: haproxy_version**
- **File**: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- **Purpose**: Executes `haproxy -v` to extract version number using regex
- **Parameters**: None (system fact)
- **Returns**: HAProxy version string

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.7.0) - standard library functions
- puppetlabs-concat (version: 9.0.2) - file concatenation
- puppetlabs-firewall (version: 8.1.3) - firewall management

**System package dependencies**:
- haproxy (main package)
- hatop (Debian monitoring tool)
- haproxy-selinux (RedHat SELinux support)
- ufw (Debian firewall)

**Service dependencies**:
- install → config → service (standard ordering)
- config changes notify service restart
- systemd daemon-reload before service start

## Puppet Facts Used

- `$facts['kernel']`: OS kernel type (Linux detection) for role class conditional
- `$facts['networking']['fqdn']`: Fully qualified domain name for exported resources
- `$facts['networking']['ip']`: IP address for load balancer member registration
- `$facts['puppet_environment']`: Environment name for PuppetDB queries
- `$facts['os']['family']`: OS family (Debian/RedHat) for package/firewall selection
- `fact('environment')`: Environment name used in profile wrapper class

## Template Conversion Notes

**haproxy.cfg.erb**:
- **Variables**: 19 variables including SSL configuration, timeouts, logging, stats
- **Ruby logic blocks**: Complex SSL conditional rendering for HTTPS binding and cipher configuration
- **Conditional rendering**: SSL certificate path concatenation, conditional redirects based on environment
- **Iterations**: Backend loop for including configuration files from conf.d directory
- **Complex expressions**: Dynamic SSL verification settings and timeout calculations

**backend.conf.epp**:
- **Variables**: 10 variables for backend configuration (name, balance method, servers, health checks)
- **Ruby logic blocks**: Conditional health check and SSL options rendering
- **Iterations**: Server loop for backend member configuration with weight and SSL settings
- **Complex expressions**: Server weight calculations and SSL verification parameter handling

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries.

**Exported Resources** (`@@`):
- `@@haproxy::balancermember` exports load balancer member information for service discovery
- Resource type: haproxy::balancermember, exports listening_service, server_names, ipaddresses, ports, and options
- Migration notes: Cross-node data sharing pattern requires centralized service registry in Ansible equivalent

**Resource Collectors** (`<<| |>`):
- Collects `Haproxy::Balancermember` resources where listening_service matches 'webservers'
- Filter condition: `listening_service == 'webservers'`
- Migration notes: Node discovery requirements need dynamic inventory or service discovery mechanism

**PuppetDB Queries**:
- Searches for nodes with `Profile::App_server` class in the same environment
- Returned data: Node certnames and IP addresses for backend registration
- Migration notes: Infrastructure data access patterns require dynamic inventory queries or external CMDB integration

**Host Identity Data**:
- Per-host PuppetDB data includes FQDN, IP address, and environment classification
- Used for node classification and automatic backend member registration

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` (main configuration)
- `/etc/haproxy/conf.d/webservers.cfg` (backend configuration)
- `/etc/haproxy/conf.d/api.cfg` (API backend configuration)
- `/etc/haproxy/conf.d/monitoring.cfg` (monitoring backend - cluster specific)
- `/etc/haproxy/conf.d/stick-tables.cfg` (session persistence - production only)
- `/etc/haproxy/errors/503.http` (error page)
- `/etc/haproxy/errors/408.http` (error page)
- `/etc/systemd/system/haproxy.service.d/override.conf` (systemd overrides)
- `/etc/logrotate.d/haproxy` (log rotation)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend - production only)
- Port 8404 (statistics interface)
- Backend ports: 8080 (webservers), 3000 (api), 9090 (monitoring)

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/*.cfg` (3 renders: webservers, api, monitoring)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# Instance-specific checks
curl -f http://localhost:8404/stats  # haproxy stats interface
curl -f http://localhost:80/health   # webservers backend health
curl -f http://localhost:3000/health # api backend health
curl -f http://localhost:9090/health # monitoring backend health

# Configuration validation commands
haproxy -f /etc/haproxy/haproxy.cfg -c
haproxy -f /etc/haproxy/haproxy.cfg -db

# Network/connectivity checks
ss -tlnp | grep :80    # HTTP port listening
ss -tlnp | grep :443   # HTTPS port listening (production)
ss -tlnp | grep :8404  # Stats port listening
netstat -an | grep :8080  # webservers backend connectivity
netstat -an | grep :3000  # api backend connectivity
netstat -an | grep :9090  # monitoring backend connectivity

# Firewall verification
ufw status                           # Debian firewall rules
firewall-cmd --list-all             # RedHat firewall rules

# SSL certificate validation (if SSL enabled)
openssl x509 -in /etc/ssl/certs/haproxy.pem -text -noout
openssl verify /etc/ssl/certs/haproxy.pem
```