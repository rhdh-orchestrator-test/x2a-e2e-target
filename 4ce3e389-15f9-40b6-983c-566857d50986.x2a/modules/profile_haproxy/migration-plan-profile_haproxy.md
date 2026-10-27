---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: `profile_haproxy` installs and configures HAProxy as a Layer-7 load balancer on `lb01.fra.example.com`. The effective configuration uses package and service `haproxy`, configuration under `/etc/haproxy`, statistics on port `9001`, TLS disabled, firewall management disabled, and three backends: `webservers`, `api`, and `internal_monitoring`. Backend hashes are recursively merged, while the host-level `api.servers` list replaces the inherited list. Discovery is disabled. The Ansible migration should store the statistics password in Vault as `vault_haproxy_stats_password`.

## Service Type and Instances

**Service Type**: Layer-7 load balancer / reverse proxy

**Configured Instances**:

- **HAProxy service**
  - Package: `haproxy`
  - Service: `haproxy`
  - Configuration: `/etc/haproxy/haproxy.cfg`
  - Configuration directory: `/etc/haproxy`
  - Runtime user: `haproxy`
  - Runtime group: `haproxy`

- **HAProxy statistics endpoint**
  - Enabled: `true`
  - Port: `9001`
  - URI: `/haproxy-stats`
  - Username: `admin`
  - Password: control-repository override present; migrate to Vault variable `vault_haproxy_stats_password`

- **`webservers` backend**
  - Balance algorithm: `roundrobin`
  - Port: `8080`
  - Health check: `httpchk GET /health`
  - Health interval: `5s`
  - Servers:
    - `web1`: `10.0.1.10`, weight `100`
    - `web2`: `10.0.1.11`, weight `100`
    - `web3`: `10.0.1.12`, weight `100`

- **`api` backend**
  - Balance algorithm: `leastconn`
  - Port: `3000`
  - Health check: `httpchk GET /api/health`
  - Health interval: `10s`
  - Host-level server list replaces the inherited list:
    - `api1-fra`: `10.100.2.10`, weight `200`
    - `api2-fra`: `10.100.2.11`, weight `100`

- **`internal_monitoring` backend**
  - Balance algorithm: `roundrobin`
  - Port: `9090`
  - Health check: `httpchk GET /-/healthy`
  - Health interval: `15s`
  - Servers:
    - `prom1-fra`: `10.100.3.10`, weight `100`

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

site-modules/profile_haproxy/data/common.yaml
site-modules/profile_haproxy/data/os/Debian.yaml
site-modules/profile_haproxy/data/os/RedHat.yaml
site-modules/profile_haproxy/data/environment/production.yaml
site-modules/profile_haproxy/data/environment/staging.yaml
site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml
site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml
data/common.yaml

site-modules/profile_haproxy/lib/facter/haproxy_version.rb
```

## Module Explanation

The module executes in the following order.

1. **`role::haproxy`** (`site-modules/role/manifests/haproxy.pp`)
   - Runs the role-specific Linux conditional when `$facts['kernel'].downcase == 'linux'`.
   - References external `Class['::profile::base::base']`.
   - Loads `Class['::profile::loadbalancer::haproxy']`.
   - Orders the base profile before the load-balancer profile.
   - The exact command and attributes for the Linux conditional `exec` resource are not present in the supplied execution-tree data.
   - Also reads the `environment` fact through the load-balancer profile context.

2. **`profile::loadbalancer::haproxy`** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`)
   - Includes `profile_haproxy`.
   - Transfers execution to the `profile_haproxy` class.

3. **`profile_haproxy`** (`site-modules/profile_haproxy/manifests/init.pp`)
   - Resolves the effective parameters for `lb01.fra.example.com`:
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
     - `stats_password`: control-repository secret; migrate to `vault_haproxy_stats_password`
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
     - `backends`: deep-merged hash containing `webservers`, host-overridden `api`, and `internal_monitoring`
     - `discovery_enabled`: `false`
   - Contains, in order:
     - `profile_haproxy::install`
     - `profile_haproxy::config`
     - `profile_haproxy::service`
     - `profile_haproxy::firewall`
   - Orders installation before configuration.
   - Configuration notifies the service.
   - Does not execute the discovery branch because `discovery_enabled` is `false`.
   - Contains the firewall class without a supplied explicit ordering relationship to the other classes.

