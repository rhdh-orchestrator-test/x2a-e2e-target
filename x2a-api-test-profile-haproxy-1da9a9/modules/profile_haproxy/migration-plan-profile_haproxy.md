---
source-path: site-modules/profile_haproxy
---

# Migration Plan: profile_haproxy

**TLDR**: This module installs and configures HAProxy as a systemd-managed HTTP/HTTPS load balancer on `lb01.fra.example.com`. The effective node configuration listens on ports `80`, `443`, and `9001`, serves the `webservers`, `api`, and `internal_monitoring` backends, enables TLS, statistics, and production stick-table settings, and uses no firewall provider because the control-repository override resolves `firewall_provider` to `none`. The module also contains an optional PuppetDB discovery path that is disabled by default.

## Service Type and Instances

**Service Type**: HTTP/HTTPS load balancer and reverse proxy.

**Configured Instances**:

- **HAProxy on `lb01.fra.example.com`**: Systemd-managed load-balancing service
  - Package: `haproxy`
  - Service: `haproxy`
  - Configuration: `/etc/haproxy/haproxy.cfg`
  - Backend fragments: `/etc/haproxy/conf.d/*.cfg`
  - Error pages: `/etc/haproxy/errors/503.http`, `/etc/haproxy/errors/408.http`
  - Runtime directory: `/var/lib/haproxy`
  - HTTP port: `80/tcp`
  - HTTPS port: `443/tcp`
  - Statistics port: `9001/tcp`
  - Statistics URI: `/haproxy-stats`
  - Maximum connections: `32768`
  - TLS minimum version: `TLSv1.3`
  - TLS cipher list: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384`
  - Statistics: enabled
  - Firewall provider: `none`
  - PuppetDB discovery: disabled by default

- **`webservers` backend**: HTTP application backend
  - Balance method: `roundrobin`
  - Port: `8080`
  - Health check: `httpchk GET /health`
  - Health-check interval: `5s`
  - Servers:
    - `web1` → `10.0.1.10:8080`, weight `100`
    - `web2` → `10.0.1.11:8080`, weight `100`
    - `web3` → `10.0.1.12:8080`, weight `100`

- **`api` backend**: API application backend
  - Balance method: `leastconn`
  - Port: `3000`
  - Health check: `httpchk GET /api/health`
  - Health-check interval: `10s`
  - Effective node-specific servers:
    - `api1-fra` → `10.100.2.10:3000`, weight `200`
    - `api2-fra` → `10.100.2.11:3000`, weight `100`

- **`internal_monitoring` backend**: Internal monitoring backend
  - Balance method: `roundrobin`
  - Port: `9090`
  - Health check: `httpchk GET /-/healthy`
  - Health-check interval: `15s`
  - Servers:
    - `prom1-fra` → `10.100.3.10:9090`, weight `100`

## File Structure

```text
site-modules/
├── role/
│   └── manifests/
│       └── haproxy.pp
├── profile/
│   └── manifests/
│       └── loadbalancer/
│           └── haproxy.pp
└── profile_haproxy/
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
    │   ├── os/
    │   │   ├── Debian.yaml
    │   │   └── RedHat.yaml
    │   ├── environment/
    │   │   ├── production.yaml
    │   │   └── staging.yaml
    │   ├── cluster/
    │   │   └── haproxy_prod_fra.yaml
    │   └── nodes/
    │       └── lb01.fra.example.com.yaml
    └── lib/
        └── facter/
            └── haproxy_version.rb

data/
├── common.yaml
└── environment/
    ├── production.yaml
    └── staging.yaml
