---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, SSH, kernel, and nginx security settings; creates three document roots and sample pages; generates self-signed certificates; and enables three nginx site configurations. Each site redirects HTTP port 80 to HTTPS port 443 and serves static content with HTTP/2.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; HTTP/2 enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; HTTP/2 enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; HTTP/2 enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`

**Security services and settings**:

- **fail2ban**: Enabled and started; protects SSH and nginx-related logs.
- **ufw**: Enabled with default-deny incoming policy; allows SSH, HTTP, and HTTPS.
- **sshd**: Root login disabled and password authentication disabled. The cookbook does not start or enable `sshd`.

## File Structure

The following files are actually used by the cookbook execution tree.

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

No provider files or custom resources are used by the execution tree.

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
```text
```

No static files are present in the supplied directory listing. The `nginx.rb` recipe references `test/index.html`, `ci/index.html`, and `status/index.html`; these source files must be supplied to the Ansible role if the sample pages are expected to be deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - The Ansible role should invoke task files in the same order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban defaults: ban time `3600`, find time `600`, and maximum retries `3`.
   - Configures SSH, nginx HTTP authentication, nginx request-rate, and nginx bot-search jails.
   - Applies an idempotent UFW default-deny policy.
   - Allows SSH on `22/tcp`, HTTP on `80/tcp`, and HTTPS on `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-route handling, martian logging, ICMP behavior, IPv6 disabling, TCP SYN cookies, and TCP retry/backlog settings.
   - Applies:
     - `net.ipv4.conf.default.rp_filter = 1`
     - `net.ipv4.conf.all.rp_filter = 1`
     - `net.ipv4.conf.all.accept_redirects = 0`
     - `net.ipv6.conf.all.accept_redirects = 0`
     - `net.ipv4.conf.default.accept_redirects = 0`
     - `net.ipv6.conf.default.accept_redirects = 0`
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
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` after sysctl configuration changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` only when either SSH setting changes.
   - Resource summary: 1 package declaration installing 2 packages, 2 service declarations, 2 templates, and 8 execute resources:
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
   - Configures worker user `nginx`, automatic worker processes, PID file `/run/nginx.pid`, worker connections `768`, keepalive timeout `65`, gzip, and nginx access and error logs.
   - Includes `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures server-token hiding, request-rate zones `login` (`10m`, `10r/m`) and `api` (`10m`, `30r/m`), request-size limits, 10-second client/header/send timeouts, TLS session settings, TLS 1.2 and TLS 1.3, explicit ECDHE/DHE ciphers, and server cipher preference.
   - Enables and starts nginx; configuration changes trigger a delayed nginx reload.
   - Creates the following document roots:
     - **test.cluster.local**: `/opt/server/test`, owner `nginx`, group `nginx`, mode `0755`; deploys `test/index.html` to `/opt/server/test/index.html`, owner `nginx`, group `nginx`, mode `0644`.
     - **ci.cluster.local**: `/opt/server/ci`, owner `nginx`, group `nginx`, mode `0755`; deploys `ci/index.html` to `/opt/server/ci/index.html`, owner `nginx`, group `nginx`, mode `0644`.
     - **status.cluster.local**: `/opt/server/status`, owner `nginx`, group `nginx`, mode `0755`; deploys `status/index.html` to `/opt/server/status/index.html`, owner `nginx`, group `nginx`, mode `0644`.
   - Resource summary: 1 package, 2 templates, 1 service, 3 directories, and 3 cookbook files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates certificates and keys for the three SSL-enabled sites:
     - **test.cluster.local**: certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`.
     - **ci.cluster.local**: certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`.
     - **status.cluster.local**: certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`.
   - Uses a 365-day, 2048-bit RSA self-signed certificate with subject values:
     - Country `US`
     - State `Example`
     - Locality `Example`
     - Organization `Example Org`
     - Organizational unit `IT`
     - Common name equal to the site name
     - Email `admin@example.com`
   - Sets each private key to mode `0640`, owner `root`, group `ssl-cert`.
   - Skips certificate generation only when both the certificate and key already exist.
   - Each generated certificate triggers a delayed nginx reload.
   - Resource summary: 1 package declaration installing 2 packages, 1 group, 2 directories, and 3 execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Processes the configured site collection containing exactly `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Uses a three-item directory loop. The structured execution tree reports 3 generic `directory[path]` resources; the supplied analysis does not identify fixed paths for these resources, so `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` must not be attributed to this recipe without source confirmation.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - **test.cluster.local**: destination `/etc/nginx/sites-available/test.cluster.local`; document root `/opt/server/test`; certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; link `/etc/nginx/sites-enabled/test.cluster.local`.
     - **ci.cluster.local**: destination `/etc/nginx/sites-available/ci.cluster.local`; document root `/opt/server/ci`; certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; link `/etc/nginx/sites-enabled/ci.cluster.local`.
     - **status.cluster.local**: destination `/etc/nginx/sites-available/status.cluster.local`; document root `/opt/server/status`; certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; link `/etc/nginx/sites-enabled/status.cluster.local`.
   - Creates 3 site links and deletes `/etc/nginx/sites-enabled/default`.
   - Each site configuration uses HTTP port `80`, redirects to HTTPS, listens on HTTPS port `443` with HTTP/2, and enables TLS 1.2 and TLS 1.3.
   - Adds HSTS, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection`, `Referrer-Policy`, Content Security Policy, gzip, static-file lookup using `try_files $uri $uri/ =404`, and denial rules for `.htaccess`, `.git`, and `.svn`.
   - Uses site-specific access and error logs:
     - **test.cluster.local**: `/var/log/nginx/test.cluster.local_access.log`, `/var/log/nginx/test.cluster.local_error.log`
     - **ci.cluster.local**: `/var/log/nginx/ci.cluster.local_access.log`, `/var/log/nginx/ci.cluster.local_error.log`
     - **status.cluster.local**: `/var/log/nginx/status.cluster.local_access.log`, `/var/log/nginx/status.cluster.local_error.log`
   - Changed site templates, links, or default-site deletion trigger delayed nginx reloads.
   - Resource summary: 3 directories, 3 templates, 3 links, and 1 file deletion resource; 10 resources total.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: Enabled and started; restarted when `/etc/fail2ban/jail.local` changes.
