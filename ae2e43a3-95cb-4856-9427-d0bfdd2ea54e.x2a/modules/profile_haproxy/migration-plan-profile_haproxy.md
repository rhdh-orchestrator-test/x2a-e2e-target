---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that configures a high-availability reverse proxy with SSL termination, statistics interface, firewall rules, and dynamic backend discovery via PuppetDB. Supports multiple backends, stick tables for session persistence, and environment-specific configuration across 21 Hiera hierarchy levels.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 8405 (stats)
  - Key Config: SSL termination, session persistence, health checks
- **webservers**: Primary backend pool
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: Backend servers on port 8080
  - Key Config: Round-robin load balancing, health checks
- **monitoring**: Monitoring backend pool (cluster-specific)
  - Location/Path: `/etc/haproxy/conf.d/monitoring.cfg`
  - Port/Socket: Backend servers on port 9090
  - Key Config: First-available load balancing

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
│   ├── datacenter/
│   │   └── dc1_fra.yaml
│   ├── environment/
│   │   ├── production.yaml
│   │   └── staging.yaml
│   ├── cluster/
│   │   └── haproxy_prod_fra.yaml
│   └── nodes/
│       └── lb01.fra.example.com.yaml
└── lib/
    └── facter/
        └── haproxy_version.rb

site-modules/profile/manifests/loadbalancer/
└── haproxy.pp

site-modules/role/manifests/
└── app_server.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes the main profile
   - `include profile::loadbalancer::haproxy`

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Wrapper class for the main HAProxy profile
   - `contain profile_haproxy`

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from 21-level Hiera hierarchy
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - **Conditional**: if discovery_enabled=true (when app servers detected)
     - `contain profile_haproxy::discover`
     - Sets ordering: `profile_haproxy::install -> profile_haproxy::config -> profile_haproxy::discover ~> profile_haproxy::service`
   - **Default ordering**: `profile_haproxy::install -> profile_haproxy::config ~> profile_haproxy::service`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - **Conditional**: if extra_packages=['haproxy-stats', 'rsyslog'] (RedHat) or ['haproxy', 'rsyslog'] (Debian)
     - `package 'haproxy-stats'` → ensure: `present` (RedHat only)
     - `package 'rsyslog'` → ensure: `present`
   - `group 'haproxy'` → gid: `188`
   - `user 'haproxy'` → uid: `188`, home: `/var/lib/haproxy`, shell: `/sbin/nologin`
   - `file '/etc/haproxy'` → owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → owner: `haproxy`, group: `haproxy`, mode: `0755`
   - **Conditional**: if selinux_enabled=true (RedHat only)
     - `exec 'haproxy_selinux_connect'` → command: `/usr/sbin/setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → mode: `0644`, owner: `root`, group: `root`
     - Passes: log_server='10.1.1.100', log_facility='local0', log_level='info', global_maxconn=100000, user='haproxy', group='haproxy', ssl_enabled=true, ssl_ciphers='ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!SHA1:!AESCCM', ssl_min_version='TLSv1.3', connect_timeout='5s', client_timeout='50s', server_timeout='50s', retries=3, stats_enabled=true, stats_port=8405, stats_uri='/stats', stats_user='admin', stats_password='admin123', backends hash
   - **Iterations**: backends.each — runs 2 times for: **webservers**, **monitoring**
     - **webservers**:
       - `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`) → mode: `0644`
         - Passes: backend_name='webservers', balance='roundrobin', port=8080, servers=[{name: 'web02', address: '10.1.1.11', weight: 150}], health_check='httpchk', health_interval='10s', ssl_enabled=false
     - **monitoring**:
       - `file '/etc/haproxy/conf.d/monitoring.cfg'` (template `backend.conf.epp`) → mode: `0644`
         - Passes: backend_name='monitoring', balance='first', port=9090, servers=[{name: 'mon01', address: '10.1.1.20', weight: 100}], health_check='httpchk', health_interval='10s', ssl_enabled=false
   - **Iterations**: ['503', '408'].each — runs 2 times for: **503**, **408**
     - **503**:
       - `file '/etc/haproxy/errors/503.http'` → content: HTTP error page, mode: `0644`
     - **408**:
       - `file '/etc/haproxy/errors/408.http'` → content: HTTP error page, mode: `0644`
   - `file '/etc/haproxy/errors'` → owner: `root`, group: `root`, mode: `0755`
   - **Conditional**: if stick_table_enabled=true (production only)
     - `file '/etc/haproxy/conf.d/stick-tables.cfg'` → content: stick table configuration, mode: `0644`

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → content: systemd overrides, mode: `0644`
   - `exec 'haproxy_systemd_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → content: log rotation config, mode: `0644`

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - **Conditional**: case firewall_provider
     - **Branch 'none'**: No firewall resources (environment override)
     - **Branch 'firewalld'** (RedHat):
       - `firewalld_port '80/tcp'` → ensure: `present`, zone: `public`
       - `firewalld_port '443/tcp'` → ensure: `present`, zone: `public`
       - `firewalld_port '8405/tcp'` → ensure: `present`, zone: `public`
     - **Branch 'ufw'** (Debian):
       - `ufw::allow 'haproxy-http'` → port: `80`, proto: `tcp`
       - `ufw::allow 'haproxy-https'` → port: `443`, proto: `tcp`
       - `ufw::allow 'haproxy-stats'` → port: `8405`, proto: `tcp`