```

## Module Explanation

The module executes through the following class chain:

`role::haproxy` → `profile::loadbalancer::haproxy` → `profile_haproxy`

The supplied analysis covers the files listed above. `profile::base::base` and the resource shown as `exec[None]` are referenced by the role but are not analyzed in the supplied migration data.

1. **`role::haproxy`** (`site-modules/role/manifests/haproxy.pp`):
   - Runs the HAProxy role only when `$facts['kernel'].downcase == 'linux'`.
   - Includes `Class['::profile::base::base']`.
   - Includes `Class['::profile::loadbalancer::haproxy']`.
   - Orders the base profile before the load-balancer profile.
   - The Linux branch contains an execution-tree resource named `exec[None]`; its command and attributes were not supplied and require source verification.

2. **`profile::loadbalancer::haproxy`** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - Bridges the role layer to `profile_haproxy`.
   - The supplied analysis identifies this class in the execution chain but does not expose its internal resources.
   - Migration must preserve its inclusion and parameter-passing behavior.

3. **`profile_haproxy`** (`site-modules/profile_haproxy/manifests/init.pp`):
   - Contains `profile_haproxy::install`.
   - Contains `profile_haproxy::config`.
   - Contains `profile_haproxy::service`.
   - Contains `profile_haproxy::firewall`.
   - Uses `discovery_enabled`, which defaults to `false`.
   - With discovery disabled, ordering is:
     - `profile_haproxy::install`
     - `profile_haproxy::config`
     - `profile_haproxy::service`
   - With discovery enabled, `profile_haproxy::discover` is inserted between configuration and service.

4. **`profile_haproxy::install`** (`site-modules/profile_haproxy/manifests/install.pp`):
   - Installs `haproxy`.
   - Expands the `extra_packages` loop; the effective control-repository value is empty, so the loop has zero iterations.
   - Creates group `haproxy` as a system group.
   - Creates user `haproxy` with:
     - GID: `haproxy`
     - Home: `/var/lib/haproxy`
     - Shell: `/sbin/nologin`
     - System account: `true`
   - Creates:
     - `/etc/haproxy`
     - `/etc/haproxy/conf.d`
     - `/var/lib/haproxy`
   - Effective directory ownership and modes:
     - `/etc/haproxy`: `root:haproxy`, `0755`
     - `/etc/haproxy/conf.d`: `root:haproxy`, `0755`
     - `/var/lib/haproxy`: `haproxy:haproxy`, `0750`
   - Debian alternative:
     - Installs `hatop`.
     - Uses `ufw` when selected by OS data.
     - Sets `selinux_enabled` to `false`.
   - RedHat alternative:
     - Installs `haproxy-systemd-wrapper`.
     - Installs `policycoreutils-python-utils`.
     - Sets `selinux_enabled` to `true`.
     - Runs `setsebool -P haproxy_connect_any 1` unless `haproxy_connect_any` is already enabled.
   - Exact individual package, command, and ordering attributes for these resources were not fully exposed by the structured analysis and should be verified against source before implementation.

5. **`profile_haproxy::config`** (`site-modules/profile_haproxy/manifests/config.pp`):
   - Renders `/etc/haproxy/haproxy.cfg` from `site-modules/profile_haproxy/templates/haproxy.cfg.erb`.
   - Main configuration ownership and mode: `root:haproxy`, `0640`.
   - Expands `$profile_haproxy::backends.each` exactly three times:
     - `webservers`
     - `api`
     - `internal_monitoring`
   - Renders the following backend fragments from `site-modules/profile_haproxy/templates/backend.conf.epp`:
     - `/etc/haproxy/conf.d/webservers.cfg`
     - `/etc/haproxy/conf.d/api.cfg`
     - `/etc/haproxy/conf.d/internal_monitoring.cfg`
   - Each backend fragment has ownership `root:haproxy` and mode `0640`.
   - `webservers` renders:
     - `server web1 10.0.1.10:8080 check weight 100 ssl verify none`
     - `server web2 10.0.1.11:8080 check weight 100 ssl verify none`
     - `server web3 10.0.1.12:8080 check weight 100 ssl verify none`
   - `api` renders:
     - `server api1-fra 10.100.2.10:3000 check weight 200 ssl verify none`
     - `server api2-fra 10.100.2.11:3000 check weight 100 ssl verify none`
   - `internal_monitoring` renders:
     - `server prom1-fra 10.100.3.10:9090 check weight 100 ssl verify none`
   - Expands `['503', '408'].each` exactly two times:
     - `/etc/haproxy/errors/503.http`
     - `/etc/haproxy/errors/408.http`
   - Creates `/etc/haproxy/errors` as `root:haproxy`, mode `0755`.
   - Error pages use Puppet sources:
     - `puppet:///modules/profile_haproxy/haproxy_errors/503.http`
     - `puppet:///modules/profile_haproxy/haproxy_errors/408.http`
   - Renders `/etc/haproxy/conf.d/stick-tables.cfg` when stick tables are enabled, with:
     ```text
     # Managed by Puppet
     stick-table type ip size 200k expire 30m
     ```
   - Main configuration, backend fragments, and stick-table configuration are described as notifying the service; these individual notification edges require source-level verification because they are not exposed in the structured summary.

