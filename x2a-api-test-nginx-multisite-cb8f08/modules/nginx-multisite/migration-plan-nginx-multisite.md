---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: `nginx-multisite` installs and hardens nginx, Fail2ban, UFW, OpenSSL, and CA certificates. It configures three HTTPS-enabled virtual sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`—with separate document roots, self-signed TLS certificates, HTTP-to-HTTPS redirects, security headers, access/error logs, and site symlinks. It also applies SSH, firewall, kernel, and Fail2ban security settings.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS nginx virtual host
  - Location/Path: `/opt/server/test`
  - HTTP/HTTPS Ports: `80` / `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS nginx virtual host
  - Location/Path: `/opt/server/ci`
  - HTTP/HTTPS Ports: `80` / `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS nginx virtual host
  - Location/Path: `/opt/server/status`
  - HTTP/HTTPS Ports: `80` / `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`

**Security instances**:

- **fail2ban**: Enabled and started
- **ufw**: Enabled with default deny, SSH/HTTP/HTTPS allowed
- **ssh**: Root login disabled and password authentication disabled

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

No static `cookbook_file` source files are listed. The recipes deploy three `index.html` files using dynamic `cookbook_file` source paths.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Uses four `include_recipe` resources.
   - The Ansible role must preserve this order. Security configuration precedes nginx and site configuration; SSL generation precedes virtual-host deployment.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw` with one package resource.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban with:
     - Ban time `3600`
     - Find time `600`
     - Maximum retries `3`
     - Backend `auto`
     - Enabled `sshd` jail on `ssh`
     - Enabled `nginx-http-auth` jail on `http,https`
     - Enabled `nginx-limit-req` jail on `http,https`
     - Enabled `nginx-botsearch` jail on `http,https`
     - SSH log `/var/log/auth.log`
     - nginx error logs `/var/log/nginx/*error.log`
     - nginx access logs `/var/log/nginx/*access.log`
     - `nginx-limit-req` maximum retries `10`
     - `nginx-botsearch` maximum retries `2`
   - Executes UFW commands in this order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, disabled IPv4/IPv6 ICMP redirects, disabled source routing, martian logging, ignored ICMP echo requests and broadcast pings, disabled IPv6, TCP SYN cookies, and TCP SYN backlog/retry settings.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as an execute resource with action `nothing`; no notification is shown in the execution tree.
   - Executes SSH hardening:
     - `sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config`
     - `sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config`
   - Declares the `ssh` service with action `nothing`; no SSH restart or reload is shown.
   - Resources: `package` 1, `service` 2, `template` 2, `execute` 8.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `www-data`, worker processes `auto`, PID `/run/nginx.pid`, worker connections `768`, global access/error logs, keepalive timeout `65`, gzip, and includes for modules, `conf.d`, and `sites-enabled`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, login rate limit `10r/m`, API rate limit `30r/m`, client body buffer `1K`, client header buffer `1k`, maximum body size `1k`, large header buffers `2 1k`, client body/header timeouts `10`, send timeout `10`, TLS `1.2` and `1.3`, and shared SSL session cache `10m`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` with mode `0755`.
   - Deploys `/opt/server/test/index.html` using source expression `#{site_folder}/index.html`.
   - Creates `/opt/server/ci` with mode `0755`.
   - Deploys `/opt/server/ci/index.html` using source expression `#{site_folder}/index.html`.
   - Creates `/opt/server/status` with mode `0755`.
   - Deploys `/opt/server/status/index.html` using source expression `#{site_folder}/index.html`.
   - The source static files are absent from the supplied directory listing and must be supplied separately.
   - Resources: `package` 1, `template` 2, `service` 1, `directory` 3, `cookbook_file` 3.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Preserves intended `root` and `ssl-cert` ownership and group handling for SSL directories.
   - Generates the certificate and key for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Common Name: `test.cluster.local`
   - Generates the certificate and key for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Common Name: `ci.cluster.local`
   - Generates the certificate and key for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Common Name: `status.cluster.local`
   - Each certificate command uses:
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout <key_file> \
       -out <cert_file> \
       -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com"
     chmod 640 <key_file>
     chown root:ssl-cert <key_file>
     ```
   - The Ansible implementation should use idempotent certificate generation and avoid unnecessary regeneration.
   - Resources: `package` 1, `group` 1, `directory` 2, `execute` 3.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
   - Template variables for `test.cluster.local` are:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - Template variables for `ci.cluster.local` are:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - Template variables for `status.cluster.local` are:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Each site listens on HTTP port `80`, redirects HTTP to HTTPS, listens on HTTPS port `443` with HTTP/2, and uses its site-specific document root.
   - Each site supports `index.html`, `index.htm`, and `index.php`, TLS 1.2/1.3, configured ciphers, one-year HSTS with subdomain inclusion, security headers, gzip, `try_files`, `.htaccess` denial, `.git`/`.svn` denial, and site-specific access/error logs.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - No nginx reload or restart is shown. Ansible should validate with `nginx -t` before any handler-driven reload.
   - Resources: `template` 3, `link` 3, `file` 1.

## Dependencies

**External cookbook dependencies**: None shown.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**:
- `fail2ban`: Enabled and started.
- `nginx`: Enabled and started.
- `ssh`: Declared with action `nothing`; no restart is shown.

**Network access configured**: SSH, HTTP port `80`, HTTPS port `443`.

## Credentials

**Detection Summary**: No externally supplied credentials, passwords, API tokens, data bags, vault lookups, or secret-manager integrations were detected. Three generated TLS private keys are sensitive artifacts.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: No data bag, vault, CyberArk, Conjur, or secret-manager path detected

### Generated TLS Private Keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`; `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by `openssl req`; owned by `root:ssl-cert` with mode `0640`.
- **Usage context**: TLS private keys used by nginx for HTTPS on port `443`.

### Generated TLS Certificates

- **Variable(s)**: `cert_file`; `/etc/ssl/certs/test.cluster.local.crt`; `/etc/ssl/certs/ci.cluster.local.crt`; `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`; `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated self-signed X.509 certificates valid for `365` days.
- **Usage context**: Server certificates used by nginx for HTTPS on port `443`.

