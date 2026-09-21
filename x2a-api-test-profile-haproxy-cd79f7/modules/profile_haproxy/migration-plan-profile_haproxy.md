---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: HAProxy load balancer module that configures a high-availability reverse proxy with SSL termination, statistics interface, dynamic backend discovery via PuppetDB, and firewall management. Supports both static Hiera-defined backends and dynamic service discovery across multiple environments and datacenters.

## Service Type and Instances

**Service Type**: Load Balancer / Reverse Proxy

**Configured Instances**:
- **haproxy**: Main load balancer service
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: 80 (HTTP), 443 (HTTPS), 8404 (stats)
  - Key Config: SSL termination, backend pools, health checks
- **webservers**: Primary backend pool
  - Location/Path: `/etc/haproxy/conf.d/webservers.cfg`
  - Port/Socket: 8080
  - Key Config: Round-robin balancing, health checks
- **api**: Dynamic backend pool (via PuppetDB discovery)
  - Location/Path: Dynamic configuration
  - Port/Socket: Variable per server
  - Key Config: Service discovery, automatic registration

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
   - Conditional: `if $facts['kernel'].downcase == 'linux'`
     - `exec 'default'` → command: `/bin/true`
   - `contain ::profile::base::base`
   - `contain ::profile::loadbalancer::haproxy`
   - Ordering: `Class['::profile::base::base'] -> Class['::profile::loadbalancer::haproxy']`

2. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - `contain profile_haproxy`

3. **profile_haproxy** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Sets class parameters from Hiera lookup
   - `contain profile_haproxy::install`
   - `contain profile_haproxy::config`
   - `contain profile_haproxy::service`
   - `contain profile_haproxy::firewall`
   - Conditional: `if $discovery_enabled` (false by default)
     - `contain profile_haproxy::discover`
     - Ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] -> Class['profile_haproxy::discover'] ~> Class['profile_haproxy::service']`
   - Default ordering: `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] ~> Class['profile_haproxy::service']`

4. **profile_haproxy::install** (`site-modules/profile_haproxy/manifests/install.pp`):
   - `package 'haproxy'` → ensure: `present`
   - Conditional: `if !empty($extra_packages)` (extra_packages: `['haproxy-stats', 'socat']` in production)
     - `package 'haproxy-stats'` → ensure: `present`
     - `package 'socat'` → ensure: `present`
   - `group 'haproxy'` → ensure: `present`
   - `user 'haproxy'` → ensure: `present`, gid: `haproxy`, shell: `/sbin/nologin`, home: `/var/lib/haproxy`
   - `file '/etc/haproxy'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/haproxy/conf.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/var/lib/haproxy'` → ensure: `directory`, owner: `haproxy`, group: `haproxy`, mode: `0755`
   - Conditional: `if $selinux_enabled` (false in staging, not set in production)
     - `exec 'haproxy_selinux_connect'` → command: `/usr/sbin/setsebool -P haproxy_connect_any 1`