6. **`profile_haproxy::service`** (`site-modules/profile_haproxy/manifests/service.pp`):
   - Creates `/etc/systemd/system/haproxy.service.d`.
   - Renders `/etc/systemd/system/haproxy.service.d/override.conf` with:
     ```ini
     [Service]
     ExecStart=
     ExecStart=/usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d/ -p /run/haproxy.pid -S /run/haproxy-master.sock
     ```
   - Defines `systemctl daemon-reload` as a refresh-only operation.
   - Manages service `haproxy` as enabled and running.
   - Validates configuration with:
     ```text
     haproxy -c -f /etc/haproxy/haproxy.cfg -f /etc/haproxy/conf.d/
     ```
   - Installs `/etc/logrotate.d/haproxy` with daily rotation, fourteen retained rotations, compression, and a post-rotate HUP of `/var/run/haproxy.pid`.
   - The supplied structured analysis confirms the named resources and broad relationships but does not independently verify every individual `require`, `subscribe`, or `notify` edge.

7. **`profile_haproxy::firewall`** (`site-modules/profile_haproxy/manifests/firewall.pp`):
   - Calls `base_utils::normalize_port(9001)`.
   - The effective control-repository value is `firewall_provider: none`.
   - With provider `none`, no firewall resources are created.
   - The supplied validation identified branch discrepancies:
     - The structured tree exposes UFW resources for `ufw`, HTTP, HTTPS, and enablement, but does not expose `ufw_allow_stats`.
     - The structured tree exposes only `firewalld_reload` in the firewalld branch, despite the earlier plan listing three port-opening resources.
   - Therefore, the migration must not claim verified UFW statistics or firewalld port-opening resources without source evidence. The intended ports are `80/tcp`, `443/tcp`, and `9001/tcp`, but branch resource coverage requires verification.

8. **`profile_haproxy::discover`** (`site-modules/profile_haproxy/manifests/discover.pp`):
   - Is not executed for the supplied node because `discovery_enabled` is `false`.
   - When enabled, exports `haproxy::balancermember` data for the local node and collects balancer members listening on `webservers`.
   - The structured analysis identifies a collector equivalent to:
     ```text
     Haproxy::Balancermember <| listening_service == 'webservers' |>
     ```
   - The exact collector syntax must be confirmed from source; the supplied plan used both `<<| |>>` and `<| |>` notation.
   - Performs an application-server discovery loop whose runtime count depends on PuppetDB results.
   - Creates API members named `api-<certname>` with port values returned from the query.
   - Ansible migration should replace exported resources and collectors with an explicit inventory group or service-discovery source.

## Variables

