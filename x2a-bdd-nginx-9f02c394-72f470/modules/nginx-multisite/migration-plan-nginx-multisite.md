---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates document roots and index files; generates 365-day self-signed RSA certificates; applies nginx, kernel, firewall, and SSH hardening; and configures HTTP-to-HTTPS redirection for all three sites.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; index `/opt/server/test/index.html`; logs `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; index `/opt/server/ci/index.html`; logs `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; index `/opt/server/status/index.html`; logs `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`

Security configuration includes enabled fail2ban and UFW, SSH root-login disabling, and SSH password-authentication disabling.

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

The cookbook uses `cookbook_file` resources for these three required static files, although their source paths are not present in the supplied directory listing:

```text
/opt/server/test/index.html
/opt/server/ci/index.html
/opt/server/status/index.html
```

The Ansible migration must provide equivalent content or source files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Provides no direct resource management.
   - The Ansible role must preserve the same conceptual order: security prerequisites, nginx configuration, SSL setup, then site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `/etc/fail2ban/jail.local` from `fail2ban.jail.local.erb` with `bantime=3600`, `findtime=600`, `maxretry=3`, SSH monitoring on `/var/log/auth.log`, nginx authentication and rate-limit jails, and nginx bot-search monitoring.
   - Applies UFW commands in this order: default deny, allow SSH, allow HTTP, allow HTTPS, then enable UFW.
   - Renders `/etc/sysctl.d/99-security.conf` and reloads it through a delayed handler.
   - Disables `PermitRootLogin` and `PasswordAuthentication` in `/etc/ssh/sshd_config`.
   - Restarts SSH only when either SSH hardening setting changes.
   - Use Ansible `package`, `service`, `template`, `command`/`shell`, `replace` or `lineinfile`, and handlers.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx.
   - Renders `/etc/nginx/nginx.conf` from `nginx.conf.erb`; settings include `www-data`, automatic worker processes, PID `/run/nginx.pid`, `worker_connections 768`, keepalive timeout `65`, gzip, and standard `conf.d` and `sites-enabled` includes.
   - Renders `/etc/nginx/conf.d/security.conf` from `security.conf.erb`; configures `server_tokens off`, login rate `10r/m`, API rate `30r/m`, restrictive client buffers and body size, short timeouts, TLS 1.2 and 1.3, SSL session cache and timeout, explicit ECDHE/DHE ciphers, and server cipher preference.
   - Enables and starts nginx.
   - Creates `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status`, owned by `www-data:www-data` with mode `0755`.
   - Deploys `/opt/server/test/index.html` from `test/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Deploys `/opt/server/ci/index.html` from `ci/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Deploys `/opt/server/status/index.html` from `status/index.html`, owned by `www-data:www-data` with mode `0644`.
   - Global templates notify a delayed nginx reload.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` as `root:root`, mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert`, mode `0710`.
   - Generates self-signed RSA 2048-bit certificates valid for `365` days with subject email `admin@example.com`.
   - Generates the certificate and key for **test.cluster.local**:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Key ownership and mode: `root:ssl-cert`, `0640`
   - Generates the certificate and key for **ci.cluster.local**:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Key ownership and mode: `root:ssl-cert`, `0640`
   - Generates the certificate and key for **status.cluster.local**:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Key ownership and mode: `root:ssl-cert`, `0640`
   - Certificate generation is skipped when both files for the named site already exist and notifies a delayed nginx reload.
   - Prefer `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate` in Ansible.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `site.conf.erb` and creates the corresponding enabled link for **test.cluster.local**:
     - Configuration: `/etc/nginx/sites-available/test.cluster.local`
     - Link: `/etc/nginx/sites-enabled/test.cluster.local`
     - Root: `/opt/server/test`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
   - Renders `site.conf.erb` and creates the corresponding enabled link for **ci.cluster.local**:
     - Configuration: `/etc/nginx/sites-available/ci.cluster.local`
     - Link: `/etc/nginx/sites-enabled/ci.cluster.local`
     - Root: `/opt/server/ci`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
   - Renders `site.conf.erb` and creates the corresponding enabled link for **status.cluster.local**:
     - Configuration: `/etc/nginx/sites-available/status.cluster.local`
     - Link: `/etc/nginx/sites-enabled/status.cluster.local`
     - Root: `/opt/server/status`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
   - Each site listens on HTTP `80`, redirects to HTTPS with `return 301 https://$server_name$request_uri;`, and listens on HTTPS `443` with SSL and HTTP/2.
   - Each site uses TLS 1.2 and 1.3, HSTS, security headers, gzip, `try_files $uri $uri/ =404`, protected `.htaccess`, `.git`, and `.svn` paths, and site-specific access and error logs.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Site templates, links, and default-site deletion notify a delayed nginx reload.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started; delayed restart after `/etc/fail2ban/jail.local` changes
