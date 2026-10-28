---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a hardened multi-site HTTPS web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, OpenSSL, CA certificates, fail2ban, and UFW; configures kernel, firewall, SSH, nginx, TLS, and fail2ban security settings; generates self-signed RSA 2048 certificates; deploys static site content; enables nginx and fail2ban; and creates three HTTPS virtual hosts with HTTP-to-HTTPS redirects. The Ansible implementation must preserve recipe order, exact paths, ports, ownership, security settings, idempotency guards, and delayed reload behavior.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS static web site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443 ssl http2`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; logs `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS static web site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443 ssl http2`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; logs `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS static web site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443 ssl http2`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; logs `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`

**Security Instances**:

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: SSH `ssh`; nginx jails use `http,https`
  - Key Config: Enabled and started; `bantime=3600`, `findtime=600`, `maxretry=3`, backend `auto`

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows `22/tcp`, `80/tcp`, and `443/tcp`
  - Key Config: Default policy deny; firewall enabled

- **ssh**: SSH daemon
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: `22/tcp`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`

## File Structure

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── files/
│   └── (no static files listed)
├── providers/
│   └── (none)
├── recipes/
│   ├── default.rb
│   ├── security.rb
│   ├── nginx.rb
│   ├── ssl.rb
│   └── sites.rb
└── templates/
    └── default/
        ├── fail2ban.jail.local.erb
        ├── nginx.conf.erb
        ├── security.conf.erb
        ├── site.conf.erb
        └── sysctl-security.conf.erb
```

The `nginx.rb` recipe references dynamic cookbook file sources `test/index.html`, `ci/index.html`, and `status/index.html`. Verify that these source files are supplied separately before implementing Ansible copy tasks.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Establishes the dependency order for packages, directories, certificates, static files, services, and virtual hosts.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban values: ban time `3600`, find time `600`, maximum retries `3`, backend `auto`, SSH protection, nginx HTTP authentication, request-limit, and bot-search jails.
   - Notifies a delayed fail2ban restart when `/etc/fail2ban/jail.local` changes.
   - Runs UFW commands in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Preserves guards that skip already-applied UFW settings.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, ICMP redirect and source-routing protection, martian logging, ICMP echo restrictions, IPv6 disablement, TCP SYN cookies, `tcp_max_syn_backlog=2048`, `tcp_synack_retries=2`, and `tcp_syn_retries=5`.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` only when notified by the sysctl template.
   - Sets `PermitRootLogin no` and `PasswordAuthentication no` in `/etc/ssh/sshd_config` using idempotent line editing.
   - Notifies a delayed `ssh` restart when either SSH setting changes.
   - Resources: one package declaration installing two packages, two services, two templates, five UFW executes, one sysctl reload execute, and two SSH hardening executes.
   - **Execute resources: 8 total**.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `www-data`, worker processes `auto`, PID `/run/nginx.pid`, worker connections `768`, global access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, rate limits `10r/m` and `30r/m`, request-size and timeout limits, TLS 1.2 and 1.3, a shared `10m` SSL session cache, `10m` SSL session timeout, strong ciphers, and preferred server ciphers.
   - Schedules delayed nginx reloads when either nginx template changes.
   - Enables and starts `nginx` with restart, reload, and status support.
   - Iteration `test.cluster.local`: creates `/opt/server/test` owned by `www-data:www-data` mode `0755`, and deploys `test/index.html` to `/opt/server/test/index.html` owned by `www-data:www-data` mode `0644`.
   - Iteration `ci.cluster.local`: creates `/opt/server/ci` owned by `www-data:www-data` mode `0755`, and deploys `ci/index.html` to `/opt/server/ci/index.html` owned by `www-data:www-data` mode `0644`.
   - Iteration `status.cluster.local`: creates `/opt/server/status` owned by `www-data:www-data` mode `0755`, and deploys `status/index.html` to `/opt/server/status/index.html` owned by `www-data:www-data` mode `0644`.
   - Resources: one package, two templates, one service, three directories, and three cookbook files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` mode `0710`.
   - Iteration `test.cluster.local`: generates `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key` using a one-year, RSA 2048-bit self-signed certificate with CN `test.cluster.local` and subject email `admin@example.com`.
   - Iteration `ci.cluster.local`: generates `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key` using a one-year, RSA 2048-bit self-signed certificate with CN `ci.cluster.local` and subject email `admin@example.com`.
   - Iteration `status.cluster.local`: generates `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key` using a one-year, RSA 2048-bit self-signed certificate with CN `status.cluster.local` and subject email `admin@example.com`.
   - Each certificate command is skipped when both its certificate and key already exist.
   - Sets private keys to `root:ssl-cert` mode `0640`.
   - Schedules a delayed nginx reload when a new certificate is generated.
   - Prefer `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate`; otherwise preserve the existing-file guards and OpenSSL parameters.
   - Resources: one package declaration installing two packages, one group, two directories, and three certificate-generation executes.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iteration `test.cluster.local`: renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`, using root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`, and `ssl_enabled=true`; creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to the available-site file.
   - Iteration `ci.cluster.local`: renders the same template to `/etc/nginx/sites-available/ci.cluster.local`, using root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`, and `ssl_enabled=true`; creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to the available-site file.
   - Iteration `status.cluster.local`: renders the same template to `/etc/nginx/sites-available/status.cluster.local`, using root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`, and `ssl_enabled=true`; creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to the available-site file.
   - All three templates and links notify delayed nginx reloads when changed.
   - Deletes `/etc/nginx/sites-enabled/default` and notifies a delayed nginx reload.
   - Resources: three templates, three links, and one file deletion.

All three virtual hosts listen on HTTP `80` and redirect to HTTPS with `return 301 https://$server_name$request_uri;`. Their HTTPS listeners use `443 ssl http2`, site-specific roots and certificates, `index.html`, `index.htm`, and `index.php`, TLS 1.2 and 1.3, HSTS, security headers, gzip, and `try_files $uri $uri/ =404`. Access to `.htaccess`, `.git`, and `.svn` paths is denied.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**: `fail2ban`, `nginx`, and `ssh` for configuration-change restart notifications.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`.