**Variable Flow Summary**: Variables are resolved from module defaults, OS data, environment data, cluster data, node data, and control-repository data. Scalar values use first-match precedence unless otherwise stated. `profile_haproxy::backends` uses deep merge. The effective example is production, cluster `haproxy_prod_fra`, node `lb01.fra.example.com`.

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
- `profile_haproxy::backends`: hash containing `webservers` and `api` (hash)
  - `webservers.balance`: `roundrobin` (string)
  - `webservers.port`: `8080` (integer)
  - `webservers.health_check`: `httpchk GET /health` (string)
  - `webservers.health_interval`: `5s` (string)
  - `webservers.ssl_enabled`: `true` (boolean)
  - `webservers.servers`: hash containing `web1`, `web2`, and `web3` (hash)
  - `web1.address`: `10.0.1.10` (string)
  - `web1.port`: `8080` (integer)
  - `web1.weight`: `100` (integer)
  - `web2.address`: `10.0.1.11` (string)
  - `web2.port`: `8080` (integer)
  - `web2.weight`: `100` (integer)
  - `web3.address`: `10.0.1.12` (string)
  - `web3.port`: `8080` (integer)
  - `web3.weight`: `100` (integer)
  - `api.balance`: `leastconn` (string)
  - `api.port`: `3000` (integer)
  - `api.health_check`: `httpchk GET /api/health` (string)
  - `api.health_interval`: `10s` (string)
  - `api.ssl_enabled`: `true` (boolean)
  - `api.servers`: common server list is replaced by node data for the supplied node (hash)

- `profile_haproxy::discovery_enabled`: `false` (boolean)

#### `site-modules/profile_haproxy/data/os/Debian.yaml` — Debian-specific data

Migration note: Loaded conditionally for Debian-family systems.

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (string)
- `profile_haproxy::firewall_provider`: `ufw` (string)
- `profile_haproxy::extra_packages`: `[hatop]` (array)
- `profile_haproxy::selinux_enabled`: `false` (boolean)

#### `site-modules/profile_haproxy/data/os/RedHat.yaml` — RedHat-specific data

Migration note: Loaded conditionally for RedHat-family systems.

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::config_dir`: `/etc/haproxy` (string)
- `profile_haproxy::firewall_provider`: `firewalld` (string)
- `profile_haproxy::firewall_zone`: `public` (string)
- `profile_haproxy::extra_packages`: `[haproxy-systemd-wrapper, policycoreutils-python-utils]` (array)
- `profile_haproxy::selinux_enabled`: `true` (boolean)

#### `site-modules/profile_haproxy/data/environment/production.yaml` — module production data

Migration note: Production defaults. Control-repository environment data, if populated, has to be compared explicitly because its contents were not supplied.

- `profile_haproxy::global_maxconn`: `16384` (integer)
- `profile_haproxy::ssl_enabled`: `true` (boolean)
- `profile_haproxy::log_level`: `warning` (string)
- `profile_haproxy::client_timeout`: `60s` (string)
- `profile_haproxy::server_timeout`: `60s` (string)
- `profile_haproxy::stats_enabled`: `false` (boolean)
- `profile_haproxy::stick_table_enabled`: `true` (boolean)
- `profile_haproxy::stick_table_size`: `200k` (string)
- `profile_haproxy::stick_table_expire`: `30m` (string)

#### `site-modules/profile_haproxy/data/environment/staging.yaml` — module staging data

Migration note: Staging defaults.

- `profile_haproxy::global_maxconn`: `2048` (integer)
- `profile_haproxy::ssl_enabled`: `false` (boolean)
- `profile_haproxy::log_level`: `debug` (string)
- `profile_haproxy::stats_enabled`: `true` (boolean)
- `profile_haproxy::stick_table_enabled`: `false` (boolean)

#### `site-modules/profile_haproxy/data/cluster/haproxy_prod_fra.yaml` — Frankfurt cluster data

Migration note: Cluster overrides for the production Frankfurt load balancer.

- `profile_haproxy::global_maxconn`: `32768` (integer)
- `profile_haproxy::ssl_ciphers`: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384` (string)
- `profile_haproxy::ssl_min_version`: `TLSv1.3` (string)
- `profile_haproxy::backends.internal_monitoring`: hash
  - `balance`: `roundrobin` (string)
  - `port`: `9090` (integer)
  - `health_check`: `httpchk GET /-/healthy` (string)
  - `health_interval`: `15s` (string)
  - `ssl_enabled`: `true` (boolean)
  - `servers.prom1-fra.address`: `10.100.3.10` (string)
  - `servers.prom1-fra.port`: `9090` (integer)
  - `servers.prom1-fra.weight`: `100` (integer)

