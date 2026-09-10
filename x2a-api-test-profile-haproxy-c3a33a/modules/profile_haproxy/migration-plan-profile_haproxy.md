---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that installs and configures HAProxy with SSL termination, statistics interface, firewall management, service discovery via PuppetDB, and dynamic backend configuration through a 21-level Hiera hierarchy.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 9000 (stats)
  - Key Config: SSL termination, backend pools, health checks
- **webservers backend**: Web application pool
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: 8080 (backend servers)
  - Key Config: roundrobin balancing, 3 servers
- **api backend**: API service pool
  - Location/Path: `/etc/haproxy/conf.d/api.cfg`
  - Port/Socket: 3000 (backend servers)
  - Key Config: leastconn balancing, 2 servers

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
   - Conditional check: if `$facts['kernel'].downcase == 'linux'`
   - Creates `exec 'default'` with command `/bin/true`
   - Contains `::profile::base::base`
   - Contains `::profile::loadbalancer::haproxy`
   - Ordering: `Class['::profile::base::base'] -> Class['::profile::loadbalancer::haproxy']`

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Contains `profile_haproxy`

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from Hiera lookups with deep merge for backends hash
   - Contains `profile_haproxy::install`
   - Contains `profile_haproxy::config`
   - Contains `profile_haproxy::service`
   - Contains `profile_haproxy::firewall`
   - Conditional: if `$discovery_enabled` (false by default)
     - Contains `profile_haproxy::discover`
     - Ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] -> Class['profile_haproxy::discover'] ~> Class['profile_haproxy::service']`
   - Default ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] ~> Class['profile_haproxy::service']`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - Creates `package 'haproxy'` with ensure: `present`
   - Conditional: if `!empty($extra_packages)` (empty array by default)
   - Creates `group 'haproxy'` with ensure: `present`
   - Creates `user 'haproxy'` with ensure: `present`, gid: `haproxy`, shell: `/sbin/nologin`, home: `/var/lib/haproxy`
   - Creates `file '/etc/haproxy'` directory with owner: `root`, group: `root`, mode: `0755`
   - Creates `file '/etc/haproxy/conf.d'` directory with owner: `root`, group: `root`, mode: `0755`
   - Creates `file '/var/lib/haproxy'` directory with owner: `haproxy`, group: `haproxy`, mode: `0755`
   - Conditional: if `$selinux_enabled` (false on Debian, true on RedHat)
     - Creates `exec 'haproxy_selinux_connect'` with command: `/usr/sbin/setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - Creates `file '/etc/haproxy/haproxy.cfg'` using template `haproxy.cfg.erb` with owner: `root`, group: `root`, mode: `0644`
   - Passes 19 variables: log_server=127.0.0.1, log_facility=local0, log_level=info, global_maxconn=4096, user=haproxy, group=haproxy, ssl_enabled=false, ssl_ciphers, connect_timeout=5s, client_timeout=30s, server_timeout=30s, retries=3, stats_enabled=true, stats_port=9000, stats_uri=/haproxy-stats, stats_user=admin, stats_password=test-haproxy-password, backends hash
   - Iterations: `$backends.each` runs 2 times for **webservers** and **api**:
     - **webservers**: Creates `file '/etc/haproxy/conf.d/webservers.cfg'` using template `backend.conf.epp` with backend_name=webservers, balance=roundrobin, port=8080, health_check=httpchk GET /health, health_interval=5s, ssl_enabled=false, servers=[{name: web1, address: 10.0.1.10, weight: 100}, {name: web2, address: 10.0.1.11, weight: 100}, {name: web3, address: 10.0.1.12, weight: 100}]
     - **api**: Creates `file '/etc/haproxy/conf.d/api.cfg'` using template `backend.conf.epp` with backend_name=api, balance=leastconn, port=3000, health_check=httpchk GET /api/health, health_interval=10s, ssl_enabled=false, servers=[{name: api1, address: 10.0.2.10, weight: 100}, {name: api2, address: 10.0.2.11, weight: 100}]
   - Iterations: `['503', '408'].each` runs 2 times for **503** and **408**:
     - **503**: Creates `file '/etc/haproxy/errors/503.http'` with static error page content
     - **408**: Creates `file '/etc/haproxy/errors/408.http'` with static error page content
   - Creates `file '/etc/haproxy/errors'` directory with owner: `root`, group: `root`, mode: `0755`
   - Conditional: if `$stick_table_enabled` (false by default)
     - Creates `file '/etc/haproxy/conf.d/stick-tables.cfg'` with stick table configuration

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - Creates `file '/etc/systemd/system/haproxy.service.d'` directory with owner: `root`, group: `root`, mode: `0755`
   - Creates `file '/etc/systemd/system/haproxy.service.d/override.conf'` with systemd service overrides
   - Creates `exec 'haproxy_systemd_reload'` with command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - Creates `service 'haproxy'` with ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - Creates `exec 'haproxy_config_check'` with command: `/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - Creates `file '/etc/logrotate.d/haproxy'` with log rotation configuration
   - Notifies: `file[override.conf] ~> exec[haproxy_systemd_reload] ~> service[haproxy]`
   - Notifies: `file[haproxy.cfg] ~> exec[haproxy_config_check] ~> service[haproxy]`

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Case statement on `$firewall_provider` (none by default):
     - **firewalld**: Creates `exec 'firewalld_reload'` with command: `/bin/firewall-cmd --reload`
     - **ufw**: Creates `package 'ufw'` with ensure: `present`, creates `exec 'ufw_allow_http'` with command: `/usr/sbin/ufw allow 80/tcp`, creates `exec 'ufw_allow_https'` with command: `/usr/sbin/ufw allow 443/tcp`, creates `exec 'ufw_enable'` with command: `/usr/sbin/ufw --force enable`
     - **none**: Creates no firewall resources
     - **default**: Creates `notify 'Unknown firewall provider: none'`

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — only if `$discovery_enabled` is true:
   - Creates `@@haproxy::balancermember 'lb01.fra.example.com'` with listening_service: `webservers`, server_names: `lb01.fra.example.com`, ipaddresses: `10.0.1.100`, ports: `8080`, options: `check`
   - Collects `<<| Haproxy::Balancermember <| listening_service == 'webservers' |>`
   - Iterations: `$app_servers.each` runs based on PuppetDB query results for discovered app servers
   - Creates `haproxy::balancermember` resources for each discovered app server

