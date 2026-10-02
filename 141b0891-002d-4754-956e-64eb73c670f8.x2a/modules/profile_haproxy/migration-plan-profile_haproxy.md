---
source-path: site-modules/profile_haproxy
---

# Migration Plan: role_haproxy

**TLDR**: HAProxy load balancer role that installs and configures HAProxy with SSL termination, statistics interface, firewall rules, and service discovery via PuppetDB. Manages multiple backend pools with health checks and supports dynamic server registration through exported resources. Includes base system utilities and services.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: /etc/haproxy/haproxy.cfg
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 9000 (stats)
  - Key Config: SSL termination, backend pools, health checks
- **webservers**: Backend pool for web servers
  - Location/Path: /etc/haproxy/conf.d/webservers.cfg
  - Port/Socket: 8080
  - Key Config: 3 servers with round-robin balancing
- **api**: Backend pool for API servers
  - Location/Path: /etc/haproxy/conf.d/api.cfg
  - Port/Socket: 3000
  - Key Config: 2 servers with least-connection balancing

## File Structure

```
site-modules/role/manifests/haproxy.pp
site-modules/profile/manifests/base/base.pp
site-modules/profile/manifests/loadbalancer/haproxy.pp
site-modules/profile_haproxy/manifests/init.pp
site-modules/profile_haproxy/manifests/install.pp
site-modules/profile_haproxy/manifests/config.pp
site-modules/profile_haproxy/manifests/service.pp
site-modules/profile_haproxy/manifests/firewall.pp
site-modules/profile_haproxy/manifests/discover.pp
site-modules/base_utils/manifests/init.pp
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
```

## Module Explanation

The module performs operations in this order:

1. **role::haproxy** (`site-modules/role/manifests/haproxy.pp`):
   - Entry point class that orchestrates the complete HAProxy deployment
   - `include profile::base::base`
   - `include profile::loadbalancer::haproxy`
   - Conditional logic based on `$facts['kernel']` for Linux systems

2. **profile::base::base** (`site-modules/profile/manifests/base/base.pp`):
   - Base system configuration and utilities
   - `include base_utils`
   - Conditional package management for system utilities
   - NTP/chrony service management based on OS
   - Syslog/rsyslog service configuration
   - MOTD file management

3. **base_utils** (`site-modules/base_utils/manifests/init.pp`):
   - System utility packages and basic configuration
   - Package installations for common tools
   - Basic system hardening settings

4. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Load balancer profile wrapper
   - `include profile_haproxy`
   - Sets load balancer specific parameters

5. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from Hiera lookup with 21-level hierarchy
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - Conditional: if discovery_enabled=true
     - `contain profile_haproxy::discover`
     - Sets ordering: `profile_haproxy::install -> profile_haproxy::config -> profile_haproxy::discover ~> profile_haproxy::service`
   - Default ordering: `profile_haproxy::install -> profile_haproxy::config ~> profile_haproxy::service`

6. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - Conditional: if extra_packages not empty (default: empty)
     - Loop runs 0 times with default configuration
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, home: `/var/lib/haproxy`, shell: `/sbin/nologin`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - Conditional: if selinux_enabled (fact-based)
     - `exec 'haproxy_selinux_connect'` → command: `setsebool -P haproxy_connect_any 1`

7. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
   - Iterations: `$backends.each` — runs 2 times for: **webservers**, **api**
     - **webservers**: `file '/etc/haproxy/conf.d/webservers.cfg'` (template `backend.conf.epp`) → mode: `0644`
     - **api**: `file '/etc/haproxy/conf.d/api.cfg'` (template `backend.conf.epp`) → mode: `0644`
   - Iterations: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**: `file '/etc/haproxy/errors/503.http'` → content: HTTP error page
     - **408**: `file '/etc/haproxy/errors/408.http'` → content: HTTP error page
   - `file '/etc/haproxy/errors'` → ensure: `directory`, mode: `0755`
   - Conditional: if stick_table_enabled=false (default)
     - Does not run

8. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → content: systemd override, mode: `0644`
   - `exec 'haproxy_systemd_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → content: logrotate config, mode: `0644`

9. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Conditional: case firewall_provider
     - **firewalld** (default): `exec 'firewalld_reload'` → command: `firewall-cmd --reload`
     - **ufw**: Package installation and rule configuration
     - **none**: Firewall management disabled
     - **default**: Warning notification

10. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — Conditional: if discovery_enabled=true
    - `@@haproxy::balancermember 'hostname.example.com'` → listening_service: `webservers`
    - `<<| Haproxy::Balancermember <| listening_service == 'webservers' |> |>>` → collects exported resources
    - Iterations: `$app_servers.each` from PuppetDB query — variable count depends on query results
    - PuppetDB queries: Searches for nodes with `Profile::App_server` class in same environment

## Variables

**Variable Flow Summary**: 25+ variables across 9 Hiera levels

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
- `profile_haproxy::stats_password`: `[ENCRYPTED]` (type: string)
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
- `profile_haproxy::backends`: (type: hash)
- `profile_haproxy::discovery_enabled`: `false` (type: boolean)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::user`: `haproxy` (type: string)
- `profile_haproxy::group`: `haproxy` (type: string)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::config_file`: `/etc/haproxy/haproxy.cfg` (type: string)
- `profile_haproxy::user`: `haproxy` (type: string)
- `profile_haproxy::group`: `haproxy` (type: string)

**environment/production.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_password`: `[ENCRYPTED]` (type: string)
- `profile_haproxy::global_maxconn`: `8192` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs/haproxy.pem` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private/haproxy.key` (type: string)
- `profile_haproxy::backends`: (type: hash)

