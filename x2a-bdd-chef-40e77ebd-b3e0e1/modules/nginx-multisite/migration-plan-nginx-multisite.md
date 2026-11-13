---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server hosting three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies hardened nginx, kernel, firewall, SSH, and fail2ban settings; creates static document roots and index files; generates idempotent self-signed certificates; and configures HTTP-to-HTTPS redirects with per-site nginx access and error logs. The Ansible implementation must preserve recipe execution order, explicit site names, certificate idempotence, delayed service reloads, and per-site configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - SSL enabled: `true`
  - Static source file: `test/index.html`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - SSL enabled: `true`
  - Static source file: `ci/index.html`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - SSL enabled: `true`
  - Static source file: `status/index.html`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`

**Security configuration namespaces**:

- **fail2ban**
  - Enabled: `true`
- **ufw**
  - Enabled: `true`
- **ssh**
  - `disable_root`: `true`
  - `password_auth`: `false`

The `security` namespace supplies conditional configuration values for fail2ban, UFW, and SSH hardening. The explicitly configured site collection contains exactly `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

## File Structure

All paths below are relative to `cookbooks/nginx-multisite`.

### Recipes

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

### Providers

```text
```

No provider files are used by the execution tree.

### Templates

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

### Attributes

```text
cookbooks/nginx-multisite/attributes/default.rb
```

### Files

No static files under `files/default/*` or `files/*` are present in the supplied directory listing.

The nginx recipe references these cookbook file sources dynamically:

```text
test/index.html
ci/index.html
status/index.html
```

These files must be supplied separately to the Ansible migration if the sites require index pages.

## Module Explanation

The cookbook performs operations in this order:

1. `security`
2. `nginx`
3. `ssl`
4. `sites`

### 1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- Uses four `include_recipe` resources.
- Preserves the dependency order in which security configuration runs first, nginx is installed next, certificates are generated before virtual-host deployment, and site links are created last.

### 2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts the `fail2ban` service.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configures fail2ban with:
  - Ban time: `3600` seconds.
  - Find time: `600` seconds.
  - Maximum retries: `3`.
  - Backend: `auto`.
  - SSH protection.
  - nginx HTTP authentication protection.
  - nginx request-rate protection.
  - nginx bot-search protection.
- Delays a fail2ban restart when `/etc/fail2ban/jail.local` changes.
- Configures UFW idempotently:
  - Default incoming policy: deny.
  - Allows SSH on port `22`.
  - Allows HTTP on port `80`.
  - Allows HTTPS on port `443`.
  - Enables UFW.
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Applies the sysctl configuration with delayed execution of:
  ```bash
  sysctl -p /etc/sysctl.d/99-security.conf
  ```
- Applies SSH hardening when the configured security values are enabled:
  - Sets `PermitRootLogin no`.
  - Sets `PasswordAuthentication no`.
  - Delays an `sshd` restart when either setting changes.
- Declares `service[sshd]` with action `nothing` for notification-based restarts.
- Uses eight execute resources:
  - Five UFW commands.
  - One sysctl reload command.
  - Two SSH hardening commands.

### 3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Configures:
  - User: `nginx`.
  - Worker processes: `auto`.
  - PID file: `/run/nginx.pid`.
  - Worker connections: `768`.
  - `sendfile on`.
  - `tcp_nopush on`.
  - `tcp_nodelay on`.
  - Keepalive timeout: `65`.
  - MIME types from `/etc/nginx/mime.types`.
  - Global access and error logs.
  - Gzip.
  - Includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Configures:
  - `server_tokens off`.
  - `login` request-rate zone at `10r/m`.
  - `api` request-rate zone at `30r/m`.
  - Ten-megabyte rate-limit zones.
  - Request body and header buffer limits.
  - Maximum request body size of `1k`.
  - Client, header, and send timeouts of `10`.
  - TLS session cache and timeout.
  - TLS protocols `TLSv1.2 TLSv1.3`.
  - Explicit ECDHE/DHE ciphers.
  - Preferred server ciphers.
