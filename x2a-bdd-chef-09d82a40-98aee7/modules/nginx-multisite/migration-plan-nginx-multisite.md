---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a hardened web server for three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, SSH, kernel, nginx, and fail2ban hardening; generates self-signed certificates; deploys static index pages; and configures HTTP-to-HTTPS redirects and HTTP/2 HTTPS listeners on ports 80 and 443.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **test.cluster.local**: Static nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`
  - Static content: `test/index.html` to `/opt/server/test/index.html`

- **ci.cluster.local**: Static nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`
  - Static content: `ci/index.html` to `/opt/server/ci/index.html`

- **status.cluster.local**: Static nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`
  - Static content: `status/index.html` to `/opt/server/status/index.html`

All three sites have `ssl_enabled: true`. Each site has its own server configuration, symlink, document root, certificate, private key, and log files.

Security attributes:

- Fail2ban enabled
- UFW enabled
- SSH root login disabled
- SSH password authentication disabled

## File Structure

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
```

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

No custom-resource provider is used.

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

The supplied cookbook directory listing contains no static file paths. The `cookbook_file` resources expect `test/index.html`, `ci/index.html`, and `status/index.html`; equivalent static content sources must be provided by the Ansible migration.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Preserves the logical execution order of host security, nginx installation, SSL setup, and site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw` without version pins.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures fail2ban with a 3600-second ban time, 600-second find time, three retries, the `auto` backend, and SSH/nginx jails for `ssh`, `http,https`, and nginx request-rate and bot-search protection.
   - Configures UFW with default-deny incoming policy and allows `22/tcp`, `80/tcp`, and `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Applies reverse-path filtering, disabled ICMP redirects and source routing, martian logging, ICMP protections, IPv6 disabling, SYN-cookie protection, and TCP backlog/retry settings.
   - Disables `PermitRootLogin` and `PasswordAuthentication` in `/etc/ssh/sshd_config`.
   - Uses delayed handlers to restart fail2ban and sshd and to apply sysctl settings.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx without a version pin.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Configures the nginx worker user as `nginx`, automatic worker processes, PID file `/run/nginx.pid`, 768 worker connections, standard access/error logs, sendfile, TCP optimizations, 65-second keepalive, gzip, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Configures `server_tokens off`, request-rate zones, restrictive client buffers and timeouts, SSL session settings, TLS 1.2 and TLS 1.3, and preferred server ciphers.
   - Enables and starts nginx.
   - Creates document roots and deploys static content for:
     - `test.cluster.local`: `/opt/server/test` and `/opt/server/test/index.html`
     - `ci.cluster.local`: `/opt/server/ci` and `/opt/server/ci/index.html`
     - `status.cluster.local`: `/opt/server/status` and `/opt/server/status/index.html`
   - Assigns document roots to owner `nginx`, group `nginx`, mode `0755`; assigns index files owner `nginx`, group `nginx`, mode `0644`.
   - The site iteration runs exactly three times for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates` without version pins.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with mode `0755`, owned by `root:root`.
   - Creates `/etc/ssl/private` with mode `0710`, owned by `root:ssl-cert`.
   - Generates self-signed RSA 2048 certificates for:
     - `test.cluster.local`: `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local`: `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`
   - Uses 365-day validity, `-nodes`, and subject values `US`, `Example`, `Example`, `Example Org`, `IT`, and `admin@example.com`.
   - Creates private keys as `root:ssl-cert` with mode `0640`.
   - Skips certificate generation when both certificate and key already exist.
   - Notifies nginx to reload after generating a certificate.
   - The certificate loop runs exactly three times for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates the nginx site-directory resources identified by the analyzed cookbook. The structured analysis reports three directory resources inside the site iteration, corresponding to `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; exact source paths for these resources require verification against the Chef source.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`, with document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`, with document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`, with document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`
   - Creates enabled-site links:
     - `/etc/nginx/sites-enabled/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local`
   - Removes `/etc/nginx/sites-enabled/default`.
   - Site templates and links notify a delayed nginx reload.
   - Each virtual host provides HTTP port 80 redirection to HTTPS, HTTPS port 443 with HTTP/2, TLS 1.2 and TLS 1.3, HSTS, security headers, gzip, `try_files $uri $uri/ =404`, protection for `.htaccess`, `.git`, and `.svn`, and site-specific access and error logs.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started; restarted when `/etc/fail2ban/jail.local` changes
