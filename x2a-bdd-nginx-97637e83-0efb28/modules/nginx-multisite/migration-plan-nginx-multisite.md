---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and configures nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies SSH, kernel, firewall, and nginx hardening; generates self-signed certificates; deploys static site content; configures HTTP-to-HTTPS redirects and HTTP/2 TLS listeners; enables the virtual hosts; and removes the default nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Static content: `/opt/server/test/index.html`, sourced from `test/index.html`
  - Logs:
    - `/var/log/nginx/test.cluster.local_access.log`
    - `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Static content: `/opt/server/ci/index.html`, sourced from `ci/index.html`
  - Logs:
    - `/var/log/nginx/ci.cluster.local_access.log`
    - `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Static content: `/opt/server/status/index.html`, sourced from `status/index.html`
  - Logs:
    - `/var/log/nginx/status.cluster.local_access.log`
    - `/var/log/nginx/status.cluster.local_error.log`

Security configuration includes fail2ban, UFW, and SSH hardening. These are security controls rather than site instances.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

**Providers:**

```text
```

No provider files are used by the execution tree.

**Templates:**

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

**Attributes:**

```text
cookbooks/nginx-multisite/attributes/default.rb
```

**Files:**

No static files under `files/default/` or `files/` are listed in the supplied cookbook directory listing. The recipes reference these `cookbook_file` sources:

```text
test/index.html
ci/index.html
status/index.html
```

These source files were not included in the supplied file listing. Do not invent additional cookbook paths until their presence is confirmed.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserve the execution sequence: host security, nginx installation and base configuration, SSL setup and certificates, then virtual hosts and site content.

2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban defaults: bantime `3600`, findtime `600`, maxretry `3`, and backend `auto`.
   - Enables the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Configures the `sshd` jail for SSH and `/var/log/auth.log`.
   - Configures the nginx authentication and request-limit jails for `http,https` and `/var/log/nginx/*error.log`.
   - Configures the nginx bot-search jail for `http,https` and `/var/log/nginx/*access.log`.
   - Uses bantime `3600`, maxretry `3` for `sshd` and `nginx-http-auth`, maxretry `10` for `nginx-limit-req`, and maxretry `2` for `nginx-botsearch`.
   - Delayed-restarts fail2ban when its jail template changes.
   - Sets the UFW default policy to deny with `ufw --force default deny`, guarded by `ufw status | grep -q "Default: deny"`.
   - Allows SSH with `ufw allow ssh`, guarded by `ufw status | grep -q "22/tcp"`.
   - Allows HTTP with `ufw allow http`, guarded by `ufw status | grep -q "80/tcp"`.
   - Allows HTTPS with `ufw allow https`, guarded by `ufw status | grep -q "443/tcp"`.
   - Enables UFW with `ufw --force enable`, guarded by `ufw status | grep -q "Status: active"`, after all required rules are present.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, disabled ICMP redirects and source routing, martian logging, ignored ICMP echo and broadcast pings, disabled IPv6, TCP SYN cookies, and TCP backlog and retry settings:
     - `net.ipv4.conf.default.rp_filter = 1`
     - `net.ipv4.conf.all.rp_filter = 1`
     - `net.ipv4.conf.all.accept_redirects = 0`
     - `net.ipv6.conf.all.accept_redirects = 0`
     - `net.ipv4.conf.default.accept_redirects = 0`
     - `net.ipv6.conf.default.accept_redirects = 0`
     - `net.ipv4.conf.all.send_redirects = 0`
     - `net.ipv4.conf.default.send_redirects = 0`
     - `net.ipv4.conf.all.accept_source_route = 0`
     - `net.ipv6.conf.all.accept_source_route = 0`
     - `net.ipv4.conf.default.accept_source_route = 0`
     - `net.ipv6.conf.default.accept_source_route = 0`
     - `net.ipv4.conf.all.log_martians = 1`
     - `net.ipv4.conf.default.log_martians = 1`
     - `net.ipv4.icmp_echo_ignore_all = 1`
     - `net.ipv4.icmp_echo_ignore_broadcasts = 1`
     - `net.ipv6.conf.all.disable_ipv6 = 1`
     - `net.ipv6.conf.default.disable_ipv6 = 1`
     - `net.ipv6.conf.lo.disable_ipv6 = 1`
     - `net.ipv4.tcp_syncookies = 1`
     - `net.ipv4.tcp_max_syn_backlog = 2048`
     - `net.ipv4.tcp_synack_retries = 2`
     - `net.ipv4.tcp_syn_retries = 5`
   - Reloads the sysctl file with `sysctl -p /etc/sysctl.d/99-security.conf` only after the template changes.
   - Disables root SSH login when `security.ssh.disable_root` is `true` by setting `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Disables SSH password authentication when `security.ssh.password_auth` is `false` by setting `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Uses guarded `sed` commands and delayed notifications to restart `service[ssh]` only when SSH configuration changes.