4. **`profile_haproxy::install`** (`site-modules/profile_haproxy/manifests/install.pp`)
   - Installs package `haproxy`.
   - Evaluates the `extra_packages` conditional; the effective value is `[]`, so the loop executes zero times.
   - Creates group `haproxy`.
   - Creates user `haproxy`.
   - Creates `/etc/haproxy`.
   - Creates `/etc/haproxy/conf.d`.
   - Creates `/var/lib/haproxy`.
   - Evaluates the OS-dependent SELinux conditional.
   - Debian defaults to `selinux_enabled: false`; RedHat defaults to `selinux_enabled: true`.
   - The exact effective SELinux value depends on the selected OS hierarchy because no control-repository override is supplied.
   - When enabled, creates `exec['haproxy_selinux_connect']`; its exact command and attributes are not present in the supplied execution-tree data.

5. **`profile_haproxy::config`** (`site-modules/profile_haproxy/manifests/config.pp`)
   - Creates `/etc/haproxy/errors`.
   - Renders `/etc/haproxy/haproxy.cfg` from `site-modules/profile_haproxy/templates/haproxy.cfg.erb` once.
   - Passes the effective global, timeout, retry, statistics, TLS, logging, and backend settings to the template.
   - Uses the corrected TLS cipher value `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384`.
   - Iterates over `$backends.each` three times:
     - `webservers`
     - `api`
     - `internal_monitoring`
   - Renders `/etc/haproxy/conf.d/webservers.cfg` from `site-modules/profile_haproxy/templates/backend.conf.epp`:
     - Balance: `roundrobin`
     - Port: `8080`
     - Check: `httpchk GET /health`
     - Interval: `5s`
     - Servers: `web1`, `web2`, `web3`
   - Renders `/etc/haproxy/conf.d/api.cfg` from `site-modules/profile_haproxy/templates/backend.conf.epp`:
     - Balance: `leastconn`
     - Port: `3000`
     - Check: `httpchk GET /api/health`
     - Interval: `10s`
     - Servers: `api1-fra`, `api2-fra`
     - The host-level server list replaces, rather than appends to, the inherited list.
   - Renders `/etc/haproxy/conf.d/internal_monitoring.cfg` from `site-modules/profile_haproxy/templates/backend.conf.epp`:
     - Balance: `roundrobin`
     - Port: `9090`
     - Check: `httpchk GET /-/healthy`
     - Interval: `15s`
     - Server: `prom1-fra`
   - Iterates over `['503', '408'].each` two times:
     - Creates `/etc/haproxy/errors/503.http`.
     - Creates `/etc/haproxy/errors/408.http`.
   - Does not create `/etc/haproxy/conf.d/stick-tables.cfg` because `stick_table_enabled` is effectively `false`.

6. **`profile_haproxy::service`** (`site-modules/profile_haproxy/manifests/service.pp`)
   - Creates `/etc/systemd/system/haproxy.service.d`.
   - Creates `/etc/systemd/system/haproxy.service.d/override.conf`.
   - Runs `exec['haproxy_systemd_reload']`; exact command and attributes are not present in the supplied execution-tree data.
   - Manages service `haproxy`.
   - Runs `exec['haproxy_config_check']`; exact command and attributes are not present in the supplied execution-tree data.
   - Creates `/etc/logrotate.d/haproxy`.
   - Receives notification from the configuration class.
   - The Ansible implementation must validate the configuration before enabling or restarting the service and notify a reload/restart handler when configuration changes.

7. **`profile_haproxy::firewall`** (`site-modules/profile_haproxy/manifests/firewall.pp`)
   - Selects behavior with `case $firewall_provider`.
   - The effective provider is `none`, so no firewall resources are created.
   - The `firewalld` branch is inactive and would run `exec['firewalld_reload']`.
   - The `ufw` branch is inactive and would install `ufw`, allow HTTP and HTTPS, and enable UFW.
   - The default branch is inactive and would create an unknown-provider notification.

