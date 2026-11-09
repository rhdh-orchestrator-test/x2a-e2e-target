---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and configures nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies nginx, kernel, SSH, firewall, and fail2ban hardening; generates 365-day RSA certificates; creates site document roots and static index files; configures HTTP-to-HTTPS redirects; and enables nginx services and security controls. No external cookbook dependencies or application credentials are defined. The migration must provide equivalent content for the three referenced static files: `test/index.html`, `ci/index.html`, and `status/index.html`.

## Service Type and Instances

**Service Type**: Web Server

**Platform support declared by metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; static source `test/index.html`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; static source `ci/index.html`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; static source `status/index.html`

**Security configuration**:

- `security.fail2ban.enabled`: `true`
- `security.ufw.enabled`: `true`
- `security.ssh.disable_root`: `true`
- `security.ssh.password_auth`: `false`

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

No provider files or executed custom resources are present.

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

The recipes reference these cookbook files, which are absent from the supplied listing:

```text
test/index.html
ci/index.html
status/index.html
```

The Ansible migration must supply equivalent content or explicitly source the files elsewhere.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role should preserve this execution order through task imports or a main task file.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the unversioned packages `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban defaults: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Enables the `sshd` jail on port `ssh` using `/var/log/auth.log`, with ban time `3600` and maximum retries `3`.
   - Enables the `nginx-http-auth` jail on `http,https` using `/var/log/nginx/*error.log`, with ban time `3600` and maximum retries `3`.
   - Enables the `nginx-limit-req` jail on `http,https` using `/var/log/nginx/*error.log`, with ban time `3600` and maximum retries `10`.
   - Enables the `nginx-botsearch` jail on `http,https` using `/var/log/nginx/*access.log`, with ban time `3600` and maximum retries `2`.
   - Restarts fail2ban after a changed jail configuration.
   - Applies UFW rules in this order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Preserves the original idempotence guards for the UFW commands, or uses equivalent `community.general.ufw` tasks.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-route rejection, martian logging, ICMP and broadcast-ping suppression, IPv6 disabling, and TCP SYN flood protection.
   - Reloads the sysctl configuration with `sysctl -p /etc/sysctl.d/99-security.conf` after changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` only when either SSH setting changes.
   - Resources in execution order: package installation, fail2ban service, fail2ban template, five UFW operations, sysctl template, delayed sysctl reload, two conditional SSH commands, and delayed `sshd` service restart.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the unversioned `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID file `/run/nginx.pid`, `768` worker connections, sendfile, TCP optimizations, keepalive timeout `65`, MIME types, access and error logs, gzip, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, request limiting zones `login` (`10m`, `10r/m`) and `api` (`10m`, `30r/m`), 1K client buffers, 1K maximum client body size, 10-second body/header/send timeouts, TLS session caching, TLS 1.2 and TLS 1.3, the configured ECDHE/DHE cipher list, and preferred server ciphers.
   - Enables and starts the `nginx` service.
   - Reloads nginx after changed nginx or security configuration templates.
   - Creates `/opt/server/test` with owner `nginx:nginx` and mode `0755`.
   - Deploys `/opt/server/test/index.html` from `test/index.html` with owner `nginx:nginx` and mode `0644`.
   - Creates `/opt/server/ci` with owner `nginx:nginx` and mode `0755`.
   - Deploys `/opt/server/ci/index.html` from `ci/index.html` with owner `nginx:nginx` and mode `0644`.
   - Creates `/opt/server/status` with owner `nginx:nginx` and mode `0755`.
   - Deploys `/opt/server/status/index.html` from `status/index.html` with owner `nginx:nginx` and mode `0644`.
   - Iterations: document-root and static-file operations run for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the unversioned packages `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with owner `root:root` and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root:ssl-cert` and mode `0710`.
   - Generates certificates only when the corresponding certificate and key do not already exist.
   - Generates self-signed RSA 2048-bit certificates valid for `365` days with no passphrase.
   - Uses subject values: country `US`, state `Example`, locality `Example`, organization `Example Org`, organizational unit `IT`, and email `admin@example.com`.
   - Generates the following certificate and key:
     - `test.cluster.local`: certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`, subject CN `test.cluster.local`.
     - `ci.cluster.local`: certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`, subject CN `ci.cluster.local`.
     - `status.cluster.local`: certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`, subject CN `status.cluster.local`.
   - Sets every private key to owner `root:ssl-cert` and mode `0640`.
   - Each certificate generation notifies a delayed nginx reload.
   - Iterations: certificate generation runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root:root` and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root:root` and mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`, using document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
     - `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`, using document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
     - `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`, using document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Creates these enabled links:
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Reloads nginx after changed site templates, links, or default-site deletion.
   - Every rendered site provides an HTTP listener on port `80`, a `301` redirect to HTTPS, and an HTTP/2 HTTPS listener on port `443`.
   - Every rendered site uses TLS 1.2 and TLS 1.3, HSTS with `max-age=31536000; includeSubDomains`, the site-specific document root, gzip, `try_files $uri $uri/ =404`, security headers, and denial rules for `.htaccess`, `.git`, and `.svn`.
   - Site-specific logs are:
     - `test.cluster.local`: `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`
     - `ci.cluster.local`: `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`
     - `status.cluster.local`: `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`
   - Resources: 2 directory resources, 3 template renders, 3 links, and 1 default-site deletion.

**Template render counts**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `sysctl-security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders, for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

Package versions are unspecified and remain distribution-selected.

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: restarted when SSH hardening changes
- UFW: enabled and configured with SSH, HTTP, and HTTPS access
- Sysctl security settings: reloaded after configuration changes

## Credentials

**Detection Summary**: No authentication credentials, API tokens, passwords, encrypted data bags, Chef Vault items, CyberArk references, Conjur variables, or database connection credentials were detected. Three locally generated TLS private keys are sensitive cryptographic files but are not retrieved from a credential provider.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files
- **Usage context**: nginx HTTPS private keys
- **Generation**: OpenSSL self-signed RSA 2048-bit certificates valid for 365 days
- **Permissions**: Owner/group `root:ssl-cert`, mode `0640`

### Certificate subject email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command
- **Usage context**: Email field in the self-signed certificate subject
- **Credential status**: Not an authentication credential

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

- `test.cluster.local:80`
- `test.cluster.local:443`
- `ci.cluster.local:80`
- `ci.cluster.local:443`
- `status.cluster.local:80`
- `status.cluster.local:443`
- SSH `22/tcp`
- Unix socket: none configured

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: 3 renders

## Pre-flight checks

```bash
# Service status
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active sshd

# Configuration validation
nginx -t
sshd -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
nginx -T | grep -E 'listen 80|listen 443 ssl http2'

# Site-specific HTTP redirects
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/

# Site-specific HTTPS content and certificates
curl -k -i --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl s_client -connect 127.0.0.1:443 -servername test.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject -dates

curl -k -i --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl s_client -connect 127.0.0.1:443 -servername ci.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject -dates

curl -k -i --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl s_client -connect 127.0.0.1:443 -servername status.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject -dates

# Document roots and static files
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
ls -ld /opt/server/status
ls -l /opt/server/status/index.html

# TLS files and permissions
ls -ld /etc/ssl/certs
ls -ld /etc/ssl/private
ls -l /etc/ssl/certs/test.cluster.local.crt /etc/ssl/private/test.cluster.local.key
ls -l /etc/ssl/certs/ci.cluster.local.crt /etc/ssl/private/ci.cluster.local.key
ls -l /etc/ssl/certs/status.cluster.local.crt /etc/ssl/private/status.cluster.local.key

# Site links and default site removal
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Network listeners
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# UFW
ufw status verbose
ufw status numbered

# Sysctl settings
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# SSH hardening
grep -E '^[# ]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[# ]*PasswordAuthentication' /etc/ssh/sshd_config

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
tail -n 50 /var/log/auth.log
```

Expected results:

- `nginx` and `fail2ban` are enabled and active.
- `sshd -t` and `nginx -t` complete without errors.
- HTTP requests for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` return `301` redirects to their HTTPS URLs.
- HTTPS requests return `200`, serve the corresponding static index file, present a certificate with the matching hostname CN, and include the configured security headers.
- Certificates are approximately 365 days valid and use TLS 1.2 or TLS 1.3.
- Document-root directories are owned by `nginx:nginx` with mode `0755`.
- Index files are owned by `nginx:nginx` with mode `0644`.
- Private keys are owned by `root:ssl-cert` with mode `0640`.
- `/etc/ssl/private` is owned by `root:ssl-cert` with mode `0710`.
- Enabled links target their corresponding files under `/etc/nginx/sites-available`.
- `/etc/nginx/sites-enabled/default` does not exist.
- nginx listens on TCP ports `80` and `443`.
- UFW is active with default incoming policy `deny`, and SSH, HTTP, and HTTPS are allowed.
- Fail2ban has enabled `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
- SSH hardening reports `PermitRootLogin no` and `PasswordAuthentication no`.
- Sysctl values include:
  - `net.ipv4.conf.default.rp_filter = 1`
  - `net.ipv4.conf.all.rp_filter = 1`
  - `net.ipv4.conf.all.accept_redirects = 0`
  - `net.ipv6.conf.all.disable_ipv6 = 1`
  - `net.ipv4.tcp_syncookies = 1`
  - `net.ipv4.tcp_max_syn_backlog = 2048`
- Logs contain no nginx syntax errors, certificate errors, failed site loads, or fail2ban startup errors.