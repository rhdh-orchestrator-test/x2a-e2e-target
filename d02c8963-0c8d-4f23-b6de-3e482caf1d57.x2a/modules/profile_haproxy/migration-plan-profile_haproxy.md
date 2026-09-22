---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that installs and configures HAProxy with SSL termination, statistics interface, firewall management, and dynamic backend discovery via PuppetDB. Supports multiple environments with different performance profiles and can discover backend servers automatically or use static configuration.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 8404 (stats)
  - Key Config: SSL termination, backend discovery, health checks
- **webservers**: Primary backend pool
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: Backend servers on port 8080
  - Key Config: Round-robin load balancing, health checks
- **monitoring**: Secondary backend pool (cluster-specific)
  - Location/Path: `/etc/haproxy/conf.d/monitoring.cfg`
  - Port/Socket: Backend servers on port 9090
  - Key Config: Source-based load balancing

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
│   ├── environment/
│   │   ├── production.yaml
│   │   └── staging.yaml
│   ├── datacenter/
│   │   └── dc1_fra.yaml
│   ├── cluster/
│   │   └── haproxy_prod_fra.yaml
│   ├── os/
│   │   ├── RedHat.yaml
│   │   └── Debian.yaml
│   └── nodes/
│       └── lb01.fra.example.com.yaml
└── lib/
    └── facter/
        └── haproxy_version.rb

site-modules/profile/manifests/loadbalancer/
└── haproxy.pp