5. **profile_haproxy::config** (`site-modules/profile_haproxy/manifests/config.pp`):
   - `file '/etc/haproxy/haproxy.cfg'` (template `site-modules/profile_haproxy/templates/haproxy.cfg.erb`) → owner: `root`, group: `root`, mode: `0644`
   - Iterations: `$backends.each` — runs 1 time for: **webservers**
     - **webservers**:
       - `file '/etc/haproxy/conf.d/webservers.cfg'` (template `site-modules/profile_haproxy/templates/backend.conf.epp`) → owner: `root`, group: `root`, mode: `0644`
   - Iterations: `['503', '408'].each` — runs 2 times for: **503**, **408**
     - **503**:
       - `file '/etc/haproxy/errors/503.http'` → content: `HTTP/1.0 503 Service Unavailable...`, owner: `root`, group: `root`, mode: `0644`
     - **408**:
       - `file '/etc/haproxy/errors/408.http'` → content: `HTTP/1.0 408 Request Timeout...`, owner: `root`, group: `root`, mode: `0644`
   - `file '/etc/haproxy/errors'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - Conditional: `if $stick_table_enabled` (true in production)
     - `file '/etc/haproxy/conf.d/stick-tables.cfg'` → content: `stick-table type ip size 100k expire 30m`, owner: `root`, group: `root`, mode: `0644`

6. **profile_haproxy::service** (`site-modules/profile_haproxy/manifests/service.pp`):
   - `file '/etc/systemd/system/haproxy.service.d'` → ensure: `directory`, owner: `root`, group: `root`, mode: `0755`
   - `file '/etc/systemd/system/haproxy.service.d/override.conf'` → content: `[Service]\nKillMode=mixed\nKillSignal=SIGUSR1\nExecReload=/bin/kill -USR2 $MAINPID`, owner: `root`, group: `root`, mode: `0644`
   - `exec 'haproxy_systemd_reload'` → command: `/bin/systemctl daemon-reload`, refreshonly: `true`
   - `service 'haproxy'` → ensure: `running`, enable: `true`, hasstatus: `true`, hasrestart: `true`
   - `exec 'haproxy_config_check'` → command: `/usr/sbin/haproxy -f /etc/haproxy/haproxy.cfg -c`, refreshonly: `true`
   - `file '/etc/logrotate.d/haproxy'` → content: `/var/log/haproxy.log { daily rotate 52 compress delaycompress }`, owner: `root`, group: `root`, mode: `0644`

7. **profile_haproxy::firewall** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Conditional: `case $firewall_provider` (firewalld in production, ufw in staging)
     - **Branch firewalld**:
       - `exec 'firewalld_reload'` → command: `/bin/firewall-cmd --reload`
     - **Branch ufw**:
       - `package 'ufw'` → ensure: `present`
       - `exec 'ufw_allow_http'` → command: `/usr/sbin/ufw allow 80/tcp`
       - `exec 'ufw_allow_https'` → command: `/usr/sbin/ufw allow 443/tcp`
       - `exec 'ufw_enable'` → command: `/usr/sbin/ufw --force enable`
     - **Branch none**: Firewall management disabled via Hiera
     - **Branch default**:
       - `notify 'Unknown firewall provider: ${firewall_provider}'`

8. **profile_haproxy::discover** (`site-modules/profile_haproxy/manifests/discover.pp`) — Only when discovery_enabled=true:
   - `@@haproxy::balancermember[$facts['networking']['fqdn']]` → listening_service: `webservers`, server_names: `$facts['networking']['fqdn']`, ipaddresses: `$facts['networking']['ip']`, ports: `8080`, options: `check`
   - `<<| Haproxy::Balancermember | listening_service == 'webservers' |>>`
   - PuppetDB Query: Finds all nodes with `Profile::App_server` class in current environment
   - Iterations: `$app_servers.each` — Loop runs 0 times (no app servers found in current environment)

## Variables

**Variable Flow Summary**: 25 variables across 8 Hiera levels

### Variable Definitions

**common.yaml (module-level)** → Migration note: Base defaults for all nodes
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::user`: `haproxy` (type: string)
- `profile_haproxy::group`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::config_file`: `/etc/haproxy/haproxy.cfg` (type: string)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::ssl_ciphers`: `ECDHE+AESGCM:ECDHE+AES256:ECDHE+AES128:!aNULL:!MD5:!DSS` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_user`: `admin` (type: string)
- `profile_haproxy::stats_password`: `ENC[PKCS7,encrypted_value]` (type: string)
- `profile_haproxy::stats_port`: `8404` (type: integer)
- `profile_haproxy::stats_uri`: `/stats` (type: string)

**os/RedHat.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::config_file`: `/etc/haproxy/haproxy.cfg` (type: string)
- `profile_haproxy::user`: `haproxy` (type: string)
- `profile_haproxy::group`: `haproxy` (type: string)

**os/Debian.yaml (OS-specific)** → Migration note: OS-specific variables, loaded conditionally based on OS family
- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::service_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::user`: `haproxy` (type: string)
- `profile_haproxy::group`: `haproxy` (type: string)

**environment/production.yaml (environment-specific)** → Migration note: Production environment overrides
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::global_maxconn`: `4000` (type: integer)
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-stats', 'socat']` (type: array)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `100k` (type: string)

**environment/staging.yaml (environment-specific)** → Migration note: Staging environment overrides
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)
- `profile_haproxy::global_maxconn`: `1000` (type: integer)
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

