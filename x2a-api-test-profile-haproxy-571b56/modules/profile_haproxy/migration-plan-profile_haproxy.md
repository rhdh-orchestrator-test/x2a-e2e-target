---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: Migrate the `profile_haproxy` Puppet profile to an Ansible role that installs and configures HAProxy, manages its systemd service and logrotate configuration, renders the main configuration and backend fragments, and supports conditional firewall and discovery behavior. The supplied execution tree validates the class flow and resource categories, but the detailed effective Hiera values, backend membership, template counts, custom fact implementation, PuppetDB query, and credential data require source-file analysis before being treated as verified. The values below are retained as source-plan assumptions and must be confirmed during migration.

## Service Type and Instances

**Service Type**: Load balancer / reverse proxy

**Configured Instances**:

- **HAProxy service**
  - Purpose: Load balancing and reverse proxy service
  - Package: `haproxy`
  - Service: `haproxy`
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Configuration directory: `/etc/haproxy`
  - Fragment directory: `/etc/haproxy/conf.d`
  - Error directory: `/etc/haproxy/errors`
  - Runtime user: `haproxy`
  - Runtime group: `haproxy`
  - Statistics endpoint: `http://127.0.0.1:9001/haproxy-stats` *(source-plan assumption; verify from Hiera and template analysis)*
  - Statistics user: `admin`
  - Statistics password: migrate to Ansible Vault variable `haproxy_stats_password`; the supplied validation does not verify the source credential
  - SSL: disabled in the supplied effective configuration assumption
  - Certificate path: `/etc/ssl/certs`
  - Private-key path: `/etc/ssl/private`
  - Log server: `10.100.1.50`
  - Log facility: `local0`
  - Log level: `warning`
  - Maximum connections: `32768`
  - Client timeout: `60s`
  - Server timeout: `60s`
  - Connect timeout: `5s`
  - Retries: `3`

- **`webservers` backend**
  - Purpose: HTTP web-server load balancing
  - Port: `8080`
  - Balance method: `roundrobin`
  - Health check: `httpchk GET /health`
  - Health-check interval: `5s`
  - Servers:
    - `web1-fra`: `10.100.1.10`, weight `100`
    - `web2-fra`: `10.100.1.11`, weight `100`
    - `web3-fra`: `10.100.1.12`, weight `100`

- **`api` backend**
  - Purpose: API load balancing
  - Port: `3000`
  - Balance method: `leastconn`
  - Health check: `httpchk GET /api/health`
  - Health-check interval: `10s`
  - Servers:
    - `api1-fra`: `10.100.2.10`, weight `200`
    - `api2-fra`: `10.100.2.11`, weight `100`

- **`internal_monitoring` backend**
  - Purpose: Internal monitoring and metrics endpoint
  - Port: `9090`
  - Balance method: `roundrobin`
  - Health check: `httpchk GET /-/healthy`
  - Health-check interval: `15s`
  - Servers:
    - `prom1-fra`: `10.100.3.10`, weight `100`

The three backend names, server lists, ports, and render counts are source-plan assumptions. The supplied validation confirms only that a backend iteration exists, not its effective values or number of iterations.

## File Structure

```text
site-modules/profile_haproxy/
├── manifests/
│   ├── init.pp
│   ├── install.pp
│   ├── config.pp
│   ├── service.pp
│   ├── firewall.pp
│   └── discover.pp
├── templates/
│   └── profile_haproxy/
│       ├── haproxy.cfg.erb
│       └── backend.conf.epp
├── lib/
│   └── facter/
│       └── haproxy_version.rb
└── data/
    ├── common.yaml
    ├── os/
    │   ├── Debian.yaml
    │   └── RedHat.yaml
    ├── environment/
    │   ├── production.yaml
    │   └── staging.yaml
    ├── datacenter/
    │   └── dc1_fra.yaml
    ├── cluster/
    │   └── haproxy_prod_fra.yaml
    └── nodes/
        └── lb01.fra.example.com.yaml

data/
├── common.yaml
└── environment/
    ├── production.yaml
    └── staging.yaml
```