- Delays nginx reloads when either nginx template changes.
- Enables and starts the `nginx` service.
- Creates document roots and deploys index files for the following sites:

  - **test.cluster.local**
    - Creates `/opt/server/test` recursively.
    - Sets directory owner and group to `nginx:nginx`.
    - Sets directory mode to `0755`.
    - Deploys `test/index.html` to `/opt/server/test/index.html`.
    - Sets file owner and group to `nginx:nginx`.
    - Sets file mode to `0644`.

  - **ci.cluster.local**
    - Creates `/opt/server/ci` recursively.
    - Sets directory owner and group to `nginx:nginx`.
    - Sets directory mode to `0755`.
    - Deploys `ci/index.html` to `/opt/server/ci/index.html`.
    - Sets file owner and group to `nginx:nginx`.
    - Sets file mode to `0644`.

  - **status.cluster.local**
    - Creates `/opt/server/status` recursively.
    - Sets directory owner and group to `nginx:nginx`.
    - Sets directory mode to `0755`.
    - Deploys `status/index.html` to `/opt/server/status/index.html`.
    - Sets file owner and group to `nginx:nginx`.
    - Sets file mode to `0644`.

- Iterates explicitly over `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
- Creates three directory resources and three cookbook file resources.

### 4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs the `openssl` and `ca-certificates` packages.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` with:
  - Owner: `root`.
  - Group: `root`.
  - Mode: `0755`.
- Creates `/etc/ssl/private` with:
  - Owner: `root`.
  - Group: `ssl-cert`.
  - Mode: `0710`.
- Generates self-signed certificates for all three SSL-enabled sites.

  - **test.cluster.local**
    - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
    - Key: `/etc/ssl/private/test.cluster.local.key`
    - Resource: `execute[generate-ssl-cert-test.cluster.local]`
    - Subject common name: `test.cluster.local`

  - **ci.cluster.local**
    - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
    - Key: `/etc/ssl/private/ci.cluster.local.key`
    - Resource: `execute[generate-ssl-cert-ci.cluster.local]`
    - Subject common name: `ci.cluster.local`

  - **status.cluster.local**
    - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
    - Key: `/etc/ssl/private/status.cluster.local.key`
    - Resource: `execute[generate-ssl-cert-status.cluster.local]`
    - Subject common name: `status.cluster.local`

- Uses:
  ```bash
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout <key_file> \
    -out <cert_file> \
    -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com"
  chmod 640 <key_file>
  chown root:ssl-cert <key_file>
  ```
- Generates certificates only when the certificate and key do not already exist.
- Delays nginx reloads after certificate generation.
- The Ansible implementation must use equivalent `creates` behavior or explicit certificate and key existence checks.

### 5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Creates `/etc/nginx/sites-available` with owner `root:root` and mode `0755`.
- Creates `/etc/nginx/sites-enabled` with owner `root:root` and mode `0755`.
- Renders the site template and creates the corresponding link for each named site:

  - **test.cluster.local**
    - Template source: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
    - Destination: `/etc/nginx/sites-available/test.cluster.local`
    - Link: `/etc/nginx/sites-enabled/test.cluster.local`
    - Link target: `/etc/nginx/sites-available/test.cluster.local`
    - Document root: `/opt/server/test`
    - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
    - Private key: `/etc/ssl/private/test.cluster.local.key`
    - SSL enabled: `true`

  - **ci.cluster.local**
    - Template source: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
    - Destination: `/etc/nginx/sites-available/ci.cluster.local`
    - Link: `/etc/nginx/sites-enabled/ci.cluster.local`
    - Link target: `/etc/nginx/sites-available/ci.cluster.local`
    - Document root: `/opt/server/ci`
    - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
    - Private key: `/etc/ssl/private/ci.cluster.local.key`
    - SSL enabled: `true`

  - **status.cluster.local**
    - Template source: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
    - Destination: `/etc/nginx/sites-available/status.cluster.local`
    - Link: `/etc/nginx/sites-enabled/status.cluster.local`
    - Link target: `/etc/nginx/sites-available/status.cluster.local`
    - Document root: `/opt/server/status`
    - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
    - Private key: `/etc/ssl/private/status.cluster.local.key`
    - SSL enabled: `true`

