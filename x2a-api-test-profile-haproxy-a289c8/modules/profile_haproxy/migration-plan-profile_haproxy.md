---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: This module installs, configures, and manages HAProxy as an HTTP/HTTPS load balancer and reverse proxy. It creates the HAProxy package, user, group, directories, systemd override, logrotate configuration, main configuration, backend fragments, optional TLS, statistics, stick-table, SELinux, and firewall configuration. Default backends are `webservers` and `api`; the `haproxy_prod_fra` cluster adds `internal_monitoring`. Configuration is primarily Hiera-driven, with deep merging for backend hashes. Optional PuppetDB discovery exports and collects `haproxy::balancermember` resources and queries application servers dynamically; this is disabled by default and should be replaced with explicit Ansible inventory or service-discovery data.

## Service Type and Instances

**Service Type**: HTTP/HTTPS load balancer and reverse proxy.

**Configured Instances**:

- **HAProxy**
  - Purpose: Terminates HTTP/HTTPS traffic and distributes requests to configured backend servers.
  - Package: `haproxy`
  - Service: `haproxy`
  - Location/Path: `/etc/haproxy`
  - Main configuration: `/etc/haproxy/haproxy.cfg`
  - Fragment directory: `/etc/haproxy/conf.d`
  - Error-page directory: `/etc/haproxy/errors`
  - Runtime directory: `/var/lib/haproxy`
  - Port/Socket: HTTP `80`; HTTPS `443` when TLS is enabled; statistics `9000` when enabled; master socket `/run/haproxy-master.sock`
  - HAProxy user/group: `haproxy`
  - PID file: `/run/haproxy.pid`
  - Key configuration: Statistics URI `/haproxy-stats`; default balance and health-check settings are defined per backend.

- **`webservers`**
  - Purpose: Routes traffic to web application servers.
  - Balance method: `roundrobin`
  - Backend port: `8080`
  - Health check: `httpchk GET /health`
  - Health interval: `5s`
  - Servers:
    - `web1`: `10.0.1.10:8080`, weight `100`
    - `web2`: `10.0.1.11:8080`, weight `100`
    - `web3`: `10.0.1.12:8080`, weight `100`

- **`api`**
  - Purpose: Routes traffic to API application servers.
  - Balance method: `leastconn`
  - Backend port: `3000`
  - Health check: `httpchk GET /api/health`
  - Health interval: `10s`
  - Servers:
    - `api1`: `10.0.2.10:3000`, weight `100`
    - `api2`: `10.0.2.11:3000`, weight `100`

- **`internal_monitoring`**
  - Purpose: Routes traffic to the Frankfurt production monitoring service.
  - Availability: Only in the `haproxy_prod_fra` cluster.
  - Balance method: `roundrobin`
  - Backend port: `9090`
  - Health check: `httpchk GET /-/healthy`
  - Health interval: `15s`
  - Servers:
    - `prom1-fra`: `10.100.3.10:9090`, weight `100`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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
