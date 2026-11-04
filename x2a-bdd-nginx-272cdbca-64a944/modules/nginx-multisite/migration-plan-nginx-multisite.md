---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; creates site roots and index files; generates self-signed certificates; deploys per-site Nginx configurations; redirects HTTP to HTTPS; applies Nginx, kernel, firewall, Fail2ban, and SSH hardening; and removes the default Nginx site. Security attribute values, site ownership details, and certificate path attributes require verification against the source attributes and recipes before migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The analyzed site collection contains these three explicitly named sites. All three are configured with SSL enabled in the migration specification.

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: HTTP/2, TLS 1.2 and 1.3, HSTS, security headers, gzip, `try_files $uri $uri/ =404`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Site configuration: `/etc/nginx/sites-available/test.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/test.cluster.local`
  - Static file: `/opt/server/test/index.html`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: HTTP/2, TLS 1.2 and 1.3, HSTS, security headers, gzip, `try_files $uri $uri/ =404`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Site configuration: `/etc/nginx/sites-available/ci.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/ci.cluster.local`
  - Static file: `/opt/server/ci/index.html`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: HTTP/2, TLS 1.2 and 1.3, HSTS, security headers, gzip, `try_files $uri $uri/ =404`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Site configuration: `/etc/nginx/sites-available/status.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/status.cluster.local`
  - Static file: `/opt/server/status/index.html`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`

Security controls are also configured or intended for the host:

- Fail2ban service with SSH and Nginx jails
- UFW default-deny policy with SSH, HTTP, and HTTPS allowed
- SSH root-login and password-authentication hardening
- Kernel networking hardening through `/etc/sysctl.d/99-security.conf`

The security attribute values and whether these controls are conditionally enabled must be verified from `attributes/default.rb` and the source recipes.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
Recipes:
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb

Providers:
No provider files or custom-resource providers are used by the execution tree.

Templates:
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb

Attributes:
attributes/default.rb

Files:
No static file path is listed in the supplied directory listing. The recipes use cookbook_file resources for site index files, but those source files are not included in the provided file list and must not be inferred as additional cookbook files.
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the dependency order of security configuration, Nginx installation, SSL prerequisites, and per-site configuration.
   - Resources: four `include_recipe` calls.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban defaults of ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Configures the `sshd` jail on SSH using `/var/log/auth.log`.
   - Configures the `nginx-http-auth` jail on HTTP and HTTPS using `/var/log/nginx/*error.log`.
   - Configures the `nginx-limit-req` jail on HTTP and HTTPS using `/var/log/nginx/*error.log`, with maximum retries `10`.
   - Configures the `nginx-botsearch` jail on HTTP and HTTPS using `/var/log/nginx/*access.log`, with maximum retries `2`.
   - Sends a delayed restart notification to `service[fail2ban]` when the Fail2ban template changes.
   - Applies UFW rules through five guarded commands:
     - `ufw --force default deny`
     - `ufw allow ssh`
     - `ufw allow http`
     - `ufw allow https`
     - `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-route protections, martian logging, ICMP protections, IPv6 disabling, TCP SYN cookies, and TCP backlog and retry settings.
   - Defines `execute[reload_sysctl]` with action `nothing`; a changed sysctl template notifies it on a delayed basis.
   - When the source attributes enable root-login hardening, changes `PermitRootLogin` to `no` in `/etc/ssh/sshd_config`.
   - When the source attributes disable password authentication, changes `PasswordAuthentication` to `no` in `/etc/ssh/sshd_config`.
   - Defines `service[ssh]` with action `nothing` as the delayed notification target.
   - Security attribute values must be verified from `attributes/default.rb` and the source recipe before migration.
   - Resources: one package resource installing two packages, two service resources, two templates, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures the `www-data` worker user, `/run/nginx.pid`, automatic worker processes, `768` worker connections, `65`-second keepalive timeout, standard access and error logs, gzip, and the `conf.d` and `sites-enabled` include paths.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, request-rate zones for `login` and `api`, request and header buffer limits, a `1k` client body limit, ten-second client/header/send timeouts, TLS 1.2 and 1.3, an SSL session cache, a ten-minute SSL session timeout, and preferred server ciphers.
   - Sends delayed reload notifications to `service[nginx]` when either global Nginx template changes.
   - Enables and starts `service[nginx]`.
   - Creates the `test.cluster.local` document root at `/opt/server/test` and deploys its index file to `/opt/server/test/index.html`.
   - Creates the `ci.cluster.local` document root at `/opt/server/ci` and deploys its index file to `/opt/server/ci/index.html`.
   - Creates the `status.cluster.local` document root at `/opt/server/status` and deploys its index file to `/opt/server/status/index.html`.
   - The supplied specification assigns `www-data` ownership, group ownership, modes, and recursive directory creation to these paths; these properties require verification against the source recipe.
   - The supplied execution analysis identifies three directory resources and three `cookbook_file` resources. It does not validate a `group[www-data]` Chef resource; preserve `www-data` as an ownership requirement only if confirmed by source.
   - Iterations:
     - `test.cluster.local` → source `test/index.html`
     - `ci.cluster.local` → source `ci/index.html`
     - `status.cluster.local` → source `status/index.html`

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed certificate and private key for `test.cluster.local`.
   - Generates a self-signed certificate and private key for `ci.cluster.local`.
   - Generates a self-signed certificate and private key for `status.cluster.local`.
   - Skips certificate generation when both the corresponding certificate and private-key files already exist.
   - Sets generated private keys to mode `0640` and ownership `root:ssl-cert`.
   - Uses a 365-day, 2048-bit RSA certificate with the subject organization values from the source command and the hostname-specific common name.
   - Sends a delayed reload notification to `service[nginx]` after certificate generation.
   - Iterations:
     - `test.cluster.local` → `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local` → `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local` → `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to the test site configuration.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to the CI site configuration.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to the status site configuration.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Sends delayed Nginx reload notifications from changed site templates, enabled links, and default-site removal.
   - Uses these site template variables:
     - `test.cluster.local`: document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local`: document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
   - Renders HTTP port `80` listeners that redirect to HTTPS.
   - Renders HTTPS port `443` listeners with HTTP/2, hostname-specific certificates, TLS 1.2 and 1.3, HSTS, security headers, gzip, `try_files $uri $uri/ =404`, and denial rules for `.htaccess`, `.git`, and `.svn`.
   - Renders site-specific access and error logs.
   - Iterations:
     - `test.cluster.local`
     - `ci.cluster.local`
     - `status.cluster.local`

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**Chef runtime support**: Chef `>= 16.0`

**Supported operating systems**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `nginx`: enabled and started
- `fail2ban`: enabled and started
- `ssh`: restarted only through delayed notifications when SSH hardening changes

**Required operating-system accounts and groups**:

- `www-data` user and group for site content, subject to source verification
- `ssl-cert` group for private-key access
- `root` ownership for certificate and private-key directories

## Credentials

**Detection Summary**: No passwords, tokens, API keys, database credentials, or externally supplied secrets detected.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, Conjur, CyberArk, Vault attributes, environment-based secrets, or hardcoded passwords were detected.

### TLS private keys

- **Variable(s)**: `key_file`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by the `openssl req` command
- **Usage context**: TLS private keys for the `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` HTTPS virtual hosts
- **Paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: Mode `0640`, owned by `root:ssl-cert`
- **Migration handling**: Protect with restrictive permissions and do not print contents

These are sensitive cryptographic files, but they are generated artifacts rather than credentials supplied through Chef Vault, data bags, environment variables, or hardcoded passwords.

### Certificate subject email

- **Variable/value**: `emailAddress=admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate subject value
- **Usage context**: Contact field in the self-signed certificate subject
- **Secret status**: Not a password, token, API key, or credential

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` is absent
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
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/opt/server/test`
- `/opt/server/ci`
- `/opt/server/status`

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`
- Unix sockets: None configured

**Logs to verify**:

- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`
- `/var/log/auth.log`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 rendering
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 rendering
- `site.conf.erb`: 3 total renderings

## Pre-flight checks

```bash
# Package and service checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
  rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl status nginx
systemctl status fail2ban
systemctl status ssh

# Configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Global Nginx configuration
grep -E 'worker_processes|worker_connections|access_log|error_log|gzip' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Site content and configuration: test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
grep -E 'listen 80|listen 443 ssl http2|server_name test\.cluster\.local|root /opt/server/test|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates

# Site content and configuration: ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
grep -E 'listen 80|listen 443 ssl http2|server_name ci\.cluster\.local|root /opt/server/ci|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates

# Site content and configuration: status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
grep -E 'listen 80|listen 443 ssl http2|server_name status\.cluster\.local|root /opt/server/status|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Default site and permissions
test ! -e /etc/nginx/sites-enabled/default
stat -c '%U:%G %a %n' /etc/ssl/certs /etc/ssl/private
stat -c '%U:%G %a %n' \
  /opt/server/test /opt/server/test/index.html \
  /opt/server/ci /opt/server/ci/index.html \
  /opt/server/status /opt/server/status/index.html

# HTTP and HTTPS endpoint checks
curl -k -I --resolve test.cluster.local:80:127.0.0.1 \
  http://test.cluster.local/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

curl -k -I --resolve ci.cluster.local:80:127.0.0.1 \
  http://ci.cluster.local/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

curl -k -I --resolve status.cluster.local:80:127.0.0.1 \
  http://status.cluster.local/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Content checks
curl -k --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | grep -E 'test|html'
curl -k --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ | grep -E 'ci|html'
curl -k --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ | grep -E 'status|html'

# Firewall
ufw status verbose
ufw status numbered

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime|findtime|maxretry|backend|enabled|port|logpath' \
  /etc/fail2ban/jail.local

# SSH hardening
grep -E '^PermitRootLogin no$|^PasswordAuthentication no$' \
  /etc/ssh/sshd_config

# Kernel security
sysctl -p /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
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
```

Expected endpoint behavior:

- `test.cluster.local:80` returns an HTTP `301` redirect to HTTPS.
- `test.cluster.local:443` returns a successful response and serves `/opt/server/test/index.html`.
- `ci.cluster.local:80` returns an HTTP `301` redirect to HTTPS.
- `ci.cluster.local:443` returns a successful response and serves `/opt/server/ci/index.html`.
- `status.cluster.local:80` returns an HTTP `301` redirect to HTTPS.
- `status.cluster.local:443` returns a successful response and serves `/opt/server/status/index.html`.

Expected security checks:

- UFW is active with default incoming policy `deny`.
- TCP ports `22`, `80`, and `443` are allowed.
- Fail2ban exposes the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
- SSH configuration contains `PermitRootLogin no` and `PasswordAuthentication no` when those source settings are enabled.
- Each certificate subject contains its corresponding hostname.
- Nginx responses include HSTS, `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`, and `Content-Security-Policy` headers.