8. **`profile_haproxy::discover`** (`site-modules/profile_haproxy/manifests/discover.pp`)
   - Is not executed because `discovery_enabled=false`.
   - If enabled, exports `haproxy::balancermember[$facts['networking']['fqdn']]` for the `webservers` service with local FQDN, local IP, port `8080`, and option `check`.
   - If enabled, collects `Haproxy::Balancermember` resources where `listening_service == 'webservers'`.
   - If enabled, iterates over `$app_servers.each` and creates `haproxy::balancermember[api-${certname}]`.
   - Uses `$facts['networking']['fqdn']`, `$facts['networking']['ip']`, and `$facts['puppet_environment']`.

## Variables

**Variable Flow Summary**: The module uses seven Hiera data levels represented by 21 hierarchy entries/files, including module defaults, OS-specific, environment, cluster, node, and control-repository data. The common data contains 26 module variables plus lookup metadata. The effective node is `lb01.fra.example.com` in the `haproxy_prod_fra` production cluster. Backend hashes use deep merging; the host-level `api.servers` array replaces the inherited array.

### Variable Definitions

#### `site-modules/profile_haproxy/data/common.yaml` — module defaults

Migration note: Base defaults for all nodes.

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
- `profile_haproxy::stats_password`: encrypted eyaml value (type: string; sensitive)
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
- `profile_haproxy::lookup_options`: deep-merge metadata for `profile_haproxy::backends` (type: hash)
- `profile_haproxy::discovery_enabled`: `false` (type: boolean)

#### `site-modules/profile_haproxy/data/os/Debian.yaml` — Debian-specific values

Migration note: Loaded conditionally for Debian-family systems.

- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::firewall_provider`: `ufw` (type: string)
- `profile_haproxy::extra_packages`: `[hatop]` (type: array)
- `profile_haproxy::selinux_enabled`: `false` (type: boolean)

#### `site-modules/profile_haproxy/data/os/RedHat.yaml` — RedHat-specific values

Migration note: Loaded conditionally for RedHat-family systems. `firewall_zone` is inactive for this node because the effective firewall provider is `none`.

- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (type: string)
- `profile_haproxy::firewall_provider`: `firewalld` (type: string)
- `profile_haproxy::firewall_zone`: `public` (type: string; inactive with provider `none`)
- `profile_haproxy::extra_packages`: `[haproxy-systemd-wrapper, policycoreutils-python-utils]` (type: array)
- `profile_haproxy::selinux_enabled`: `true` (type: boolean)

#### `site-modules/profile_haproxy/data/environment/production.yaml` — production values

Migration note: Production-specific values for nodes in the production environment.

- `profile_haproxy::global_maxconn`: `16384` (type: integer)
- `profile_haproxy::ssl_enabled`: `true` (type: boolean)
- `profile_haproxy::log_level`: `warning` (type: string)
- `profile_haproxy::client_timeout`: `60s` (type: string)
- `profile_haproxy::server_timeout`: `60s` (type: string)
- `profile_haproxy::stats_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_size`: `200k` (type: string)
- `profile_haproxy::stick_table_expire`: `30m` (type: string)

#### `site-modules/profile_haproxy/data/environment/staging.yaml` — staging values

Migration note: Staging-specific values for nodes in the staging environment.

- `profile_haproxy::global_maxconn`: `2048` (type: integer)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::log_level`: `debug` (type: string)
- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

#### `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml` — Frankfurt production cluster

Migration note: Cluster-wide overrides for the Frankfurt production HAProxy cluster.