The input identifies 45 analyzed files, but supplies an explicit listing for only the files shown above. The remaining analyzed files must be inventoried or mapped before migration completeness can be demonstrated.

## Module Explanation

The validated class-level execution flow is installation, configuration, optional discovery, service management, and firewall containment. Detailed resource attributes and effective values require manifest and Hiera source verification.

1. **`profile_haproxy`** (`site-modules/profile_haproxy/manifests/init.pp`)
   - Contains `profile_haproxy::install`, `profile_haproxy::config`, `profile_haproxy::service`, `profile_haproxy::firewall`, and conditional `profile_haproxy::discover`.
   - Establishes installation before configuration.
   - Configuration notifies service management.
   - Includes `profile_haproxy::discover` only when `discovery_enabled` is true.
   - Contains the firewall class without a validated explicit class-level ordering relationship.
   - Ansible order: install packages and directories, render configuration, validate configuration, reload systemd if required, then enable/start or reload HAProxy.

2. **`profile_haproxy::install`** (`site-modules/profile_haproxy/manifests/install.pp`)
   - Manages package resource `haproxy`.
   - Manages the `haproxy` group and user.
   - Creates `/etc/haproxy`, `/etc/haproxy/conf.d`, and `/var/lib/haproxy`.
   - Contains an extra-package conditional. The supplied plan assumes no effective extra packages; confirm this from Hiera.
   - Contains a conditional SELinux command represented by `exec[haproxy_selinux_connect]`.
   - Ansible implementation:
     - Install `haproxy`.
     - Create the `haproxy` group and user.
     - Create required directories.
     - Install conditional OS packages only when verified by OS-specific data.
     - Execute the SELinux task only when `haproxy_selinux_enabled` is true.

3. **`profile_haproxy::config`** (`site-modules/profile_haproxy/manifests/config.pp`)
   - Manages `/etc/haproxy/errors`.
   - Manages error file resources `/etc/haproxy/errors/503.http` and `/etc/haproxy/errors/408.http`.
   - Renders `/etc/haproxy/haproxy.cfg` from `site-modules/profile_haproxy/templates/profile_haproxy/haproxy.cfg.erb`.
   - Iterates over `$backends.each`.
   - Source-plan backend iterations are:
     - `webservers`, producing `/etc/haproxy/conf.d/webservers.cfg`
     - `api`, producing `/etc/haproxy/conf.d/api.cfg`
     - `internal_monitoring`, producing `/etc/haproxy/conf.d/internal_monitoring.cfg`
   - The supplied validation confirms a backend loop but does not verify these item names or counts.
   - Conditionally manages `/etc/haproxy/conf.d/stick-tables.cfg` when `stick_table_enabled` is true. The supplied plan assumes this is disabled.
   - Notifies `profile_haproxy::service` when configuration changes.
   - Ansible implementation:
     - Render the main HAProxy configuration.
     - Render the three named backend fragments when their backend data is confirmed.
     - Render the two error files as file resources, not as templates unless source analysis proves otherwise.
     - Validate configuration before notifying a reload or restart handler.

4. **`profile_haproxy::service`** (`site-modules/profile_haproxy/manifests/service.pp`)
   - Manages `/etc/systemd/system/haproxy.service.d`.
   - Manages `/etc/systemd/system/haproxy.service.d/override.conf`.
   - Uses `exec[haproxy_systemd_reload]` after systemd override changes.
   - Manages `service[haproxy]`.
   - Uses `exec[haproxy_config_check]` for HAProxy configuration validation.
   - Manages `/etc/logrotate.d/haproxy`.
   - Ansible implementation:
     - Notify a `systemd daemon-reload` handler when `override.conf` changes.
     - Run `haproxy -c -f /etc/haproxy/haproxy.cfg` before service restart or reload.
     - Enable and start `haproxy`.
     - Install the logrotate configuration.
     - Prevent service changes when validation fails.