- `nginx`: enabled and started; reloaded when nginx configuration, site configuration, links, or certificates change
- `sshd`: restarted only when SSH hardening changes

**Firewall dependencies**:

- `22/tcp` for SSH
- `80/tcp` for HTTP
- `443/tcp` for HTTPS

## Credentials

**Detection Summary**: No passwords, API tokens, data bags, encrypted data bags, Chef Vault references, CyberArk integrations, Conjur variables, or secret-manager URLs were detected. Generated TLS private keys are sensitive local files but are not sourced from an external secret provider.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### TLS Private Keys

- **Variable(s)**:
  - `node['nginx']['ssl']['private_key_path']`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by OpenSSL; not stored in a Chef data bag or vault
- **Usage context**: TLS private keys used by nginx HTTPS virtual hosts
- **Permissions**: `/etc/ssl/private` is `0710`, owned by `root:ssl-cert`; key files are `0640`, owned by `root:ssl-cert`

### Self-Signed Certificate Subject Email

- **Variable(s)**: Literal `admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded non-secret certificate subject value
- **Usage context**: Email address in generated self-signed certificate subjects
- **Security classification**: Not a password, token, or authentication credential

No database credentials, SSH keys, API keys, hardcoded passwords, or environment-variable secrets were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
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
- `/etc/nginx/sites-enabled/default` must not exist

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: `22/tcp`
- Nginx PID: `/run/nginx.pid`
- Unix socket: none

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 rendering
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 rendering
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 rendering
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 rendering
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 rendering
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 rendering
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 rendering

## Pre-flight checks

```bash
# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban
systemctl status sshd 2>/dev/null || systemctl status ssh

# Nginx configuration validation
nginx -t
systemctl reload nginx
grep -E 'worker_processes|worker_connections|access_log|error_log|gzip on' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols' \
  /etc/nginx/conf.d/security.conf

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
test -L /etc/nginx/sites-enabled/test.cluster.local
curl -I --resolve test.cluster.local:80:127.0.0.1 http://test.cluster.local/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
test -L /etc/nginx/sites-enabled/ci.cluster.local
curl -I --resolve ci.cluster.local:80:127.0.0.1 http://ci.cluster.local/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
test -L /etc/nginx/sites-enabled/status.cluster.local
curl -I --resolve status.cluster.local:80:127.0.0.1 http://status.cluster.local/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Certificate and key validation
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Firewall validation
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# fail2ban validation
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Kernel hardening
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
```

Expected results:

- nginx and fail2ban are installed, enabled, active, and running.
- `nginx -t` succeeds.
- Each HTTP endpoint returns a redirect to its corresponding HTTPS hostname.
- Each HTTPS endpoint returns `200 OK` and serves its site-specific index file.
- Each certificate is self-signed, has the expected hostname subject, and is valid for 365 days.
- Private keys are owned by `root:ssl-cert` with mode `0640`.
- UFW is active with default incoming policy deny and permits `22/tcp`, `80/tcp`, and `443/tcp`.
- `PermitRootLogin no` and `PasswordAuthentication no` are present.
- The SSH, nginx HTTP authentication, nginx request-rate, and nginx bot-search fail2ban jails are enabled.
- Kernel hardening settings are applied, including reverse-path filtering, disabled redirects and source routing, martian logging, ICMP protection, IPv6 disabling, and TCP SYN-cookie protection.