---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx on Ubuntu or CentOS with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and configures nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies SSH and kernel hardening; generates self-signed TLS certificates; deploys static content; renders and enables three nginx virtual hosts; and removes the default site. The Ansible migration must preserve recipe ordering, idempotent guards, delayed service notifications, filesystem ownership, certificate permissions, firewall policy, and all three site definitions.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled static nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source content `test/index.html`

- **ci.cluster.local**: HTTPS-enabled static nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source content `ci/index.html`

- **status.cluster.local**: HTTPS-enabled static nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source content `status/index.html`

Security configuration is enabled with fail2ban and UFW. SSH hardening disables root login and password authentication. Kernel network hardening is applied through `/etc/sysctl.d/99-security.conf`.

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
```text
```

No static files under `files/default/*` or `files/*` are listed in the supplied cookbook structure. The recipes expect `test/index.html`, `ci/index.html`, and `status/index.html` as `cookbook_file` sources, but those files are not included in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - Ansible task imports or includes must preserve this order.

2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Delays a `fail2ban` restart when `/etc/fail2ban/jail.local` changes.
   - Configures fail2ban with `bantime=3600`, `findtime=600`, `maxretry=3`, and backend `auto`.
   - Enables the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Uses `/var/log/auth.log` for SSH and `/var/log/nginx/*error.log` and `/var/log/nginx/*access.log` for nginx.
   - Applies UFW rules in order:
     - `ufw --force default deny`
     - `ufw allow ssh`
     - `ufw allow http`
     - `ufw allow https`
     - `ufw --force enable`
   - Preserves the existing idempotent command guards for default policy, ports `22/tcp`, `80/tcp`, `443/tcp`, and active UFW status.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Delays `sysctl -p /etc/sysctl.d/99-security.conf` when the sysctl template changes.
   - Applies reverse-path filtering, redirect rejection, source-route rejection, martian logging, ICMP suppression, IPv6 disabling, and TCP SYN flood protection.
   - Disables root SSH login with `PermitRootLogin no` when not already configured.
   - Disables SSH password authentication with `PasswordAuthentication no` when not already configured.
   - Delays an `sshd` restart when either SSH hardening command changes.
   - Declares the `sshd` service with action `nothing`.

3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Delays an nginx reload when `/etc/nginx/nginx.conf` changes.
   - Configures nginx user `nginx`, automatic worker processes, PID file `/run/nginx.pid`, `768` worker connections, access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Delays an nginx reload when the security configuration changes.
   - Configures server-token hiding, `login` and `api` rate-limit zones, a `1k` client body limit, ten-second client body/header/send timeouts, TLS 1.2 and TLS 1.3, explicit ECDHE/DHE ciphers, a `10m` shared SSL session cache, and a ten-minute SSL session timeout.
   - Enables and starts the nginx service.
   - Expands the site collection three times:
     - **test.cluster.local**: creates `/opt/server/test` with owner `nginx`, group `nginx`, mode `0755`, and deploys `test/index.html` to `/opt/server/test/index.html` with owner `nginx`, group `nginx`, mode `0644`.
     - **ci.cluster.local**: creates `/opt/server/ci` with owner `nginx`, group `nginx`, mode `0755`, and deploys `ci/index.html` to `/opt/server/ci/index.html` with owner `nginx`, group `nginx`, mode `0644`.
     - **status.cluster.local**: creates `/opt/server/status` with owner `nginx`, group `nginx`, mode `0755`, and deploys `status/index.html` to `/opt/server/status/index.html` with owner `nginx`, group `nginx`, mode `0644`.

