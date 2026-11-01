---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an Nginx web server hosting three HTTPS-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, SSH, sysctl, and Nginx security hardening; creates self-signed certificates and private keys; deploys static site content; and enables three Nginx virtual hosts listening on ports 80 and 443.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled static Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`
  - Static source file: `test/index.html`
  - SSL enabled: `true`

- **ci.cluster.local**: HTTPS-enabled static Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`
  - Static source file: `ci/index.html`
  - SSL enabled: `true`

- **status.cluster.local**: HTTPS-enabled static Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`
  - Static source file: `status/index.html`
  - SSL enabled: `true`

**Security configuration**:

- Fail2ban enabled
- UFW enabled with default incoming policy set to deny
- SSH root login disabled
- SSH password authentication disabled

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

No provider files are used by the executed recipes.

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

No static files under `files/default/` or `files/` were listed in the supplied cookbook analysis. The recipes reference `test/index.html`, `ci/index.html`, and `status/index.html` through dynamic `cookbook_file` resources. These source files must be verified in the actual Chef cookbook before implementing their Ansible equivalents.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Preserves the execution sequence of security hardening, Nginx installation, SSL setup, and virtual-host deployment.

2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `/etc/fail2ban/jail.local` from `fail2ban.jail.local.erb` with mode `0644`.
   - Configures a 3600-second ban time, 600-second find time, and maximum of 3 retries.
   - Configures SSH protection on `ssh` using `/var/log/auth.log`.
   - Configures Nginx HTTP authentication, request-rate, and bot-search protection on `http,https`.
   - Uses `/var/log/nginx/*error.log` and `/var/log/nginx/*access.log` for Nginx Fail2ban monitoring.
   - Applies UFW rules in this order:
     1. Default incoming policy deny.
     2. Allow SSH.
     3. Allow HTTP.
     4. Allow HTTPS.
     5. Enable UFW.
   - Preserves idempotent checks for existing UFW policies and rules.
   - Renders `/etc/sysctl.d/99-security.conf` from `sysctl-security.conf.erb` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-route rejection, martian logging, ICMP suppression, IPv6 disabling, and TCP SYN flood protection.
   - Reloads sysctl settings with `sysctl -p /etc/sysctl.d/99-security.conf` after configuration changes.
   - Disables SSH root login by setting `PermitRootLogin no`.
   - Disables SSH password authentication by setting `PasswordAuthentication no`.
   - Restarts SSH only when either SSH setting changes.
   - Resources: 1 package, 2 services, 2 templates, and 8 execute resources; total `13` resources.

3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `/etc/nginx/nginx.conf` from `nginx.conf.erb` with mode `0644`.
   - Configures the `www-data` worker user, automatic worker processes, 768 worker connections, standard access and error logs, sendfile, TCP optimizations, a 65-second keepalive timeout, gzip, and module, `conf.d`, and enabled-site includes.
   - Renders `/etc/nginx/conf.d/security.conf` from `security.conf.erb` with mode `0644`.
   - Configures Nginx version hiding, login and API rate-limit zones, small client buffers, 1K maximum client body size, 10-second client and send timeouts, TLS 1.2 and TLS 1.3, a shared 10 MB SSL session cache, a 10-minute SSL session timeout, explicit ECDHE/DHE ciphers, and preferred server ciphers.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`.
   - Deploys `/opt/server/test/index.html` from `test/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`.
   - Deploys `/opt/server/ci/index.html` from `ci/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`.
   - Deploys `/opt/server/status/index.html` from `status/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Resources: 1 package, 2 templates, 1 service, 3 directories, and 3 cookbook files; total `10` resources.

4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Checks the SSL-enabled setting before certificate creation.
   - Generates a self-signed RSA 2048-bit certificate and unencrypted private key for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
     - Validity: 365 days
     - Common name: `test.cluster.local`
   - Generates a self-signed RSA 2048-bit certificate and unencrypted private key for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
     - Validity: 365 days
     - Common name: `ci.cluster.local`
   - Generates a self-signed RSA 2048-bit certificate and unencrypted private key for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
     - Validity: 365 days
     - Common name: `status.cluster.local`
   - Uses subject values `US`, `Example`, `Example`, `Example Org`, `IT`, and `admin@example.com`.
   - Runs certificate commands only when the corresponding certificate or key is absent.
   - Sets private keys to mode `0640` and ownership `root:ssl-cert`.
   - Notifies Nginx for a delayed reload after certificate generation.
   - Resources: 1 package resource installing 2 packages, 1 group, 2 directories, and 3 execute resources; total `7` resources.

5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `/etc/nginx/sites-available/test.cluster.local` from `site.conf.erb`.
   - Links `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `/etc/nginx/sites-available/ci.cluster.local` from `site.conf.erb`.
   - Links `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `/etc/nginx/sites-available/status.cluster.local` from `site.conf.erb`.
   - Links `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Sends delayed Nginx reload notifications when virtual-host templates, links, or default-site removal changes.
   - Renders each enabled site with:
     - HTTP listener on port `80`
     - HTTP-to-HTTPS redirect
     - HTTPS listener on port `443`
     - HTTP/2
     - Site-specific document root
     - TLS 1.2 and TLS 1.3
     - HSTS with one-year max age and `includeSubDomains`
     - `X-Frame-Options DENY`
     - `X-Content-Type-Options nosniff`
     - `X-XSS-Protection`
     - `Referrer-Policy`
     - Content Security Policy
     - Gzip compression
     - `try_files $uri $uri/ =404`
     - Restrictions for `.htaccess`, `.git`, and `.svn`
     - Site-specific access and error logs
   - Site-specific template variables:
     - `test.cluster.local`: root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local`: root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
   - Resources: 3 templates, 3 links, and 1 file; total `7` resources.

**Template render counts**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `sysctl-security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders
- Total template renders: `7`

## Dependencies

**External cookbook dependencies**: None listed.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started; delayed restart after configuration changes
- `nginx`: enabled and started; delayed reload after configuration, certificate, virtual-host, or link changes
- `ssh`: restarted only after SSH hardening changes

## Credentials

**Detection Summary**: No passwords, API tokens, data bags, encrypted data bags, Chef Vault items, CyberArk references, Conjur variables, or external secret-manager integrations were detected. Three locally generated TLS private keys and three locally generated TLS certificates were identified.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### TLS Private Keys

- **Variable(s)**: `key_file`, `node['nginx']['ssl']['private_key_path']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files
- **Usage context**: Nginx HTTPS private keys
- **Paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Generation**: Self-signed, unencrypted RSA 2048-bit keys
- **Permissions**: Mode `0640`, owner and group `root:ssl-cert`
- **Migration requirement**: Protect replacement keys with Ansible Vault or an approved secret-management system.

### TLS Certificates

- **Variable(s)**: `cert_file`, `node['nginx']['ssl']['certificate_path']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed files
- **Usage context**: Nginx HTTPS server certificates
- **Paths**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`

### Certificate Subject Email

- **Variable/Value**: `admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command
- **Usage context**: Email address in the self-signed certificate subject
- **Secret status**: Not a credential or authentication secret

No database connection strings or environment-variable-based secrets were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`

**Service endpoints to check**:

- `test.cluster.local`: ports `80` and `443`
- `ci.cluster.local`: ports `80` and `443`
- `status.cluster.local`: ports `80` and `443`
- SSH: port `22`
- Nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `/etc/fail2ban/jail.local`: 1 render
- `/etc/nginx/nginx.conf`: 1 render
- `/etc/nginx/conf.d/security.conf`: 1 render
- `/etc/sysctl.d/99-security.conf`: 1 render
- `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `/etc/nginx/sites-available/status.cluster.local`: 1 render

## Pre-flight checks:

```bash
# Package status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh || systemctl status sshd

# Nginx validation
nginx -t
systemctl is-enabled nginx
systemctl is-active nginx

# Fail2ban validation
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# UFW validation
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# SSH hardening validation
grep '^PermitRootLogin no' /etc/ssh/sshd_config
grep '^PasswordAuthentication no' /etc/ssh/sshd_config
sshd -t

# Sysctl validation
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.icmp_echo_ignore_broadcasts
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries

# Listening ports
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
```

### test.cluster.local

```bash
# HTTP redirect
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
# Expected: HTTP 301 and Location: https://test.cluster.local/

# HTTPS response
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
# Expected: HTTP 200

# Content
curl -k --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# Files and permissions
stat -c '%A %U:%G %n' \
  /opt/server/test \
  /opt/server/test/index.html \
  /etc/ssl/certs/test.cluster.local.crt \
  /etc/ssl/private/test.cluster.local.key

# Virtual-host link
readlink -f /etc/nginx/sites-enabled/test.cluster.local
# Expected: /etc/nginx/sites-available/test.cluster.local

# Certificate and key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject | grep 'CN = test.cluster.local'
openssl x509 -noout -modulus \
  -in /etc/ssl/certs/test.cluster.local.crt | openssl sha256
openssl rsa -noout -modulus \
  -in /etc/ssl/private/test.cluster.local.key | openssl sha256

# Site logs
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
```

### ci.cluster.local

```bash
# HTTP redirect
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
# Expected: HTTP 301 and Location: https://ci.cluster.local/

# HTTPS response
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
# Expected: HTTP 200

# Content
curl -k --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# Files and permissions
stat -c '%A %U:%G %n' \
  /opt/server/ci \
  /opt/server/ci/index.html \
  /etc/ssl/certs/ci.cluster.local.crt \
  /etc/ssl/private/ci.cluster.local.key

# Virtual-host link
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
# Expected: /etc/nginx/sites-available/ci.cluster.local

# Certificate and key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject | grep 'CN = ci.cluster.local'
openssl x509 -noout -modulus \
  -in /etc/ssl/certs/ci.cluster.local.crt | openssl sha256
openssl rsa -noout -modulus \
  -in /etc/ssl/private/ci.cluster.local.key | openssl sha256

# Site logs
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
```

### status.cluster.local

```bash
# HTTP redirect
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
# Expected: HTTP 301 and Location: https://status.cluster.local/

# HTTPS response
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
# Expected: HTTP 200

# Content
curl -k --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Files and permissions
stat -c '%A %U:%G %n' \
  /opt/server/status \
  /opt/server/status/index.html \
  /etc/ssl/certs/status.cluster.local.crt \
  /etc/ssl/private/status.cluster.local.key

# Virtual-host link
readlink -f /etc/nginx/sites-enabled/status.cluster.local
# Expected: /etc/nginx/sites-available/status.cluster.local

# Certificate and key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject | grep 'CN = status.cluster.local'
openssl x509 -noout -modulus \
  -in /etc/ssl/certs/status.cluster.local.crt | openssl sha256
openssl rsa -noout -modulus \
  -in /etc/ssl/private/status.cluster.local.key | openssl sha256

# Site logs
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
```

### Shared Nginx and site checks

```bash
cat /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/security.conf

test ! -e /etc/nginx/sites-enabled/default
# Expected: exit status 0

grep -E 'listen 80|listen 443 ssl http2|server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/test.cluster.local

grep -E 'listen 80|listen 443 ssl http2|server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/ci.cluster.local

grep -E 'listen 80|listen 443 ssl http2|server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/status.cluster.local

tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
```