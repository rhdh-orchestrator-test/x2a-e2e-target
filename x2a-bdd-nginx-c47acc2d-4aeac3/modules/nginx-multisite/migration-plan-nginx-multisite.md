---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, sysctl, and SSH hardening; creates document roots and self-signed certificates; deploys global and per-site Nginx configuration; redirects HTTP to HTTPS; and reloads affected services when configuration or certificates change.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: `ssl_enabled: true`; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; static file `/opt/server/test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: `ssl_enabled: true`; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; static file `/opt/server/ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: `ssl_enabled: true`; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; static file `/opt/server/status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

Additional configured services:

- **fail2ban**: Enabled, started, and configured for SSH and Nginx protections
- **ufw**: Enabled with default-deny policy and SSH, HTTP, and HTTPS allowed
- **ssh**: Root login and password authentication disabled

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
├── providers/
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
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

No custom-resource provider is used by the executed recipe tree.

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

No static `files/default/*` or `files/*` files are listed. The `nginx.rb` recipe references `test/index.html`, `ci/index.html`, and `status/index.html`, but those source files are absent from the supplied directory listing. The Ansible migration must provide equivalent files or explicitly handle their absence.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Ansible must preserve this execution order through task-file imports or role task includes.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban with `bantime=3600`, `findtime=600`, `maxretry=3`, backend `auto`, SSH protection on `ssh`, and Nginx protections on `http,https` for `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch`.
   - Configures UFW with default incoming policy `deny`, permits SSH TCP `22`, HTTP TCP `80`, and HTTPS TCP `443`, then enables the firewall.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies redirect, reverse-path, source-route, martian-packet, ICMP, IPv6, SYN-cookie, backlog, and TCP retry hardening.
   - Configures:
     - `net.ipv4.conf.default.rp_filter = 1`
     - `net.ipv4.conf.all.rp_filter = 1`
     - `net.ipv4.conf.all.accept_redirects = 0`
     - `net.ipv6.conf.all.accept_redirects = 0`
     - `net.ipv4.conf.default.accept_redirects = 0`
     - `net.ipv6.conf.default.accept_redirects = 0`
     - `net.ipv4.conf.all.send_redirects = 0`
     - `net.ipv4.conf.default.send_redirects = 0`
     - `net.ipv4.conf.all.accept_source_route = 0`
     - `net.ipv6.conf.all.accept_source_route = 0`
     - `net.ipv4.conf.default.accept_source_route = 0`
     - `net.ipv6.conf.default.accept_source_route = 0`
     - `net.ipv4.conf.all.log_martians = 1`
     - `net.ipv4.conf.default.log_martians = 1`
     - `net.ipv4.icmp_echo_ignore_all = 1`
     - `net.ipv4.icmp_echo_ignore_broadcasts = 1`
     - `net.ipv6.conf.all.disable_ipv6 = 1`
     - `net.ipv6.conf.default.disable_ipv6 = 1`
     - `net.ipv6.conf.lo.disable_ipv6 = 1`
     - `net.ipv4.tcp_syncookies = 1`
     - `net.ipv4.tcp_max_syn_backlog = 2048`
     - `net.ipv4.tcp_synack_retries = 2`
     - `net.ipv4.tcp_syn_retries = 5`
   - Reloads sysctl settings with `sysctl -p /etc/sysctl.d/99-security.conf` after changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts SSH only when either SSH setting changes.
   - Iterations: no `.each` loop; package resources cover `fail2ban` and `ufw`, and both SSH hardening settings are applied conditionally.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `www-data`, automatic worker processes, PID `/run/nginx.pid`, `worker_connections 768`, global access and error logs, `sendfile`, TCP optimizations, keepalive timeout `65`, gzip, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, login rate limit `10r/m`, API rate limit `30r/m`, 1K client buffers, maximum request body `1k`, client timeouts `10`, TLS `TLSv1.2 TLSv1.3`, SSL cache `shared:SSL:10m`, and SSL timeout `10m`.
   - Enables and starts the `nginx` service.
   - Iterates over the following explicit sites:
     - `test.cluster.local`: creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`, then deploys `/opt/server/test/index.html` from `test/index.html` with mode `0644` and owner `www-data:www-data`.
     - `ci.cluster.local`: creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`, then deploys `/opt/server/ci/index.html` from `ci/index.html` with mode `0644` and owner `www-data:www-data`.
     - `status.cluster.local`: creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`, then deploys `/opt/server/status/index.html` from `status/index.html` with mode `0644` and owner `www-data:www-data`.
   - Reloads Nginx after global configuration changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Evaluates the following explicit SSL-enabled sites:
     - `test.cluster.local`: generates `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key` with CN `test.cluster.local`.
     - `ci.cluster.local`: generates `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key` with CN `ci.cluster.local`.
     - `status.cluster.local`: generates `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key` with CN `status.cluster.local`.
   - Generates certificates only when the certificate and key are not already present.
   - Uses a 365-day, 2048-bit RSA self-signed certificate with subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Sets private keys to mode `0640`, owner `root`, and group `ssl-cert`.
   - Reloads Nginx after certificate generation.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Uses `server_name=test.cluster.local`, `document_root=/opt/server/test`, `ssl_enabled=true`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Uses `server_name=ci.cluster.local`, `document_root=/opt/server/ci`, `ssl_enabled=true`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Uses `server_name=status.cluster.local`, `document_root=/opt/server/status`, `ssl_enabled=true`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Configures HTTP port `80` to redirect to HTTPS, HTTPS port `443`, HTTP/2, TLS 1.2 and 1.3, HSTS, static document roots, index files, security headers, gzip, `try_files $uri $uri/ =404`, protected `.htaccess`, `.git`, and `.svn` paths, and per-site access and error logs.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Reloads Nginx when a site configuration, symlink, or default-site deletion changes.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata.

**Chef runtime requirement**: Chef `>= 16.0`

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Ansible collection dependencies**:

- `community.general` for UFW management
- `community.crypto` for private-key and certificate management, when available

**Service dependencies**:

- `fail2ban`
- `nginx`
- `ssh`

The target system must provide the Nginx service account and group. Ubuntu normally provides `www-data`; CentOS-based systems may require platform-specific ownership adjustments.

## Credentials

**Detection Summary**: No application credentials, data bags, vault references, API tokens, database passwords, or environment-variable secrets were detected. Six locally generated TLS artifacts were identified: three private keys and three self-signed certificates.

**Source**:

- **Provider**: None detected
- **URL**: Not applicable
- **Path**: Not applicable

### Self-signed TLS private keys

- **Variable(s)**:
  - `key_file`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by `openssl req`
- **Usage context**: Nginx HTTPS private keys
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`

### Self-signed TLS certificates

- **Variable(s)**:
  - `cert_file`
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by `openssl req`
- **Usage context**: Nginx HTTPS server certificates
- **Certificate validity**: `365` days
- **Certificate subject email**: `admin@example.com`

No Chef Vault, encrypted data bag, standard data bag, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, hardcoded password, database connection string, or secret environment variable was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` — must be absent
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
- `/opt/server/status/index.html`
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

- `test.cluster.local:80`
- `test.cluster.local:443`
- `ci.cluster.local:80`
- `ci.cluster.local:443`
- `status.cluster.local:80`
- `status.cluster.local:443`
- SSH TCP port `22`
- Nginx PID file `/run/nginx.pid`
- Unix sockets: None configured

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: once
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: once
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: once
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: once
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: once
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: once
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: once

**Total template render operations**: `7`

## Pre-flight checks

```bash
# Package status
dpkg-query -W nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh

# Nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Test site
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
ls -l /etc/ssl/certs/test.cluster.local.crt
ls -l /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates

# CI site
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
ls -l /etc/ssl/certs/ci.cluster.local.crt
ls -l /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates

# Status site
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
ls -l /etc/ssl/certs/status.cluster.local.crt
ls -l /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Expected certificate subjects:
# CN = test.cluster.local
# CN = ci.cluster.local
# CN = status.cluster.local

# Security headers and TLS
for site in test.cluster.local ci.cluster.local status.cluster.local; do
  curl -k -I --resolve "${site}:443:127.0.0.1" "https://${site}/" | \
    grep -E 'HTTP/|Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Content-Security-Policy'
done

openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local -tls1_2 </dev/null 2>/dev/null | \
  grep -E 'Protocol|Cipher'

openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local -tls1_3 </dev/null 2>/dev/null | \
  grep -E 'Protocol|Cipher'

# Listening ports
ss -tlnp | grep -E ':(80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# UFW
ufw status verbose
ufw status numbered
# Expected: active, default deny, and TCP ports 22, 80, and 443 allowed

# Fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime|findtime|maxretry|enabled|port|logpath' \
  /etc/fail2ban/jail.local

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin|^[[:space:]]*PasswordAuthentication' \
  /etc/ssh/sshd_config
sshd -t
# Expected:
# PermitRootLogin no
# PasswordAuthentication no

# Sysctl
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
cat /etc/sysctl.d/99-security.conf

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

Expected results include HTTP `301` redirects to HTTPS for all three hostnames, valid HTTPS responses, Nginx listeners on ports `80` and `443`, TLS 1.2 and 1.3 support, the expected security headers, valid certificate common names, active UFW and Fail2ban services, hardened SSH settings, and distinct access and error logs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.