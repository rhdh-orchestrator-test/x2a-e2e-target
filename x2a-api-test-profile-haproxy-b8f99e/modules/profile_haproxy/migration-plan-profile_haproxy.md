---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: This module installs and configures HAProxy as a systemd-managed HTTP load balancer. It creates the HAProxy package, service account, directories, primary configuration, backend fragments, error files, systemd drop-in, logrotate configuration, and optional firewall and PuppetDB discovery resources. For `lb01.fra.example.com`, the effective configuration uses HAProxy package `haproxy`, service `haproxy`, HTTP port `80`, statistics port `9001`, `global_maxconn=32768`, three backends, disabled SSL, disabled firewall management, disabled stick tables, and disabled PuppetDB discovery. The statistics password is overridden by control-repository data with the plaintext value `test-haproxy-password`; migrate this credential to Ansible Vault.

## Service Type and Instances

**Service Type**: HTTP load balancer / reverse proxy

**Configured Instances**:

- **HAProxy primary service**: Systemd-managed HAProxy load balancer
  - Package: `haproxy`
  - Service: `haproxy`
  - Configuration: `/etc/haproxy/haproxy.cfg`
  - Configuration directory: `/etc/haproxy`
  - Backend directory: `/etc/haproxy/conf.d`
  - Runtime directory: `/var/lib/haproxy`
  - User/group: `haproxy:haproxy`
  - Frontend: `*:80`
  - TLS frontend: disabled because effective `ssl_enabled=false`
  - Statistics listener: enabled
  - Statistics port: `9001`
  - Statistics URI: `/haproxy-stats`
  - Statistics user: `admin`
  - Statistics password: `test-haproxy-password`; store securely in Ansible Vault
  - Maximum connections: `32768`
  - Socket: `/var/lib/haproxy/stats`
  - Socket mode: `660`
  - Socket level: `admin`

- **`webservers` backend**: HTTP web-server pool
  - Balance method: `roundrobin`
  - Port: `8080`
  - Health check: `httpchk GET /health`
  - Health interval: `5s`
  - `web1`: `10.0.1.10:8080`, weight `100`
  - `web2`: `10.0.1.11:8080`, weight `100`
  - `web3`: `10.0.1.12:8080`, weight `100`

- **`api` backend**: API-server pool
  - Balance method: `leastconn`
  - Port: `3000`
  - Health check: `httpchk GET /api/health`
  - Health interval: `10s`
  - `api1-fra`: `10.100.2.10:3000`, weight `200`
  - `api2-fra`: `10.100.2.11:3000`, weight `100`
  - The node-level server list replaces the common `api` server list while retaining common backend settings through deep merge.

- **`internal_monitoring` backend**: Internal monitoring pool
  - Balance method: `roundrobin`
  - Port: `9090`
  - Health check: `httpchk GET /-/healthy`
  - Health interval: `15s`
  - `prom1-fra`: `10.100.3.10:9090`, weight `100`

## File Structure

```text
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

data/common.yaml
site-modules/profile_haproxy/data/common.yaml
site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml
site-modules/profile_haproxy/data/environment/production.yaml
site-modules/profile_haproxy/data/os/Debian.yaml
site-modules/profile_haproxy/data/os/RedHat.yaml
site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml

site-modules/profile_haproxy/lib/facter/haproxy_version.rb
```

## Module Explanation

The module performs operations in this order:

1. **`role::haproxy`** (`site-modules/role/manifests/haproxy.pp`):
   - Includes `::profile::base::base`.
   - Includes `::profile::loadbalancer::haproxy`.
   - The load-balancer profile includes `profile_haproxy`.
   - Uses the `kernel` fact to execute the Linux-specific `exec[None]` resource on Linux systems.
   - Does not execute that resource on non-Linux systems.
   - Reads the Puppet `environment` value for control-repository/profile selection.
   - Ordering: `Class['::profile::base::base'] -> Class['::profile::loadbalancer::haproxy']`.

