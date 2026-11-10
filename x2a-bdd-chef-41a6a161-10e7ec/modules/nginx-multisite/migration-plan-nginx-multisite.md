---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It applies security hardening, installs nginx, fail2ban, UFW, OpenSSL, and CA certificates, generates self-signed certificates, deploys static content, configures HTTP-to-HTTPS redirects, and enables nginx site configurations. Preserve the recipe execution order: security, nginx installation and base configuration, SSL certificate generation, and virtual-host configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS static site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; content source `test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS static site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; content source `ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS static site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; content source `status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

**Security configuration**:

- **fail2ban**: enabled and started; configuration at `/etc/fail2ban/jail.local`
- **ufw**: enabled with default-deny incoming policy; SSH, HTTP, and HTTPS allowed
- **ssh**: root login disabled; password authentication disabled

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

No provider files are used by the execution tree.

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

No static files are present in the supplied directory listing. The recipes reference `test/index.html`, `ci/index.html`, and `status/index.html` through `cookbook_file` resources, but those source files must be supplied before migration to reproduce the deployed content.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserve this exact execution order in Ansible using ordered task-file inclusion or equivalent role task sections.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban defaults: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Enables the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails with their configured ports, log patterns, ban times, and retry limits.
   - Delayed-restarts `fail2ban` when the jail configuration changes.
   - Applies UFW default-deny policy and allows SSH, HTTP, and HTTPS using idempotent checks.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, disabled ICMP redirects and source routing, martian logging, ignored pings, disabled IPv6, TCP SYN cookies, and TCP backlog/retry settings.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` through a delayed notification when the sysctl template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` when root-login hardening is enabled.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` when password-authentication hardening is disabled.
   - Delayed-restarts `sshd` when either SSH hardening setting changes.
   - Resource order: package installation, `fail2ban` service, jail template, UFW commands, sysctl template and reload, conditional SSH-hardening commands, and `sshd` service declaration.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the unpinned `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures nginx user `nginx`, automatic worker processes, PID `/run/nginx.pid`, 768 worker connections, sendfile, TCP optimizations, 65-second keepalive timeout, global logs, gzip, MIME types, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, request-rate zones, client buffer and timeout limits, 1K maximum body size, TLS 1.2 and 1.3, TLS session caching, configured ciphers, and server cipher preference.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` owned by `nginx:nginx` with mode `0755`, then deploys `test/index.html` to `/opt/server/test/index.html` owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/ci` owned by `nginx:nginx` with mode `0755`, then deploys `ci/index.html` to `/opt/server/ci/index.html` owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/status` owned by `nginx:nginx` with mode `0755`, then deploys `status/index.html` to `/opt/server/status/index.html` owned by `nginx:nginx` with mode `0644`.
   - Iterations: the site directory and content loop runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Changed nginx templates trigger delayed nginx reloads.
   - Resource order: nginx package, main configuration template, security configuration template, nginx service, three directories, and three `cookbook_file` resources.
   - No `group[nginx]` resource is present in the analyzed recipe.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates self-signed 365-day RSA 2048-bit certificates when the certificate and key do not already exist.
   - Uses `openssl req -x509 -nodes -days 365 -newkey rsa:2048` with site-specific subjects.
   - Sets generated private keys to mode `0640` and ownership `root:ssl-cert`.
   - Delayed-reloads nginx when a certificate or key is generated.
   - Iterations: SSL generation runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, because all have `ssl_enabled: true`.
   - `test.cluster.local`: certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`, subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`.
   - `ci.cluster.local`: certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`, subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`.
   - `status.cluster.local`: certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`, subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled`, owned by `root:root` with mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for each site.
   - `test.cluster.local`: renders `/etc/nginx/sites-available/test.cluster.local` with root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`; creates symlink `/etc/nginx/sites-enabled/test.cluster.local`.
   - `ci.cluster.local`: renders `/etc/nginx/sites-available/ci.cluster.local` with root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`; creates symlink `/etc/nginx/sites-enabled/ci.cluster.local`.
   - `status.cluster.local`: renders `/etc/nginx/sites-available/status.cluster.local` with root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`; creates symlink `/etc/nginx/sites-enabled/status.cluster.local`.
   - Each site provides HTTP port `80` to HTTPS redirection, HTTPS port `443` with HTTP/2, TLS 1.2 and 1.3, HSTS, security headers, gzip, `try_files`, and protection for `.htaccess`, `.git`, and `.svn`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Changed site templates, symlinks, or default-site removal trigger delayed nginx reloads.
   - Iterations: site-template and symlink loops run for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: restarted only when SSH hardening changes
- UFW: enabled through firewall configuration

**Supported platforms**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

Package versions are not pinned.

## Credentials

**Detection Summary**: No passwords, API tokens, data bags, Chef Vault items, CyberArk references, Conjur variables, database credentials, or environment-variable secrets were detected. Three generated TLS private keys are sensitive artifacts, but they are not supplied through a secret manager.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Generated TLS private keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`; `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by OpenSSL; not stored in a data bag, vault, or external secret manager.
- **Usage context**: TLS private keys used by nginx for the three HTTPS virtual hosts.
- **Permissions**: Mode `0640`, owned by `root:ssl-cert`.
- **Migration guidance**: Preserve mode `0640` and ownership `root:ssl-cert`. Obtain production replacement certificates through the approved certificate or secret-management process.

### Certificate subject email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate subject value.
- **Usage context**: Included as the email address in each self-signed certificate subject.
- **Security classification**: Not a password, token, or authentication credential.

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
- `/etc/nginx/sites-enabled/default` is absent
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/opt/server/test`
- `/opt/server/ci`
- `/opt/server/status`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/ssl/certs`
- `/etc/ssl/private`

**Service endpoints to check**:
- `test.cluster.local:80` and `test.cluster.local:443`
- `ci.cluster.local:80` and `ci.cluster.local:443`
- `status.cluster.local:80` and `status.cluster.local:443`
- SSH `22/tcp`
- No Unix sockets or custom IPC endpoints are configured.

**Templates rendered**:
- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

Total template render operations: 7.

## Pre-flight checks:

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# nginx configuration
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'

# test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
readlink -f /etc/nginx/sites-enabled/test.cluster.local

# ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
readlink -f /etc/nginx/sites-enabled/ci.cluster.local

# status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
readlink -f /etc/nginx/sites-enabled/status.cluster.local

# TLS certificates and private-key permissions
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%A %U:%G %n' /etc/ssl/private/test.cluster.local.key
stat -c '%A %U:%G %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%A %U:%G %n' /etc/ssl/private/status.cluster.local.key

# Ports and processes
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
pgrep -a nginx

# UFW
ufw status verbose
ufw status numbered

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t
systemctl status sshd

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
tail -n 50 /var/log/auth.log
journalctl -u fail2ban --no-pager -n 50
journalctl -u nginx --no-pager -n 50

# Security headers
curl -k -s -D - --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ -o /dev/null
curl -k -s -D - --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ -o /dev/null
curl -k -s -D - --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ -o /dev/null

# Default site removal
test ! -e /etc/nginx/sites-enabled/default
```

Expected results include:

- nginx and fail2ban are active and enabled.
- `nginx -t` succeeds and the expanded configuration contains all three hostnames.
- Each HTTP endpoint returns a `301` redirect to HTTPS.
- Each HTTPS endpoint returns `200 OK` and serves its site content.
- Each site has its expected certificate, private key, configuration, and symlink.
- Certificates are valid for 365 days from generation and contain their respective hostnames.
- Private keys are `0640` and owned by `root:ssl-cert`.
- nginx listens on ports `80` and `443`.
- UFW is active, denies incoming traffic by default, and allows SSH, HTTP, and HTTPS.
- SSH root login and password authentication are disabled while SSH remains available.
- Required kernel security settings are active.
- All four fail2ban jails are enabled and available.
- HTTPS responses include HSTS, `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`, and `Content-Security-Policy`.
- The default nginx site is absent or not enabled.