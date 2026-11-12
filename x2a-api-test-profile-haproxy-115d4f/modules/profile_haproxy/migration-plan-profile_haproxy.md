---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: `profile_haproxy` manages HAProxy on Linux by installing the `haproxy` package, creating the HAProxy user, group, directories, configuration, systemd override, log rotation, and service resources. For `lb01.fra.example.com`, the effective configuration disables SSL, firewall management, extra packages, stick tables, and PuppetDB discovery; enables the statistics interface on port `9001`; uses production logging and timeout settings; and renders the `webservers`, `api`, and `internal_monitoring` backends. The HAProxy statistics password must be migrated to Ansible Vault or an external secret manager rather than using the plaintext test override.

## Service Type and Instances

**Service Type**: Load balancer / reverse proxy

**Configured Instances**:

- **HAProxy service**
  - Service name: `haproxy`
  - Package: `haproxy`
  - Configuration directory: `/etc/haproxy`
  - Main configuration: `/etc/haproxy/haproxy.cfg`
  - Backend configuration directory: `/etc/haproxy/conf.d`
  - Error directory: `/etc/haproxy/errors`
  - Runtime directory: `/var/lib/haproxy`
  - User: `haproxy`
  - Group: `haproxy`
  - Effective state: running

- **Statistics interface**
  - Enabled for `lb01.fra.example.com`: `true`
  - Listen port: `9001`
  - URI: `/haproxy-stats`
  - User: `admin`
  - Password: sensitive; migrate through Ansible Vault or an external secret manager
  - Plaintext value `test-haproxy-password` is test data and must not be promoted to production

- **Backend `webservers`**
  - Balance algorithm: `roundrobin`
  - Port: `8080`
  - Health check: `httpchk GET /health`
  - Health interval: `5s`
  - Servers:
    - `web1-fra`: `10.100.1.10`, weight `100`
    - `web2-fra`: `10.100.1.11`, weight `100`
    - `web3-fra`: `10.100.1.12`, weight `100`

- **Backend `api`**
  - Balance algorithm: `leastconn`
  - Port: `3000`
  - Health check: `httpchk GET /api/health`
  - Health interval: `10s`
  - Servers:
    - `api1-fra`: `10.100.2.10`, weight `200`
    - `api2-fra`: `10.100.2.11`, weight `100`

- **Backend `internal_monitoring`**
  - Balance algorithm: `roundrobin`
  - Port: `9090`
  - Health check: `httpchk GET /-/healthy`
  - Health interval: `15s`
  - Servers:
    - `prom1-fra`: `10.100.3.10`, weight `100`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
### Manifests

- `site-modules/role/manifests/haproxy.pp`
- `site-modules/profile/manifests/loadbalancer/haproxy.pp`
- `site-modules/profile_haproxy/manifests/init.pp`
- `site-modules/profile_haproxy/manifests/install.pp`
- `site-modules/profile_haproxy/manifests/config.pp`
- `site-modules/profile_haproxy/manifests/service.pp`
- `site-modules/profile_haproxy/manifests/firewall.pp`
- `site-modules/profile_haproxy/manifests/discover.pp`

### Templates

- `site-modules/profile_haproxy/templates/haproxy.cfg.erb`
- `site-modules/profile_haproxy/templates/backend.conf.epp`

### Hiera data

- `site-modules/profile_haproxy/data/common.yaml`
- `site-modules/profile_haproxy/data/os/Debian.yaml`
- `site-modules/profile_haproxy/data/os/RedHat.yaml`
- `site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml`
- `site-modules/profile_haproxy/data/environment/production.yaml`
- `site-modules/profile_haproxy/data/environment/staging.yaml`
- `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml`
- `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml`
- `data/common.yaml`
- `site-modules/profile_haproxy/hiera.yaml`

### Custom components

- `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
```