2. **`profile::loadbalancer::haproxy`** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Includes `profile_haproxy`.
   - Acts as the site profile wrapper for the HAProxy module.

3. **`profile_haproxy`** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Resolves class parameters through Hiera.
   - Contains `profile_haproxy::install`.
   - Contains `profile_haproxy::config`.
   - Contains `profile_haproxy::service`.
   - Contains `profile_haproxy::firewall`.
   - Does not contain `profile_haproxy::discover` for the described node because `discovery_enabled=false`.
   - Ordering:
     - `Class['profile_haproxy::install'] -> Class['profile_haproxy::config']`
     - `Class['profile_haproxy::config'] ~> Class['profile_haproxy::service']`
   - The firewall class has no explicit ordering relationship shown against install, config, or service.

4. **`profile_haproxy::install`** (`site-modules/profile_haproxy/manifests/install.pp`):
   - Installs package `haproxy`.
   - Creates group `haproxy`.
   - Creates user `haproxy`.
   - Creates `/etc/haproxy`.
   - Creates `/etc/haproxy/conf.d`.
   - Creates `/var/lib/haproxy`.
   - Debian conditional:
     - The configured default extra package is `hatop`.
     - The effective control-repository value is `extra_packages=[]`; no extra package resources are created.
   - RedHat conditional:
     - Supports `haproxy-systemd-wrapper`.
     - Supports `policycoreutils-python-utils`.
     - The effective control-repository empty list prevents these packages from being installed for the described node.
   - SELinux conditional:
     - Debian effective value: `false`; no SELinux exec runs.
     - RedHat effective value: `true`; creates `exec['haproxy_selinux_connect']`.
   - The Ansible implementation must select OS-specific behavior using `ansible_facts['os_family']`.

5. **`profile_haproxy::config`** (`site-modules/profile_haproxy/manifests/config.pp`):
   - Creates `/etc/haproxy/errors`.
   - Renders `/etc/haproxy/haproxy.cfg` once from `site-modules/profile_haproxy/templates/haproxy.cfg.erb`.
   - Renders `/etc/haproxy/conf.d/webservers.cfg` once from `site-modules/profile_haproxy/templates/backend.conf.epp`.
   - Renders `/etc/haproxy/conf.d/api.cfg` once from `site-modules/profile_haproxy/templates/backend.conf.epp`.
   - Renders `/etc/haproxy/conf.d/internal_monitoring.cfg` once from `site-modules/profile_haproxy/templates/backend.conf.epp`.
   - The backend loop runs three times with actual names:
     - `webservers`
     - `api`
     - `internal_monitoring`
   - Creates `/etc/haproxy/errors/503.http`.
   - Creates `/etc/haproxy/errors/408.http`.
   - The error-file loop runs twice with actual status values:
     - `503`
     - `408`
   - Does not create `/etc/haproxy/conf.d/stick-tables.cfg` because effective `stick_table_enabled=false`.
   - If the control-repository override is removed, stick-table configuration uses `size=200k` and `expire=30m`.

   **Primary configuration values**:
   - `log_server=127.0.0.1`
   - `log_facility=local0`
   - `log_level=warning`
   - `global_maxconn=32768`
   - `user=haproxy`
   - `group=haproxy`
   - `ssl_enabled=false`
   - `connect_timeout=5s`
   - `client_timeout=60s`
   - `server_timeout=60s`
   - `retries=3`
   - `stats_enabled=true`
   - `stats_port=9001`
   - `stats_uri=/haproxy-stats`
   - `stats_user=admin`
   - `stats_password=test-haproxy-password`
   - `ssl_ciphers=ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384`
   - `ssl_cert_path=/etc/ssl/certs`
   - `backends=webservers, api, internal_monitoring`

   **Rendered directives**:
   - `chroot /var/lib/haproxy`
   - `daemon`
   - `stats socket /var/lib/haproxy/stats mode 660 level admin`
   - HTTP defaults
   - `timeout connect 5s`
   - `timeout client 60s`
   - `timeout server 60s`
   - `retries 3`
   - `errorfile 503 /etc/haproxy/errors/503.http`
   - `errorfile 408 /etc/haproxy/errors/408.http`
   - Statistics listener bound to `*:9001`
   - `stats uri /haproxy-stats`
   - `stats auth admin:test-haproxy-password`
   - `frontend http_front`
   - `bind *:80`
   - `default_backend webservers`

   **Expanded backend iterations**:
   - `webservers`: renders `web1`, `web2`, and `web3`; uses `roundrobin`, `httpchk GET /health`, and `default-server inter 5s`.
   - `api`: renders `api1-fra` and `api2-fra`; uses `leastconn`, `httpchk GET /api/health`, and `default-server inter 10s`.
   - `internal_monitoring`: renders `prom1-fra`; uses `roundrobin`, `httpchk GET /-/healthy`, and `default-server inter 15s`.
   - SSL server suffixes are not rendered because `ssl_enabled=false`.

