---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that installs and configures HAProxy with SSL termination, statistics interface, firewall rules, and dynamic backend discovery via PuppetDB. Supports multiple backends with health checks, error pages, and systemd service management.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 8404 (stats)
  - Key Config: SSL termination, backend pools, health checks
- **webservers**: Primary backend pool
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: Backend servers on port 8080
  - Key Config: Round-robin load balancing, health checks
- **api**: API backend pool
  - Location/Path: `/etc/haproxy/conf.d/api.cfg`
  - Port/Socket: Backend servers on port 3000
  - Key Config: Least connections balancing, SSL to backends

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
└── lib/
    └── facter/
        └── haproxy_version.rb

site-modules/role/
└── manifests/
    └── haproxy.pp

site-modules/profile/
└── manifests/
    └── loadbalancer/
        └── haproxy.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::haproxy** (`site-modules/role/manifests/haproxy.pp`):
   - Kernel detection using `$facts['kernel']` for Linux validation
   - `include profile::loadbalancer::haproxy`
   - Sets class ordering and execution context

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Wrapper class using `fact('environment')` for environment detection
   - `include profile_haproxy`
   - Provides abstraction layer for role-based classification

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from Hiera lookup
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - **Conditional**: if `$discovery_enabled` is true
     - `contain profile_haproxy::discover`
     - Sets ordering: `profile_haproxy::install -> profile_haproxy::config -> profile_haproxy::discover ~> profile_haproxy::service`
   - **Default ordering**: `profile_haproxy::install -> profile_haproxy::config ~> profile_haproxy::service`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - **Conditional**: if `!empty($extra_packages)`
     - Iterations: `$extra_packages.each` — runs 0 times (empty array by default)
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, home: `/var/lib/haproxy`, shell: `/sbin/nologin`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - **Conditional**: if `$selinux_enabled` is true
     - `exec 'haproxy_selinux_connect'` → command: `/usr/sbin/setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
   - **Iterations**: `$backends.each` — runs dynamically based on Hiera data (default: **webservers**, **api**)
     - **webservers**:
       - `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`)
     - **api**:
       - `file '/etc/haproxy/conf.d/api.cfg'` (template `backend.conf.epp`)
   - **Iterations**: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → static error page content
     - **408**: `file '/etc/haproxy/errors/408.http'` → static error page content
   - `file '/etc/haproxy/errors'` → ensure: `directory`
   - **Conditional**: if `$stick_table_enabled` is true
     - `file '/etc/haproxy/conf.d/stick-tables.cfg'` → stick table configuration
   - **notifies**: Configuration changes notify service restart

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → systemd overrides
   - `exec 'haproxy_systemd_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`
   - `exec 'haproxy_config_check'` → command: `/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → log rotation configuration

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - **Conditional**: case `$firewall_provider`
     - **ufw branch** (default):
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `/usr/sbin/ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `/usr/sbin/ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `/usr/sbin/ufw --force enable`
     - **firewalld branch**: Alternative firewall configuration
     - **none branch**: No firewall configuration

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — **Conditional**: only executed if `$discovery_enabled` is true
   - `@@haproxy::balancermember[$facts['networking']['fqdn']]` → exports this node as backend
   - `<<| Haproxy::Balancermember | listening_service == 'webservers' |>>` → collects exported resources
   - **PuppetDB query**: finds nodes with `Profile::App_server` class in current environment
   - **Iterations**: `$app_servers.each` — runs N times based on query results
     - For each discovered server: creates `haproxy::balancermember` resource

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
- `profile_haproxy::global_maxconn`: `4000` (type: integer)
- `profile_haproxy::client_timeout`: `50000ms` (type: string)
- `profile_haproxy::server_timeout`: `50000ms` (type: string)
- `profile_haproxy::connect_timeout`: `5000ms` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::ssl_ciphers`: `ECDHE+aRSA+AES256+GCM+SHA384` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::backends`: (type: hash)
- `profile_haproxy::extra_packages`: `[]` (type: array)
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)
- `profile_haproxy::discovery_enabled`: `false` (type: boolean)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)

**environment/production.yaml (environment-specific)** → Migration note: Production environment overrides
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::global_maxconn`: `8000` (type: integer)
- `profile_haproxy::log_level`: `warning` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Staging environment overrides
- `profile_haproxy::global_maxconn`: `2000` (type: integer)
- `profile_haproxy::log_level`: `debug` (type: string)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Datacenter-specific server IPs and network configuration
- `profile_haproxy::backends`: (type: hash)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: Cluster-specific backend additions
- `profile_haproxy::backends`: (type: hash)

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Individual host overrides
- `profile_haproxy::backends`: (type: hash)

### Variable Migration Summary