4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates certificates for all three SSL-enabled sites:
     - **test.cluster.local**: `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`.
     - **ci.cluster.local**: `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`.
     - **status.cluster.local**: `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`.
   - Uses RSA 2048-bit keys, `365` days of validity, and the subject format `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Sets generated private keys to mode `0640` and ownership `root:ssl-cert`.
   - Skips certificate generation when both the certificate and key already exist.
   - Delays an nginx reload when a certificate-generation command changes.
   - Iterations: **test.cluster.local**, **ci.cluster.local**, and **status.cluster.local**; all three have `ssl_enabled: true`.

5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Preserves the analyzed site-directory loop as three iterations for **test.cluster.local**, **ci.cluster.local**, and **status.cluster.local**, with three resolved directory resources in the execution tree.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - **test.cluster.local**: destination `/etc/nginx/sites-available/test.cluster.local`, document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
     - **ci.cluster.local**: destination `/etc/nginx/sites-available/ci.cluster.local`, document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
     - **status.cluster.local**: destination `/etc/nginx/sites-available/status.cluster.local`, document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Sets virtual-host template mode to `0644`.
   - Creates enabled-site links:
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Delays nginx reloads when templates, links, or default-site removal change.
   - Renders an HTTP port `80` redirect server and an HTTPS port `443` HTTP/2 server for each site.
   - Enables TLS 1.2 and TLS 1.3, HSTS, security headers, gzip, `try_files $uri $uri/ =404`, `.ht*` denial, and `.git` and `.svn` denial.
   - Creates per-site access and error logs:
     - `/var/log/nginx/test.cluster.local_access.log`
     - `/var/log/nginx/test.cluster.local_error.log`
     - `/var/log/nginx/ci.cluster.local_access.log`
     - `/var/log/nginx/ci.cluster.local_error.log`
     - `/var/log/nginx/status.cluster.local_access.log`
     - `/var/log/nginx/status.cluster.local_error.log`

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: restarted only when SSH hardening changes
- UFW: enabled after SSH, HTTP, and HTTPS rules are configured

**Runtime ordering**:

1. Security packages, hardening, and firewall rules
2. nginx installation and base configuration
3. SSL packages, directories, and certificate generation
4. Site directories, virtual-host templates, links, and default-site removal

## Credentials

**Detection Summary**: 0 credentials detected across the supplied cookbook files. The cookbook does generate six sensitive TLS artifacts: three private keys and three self-signed certificates.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Generated TLS Private Keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by the `openssl req` command; not sourced from a vault or data bag
- **Usage context**: HTTPS private keys for the three nginx virtual hosts
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`; parent directory `/etc/ssl/private` has mode `0710`

### Generated TLS Certificates

- **Variable(s)**: `cert_file`; `/etc/ssl/certs/test.cluster.local.crt`; `/etc/ssl/certs/ci.cluster.local.crt`; `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally as self-signed certificates
- **Usage context**: HTTPS certificates for the three nginx virtual hosts
- **Certificate lifetime**: `365` days

The hardcoded subject email `admin@example.com` is a certificate identity field, not a password, token, or other credential.

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
- `/etc/nginx/sites-enabled/default` is absent
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
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

- `test.cluster.local`: ports `80` and `443`
- `ci.cluster.local`: ports `80` and `443`
- `status.cluster.local`: ports `80` and `443`
- SSH: port `22`
- Unix socket: none configured

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`:
  - `/etc/nginx/sites-available/test.cluster.local`: 1 render
  - `/etc/nginx/sites-available/ci.cluster.local`: 1 render
  - `/etc/nginx/sites-available/status.cluster.local`: 1 render
  - Total: 3 renders

## Pre-flight checks:

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl status sshd
ufw status verbose

# Configuration validation
nginx -t
sshd -t
nginx -T | grep -E \
'server_name (test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local)|listen (80|443)'

grep -E 'worker_processes|worker_connections|access_log|error_log|gzip' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|ssl_protocols|ssl_ciphers|client_max_body_size' \
  /etc/nginx/conf.d/security.conf

# Firewall validation
ufw status numbered
# Expected: active; default incoming deny; SSH, HTTP, and HTTPS allowed

# SSH hardening validation
grep -E '^[[:space:]]*(PermitRootLogin|PasswordAuthentication)' \
  /etc/ssh/sshd_config
# Expected:
# PermitRootLogin no
# PasswordAuthentication no

# Kernel hardening validation
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
cat /etc/sysctl.d/99-security.conf

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test ! -e /etc/nginx/sites-enabled/default
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -dates

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -dates

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -dates

# Expected site results
# HTTP returns a 301 redirect to HTTPS.
# HTTPS normally returns 200 OK when index.html exists.
# Certificate subjects contain CN=test.cluster.local, CN=ci.cluster.local,
# and CN=status.cluster.local respectively.

# nginx security headers
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | grep -E \
'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection|Referrer-Policy|Content-Security-Policy'

# TLS and key permissions
stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

stat -c '%U:%G %a %n' /etc/ssl/private /etc/ssl/certs

openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates

# Expected key ownership: root:ssl-cert
# Expected key mode: 640
# Expected TLS protocols: TLS 1.2 and TLS 1.3

# fail2ban validation
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime|findtime|maxretry|enabled|port|logpath' \
  /etc/fail2ban/jail.local
```