6. **`profile_haproxy::service`** (`site-modules/profile_haproxy/manifests/service.pp`):
   - Creates `/etc/systemd/system/haproxy.service.d`.
   - Creates `/etc/systemd/system/haproxy.service.d/override.conf`.
   - Runs `exec['haproxy_systemd_reload']`.
   - Runs `exec['haproxy_config_check']`.
   - Enables and manages `service['haproxy']`.
   - Creates `/etc/logrotate.d/haproxy`.
   - Required operational order:
     - Create the systemd drop-in directory.
     - Create `override.conf`.
     - Run `systemctl daemon-reload`.
     - Validate the HAProxy configuration.
     - Enable and start or restart `haproxy`.
     - Deploy logrotate configuration.
   - Exact command strings, service attributes, override contents, logrotate contents, and resource-level ordering require verification from the source manifest or existing host configuration before implementation.

7. **`profile_haproxy::firewall`** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Resolves `firewall_provider`.
   - The effective provider is `none`.
   - No firewalld resources, UFW package, UFW rules, or reload commands execute for the described node.
   - Supported alternative branches:
     - `firewalld`: configure the `public` zone, iterate over `80/tcp`, `443/tcp` when SSL is enabled, and `9001/tcp` when statistics are enabled, then run `exec['firewalld_reload']`.
     - `ufw`: install `ufw`, allow HTTP, optionally allow HTTPS and the statistics port, then run `exec['ufw_enable']`.
     - Unknown provider: notify `Unknown firewall provider: ${firewall_provider}`.

8. **`profile_haproxy::discover`** (`site-modules/profile_haproxy/manifests/discover.pp`):
   - Not executed for `lb01.fra.example.com` because `discovery_enabled=false`.
   - When enabled, exports `haproxy::balancermember[$facts['networking']['fqdn']]` with:
     - `listening_service=webservers`
     - `server_names=$facts['networking']['fqdn']`
     - `ipaddresses=$facts['networking']['ip']`
     - `ports=8080`
     - `options=check`
   - Collects `Haproxy::Balancermember <| listening_service == 'webservers' |>`.
   - Queries PuppetDB for `Profile::App_server` resources associated with `Profile::Base` resources whose environment equals `$facts['puppet_environment']`.
   - The `$app_servers.each` loop is runtime-dependent; no concrete discovered names are present in Hiera.
   - Each discovered server creates `haproxy::balancermember 'api-${certname}'`.
   - Ansible replacement: use inventory groups, service discovery, or an explicit backend host variable. Do not reproduce PuppetDB exported-resource semantics directly.

## Variables

**Variable Flow Summary**: 32 HAProxy-related parameters are resolved through a 21-level Hiera hierarchy. The supplied data uses control-repository common, node, cluster, environment, OS, and module-common levels. `profile_haproxy::backends` uses deep merge. The effective node is `lb01.fra.example.com` in the `haproxy_prod_fra` production cluster.