**Network dependencies**: SSH `22/tcp`, HTTP `80/tcp`, and HTTPS `443/tcp`.

## Credentials

**Detection Summary**: No runtime credentials or external secret-store integrations were detected. Certificate subject metadata and generated private keys are present, but there are no passwords, API tokens, database credentials, data bag lookups, Vault lookups, or CyberArk integrations.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed certificate subject email

- **Variable(s)**: Hardcoded `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL subject
- **Usage context**: Subject metadata for all three generated self-signed certificates

### TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL; not retrieved from a secret manager
- **Usage context**: Private keys for the three nginx HTTPS virtual hosts
- **Permissions**: Directory `/etc/ssl/private` is `root:ssl-cert` mode `0710`; key files are `root:ssl-cert` mode `0640`

Protect generated private keys from task output and use `no_log: true` for commands that could expose key-generation details.

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-enabled/default` absent
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
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
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

**Service endpoints to check**: `22/tcp`, `80/tcp`, `443/tcp`; no Unix sockets or custom IPC endpoints.

**Services to verify**: `nginx` enabled and running; `fail2ban` enabled and running; `ssh` running after SSH configuration changes.

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: three times, for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`

## Pre-flight checks:

```bash
# Packages and services
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
  rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
ufw status verbose

# Expected: nginx and fail2ban are enabled and active; UFW is active with
# default deny and ports 22/tcp, 80/tcp, and 443/tcp allowed.

# Global nginx validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
nginx -T | grep -E 'listen 80|listen 443 ssl http2'
ss -tlnp | grep -E ':(80|443)\b'

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
stat -c '%U:%G %a %n' /opt/server/test /opt/server/test/index.html \
  /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
stat -c '%U:%G %a %n' /opt/server/ci /opt/server/ci/index.html \
  /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
stat -c '%U:%G %a %n' /opt/server/status /opt/server/status/index.html \
  /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# TLS and SNI
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates

openssl s_client -connect 127.0.0.1:443 -servername test.cluster.local \
  </dev/null 2>/dev/null | openssl x509 -noout -subject -dates
openssl s_client -connect 127.0.0.1:443 -servername ci.cluster.local \
  </dev/null 2>/dev/null | openssl x509 -noout -subject -dates
openssl s_client -connect 127.0.0.1:443 -servername status.cluster.local \
  </dev/null 2>/dev/null | openssl x509 -noout -subject -dates

# Security settings
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf
grep -E 'net\.(ipv4|ipv6)' /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config

# fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E '^(bantime|findtime|maxretry|backend|enabled|port|logpath)' \
  /etc/fail2ban/jail.local

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
```