8. **profile_haproxy::discover** (when discovery_enabled=true):
   - Exports `@@haproxy::balancermember` with fqdn='lb01.fra.example.com', ip='10.1.1.5', port='8080'
   - Collects `Haproxy::Balancermember <<| listening_service == 'webservers' |>>`
   - **Iterations**: app_servers.each — runs for dynamically discovered application servers
     - Creates backend server entries for each discovered app server with Profile::App_server and Profile::Base classes

## Variables

**Variable Flow Summary**: 29 variables across 8 Hiera levels

### Variable Definitions

**common.yaml (module-level defaults)** → Migration note: Base defaults for all nodes
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
- `profile_haproxy::stats_password`: `ENC[PKCS7,encrypted_password]` (type: string)
- `profile_haproxy::global_maxconn`: `4000` (type: integer)
- `profile_haproxy::client_timeout`: `30s` (type: string)
- `profile_haproxy::server_timeout`: `30s` (type: string)
- `profile_haproxy::connect_timeout`: `5s` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:DHE+AESGCM:!aNULL:!SHA1` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::backends`: `{}` (type: hash)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::firewall_zone`: `public` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-stats', 'rsyslog']` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy', 'rsyslog']` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Datacenter-specific variables for Frankfurt DC1
- `profile_haproxy::log_server`: `10.1.1.100` (type: string)
- `profile_haproxy::ntp_servers`: `['10.1.1.1', '10.1.1.2']` (type: array)
- `profile_haproxy::backends`: (type: hash)
  - `webservers`: `{balance: 'roundrobin', port: 8080, servers: [{name: 'web01', address: '10.1.1.10', weight: 100}]}`