3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `www-data`, worker processes `auto`, PID `/run/nginx.pid`, worker connections `768`, keepalive timeout `65`, standard access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*` includes.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, login rate limit `10r/m`, API rate limit `30r/m`, 1K client buffers, maximum body size `1k`, large header buffers `2 1k`, body/header/send timeouts of `10`, TLS 1.2 and 1.3, a shared `SSL` session cache of `10m`, a `10m` TLS session timeout, configured ECDHE/DHE ciphers, and server cipher preference.
   - Delayed-reloads nginx when either nginx template changes.
   - Enables and starts the nginx service.
   - Creates `/opt/server/test` for `test.cluster.local` with owner/group `www-data`, mode `0755`, and recursive directory handling.
   - Deploys `/opt/server/test/index.html` from `test/index.html` with owner/group `www-data` and mode `0644`.
   - Creates `/opt/server/ci` for `ci.cluster.local` with owner/group `www-data`, mode `0755`, and recursive directory handling.
   - Deploys `/opt/server/ci/index.html` from `ci/index.html` with owner/group `www-data` and mode `0644`.
   - Creates `/opt/server/status` for `status.cluster.local` with owner/group `www-data`, mode `0755`, and recursive directory handling.
   - Deploys `/opt/server/status/index.html` from `status/index.html` with owner/group `www-data` and mode `0644`.
   - Iterations: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resource counts: one package, two templates, one service, three directories, and three `cookbook_file` resources.

4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate valid for 365 days when the certificate and key do not already exist.
   - Uses subject metadata `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Sets generated private keys to mode `640` and owner/group `root:ssl-cert`.
   - Generates the certificate and key for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Common name: `test.cluster.local`
     - Resource name: `generate-ssl-cert-test.cluster.local`
   - Generates the certificate and key for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Common name: `ci.cluster.local`
     - Resource name: `generate-ssl-cert-ci.cluster.local`
   - Generates the certificate and key for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Common name: `status.cluster.local`
     - Resource name: `generate-ssl-cert-status.cluster.local`
   - Each generated certificate triggers a delayed nginx reload.
   - Iterations: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resource counts: one package declaration installing two packages, one group, two directories, and three execute resources.

5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
   - Uses document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders the site configuration for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
   - Uses document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders the site configuration for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
   - Uses document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Both each template and each link trigger a delayed nginx reload.
   - Deletes `/etc/nginx/sites-enabled/default` and triggers a delayed nginx reload.
   - Each SSL-enabled site configuration contains a port 80 listener redirecting to HTTPS, a port 443 HTTP/2 TLS listener, site-specific certificate and key paths, TLS 1.2 and 1.3, one-year HSTS with subdomains, security headers, gzip, static-file `try_files`, protections for `.htaccess`, `.git`, and `.svn`, and site-specific access and error logs.
   - Iterations: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resource counts: three templates, three links, and one file deletion.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: restarted only when SSH hardening changes require it

**Operating system dependencies**:
- `www-data` user and group
- `/etc/ssh/sshd_config`
- `ssl-cert` is created by the cookbook

## Credentials

**Detection Summary**: 0 credentials detected across the supplied cookbook files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No data bags, Chef Vault, Conjur, CyberArk, HashiCorp Vault, AWS Secrets Manager, secret-related node attributes, or environment-variable secrets are used.

The generated SSL private keys are operationally sensitive but are created locally and are not retrieved from a secret store. Certificate metadata contains organization `Example Org`, organizational unit `IT`, and email address `admin@example.com`; this is not a password, token, or API key.

## Checks for the Migration

**Files to verify**:
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-enabled/default` is absent
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
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
- TCP `80` for HTTP
- TCP `443` for HTTPS
- TCP `22` for SSH
- `/run/nginx.pid` for nginx PID tracking

**Templates rendered**:
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: 3 renderings
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks

```bash
# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status and enablement
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
nginx -T | grep -E 'listen 80|listen 443 ssl http2'

# Firewall and SSH endpoints
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'
systemctl status ssh
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# Security services and kernel settings
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
cat /etc/sysctl.d/99-security.conf

# Listening ports and nginx process
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
ss -tlnp | grep ':22 '
pgrep -a nginx
cat /run/nginx.pid

# Base logs and default site
test -f /var/log/nginx/access.log
test -f /var/log/nginx/error.log
test ! -e /etc/nginx/sites-enabled/default
```

### `test.cluster.local`

```bash
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
stat -c '%U %G %a %n' /opt/server/test /opt/server/test/index.html
ls -l /etc/nginx/sites-available/test.cluster.local
ls -l /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U %G %a %n' /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: test.cluster.local' https://127.0.0.1/
test -f /var/log/nginx/test.cluster.local_access.log
test -f /var/log/nginx/test.cluster.local_error.log
```

### `ci.cluster.local`

```bash
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
stat -c '%U %G %a %n' /opt/server/ci /opt/server/ci/index.html
ls -l /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U %G %a %n' /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: ci.cluster.local' https://127.0.0.1/
test -f /var/log/nginx/ci.cluster.local_access.log
test -f /var/log/nginx/ci.cluster.local_error.log
```

### `status.cluster.local`

```bash
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
stat -c '%U %G %a %n' /opt/server/status /opt/server/status/index.html
ls -l /etc/nginx/sites-available/status.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U %G %a %n' /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: status.cluster.local' https://127.0.0.1/
test -f /var/log/nginx/status.cluster.local_access.log
test -f /var/log/nginx/status.cluster.local_error.log
```

### Certificate and key validation

```bash
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U %G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U %G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U %G %a %n' /etc/ssl/private/status.cluster.local.key
```

The expected result is an enabled and running nginx service serving all three named sites, redirecting HTTP to HTTPS, presenting a self-signed certificate for each hostname, and exposing only the intended HTTP, HTTPS, and SSH firewall rules.