#### `site-modules/profile_haproxy/data/nodes/lb01.fra.example.com.yaml` — host-specific data

Migration note: Host overrides for the supplied Frankfurt load balancer.

- `profile_haproxy::stats_enabled`: `true` (boolean)
- `profile_haproxy::stats_port`: `9001` (integer)
- `profile_haproxy::backends.api.servers`: hash
  - `api1-fra.address`: `10.100.2.10` (string)
  - `api1-fra.port`: `3000` (integer)
  - `api1-fra.weight`: `200` (integer)
  - `api2-fra.address`: `10.100.2.11` (string)
  - `api2-fra.port`: `3000` (integer)
  - `api2-fra.weight`: `100` (integer)

#### `data/common.yaml` — control-repository common data

Migration note: Control-repository overrides applied broadly. These values override module defaults according to the configured hierarchy precedence.

- `profile_haproxy::package_name`: `haproxy` (string)
- `profile_haproxy::stats_password`: `test-haproxy-password` (string; plaintext secret and must be moved to Ansible Vault or another secret backend)
- `profile_haproxy::firewall_provider`: `none` (string)
- `profile_haproxy::extra_packages`: `[]` (array)
- `profile_haproxy::ssl_enabled`: `false` (boolean)
- `profile_haproxy::stick_table_enabled`: `false` (boolean)

#### `data/environment/production.yaml` — control-repository production data

Migration note: This file is listed in the hierarchy, but its variables and values were not supplied. Do not invent values; inspect the file and map every defined key into Ansible production variables.

#### `data/environment/staging.yaml` — control-repository staging data

Migration note: This file is listed in the hierarchy, but its variables and values were not supplied. Do not invent values; inspect the file and map every defined key into Ansible staging variables.

### Effective Values for `lb01.fra.example.com`

- `package_name`: `haproxy`
- `stats_enabled`: `true`
- `stats_port`: `9001`
- `stats_uri`: `/haproxy-stats`
- `global_maxconn`: `32768`
- `ssl_enabled`: `true`
- `ssl_min_version`: `TLSv1.3`
- `ssl_ciphers`: `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384`
- `client_timeout`: `60s`
- `server_timeout`: `60s`
- `stats_password`: `test-haproxy-password` from control common data
- `firewall_provider`: `none`
- `extra_packages`: `[]`
- `stick_table_enabled`: `true`
- `stick_table_size`: `200k`
- `stick_table_expire`: `30m`

### Variable Migration Summary

- **Common defaults**: 26 module-common entries, including the `backends` hash and `discovery_enabled`
- **OS-specific variables**: 5 Debian entries and 6 RedHat entries
- **Environment-specific variables**: 9 production entries and 5 staging entries
- **Cluster-specific variables**: 4 top-level entries, including nested `internal_monitoring` backend data
- **Host-specific variables**: 3 entries, including nested `api.servers` data
- **Control-repository overrides**: 6 entries from `data/common.yaml`
- **Control-repository environment variables**: contents of production and staging files require source inspection
- **Encrypted variables**: 1 encrypted module-default value, `stats_password`
- **Plaintext sensitive overrides**: 1 control-repository `stats_password` value
- **Filesystem path settings**: `ssl_cert_path` and `ssl_key_path` are paths, not credentials

### Cross-Level Overrides

- **`profile_haproxy::package_name`**: module common, Debian data, RedHat data, and control common; first-match scalar lookup; effective value `haproxy`
- **`profile_haproxy::ssl_enabled`**: module common, module production, module staging, and control common; first-match scalar lookup; effective production value `true`
- **`profile_haproxy::stats_enabled`**: module common, module production, module staging, and node data; first-match scalar lookup; effective node value `true`
- **`profile_haproxy::stats_port`**: module common and node data; first-match scalar lookup; effective node value `9001`
- **`profile_haproxy::global_maxconn`**: module common, module production, module staging, and cluster data; first-match scalar lookup; effective cluster value `32768`
- **`profile_haproxy::backends`**: module common, cluster data, and node data; deep merge; cluster adds `internal_monitoring`, and node replaces `api.servers`
- **`profile_haproxy::stats_password`**: encrypted module default and plaintext control common override; migration must store the effective secret in Ansible Vault or another secure backend
- **`profile_haproxy::firewall_provider`**: OS data provides `ufw` or `firewalld`, while control common provides `none`; effective supplied value is `none`
- **`profile_haproxy::extra_packages`**: OS data provides packages, while control common provides an empty array; effective supplied value is `[]`
- **`profile_haproxy::stick_table_enabled`**: module production enables it, while control common disables it; effective supplied production value is `true` under the stated precedence