**datacenter/dc1_fra.yaml (datacenter-specific)** → Migration note: Frankfurt datacenter configuration
- `profile_haproxy::log_server`: `syslog.fra.example.com` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::ntp_servers`: `['ntp1.fra.example.com', 'ntp2.fra.example.com']` (type: array)

**cluster/haproxy_prod_fra.yaml (cluster-specific)** → Migration note: Production cluster in Frankfurt
- `profile_haproxy::global_maxconn`: `8000` (type: integer)
- `profile_haproxy::client_timeout`: `50s` (type: string)
- `profile_haproxy::server_timeout`: `50s` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)

**nodes/lb01.fra.example.com.yaml (host-specific)** → Migration note: Individual host overrides
- `profile_haproxy::backends`: `{webservers => {balance => roundrobin, port => 8080, servers => [{name => web01, address => 10.1.1.10, weight => 100}, {name => web02, address => 10.1.1.11, weight => 100}], health_check => httpchk GET /health, health_interval => 5s}}` (type: hash)
- `profile_haproxy::stats_port`: `8404` (type: integer)
- `profile_haproxy::log_server`: `syslog.fra.example.com` (type: string)

### Variable Migration Summary

- **Common defaults**: 16 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 6 variables that vary by operating system family
- **Environment-specific variables**: 8 variables that vary by deployment environment (production, staging)
- **Host-specific variables**: 3 variables for individual host overrides
- **Encrypted variables**: 1 variable that is encrypted (eyaml) and needs secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_haproxy::ssl_enabled**: defined at environment and module levels, merge strategy: first
- **profile_haproxy::global_maxconn**: defined at environment, cluster, and module levels, merge strategy: first
- **profile_haproxy::package_name**: defined at environment, module, and OS levels, merge strategy: first
- **profile_haproxy::stats_password**: defined at environment and module levels, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging
- Hash variables like `backends` use deep merge to combine server definitions across hierarchy levels

## Custom Types and Providers

**Custom Fact: haproxy_version**
- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Description: Executes `haproxy -v` command to extract version number using regex pattern. Only runs on Linux systems.
- Parameters: None (executes system command)
- Returns: HAProxy version string

## Dependencies

**External module dependencies**:
- puppetlabs-stdlib (version: 9.7.0)
- puppetlabs-concat (version: 9.0.2)
- puppetlabs-firewall (version: 8.1.3)

**System package dependencies**:
- haproxy (main package)
- haproxy-stats (production only)
- socat (production only)
- ufw (staging firewall)

**Service dependencies**:
- install → config → service (notify chain)
- install → config → discover → service (when discovery enabled)

## Puppet Facts Used

- `$facts['kernel']`: Operating system kernel (Linux detection)
- `$facts['networking']['fqdn']`: Fully qualified domain name (exported resource naming)
- `$facts['networking']['ip']`: Primary IP address (backend registration)
- `$facts['puppet_environment']`: Puppet environment name (PuppetDB queries)
- `$facts['os']['family']`: OS family (Debian/RedHat package differences)

## Template Conversion Notes

**haproxy.cfg.erb**:
- Variables used: log_server, ssl_enabled, stats configuration, timeouts, global_maxconn, ssl_ciphers, backends
- Ruby logic blocks: SSL conditional rendering, stats interface conditional, backend iteration loops
- Conditional rendering: SSL certificate paths only rendered when ssl_enabled=true
- Iterations: Backend configuration blocks generated for each backend in hash
- Complex expressions: SSL cipher suite configuration, backend server health check options

**backend.conf.epp**:
- Variables used: backend_name, balance method, port, servers array, health_check, health_interval, ssl_enabled
- Ruby logic blocks: Server iteration with weight and SSL options, health check conditionals
- Conditional rendering: SSL verification options only when backend SSL enabled
- Iterations: Server configuration lines for each server in servers array
- Complex expressions: Dynamic server configuration with conditional SSL verification and weight balancing

## PuppetDB Dependencies

**Context**: PuppetDB provides a centralized data store for cross-node resource sharing, node facts, and infrastructure queries. This module uses PuppetDB for dynamic backend discovery and load balancer member registration.

**Exported Resources** (`@@`):
- **@@haproxy::balancermember**: Exports current node as webserver backend member with listening_service 'webservers', port 8080, and health check options. Migration notes: Replace with Ansible service registration to external service discovery (Consul, etcd) or shared inventory system.

**Resource Collectors** (`<<| |>>`):
- **Haproxy::Balancermember collection**: Collects all exported webserver backend members with filter `listening_service == 'webservers'`. Migration notes: Replace with Ansible dynamic inventory queries or service discovery lookups to populate backend server lists.

**PuppetDB Queries**:
- **App server discovery**: Finds all nodes with `Profile::App_server` class in current environment for dynamic API backend registration. Migration notes: Replace with Ansible inventory group queries or service discovery API calls to identify application servers.

**Host Identity Data**:
- **FQDN and IP extraction**: Uses `$facts['networking']['fqdn']` and `$facts['networking']['ip']` for backend member identification. Migration notes: Replace with Ansible facts `ansible_fqdn` and `ansible_default_ipv4.address` for node identification in service registration.

## Checks for the Migration

**Files to verify**:
- `/etc/haproxy/haproxy.cfg`
- `/etc/haproxy/conf.d/webservers.cfg`
- `/etc/haproxy/errors/503.http`
- `/etc/haproxy/errors/408.http`
- `/etc/systemd/system/haproxy.service.d/override.conf`
- `/etc/logrotate.d/haproxy`

**Service endpoints to check**:
- Port 80 (HTTP frontend)
- Port 443 (HTTPS frontend)
- Port 8404 (statistics interface)
- Backend servers on port 8080

**Templates rendered**:
- `haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` (1 render)
- `backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status haproxy
systemctl is-enabled haproxy

# Instance-specific checks
haproxy -f /etc/haproxy/haproxy.cfg -c
curl -I http://localhost:8404/stats
netstat -tlnp | grep :80
netstat -tlnp | grep :443
netstat -tlnp | grep :8404

# Configuration validation commands
test -f /etc/haproxy/haproxy.cfg
test -f /etc/haproxy/conf.d/webservers.cfg
test -d /etc/haproxy/errors

# Network/connectivity checks
curl -I http://10.1.1.10:8080/health
curl -I http://10.1.1.11:8080/health
ping -c 1 syslog.fra.example.com
```