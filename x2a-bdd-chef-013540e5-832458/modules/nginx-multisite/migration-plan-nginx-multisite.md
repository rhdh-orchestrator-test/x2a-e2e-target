---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; generates self-signed TLS certificates; applies kernel and SSH hardening; deploys site content and Nginx virtual-host configurations; enables HTTP-to-HTTPS redirects; and configures security controls. All sites use ports 80 and 443 with document roots under `/opt/server`.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; content `/opt/server/test/index.html`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; content `/opt/server/ci/index.html`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; content `/opt/server/status/index.html`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

- **fail2ban**: Host intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: None
  - Key Config: Enabled and started; ban time `3600`; find time `600`; maximum retries `3`; protects SSH and Nginx HTTP/HTTPS logs

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Enabled with default incoming policy `deny`

- **ssh**: SSH hardening configuration
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: SSH TCP `22`
  - Key Config: Root login disabled; password authentication disabled

## File Structure

The following files are used by the cookbook execution flow.

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

No static files are listed in the supplied cookbook directory. The recipes reference dynamic `cookbook_file` sources named `test/index.html`, `ci/index.html`, and `status/index.html`; these source paths must be supplied in the Ansible role if the corresponding site content is required.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible implementation must preserve this execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban with ban time `3600`, find time `600`, maximum retries `3`, SSH protection, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Uses `/var/log/auth.log`, `/var/log/nginx/*error.log`, and `/var/log/nginx/*access.log`.
   - Sets the UFW default policy to deny.
   - Allows SSH on `22/tcp`, HTTP on `80/tcp`, and HTTPS on `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies reverse-path filtering, redirect suppression, source-route suppression, martian packet logging, ICMP protections, IPv6 disabling, and TCP SYN flood protection.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` when the sysctl template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` when required.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` when required.
   - Delays an `sshd` restart when either SSH hardening setting changes.
   - Resource counts: package `1`, service `2`, template `2`, execute `7`.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, worker processes `auto`, PID file `/run/nginx.pid`, worker connections `768`, standard access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures version hiding, `login` limiting at `10r/m`, `api` limiting at `30r/m`, `client_max_body_size 1k`, client and send timeouts of `10`, TLS 1.2 and 1.3, the configured cipher list, and preferred server ciphers.
   - Enables and starts the `nginx` service with reload, restart, and status support.
   - Creates `/opt/server/test` owned by `nginx:nginx` with mode `0755`.
   - Deploys source `test/index.html` to `/opt/server/test/index.html`, owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/ci` owned by `nginx:nginx` with mode `0755`.
   - Deploys source `ci/index.html` to `/opt/server/ci/index.html`, owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/status` owned by `nginx:nginx` with mode `0755`.
   - Deploys source `status/index.html` to `/opt/server/status/index.html`, owned by `nginx:nginx` with mode `0644`.
   - Resource counts: package `1`, template `2`, service `1`, directory `3`, cookbook file `3`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed RSA `2048` certificate for `test.cluster.local`, valid for `365` days, at `/etc/ssl/certs/test.cluster.local.crt`, with key `/etc/ssl/private/test.cluster.local.key`.
   - Generates a self-signed RSA `2048` certificate for `ci.cluster.local`, valid for `365` days, at `/etc/ssl/certs/ci.cluster.local.crt`, with key `/etc/ssl/private/ci.cluster.local.key`.
   - Generates a self-signed RSA `2048` certificate for `status.cluster.local`, valid for `365` days, at `/etc/ssl/certs/status.cluster.local.crt`, with key `/etc/ssl/private/status.cluster.local.key`.
   - Uses subject format `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=[hostname]/emailAddress=admin@example.com`.
   - Generates keys without passphrases, sets key mode `640`, and owns keys as `root:ssl-cert`.
   - Skips certificate generation when both the certificate and key already exist.
   - Delays Nginx reloads when certificates change.
   - Resource counts: package `1`, group `1`, directory `2`, execute `3`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` owned by `root:root` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` owned by `root:root` with mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with variables `server_name: test.cluster.local`, `document_root: /opt/server/test`, `ssl_enabled: true`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with variables `server_name: ci.cluster.local`, `document_root: /opt/server/ci`, `ssl_enabled: true`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with variables `server_name: status.cluster.local`, `document_root: /opt/server/status`, `ssl_enabled: true`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Delays Nginx reloads after template, link, or deletion changes.
   - Each rendered virtual host listens on HTTP `80`, redirects to HTTPS, listens on HTTPS `443` with HTTP/2, serves its site document root, enables HSTS for one year, adds security headers and gzip, uses `try_files $uri $uri/ =404`, denies `.htaccess`, `.git`, and `.svn`, and writes site-specific access and error logs.
   - Site-specific logs are `/var/log/nginx/test.cluster.local_access.log`, `/var/log/nginx/test.cluster.local_error.log`, `/var/log/nginx/ci.cluster.local_access.log`, `/var/log/nginx/ci.cluster.local_error.log`, `/var/log/nginx/status.cluster.local_access.log`, and `/var/log/nginx/status.cluster.local_error.log`.
   - Resource counts: directory `2`, template `3`, link `3`, file deletion `1`.