The supplied analysis reports 45 analyzed files, while the preserved inventory identifies 21 files. The remaining 24 files are not individually named in the supplied material and require inventory reconciliation. They must be classified as dependencies, unused data, generated files, or out of scope before migration sign-off.

## Module Explanation

The module performs operations in this order:

1. **`role::haproxy`** (`site-modules/role/manifests/haproxy.pp`)
   - Executes the HAProxy role only when `$facts['kernel'].downcase == 'linux'`.
   - References `$facts['kernel']` and `fact('environment')`.
   - Includes `::profile::base::base` and `::profile::loadbalancer::haproxy`.
   - Contains an `exec` resource whose command and attributes are unavailable in the supplied execution-tree data and require source verification.
   - Orders `Class['::profile::base::base']` before `Class['::profile::loadbalancer::haproxy']`.

2. **`profile::loadbalancer::haproxy`** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`)
   - Includes `profile_haproxy`.
   - Acts as the HAProxy implementation entry point.
   - Runs after the base profile has completed.

3. **`profile_haproxy`** (`site-modules/profile_haproxy/manifests/init.pp`)
   - Contains `profile_haproxy::install`.
   - Contains `profile_haproxy::config`.
   - Contains `profile_haproxy::service`.
   - Contains `profile_haproxy::firewall`.
   - Does not evaluate `profile_haproxy::discover` because effective `discovery_enabled` is `false`.
   - Orders installation before configuration and refreshes the service after configuration:
     `Class['profile_haproxy::install'] -> Class['profile_haproxy::config'] ~> Class['profile_haproxy::service']`.
   - The firewall class is contained, but its effective provider is `none`, so no firewall resources are created.

4. **`profile_haproxy::install`** (`site-modules/profile_haproxy/manifests/install.pp`)
   - Installs package `haproxy` with `ensure => present`.
   - Creates group `haproxy`.
   - Creates user `haproxy`.
   - Creates `/etc/haproxy`.
   - Creates `/etc/haproxy/conf.d`.
   - Creates `/var/lib/haproxy`.
   - Evaluates the extra-package loop zero times because effective `extra_packages` is `[]`.
   - Does not create `exec['haproxy_selinux_connect']` because effective `selinux_enabled` is `false` for the supplied Debian node.

5. **`profile_haproxy::config`** (`site-modules/profile_haproxy/manifests/config.pp`)
   - Creates `/etc/haproxy/errors`.
   - Creates `/etc/haproxy/errors/503.http`.
   - Creates `/etc/haproxy/errors/408.http`.
   - Renders `/etc/haproxy/haproxy.cfg` from `site-modules/profile_haproxy/templates/haproxy.cfg.erb` once.
   - Passes effective statistics, timeout, retry, logging, SSL, and backend values to the main template.
   - Iterates over `$backends.each` with exactly these names:
     - `webservers`
     - `api`
     - `internal_monitoring`
   - For `webservers`, renders `/etc/haproxy/conf.d/webservers.cfg` once from `site-modules/profile_haproxy/templates/backend.conf.epp`.
   - For `api`, renders `/etc/haproxy/conf.d/api.cfg` once from `site-modules/profile_haproxy/templates/backend.conf.epp`.
   - For `internal_monitoring`, renders `/etc/haproxy/conf.d/internal_monitoring.cfg` once from `site-modules/profile_haproxy/templates/backend.conf.epp`.
   - Does not create `/etc/haproxy/conf.d/stick-tables.cfg` because effective `stick_table_enabled` is `false`.
   - Effective main configuration values include:
     - `stats_enabled`: `true`
     - `stats_port`: `9001`
     - `stats_uri`: `/haproxy-stats`
     - `stats_user`: `admin`
     - `stats_password`: sensitive Vault value required
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
     - `log_server`: `10.100.1.50`
     - `log_facility`: `local0`
     - `log_level`: `warning`

   - **`webservers` loop iteration**
     - `balance`: `roundrobin`
     - `port`: `8080`
     - `health_check`: `httpchk GET /health`
     - `health_interval`: `5s`
     - `web1-fra`: `10.100.1.10`, weight `100`
     - `web2-fra`: `10.100.1.11`, weight `100`
     - `web3-fra`: `10.100.1.12`, weight `100`

   - **`api` loop iteration**
     - `balance`: `leastconn`
     - `port`: `3000`
     - `health_check`: `httpchk GET /api/health`
     - `health_interval`: `10s`
     - `api1-fra`: `10.100.2.10`, weight `200`
     - `api2-fra`: `10.100.2.11`, weight `100`

   - **`internal_monitoring` loop iteration**
     - `balance`: `roundrobin`
     - `port`: `9090`
     - `health_check`: `httpchk GET /-/healthy`
     - `health_interval`: `15s`
     - `prom1-fra`: `10.100.3.10`, weight `100`

6. **`profile_haproxy::service`** (`site-modules/profile_haproxy/manifests/service.pp`)
   - Creates `/etc/systemd/system/haproxy.service.d`.
   - Creates `/etc/systemd/system/haproxy.service.d/override.conf`.
   - Declares `exec['haproxy_systemd_reload']`.
   - Declares `service['haproxy']` with effective state `running`.
   - Declares `exec['haproxy_config_check']`.
   - Creates `/etc/logrotate.d/haproxy`.
   - The supplied execution-tree data confirms these resource titles but does not provide the commands or attributes for the two `exec` resources or the logrotate content. Verify those behaviors directly from source before migration.
   - Configuration changes notify the HAProxy service through the class-level refresh chain.

7. **`profile_haproxy::firewall`** (`site-modules/profile_haproxy/manifests/firewall.pp`)
   - Selects effective firewall provider `none`.
   - Creates no firewall package, rule, reload, or enable resources for `lb01.fra.example.com`.
   - Supports `firewalld` in other environments through `exec['firewalld_reload']`.
   - Supports `ufw` in other environments through package `ufw`, `exec['ufw_allow_http']`, `exec['ufw_allow_https']`, and `exec['ufw_enable']`.
   - Emits a notification for an unknown provider.

8. **`profile_haproxy::discover`** (`site-modules/profile_haproxy/manifests/discover.pp`)
   - Is not executed for the supplied node because `discovery_enabled` is `false`.
   - If enabled, exports `@@haproxy::balancermember[$facts['networking']['fqdn']]` for `webservers`.
   - If enabled, collects `Haproxy::Balancermember` resources where `listening_service == 'webservers'`.
   - If enabled, iterates over `$app_servers.each`; the supplied data does not provide a resolved list, so item expansion cannot be materialized.
   - Each resolved application-server item would create `haproxy::balancermember["api-${certname}"]`.
   - Uses `$facts['networking']['fqdn']`, `$facts['networking']['ip']`, and `$facts['puppet_environment']`.
   - Uses a PuppetDB query to discover `Profile::App_server` classes associated with `Profile::Base` resources in the local Puppet environment.

## Variables

**Variable Flow Summary**: 34 directly configured profile parameters plus optional discovery, firewall, SELinux, extra-package, stick-table, NTP, backend, and PuppetDB values across module defaults, OS, datacenter, environment, cluster, node, and control-repository levels.

The supplied material identifies the hierarchy levels and source files but does not include the exact lookup-order contents from `site-modules/profile_haproxy/hiera.yaml`. The migration must verify that file and record the exact precedence order before implementation. The effective values below reflect the supplied precedence analysis.

### Variable Definitions

#### `site-modules/profile_haproxy/data/common.yaml` — module defaults

Migration note: Base defaults for all nodes.

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (string)
- `profile_haproxy::config_file`: `/etc/haproxy/haproxy.cfg` (string)
- `profile_haproxy::service_name`: `haproxy` (string)
- `profile_haproxy::user`: `haproxy` (string)
- `profile_haproxy::group`: `haproxy` (string)
- `profile_haproxy::stats_enabled`: `true` (boolean)
- `profile_haproxy::stats_port`: `9000` (integer)
- `profile_haproxy::stats_uri`: `/haproxy-stats` (string)
- `profile_haproxy::stats_user`: `admin` (string)
- `profile_haproxy::stats_password`: EYAML-encrypted value (string)
- `profile_haproxy::global_maxconn`: `4096` (integer)
- `profile_haproxy::client_timeout`: `30s` (string)
- `profile_haproxy::server_timeout`: `30s` (string)
- `profile_haproxy::connect_timeout`: `5s` (string)
- `profile_haproxy::retries`: `3` (integer)
- `profile_haproxy::ssl_enabled`: `false` (boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (string/reference)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256` (string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (string)
- `profile_haproxy::log_server`: `127.0.0.1` (string)
- `profile_haproxy::log_facility`: `local0` (string)
- `profile_haproxy::log_level`: `info` (string)
- `profile_haproxy::backends`: deep-merged hash containing `webservers` and `api` defaults

#### `site-modules/profile_haproxy/data/os/Debian.yaml` — Debian-specific

Migration note: Debian-specific package, firewall, extra-package, and SELinux defaults.

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (string)
- `profile_haproxy::firewall_provider`: `ufw` (string)
- `profile_haproxy::extra_packages`: `[hatop]` (array)
- `profile_haproxy::selinux_enabled`: `false` (boolean)

#### `site-modules/profile_haproxy/data/os/RedHat.yaml` — RedHat-specific

Migration note: RedHat-specific firewall, package, and SELinux defaults. These values are inactive for the supplied Debian node.

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (string)
- `profile_haproxy::firewall_provider`: `firewalld` (string)
- `profile_haproxy::firewall_zone`: defined for RedHat firewall configuration (string)
- `profile_haproxy::extra_packages`: `[haproxy-systemd-wrapper, policycoreutils-python-utils]` (array)
- `profile_haproxy::selinux_enabled`: `true` (boolean)

#### `site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml` — datacenter-specific

Migration note: Frankfurt logging, NTP, and backend overrides.

- `profile_haproxy::log_server`: `10.100.1.50` (string)
- `profile_haproxy::ntp_servers`: `[ntp1.dc1.fra.example.com, ntp2.dc1.fra.example.com]` (array)
- `profile_haproxy::backends`: deep-merged hash containing Frankfurt backend server overrides

#### `site-modules/profile_haproxy/data/environment/production.yaml` — production-specific

Migration note: Production timeouts, logging, SSL, statistics, and stick-table defaults. Some values are overridden at higher-priority levels.

- `profile_haproxy::global_maxconn`: `16384` (integer)
- `profile_haproxy::ssl_enabled`: `true` (boolean)
- `profile_haproxy::log_level`: `warning` (string)
- `profile_haproxy::client_timeout`: `60s` (string)
- `profile_haproxy::server_timeout`: `60s` (string)
- `profile_haproxy::stats_enabled`: `false` (boolean)
- `profile_haproxy::stick_table_enabled`: `true` (boolean)
- `profile_haproxy::stick_table_size`: `200k` (string)
- `profile_haproxy::stick_table_expire`: `30m` (string)

#### `site-modules/profile_haproxy/data/environment/staging.yaml` — staging-specific

Migration note: Staging data is part of the migration inventory, but its variable values were not supplied and require direct source review.

- Variables and exact values: pending source verification

#### `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml` — cluster-specific

Migration note: Production Frankfurt cluster connection, TLS, and backend settings.

- `profile_haproxy::global_maxconn`: `32768` (integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384` (string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (string)
- `profile_haproxy::backends`: deep-merged hash adding `internal_monitoring`

#### `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml` — host-specific

Migration note: Host-specific statistics and API backend overrides.

- `profile_haproxy::stats_enabled`: `true` (boolean)
- `profile_haproxy::stats_port`: `9001` (integer)
- `profile_haproxy::backends`: deep-merged hash overriding the `api.servers` list

#### `data/common.yaml` — control-repository overrides

Migration note: Control-repository overrides have the effective highest priority in the supplied analysis. The password value is unsafe test data.

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::stats_password`: `test-haproxy-password` (string; plaintext test override)
- `profile_haproxy::firewall_provider`: `none` (string)
- `profile_haproxy::extra_packages`: `[]` (array)
- `profile_haproxy::ssl_enabled`: `false` (boolean)
- `profile_haproxy::stick_table_enabled`: `false` (boolean)

#### Variables referenced but not fully defined in supplied Hiera data

Migration note: These variables must be traced through manifests, templates, and all Hiera levels.

- `profile_haproxy::discovery_enabled`: effective `false` (boolean)
- `profile_haproxy::app_servers`: unresolved list when discovery is enabled (array)
- `profile_haproxy::firewall_zone`: RedHat-specific value (string)
- `profile_haproxy::ntp_servers`: datacenter-specific server list (array)
- `profile_haproxy::stick_table_size`: `200k` when production stick tables are enabled (string)
- `profile_haproxy::stick_table_expire`: `30m` when production stick tables are enabled (string)

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
- `stats_password`: Ansible Vault or external secret-manager value
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
- `log_server`: `10.100.1.50`
- `log_facility`: `local0`
- `log_level`: `warning`
- `firewall_provider`: `none`
- `extra_packages`: `[]`
- `selinux_enabled`: `false`
- `discovery_enabled`: `false`
- `stick_table_enabled`: `false`
- `backends`: deep-merged effective map containing `webservers`, `api`, and `internal_monitoring`

### Variable Migration Summary

- **Common defaults**: 25 primary profile values plus backend defaults from `site-modules/profile_haproxy/data/common.yaml`
- **OS-specific variables**: package name, configuration path, firewall provider, firewall zone, extra packages, and SELinux behavior
- **Environment-specific variables**: production and staging timeout, logging, SSL, statistics, and stick-table values
- **Datacenter-specific variables**: logging destination, NTP servers, and backend addresses
- **Cluster-specific variables**: connection limit, TLS settings, and additional backend
- **Host-specific variables**: statistics port/state and API backend server list
- **Control-repository overrides**: 6 keys
- **Discovery/PuppetDB variables**: discovery enablement, application-server list, and PuppetDB environment selection
- **Encrypted variables**: 1 direct credential, `profile_haproxy::stats_password`
- **Sensitive file references**: `profile_haproxy::ssl_key_path`

### Cross-Level Overrides

- `profile_haproxy::package_name`: common, OS, and control repository; scalar first/highest-priority value; effective `haproxy`
- `profile_haproxy::stats_enabled`: common `true`, production `false`, node `true`; effective `true`
- `profile_haproxy::stats_port`: common `9000`, node `9001`; effective `9001`
- `profile_haproxy::global_maxconn`: common `4096`, production `16384`, cluster `32768`; effective `32768`
- `profile_haproxy::ssl_enabled`: common `false`, production `true`, control repository `false`; effective `false`
- `profile_haproxy::ssl_ciphers`: common AES128 list, cluster AES256 list; effective cluster AES256 list
- `profile_haproxy::ssl_min_version`: common `TLSv1.2`, cluster `TLSv1.3`; effective `TLSv1.3`
- `profile_haproxy::log_level`: common `info`, production `warning`; effective `warning`
- `profile_haproxy::client_timeout`: common `30s`, production `60s`; effective `60s`
- `profile_haproxy::server_timeout`: common `30s`, production `60s`; effective `60s`
- `profile_haproxy::log_server`: common `127.0.0.1`, datacenter `10.100.1.50`; effective `10.100.1.50`
- `profile_haproxy::backends`: deep merge across common, datacenter, cluster, and node levels; the node-level `api.servers` list is effective
- `profile_haproxy::stats_password`: EYAML-encrypted module value and plaintext control-repository value; the control-repository value wins in the supplied hierarchy but must be replaced with Vault storage
- `profile_haproxy::firewall_provider`: Debian `ufw`, RedHat `firewalld`, control repository `none`; effective `none`
- `profile_haproxy::extra_packages`: Debian `[hatop]`, RedHat `[haproxy-systemd-wrapper, policycoreutils-python-utils]`, control repository `[]`; effective empty
- `profile_haproxy::stick_table_enabled`: production `true`, control repository `false`; effective `false`

### Merge Strategy Notes

- Variables using `hash` merge combine hash values from multiple levels using a shallow merge.
- Variables using `deep` merge recursively combine nested hash values.
- Variables using `first` or the default scalar behavior use the first value found at the highest-priority hierarchy level.
- `profile_haproxy::backends` uses deep merge; the effective host-level `api.servers` list replaces the inherited list rather than concatenating it.
- The exact precedence order must be confirmed from `site-modules/profile_haproxy/hiera.yaml`.

## Custom Types and Providers

### Custom fact: `haproxy_version`

- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Platform: Linux only
- Intended command: `haproxy -v 2>/dev/null`
- Intended behavior: extract the first semantic version after the word `version`
- Returns `nil` when HAProxy is unavailable or output does not match
- The supplied structured summary does not include a custom-fact analysis; these implementation details are source-derived and require verification.
- Ansible equivalent:
  - Run `haproxy -v` with `ansible.builtin.command`
  - Parse the version with a regular expression
  - Alternatively install `/etc/ansible/facts.d/haproxy_version.fact`

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.7.0`
- `puppetlabs-concat` `9.0.2`
- `puppetlabs-firewall` `8.1.3`

These versions are supplied by the migration data and require verification against `Puppetfile` or `metadata.json`.

**System package dependencies**:

- `haproxy`
- No extra packages for the supplied node because `extra_packages` is `[]`
- `ufw` is not installed because firewall management is `none`

**Service dependencies**:

- Base profile completes before `profile::loadbalancer::haproxy`
- `profile_haproxy::install` precedes `profile_haproxy::config`
- `profile_haproxy::config` refreshes `profile_haproxy::service`
- If discovery is enabled: `install -> config -> discover ~> service`

## Puppet Facts Used

- `$facts['kernel']`
  - Provides the operating-system kernel name.
  - Restricts HAProxy role execution to Linux.

- `fact('environment')`
  - Provides the Puppet environment name.
  - Is referenced by the load-balancer profile chain.

- `$facts['networking']['fqdn']`
  - Provides the local fully qualified hostname.
  - Becomes the exported balancermember title and server name when discovery is enabled.

- `$facts['networking']['ip']`
  - Provides the local primary IP address.
  - Becomes the exported balancermember address when discovery is enabled.

- `$facts['puppet_environment']`
  - Provides the Puppet environment identifier.
  - Is used in the PuppetDB application-server query.

- `haproxy_version`
  - Custom Linux fact for the installed HAProxy semantic version.
  - Availability and implementation require source verification.

## Template Conversion Notes

### `profile_haproxy/haproxy.cfg.erb`

- Source: `site-modules/profile_haproxy/templates/haproxy.cfg.erb`
- Destination: `/etc/haproxy/haproxy.cfg`
- Render count: `1`
- Supplied scan: 21 variables and 5 Ruby logic blocks
- Convert ERB conditionals to Jinja2 conditionals.
- Preserve conditional rendering for statistics and SSL.
- Effective values include:
  - `global_maxconn`: `32768`
  - `client_timeout`: `60s`
  - `server_timeout`: `60s`
  - `connect_timeout`: `5s`
  - `retries`: `3`
  - `log_server`: `10.100.1.50`
  - `log_facility`: `local0`
  - `log_level`: `warning`
  - Statistics enabled on port `9001` with URI `/haproxy-stats`
  - SSL disabled
- TLS variables remain available but must not render an active TLS listener while `ssl_enabled` is `false`.
- Pass the statistics password from Ansible Vault and use `no_log: true` for secret-handling tasks.

### `profile_haproxy/backend.conf.epp`

- Source: `site-modules/profile_haproxy/templates/backend.conf.epp`
- Destination pattern: `/etc/haproxy/conf.d/<backend_name>.cfg`
- Render count: `3`
- Rendered names:
  - `webservers`
  - `api`
  - `internal_monitoring`
- Supplied scan: 11 variables and 6 EPP logic blocks
- Convert EPP conditionals and server iterations to Jinja2.
- Preserve backend name, balance algorithm, port, health-check expression, health interval, server name, address, and weight.
- Preserve the effective deep-merge result before rendering; do not independently merge server arrays in the template.

## PuppetDB Dependencies

**Context**: PuppetDB is used only by the optional discovery path, which is disabled for `lb01.fra.example.com`.

- **Exported Resources** (`@@`)
  - Resource type: `haproxy::balancermember`
  - Title: `$facts['networking']['fqdn']`
  - Exported values:
    - `listening_service`: `webservers`
    - `server_names`: local FQDN
    - `ipaddresses`: local networking IP
    - `ports`: `8080`
    - `options`: `check`
  - Active only when `discovery_enabled` is `true`.
  - Migration note: replace cross-node exported resources with inventory-driven backend membership or an explicit registration workflow.

- **Resource Collectors** (`<<| |>>`)
  - Collector: `Haproxy::Balancermember <| listening_service == 'webservers' |>`
  - Active only when discovery is enabled.
  - Migration note: Ansible requires an inventory, generated host variables, or another explicit source of discovered backend members.

- **PuppetDB Queries**
  - Query:
    `resources[certname, parameters] { type = 'Class' and title = 'Profile::App_server' and certname in resources[certname] { type = 'Class' and title = 'Profile::Base' and parameters.environment = '${facts['puppet_environment']}' } }`
  - Returned data: application-server class resources associated with base-profile resources in the local Puppet environment.
  - Migration note: query PuppetDB explicitly with `ansible.builtin.uri` only if PuppetDB compatibility is required; transform results into backend variables before rendering.

- **Host Identity Data**
  - `$facts['networking']['fqdn']`: local host identity and exported resource title.
  - `$facts['networking']['ip']`: local host address for exported membership.
  - `$facts['puppet_environment']`: environment selector for node discovery.
  - Current behavior: no exported resource, collector, or PuppetDB query executes because `discovery_enabled` is `false`.

## Credential Handling

- **`profile_haproxy::stats_password`**
  - Used for HAProxy statistics authentication.
  - Module defaults contain an EYAML-encrypted value.
  - Control-repository data contains plaintext `test-haproxy-password`.
  - Store the production value in Ansible Vault or an external secret manager.
  - Do not place the value in plaintext `group_vars/all.yml`.
  - Use `no_log: true` for tasks that read, template, or handle the secret.

- **`profile_haproxy::ssl_key_path`**
  - References `/etc/ssl/private`.
  - Private key material is not present in the supplied scan.
  - If TLS is enabled later, deploy the key with restrictive ownership and mode, such as `0600`.
  - Keep private key material in Vault or an external secret provider.

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
- `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- `site-modules/profile_haproxy/data/common.yaml`
- `site-modules/profile_haproxy/data/os/Debian.yaml`
- `site-modules/profile_haproxy/data/os/RedHat.yaml`
- `site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml`
- `site-modules/profile_haproxy/data/environment/production.yaml`
- `site-modules/profile_haproxy/data/environment/staging.yaml`
- `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml`
- `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml`
- `data/common.yaml`
- `site