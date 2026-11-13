---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies kernel and SSH hardening; generates one idempotent self-signed certificate per site; deploys static site content; and configures HTTP-to-HTTPS redirects, TLS, security headers, rate limiting, logging, and firewall rules. The Ansible implementation must preserve recipe order, exact site names, paths, ownership, permissions, handlers, conditional SSH hardening, and expanded site iterations.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The `node['nginx']['sites']` collection contains exactly three sites. All three have `ssl_enabled: true`.

- **test.cluster.local**: Static Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; content source `test/index.html`; destination `/opt/server/test/index.html`

- **ci.cluster.local**: Static Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; content source `ci/index.html`; destination `/opt/server/ci/index.html`

- **status.cluster.local**: Static Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; content source `status/index.html`; destination `/opt/server/status/index.html`

Security configuration references:

- Fail2ban is enabled.
- UFW is enabled.
- SSH root login is disabled.
- SSH password authentication is disabled.

The exact security and SSL path attribute definitions should be verified against `cookbooks/nginx-multisite/attributes/default.rb` before migration. The operational behavior described here is based on the referenced values and recipe execution tree.

## File Structure

### Recipes

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

### Providers

```text
```

No provider files or custom resources are used by the execution tree.

### Templates

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

### Attributes

```text
cookbooks/nginx-multisite/attributes/default.rb
```

### Files

No static `files/default/*` files are listed in the supplied directory analysis. The recipes use `cookbook_file` resources with dynamically constructed sources:

```text
test/index.html
ci/index.html
status/index.html
```

Equivalent Ansible source files must be available during implementation.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)
2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)
3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

### 1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- The Ansible role must preserve this order.

### 2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts `fail2ban`.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configures Fail2ban defaults:
  - Ban time: `3600`
  - Find time: `600`
  - Maximum retries: `3`
  - Backend: `auto`
  - SSH protection on `ssh`
  - Nginx authentication, rate-limit, and bot-search jails on `http,https`
  - SSH log: `/var/log/auth.log`
  - Nginx error logs: `/var/log/nginx/*error.log`
  - Nginx access logs: `/var/log/nginx/*access.log`
- Restarts Fail2ban through a delayed handler when `jail.local` changes.
- Applies UFW rules:
  - Default incoming policy: deny
  - Allow SSH: `22/tcp`
  - Allow HTTP: `80/tcp`
  - Allow HTTPS: `443/tcp`
  - Enable UFW
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Configures reverse-path filtering, redirect and source-route protections, martian logging, ICMP protections, IPv6 disabling, SYN cookies, and TCP backlog/retry settings.
- Runs `sysctl -p /etc/sysctl.d/99-security.conf` through a delayed notification when the sysctl template changes.
- When the configured SSH settings require it:
  - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
  - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
  - Restarts `sshd` through a delayed handler when either setting changes.
- Defines `service[sshd]` with action `nothing`.
- Execute resources:
  - `ufw_default_deny`
  - `ufw_allow_ssh`
  - `ufw_allow_http`
  - `ufw_allow_https`
  - `ufw_enable`
  - `reload_sysctl`
  - `disable root login`
  - `disable password auth`
- Resource summary:
  - `package`: 1 resource installing 2 packages
  - `service`: `fail2ban` and `sshd`
  - `template`: 2
  - `execute`: 8

### 3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Configures:
  - Worker user: `nginx`
  - Worker processes: `auto`
  - PID file: `/run/nginx.pid`
  - Worker connections: `768`
  - Keepalive timeout: `65`
  - Access log: `/var/log/nginx/access.log`
  - Error log: `/var/log/nginx/error.log`
  - Gzip
  - `/etc/nginx/conf.d/*.conf`
  - `/etc/nginx/sites-enabled/*`
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Configures server-token hiding, rate-limit zones, request-size/time-out limits, TLS 1.2 and 1.3, SSL session caching, explicit cipher suites, and server cipher preference.
- Enables and starts Nginx.
- Reloads Nginx through a delayed handler when either Nginx configuration template changes.

Site iterations:

1. **test.cluster.local**
   - Creates `/opt/server/test` recursively.
   - Sets owner and group to `nginx`.
   - Sets directory mode to `0755`.
   - Deploys `test/index.html` to `/opt/server/test/index.html`.
   - Sets file owner and group to `nginx`.
   - Sets file mode to `0644`.

2. **ci.cluster.local**
   - Creates `/opt/server/ci` recursively.
   - Sets owner and group to `nginx`.
   - Sets directory mode to `0755`.
   - Deploys `ci/index.html` to `/opt/server/ci/index.html`.
   - Sets file owner and group to `nginx`.
   - Sets file mode to `0644`.

3. **status.cluster.local**
   - Creates `/opt/server/status` recursively.
   - Sets owner and group to `nginx`.
   - Sets directory mode to `0755`.
   - Deploys `status/index.html` to `/opt/server/status/index.html`.
   - Sets file owner and group to `nginx`.
   - Sets file mode to `0644`.

Resource summary:

- `package`: 1
- `template`: 2
- `service`: 1
- `directory`: 3
- `cookbook_file`: 3

### 4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs `openssl` and `ca-certificates`.
- Creates group `ssl-cert`.
- Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
- Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
- Evaluates the following three sites:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`
- Generates certificates only when the corresponding certificate and key pair does not already exist.

Certificate iterations:

1. **test.cluster.local**
   - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
   - Key: `/etc/ssl/private/test.cluster.local.key`

2. **ci.cluster.local**
   - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
   - Key: `/etc/ssl/private/ci.cluster.local.key`

3. **status.cluster.local**
   - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
   - Key: `/etc/ssl/private/status.cluster.local.key`

Each certificate uses:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout <key_file> \
  -out <cert_file> \
  -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com"
chmod 640 <key_file>
chown root:ssl-cert <key_file>
```

- Certificates are RSA `2048`, self-signed, and valid for `365` days.
- A newly generated certificate triggers a delayed Nginx reload.
- The Ansible implementation must use an existence check or an idempotent certificate module and must not regenerate existing certificate/key pairs on every run.

Resource summary:

- `package`: 1 resource installing 2 packages
- `group`: 1
- `directory`: 2
- `execute`: 3

### 5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Processes the three named site instances:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`
- The structured execution tree contains three loop directory resources associated with the named site iterations. It does not show separate directory resources for `/etc/nginx/sites-available` or `/etc/nginx/sites-enabled`; those unsupported resources must not be added to the migration.
- Renders and enables the site configurations.

Site iterations:

1. **test.cluster.local**
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.

2. **ci.cluster.local**
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.

3. **status.cluster.local**
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.

Template variables:

- `server_name`
- `document_root`
- `ssl_enabled`
- `cert_file`
- `key_file`

Each rendered configuration includes:

- HTTP listener on port `80`
- HTTPS listener on port `443` with HTTP/2
- HTTP-to-HTTPS redirect
- Site-specific document root
- `index.html`, `index.htm`, and `index.php`
- TLS 1.2 and TLS 1.3
- HSTS with `max-age=31536000; includeSubDomains`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- Strict referrer policy
- Content Security Policy
- Gzip compression
- `try_files $uri $uri/ =404`
- `.htaccess`, `.git`, and `.svn` denial rules
- Site-specific access and error logs

Site logs:

- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`

- Deletes `/etc/nginx/sites-enabled/default`.
- Reloads Nginx when site templates, links, or the default-site deletion changes.

Resource summary from the structured execution tree:

- Three loop directory resources associated with the named sites
- `template`: 3
- `link`: 3
- `file`: 1
- No separate `/etc/nginx/sites-available` or `/etc/nginx/sites-enabled` directory resources are shown.

## Dependencies

**External cookbook dependencies**: None shown.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
  - Enabled and started
  - Restarted when `/etc/fail2ban/jail.local` changes
- `nginx`
  - Enabled and started
  - Reloaded when Nginx configuration, site templates, links, or certificates change
- `sshd`
  - Restarted when SSH hardening settings change

**Operating system metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

UFW is explicitly configured and is normally associated with Ubuntu. Verify the target operating system before applying the migration to CentOS.

## Credentials

**Detection Summary**: 0 external credentials detected across the analyzed files.

**Source**:
  - **Provider**: None detected
  - **URL**: Not applicable
  - **Path**: Not applicable

### Self-signed TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; no vault, data bag, or external secret provider
- **Usage context**: TLS private keys for the three Nginx HTTPS virtual hosts
- **Permissions**: Owner `root`, group `ssl-cert`, mode `0640`; parent directory mode `0710`

### Self-signed TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: TLS certificates for the three Nginx HTTPS virtual hosts
- **Validity**: `365` days
- **Key type**: RSA `2048`

No user credentials, passwords, API tokens, data bags, Chef Vault items, CyberArk references, Conjur variables, or environment-variable secrets were detected.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/etc/nginx/sites-enabled/default
/opt/server/test
/opt/server/test/index.html
/opt/server/ci
/opt/server/ci/index.html
/opt/server/status
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/private/status.cluster.local.key
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
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

`/etc/nginx/sites-enabled/default` must not exist.

**Service endpoints to check**:

- `test.cluster.local:80`
- `test.cluster.local:443`
- `ci.cluster.local:80`
- `ci.cluster.local:443`
- `status.cluster.local:80`
- `status.cluster.local:443`
- SSH `22/tcp`

No Unix sockets are configured.

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: 1 render to `/etc/nginx/nginx.conf`
- `security.conf.erb`: 1 render to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: 1 render to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: 3 renders:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active sshd

# Configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
nginx -T | grep -E 'listen 80|listen 443 ssl http2'
sshd -t

# Test site
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

# CI site
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

# Status site
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

# Expected HTTP behavior
# Each HTTP request returns 301 and redirects to HTTPS.
# Each HTTPS request normally returns 200 and serves the correct site content.

# Site links and default-site removal
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Certificate subjects and validity
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates

# Expected certificate common names:
# test.cluster.local
# ci.cluster.local
# status.cluster.local

# Private-key permissions
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
# Expected: root:ssl-cert 640

# Security headers for test.cluster.local
curl -k -s -D - --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ -o /dev/null | \
  grep -Ei 'strict-transport-security|x-frame-options|x-content-type-options|content-security-policy'

# Security headers for ci.cluster.local
curl -k -s -D - --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ -o /dev/null | \
  grep -Ei 'strict-transport-security|x-frame-options|x-content-type-options|content-security-policy'

# Security headers for status.cluster.local
curl -k -s -D - --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ -o /dev/null | \
  grep -Ei 'strict-transport-security|x-frame-options|x-content-type-options|content-security-policy'

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime|findtime|maxretry|backend|logpath|port|enabled' \
  /etc/fail2ban/jail.local

# UFW
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# Listening ports
ss -tlnp | grep -E ':(22|80|443)\b'
```

Expected results:

- Nginx and Fail2ban are enabled and running.
- SSH is running.
- All five system packages are installed.
- `nginx -t` and `sshd -t` succeed.
- All three sites have HTTP port `80` and HTTPS port `443` listeners.
- HTTP redirects to HTTPS for all three sites.
- HTTPS serves the correct content for each named site.
- UFW is active with default incoming policy `deny`.
- Ports `22/tcp`, `80/tcp`, and `443/tcp` are allowed.
- `PermitRootLogin no` and `PasswordAuthentication no` are present.
- Fail2ban provides the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
- Expected kernel values include:
  - `net.ipv4.conf.default.rp_filter = 1`
  - `net.ipv4.conf.all.rp_filter = 1`
  - `net.ipv4.conf.all.accept_redirects = 0`
  - `net.ipv6.conf.all.accept_redirects = 0`
  - `net.ipv4.conf.all.accept_source_route = 0`
  - `net.ipv4.icmp_echo_ignore_all = 1`
  - `net.ipv4.tcp_syncookies = 1`
  - `net.ipv4.tcp_max_syn_backlog = 2048`
  - `net.ipv6.conf.all.disable_ipv6 = 1`