---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts nginx, creates site document roots and index files, generates self-signed certificates, redirects HTTP to HTTPS, applies nginx security headers and rate limits, configures Fail2ban and UFW, applies kernel network-hardening settings, and disables root SSH login and SSH password authentication. Certificate paths, log paths, security attributes, template contents, and platform support require confirmation against the cookbook attributes, templates, and metadata because the supplied structured analysis does not independently verify those values.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

Security settings configured by the cookbook include:

- Fail2ban enabled
- UFW enabled
- Root SSH login disabled
- SSH password authentication disabled

## File Structure

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── files/
│   └── default/
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
└── providers/
```

No custom-resource provider is used by the execution tree. No static file under `files/default/` or `files/` was listed. The `cookbook_file` resources deploy `index.html`, but the corresponding source paths were not provided and must be supplied separately for the Ansible migration.

## Module Explanation

The cookbook performs operations in this order:

1. `cookbooks/nginx-multisite/recipes/default.rb`
2. `cookbooks/nginx-multisite/recipes/security.rb`
3. `cookbooks/nginx-multisite/recipes/nginx.rb`
4. `cookbooks/nginx-multisite/recipes/ssl.rb`
5. `cookbooks/nginx-multisite/recipes/sites.rb`

### 1. Default entry recipe

**Recipe**: `cookbooks/nginx-multisite/recipes/default.rb`

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- Resources: four `include_recipe` declarations.
- Ansible equivalent: include `security.yml`, `nginx.yml`, `ssl.yml`, and `sites.yml` from `tasks/main.yml` in this order.

### 2. Security configuration

**Recipe**: `cookbooks/nginx-multisite/recipes/security.rb`

- Installs packages `fail2ban` and `ufw`.
- Enables and starts the `fail2ban` service.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configures the following Fail2ban defaults:
  - `bantime = 3600`
  - `findtime = 600`
  - `maxretry = 3`
  - `backend = auto`
- Configures the `sshd` jail for port `ssh` and `/var/log/auth.log`.
- Configures the `nginx-http-auth` jail for ports `http,https`.
- Configures the `nginx-limit-req` jail for ports `http,https` with maximum retries `10`.
- Configures the `nginx-botsearch` jail for ports `http,https` with maximum retries `2`.
- Uses nginx log patterns `/var/log/nginx/*error.log` and `/var/log/nginx/*access.log`.
- Executes UFW operations in this order:
  1. `ufw --force default deny`
  2. `ufw allow ssh`
  3. `ufw allow http`
  4. `ufw allow https`
  5. `ufw --force enable`
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Configures reverse-path filtering, redirect and source-route rejection, martian packet logging, ICMP suppression, IPv6 disabling, and TCP SYN flood protection.
- Defines `reload_sysctl` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; no triggering notification or subscription is shown.
- When `security.ssh.disable_root` is true, changes `PermitRootLogin` to `no` in `/etc/ssh/sshd_config`.
- When `security.ssh.password_auth` is false, changes `PasswordAuthentication` to `no` in `/etc/ssh/sshd_config`.
- Declares `sshd` with action `nothing`; no automatic restart or reload is shown.
- Total resource declarations: 13:
  - One package resource containing two packages
  - Two service resources
  - Two template resources
  - Eight execute resources

The exact security attribute values and template contents require confirmation against the source attributes and templates.

### 3. Base nginx installation and content

**Recipe**: `cookbooks/nginx-multisite/recipes/nginx.rb`

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Configures nginx user `nginx`, worker processes `auto`, PID `/run/nginx.pid`, worker connections `768`, access log `/var/log/nginx/access.log`, error log `/var/log/nginx/error.log`, gzip, `/etc/nginx/conf.d/*.conf`, `/etc/nginx/sites-enabled/*`, and `/usr/share/nginx/modules/*.conf`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- The described security configuration includes `server_tokens off`, `login` and `api` rate-limit zones, client buffer and timeout limits, SSL session settings, TLS `1.2` and `1.3`, and the configured cipher list. These template values require confirmation against the source template.
- Enables and starts the `nginx` service.
- Creates `/opt/server/test` and `/opt/server/test/index.html` with mode `0644`.
- Creates `/opt/server/ci` and `/opt/server/ci/index.html` with mode `0644`.
- Creates `/opt/server/status` and `/opt/server/status/index.html` with mode `0644`.
- The three index files use dynamically constructed `cookbook_file` sources based on `site_folder`; the source content is not present in the analyzed file set.
- Iterations expanded:
  - `test.cluster.local`: `/opt/server/test`, `/opt/server/test/index.html`
  - `ci.cluster.local`: `/opt/server/ci`, `/opt/server/ci/index.html`
  - `status.cluster.local`: `/opt/server/status`, `/opt/server/status/index.html`
- Total resource declarations: 10:
  - One package
  - Two templates
  - One service
  - Three directories
  - Three `cookbook_file` resources

### 4. SSL package, directories, and certificates

**Recipe**: `cookbooks/nginx-multisite/recipes/ssl.rb`

- Installs `openssl` and `ca-certificates`.
- Creates group `ssl-cert`.
- Creates `/etc/ssl/certs` with mode `0755`.
- Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
- Generates a self-signed RSA 2048-bit certificate for `test.cluster.local`:
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Common name: `test.cluster.local`
- Generates a self-signed RSA 2048-bit certificate for `ci.cluster.local`:
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Common name: `ci.cluster.local`
- Generates a self-signed RSA 2048-bit certificate for `status.cluster.local`:
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Common name: `status.cluster.local`
- Uses validity `365` days and unencrypted keys via `-nodes`.
- Uses subject values:
  - Country: `US`
  - State: `Example`
  - Locality: `Example`
  - Organization: `Example Org`
  - Organizational unit: `IT`
  - Email: `admin@example.com`
- Sets each private key to owner `root`, group `ssl-cert`, and mode `0640`.
- Iterations expanded:
  - `test.cluster.local`: certificate and key paths listed above
  - `ci.cluster.local`: certificate and key paths listed above
  - `status.cluster.local`: certificate and key paths listed above
- Total resource declarations: 7:
  - One package resource containing two packages
  - One group
  - Two directories
  - Three execute resources

The Ansible implementation should use `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate` where possible, or guarded commands when exact Chef behavior is required.

### 5. nginx site directories and virtual-host configuration

**Recipe**: `cookbooks/nginx-multisite/recipes/sites.rb`

The validated resource set contains no directory resources for `/etc/nginx/sites-available` or `/etc/nginx/sites-enabled`.

- Creates `/opt/server/test`.
- Creates `/opt/server/ci`.
- Creates `/opt/server/status`.
- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
- Creates symlink `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
- Creates symlink `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
- Creates symlink `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
- Deletes `/etc/nginx/sites-enabled/default`.

Template variables:

- `test.cluster.local`:
  - `server_name`: `test.cluster.local`
  - `document_root`: `/opt/server/test`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/test.cluster.local.key`
- `ci.cluster.local`:
  - `server_name`: `ci.cluster.local`
  - `document_root`: `/opt/server/ci`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
- `status.cluster.local`:
  - `server_name`: `status.cluster.local`
  - `document_root`: `/opt/server/status`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/status.cluster.local.key`

The described virtual-host behavior includes:

- HTTP port `80` listeners redirecting to HTTPS.
- HTTPS port `443` listeners with SSL and HTTP/2.
- Site-specific document roots.
- `index.html`, `index.htm`, and `index.php`.
- TLS `1.2` and `1.3`.
- One-year HSTS with subdomains.
- `X-Frame-Options: DENY`.
- `X-Content-Type-Options: nosniff`.
- `X-XSS-Protection: 1; mode=block`.
- `Referrer-Policy: strict-origin-when-cross-origin`.
- Content Security Policy primarily restricting content to the same origin.
- Gzip.
- `try_files $uri $uri/ =404`.
- Denial of `.htaccess`, `.git`, and `.svn` paths.
- Site-specific access and error logs.

The template behavior requires confirmation against `site.conf.erb`.

- Total resource declarations: 10:
  - Three document-root directories
  - Three templates
  - Three symlinks
  - One deleted default-site file

## Dependencies

**External cookbook dependencies**: None identified.

**System package dependencies**:

- `nginx`
- `openssl`
- `ca-certificates`
- `fail2ban`
- `ufw`

**Service dependencies**:

- `nginx`: enabled and started
- `fail2ban`: enabled and started
- `sshd`: declared with action `nothing`; no restart or reload
- UFW allows SSH, HTTP port `80`, and HTTPS port `443`

**Platform support**: Ubuntu `>= 18.04` and CentOS `>= 7.0` were stated in the original plan but are not present in the supplied structured analysis. Confirm against cookbook metadata before migration.

## Credentials

**Detection Summary**: No externally supplied authentication credentials, API tokens, data bags, encrypted data bags, Chef Vault items, CyberArk references, Conjur variables, secret environment variables, database passwords, SSH private keys, or embedded database connection strings were detected. Three locally generated TLS private keys and one hardcoded certificate subject email were identified.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: No secret-store path or data-bag path detected

### Generated TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files
- **Usage context**: nginx TLS private keys
- **Protection**: Owner `root`, group `ssl-cert`, mode `0640`

### TLS certificate subject email

- **Variable**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command
- **Usage context**: Subject email field in self-signed certificates
- **Sensitive**: Not a password or authentication secret

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
- `/etc/nginx/sites-enabled/default` should be absent
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
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
- SSH: port `22`
- Unix socket: none configured

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb`: 3 renders total

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# nginx configuration
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'
nginx -T | grep -E 'listen 80|listen 443 ssl http2'

# test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

# ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

# status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

# TLS certificates and private-key permissions
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# Security headers
curl -k -s -D - --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ -o /dev/null | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Content-Security-Policy'
curl -k -s -D - --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ -o /dev/null | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Content-Security-Policy'
curl -k -s -D - --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ -o /dev/null | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Content-Security-Policy'

# Firewall
ufw status verbose
ufw status numbered

# SSH hardening; validate before any reload
grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config
sshd -t

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Sysctl
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# Network listeners
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
ss -tlnp | grep ':22'

# Logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
tail -n 50 /var/log/auth.log
```

Expected results:

- `nginx` and `fail2ban` are active and enabled.
- nginx syntax validation succeeds.
- All three server names and listeners on ports `80` and `443` are present.
- HTTP requests to `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` return `301` redirects to HTTPS.
- HTTPS requests to all three sites return `200 OK` and serve their corresponding `index.html`.
- All three certificates are self-signed, use the matching hostname, and are valid for 365 days.
- All three private keys are owned by `root:ssl-cert` with mode `640`.
- HSTS and the configured security headers are present.
- UFW has a default incoming policy of deny and allows SSH, HTTP, and HTTPS.
- SSH configuration contains `PermitRootLogin no` and `PasswordAuthentication no`; `sshd -t` succeeds.
- The `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails are enabled.
- Sysctl values match the configured security settings.
- nginx listens on ports `80` and `443`; SSH listens on port `22`.
- nginx and Fail2ban logs contain no startup or configuration errors.
- The Chef execution tree does not restart or reload `sshd`; do not add an automatic SSH restart without a controlled operational decision.