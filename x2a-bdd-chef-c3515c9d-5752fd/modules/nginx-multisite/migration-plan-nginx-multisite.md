---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a hardened multi-site HTTPS web server on Ubuntu or CentOS. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies nginx, kernel, firewall, and SSH hardening; generates self-signed certificates; deploys static content; and configures three HTTPS-enabled virtual hosts. The Ansible migration must preserve the recipe execution order, site names, paths, ports, security settings, idempotent checks, and delayed service notifications.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled static nginx site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`; source `test/index.html`

- **ci.cluster.local**: HTTPS-enabled static nginx site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`; source `ci/index.html`

- **status.cluster.local**: HTTPS-enabled static nginx site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`; source `status/index.html`

**Security configuration**:

- fail2ban enabled
- UFW enabled with default incoming policy `deny`
- SSH root login disabled
- SSH password authentication disabled

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── recipes/
│   ├── default.rb
│   ├── security.rb
│   ├── nginx.rb
│   ├── ssl.rb
│   └── sites.rb
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
    └── [no static files listed]
```

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

No custom resource providers are used by the execution tree.

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

No static files are listed in the supplied cookbook directory listing. The cookbook nevertheless references these cookbook-file sources:

```text
test/index.html
ci/index.html
status/index.html
```

The Ansible migration must provide equivalent static content for all three sites.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that exact order.
   - Runs security configuration first.
   - Installs and starts nginx second.
   - Installs OpenSSL and generates certificates third.
   - Deploys site configurations and links last.
   - The Ansible role must preserve this ordered execution.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages without pinned versions.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban defaults:
     - Ban time: `3600`
     - Find time: `600`
     - Maximum retries: `3`
     - Backend: `auto`
   - Enables these jails:
     - `sshd`: port `ssh`, log `/var/log/auth.log`, ban time `3600`, maximum retries `3`
     - `nginx-http-auth`: ports `http,https`, log `/var/log/nginx/*error.log`, ban time `3600`, maximum retries `3`
     - `nginx-limit-req`: ports `http,https`, log `/var/log/nginx/*error.log`, ban time `3600`, maximum retries `10`
     - `nginx-botsearch`: ports `http,https`, log `/var/log/nginx/*access.log`, ban time `3600`, maximum retries `2`
   - Delayed-restarts `fail2ban` when `/etc/fail2ban/jail.local` changes.
   - Configures UFW with:
     - Default incoming policy `deny`
     - SSH allowed on `22/tcp`
     - HTTP allowed on `80/tcp`
     - HTTPS allowed on `443/tcp`
     - Firewall enabled
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies kernel security settings:
     - Enables reverse path filtering for default and all IPv4 interfaces.
     - Disables IPv4 and IPv6 ICMP redirects.
     - Disables source routing.
     - Enables martian packet logging.
     - Ignores ICMP echo requests and directed broadcast pings.
     - Disables IPv6 on all, default, and loopback interfaces.
     - Enables TCP SYN cookies.
     - Sets TCP SYN backlog to `2048`.
     - Sets TCP SYN-ACK retries to `2`.
     - Sets TCP SYN retries to `5`.
   - Delayed-executes `sysctl -p /etc/sysctl.d/99-security.conf` when the sysctl template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Delayed-restarts the SSH service when either SSH setting changes.
   - Uses `sshd` on CentOS and `ssh` on Ubuntu where no `sshd` alias exists.
   - Validates SSH configuration before restarting the service.
   - Declares the SSH service with action `nothing`; it is only notified by SSH configuration changes.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package without a pinned version.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures:
     - Worker user `nginx`
     - Worker processes `auto`
     - PID file `/run/nginx.pid`
     - Worker connections `768`
     - `sendfile` enabled
     - TCP nopush and TCP nodelay enabled
     - Keepalive timeout `65`
     - Access log `/var/log/nginx/access.log`
     - Error log `/var/log/nginx/error.log`
     - Gzip enabled
     - Includes `/etc/nginx/conf.d/*.conf`
     - Includes `/etc/nginx/sites-enabled/*`
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures:
     - `server_tokens off`
     - Rate-limit zone `login`: `10m`, `10r/m`
     - Rate-limit zone `api`: `10m`, `30r/m`
     - `client_body_buffer_size 1K`
     - `client_header_buffer_size 1k`
     - `client_max_body_size 1k`
     - `large_client_header_buffers 2 1k`
     - `client_body_timeout 10`
     - `client_header_timeout 10`
     - `send_timeout 10`
     - TLS session cache `shared:SSL:10m`
     - TLS session timeout `10m`
     - TLS protocols `TLSv1.2 TLSv1.3`
     - Explicit ECDHE/DHE cipher list
     - Server cipher preference enabled
   - Enables and starts nginx.
   - Delayed-reloads nginx when either nginx configuration template changes.
   - Creates these three document roots:
     - `/opt/server/test` for `test.cluster.local`
     - `/opt/server/ci` for `ci.cluster.local`
     - `/opt/server/status` for `status.cluster.local`
   - Uses owner `nginx`, group `nginx`, and mode `0755` for each document root.
   - Deploys these static files with owner `nginx`, group `nginx`, and mode `0644`:
     - `test/index.html` to `/opt/server/test/index.html`
     - `ci/index.html` to `/opt/server/ci/index.html`
     - `status/index.html` to `/opt/server/status/index.html`

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates` without pinned versions.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Iterates over the three configured sites:
     - `test.cluster.local`
     - `ci.cluster.local`
     - `status.cluster.local`
   - Generates a self-signed RSA 2048-bit certificate and key for each site only when both files are absent.
   - Uses a validity period of `365` days and this subject pattern:
     - `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`
   - Generates:
     - `test.cluster.local`: certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local`: certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
   - Sets every private key to owner `root`, group `ssl-cert`, and mode `0640`.
   - Delayed-reloads nginx when a certificate or key is newly generated.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates the three site document-root directories through the `nginx.sites` iteration:
     - `/opt/server/test`
     - `/opt/server/ci`
     - `/opt/server/status`
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Iterates over the three configured sites:
     - `test.cluster.local`
     - `ci.cluster.local`
     - `status.cluster.local`
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-available/status.cluster.local`
   - Uses mode `0644` for every rendered site configuration.
   - Creates these enabled-site links:
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
   - Removes `/etc/nginx/sites-enabled/default`.
   - Delayed-reloads nginx when a site template, site link, or default-site removal changes.
   - Configures every site with:
     - HTTP listener on port `80`
     - Redirect from HTTP to `https://$server_name$request_uri`
     - HTTPS listener on port `443` with HTTP/2
     - Site-specific document root
     - TLS 1.2 and TLS 1.3
     - One-year HSTS with `includeSubDomains`
     - `X-Frame-Options: DENY`
     - `X-Content-Type-Options: nosniff`
     - `X-XSS-Protection: 1; mode=block`
     - `Referrer-Policy: strict-origin-when-cross-origin`
     - Content Security Policy primarily restricting resources to `'self'`
     - Gzip compression
     - `try_files $uri $uri/ =404`
     - Denial of `.htaccess`, `.git`, and `.svn` paths
     - Site-specific access and error logs