The certificate subject contains the non-secret contact value `admin@example.com`. No password is used because the command includes `-nodes`.

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
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
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

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH service `ssh`; numeric SSH port is not specified

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: 1 render to `/etc/nginx/nginx.conf`
- `security.conf.erb`: 1 render to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: 1 render to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: 3 renders:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

**Additional paths to verify**:

- Document roots: `/opt/server/test`, `/opt/server/ci`, `/opt/server/status`
- Global logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- Site logs:
  - `/var/log/nginx/test.cluster.local_access.log`
  - `/var/log/nginx/test.cluster.local_error.log`
  - `/var/log/nginx/ci.cluster.local_access.log`
  - `/var/log/nginx/ci.cluster.local_error.log`
  - `/var/log/nginx/status.cluster.local_access.log`
  - `/var/log/nginx/status.cluster.local_error.log`
- SSH authentication log: `/var/log/auth.log`

## Pre-flight checks

```bash
# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Configuration validation
nginx -t
grep -E 'user |worker_processes|worker_connections|keepalive_timeout|access_log|error_log' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|client_body_timeout|ssl_protocols' \
  /etc/nginx/conf.d/security.conf

# Site files and symlinks
test -f /etc/nginx/sites-available/test.cluster.local
test -f /etc/nginx/sites-available/ci.cluster.local
test -f /etc/nginx/sites-available/status.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
grep -E 'server_name test.cluster.local|root /opt/server/test|listen 80|listen 443' \
  /etc/nginx/sites-available/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -checkend 0
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
grep -E 'server_name ci.cluster.local|root /opt/server/ci|listen 80|listen 443' \
  /etc/nginx/sites-available/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -checkend 0
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
grep -E 'server_name status.cluster.local|root /opt/server/status|listen 80|listen 443' \
  /etc/nginx/sites-available/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -checkend 0
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Expected HTTP behavior
# Each HTTP request returns 301 with a Location header targeting HTTPS.

# Listening ports
ss -tlnp | grep -E ':(80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# UFW policy
ufw status verbose
ufw status numbered
# Expected: default deny, SSH allowed, HTTP allowed, HTTPS allowed

# Fail2ban jails
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Kernel security settings
grep -E 'rp_filter|accept_redirects|send_redirects|accept_source_route|log_martians|disable_ipv6|tcp_syncookies' \
  /etc/sysctl.d/99-security.conf

# SSH hardening
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config
# Expected:
# PermitRootLogin no
# PasswordAuthentication no

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

The Ansible implementation must preserve recipe ordering, define all three site keys exactly, deploy the five templates to their specified destinations, generate all three certificate/key pairs, and run `nginx -t` before any service reload.