## Dependencies

**External cookbook dependencies**: None listed.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**: `fail2ban`, `nginx`, and `sshd` or the platform-equivalent SSH service. `sshd` is restarted only when SSH configuration changes.

**Required groups**: `nginx` for site content ownership; `ssl-cert` for private-key ownership.

**Operating system support declared by metadata**: Ubuntu `>= 18.04`; CentOS `>= 7.0`. UFW and `/var/log/auth.log` are particularly aligned with Debian/Ubuntu systems, so equivalent CentOS firewall, log, and SSH behavior must be validated.

## Credentials

**Detection Summary**: No externally supplied credentials detected. Three locally generated TLS private keys and three locally generated self-signed certificates are present.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### TLS private keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`; `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by OpenSSL; not stored in a data bag, vault, environment variable, or hardcoded secret attribute.
- **Usage context**: TLS private keys used by Nginx for HTTPS on port `443`.
- **Permissions**: Mode `640`, owned by `root:ssl-cert`.

### Self-signed TLS certificates

- **Variable(s)**: `cert_file`; `/etc/ssl/certs/test.cluster.local.crt`; `/etc/ssl/certs/ci.cluster.local.crt`; `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`; `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by OpenSSL.
- **Usage context**: TLS certificates used by Nginx for HTTPS.
- **Certificate subject email**: `admin@example.com`
- **Validity**: `365` days
- **Key type**: RSA `2048`

No data-bag credential, Chef Vault secret, external secret-manager URL, database credential, API token, password attribute, or secret environment variable was detected.

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
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/opt/server/test/index.html
/opt/server/ci/index.html
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/test.cluster.local_access.log
/var/log/nginx/test.cluster.local_error.log
/var/log/nginx/ci.cluster.local_access.log
/var/log/nginx/ci.cluster.local_error.log
/var/log/nginx/status.cluster.local_access.log
/var/log/nginx/status.cluster.local_error.log
```

**Service endpoints to check**: `test.cluster.local` HTTP `80` and HTTPS `443`; `ci.cluster.local` HTTP `80` and HTTPS `443`; `status.cluster.local` HTTP `80` and HTTPS `443`; SSH TCP `22`; Nginx PID file `/run/nginx.pid`; no Unix socket configured.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: `1` render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: `1` render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: `1` render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: `1` render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: `1` render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: `1` render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: `1` render

**Total template render operations**: `7`.

## Pre-flight checks:

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Nginx configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# test.cluster.local
curl -I --resolve test.cluster.local:80:127.0.0.1 http://test.cluster.local/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
test -L /etc/nginx/sites-enabled/test.cluster.local

# ci.cluster.local
curl -I --resolve ci.cluster.local:80:127.0.0.1 http://ci.cluster.local/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
test -L /etc/nginx/sites-enabled/ci.cluster.local

# status.cluster.local
curl -I --resolve status.cluster.local:80:127.0.0.1 http://status.cluster.local/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
test -L /etc/nginx/sites-enabled/status.cluster.local

# TLS certificates, key permissions, and subjects
stat -c '%A %U:%G %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Expected private-key ownership and permissions:
# root:ssl-cert
# 640

# Ports and listeners
ss -tlnp | grep -E ':(80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Firewall validation
ufw status verbose
ufw status numbered

# Expected:
# Default incoming policy: deny
# TCP 22, 80, and 443 allowed
# UFW status: active

# SSH hardening validation
grep -E '^[[:space:]]*PermitRootLogin|^[[:space:]]*PasswordAuthentication' \
  /etc/ssh/sshd_config
systemctl status sshd 2>/dev/null || systemctl status ssh

# Expected:
# PermitRootLogin no
# PasswordAuthentication no

# Kernel security validation
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6
cat /etc/sysctl.d/99-security.conf

# Expected important values:
# rp_filter = 1
# accept_redirects = 0
# send_redirects = 0
# accept_source_route = 0
# icmp_echo_ignore_all = 1
# tcp_syncookies = 1
# tcp_max_syn_backlog = 2048
# IPv6 disabled on configured interfaces

# Fail2ban validation
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Expected jails:
# sshd
# nginx-http-auth
# nginx-limit-req
# nginx-botsearch
```