## Variables

**Variable Flow Summary**: 29 variables across 9 Hiera levels

### Variable Definitions

**site-modules/profile_haproxy/data/common.yaml (module defaults)** → Migration note: Base module configuration for all nodes
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
- `profile_haproxy::stats_password`: `ENC[PKCS7,...]` (type: string, encrypted)
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

**data/common.yaml (environment defaults)** → Migration note: Environment-wide defaults for all nodes
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::stats_password`: `test-haproxy-password` (type: string, plaintext)
- `profile_haproxy::firewall_provider`: `none` (type: string)
- `profile_haproxy::extra_packages`: `[]` (type: array)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

**site-modules/profile_haproxy/data/os/Debian.yaml (OS-specific)** → Migration note: Debian/Ubuntu-specific configuration
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `[hatop]` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**site-modules/profile_haproxy/data/os/RedHat.yaml (OS-specific)** → Migration note: RedHat/CentOS-specific configuration
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::firewall_zone`: `public` (type: string)
- `profile_haproxy::extra_packages`: `[haproxy-systemd-wrapper, policycoreutils-python-utils]` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

### Variable Migration Summary

- **Common defaults**: 25 variables from module common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family (Debian vs RedHat)
- **Environment-specific variables**: 7 variables that vary by deployment environment (dev, staging, prod)
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::package_name**: defined at module/environment/os levels, merge strategy: first
- **profile_haproxy::stats_password**: defined at module/environment levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at module/environment levels, merge strategy: first
- **profile_haproxy::backends**: defined at module/datacenter/cluster/node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `deep` merge - Hash values are recursively merged (deep merge) for backends configuration
- Variables using `first` (default) - First value found wins, no merging for most scalar values

## Custom Types and Providers

**Custom Fact: haproxy_version**
- **File**: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- **Purpose**: Executes `haproxy -v` to extract version number for compatibility checks
- **Platform**: Linux only
- **Returns**: HAProxy version string (e.g., "2.4.18")

## Dependencies

