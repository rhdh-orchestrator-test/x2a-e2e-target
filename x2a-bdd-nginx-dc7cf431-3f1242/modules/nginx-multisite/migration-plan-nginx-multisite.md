---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a multi-site web server on Ubuntu or CentOS with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates document roots and index files; generates self-signed certificates; configures HTTP-to-HTTPS redirects, HTTP/2, security headers, TLS settings, rate limiting, firewall rules, SSH hardening, and kernel network-security parameters.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; deployed file `/opt/server/test/index.html`; virtual host `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; deployed file `/opt/server/ci/index.html`; virtual host `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; deployed file `/opt/server/status/index.html`; virtual host `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

- **fail2ban**: Host intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Protects SSH, HTTP, and HTTPS
  - Key Config: Package `fail2ban`; enabled and started; global `bantime = 3600`, `findtime = 600`, and `maxretry = 3`

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows SSH `22/tcp`, HTTP `80/tcp`, and HTTPS `443/tcp`
  - Key Config: Default policy deny; firewall enabled

- **ssh**: SSH service hardening
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: SSH port `22`
  - Key Config: Root login disabled; password authentication disabled; service restarted only when corresponding configuration changes

## File Structure

The following files are used by the cookbook and are listed relative to `cookbooks/nginx-multisite`.

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

No custom-resource providers are used in the execution tree.

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

No static file paths are present in the supplied directory listing. The recipes reference `cookbook_file` sources dynamically as `test/index.html`, `ci/index.html`, and `status/index.html`; these source files must be supplied separately if they exist outside the listed files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Executes the recipes in order: `security`, `nginx`, `ssl`, and `sites`.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures `bantime = 3600`, `findtime = 600`, `maxretry = 3`, backend `auto`, SSH protection using `/var/log/auth.log`, nginx authentication/rate-limit/bot-search jails, and ports `80` and `443`.
   - Sets the UFW default policy to deny and allows SSH, HTTP, and HTTPS when those rules are absent.
   - Enables UFW when it is inactive.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-route rejection, martian logging, ICMP protections, IPv6 disablement, SYN cookies, and TCP retry/backlog settings.
   - Reloads the sysctl file with `sysctl -p /etc/sysctl.d/99-security.conf` through a delayed notification.
   - Disables root SSH login with `PermitRootLogin no` when `security.ssh.disable_root` is `true`.
   - Disables SSH password authentication with `PasswordAuthentication no` when `security.ssh.password_auth` is `false`.
   - Defines `service[ssh]` with action `nothing`; it is restarted only by delayed notifications from the two SSH hardening commands.
   - Uses 1 grouped package resource, 2 service resources, 2 templates, and **8 execute resources**: `ufw_default_deny`, `ufw_allow_ssh`, `ufw_allow_http`, `ufw_allow_https`, `ufw_enable`, `reload_sysctl`, `disable root login`, and `disable password auth`.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `www-data`, automatic worker processes, PID file `/run/nginx.pid`, `768` worker connections, keepalive timeout `65`, standard access/error logs, gzip, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, rate-limit zones `login` (`10m`, `10r/m`) and `api` (`10m`, `30r/m`), small client buffers and body size, 10-second body/header/send timeouts, TLS session cache and timeout, TLS `1.2` and `1.3`, configured ciphers, and server cipher preference.
   - Enables and starts `nginx`; configuration changes trigger delayed reloads.
   - Iterates over the following three sites:
     - **test.cluster.local**: creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`; deploys source `test/index.html` to `/opt/server/test/index.html` owned by `www-data:www-data` with mode `0644`.
     - **ci.cluster.local**: creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`; deploys source `ci/index.html` to `/opt/server/ci/index.html` owned by `www-data:www-data` with mode `0644`.
     - **status.cluster.local**: creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`; deploys source `status/index.html` to `/opt/server/status/index.html` owned by `www-data:www-data` with mode `0644`.
   - Uses 1 package, 2 templates, 1 service, 3 directories, and 3 cookbook files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Iterates over the following three SSL-enabled sites:
     - **test.cluster.local**: generates `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`.
     - **ci.cluster.local**: generates `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`.
     - **status.cluster.local**: generates `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`.
   - Each certificate is a self-signed RSA 2048-bit certificate valid for `365` days, with the site name as the common name and `admin@example.com` as the subject email.
   - Each private key is owned by `root:ssl-cert` with mode `640`.
   - Generation is skipped when both certificate and key already exist.
   - Certificate generation sends a delayed reload notification to nginx.
   - Uses 1 grouped package resource, 1 group, 2 directories, and 3 execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterates over the following three sites and renders `cookbooks/nginx-multisite/templates/default/site.conf.erb`:
     - **test.cluster.local**: destination `/etc/nginx/sites-available/test.cluster.local`; document root `/opt/server/test`; certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; link `/etc/nginx/sites-enabled/test.cluster.local`.
     - **ci.cluster.local**: destination `/etc/nginx/sites-available/ci.cluster.local`; document root `/opt/server/ci`; certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; link `/etc/nginx/sites-enabled/ci.cluster.local`.
     - **status.cluster.local**: destination `/etc/nginx/sites-available/status.cluster.local`; document root `/opt/server/status`; certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; link `/etc/nginx/sites-enabled/status.cluster.local`.
   - Creates each enabled-site link to its corresponding `sites-available` file.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Template, link, and deletion changes trigger delayed nginx reloads.
   - Each rendered virtual host listens on HTTP `80` and redirects to `https://$server_name$request_uri`.
   - Each HTTPS server listens on `443 ssl http2`, uses the site-specific root and certificate files, enables TLS `1.2` and `1.3`, HSTS with `max-age=31536000; includeSubDomains`, gzip, and `try_files $uri $uri/ =404`.
   - Adds `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection`, `Referrer-Policy`, and Content Security Policy headers.
   - Denies `.htaccess`, `.git`, and `.svn` paths.
   - Writes site-specific access and error logs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Uses 3 template renders, 3 links, and 1 file deletion.