5. **`profile_haproxy::firewall`** (`site-modules/profile_haproxy/manifests/firewall.pp`)
   - Supports `firewalld`, `ufw`, `none`, and an unknown-provider branch.
   - The supplied plan assumes effective provider `none`; this value is not validated by the execution-tree analysis.
   - `firewalld` branch: includes `exec[firewalld_reload]`; exact managed rules require source analysis.
   - `ufw` branch: includes package resource `ufw`, `exec[ufw_allow_http]`, `exec[ufw_allow_https]`, and `exec[ufw_enable]`.
   - `none` branch: disables firewall management.
   - Unknown provider branch: emits an unknown-provider notification.
   - Ansible should use `ansible.posix.firewalld` or `community.general.ufw` where practical and fail clearly for unsupported providers.

6. **`profile_haproxy::discover`** (`site-modules/profile_haproxy/manifests/discover.pp`)
   - Is conditionally included when `discovery_enabled` is true.
   - Exports one `haproxy::balancermember` resource using the local host identity.
   - Collects `Haproxy::Balancermember` resources filtered by `listening_service == 'webservers'`.
   - Iterates over `$app_servers.each` and creates API balancer members.
   - Uses networking FQDN, networking IP, and Puppet environment facts.
   - The detailed exported attributes and PuppetDB query shown in the source plan are not validated by the supplied analysis.
   - Ansible should replace this behavior with explicit inventory groups, group variables, dynamic inventory, or a separately validated service-discovery mechanism.
   - Discovery remains disabled by default unless source analysis confirms otherwise.

## Variables

**Variable Flow Summary**: The source plan describes module, OS, environment, datacenter, cluster, node, and control-repository data with recursive backend merging. The supplied validation does not contain Hiera hierarchy, lookup precedence, parameter declarations, or merge metadata; therefore, the values and precedence below are migration-source assumptions requiring confirmation.

### Variable Definitions