- `nginx`: enabled and started; delayed reload after global configuration, certificates, site configuration, links, or default-site deletion changes
- `ssh`: already managed by the host; delayed restart after SSH hardening changes

**Network ports allowed by UFW**: `22/tcp`, `80/tcp`, `443/tcp`

## Credentials

**Detection Summary**: No credentials or secret stores detected across the analyzed cookbook files.

**Source**:
- **Provider**: None detected
- **URL**: None
- **Path**: None

### Self-Signed Certificate Subject Email

- **Variable(s)**: None; literal `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate subject metadata
- **Usage context**: Subject email for each development self-signed certificate
- **Sensitivity**: Not a password, token, API key, or authentication credential

### TLS Certificates and Private Keys

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/certs/status.cluster.local.crt`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL; not retrieved from a vault or data bag
- **Usage context**: TLS termination for the three nginx virtual hosts
- **Migration note**: These are self-signed development certificates. Production deployments should use certificates issued by an organizational CA or ACME infrastructure.

No data bags, Chef Vault items, Conjur variables, CyberArk data, Vault attributes, environment-variable secrets, database credentials, API tokens, or hardcoded passwords were detected.

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
- Unix socket or IPC endpoint: none

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

### Package and service status

```bash
dpkg-query -W nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled --quiet nginx && systemctl is-active --quiet nginx
systemctl is-enabled --quiet fail2ban && systemctl is-active --quiet fail2ban
systemctl is-active --quiet ssh
```

### Configuration validation

```bash
nginx -t
nginx -T | grep -E \
'server_name (test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local)|listen (80|443)'

sshd -t
sysctl -p /etc/sysctl.d/99-security.conf
ufw status verbose
```

### Site: test.cluster.local

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

curl -k -I --resolve test.cluster.local:80:127.0.0.1 http://test.cluster.local/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
```

Expected: HTTP returns `301`; HTTPS returns a successful response; the certificate contains `CN=test.cluster.local`; the key is `root:ssl-cert` with mode `640`.

### Site: ci.cluster.local

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

curl -k -I --resolve ci.cluster.local:80:127.0.0.1 http://ci.cluster.local/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
```

Expected: HTTP returns `301`; HTTPS returns a successful response; the certificate contains `CN=ci.cluster.local`; the key is `root:ssl-cert` with mode `640`.

### Site: status.cluster.local

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

curl -k -I --resolve status.cluster.local:80:127.0.0.1 http://status.cluster.local/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected: HTTP returns `301`; HTTPS returns a successful response; the certificate contains `CN=status.cluster.local`; the key is `root:ssl-cert` with mode `640`.

### Ports and processes

```bash
ss -tlnp | grep -E ':(22|80|443)\b'
pgrep -a nginx
```

Expected listeners are SSH on `22`, nginx HTTP on `80`, and nginx HTTPS on `443`.

### UFW

```bash
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'
```

Expected: UFW is active, incoming traffic defaults to deny, and ports `22/tcp`, `80/tcp`, and `443/tcp` are allowed.

### fail2ban

```bash
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

grep -E 'bantime|findtime|maxretry|enabled|logpath|port' \
  /etc/fail2ban/jail.local
```

Expected: `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` are enabled with the configured SSH and nginx log paths.

### SSH hardening

```bash
grep -E '^[#]*PermitRootLogin|^[#]*PasswordAuthentication' \
  /etc/ssh/sshd_config

sshd -T | grep -E 'permitrootlogin|passwordauthentication'
```

Expected:

```text
permitrootlogin no
passwordauthentication no
```

### Kernel security

```bash
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
```