**environment/production.yaml (environment-specific)** → Migration note: Production environment overrides
- `profile_haproxy::global_maxconn`: `50000` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::client_timeout`: `50s` (type: string)
- `profile_haproxy::server_timeout`: `50s` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `100k` (type: string)
- `profile_haproxy::stick_table_expire`: `30m` (type: string)
- `profile_haproxy::firewall_provider`: `none` (type: string)
- `profile_haproxy::stats_password`: `admin123` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Staging environment overrides
- `profile_haproxy::global_maxconn`: `1000` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: Cluster-specific overrides for production Frankfurt HAProxy cluster
- `profile_haproxy::global_maxconn`: `100000` (type: integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!SHA1:!AESCCM` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (type: string)
- `profile_haproxy::backends`: (type: hash)
  - `monitoring`: `{balance: 'first', port: 9090, servers: [{name: 'mon01', address: '10.1.1.20', weight: 100}]}`

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Host-specific overrides for individual load balancer
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_port`: `8405` (type: integer)
- `profile_haproxy::backends`: (type: hash)
  - `webservers`: `{servers: [{name: 'web02', address: '10.1.1.11', weight: 150}]}`

### Variable Migration Summary

- **Common defaults**: 25 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family (RedHat vs Debian)
- **Environment-specific variables**: 9 variables that vary by deployment environment (production vs staging)
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::stats_password**: defined at environment, module levels, merge strategy: first
- **profile_haproxy::firewall_provider**: defined at environment, OS levels, merge strategy: first
- **profile_haproxy::backends**: defined at datacenter, cluster, node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (backends configuration)
- Variables using `first` (default) - First value found wins, no merging (most scalar values)

## Custom Types and Providers

**Custom Fact: haproxy_version**
- **File**: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- **Purpose**: Executes `haproxy -v` to extract version number using regex
- **Parameters**: None (auto-executed)
- **Returns**: HAProxy version string
- **Migration**: Replace with `ansible.builtin.package_facts` or `ansible.builtin.shell` task

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.7.0)
- puppetlabs-concat (version: 9.0.2)
- puppetlabs-firewall (version: 8.1.3)

**System package dependencies**:
- haproxy (main package)
- haproxy-stats (RedHat only)
- rsyslog (logging)

**Service dependencies**:
- install → config → service (notify chain)
- install → config → discover → service (when discovery enabled)

## Puppet Facts Used

- `$facts['networking']['fqdn']`: Fully qualified domain name for server registration in PuppetDB exports
- `$facts['networking']['ip']`: IP address for backend server configuration
- `$facts['puppet_environment']`: Environment name for PuppetDB queries to filter application servers
- `$facts['os']['family']`: OS family for package/config selection (RedHat vs Debian)
- `$facts['architecture']`: CPU architecture for package selection

## Template Conversion Notes

**haproxy.cfg.erb**:
- **Variables**: 19 variables including log_server, global_maxconn, ssl settings, timeouts, stats configuration
- **Ruby logic blocks**: SSL conditional block for cipher configuration and HTTPS redirect rules, backend iteration with include statements
- **Conditional rendering**: SSL certificate paths and cipher suites only rendered when ssl_enabled=true
- **Iterations**: backends.each loop for including backend configuration files from conf.d directory

**backend.conf.epp**:
- **Variables**: 10 variables including backend_name, balance method, port, servers array, health check settings
- **Ruby logic blocks**: Conditional health check configuration and SSL backend options
- **Conditional rendering**: Health check options only rendered when health_check is defined
- **Iterations**: servers.each loop for individual server definitions with weight and SSL settings

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources**:
- `@@haproxy::balancermember` exports current node as webserver backend (listening_service: 'webservers', port: '8080') - Migration notes: Cross-node data sharing pattern for dynamic load balancer member registration

**Resource Collectors**:
- `Haproxy::Balancermember <<| listening_service == 'webservers' |>>` collects all webserver backends - Migration notes: Node discovery requirements for automatic backend pool population

**PuppetDB Queries**:
- Query for application servers in current environment with Profile::App_server and Profile::Base classes - Migration notes: Infrastructure data access patterns for dynamic service discovery
- Results used to dynamically build API backend server list and populate $app_servers variable

**Host Identity Data**:
- Per-host PuppetDB data includes FQDN, IP address, and class assignments used for node classification and backend server registration

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` (main configuration)
- `/etc/haproxy/conf.d/webservers.cfg` (webservers backend configuration)
- `/etc/haproxy/conf.d/monitoring.cfg` (monitoring backend configuration)
- `/etc/haproxy/conf.d/stick-tables.cfg` (session persistence configuration)
- `/etc/haproxy/errors/503.http` (service unavailable error page)
- `/etc/haproxy/errors/408.http` (request timeout error page)
- `/etc/systemd/system/haproxy.service.d/override.conf` (systemd overrides)
- `/etc/logrotate.d/haproxy` (log rotation configuration)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 8405 (statistics interface)
- Backend webservers on port 8080
- Backend monitoring on port 9090

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/monitoring.cfg` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# haproxy instance checks
haproxy -f /etc/haproxy/haproxy.cfg -c
curl -I http://localhost:8405/stats
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :8405

# webservers backend checks
curl -I http://10.1.1.11:8080/health
telnet 10.1.1.11 8080

# monitoring backend checks
curl -I http://10.1.1.20:9090/health
telnet 10.1.1.20 9090

# Configuration validation commands
haproxy -f /etc/haproxy/haproxy.cfg -c -V
ls -la /etc/haproxy/conf.d/
cat /etc/haproxy/errors/503.http

# Network/connectivity checks
ping 10.1.1.11
ping 10.1.1.20
ss -tlnp | grep haproxy
```