- Uses mode `0644` for all rendered site templates.
- Delays nginx reloads when site templates or links change.
- Deletes `/etc/nginx/sites-enabled/default`.
- Delays nginx reload after deleting the default site.
- Uses two directory resources, three template resources, three link resources, and one delete-file resource.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `sshd`: restarted only when SSH hardening changes.
- UFW: enabled through firewall configuration commands.

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The recipe uses UFW commands and Debian-style nginx site directories. Validate compatibility before applying it to CentOS, including UFW availability and SSH service naming.

## Credentials

**Detection Summary**: No credentials or secrets detected across the analyzed files.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

The generated certificates are self-signed development certificates, not credentials. The certificate subject contains the static email address `admin@example.com`, but no password, token, private key content, data bag, vault reference, or external secret-manager lookup is present.

No references were detected for:

- `data_bag_item`
- `encrypted_data_bag_item`
- `chef_vault_item`
- `ChefVault::Item`
- `conjur_variable`
- CyberArk data bags
- `node['vault']`
- `node['secrets']`
- `ENV['PASSWORD']`
- `ENV['API_KEY']`

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` must be absent
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`

**Service endpoints to check**:

- HTTP: port `80`
- HTTPS: port `443`
- SSH: port `22`
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Nginx configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Site configuration files and links
test -f /etc/nginx/sites-available/test.cluster.local
test -f /etc/nginx/sites-available/ci.cluster.local
test -f /etc/nginx/sites-available/status.cluster.local

test -L /etc/nginx/sites-enabled/test.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

# test.cluster.local document root
stat -c '%U:%G %a %n' /opt/server/test
stat -c '%U:%G %a %n' /opt/server/test/index.html

# ci.cluster.local document root
stat -c '%U:%G %a %n' /opt/server/ci
stat -c '%U:%G %a %n' /opt/server/ci/index.html

# status.cluster.local document root
stat -c '%U:%G %a %n' /opt/server/status
stat -c '%U:%G %a %n' /opt/server/status/index.html

# test.cluster.local TLS
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

# ci.cluster.local TLS
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

# status.cluster.local TLS
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# test.cluster.local endpoints
curl -I --resolve test.cluster.local:80:127.0.0.1 \
  http://test.cluster.local/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# ci.cluster.local endpoints
curl -I --resolve ci.cluster.local:80:127.0.0.1 \
  http://ci.cluster.local/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# status.cluster.local endpoints
curl -I --resolve status.cluster.local:80:127.0.0.1 \
  http://status.cluster.local/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Security headers and nginx version hiding
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | grep -i '^Server:'

# Firewall
ufw status verbose
ufw status numbered

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t
systemctl status sshd || systemctl status ssh

# Kernel security
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Listening ports
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Logs
test -f /var/log/nginx/access.log
test -f /var/log/nginx/error.log
test -f /var/log/nginx/test.cluster.local_access.log
test -f /var/log/nginx/test.cluster.local_error.log
test -f /var/log/nginx/ci.cluster.local_access.log
test -f /var/log/nginx/ci.cluster.local_error.log
test -f /var/log/nginx/status.cluster.local_access.log
test -f /var/log/nginx/status.cluster.local_error.log

journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

Expected results:

- nginx and fail2ban are active and enabled.
- `nginx -t` succeeds.
- All three site names appear in the expanded nginx configuration.
- Each site has a `755` nginx-owned document root and a `644` nginx-owned index file.
- Each certificate has the correct site common name and approximately 365 days of validity.
- Each private key is owned by `root:ssl-cert` with mode `640`.
- HTTP returns `301` and redirects to the corresponding HTTPS URL.
- HTTPS returns `200 OK` and serves the corresponding index file.
- UFW is active with default incoming policy `deny` and allows ports `22`, `80`, and `443`.
- Root SSH login and SSH password authentication are disabled.
- SSH configuration validation succeeds.
- Required sysctl hardening values are applied.
- All four expected fail2ban jails are enabled.
- nginx listens on ports `80` and `443`.
- Global and per-site nginx logs exist.
- The nginx `Server` header does not expose the nginx version.