**External module dependencies**:
- `puppetlabs-stdlib` (version: 9.7.0)
- `puppetlabs-concat` (version: 9.0.2)
- `puppetlabs-firewall` (version: 8.1.3)

**System package dependencies**:
- `haproxy` (main package)
- `hatop` (Debian monitoring tool)
- `haproxy-systemd-wrapper` (RedHat systemd integration)
- `policycoreutils-python-utils` (RedHat SELinux tools)
- `ufw` (Debian firewall)

**Service dependencies**:
- Install → Config → Service (standard ordering)
- Config changes notify service restart
- Discovery (if enabled) runs after config, before service

## Puppet Facts Used

- `$facts['kernel']`: Operating system kernel (Linux detection for conditional execution)
- `$facts['networking']['fqdn']`: Fully qualified domain name (service discovery and exported resources)
- `$facts['networking']['ip']`: Primary IP address (service discovery and backend member registration)
- `$facts['puppet_environment']`: Puppet environment name (service discovery scope)
- `$facts['os']['family']`: OS family (Debian/RedHat configuration branching)

## Template Conversion Notes

**haproxy.cfg.erb**:
- **Variables**: 19 variables including SSL configuration, timeouts, stats settings, backends hash
- **Ruby logic blocks**: SSL conditional rendering for certificate paths and cipher configuration
- **Conditional rendering**: Stats page section conditional on `stats_enabled` variable
- **Complex expressions**: Backend loop references for configuration file includes

**backend.conf.epp**:
- **Variables**: 10 variables for backend configuration (name, balance method, port, health checks, servers array)
- **Ruby logic blocks**: Health check conditional rendering and SSL backend options
- **Iterations**: Server array loop with weight and SSL options for each backend server
- **Complex expressions**: Dynamic server configuration based on SSL enablement

## PuppetDB Dependencies

**Context**: PuppetDB provides centralized data store for cross-node resource sharing and service discovery. This module uses PuppetDB for dynamic backend member registration and collection.

**Exported Resources** (`@@`):
- **Resource type**: `haproxy::balancermember`
- **What it exports**: Load balancer member registration with FQDN, IP address, port 8080, and health check options
- **Who collects it**: Other HAProxy instances in the same environment
- **Migration notes**: Cross-node data sharing for load balancer pool membership requires centralized inventory system

**Resource Collectors** (`<<| |>`):
- **What is collected**: `Haproxy::Balancermember` resources with `listening_service == 'webservers'`
- **Filter condition**: Matches webservers backend pool members only
- **Migration notes**: Node discovery requires inventory system to identify backend pool members

**PuppetDB Queries**:
- **Query**: Discovers nodes with `Profile::App_server` class in same environment
- **Returned data**: Node FQDN, IP addresses, and service ports for dynamic backend configuration
- **Migration notes**: Infrastructure data access requires inventory system integration for service discovery

**Host Identity Data**:
- **Per-host PuppetDB data**: FQDN, IP address, environment, and class assignments
- **Usage**: Node classification for backend pool membership and service discovery scope

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg` (main configuration)
- `/etc/haproxy/conf.d/webservers.cfg` (webservers backend)
- `/etc/haproxy/conf.d/api.cfg` (api backend)
- `/etc/haproxy/errors/503.http` (error page)
- `/etc/haproxy/errors/408.http` (error page)
- `/etc/systemd/system/haproxy.service.d/override.conf` (systemd overrides)
- `/etc/logrotate.d/haproxy` (log rotation)

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 9000 (statistics interface)
- Backend servers on ports 8080 and 3000

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/api.cfg` (1 render)

## Pre-flight checks:
```bash
# Service status checks
systemctl status haproxy
systemctl is-enabled haproxy

# Configuration validation
haproxy -f /etc/haproxy/haproxy.cfg -c

# HAProxy instance checks
curl -I http://localhost:9000/haproxy-stats
curl -I http://localhost/health

# Webservers backend checks
curl -I http://10.0.1.10:8080/health
curl -I http://10.0.1.11:8080/health
curl -I http://10.0.1.12:8080/health

# API backend checks
curl -I http://10.0.2.10:3000/api/health
curl -I http://10.0.2.11:3000/api/health

# Network connectivity checks
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :9000

# Log file checks
tail -f /var/log/haproxy.log
journalctl -u haproxy -f
```