## Dependencies

**External cookbook dependencies**: None are shown in `metadata.rb`.

**System package dependencies**: `fail2ban`, `ufw`, `nginx`, `openssl`, `ca-certificates`.

**Service dependencies**:

- `fail2ban`: enabled and started; restarted when `/etc/fail2ban/jail.local` changes.
- `nginx`: enabled and started; reloaded when global configuration, security configuration, certificates, virtual-host files, links, or default-site removal changes.
- `ssh`: not started or enabled by this cookbook; restarted only when SSH hardening settings change.

**Supported platforms**: Ubuntu `>= 18.04` and CentOS `>= 7.0`. The Ansible implementation must account for differences in package names, service names, UFW availability, and SSH service naming.

## Credentials

**Detection Summary**: No external credentials, data bags, vault lookups, or API secrets were detected. Three generated TLS private keys and one non-secret certificate subject email are documented below.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Generated TLS Private Keys

- **Variable(s)**: `/etc/ssl/private/test.cluster.local.key`, `/etc/ssl/private/ci.cluster.local.key`, `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by the `openssl req` command; not retrieved from a vault or data bag
- **Usage context**: nginx TLS private keys
- **Permissions**: Mode `640`, owner `root`, group `ssl-cert`

### Self-Signed Certificate Subject Email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command
- **Usage context**: Certificate subject email address; not a password, token, or authentication secret

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, Conjur, CyberArk, environment-variable secret, database credential, API token, or hardcoded password was detected.

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
- `/etc/nginx/sites-enabled/default` must not exist
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
- `/var/log/auth.log`

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: `22`
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: 1 time
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: 1 time
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: 1 time
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: 1 time
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: 3 times
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl status nginx
systemctl status fail2ban
systemctl status ssh 2>/dev/null || systemctl status sshd

# nginx validation
nginx -t
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test ! -e /etc/nginx/sites-enabled/default

# Instance: test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
grep -E 'listen|server_name|root|ssl_certificate|ssl_certificate_key|Strict-Transport-Security' \
  /etc/nginx/sites-available/test.cluster.local

# Instance: ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
grep -E 'listen|server_name|root|ssl_certificate|ssl_certificate_key|Strict-Transport-Security' \
  /etc/nginx/sites-available/ci.cluster.local

# Instance: status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
grep -E 'listen|server_name|root|ssl_certificate|ssl_certificate_key|Strict-Transport-Security' \
  /etc/nginx/sites-available/status.cluster.local

# Expected instance behavior:
# HTTP returns a 301 redirect to HTTPS.
# HTTPS responds successfully with -k because certificates are self-signed.
# Each certificate subject contains its exact site name.
# Each private key is owned by root:ssl-cert with mode 640.

# Firewall
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# SSH hardening
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config
sshd -t

# fail2ban
fail2ban-client status
fail2ban-client status sshd
grep -E 'bantime|findtime|maxretry|backend|enabled|port|logpath' \
  /etc/fail2ban/jail.local

# Kernel security settings
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.icmp_echo_ignore_broadcasts
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries
grep -E 'rp_filter|accept_redirects|send_redirects|accept_source_route|log_martians|icmp_echo|disable_ipv6|tcp_syncookies|tcp_max_syn_backlog|tcp_synack_retries|tcp_syn_retries' \
  /etc/sysctl.d/99-security.conf

# Listening ports and nginx PID
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
test -f /run/nginx.pid
ss -tln
```