- `nginx`: Enabled and started; reloaded when nginx configuration, certificates, site templates, links, or default-site deletion changes.
- `sshd`: Not started or enabled by this cookbook; restarted when SSH hardening settings change.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: No application credentials, API tokens, database passwords, data bags, Chef Vault entries, CyberArk references, or secret-manager integrations were detected. Three locally generated TLS private keys are sensitive files.

**Source**:
  - **Provider**: None detected; certificates and keys are generated locally with OpenSSL.
  - **URL**: None.
  - **Path**: `/etc/ssl/certs` and `/etc/ssl/private`

### Self-signed TLS private keys

- **Variable(s)**: `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files; not stored in a data bag or vault.
- **Usage context**: nginx HTTPS private keys for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
- **Files**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`.

### Certificate subject email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded non-secret certificate subject value.
- **Usage context**: Email address in each self-signed certificate subject.

No passwords or access tokens are present in the supplied attributes, recipes, or templates.

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
- `/etc/nginx/sites-enabled/default` should not exist
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

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`

No Unix sockets or application backends are configured.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

**Total template render operations**: 7

## Pre-flight checks

```bash
# Package status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# Configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
sshd -t

# Listener checks
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Firewall checks
ufw status verbose
ufw status numbered

# fail2ban checks
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH hardening checks
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# Kernel security checks
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# Expected sysctl values
# net.ipv4.conf.default.rp_filter = 1
# net.ipv4.conf.all.rp_filter = 1
# net.ipv4.icmp_echo_ignore_all = 1
# net.ipv6.conf.all.disable_ipv6 = 1
# net.ipv4.tcp_syncookies = 1
# net.ipv4.tcp_max_syn_backlog = 2048
```

### test.cluster.local

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
```

Expected results: HTTP redirects to `https://test.cluster.local`; HTTPS returns normally `200`; the certificate contains `CN=test.cluster.local`; and the key is owned by `root:ssl-cert` with mode `640`.

### ci.cluster.local

```bash
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
```

Expected results: HTTP redirects to `https://ci.cluster.local`; HTTPS returns normally `200`; the certificate contains `CN=ci.cluster.local`; and the key is owned by `root:ssl-cert` with mode `640`.

### status.cluster.local

```bash
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected results: HTTP redirects to `https://status.cluster.local`; HTTPS returns normally `200`; the certificate contains `CN=status.cluster.local`; and the key is owned by `root:ssl-cert` with mode `640`.

### Certificate validation

```bash
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
```

Each certificate should be valid for 365 days from generation and contain the matching site name as its common name.

### Log verification

```bash
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
```

### Handler verification

Verify that changes invoke the expected handlers:

- `/etc/nginx/nginx.conf` → nginx reload
- `/etc/nginx/conf.d/security.conf` → nginx reload
- `/etc/nginx/sites-available/test.cluster.local` → nginx reload
- `/etc/nginx/sites-available/ci.cluster.local` → nginx reload
- `/etc/nginx/sites-available/status.cluster.local` → nginx reload
- TLS certificate or key material → nginx reload
- `/etc/fail2ban/jail.local` → fail2ban restart
- `/etc/sysctl.d/99-security.conf` → `sysctl -p /etc/sysctl.d/99-security.conf`
- SSH configuration changes → sshd restart