site-modules/role/manifests/
└── haproxy.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::haproxy** (`site-modules/role/manifests/haproxy.pp`):
   - Conditional check: if `$facts['kernel'].downcase == 'linux'`
   - `contain profile::loadbalancer::haproxy`

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - `contain profile_haproxy`

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from Hiera lookup with 21-level hierarchy
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - Conditional: if discovery_enabled=true: `contain profile_haproxy::discover`
   - Sets ordering: `profile_haproxy::install -> profile_haproxy::config ~> profile_haproxy::service`
   - Sets ordering with discovery: `profile_haproxy::install -> profile_haproxy::config -> profile_haproxy::discover ~> profile_haproxy::service`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - Conditional if extra_packages defined:
     - `package 'haproxy-systemd-wrapper'` → ensure: `present` (RedHat only)
     - `package 'rsyslog'` → ensure: `present` (RedHat only)
     - `package 'hatop'` → ensure: `present` (Debian only)
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, shell: `/sbin/nologin`, home: `/var/lib/haproxy`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - Conditional if selinux_enabled=true (RedHat):
     - `exec 'haproxy_selinux_connect'` → command: `/usr/sbin/setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
   - `file '/etc/haproxy/errors'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - Iterations: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: HTTP error page
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: HTTP error page
   - Iterations: `$backends.each` — runs 2 times for: **webservers**, **monitoring**
     - **webservers**: `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`)
     - **monitoring**: `file '/etc/haproxy/conf.d/monitoring.cfg'` (template `backend.conf.epp`)
   - Conditional if stick_table_enabled=true (production):
     - `file '/etc/haproxy/conf.d/stick-tables.cfg'` → content: stick table configuration

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → content: systemd override configuration
   - `exec 'haproxy_systemd_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → content: log rotation configuration

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Conditional case firewall_provider:
     - **firewalld** (RedHat): `exec 'firewalld_reload'` → command: `/bin/firewall-cmd --reload`
     - **ufw** (Debian):
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `/usr/sbin/ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `/usr/sbin/ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `/usr/sbin/ufw --force enable`

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — conditional if discovery_enabled=true:
   - `@@haproxy::balancermember 'lb01.fra.example.com'` → listening_service: `webservers`, server_names: `lb01.fra.example.com`, ipaddresses: `10.1.1.5`, ports: `8080`, options: `check`
   - `<<| Haproxy::Balancermember | listening_service == 'webservers' |>>`
   - Iterations: `$app_servers.each` from PuppetDB query — variable count based on environment
     - Creates `haproxy::balancermember "api-${certname}"` for each discovered server

## Variables

**Variable Flow Summary**: 29 variables across 8 Hiera levels

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
- `profile_haproxy::stats_password`: `ENC[PKCS7,encrypted_password]` (type: string)
- `profile_haproxy::global_maxconn`: `4000` (type: integer)
- `profile_haproxy::client_timeout`: `50000ms` (type: string)
- `profile_haproxy::server_timeout`: `50000ms` (type: string)
- `profile_haproxy::connect_timeout`: `5000ms` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!SHA1:!AESCCM` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::backends`: (type: hash)

**environment/production.yaml (environment-specific)** → Migration note: Production performance tuning and security settings
- `profile_haproxy::global_maxconn`: `8000` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `notice` (type: string)
- `profile_haproxy::client_timeout`: `60000ms` (type: string)
- `profile_haproxy::server_timeout`: `60000ms` (type: string)
- `profile_haproxy::stats_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `100k` (type: string)
- `profile_haproxy::stick_table_expire`: `30m` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Staging debugging and testing configuration
- `profile_haproxy::global_maxconn`: `2000` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Frankfurt datacenter-specific settings
- `profile_haproxy::log_server`: `10.1.1.100` (type: string)
- `profile_haproxy::backends`: (type: hash)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: High-performance production cluster settings
- `profile_haproxy::global_maxconn`: `12000` (type: integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+CHACHA20:!aNULL:!SHA1` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (type: string)
- `profile_haproxy::backends`: (type: hash)

**os/RedHat.yaml (OS-specific)** → Migration note: RedHat/CentOS-specific packages and firewall
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::firewall_zone`: `public` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-systemd-wrapper', 'rsyslog']` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

**os/Debian.yaml (OS-specific)** → Migration note: Debian/Ubuntu-specific packages and firewall
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `['hatop']` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Individual host customizations
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_port`: `8405` (type: integer)
- `profile_haproxy::backends`: (type: hash)

### Variable Migration Summary

- **Common defaults**: 24 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 4 variables that vary by operating system family
- **Environment-specific variables**: 9 variables that vary by deployment environment (dev, staging, prod)
- **Datacenter-specific variables**: 2 variables for datacenter-specific settings
- **Cluster-specific variables**: 4 variables for high-performance cluster configurations
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::global_maxconn**: defined at common, environment, and cluster levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common and environment levels, merge strategy: first
- **profile_haproxy::stats_enabled**: defined at common, environment, and node levels, merge strategy: first
- **profile_haproxy::backends**: defined at common, datacenter, cluster, and node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (deep merge) for backends configuration
- Variables using `first` (default) - First value found wins, no merging for most scalar values

## Custom Types and Providers

**Custom Fact: haproxy_version**
- **File**: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- **Purpose**: Executes `haproxy -v` to extract version number using regex
- **Returns**: HAProxy version string for compatibility checks

## Dependencies

**External module dependencies**:
- `puppetlabs-stdlib` (version: 9.7.0) - for standard library functions
- `puppetlabs-concat` (version: 9.0.2) - for file concatenation
- `puppetlabs-firewall` (version: 8.1.3) - for firewall management

**System package dependencies**:
- `haproxy` - main load balancer package
- `haproxy-systemd-wrapper` (RedHat) - systemd integration
- `rsyslog` (RedHat) - logging support
- `hatop` (Debian) - monitoring tool
- `ufw` (Debian) - firewall management

**Service dependencies**:
- install → config → service (standard pattern)
- config changes notify service restart
- discovery (when enabled) runs between config and service

## Puppet Facts Used

- `$facts['kernel']` - OS kernel type for Linux detection in role class
- `$facts['networking']['fqdn']` - fully qualified domain name for service discovery
- `$facts['networking']['ip']` - IP address for load balancer member registration
- `$facts['puppet_environment']` - environment name for PuppetDB queries
- `$facts['os']['family']` - OS family (RedHat/Debian) for package selection

## Template Conversion Notes

**haproxy.cfg.erb**:
- **Variables used**: log_server, log_facility, log_level, global_maxconn, user, group, ssl_enabled, ssl_ciphers, ssl_min_version, connect_timeout, client_timeout, server_timeout, retries, stats_enabled, stats_port, stats_uri, stats_user, stats_password
- **Ruby logic blocks**: Conditional SSL configuration block, conditional stats interface block
- **Complex expressions**: SSL cipher suite configuration, backend section placeholder

**backend.conf.epp**:
- **Variables used**: backend_name, balance, port, servers, health_check, health_interval, ssl_enabled
- **Conditional rendering**: Health check configuration, SSL verification options
- **Iterations**: Server list iteration with weight and address configuration

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. This module uses PuppetDB for dynamic backend server discovery.

**Exported Resources**:
- `@@haproxy::balancermember` - exports current node as load balancer member with listening_service 'webservers', FQDN, IP address, port 8080, and health check options
- Migration notes: Requires cross-node data sharing for dynamic load balancer member registration

**Resource Collectors**:
- `<<| Haproxy::Balancermember | listening_service == 'webservers' |>>` - collects all exported balancer members for webservers service
- Migration notes: Requires node discovery mechanism to find all registered backend servers

**PuppetDB Queries**:
- Query to find all application servers in current environment with 'Profile::App_server' class
- Returns node list used for dynamic backend server configuration
- Migration notes: Requires infrastructure data access for environment-based server discovery

**Host Identity Data**:
- Uses `$facts['networking']['fqdn']` and `$facts['networking']['ip']` for node identification in PuppetDB
- Migration notes: Node classification depends on network identity data for proper service registration

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg`
- `/etc/haproxy/conf.d/webservers.cfg`
- `/etc/haproxy/conf.d/monitoring.cfg`
- `/etc/haproxy/errors/503.http`
- `/etc/haproxy/errors/408.http`
- `/etc/systemd/system/haproxy.service.d/override.conf`
- `/etc/logrotate.d/haproxy`
- `/etc/haproxy/conf.d/stick-tables.cfg` (production only)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 8404 (statistics interface, default)
- Port 8405 (statistics interface, lb01.fra.example.com)
- Backend servers on port 8080 (webservers)
- Backend servers on port 9090 (monitoring)

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/monitoring.cfg` (1 render, cluster-specific)

## Pre-flight checks:

```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# Configuration validation
/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -c

# haproxy instance checks
curl -I http://localhost:80/
curl -I https://localhost:443/ # if SSL enabled
curl http://localhost:8404/stats # if stats enabled
curl http://localhost:8405/stats # for lb01.fra.example.com

# webservers backend checks
curl -I http://10.1.1.10:8080/
curl -I http://10.1.1.11:8080/

# monitoring backend checks (cluster-specific)
curl -I http://10.1.1.50:9090/

# Firewall verification
firewall-cmd --list-all # RedHat
ufw status # Debian

# SSL certificate verification (if SSL enabled)
test -f /etc/ssl/certs/haproxy.pem
test -f /etc/ssl/private/haproxy.key

# Log file verification
test -f /var/log/haproxy.log
tail -n 10 /var/log/haproxy.log
```