site-modules/profile_haproxy/files/haproxy_errors/503.http
site-modules/profile_haproxy/files/haproxy_errors/408.http
site-modules/profile_haproxy/hiera.yaml
site-modules/profile_haproxy/data/common.yaml
site-modules/profile_haproxy/data/environment/production.yaml
site-modules/profile_haproxy/data/environment/staging.yaml
site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml
data/common.yaml
site-modules/profile_haproxy/lib/facter/haproxy_version.rb
```

## Module Explanation

The module executes in the following order.

### 1. `role::haproxy` (`site-modules/role/manifests/haproxy.pp`)

- Evaluates the Linux-only condition `$facts['kernel'].downcase == 'linux'`.
- References `Class['::profile::base::base']`.
- References `Class['::profile::loadbalancer::haproxy']`.
- The supplied execution tree does not expose the exact command or title associated with `exec[None]`.
- Orders `Class['::profile::base::base']` before `Class['::profile::loadbalancer::haproxy']`.

### 2. `profile::loadbalancer::haproxy` (`site-modules/profile/manifests/loadbalancer/haproxy.pp`)

- Includes `profile_haproxy`.
- Delegates HAProxy installation, configuration, service management, firewall configuration, and optional discovery to `profile_haproxy`.

### 3. `profile_haproxy` (`site-modules/profile_haproxy/manifests/init.pp`)

- Contains `profile_haproxy::install`.
- Contains `profile_haproxy::config`.
- Contains `profile_haproxy::service`.
- Contains `profile_haproxy::firewall`.
- Uses `profile_haproxy::discovery_enabled`, which defaults to `false`.
- When discovery is enabled:
  - Installation precedes configuration.
  - Configuration precedes discovery.
  - Discovery refreshes the service.
- When discovery is disabled:
  - Installation precedes configuration.
  - Configuration refreshes the service.
- Configuration resources notify the service class, causing service refresh or restart behavior after configuration changes.

### 4. `profile_haproxy::install` (`site-modules/profile_haproxy/manifests/install.pp`)

- Installs `Package['haproxy']` with `ensure => installed`.
- Evaluates `profile_haproxy::extra_packages`, defaulting to `[]`.
- The supplied repository data produces no extra-package resources.
- If configured, the extra-package loop creates one installed package resource for each configured package, requiring `Package['haproxy']`.
- Creates `Group['haproxy']` with `ensure => present` and `system => true`.
- Creates `User['haproxy']` with:
  - `ensure => present`
  - `gid => haproxy`
  - `home => /var/lib/haproxy`
  - `shell => /sbin/nologin`
  - `system => true`
  - Requirement on `Group['haproxy']`
- Creates `/etc/haproxy` as a `0755` directory owned by `root:haproxy`.
- Creates `/etc/haproxy/conf.d` as a `0755` directory owned by `root:haproxy`.
- Creates `/var/lib/haproxy` as a `0750` directory owned by `haproxy:haproxy`.
- Evaluates `profile_haproxy::selinux_enabled`, defaulting to `false`.
- When SELinux is enabled, creates `exec['haproxy_selinux_connect']`:
  - Command: `setsebool -P haproxy_connect_any 1`
  - Guard: `getsebool haproxy_connect_any | grep -q on`
  - Search path: `/usr/sbin`, `/usr/bin`, `/sbin`, `/bin`
  - Requirement: `Package['haproxy']`

### 5. `profile_haproxy::config` (`site-modules/profile_haproxy/manifests/config.pp`)

- Creates `/etc/haproxy/haproxy.cfg`:
  - Owner/group: `root:haproxy`
  - Mode: `0640`
  - Template: `site-modules/profile_haproxy/templates/haproxy.cfg.erb`
  - Render count: `1`
  - Notifies `Class['profile_haproxy::service']`
- Iterates over `$profile_haproxy::backends`.
- Default iterations:
  - `webservers`
  - `api`
- `haproxy_prod_fra` iterations:
  - `webservers`
  - `api`
  - `internal_monitoring`
- Creates `/etc/haproxy/conf.d/webservers.cfg` from `backend.conf.epp` with one render:
  - Balance: `roundrobin`
  - Port: `8080`
  - Health check: `httpchk GET /health`
  - Interval: `5s`
  - Servers: `web1`, `web2`, and `web3`
  - Each server has weight `100`.
  - TLS follows the effective environment and cluster value.
  - Notifies `Class['profile_haproxy::service']`.
- Creates `/etc/haproxy/conf.d/api.cfg` from `backend.conf.epp` with one render:
  - Balance: `leastconn`
  - Port: `3000`
  - Health check: `httpchk GET /api/health`
  - Interval: `10s`
  - Servers: `api1` and `api2`
  - Each server has weight `100`.
  - TLS follows the effective environment and cluster value.
  - Notifies `Class['profile_haproxy::service']`.
- Creates `/etc/haproxy/conf.d/internal_monitoring.cfg` only for `haproxy_prod_fra`, from `backend.conf.epp` with one render:
  - Balance: `roundrobin`
  - Port: `9090`
  - Health check: `httpchk GET /-/healthy`
  - Interval: `15s`
  - Server: `prom1-fra` with weight `100`
  - TLS follows the effective environment and cluster value.
  - Notifies `Class['profile_haproxy::service']`.
- Iterates over error-page names `503` and `408`:
  - Creates `/etc/haproxy/errors/503.http` from `haproxy_errors/503.http`.
  - Creates `/etc/haproxy/errors/408.http` from `haproxy_errors/408.http`.
  - Both files are owned by `root:haproxy` and mode `0644`.
- Creates `/etc/haproxy/errors` as a `0755` directory owned by `root:haproxy`.
- When `profile_haproxy::stick_table_enabled` is `true`, creates `/etc/haproxy/conf.d/stick-tables.cfg`:
  - Owner/group: `root:haproxy`
  - Mode: `0640`
  - Size: `200k`
  - Expiration: `30m`
  - Notifies `Class['profile_haproxy::service']`
- Production enables the stick table; staging disables it.

### 6. `profile_haproxy::service` (`site-modules/profile_haproxy/manifests/service.pp`)

- Creates `/etc/systemd/system/haproxy.service.d` as a `0755` root-owned directory.
- Creates `/etc/systemd/system/haproxy.service.d/override.conf` as a root-owned `0644` file.
- The systemd override clears the packaged start command and starts HAProxy with:
  - `/usr/sbin/haproxy -Ws`
  - Main configuration `/etc/haproxy/haproxy.cfg`
  - Fragment directory `/etc/haproxy/conf.d/`
  - PID file `/run/haproxy.pid`
  - Master socket `/run/haproxy-master.sock`
- The override refreshes `exec['haproxy_systemd_reload']`.
- `exec['haproxy_systemd_reload']` runs `systemctl daemon-reload` and is refresh-only.
- Manages `Service['haproxy']` with:
  - `ensure => running`
  - `enable => true`
  - `hasrestart => true`
  - `hasstatus => true`
  - Requirements on `Package['haproxy']` and `Exec['haproxy_systemd_reload']`
- Creates refresh-only `exec['haproxy_config_check']`:
  - Command: `haproxy -c -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d/`
  - Search path: `/usr/sbin`, `/usr/bin`, `/sbin`, `/bin`
  - Subscribes to the main configuration.
  - Runs before `Service['haproxy']`.
- The service subscribes to `/etc/haproxy/haproxy.cfg`.
- Creates `/etc/logrotate.d/haproxy` as a root-owned `0644` file.
- Logrotate rotates `/var/log/haproxy/*.log` daily, keeps 14 files, compresses with delayed compression, and uses shared scripts.
- Post-rotate command:
  ```shell
  /bin/kill -HUP $(cat /var/run/haproxy.pid 2>/dev/null) 2>/dev/null || true
  ```

### 7. `profile_haproxy::firewall` (`site-modules/profile_haproxy/manifests/firewall.pp`)

- Evaluates `base_utils::normalize_port(9000)`.
- The normalized value has no resource effect in the supplied branches.
- The effective provider is `none`; therefore no firewall resources are created by default.
- With `firewalld`, creates:
  - `firewalld_allow_80` for TCP port `80`.
  - `firewalld_allow_443` for TCP port `443`.
  - `firewalld_allow_stats_9000` for TCP port `9000` when statistics are enabled.
  - `firewalld_reload`, refresh-only, after firewall changes.
- With `ufw`, installs `ufw` and creates:
  - `ufw_allow_http` for TCP port `80`.
  - `ufw_allow_https` for TCP port `443`.
  - `ufw_allow_stats` for TCP port `9000` when statistics are enabled.
  - `ufw_enable` to enable UFW.
- With an unknown provider, creates a notification identifying the provider value.

### 8. `profile_haproxy::discover` (`site-modules/profile_haproxy/manifests/discover.pp`)

- Executes only when `profile_haproxy::discovery_enabled` is explicitly `true`.
- Exports `haproxy::balancermember` for the local host:
  - Resource title: `$facts['networking']['fqdn']`
  - `listening_service`: `webservers`
  - `server_names`: local FQDN
  - `ipaddresses`: local networking IP
  - `ports`: `8080`
  - `options`: `check`
- Collects all exported `Haproxy::Balancermember` resources where `listening_service == 'webservers'`.
- Queries PuppetDB for `Profile::App_server` resources whose `Profile::Base` environment matches `$facts['puppet_environment']`.
- Iterates over the returned `$app_servers` results.
- For each result, creates `haproxy::balancermember[api-<certname>]` with:
  - `listening_service`: `api`
  - `server_names`: `<certname>`
  - `ipaddresses`: `<certname>`
  - `ports`: PuppetDB `parameters['port']`
  - `options`: `check inter 10s`
- The number of discovery iterations cannot be resolved statically.
- Ansible should replace this with inventory groups, discovered service facts, a service registry, or an explicit backend-server list.

### Resource Summary

- `site-modules/profile_haproxy/manifests/install.pp`
  - Unconditional: HAProxy package, group, user, three directories.
  - Conditional: extra packages and SELinux `exec`.
- `site-modules/profile_haproxy/manifests/config.pp`
  - Unconditional: one main configuration, two error files, and the error directory.
  - Backend loop: two files by default; three in `haproxy_prod_fra`.
  - Conditional: one stick-table file in production.
- `site-modules/profile_haproxy/manifests/service.pp`
  - Systemd drop-in directory, override file, daemon reload, service, configuration check, and logrotate file.
- `site-modules/profile_haproxy/manifests/firewall.pp`
  - No resources for the effective `none` provider.
  - Firewalld and UFW resources are conditional on the selected provider.
- `site-modules/profile_haproxy/manifests/discover.pp`
  - Disabled by default.
  - When enabled, creates one local exported resource, collects matching webserver resources, and creates one API resource per PuppetDB result.

## Variables

**Variable Flow Summary**: 32 mapped HAProxy parameters: 24 core settings and 8 conditional or feature settings. Values are resolved through a 21-level Hiera hierarchy. The `backends` hash uses deep merging.

### Variable Definitions

#### `site-modules/profile_haproxy/data/common.yaml` — module defaults

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
- `profile_haproxy::stats_password`: encrypted EYAML value (type: string; secret)
- `profile_haproxy::global_maxconn`: `4096` (type: integer)
- `profile_haproxy::client_timeout`: `30s` (type: string)
- `profile_haproxy::server_timeout`: `30s` (type: string)
- `profile_haproxy::connect_timeout`: `5s` (type: string)
- `profile_haproxy::retries`: `3` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (type: string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (type: string; sensitive path)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (type: string)
- `profile_haproxy::log_server`: `127.0.0.1` (type: string)
- `profile_haproxy::log_facility`: `local0` (type: string)
- `profile_haproxy::log_level`: `info` (type: string)
- `profile_haproxy::backends`: hash containing `webservers` and `api` (type: hash)
- `profile_haproxy::discovery_enabled`: `false` (type: boolean)
- `profile_haproxy::extra_packages`: `[]` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)
- `profile_haproxy::firewall_provider`: `ufw` before repository override (type: string)

#### `data/common.yaml` — repository common overrides

- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::stats_password`: `test-haproxy-password` (type: string; sensitive test value)
- `profile_haproxy::firewall_provider`: `none` (type: string)
- `profile_haproxy::extra_packages`: `[]` (type: array)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

The test password must not be migrated as production plaintext. Store the production value in Ansible Vault.

#### `site-modules/profile_haproxy/data/environment/production.yaml` — production overrides

- `profile_haproxy::global_maxconn`: `16384` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `warning` (type: string)
- `profile_haproxy::client_timeout`: `60s` (type: string)
- `profile_haproxy::server_timeout`: `60s` (type: string)
- `profile_haproxy::stats_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `200k` (type: string)
- `profile_haproxy::stick_table_expire`: `30m` (type: string)

#### `site-modules/profile_haproxy/data/environment/staging.yaml` — staging overrides

- `profile_haproxy::global_maxconn`: `2048` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

#### `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml` — Frankfurt production overrides

- `profile_haproxy::global_maxconn`: `32768` (type: integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (type: string)
- `profile_haproxy::backends`: deep-merged hash adding `internal_monitoring` (type: hash)

#### Hiera hierarchy

`site-modules/profile_haproxy/hiera.yaml` defines the following order, from highest priority to lowest:

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

The backend lookup explicitly uses `profile_haproxy::backends` with `deep` merge.

### Ansible Variable Mapping

- `profile_haproxy::package_name` → `haproxy_package_name`
- `profile_haproxy::config_dir` → `haproxy_config_dir`
- `profile_haproxy::config_file` → `haproxy_config_file`
- `profile_haproxy::service_name` → `haproxy_service_name`
- `profile_haproxy::user` → `haproxy_user`
- `profile_haproxy::group` → `haproxy_group`
- `profile_haproxy::stats_enabled` → `haproxy_stats_enabled`
- `profile_haproxy::stats_port` → `haproxy_stats_port`
- `profile_haproxy::stats_uri` → `haproxy_stats_uri`
- `profile_haproxy::stats_user` → `haproxy_stats_user`
- `profile_haproxy::stats_password` → vaulted `haproxy_stats_password`
- `profile_haproxy::global_maxconn` → `haproxy_global_maxconn`
- `profile_haproxy::client_timeout` → `haproxy_client_timeout`
- `profile_haproxy::server_timeout` → `haproxy_server_timeout`
- `profile_haproxy::connect_timeout` → `haproxy_connect_timeout`
- `profile_haproxy::retries` → `haproxy_retries`
- `profile_haproxy::ssl_enabled` → `haproxy_ssl_enabled`
- `profile_haproxy::ssl_cert_path` → `haproxy_ssl_cert_path`
- `profile_haproxy::ssl_key_path` → `haproxy_ssl_key_path`
- `profile_haproxy::ssl_ciphers` → `haproxy_ssl_ciphers`
- `profile_haproxy::ssl_min_version` → `haproxy_ssl_min_version`
- `profile_haproxy::log_server` → `haproxy_log_server`
- `profile_haproxy::log_facility` → `haproxy_log_facility`
- `profile_haproxy::log_level` → `haproxy_log_level`
- `profile_haproxy::backends` → `haproxy_backends`
- `profile_haproxy::discovery_enabled` → `haproxy_discovery_enabled`
- `profile_haproxy::extra_packages` → `haproxy_extra_packages`
- `profile_haproxy::selinux_enabled` → `haproxy_selinux_enabled`
- `profile_haproxy::firewall_provider` → `haproxy_firewall_provider`
- `profile_haproxy::stick_table_enabled` → `haproxy_stick_table_enabled`
- `profile_haproxy::stick_table_size` → `haproxy_stick_table_size`
- `profile_haproxy::stick_table_expire` → `haproxy_stick_table_expire`

### Variable Migration Summary

- **Core settings**: 24 variables covering package, paths, service identity, statistics, limits, timeouts, TLS, logging, and backends.
- **Conditional settings**: 8 variables covering discovery, extra packages, SELinux, firewall, and stick tables.
- **Common defaults**: 28 primary settings plus conditional defaults from module and repository common data.
- **Environment-specific variables**: 9 production settings and 5 staging settings.
- **Cluster-specific variables**: 4 Frankfurt production overrides.
- **Deep-merged structures**: 1, `profile_haproxy::backends`.
- **Encrypted variables**: 1 statistics password.
- **Sensitive paths**: TLS certificate and private-key paths.
- **Repository overrides**: package name, statistics password, firewall provider, extra packages, SSL default, and stick-table default.

### Cross-Level Overrides

- `profile_haproxy::package_name`: module common and repository common; first/highest-priority applicable value wins.
- `profile_haproxy::stats_password`: encrypted module common and repository common; the supplied test context resolves to `test-haproxy-password`, but production must use Ansible Vault.
- `profile_haproxy::ssl_enabled`: module common `false`, repository common `false`, production `true`, staging `false`.
- `profile_haproxy::global_maxconn`: module common `4096`, production `16384`, staging `2048`, Frankfurt production `32768`.
- `profile_haproxy::log_level`: module common `info`, production `warning`, staging `debug`.
- `profile_haproxy::backends`: module common defines `webservers` and `api`; Frankfurt production deep-merges `internal_monitoring`.
- `profile_haproxy::firewall_provider`: manifest default `ufw`, repository common overrides it to `none`.
- `profile_haproxy::stick_table_enabled`: repository common defaults to `false`; production overrides it to `true`.

### Merge Strategy Notes

- `deep` merge is used for `profile_haproxy::backends`; nested backend hashes are recursively combined.
- `first` lookup behavior applies to ordinary scalar values; the highest-priority applicable Hiera value wins.
- Empty arrays such as `profile_haproxy::extra_packages` remain empty unless overridden at a higher-priority level.

## Custom Types and Providers

### Custom fact: `haproxy_version`

- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Scope: Linux only.
- Command: `haproxy -v 2>/dev/null`
- Behavior: Extracts the first semantic version following the word `version`.
- Returns `nil` when HAProxy is unavailable or output does not match.
- Ansible equivalent: create `/etc/ansible/facts.d/haproxy_version.fact`, or run `haproxy -v` with `ansible.builtin.command` and parse the output.
- The fact is not consumed by the supplied manifests or templates.

## Dependencies

**External Puppet module dependencies**:

- `puppetlabs-stdlib` `9.7.0`
- `puppetlabs-concat` `9.0.2`
- `puppetlabs-firewall` `8.1.3`

**Additional referenced dependency**:

- `base_utils::normalize_port()`, called by `profile_haproxy::firewall`.
- Its implementation is not included.
- Its result does not affect the effective `firewall_provider: none` path.

**System package dependencies**:

- `haproxy`
- `ufw` only when `haproxy_firewall_provider` is `ufw`
- Packages listed in `haproxy_extra_packages`, currently none

**Service dependencies**:

- HAProxy package before the HAProxy service.
- Systemd drop-in directory before `override.conf`.
- `override.conf` refreshes `systemctl daemon-reload`.
- HAProxy configuration validation before the service.
- Configuration changes notify or subscribe the HAProxy service.
- Installation before configuration.
- Configuration before service.
- Discovery, when enabled, after configuration and before service refresh.

## Puppet Facts Used

- `$facts['kernel']`: Determines whether `role::haproxy` executes its Linux-only conditional.
- `$facts['networking']['fqdn']`: Titles and names the exported local webserver balancer member.
- `$facts['networking']['ip']`: Supplies the exported local balancer member IP address.
- `$facts['puppet_environment']`: Restricts the PuppetDB application-server query.
- `$facts.architecture`: Selects the architecture Hiera level.
- `$facts.os.name`: Selects the OS release Hiera level.
- `$facts.os.release.full`: Selects the full OS release Hiera level.
- `$facts.os.family`: Selects the OS-family Hiera level.
- `$facts.os.release.major`: Selects the OS-family-and-major-release Hiera level.
- `$facts.is_virtual`: Selects the `is_container` Hiera level.
- `$facts.virtual`: Selects the `virtual` Hiera level.

## Template Conversion Notes

### `site-modules/profile_haproxy/templates/haproxy.cfg.erb`

- Render count: `1`.
- Uses approximately 21 variables.
- Uses approximately 4 logic blocks.
- Convert to a Jinja2 template using:
  - `haproxy_global_maxconn` for global connection limits.
  - `haproxy_client_timeout`, `haproxy_server_timeout`, and `haproxy_connect_timeout` for timeout directives.
  - `haproxy_retries` for retry behavior.
  - `haproxy_log_server`, `haproxy_log_facility`, and `haproxy_log_level` for logging.
  - `haproxy_ssl_enabled`, `haproxy_ssl_cert_path`, `haproxy_ssl_key_path`, `haproxy_ssl_ciphers`, and `haproxy_ssl_min_version` for conditional TLS listeners.
  - `haproxy_stats_enabled`, `haproxy_stats_port`, `haproxy_stats_uri`, `haproxy_stats_user`, and vaulted `haproxy_stats_password` for the optional statistics listener.
  - `haproxy_backends` to reference the generated backend fragments.
- Implement TLS and statistics blocks with Jinja2 conditionals.
- Render environment and cluster-specific values through normal Ansible variable precedence.

### `site-modules/profile_haproxy/templates/backend.conf.epp`

- Render count: one per backend.
- Default render count: `2`.
- `haproxy_prod_fra` render count: `3`.
- Uses approximately 11 variables and 4 logic blocks.
- Convert to a Jinja2 template receiving:
  - Backend name.
  - Balance method.
  - Backend port.
  - Health-check string.
  - Health-check interval.
  - TLS enabled state.
  - Server list.
- Iterate over the named server list to render `web1`, `web2`, `web3`, `api1`, `api2`, or `prom1-fra`.
- Use conditionals for TLS server options, health checks, and optional backend settings.
- Preserve server names, addresses, ports, and weights exactly.

### Stick-table configuration

- Replace the conditional Puppet file resource with an Ansible template or copy task.
- Create it only when `haproxy_stick_table_enabled` is true.
- Render:
  ```text
  # Managed by Puppet
  stick-table type 200k size 200k expire 30m
  ```
- Preserve the effective Puppet content semantics: `stick-table type ip size 200k expire 30m`.

## PuppetDB Dependencies

**Context**: PuppetDB provides cross-node resource sharing, node facts, and infrastructure queries.

- **Exported Resources**:
  - Exports `haproxy::balancermember[<local FQDN>]`.
  - The exported member represents a local webserver on port `8080`.
  - Migration: replace cross-node exported-resource sharing with an Ansible inventory group or an explicit service-discovery source.

- **Resource Collectors**:
  - Collects `Haproxy::Balancermember` resources where `listening_service == 'webservers'`.
  - Migration: build the `webservers` backend from inventory or discovered host variables.

- **PuppetDB Queries**:
  - Query selects `Profile::App_server` resources whose `Profile::Base` environment equals `$facts['puppet_environment']`.
  - Returned `certname` and `parameters['port']` values are used to create API balancer members.
  - Migration: replace with inventory host variables, a service registry, or explicit `haproxy_backends` data.

- **Host Identity Data**:
  - Local FQDN and IP facts identify the exported webserver member.
  - Puppet environment provides query classification.
  - Migration: use Ansible `inventory_hostname`, `ansible_fqdn`, `ansible_host`, group membership, and environment variables.

## Checks for the Migration

**Files to verify**:

- `site-modules/role/manifests/haproxy.pp`
- `site-modules/profile/manifests/loadbalancer/haproxy.pp`
- `site-modules/profile_haproxy/manifests/init.pp`
- `site-modules/profile_haproxy/manifests/install.pp`
- `site-modules/profile_haproxy/manifests/config.pp`
- `site-modules/profile_haproxy/manifests/service.pp`
- `site-modules/profile_haproxy/manifests/firewall.pp`
- `site-modules/profile_haproxy/manifests/discover.pp`
- `site-modules/profile_haproxy/templates/haproxy.cfg.erb`
- `site-modules/profile_haproxy/templates/backend.conf.epp`
- `site-modules/profile_haproxy/files/haproxy_errors/503.http`
- `site-modules/profile_haproxy/files/haproxy_errors/408.http`
- `site-modules/profile_haproxy/hiera.yaml`
- `site-modules/profile_haproxy/data/common.yaml`
- `site-modules/profile_haproxy/data/environment/production.yaml`
- `site-modules/profile_haproxy/data/environment/staging.yaml`
- `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml`
- `data/common.yaml`
- `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- `/etc/haproxy/haproxy.cfg`
- `/etc/haproxy/conf.d/webservers.cfg`
-