**environment/staging.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::global_maxconn`: `2048` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)
- `profile_haproxy::backends`: (type: hash)

### Variable Migration Summary

- **Common defaults**: 25 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 12 variables that vary by deployment environment (dev, staging, prod)
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::package_name**: defined at common, os levels, merge strategy: first
- **profile_haproxy::stats_password**: defined at common, environment levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common, environment levels, merge strategy: first
- **profile_haproxy::backends**: defined at common, environment, datacenter, cluster, node levels, merge strategy: deep

### Merge Strategy Notes

- Variables using `hash` merge - Hash values from multiple levels are merged (shallow merge)
- Variables using `deep` merge - Hash values are recursively merged (deep merge)
- Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Custom Fact**: haproxy_version
- **File**: site-modules/profile_haproxy/lib/facter/haproxy_version.rb
- **Purpose**: Executes `haproxy -v` command to extract version number using regex pattern
- **Platform**: Only runs on Linux systems
- **Parameters**: None (fact collection)

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.7.0)
- puppetlabs-concat (version: 9.0.2)
- puppetlabs-firewall (version: 8.1.3)

**System package dependencies**:
- haproxy (main package)
- ufw (conditional, for Ubuntu firewall)

**Service dependencies**:
- install → config → service (notification chain)
- install → config → discover → service (when discovery enabled)

## Puppet Facts Used

- `$facts['kernel']`: Operating system kernel (Linux detection)
- `$facts['networking']['fqdn']`: Fully qualified domain name for service discovery
- `$facts['networking']['ip']`: IP address for service discovery
- `$facts['puppet_environment']`: Environment name for PuppetDB queries

## Template Conversion Notes

**haproxy.cfg.erb**:
- **Variables**: 19 variables including log_server, global_maxconn, ssl_enabled, stats configuration, timeouts
- **Ruby Logic**: SSL conditional blocks, stats conditional block, backends iteration
- **Conditional Rendering**: SSL configuration only when ssl_enabled=true, stats section when stats_enabled=true
- **Complex Expressions**: Backend loop with name extraction

**backend.conf.epp**:
- **Variables**: 10 variables including backend_name, balance, port, servers array, health_check options
- **Ruby Logic**: Server iteration with weight and SSL options
- **Conditional Rendering**: Health check options, SSL verification
- **Iterations**: Servers array loop with address:port:weight format

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources**:
- `@@haproxy::balancermember[$facts['networking']['fqdn']]` → exports server registration for load balancer discovery, migration notes about cross-node data sharing patterns for dynamic backend server registration
  - listening_service: `webservers`
  - server_names: `$facts['networking']['fqdn']`
  - ipaddresses: `$facts['networking']['ip']`
  - ports: `8080`
  - options: `check`

**Resource Collectors**:
- `Haproxy::Balancermember <| listening_service == 'webservers' |>` → collects exported server registrations, migration notes about node discovery requirements for automatic backend pool population

**PuppetDB Queries**:
- Query for nodes with `Profile::App_server` class in same environment, migration notes about infrastructure data access patterns for service discovery
- Returns certname and parameters for dynamic backend server discovery

**Host Identity Data**:
- Per-host PuppetDB data includes FQDN, IP address, and environment classification used for node classification and service registration

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
- Port 443 (HTTPS frontend, when SSL enabled)
- Port 9000 (statistics interface)

**Templates rendered**:
- haproxy.cfg.erb (1 render with 19 variables)
- backend.conf.epp (2 renders for webservers and api backends)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# Instance-specific checks
haproxy -f /etc/haproxy/haproxy.cfg -c
curl -s http://localhost:9000/haproxy-stats
curl -s http://localhost/health
curl -s http://localhost:8080/health
curl -s http://localhost:3000/api/health

# Configuration validation commands
haproxy -f /etc/haproxy/haproxy.cfg -c -q
test -f /etc/haproxy/conf.d/webservers.cfg
test -f /etc/haproxy/conf.d/api.cfg

# Network/connectivity checks
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :9000
ss -tlnp | grep haproxy
```