- `profile_haproxy::global_maxconn`: `32768` (type: integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384` (type: string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (type: string)
- `profile_haproxy::backends`: additional `internal_monitoring` backend (type: hash)

#### `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml` — host-specific values

Migration note: Host-specific overrides for `lb01.fra.example.com`.

- `profile_haproxy::stats_enabled`: `true` (type: boolean)
- `profile_haproxy::stats_port`: `9001` (type: integer)
- `profile_haproxy::backends`: host-level `api.servers` replacement (type: hash)

#### `data/common.yaml` — control-repository overrides

Migration note: Highest-priority control-repository overrides for the migrated node.

- `profile_haproxy::package_name`: `haproxy` (type: string)
- `profile_haproxy::stats_password`: control-repository secret (type: string; sensitive; migrate to `vault_haproxy_stats_password`)
- `profile_haproxy::firewall_provider`: `none` (type: string)
- `profile_haproxy::extra_packages`: `[]` (type: array)
- `profile_haproxy::ssl_enabled`: `false` (type: boolean)
- `profile_haproxy::stick_table_enabled`: `false` (type: boolean)

### Variable Migration Summary

- **Common defaults**: 26 module variables plus lookup metadata from `common.yaml`
- **OS-specific variables**: 5 Debian variables and 6 RedHat variables
- **Environment-specific variables**: 8 production variables and 5 staging variables
- **Cluster-specific variables**: 4 variables
- **Host-specific variables**: 3 variables
- **Control-repository overrides**: 6 relevant HAProxy variables
- **Sensitive variables**: 1 detected secret, `stats_password`
- **Non-sensitive paths**: `ssl_cert_path` and `ssl_key_path` are ordinary filesystem paths, not encrypted values

Recommended Ansible mappings include:

- `haproxy_package_name`
- `haproxy_config_dir`
- `haproxy_config_file`
- `haproxy_service_name`
- `haproxy_user`
- `haproxy_group`
- `haproxy_stats_enabled`
- `haproxy_stats_port`
- `haproxy_stats_uri`
- `haproxy_stats_user`
- `vault_haproxy_stats_password`
- `haproxy_global_maxconn`
- `haproxy_client_timeout`
- `haproxy_server_timeout`
- `haproxy_connect_timeout`
- `haproxy_retries`
- `haproxy_ssl_enabled`
- `haproxy_ssl_cert_path`
- `haproxy_ssl_key_path`
- `haproxy_ssl_ciphers`
- `haproxy_ssl_min_version`
- `haproxy_log_server`
- `haproxy_log_facility`
- `haproxy_log_level`
- `haproxy_backends`
- `haproxy_firewall_provider`
- `haproxy_extra_packages`
- `haproxy_selinux_enabled`
- `haproxy_stick_table_enabled`
- `haproxy_stick_table_size`
- `haproxy_stick_table_expire`
- `haproxy_discovery_enabled`

### Cross-Level Overrides

- **`profile_haproxy::package_name`**
  - Defined in common, Debian, RedHat, and control-repository data
  - Effective value: `haproxy`
  - Merge strategy: first/highest priority

- **`profile_haproxy::stats_password`**
  - Defined in module common and control-repository common
  - Effective value: redacted control-repository secret
  - Merge strategy: first/highest priority
  - Migration strategy: store only in Ansible Vault as `vault_haproxy_stats_password`

- **`profile_haproxy::ssl_enabled`**
  - Defined in module common, production, staging, and control-repository common
  - Effective value: `false`
  - Merge strategy: first/highest priority

- **`profile_haproxy::global_maxconn`**
  - Defined in module common, production, staging, and cluster data
  - Effective production-cluster value: `32768`

- **`profile_haproxy::stats_enabled`**
  - Defined in module common, production, staging, and node data
  - Effective node value: `true`

- **`profile_haproxy::stats_port`**
  - Defined in module common and node data
  - Effective node value: `9001`

- **`profile_haproxy::ssl_ciphers`**
  - Defined in module common and cluster data
  - Effective value: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384`

- **`profile_haproxy::ssl_min_version`**
  - Defined in module common and cluster data
  - Effective value: `TLSv1.3`

- **`profile_haproxy::backends`**
  - Defined in module common, cluster, and node data
  - Merge strategy: deep
  - Hash keys are merged recursively.
  - The host-level `api.servers` list replaces the inherited list.
  - Effective keys: `webservers`, `api`, `internal_monitoring`

- **`profile_haproxy::firewall_provider`**
  - OS defaults are `ufw` or `firewalld`
  - Control-repository common overrides the value to `none`

- **`profile_haproxy::extra_packages`**
  - OS defaults contain packages
  - Control-repository common overrides the value to `[]`
  - Effective loop runs zero times

- **`profile_haproxy::discovery_enabled`**
  - Defined by the module default as `false`
  - No higher-priority override is supplied
  - Effective value: `false`

### Merge Strategy Notes

- Variables using `hash` merge combine hash values from multiple levels using shallow merging.
- `profile_haproxy::backends` uses deep merging, so nested hash keys are recursively combined.
- Arrays are not concatenated for the host-level `api.servers` override; the host list replaces the inherited list.
- Variables using `first` or the default lookup behavior use the first value found at the highest applicable priority.

## Custom Types and Providers

No custom Puppet resource types or providers are shown.

### Custom Fact

- **File**: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- **Fact**: `haproxy_version`
- The supplied component notes describe Linux-only execution of `haproxy -v 2>/dev/null`, extraction of the first semantic version after `version`, and `nil` when HAProxy is unavailable or no version is found.
- These implementation details should be verified against the complete custom-component source analysis before migration.
- Ansible equivalent:
  - Prefer a custom fact at `/etc/ansible/facts.d/haproxy_version.fact`.
  - Alternatively run `haproxy -v` and parse the version.
  - No custom Ansible module is required.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.7.0`
- `puppetlabs-concat` `9.0.2`
- `puppetlabs-firewall` `8.1.3`

**System package dependencies**:

- `haproxy`
- Debian default extra package: `hatop`, overridden to none
- RedHat default extra packages:
  - `haproxy-systemd-wrapper`
  - `policycoreutils-python-utils`
  - overridden to none

**Service dependencies**:

- `Class['::profile::base::base']` precedes `Class['::profile::loadbalancer::haproxy']`.
- `profile_haproxy::install` precedes `profile_haproxy::config`.
- `profile_haproxy::config` notifies `profile_haproxy::service`.
- With discovery disabled, the effective flow is:
  - `profile_haproxy::install -> profile_haproxy::config ~> profile_haproxy::service`
- With discovery enabled, the intended flow additionally includes:
  - `profile_haproxy::config -> profile_haproxy::discover ~> profile_haproxy::service`

## Puppet Facts Used

- **`$facts['kernel']`**
  - Provides the operating-system kernel name.
  - Used to restrict the role-specific command to Linux.

- **`fact('environment')`**
  - Provides the Puppet environment value.
  - Referenced by the load-balancer profile context.

- **`$facts['networking']['fqdn']`**
  - Provides the HAProxy host FQDN.
  - Used as the exported balancermember title and server name when discovery is enabled.

- **`$facts['networking']['ip']`**
  - Provides the host networking IP address.
  - Used as the exported balancermember address when discovery is enabled.

- **`$facts['puppet_environment']`**
  - Provides the Puppet environment assigned to the node.
  - Used by the discovery implementation context.

- **`haproxy_version`**
  - Custom fact for the installed HAProxy semantic version.
  - The detailed implementation is retained as source-reported but requires verification against the complete custom-component analysis.

## Template Conversion Notes

### `site-modules/profile_haproxy/templates/haproxy.cfg.erb`

- Destination: `/etc/haproxy/haproxy.cfg`
- Render count: `1`
- Supplied metadata: 21 variables and 5 logic blocks
- Convert to a Jinja2 template.
- Preserve conditional rendering for statistics and TLS.
- Render the effective global settings and backend include structure.
- Use `vault_haproxy_stats_password` for the statistics password.
- Do not log the rendered configuration or expose the password in task output.

### `site-modules/profile_haproxy/templates/backend.conf.epp`

- Destinations:
  - `/etc/haproxy/conf.d/webservers.cfg`
  - `/etc/haproxy/conf.d/api.cfg`
  - `/etc/haproxy/conf.d/internal_monitoring.cfg`
- Render count: `3`
- Supplied metadata: 11 variables and 5 logic blocks
- Convert to a Jinja2 template rendered once per backend.
- Iterate over `haproxy_backends | dict2items`.
- Iterate over each backend server list.
- Preserve backend-specific balance, port, health check, and interval values.
- Preserve replacement semantics for the host-level `api.servers` list.

## PuppetDB Dependencies

Discovery is disabled for the effective node, so no PuppetDB resources are active during migration. The Puppet source nevertheless contains these discovery patterns:

- **Exported resource**
  - Resource type: `haproxy::balancermember`
  - Resource title: `$facts['networking']['fqdn']`
  - Listening service: `webservers`
  - Server name: local FQDN
  - Address: local IP
  - Port: `8080`
  - Options: `check`
  - Migration note: replace cross-node exported-resource sharing with explicit Ansible inventory, group variables, or a service-discovery source.

- **Resource collector**
  - Expression: `Haproxy::Balancermember <| listening_service == 'webservers' |>`
  - Migration note: inventory must explicitly identify the nodes that provide web-server backend members.

- **PuppetDB query**
  - The supplied structured execution-tree summary does not show a `puppetdb_query()` call or exact query details.
  - Earlier source notes claim a query for `Profile::App_server` resources filtered by `Profile::Base` environment matching `$facts['puppet_environment']`, but this is not corroborated by the supplied tree.
  - Treat that query behavior as unverified until complete source analysis is available.

- **Host identity data**
  - `$facts['networking']['fqdn']` identifies the exporting host.
  - `$facts['networking']['ip']` supplies its address.
  - `$facts['puppet_environment']` supplies the environment classification used by the discovery context.

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
- `/etc/haproxy/haproxy.cfg`
- `/etc/haproxy/conf.d/webservers.cfg`
- `/etc/haproxy/conf.d/api.cfg`
- `/etc/haproxy/conf.d/internal_monitoring.cfg`
- `/etc/haproxy/errors/503.http`
- `/etc/haproxy/errors/408.http`
- `/etc/haproxy/errors`
- `/etc/systemd/system/haproxy.service.d`
- `/etc/systemd/system/haproxy.service.d/override.conf`
- `/etc/logrotate.d/haproxy`
- `/var/lib/haproxy`

**Service endpoints to check**:

- `webservers`: port `8080`
- `api`: port `3000`
- `internal_monitoring`: port `9090`
- HAProxy statistics: port `9001`, URI `/haproxy-stats`
- TLS endpoint: not enabled because `ssl_enabled=false`

**Templates rendered**:

- `site-modules/profile_haproxy/templates/haproxy.cfg.erb` → `/etc/haproxy/haproxy.cfg` → `1` render
- `site-modules/profile_haproxy/templates/backend.conf.epp` → `/etc/haproxy/conf.d/webservers.cfg` → `1` render
- `site-modules/profile_haproxy/templates/backend.conf.epp` → `/etc/haproxy/conf.d/api.cfg` → `1` render
- `site-modules/profile_haproxy/templates/backend.conf.epp` → `/etc/haproxy/conf.d/internal_monitoring.cfg` → `1` render
- Error-page loop → `/etc/haproxy/errors/503.http` and `/etc/haproxy/errors/408.http` → `2` iterations
- Stick-table configuration → not rendered because `stick_table_enabled=false`

## Pre-flight checks

```bash
# Package and identity checks
rpm -q haproxy 2>/dev/null || dpkg-query -W haproxy
getent passwd haproxy
getent group haproxy

# Filesystem checks
test -d /etc/haproxy
test -d /etc/haproxy/conf.d
test -d /etc/haproxy/errors
test -d /var/lib/haproxy

# Configuration files
test -f /etc/haproxy/haproxy.cfg
test -f /etc/haproxy/conf.d/webservers.cfg
test -f /etc/haproxy/conf.d/api.cfg
test -f /etc/haproxy/conf.d/internal_monitoring.cfg
test -f /etc/haproxy/errors/503.http
test -f /etc/haproxy/errors/408.http
test -f /etc/systemd/system/haproxy.service.d/override.conf
test -f /etc/logrotate.d/haproxy

# HAProxy configuration validation
haproxy -c -f /etc/haproxy/haproxy.cfg

# Service checks
systemctl daemon-reload
systemctl is-enabled haproxy
systemctl is-active haproxy
systemctl status haproxy --no-pager

# Individual backend checks
curl --fail --silent --show-error http://127.0.0.1:8080/health
curl --fail --silent --show-error http://127.0.0.1:3000/api/health
curl --fail --silent --show-error http://127.0.0.1:9090/-/healthy

# Statistics endpoint check
curl --fail --silent --show-error http://127.0.0.1:9001/haproxy-stats

# Listening socket checks
ss -ltnp | grep -E ':(8080|3000|9090|9001)\b'

# HAProxy version fact check
haproxy -v
```