### Hiera Hierarchy

Highest to lowest:

- `nodes/%{trusted.certname}.yaml`
- `role/%{::role}.yaml`
- `cluster/%{::cluster_name}.yaml`
- `application_tier/%{::app_tier}.yaml`
- `application/%{::application}.yaml`
- `team/%{::team}.yaml`
- `business_unit/%{::business_unit}.yaml`
- `lifecycle/%{::lifecycle}.yaml`
- `environment/%{::environment}.yaml`
- `network_zone/%{::network_zone}.yaml`
- `datacenter/%{::datacenter}.yaml`
- `region/%{::region}.yaml`
- `country/%{::country}.yaml`
- `architecture/%{facts.architecture}.yaml`
- `os_release/%{facts.os.name}_%{facts.os.release.full}.yaml`
- `osfamily_release/%{facts.os.family}_%{facts.os.release.major}.yaml`
- `os/%{facts.os.family}.yaml`
- `kernel/%{facts.kernel}.yaml`
- `is_container/%{facts.is_virtual}.yaml`
- `virtual/%{facts.virtual}.yaml`
- `common.yaml`

Class parameter lookup uses:

- `lookup('profile_haproxy::<parameter>')`
- `lookup('profile_haproxy::backends', { merge => 'deep' })`
- `lookup('profile_haproxy::discovery_enabled', Boolean, 'first', false)`

### Variable Definitions

#### `data/common.yaml` — control-repository common data

Migration note: Highest-priority common overrides for all applicable nodes.

- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::stats_password`: `test-haproxy-password` (type: string; plaintext secret override)
- `profile_haproxy::firewall_provider`: `none` (type: string)
- `profile_haproxy::extra_packages`: `[]` (type: array)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

#### `site-modules/profile_haproxy/data/common.yaml` — module defaults

Migration note: Base module defaults for nodes without higher-priority overrides.

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
- `profile_haproxy::stats_password`: `ENC[PKCS7,MIIBygYJKoZIhvcNAQcDoIIBuzCCAbcCAQAxggEhMIIBHQIBADAFMAACAQEwDQYJKoZIhvcNAQEBBQAEggEAExample]` (type: eyaml-encrypted string)
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
- `profile_haproxy::backends`: hash containing `webservers` and `api` (type: hash)
- `lookup_options.profile_haproxy::backends.merge`: `deep` (type: string)

Common `webservers` backend:

- `balance`: `roundrobin` (type: string)
- `port`: `8080` (type: integer)
- `health_check`: `httpchk GET /health` (type: string)
- `health_interval`: `5s` (type: string)
- Servers: `web1`, `web2`, and `web3` (type: hash)

Common `api` backend:

- `balance`: `leastconn` (type: string)
- `port`: `3000` (type: integer)
- `health_check`: `httpchk GET /api/health` (type: string)
- `health_interval`: `10s` (type: string)
- Servers: `api1` and `api2` (type: hash)

#### `site-modules/profile_haproxy/data/environment/production.yaml` — production data

Migration note: Production-specific values; overridden by higher-priority cluster, node, or control-repository data where applicable.

- `profile_haproxy::global_maxconn`: `16384` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `warning` (type: string)
- `profile_haproxy::client_timeout`: `60s` (type: string)
- `profile_haproxy::server_timeout`: `60s` (type: string)
- `profile_haproxy::stats_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `200k` (type: string)
- `profile_haproxy::stick_table_expire`: `30m` (type: string)

#### `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml` — cluster data

Migration note: Frankfurt production-cluster settings.