#### `site-modules/profile_haproxy/data/common.yaml` — module defaults

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
- `profile_haproxy::stats_password`: `ENC[PKCS7,...]` (encrypted string)
- `profile_haproxy::global_maxconn`: `4096` (integer)
- `profile_haproxy::client_timeout`: `30s` (string)
- `profile_haproxy::server_timeout`: `30s` (string)
- `profile_haproxy::connect_timeout`: `5s` (string)
- `profile_haproxy::retries`: `3` (integer)
- `profile_haproxy::ssl_enabled`: `false` (boolean)
- `profile_haproxy::ssl_cert_path`: `/etc/ssl/certs` (string)
- `profile_haproxy::ssl_key_path`: `/etc/ssl/private` (string)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256` (string)
- `profile_haproxy::ssl_min_version`: `TLSv1.2` (string)
- `profile_haproxy::log_server`: `127.0.0.1` (string)
- `profile_haproxy::log_facility`: `local0` (string)
- `profile_haproxy::log_level`: `info` (string)
- `profile_haproxy::backends`: hash containing `webservers` and `api`
- `lookup_options.profile_haproxy::backends.merge`: `deep` (string)

#### `site-modules/profile_haproxy/data/os/Debian.yaml` — Debian-specific data

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (string)
- `profile_haproxy::firewall_provider`: `ufw` (string)
- `profile_haproxy::extra_packages`: `[hatop]` (array)
- `profile_haproxy::selinux_enabled`: `false` (boolean)

#### `site-modules/profile_haproxy/data/os/RedHat.yaml` — RedHat-specific data

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (string)
- `profile_haproxy::firewall_provider`: `firewalld` (string)
- `profile_haproxy::firewall_zone`: `public` (string)
- `profile_haproxy::extra_packages`: `[haproxy-systemd-wrapper, policycoreutils-python-utils]` (array)
- `profile_haproxy::selinux_enabled`: `true` (boolean)

#### `site-modules/profile_haproxy/data/environment/production.yaml` — production data

- `profile_haproxy::global_maxconn`: `16384` (integer)
- `profile_haproxy::ssl_enabled`: `true` (boolean)
- `profile_haproxy::log_level`: `warning` (string)
- `profile_haproxy::client_timeout`: `60s` (string)
- `profile_haproxy::server_timeout`: `60s` (string)
- `profile_haproxy::stats_enabled`: `false` (boolean)
- `profile_haproxy::stick_table_enabled`: `true` (boolean)
- `profile_haproxy::stick_table_size`: `200k` (string)
- `profile_haproxy::stick_table_expire`: `30m` (string)

#### `site-modules/profile_haproxy/data/environment/staging.yaml` — staging data

- `profile_haproxy::global_maxconn`: `2048` (integer)
- `profile_haproxy::ssl_enabled`: `false` (boolean)
- `profile_haproxy::log_level`: `debug` (string)
- `profile_haproxy::stats_enabled`: `true` (boolean)
- `profile_haproxy::stick_table_enabled`: `false` (boolean)

#### `site-modules/profile_haproxy/data/datacenter/dc1_fra.yaml` — Frankfurt datacenter data

- `profile_haproxy::log_server`: `10.100.1.50` (string)
- `profile_haproxy::ntp_servers`: `[ntp1.dc1.fra.example.com, ntp2.dc1.fra.example.com]` (array)
- `profile_haproxy::backends.webservers.servers`: Frankfurt web server list (array)
- `profile_haproxy::backends.api.servers`: Frankfurt API server list (array)

#### `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml` — cluster data

- `profile_haproxy::global_maxconn`: `32768` (integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384` (string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (string)
- `profile_haproxy::backends.internal_monitoring`: backend hash for port `9090` (hash)

#### `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml` — host-specific data

- `profile_haproxy::stats_enabled`: `true` (boolean)
- `profile_haproxy::stats_port`: `9001` (integer)
- `profile_haproxy::backends.api.servers`: API server list with weights `200` and `100` (array)

#### `data/common.yaml` — control-repository overrides

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::stats_password`: `test-haproxy-password` (plaintext string in source plan; replace with Vault secret)
- `profile_haproxy::firewall_provider`: `none` (string)
- `profile_haproxy::extra_packages`: `[]` (array)
- `profile_haproxy::ssl_enabled`: `false` (boolean)
- `profile_haproxy::stick_table_enabled`: `false` (boolean)

### Variable Migration Summary

- **Module common defaults**: HAProxy package, paths, service, identity, timeouts, SSL defaults, logging defaults, statistics defaults, backend defaults, and backend merge configuration.
- **OS-specific variables**: Package paths, firewall provider, firewall zone, extra packages, and SELinux behavior.
- **Environment-specific variables**: Connection limits, SSL state, logging level, timeouts, statistics state, and stick-table settings.
- **Datacenter-specific variables**: Log server, NTP servers, and backend server lists.
- **Cluster-specific variables**: Connection limit, TLS settings, and the monitoring backend.
- **Host-specific variables**: Statistics state and port, plus API server overrides.
- **Control-repository overrides**: Package, statistics password, firewall provider, extra packages, SSL state, and stick-table state.
- **Encrypted variables**: The source plan identifies the statistics password as sensitive. TLS certificate and private-key material are migration recommendations, not detected entries in the supplied validation data.
- **Ansible mapping**:
  - Common values: role defaults.
  - OS values: `vars/Debian.yml` and `vars/RedHat.yml`.
  - Environment values: `group_vars/production.yml` and `group_vars/staging.yml`.
  - Datacenter values: `group_vars/dc1_fra.yml`.
  - Cluster values: cluster group variables.
  - Host values: `host_vars/lb01.fra.example.com.yml`.
  - Secrets: Ansible Vault, including `haproxy_stats_password` and any verified TLS material.
  - Backends: recursively merged dictionaries using `combine(..., recursive=True)` or equivalent role-variable composition.

### Cross-Level Overrides

The following overrides are described in the source plan but require Hiera analysis for verification:

- **`profile_haproxy::package_name`**: module common, OS data, and control common; expected effective value `haproxy`; scalar first-value precedence.
- **`profile_haproxy::config_dir`**: module common and OS data; expected effective value `/etc/haproxy`.
- **`profile_haproxy::global_maxconn`**: module common, environment, and cluster; expected Frankfurt production value `32768`.
- **`profile_haproxy::ssl_enabled`**: module common, environment, and control common; expected effective value `false`.
- **`profile_haproxy::stats_enabled`**: module common, environment, and node; expected host value `true`.
- **`profile_haproxy::stats_port`**: module common and node; expected host value `9001`.
- **`profile_haproxy::stats_password`**: encrypted module common and control common; migrate only to Vault.
- **`profile_haproxy::firewall_provider`**: OS data and control common; expected effective value `none`.
- **`profile_haproxy::extra_packages`**: OS data and control common; expected effective value `[]`.
- **`profile_haproxy::stick_table_enabled`**: environment and control common; expected effective value `false`.
- **`profile_haproxy::backends`**: module common, datacenter, cluster, and node; expected merge strategy `deep`.

### Merge Strategy Notes

- `deep` merge: Backend hashes are recursively merged across common, datacenter, cluster, and host layers.
- `first` or default scalar lookup: The highest-precedence scalar value wins without merging.
- Exact precedence and lookup behavior must be confirmed from the missing Hiera hierarchy and lookup metadata.

## Custom Types and Providers

- **Custom fact: `haproxy_version`**
  - File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
  - Source-plan behavior: Linux-only execution of `haproxy -v 2>/dev/null`, extracting a semantic version and returning the version or `nil`.
  - The supplied validation does not verify this implementation.
  - Ansible equivalent: run `haproxy -v` with `ansible.builtin.command`, extract the version with a regular expression, and store it with `ansible.builtin.set_fact`.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` version `9.7.0`
- `puppetlabs-concat` version `9.0.2`
- `puppetlabs-firewall` version `8.1.3`

**System package dependencies**:

- Required: `haproxy`
- Debian conditional: `hatop`
- RedHat conditional: `haproxy-systemd-wrapper`
- RedHat conditional: `policycoreutils-python-utils`
- Effective extra-package selection requires Hiera verification.

**Service dependencies**:

- Installation precedes configuration.
- Configuration validation precedes service restart or reload.
- Systemd daemon reload follows changes to `/etc/systemd/system/haproxy.service.d/override.conf`.
- Firewall management is independent in the validated class tree.
- Discovery dependencies require explicit inventory or service-discovery replacement in Ansible.

## Puppet Facts Used

- `$facts['networking']['fqdn']`
  - Local fully qualified domain name used by the discovery class.
  - The supplied validation confirms fact usage but not all exported-resource fields.

- `$facts['networking']['ip']`
  - Local IP address used by the discovery class.

- `$facts['puppet_environment']`
  - Puppet environment used by the discovery class.

- `haproxy_version`
  - Custom fact listed in the source plan.
  - Its implementation details require custom-component source verification.

## Template Conversion Notes

### `site-modules/profile_haproxy/templates/profile_haproxy/haproxy.cfg.erb`

- Destination: `/etc/haproxy/haproxy.cfg`
- Source-plan render count: `1`; this count requires template analysis verification.
- Convert ERB conditionals to Jinja2 conditionals for:
  - SSL configuration
  - Statistics configuration
  - Backend iteration
- Use Vault-backed `haproxy_stats_password` without exposing it in task output.
- Pass the verified HAProxy settings and recursively merged backend map to the template.

### `site-modules/profile_haproxy/templates/profile_haproxy/backend.conf.epp`

- Source-plan destinations:
  - `/etc/haproxy/conf.d/webservers.cfg`
  - `/etc/haproxy/conf.d/api.cfg`
  - `/etc/haproxy/conf.d/internal_monitoring.cfg`
- Source-plan render count: `3`; the supplied validation confirms only that a backend loop exists.
- Convert EPP logic to Jinja2.
- Iterate over backend names and each backend’s server list.
- Preserve balance method, port, health-check directive, health-check interval, server name, address, and weight.

### Error resources

- `/etc/haproxy/errors/503.http`
- `/etc/haproxy/errors/408.http`

The validated analysis identifies file resources generated by a loop over `503` and `408`. Treat these as file resources unless source analysis confirms that they are rendered from templates. Do not count them as templates in the migration.

## PuppetDB Dependencies

**Context**: The supplied validation confirms PuppetDB-related resource export, collection, and an application-server iteration, but does not validate the detailed query, exported attributes, or query parameters.

- **Exported Resources**:
  - The discovery class exports one `haproxy::balancermember` resource using the local host identity.
  - Exact exported parameters are not validated by the supplied analysis.
  - Ansible replacement: explicit inventory or dynamic service-discovery data.

- **Resource Collectors**:
  - `Haproxy::Balancermember <| listening_service == 'webservers' |>`
  - Collects exported web-server balancer members.
  - Ansible replacement: inventory group membership and backend variables.

- **PuppetDB Queries**:
  - The validation does not provide a supported exact query or query parameters.
  - Do not reproduce the source-plan `Profile::App_server` / `Profile::Base` query until `discover.pp` and related PuppetDB code are analyzed.

- **Host Identity Data**:
  - The discovery class uses networking FQDN, networking IP, and Puppet environment facts.
  - Discovery is disabled by default in the source-plan effective configuration assumption.

## Checks for the Migration

**Files to verify**:

- `/etc/haproxy/haproxy.cfg`
- `/etc/haproxy/conf.d/webservers.cfg`
- `/etc/haproxy/conf.d/api.cfg`
- `/etc/haproxy/conf.d/internal_monitoring.cfg`
- `/etc/haproxy/errors`
- `/etc/haproxy/errors/503.http`
- `/etc/haproxy/errors/408.http`
- `/etc/systemd/system/haproxy.service.d`
- `/etc/systemd/system/haproxy.service.d/override.conf`
- `/etc/logrotate.d/haproxy`
- `/var/lib/haproxy`

**Packages to verify**:

- `haproxy`
- Any OS-specific extra packages only after Hiera verification

**Service endpoints to check**:

- HAProxy statistics: `http://127.0.0.1:9001/haproxy-stats`
- `webservers` backend: port `8080`
- `api` backend: port `3000`
- `internal_monitoring` backend: port `9090`

**Templates and resources to verify**:

- Main HAProxy configuration: expected source-plan count `1`; verify against template analysis.
- `webservers` backend fragment: expected source-plan count `1`; verify against backend analysis.
- `api` backend fragment: expected source-plan count `1`; verify against backend analysis.
- `internal_monitoring` backend fragment: expected source-plan count `1`; verify against backend analysis.
- `503.http`: file resource, expected count `1`.
- `408.http`: file resource, expected count `1`.
- `stick-tables.cfg`: expected count `0` under the source-plan effective configuration assumption.

## Pre-flight checks

```bash
# Verify package installation and version
haproxy -v
dpkg-query -W haproxy 2>/dev/null || rpm -q haproxy

# Verify the main HAProxy configuration
haproxy -c -f /etc/haproxy/haproxy.cfg

# Verify that the backend fragments exist
test -f /etc/haproxy/conf.d/webservers.cfg
test -f /etc/haproxy/conf.d/api.cfg
test -f /etc/haproxy/conf.d/internal_monitoring.cfg

# Verify error resources
test -f /etc/haproxy/errors/503.http
test -f /etc/haproxy/errors/408.http

# Verify systemd override and service state
systemctl daemon-reload
systemctl is-enabled haproxy
systemctl is-active haproxy

# Verify HAProxy listener and statistics endpoint
ss -ltnp | grep ':9001'
curl --fail http://127.0.0.1:9001/haproxy-stats

# Verify each backend endpoint independently
curl --fail http://127.0.0.1:8080/health
curl --fail http://127.0.0.1:3000/api/health
curl --fail http://127.0.0.1:9090/-/healthy

# Verify service logs
journalctl -u haproxy --no-pager -n 100

# Verify that the statistics password is supplied by Ansible Vault
# and is not printed in task output.

# Verify that no firewall changes occur when the verified provider is "none".

# Verify that configuration changes trigger reload or restart
# only after successful "haproxy -c" validation.
```