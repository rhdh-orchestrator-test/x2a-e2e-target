---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module with SSL termination, statistics interface, dynamic service discovery via PuppetDB, OS-specific firewall management (firewalld/ufw), and comprehensive backend configuration through Hiera hierarchy. Supports both static backend configuration and dynamic discovery of application servers.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 9000/9001 (stats)
  - Key Config: SSL termination, backend pools, health checks
- **stats interface**: HAProxy statistics dashboard
  - Location/Path: `/stats` URI endpoint
  - Port/Socket: 9000 (default), 9001 (lb01.fra.example.com override)
  - Key Config: HTTP auth, admin access, 30s refresh

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
site-modules/profile_haproxy/lib/facter/haproxy_version.rb
```

## Module Explanation

The module performs operations in this order:

1. **role::haproxy** (`site-modules/role/manifests/haproxy.pp`):
   - Conditional check: if `$facts['kernel'].downcase == 'linux'`
     - Creates `exec 'default'` resource with command `/bin/true`
   - Contains `::profile::base::base` class
   - Contains `::profile::loadbalancer::haproxy` class
   - Ordering: `Class['::profile::base::base'] -> Class['::profile::loadbalancer::haproxy']`

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Contains `profile_haproxy` class

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from Hiera lookups
   - Contains `profile_haproxy::install`
   - Contains `profile_haproxy::config`
   - Contains `profile_haproxy::service`
   - Contains `profile_haproxy::firewall`
   - Conditional: if `$discovery_enabled` (false by default)
     - Contains `profile_haproxy::discover`
     - Ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] -> Class['profile_haproxy::discover'] ~> Class['profile_haproxy::service']`
   - Else ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] ~> Class['profile_haproxy::service']`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - Creates `package 'haproxy'` with ensure present
   - Conditional: if `!empty($extra_packages)`
     - RedHat: Creates `package 'haproxy-selinux'` with ensure present
     - Debian: Creates `package 'haproxy-doc'` with ensure present
   - Creates `group 'haproxy'` with ensure present
   - Creates `user 'haproxy'` with gid haproxy, shell `/sbin/nologin`, home `/var/lib/haproxy`
   - Creates directory `/etc/haproxy` with mode 0755
   - Creates directory `/etc/haproxy/conf.d` with mode 0755
   - Creates directory `/var/lib/haproxy` owned by haproxy:haproxy
   - Conditional: if `$selinux_enabled` (RedHat: true, Debian: false)
     - Creates `exec 'haproxy_selinux_connect'` with command `setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - Creates `/etc/haproxy/haproxy.cfg` from template `haproxy.cfg.erb`
   - Iterations: `$backends.each` - runs 0 times (empty hash in common.yaml)
   - Iterations: `['503', '408'].each` - runs 2 times:
     - **503**: Creates `/etc/haproxy/errors/503.http` with HTTP error page content
     - **408**: Creates `/etc/haproxy/errors/408.http` with HTTP error page content
   - Creates directory `/etc/haproxy/errors` with mode 0755
   - Conditional: if `$stick_table_enabled` (defaults to false) - no resources created

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - Creates directory `/etc/systemd/system/haproxy.service.d`
   - Creates `/etc/systemd/system/haproxy.service.d/override.conf` with systemd override
   - Creates `exec 'haproxy_systemd_reload'` with command `systemctl daemon-reload`
   - Creates `service 'haproxy'` with ensure running and enable true
   - Creates `exec 'haproxy_config_check'` with command `haproxy -f /etc/haproxy/haproxy.cfg -c`
   - Creates `/etc/logrotate.d/haproxy` with logrotate configuration

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Case statement on `$firewall_provider`:
     - **firewalld branch** (RedHat):
       - Iterations: `['80', '443'].each` - runs 2 times:
         - **80**: Creates `exec 'firewalld_allow_80'` with command `firewall-cmd --zone=public --add-port=80/tcp --permanent`
         - **443**: Creates `exec 'firewalld_allow_443'` with command `firewall-cmd --zone=public --add-port=443/tcp --permanent`
       - Conditional: if `$stats_enabled` - creates stats port firewall rule
       - Creates `exec 'firewalld_reload'` with command `firewall-cmd --reload`
     - **ufw branch** (Debian):
       - Creates `package 'ufw'` with ensure installed
       - Creates `exec 'ufw_allow_http'` with command `ufw allow 80/tcp`
       - Creates `exec 'ufw_allow_https'` with command `ufw allow 443/tcp`
       - Conditional: if `$stats_enabled` - creates stats port ufw rule
       - Creates `exec 'ufw_enable'` with command `ufw --force enable`

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`):
   - Only included if `$discovery_enabled` is true
   - Exports `@@haproxy::balancermember[$facts['networking']['fqdn']]` with listening_service 'webservers'
   - Collects `Haproxy::Balancermember <<| listening_service == 'webservers' |>>`
   - Performs PuppetDB query for application servers in current environment
   - Iterations: `$app_servers.each` - creates balancermember resources for each discovered server

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
- `profile_haproxy::stats_port`: `9000` (type: integer)
- `profile_haproxy::stats_uri`: `/stats` (type: string)
- `profile_haproxy::stats_user`: `admin` (type: string)
- `profile_haproxy::stats_password`: `[ENCRYPTED]` (type: string)
- `profile_haproxy::global_maxconn`: `4000` (type: integer)
- `profile_haproxy::client_timeout`: `50000ms` (type: string)
- `profile_haproxy::server_timeout`: `50000ms` (type: string)
- `profile_haproxy::connect_timeout`: `5000ms` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+AES256:ECDHE+AES128:!aNULL:!MD5:!DSS` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::backends`: `{}` (type: hash)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-selinux']` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)
- `profile_haproxy::firewall_zone`: `public` (type: string)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-doc']` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**environment/production.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::stats_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::client_timeout`: `60000ms` (type: string)
- `profile_haproxy::server_timeout`: `60000ms` (type: string)
- `profile_haproxy::log_level`: `warning` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Environment-specific variables that vary by deployment environment
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Datacenter-specific variables for geographic locations
- `profile_haproxy::log_server`: `10.1.1.100` (type: string)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: Cluster-specific variables for service groups
- `profile_haproxy::global_maxconn`: `8000` (type: integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+AES256:!aNULL:!MD5` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (type: string)

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Host-specific variables for individual node overrides
- `profile_haproxy::stats_port`: `9001` (type: integer)

### Variable Migration Summary

- **Common defaults**: 25 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 7 variables that vary by operating system family
- **Environment-specific variables**: 8 variables that vary by deployment environment (dev, staging, prod)
- **Datacenter-specific variables**: 1 variable for geographic location settings
- **Cluster-specific variables**: 3 variables for service group configurations
- **Host-specific variables**: 1 variable for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::stats_enabled**: defined at common/environment levels, merge strategy: first
- **profile_haproxy::ssl_enabled**: defined at common/environment levels, merge strategy: first
- **profile_haproxy::stats_password**: defined at common level, merge strategy: first
- **profile_haproxy::backends**: defined at common level, merge strategy: deep

### Merge Strategy Notes

- Variables using `hash` merge - Hash values from multiple levels are merged (shallow merge)
- Variables using `deep` merge - Hash values are recursively merged (deep merge)
- Variables using `first` (default) - First value found wins, no merging

## Custom Types and Providers

**Custom Fact: haproxy_version**
- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Purpose: Executes `haproxy -v` to extract version number using regex pattern
- Linux-only execution with regex matching on version output
- Returns: HAProxy version string for package management decisions

## Dependencies

**External module dependencies**:
- `puppetlabs-stdlib` (version: 9.7.0)
- `puppetlabs-concat` (version: 9.0.2)
- `puppetlabs-firewall` (version: 8.1.3)

**System package dependencies**:
- `haproxy` (main package)
- `haproxy-selinux` (RedHat only)
- `haproxy-doc` (Debian only)
- `ufw` (Debian firewall)

**Service dependencies**:
- Install → Config → Service (with notification)
- Install → Config → Discover → Service (when discovery enabled)
- Firewall configuration runs in parallel

## Puppet Facts Used

- `$facts['kernel']`: OS kernel type (Linux check in role class)
- `$facts['networking']['fqdn']`: Fully qualified domain name for exported resources
- `$facts['networking']['ip']`: Primary IP address for load balancer member registration
- `$facts['puppet_environment']`: Puppet environment name for PuppetDB queries
- Custom fact `haproxy_version`: HAProxy version string extracted from `haproxy -v` output

## Template Conversion Notes

**haproxy.cfg.erb**:
- Variables: 19 template variables including SSL config, timeouts, logging settings
- Ruby logic blocks: SSL conditional rendering, stats interface conditional sections
- Complex expressions: Backend iteration loop (currently empty due to empty backends hash)
- Conditional rendering: SSL certificate paths, stats authentication, logging configuration

**backend.conf.epp**:
- Variables: 10 parameters for backend server configuration
- Ruby logic blocks: Health check conditionals, SSL server option rendering
- Iterations: Server list processing with weight assignments and SSL settings
- Complex expressions: Dynamic backend member generation with health check options

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. Document all PuppetDB usage patterns found in this module.

**Exported Resources** (`@@`):
- `@@haproxy::balancermember[$facts['networking']['fqdn']]`: Exports this node as load balancer member with listening_service 'webservers', server_names from FQDN, ipaddresses from networking facts, ports 8080, options 'check'. Migration notes: Cross-node data sharing pattern for service discovery requires centralized inventory system.

**Resource Collectors** (`<<| |>>`):
- `Haproxy::Balancermember <<| listening_service == 'webservers' |>>`: Collects all webserver members with filter condition on listening_service. Migration notes: Node discovery requirements need inventory query mechanism for dynamic backend configuration.

**PuppetDB Queries**:
- Query for application servers with `Profile::App_server` class in current environment. Returns server list for dynamic backend member creation. Migration notes: Infrastructure data access patterns require service discovery mechanism or static inventory management.

**Host Identity Data**:
- Per-host PuppetDB data includes FQDN, IP address, and environment classification used for load balancer member registration and backend server discovery.

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg`
- `/etc/haproxy/conf.d/*.cfg`
- `/etc/haproxy/errors/503.http`
- `/etc/haproxy/errors/408.http`
- `/etc/systemd/system/haproxy.service.d/override.conf`
- `/etc/logrotate.d/haproxy`

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend, if SSL enabled)
- Port 9000 (stats interface default)
- Port 9001 (stats interface lb01.fra.example.com)

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/*.cfg` (0 renders due to empty backends hash, would render once per backend when configured)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# haproxy instance checks
haproxy -f /etc/haproxy/haproxy.cfg -c
curl -I http://localhost:80
curl -I https://localhost:443
curl -u admin:[password] http://localhost:9000/stats
curl -u admin:[password] http://localhost:9001/stats  # lb01.fra.example.com only

# Configuration validation commands
test -f /etc/haproxy/haproxy.cfg
test -d /etc/haproxy/conf.d
test -f /etc/haproxy/errors/503.http
test -f /etc/haproxy/errors/408.http

# Network/connectivity checks
ss -tlnp | grep :80
ss -tlnp | grep :443
ss -tlnp | grep :9000
ss -tlnp | grep :9001  # lb01.fra.example.com only
firewall-cmd --list-ports  # RedHat
ufw status  # Debian
```