- `profile_haproxy::global_maxconn`: `32768` (type: integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (type: string)
- `profile_haproxy::backends.internal_monitoring`: hash (type: hash)
  - `balance`: `roundrobin`
  - `port`: `9090`
  - `health_check`: `httpchk GET /-/healthy`
  - `health_interval`: `15s`
  - `servers.prom1-fra.address`: `10.100.3.10`
  - `servers.prom1-fra.weight`: `100`

#### `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml` — host data

Migration note: Host-specific overrides for `lb01.fra.example.com`.

- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_port`: `9001` (type: integer)
- `profile_haproxy::backends.api.servers`: hash (type: hash)
  - `api1-fra.address`: `10.100.2.10`
  - `api1-fra.weight`: `200`
  - `api2-fra.address`: `10.100.2.11`
  - `api2-fra.weight`: `100`

#### `site-modules/profile_haproxy/data/os/Debian.yaml` — Debian data

Migration note: Debian-specific values selected from `facts.os.family`.

- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `['hatop']` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

#### `site-modules/profile_haproxy/data/os/RedHat.yaml` — RedHat data

Migration note: RedHat-specific values selected from `facts.os.family`.

- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::firewall_zone`: `public` (type: string)
- `profile_haproxy::extra_packages`: `['haproxy-systemd-wrapper', 'policycoreutils-python-utils']` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

### Effective Values for `lb01.fra.example.com`

- `package_name`: `haproxy`
- `config_dir`: `/etc/haproxy`
- `config_file`: `/etc/haproxy/haproxy.cfg`
- `service_name`: `haproxy`
- `user`: `haproxy`
- `group`: `haproxy`
- `stats_enabled`: `true`
- `stats_port`: `9001`
- `stats_uri`: `/haproxy-stats`
- `stats_user`: `admin`
- `stats_password`: `test-haproxy-password`
- `global_maxconn`: `32768`
- `client_timeout`: `60s`
- `server_timeout`: `60s`
- `connect_timeout`: `5s`
- `retries`: `3`
- `ssl_enabled`: `false`
- `ssl_cert_path`: `/etc/ssl/certs`
- `ssl_key_path`: `/etc/ssl/private`
- `ssl_ciphers`: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384`
- `ssl_min_version`: `TLSv1.3`
- `log_server`: `127.0.0.1`
- `log_facility`: `local0`
- `log_level`: `warning`
- `firewall_provider`: `none`
- `extra_packages`: `[]`
- `stick_table_enabled`: `false`
- `discovery_enabled`: `false`

### Variable Migration Summary

- **Control-repository common**: 6 variables
- **Module common**: 25 variables plus backend merge configuration
- **OS-specific**: 5 Debian variables or 6 RedHat variables
- **Environment-specific**: 9 production variables
- **Cluster-specific**: 4 variables
- **Host-specific**: 3 variables
- **Encrypted variables**: 1 encrypted source value, `profile_haproxy::stats_password`
- **Credential/path-sensitive variables**: `stats_password`, `ssl_cert_path`, and `ssl_key_path`

Ansible mapping:

- Store common and environment values in group variables.
- Store `lb01.fra.example.com` overrides in host variables.
- Store backend definitions as structured YAML dictionaries.
- Use Ansible Vault for the statistics password.
- Use `ansible_facts['os_family']` for Debian and RedHat conditionals.
- Use inventory groups or explicit variables instead of PuppetDB discovery.

### Cross-Level Overrides

- `profile_haproxy::package_name`: defined in module common, OS data, and control-repository common; effective value `haproxy`.
- `profile_haproxy::stats_password`: encrypted in module common and overridden by plaintext control-repository common; effective value `test-haproxy-password`.
- `profile_haproxy::ssl_enabled`: module common `false`, production `true`, control-repository common `false`; effective value `false`.
- `profile_haproxy::global_maxconn`: module common `4096`, production `16384`, cluster `32768`; effective value `32768`.
- `profile_haproxy::stats_enabled`: module common `true`, production `false`, node `true`; effective value `true`.
- `profile_haproxy::stats_port`: module common `9000`, node `9001`; effective value `9001`.
- `profile_haproxy::backends`: deep merge; common `webservers` is retained, common `api` is retained with its server list overridden by the node, and cluster `internal_monitoring` is added.
- `profile_haproxy::stick_table_enabled`: production `true`, control-repository common `false`; effective value `false`.

### Merge Strategy Notes

- `hash` merge: hash values from multiple levels are merged shallowly.
- `deep` merge: nested hash values are recursively merged.
- `first` merge: first value found wins.
- Default lookup behavior is `first` unless explicitly configured otherwise.
- `profile_haproxy::backends` uses `deep`.
- `profile_haproxy::discovery_enabled` uses `first` with default `false`.

## Custom Types and Providers

### Custom Facter Fact

- Fact: `haproxy_version`
- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Intended behavior: Linux-only fact that runs `haproxy -v 2>/dev/null`.
- Extracts the first `digits.digits.digits` version following the word `version`.
- Returns `nil` when HAProxy is unavailable or output does not match.
- The supplied execution-tree analysis did not include this fact implementation; verify the source file separately before relying on these details.
- Ansible equivalent:
  - Install `/etc/ansible/facts.d/haproxy_version.fact`, or
  - Run `haproxy -v` and parse the result in a task.
- No custom Ansible module is required.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.7.0`
- `puppetlabs-concat` `9.0.2`
- `puppetlabs-firewall` `8.1.3`

**System package dependencies**:

- `haproxy`
- `hatop` on Debian when the higher-priority empty `extra_packages` override is absent
- `haproxy-systemd-wrapper` on RedHat when enabled
- `policycoreutils-python-utils` on RedHat when enabled
- `ufw` when the UFW firewall branch is selected

**Service dependencies**:

- Installation precedes configuration.
- Configuration completion notifies the service.
- The systemd drop-in must exist before daemon reload.
- HAProxy configuration validation must pass before service start or restart.
- When discovery is enabled, discovery follows configuration and notifies the service.
- Firewall configuration is disabled for the described node.

## Puppet Facts Used

- `$facts['kernel']`: determines whether the Linux-specific role exec runs.
- `fact('environment')`: selects the Puppet control-repository environment.
- `$facts['networking']['fqdn']`: identifies the host for exported balancermembers.
- `$facts['networking']['ip']`: supplies the exported balancermember IP address.
- `$facts['puppet_environment']`: filters the PuppetDB application-server query.
- `facts.architecture`: selects architecture-specific Hiera data.
- `facts.os.name`: selects OS-release Hiera data.
- `facts.os.release.full`: selects full OS-release Hiera data.
- `facts.os.family`: selects Debian or RedHat Hiera data.
- `facts.os.release.major`: selects OS-family and major-release Hiera data.
- `facts.is_virtual`: selects the container-detection Hiera level.
- `facts.virtual`: selects virtual/physical Hiera data.
- `haproxy_version`: reports the installed HAProxy version; implementation requires source verification.

## Template Conversion Notes

### `site-modules/profile_haproxy/templates/haproxy.cfg.erb`

- Render count: `1`.
- Documented variables:
  - `log_server`
  - `log_facility`
  - `log_level`
  - `global_maxconn`
  - `user`
  - `group`
  - `ssl_enabled`
  - `ssl_ciphers`
  - `ssl_cert_path`
  - `ssl_key_path`
  - `ssl_min_version`
  - `connect_timeout`
  - `client_timeout`
  - `server_timeout`
  - `retries`
  - `stats_enabled`
  - `stats_port`
  - `stats_uri`
  - `stats_user`
  - `stats_password`
  - `backends`
- The validation notes identify a reported 21-variable count, while the supplied plan previously listed only 19. The three SSL path/version values are documented here, but exact template references require source verification.
- Logic:
  - SSL global directives render only when `ssl_enabled`.
  - The statistics listener renders only when `stats_enabled`.
  - HTTPS bind and redirect render only when `ssl_enabled`.
  - Backend references render once for each backend.
- Ansible conversion:
  - Use a Jinja2 template.
  - Preserve HAProxy directive ordering and conditional whitespace.
  - Store `stats_password` in Ansible Vault.
  - Do not expose the password in task output.

### `site-modules/profile_haproxy/templates/backend.conf.epp`

- Render count: `3`.
- Documented variables:
  - `backend_name`
  - `balance`
  - `port`
  - `servers`
  - `health_check`
  - `health_interval`
  - `ssl_enabled`
  - Nested server address
  - Nested server port
  - Nested server weight
  - Nested server check state
- The validation notes report 11 variables and one aggregate logic block; the exact EPP variable references and block structure require source verification.
- Aggregate logic:
  - Render the backend name and balance method.
  - Render the backend port.
  - Render the health-check directive when present.
  - Render the health interval when present.
  - Iterate over the actual server entries.
  - Render each server address, port, check setting, and weight.
  - Append `ssl verify none` only when `ssl_enabled=true`.
- Ansible conversion:
  - Use one Jinja2 template per backend or a task loop writing `/etc/haproxy/conf.d/{{ backend_name }}.cfg`.
  - Preserve the deep-merged backend data and actual server names.

### Error Files

- `/etc/haproxy/errors/503.http`
- `/etc/haproxy/errors/408.http`
- The supplied execution-tree data does not contain their exact contents. Preserve the current files or obtain the Puppet source before implementation.

### Service Templates and Files

- `/etc/systemd/system/haproxy.service.d/override.conf`
- `/etc/logrotate.d/haproxy`
- Exact contents require source or host verification.

## PuppetDB Dependencies

**Context**: PuppetDB is used only when `discovery_enabled=true`. It is disabled for `lb01.fra.example.com`.

- **Exported Resources**:
  - Resource type: `haproxy::balancermember`
  - Exported title: `$facts['networking']['fqdn']`
  - Exported values:
    - `listening_service=webservers`
    - `server_names=$facts['networking']['fqdn']`
    - `ipaddresses=$facts['networking']['ip']`
    - `ports=8080`
    - `options=check`
  - Effective behavior: no resource is exported because discovery is disabled.
  - Migration: define backend members in Ansible inventory or explicit variables.

- **Resource Collectors**:
  - Collector: `Haproxy::Balancermember <| listening_service == 'webservers' |>`.
  - Effective behavior: no collector is evaluated because discovery is disabled.
  - Migration: replace cross-node collection with inventory groups or generated backend variables.

- **PuppetDB Queries**:
  - Query:
    `resources[certname, parameters] { type = 'Class' and title = 'Profile::App_server' and certname in resources[certname] { type = 'Class' and title = 'Profile::Base' and parameters.environment = '${facts['puppet_environment']}' } }`
  - Returned data: application-server certificates and parameters matching the current Puppet environment.
  - Use: creates `haproxy::balancermember 'api-${certname}'`.
  - Effective behavior: query is not executed because discovery is disabled.
  - Migration: use environment-specific inventory groups such as `groups['app_servers']` or `haproxy_api_servers`.

- **Host Identity Data**:
  - `$facts['networking']['fqdn']` identifies the local host.
  - `$facts['networking']['ip']` supplies the local exported address.
  - `$facts['puppet_environment']` selects same-environment application servers.
  - Migration: use `inventory_hostname`, `ansible_fqdn`, host variables, and inventory group membership.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/haproxy.pp`
- `site-modules/profile/manifests/loadbalancer/haproxy.pp`
- `site-modules/profile_haproxy/manifests/init.pp`
- `site-modules/profile_haproxy/manifests/install.pp`
- `site-modules/profile_haproxy/manifests/config.pp`
- `site-modules/profile_haproxy/manifests/service.pp`
- `site-modules/profile_haproxy/manifests/fire