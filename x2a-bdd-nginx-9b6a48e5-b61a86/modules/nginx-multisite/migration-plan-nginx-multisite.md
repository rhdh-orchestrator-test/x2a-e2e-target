---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies kernel and SSH hardening; generates self-signed certificates; deploys static content; renders and enables three Nginx virtual-host configurations; redirects HTTP to HTTPS; and removes the default Nginx site. The Ansible implementation must preserve recipe order, idempotent guards, delayed service notifications, certificate paths, permissions, and all three site names.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; logs `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; logs `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; logs `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`

**Security configuration**:

- Fail2ban enabled with service `fail2ban`
- UFW enabled
- SSH root login disabled
- SSH password authentication disabled

The cookbook supports Ubuntu `>= 18.04` and CentOS `>= 7.0`.

## File Structure

The following files are used by the cookbook and are listed relative to the cookbook root.

**Recipes:**
```text
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

**Providers:**
```text
```

No provider files or custom-resource providers are used.

**Templates:**
```text
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb
```

**Attributes:**
```text
attributes/default.rb
```

**Files:**
```text
```

No static files under `files/default/*` or `files/*` are listed in the supplied cookbook directory listing. The recipes reference these `cookbook_file` sources:

```text
test/index.html
ci/index.html
status/index.html
```

Equivalent source files must be supplied in the Ansible implementation or their absence must be addressed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - Ansible task imports must preserve this order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw` with package state `present`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures defaults of ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Configures the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Applies UFW default-deny policy.
   - Allows SSH on TCP port `22`, HTTP on TCP port `80`, and HTTPS on TCP port `443`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Reloads sysctl settings with `sysctl -p /etc/sysctl.d/99-security.conf` when the sysctl template changes.
   - Disables SSH root login by setting `PermitRootLogin no`.
   - Disables SSH password authentication by setting `PasswordAuthentication no`.
   - Restarts `ssh` only when either SSH hardening setting changes.
   - Uses eight execute resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `www-data`, automatic worker processes, PID `/run/nginx.pid`, worker connections `768`, keepalive timeout `65`, standard access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures server-token hiding, request limits, client buffer and timeout limits, TLS session settings, TLS `1.2` and `1.3`, the configured cipher list, and preferred server ciphers.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`.
   - Deploys `/opt/server/test/index.html` from `test/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`.
   - Deploys `/opt/server/ci/index.html` from `ci/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`.
   - Deploys `/opt/server/status/index.html` from `status/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Sends delayed Nginx reload notifications when base configuration or security configuration changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate and key for `test.cluster.local` only when both files are absent:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Resource: `execute[generate-ssl-cert-test.cluster.local]`
   - Generates a self-signed RSA 2048-bit certificate and key for `ci.cluster.local` only when both files are absent:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Resource: `execute[generate-ssl-cert-ci.cluster.local]`
   - Generates a self-signed RSA 2048-bit certificate and key for `status.cluster.local` only when both files are absent:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Resource: `execute[generate-ssl-cert-status.cluster.local]`
   - Uses 365-day validity and a subject common name matching each site name.
   - Sets private keys to mode `0640` and ownership `root:ssl-cert`.
   - Sends delayed Nginx reload notifications after certificate generation.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with variables for the hostname, `/opt/server/test`, SSL enabled, and the test certificate and key.
   - Links `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with variables for the hostname, `/opt/server/ci`, SSL enabled, and the CI certificate and key.
   - Links `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with variables for the hostname, `/opt/server/status`, SSL enabled, and the status certificate and key.
   - Links `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Sends delayed Nginx reload notifications for virtual-host templates, links, and default-site deletion.

Each virtual host contains:

- An HTTP listener on port `80` that redirects to `https://$server_name$request_uri`.
- An HTTPS listener on port `443 ssl http2`.
- Site-specific document root and certificate paths.
- TLS `1.2` and `1.3`.
- HSTS for one year including subdomains.
- `X-Frame-Options: DENY`.
- `X-Content-Type-Options: nosniff`.
- `X-XSS-Protection: 1; mode=block`.
- Strict referrer policy.
- Content Security Policy.
- Gzip compression.
- `try_files $uri $uri/ =404`.
- Denial of `.htaccess`, `.git`, and `.svn` paths.

## Dependencies

**External cookbook dependencies**: None listed.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started; restarted when `/etc/fail2ban/jail.local` changes
- `nginx`: enabled and started; reloaded after relevant configuration, certificate, virtual-host, link, and default-site changes
- `ssh`: not enabled or started by this cookbook; restarted only after SSH hardening changes

**Kernel configuration dependency**:

- `/etc/sysctl.d/99-security.conf`
- Reload command: `sysctl -p /etc/sysctl.d/99-security.conf`

## Credentials

**Detection Summary**: No externally supplied credentials were detected. Three generated TLS private keys and three generated self-signed certificates are created locally.

**Source**:
  - **Provider**: Internal OpenSSL generation
  - **URL**: None
  - **Path**: `/etc/ssl/certs/<site_name>.crt` and `/etc/ssl/private/<site_name>.key`

### Generated TLS private keys

- **Variable(s)**: `key_file`, `node['nginx']['ssl']['private_key_path']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by OpenSSL; no Vault, data bag, environment-variable, CyberArk, Conjur, or external secret-provider source
- **Usage context**: Nginx HTTPS private keys
- **Generated paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: `root:ssl-cert`, mode `0640`

### Generated self-signed certificates

- **Variable(s)**: `cert_file`, `node['nginx']['ssl']['certificate_path']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: Nginx HTTPS server certificates
- **Generated paths**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`

### Hardcoded certificate subject email

- **Variable**: `emailAddress=admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command
- **Usage context**: Subject metadata in generated self-signed certificates
- **Secret status**: Not a credential or authentication secret

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/etc/nginx/sites-enabled/default
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/private/status.cluster.local.key
/opt/server/test/index.html
/opt/server/ci/index.html
/opt/server/status/index.html
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/test.cluster.local_access.log
/var/log/nginx/test.cluster.local_error.log
/var/log/nginx/ci.cluster.local_access.log
/var/log/nginx/ci.cluster.local_error.log
/var/log/nginx/status.cluster.local_access.log
/var/log/nginx/status.cluster.local_error.log
/var/log/auth.log
```

`/etc/nginx/sites-enabled/default` must not exist after deployment.

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: TCP `22`

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `sysctl-security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks:

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl status nginx
systemctl status fail2ban
systemctl status ssh

# Nginx configuration and listeners
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
ss -tlnp | grep -E ':80 |:443 '
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Test instance: test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head
ls -l /opt/server/test/index.html
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates

# Test instance: ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head
ls -l /opt/server/ci/index.html
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates

# Test instance: status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head
ls -l /opt/server/status/index.html
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Enabled-site links and removed default site
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# TLS permissions
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E '^(bantime|findtime|maxretry|backend)' /etc/fail2ban/jail.local

# UFW
ufw status verbose
ufw status numbered

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t

# Kernel hardening
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.tcp_syncookies
```

Expected results:

- `nginx -t` succeeds and all three hostnames appear in the expanded configuration.
- Each HTTP endpoint returns `301`.
- Each HTTPS endpoint returns a successful response, normally `200`.
- `test.cluster.local` serves `/opt/server/test/index.html` and has certificate CN `test.cluster.local`.
- `ci.cluster.local` serves `/opt/server/ci/index.html` and has certificate CN `ci.cluster.local`.
- `status.cluster.local` serves `/opt/server/status/index.html` and has certificate CN `status.cluster.local`.
- Nginx listens on TCP ports `80` and `443`.
- Each enabled-site link resolves to its corresponding `sites-available` file.
- `/etc/nginx/sites-enabled/default` does not exist.
- TLS keys are owned by `root:ssl-cert` with mode `640`; `/etc/ssl/private` is owned by `root:ssl-cert` with mode `710`.
- The four configured Fail2ban jails are present and active.
- UFW is active with default incoming policy `deny`; SSH, HTTP, and HTTPS are allowed.
- SSH root login and password authentication are disabled.
- SSH configuration validation succeeds.
- Kernel security settings are applied.

**Attribute verification**: The supplied validation confirms the three site names and document roots from the execution tree. The SSL path values and security defaults asserted for `cookbooks/nginx-multisite/attributes/default.rb` were not present in the separate structured attribute analysis and must be verified against that file before migration.