### Merge Strategy Notes

- Variables using **deep merge**: nested values in `profile_haproxy::backends` are recursively merged.
- Variables using **first-match lookup**: scalar values such as ports, package names, booleans, and strings use the first value found in the hierarchy.
- Variables using **array values**: `extra_packages` is resolved as a complete array; the effective control value is empty.
- Ansible migration must represent the resulting precedence explicitly through `group_vars`, `host_vars`, and environment-specific variable files.

## Custom Types and Providers

### Custom Fact: `haproxy_version`

- File: `site-modules/profile_haproxy/lib/facter/haproxy_version.rb`
- Confined to Linux.
- Executes:
  ```text
  haproxy -v 2>/dev/null
  ```
- Extracts a semantic version using:
  ```text
  /version\s+(\d+\.\d+\.\d+)/
  ```
- Returns the captured version or `nil`.
- Ansible replacement:
  - Use `ansible.builtin.command` with `changed_when: false` and parse stdout, or
  - Install `/etc/ansible/facts.d/haproxy_version.fact`.

No custom Puppet resource type or provider is defined in the supplied module.

## Dependencies

**External module dependencies**:

- `puppetlabs-stdlib` `9.7.0`
- `puppetlabs-concat` `9.0.2`
- `puppetlabs-firewall` `8.1.3`

**Additional code dependencies**:

- `base_utils::normalize_port()`
- `profile::base::base`
- `profile::loadbalancer::haproxy`
- The source for `base_utils` and the internals of `profile::base::base` are not included in the supplied analysis.

**System package dependencies**:

- `haproxy`
- Debian alternative: `hatop`
- Debian UFW alternative: `ufw`
- RedHat alternative: `haproxy-systemd-wrapper`
- RedHat SELinux alternative: `policycoreutils-python-utils`
- RedHat SELinux commands: `setsebool`, `getsebool`

**Service dependencies**:

- Package installation precedes configuration.
- Configuration precedes service activation or restart.
- The systemd override requires its parent directory.
- The systemd daemon reload follows changes to the override.
- HAProxy configuration validation must pass before service restart.
- Firewall resources are contained in `profile_haproxy::firewall`; explicit ordering against the HAProxy service was not verified.

## Puppet Facts Used

- `$facts['kernel']`
  - Kernel name.
  - Restricts `role::haproxy` to Linux.

- `$facts['networking']['fqdn']`
  - Current node FQDN.
  - Used for exported discovery member identity and discovered API member naming.

- `$facts['networking']['ip']`
  - Current node IP address.
  - Used by the exported `haproxy::balancermember`.

- `$facts['puppet_environment']`
  - Current Puppet environment.
  - Used by the PuppetDB application-server discovery filter.

- `fact('environment')`
  - Puppet environment value referenced by the profile wrapper context.

- `haproxy_version`
  - Custom Linux fact that parses the installed HAProxy version.
  - No consuming resource was identified.

## Template Conversion Notes

### `site-modules/profile_haproxy/templates/haproxy.cfg.erb`

- Render count: `1`
- Destination: `/etc/haproxy/haproxy.cfg`
- Variables:
  - `log_server`
  - `log_facility`
  - `log_level`
  - `global_maxconn`
  - `user`
  - `group`
  - `ssl_enabled`
  - `ssl_ciphers`
  - `connect_timeout`
  - `client_timeout`
  - `server_timeout`
  - `retries`
  - `stats_enabled`
  - `stats_port`
  - `stats_uri`
  - `stats_user`
  - `stats_password`
  - `ssl_cert_path`
  - `backends`
  - loop variables `name` and `config`