## Dependencies

**External cookbook dependencies**: None shown in `metadata.rb`.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

Package versions are not pinned.

**Service dependencies**:

- `fail2ban`: enabled and started; delayed restart when `/etc/fail2ban/jail.local` changes
- `nginx`: enabled and started; delayed reload after configuration, certificate, site, link, or default-site changes
- `sshd` or `ssh`: restarted only when SSH hardening changes; declared with action `nothing`

**Ansible collection considerations**:

- `ansible.builtin.package`
- `ansible.builtin.service`
- `ansible.builtin.template`
- `ansible.builtin.file`
- `ansible.builtin.copy`
- `ansible.builtin.lineinfile`
- `ansible.builtin.command`
- `ansible.posix.sysctl`
- `community.general.ufw`, if available

## Credentials

**Detection Summary**: No externally sourced application credentials were detected. Six locally generated TLS artifacts are created across `cookbooks/nginx-multisite/recipes/ssl.rb` and `cookbooks/nginx-multisite/recipes/sites.rb`.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

### Self-signed TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; not stored in a data bag, vault, or external secret manager
- **Usage context**: Nginx HTTPS private keys
- **Protection**: Owner `root`, group `ssl-cert`, mode `0640`; parent directory `/etc/ssl/private` with mode `0710`

### Self-signed TLS certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: Nginx HTTPS certificate files
- **Validity**: `365` days
- **Certificate subject email**: `admin@example.com`

No hardcoded passwords, API keys, access tokens, data bags, Chef Vault items, CyberArk references, Conjur variables, or secret-manager integrations were detected.

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
/opt/server/test
/opt/server/test/index.html
/opt/server/ci
/opt/server/ci/index.html
/opt/server/status
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
```

The following file must be absent:

```text
/etc/nginx/sites-enabled/default
```

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: TCP `22`, allowed through UFW
- Nginx PID: `/run/nginx.pid`
- Unix sockets: none configured

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
# Package status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl status sshd || systemctl status ssh

# Nginx configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
nginx -T | grep -E 'listen 80|listen 443 ssl http2'

# Main nginx settings
grep -E 'user nginx|worker_processes auto|worker_connections 768|keepalive_timeout 65|gzip on' \
  /etc/nginx/nginx.conf

# Nginx security settings
grep -E 'server_tokens off|limit_req_zone|client_max_body_size|ssl_protocols|ssl_session_cache' \
  /etc/nginx/conf.d/security.conf

# Security configuration
grep -E '^\[sshd\]|^\[nginx-http-auth\]|^\[nginx-limit-req\]|^\[nginx-botsearch\]' \
  /etc/fail2ban/jail.local
grep -E 'PermitRootLogin no|PasswordAuthentication no' /etc/ssh/sshd_config
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter

# Firewall configuration
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# Default site removal
test ! -e /etc/nginx/sites-enabled/default
```

### test.cluster.local

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

grep -E 'server_name test\.cluster\.local|root /opt/server/test|listen 80|listen 443 ssl http2' \
  /etc/nginx/sites-available/test.cluster.local
grep -E 'ssl_certificate |ssl_certificate_key ' \
  /etc/nginx/sites-available/test.cluster.local

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U %G %a %n' /etc/ssl/private/test.cluster.local.key
```

### ci.cluster.local

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

grep -E 'server_name ci\.cluster\.local|root /opt/server/ci|listen 80|listen 443 ssl http2' \
  /etc/nginx/sites-available/ci.cluster.local
grep -E 'ssl_certificate |ssl_certificate_key ' \
  /etc/nginx/sites-available/ci.cluster.local

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U %G %a %n' /etc/ssl/private/ci.cluster.local.key
```

### status.cluster.local

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

grep -E 'server_name status\.cluster\.local|root /opt/server/status|listen 80|listen 443 ssl http2' \
  /etc/nginx/sites-available/status.cluster.local
grep -E 'ssl_certificate |ssl_certificate_key ' \
  /etc/nginx/sites-available/status.cluster.local

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U %G %a %n' /etc/ssl/private/status.cluster.local.key
```