- **Common defaults**: 29 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 3 variables that vary by operating system family
- **Environment-specific variables**: 3 variables that vary by deployment environment (dev, staging, prod)
- **Datacenter-specific variables**: 1 variable for datacenter-specific server IPs
- **Cluster-specific variables**: 1 variable for cluster-specific backend additions
- **Host-specific variables**: 1 variable for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::package_name**: defined at common, os levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common, environment levels, merge strategy: first
- **profile_haproxy::stats_password**: defined at common (both module and environment), merge strategy: first
- **profile_haproxy::backends**: defined at common, datacenter, cluster, node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (deep merge) for backends configuration
- Variables using `first` (default) - First value found wins, no merging for most scalar values

## Custom Types and Providers

**Custom Fact: haproxy_version**
- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Purpose: Executes `haproxy -v` to extract version number using regex
- Linux-only execution
- Parameters: None (system command execution)
- Ansible equivalent: `shell` task with `haproxy -v | grep -oP 'version \K[0-9.]+'`

## Dependencies

**External module dependencies**:
- `puppetlabs-stdlib` (version: 9.7.0)
- `puppetlabs-concat` (version: 9.0.2)
- `puppetlabs-firewall` (version: 8.1.3)

**System package dependencies**:
- `haproxy` (main package)
- `ufw` (firewall management)

**Service dependencies**:
- Install → Config → Service (with notification)
- Config changes notify service restart
- Systemd daemon-reload before service management

## Puppet Facts Used

- `$facts['kernel']`: OS kernel type (Linux detection) - used in role::haproxy
- `$facts['networking']['fqdn']`: Fully qualified domain name - used for exported resources
- `$facts['networking']['ip']`: Primary IP address - used for backend configuration
- `$facts['puppet_environment']`: Puppet environment name - used for PuppetDB queries
- `$facts['os']['family']`: OS family (RedHat/Debian) - used for OS-specific configuration
- `fact('environment')`: Environment detection - used in profile::loadbalancer::haproxy

## Template Conversion Notes

**haproxy.cfg.erb**:
- Variables: 19 total including log_server, global_maxconn, ssl_enabled, stats_password
- Ruby logic: SSL configuration conditional blocks based on ssl_enabled parameter
- Complex expressions: SSL cipher configuration, timeout formatting
- Backend iteration: Loops through backends hash for include statements
- Conditional rendering: Statistics interface configuration based on stats_enabled

**backend.conf.epp**:
- Variables: 10 total including backend_name, balance, port, servers array
- Ruby logic: Health check conditionals, SSL backend options
- Server iteration: Loops through servers array for server definitions
- Weight and health check configuration per server
- SSL backend configuration based on ssl_enabled parameter

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources**:
- `@@haproxy::balancermember[$facts['networking']['fqdn']]` → exports this node as webserver backend, migration notes: requires cross-node data sharing for dynamic backend discovery
- Parameters: listening_service='webservers', server_names=FQDN, ipaddresses=IP, ports='8080', options='check'

**Resource Collectors**:
- `Haproxy::Balancermember <<| listening_service == 'webservers' |>>` → collects all webserver backends, migration notes: requires node discovery for automatic backend registration

**PuppetDB Queries**:
- Query for application servers: finds nodes with `Profile::App_server` class in current environment, migration notes: requires infrastructure data access for dynamic service discovery
- Used to dynamically build API backend pool from discovered servers
- Requires PuppetDB connectivity and proper node classification

**Host Identity Data**:
- Per-host PuppetDB data used for node classification and backend pool membership
- FQDN and IP address data used for cross-node resource sharing

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` (main configuration)
- `/etc/haproxy/conf.d/webservers.cfg` (backend configuration)
- `/etc/haproxy/conf.d/api.cfg` (API backend configuration)
- `/etc/haproxy/errors/503.http` (error pages)
- `/etc/haproxy/errors/408.http` (error pages)
- `/etc/systemd/system/haproxy.service.d/override.conf` (systemd overrides)
- `/etc/logrotate.d/haproxy` (log rotation)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend)
- Port 8404 (statistics interface)
- Backend servers on ports 8080, 3000

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/api.cfg` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# haproxy instance checks
haproxy -f /etc/haproxy/haproxy.cfg -c
curl -I http://localhost:8404/stats

# webservers instance checks
ss -tlnp | grep :8080
curl -I http://localhost/health

# api instance checks  
ss -tlnp | grep :3000
curl -I https://localhost/api/health

# Configuration validation commands
haproxy -f /etc/haproxy/haproxy.cfg -c
nginx -t 2>/dev/null || echo "nginx not configured"

# Network/connectivity checks
ss -tlnp | grep :80
ss -tlnp | grep :443
ss -tlnp | grep :8404
netstat -tlnp | grep haproxy
```