- Effective output:
  - `maxconn 32768`
  - `user haproxy`
  - `group haproxy`
  - TLS enabled
  - Statistics listener on `*:9001`
  - HTTPS certificate reference `/etc/ssl/certs/haproxy.pem`
  - HTTP listener on `*:80`
  - HTTPS listener on `*:443 ssl crt /etc/ssl/certs/haproxy.pem`
  - HTTPS redirect enabled
  - Default backend `webservers`
- The analyzed template reports 21 variables and 4 logic blocks. The source summary explicitly identifies:
  - TLS/global TLS conditional rendering
  - Statistics listener conditional rendering
  - Backend iteration
  - Frontend/HTTPS conditional rendering
- The Ansible conversion should implement these as Jinja2 conditionals and a backend loop.
- `ssl_min_version` and `ssl_key_path` are class variables but are not referenced by this template.
- Error-file paths are literal `/etc/haproxy/errors/...` paths rather than values derived from `config_dir`.

### `site-modules/profile_haproxy/templates/backend.conf.epp`

- Render count: `3`
- Destinations:
  - `/etc/haproxy/conf.d/webservers.cfg`
  - `/etc/haproxy/conf.d/api.cfg`
  - `/etc/haproxy/conf.d/internal_monitoring.cfg`
- Confirmed variables:
  - `backend_name`
  - `balance`
  - `port`
  - `servers`
  - `health_check`
- Additional effective context values:
  - `health_interval`
  - `ssl_enabled`
  - server name
  - server address
  - server port
  - server weight
- The structured analysis reports 11 variables and 3 logic blocks, but the supplied source summary does not provide the names of all 11 variables. The six additional names must be extracted from the EPP source before final Ansible implementation.
- The three logic blocks should be represented in Jinja2 as:
  - conditional health-check rendering
  - conditional SSL options
  - iteration over backend server definitions
- Effective server lines include `check`, `weight`, `ssl`, and `verify none`.

## PuppetDB Dependencies

**Context**: PuppetDB is used only by the optional discovery path, which is disabled for the supplied node.

- **Exported Resources**:
  - Resource type: `haproxy::balancermember`
  - Exported identity: local FQDN from `$facts['networking']['fqdn']`
  - Listening service: `webservers`
  - Address: local `$facts['networking']['ip']`
  - Port: `8080`
  - Options: `check`
  - Migration: Replace exported cross-node resources with an explicit Ansible inventory group, generated backend variable, or service-discovery registration.

- **Resource Collector**:
  - Intended collector: `Haproxy::Balancermember` resources filtered by `listening_service == 'webservers'`.
  - The structured analysis and original plan use different collector delimiters. Confirm whether the source uses `<| |>` or `<<| |>>` before migration.
  - Migration: Replace collector behavior with a deterministic inventory group or generated list of web servers.

- **PuppetDB Query**:
  - The plan describes a query selecting `Class` resources titled `Profile::App_server`, restricted to certificates that also have `Profile::Base` with an environment matching `$facts['puppet_environment']`.
  - The structured analysis confirms the discovery operation but does not provide the complete query body. Query syntax and returned parameter structure require source verification.
  - Migration: Use an Ansible inventory group or service-discovery API filtered by environment.

- **Application-server Discovery Loop**:
  - Iteration: `$app_servers.each`
  - Runtime count: determined by PuppetDB results.
  - For each returned server, creates an API member named `api-<certname>`.
  - Listening service: `api`
  - Address: returned server identity or address
  - Port: `$server['parameters']['port']`
  - Options: `check inter 10s`
  - Migration: Generate the API backend from an explicit inventory group and host variables. Preserve the runtime-dependent behavior only if the replacement discovery source provides equivalent data.

- **Host Identity Data**:
  - FQDN and IP facts identify the exporting node.
  - Puppet environment fact