---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and static index files; generates self-signed RSA certificates; deploys nginx, security, and virtual-host configuration; redirects HTTP to HTTPS; applies firewall and kernel hardening; and disables root SSH login and SSH password authentication.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; index file `/opt/server/test/index.html`
  - Access Log: `/var/log/nginx/test.cluster.local_access.log`
  - Error Log: `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; index file `/opt/server/ci/index.html`
  - Access Log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error Log: `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; index file `/opt/server/status/index.html`
  - Access Log: `/var/log/nginx/status.cluster.local_access.log`
  - Error Log: `/var/log/nginx/status.cluster.local_error.log`

**Security configuration**:

- **fail2ban**
  - Enabled: `true`
  - Service: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`

- **ufw**
  - Enabled: `true`
  - Default policy: deny
  - Allowed services: SSH, HTTP, HTTPS

- **ssh**
  - Root login: disabled
  - Password authentication: disabled
  - Configuration: `/etc/ssh/sshd_config`

## File Structure

The following is the complete relevant directory listing from the cookbook.

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

No provider files or custom resources are used by the executed recipe tree.

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

No static files under `files/default/` or `files/` are listed. The `cookbook_file` resources reference these required sources, which must be supplied during the Ansible migration:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. `cookbooks/nginx-multisite/recipes/security.rb`
2. `cookbooks/nginx-multisite/recipes/nginx.rb`
3. `cookbooks/nginx-multisite/recipes/ssl.rb`
4. `cookbooks/nginx-multisite/recipes/sites.rb`

### 1. Default entry recipe

**Recipe**: `cookbooks/nginx-multisite/recipes/default.rb`

- Includes `cookbooks/nginx-multisite/recipes/security.rb`.
- Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
- Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
- Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
- The Ansible role or entry task file must preserve this execution order.
- Security configuration runs before nginx installation.
- nginx installation and base configuration run before certificate generation.
- Certificate generation runs before virtual-host deployment.

### 2. Security configuration

**Recipe**: `cookbooks/nginx-multisite/recipes/security.rb`

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts `fail2ban`.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
- Restarts fail2ban only when `/etc/fail2ban/jail.local` changes.
- Configures fail2ban with:
  - Global bantime `3600`
  - Global findtime `600`
  - Global maxretry `3`
  - Backend `auto`
  - `sshd` jail on port `ssh`, logging `/var/log/auth.log`, bantime `3600`, max retries `3`
  - `nginx-http-auth` jail on ports `http,https`, logging `/var/log/nginx/*error.log`, bantime `3600`, max retries `3`
  - `nginx-limit-req` jail on ports `http,https`, logging `/var/log/nginx/*error.log`, bantime `3600`, max retries `10`
  - `nginx-botsearch` jail on ports `http,https`, logging `/var/log/nginx/*access.log`, bantime `3600`, max retries `2`
- Configures UFW with:
  - Default incoming policy `deny`
  - SSH allowed
  - HTTP `80/tcp` allowed
  - HTTPS `443/tcp` allowed
  - Firewall enabled
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Reloads sysctl with `sysctl -p /etc/sysctl.d/99-security.conf` only when the sysctl template changes.
- Applies these kernel settings:
  - `net.ipv4.conf.default.rp_filter = 1`
  - `net.ipv4.conf.all.rp_filter = 1`
  - IPv4 and IPv6 ICMP redirects disabled
  - IPv4 and IPv6 source routing disabled
  - Martian packet logging enabled
  - ICMP echo requests and broadcast pings ignored
  - IPv6 disabled on `all`, `default`, and `lo`
  - TCP SYN cookies enabled
  - TCP SYN backlog set to `2048`
  - TCP SYN-ACK retries set to `2`
  - TCP SYN retries set to `5`
- Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
- Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
- Validates SSH configuration before restarting the SSH service when either SSH setting changes.

**Resource count**:

- Package: `1` resource declaration installing two packages
- Service: `2`
- Template: `2`
- Execute: `8`
  - Five UFW commands
  - `reload_sysctl`
  - `disable root login`
  - `disable password auth`
- Total Chef resource declarations: `13`

### 3. nginx installation and base configuration

**Recipe**: `cookbooks/nginx-multisite/recipes/nginx.rb`

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Enables and starts nginx.
- Reloads nginx after changes to the main configuration, security configuration, site files, site links, removed default site, or generated certificates.
- The main nginx configuration specifies:
  - Worker user `www-data`
  - Worker processes `auto`
  - PID file `/run/nginx.pid`
  - Module include `/etc/nginx/modules-enabled/*.conf`
  - Worker connections `768`
  - Access log `/var/log/nginx/access.log`
  - Error log `/var/log/nginx/error.log`
  - Gzip enabled
  - Includes `/etc/nginx/mime.types`
  - Includes `/etc/nginx/conf.d/*.conf`
  - Includes `/etc/nginx/sites-enabled/*`
  - Keepalive timeout `65`
  - Default content type `application/octet-stream`
- The nginx security configuration specifies:
  - `server_tokens off`
  - `login` request-rate zone: `10m`, `10r/m`
  - `api` request-rate zone: `10m`, `30r/m`
  - Client body buffer `1K`
  - Client header buffer `1k`
  - Maximum body size `1k`
  - Large header buffers `2 1k`
  - Client body timeout `10`
  - Client header timeout `10`
  - Send timeout `10`
  - TLS protocols `TLSv1.2 TLSv1.3`
  - TLS session cache `shared:SSL:10m`
  - TLS session timeout `10m`
  - Explicit ECDHE/DHE cipher list
  - Server cipher preference enabled

The document-root and static-file loop expands to these exact resources:

- **test.cluster.local**
  - Creates `/opt/server/test` owned by `www-data:www-data`, mode `0755`, recursively.
  - Copies `test/index.html` to `/opt/server/test/index.html`, owned by `www-data:www-data`, mode `0644`.

- **ci.cluster.local**
  - Creates `/opt/server/ci` owned by `www-data:www-data`, mode `0755`, recursively.
  - Copies `ci/index.html` to `/opt/server/ci/index.html`, owned by `www-data:www-data`, mode `0644`.

- **status.cluster.local**
  - Creates `/opt/server/status` owned by `www-data:www-data`, mode `0755`, recursively.
  - Copies `status/index.html` to `/opt/server/status/index.html`, owned by `www-data:www-data`, mode `0644`.

**Resource count**:

- Package: `1`
- Template: `2`
- Service: `1`
- Directory: `3`
- Cookbook file: `3`
- Total resource declarations: `10`

### 4. SSL packages, directories, and certificates

**Recipe**: `cookbooks/nginx-multisite/recipes/ssl.rb`

- Installs the `openssl` and `ca-certificates` packages.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` owned by `root:root`, mode `0755`.
- Creates `/etc/ssl/private` owned by `root:ssl-cert`, mode `0710`.
- Generates RSA `2048` self-signed certificates valid for `365` days.
- Uses certificate subject fields:
  - Country: `US`
  - State: `Example`
  - Locality: `Example`
  - Organization: `Example Org`
  - Organizational unit: `IT`
  - Email: `admin@example.com`

The SSL loop expands to these exact certificate resources:

- **test.cluster.local**
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Resource: `execute[generate-ssl-cert-test.cluster.local]`
  - Common name: `test.cluster.local`

- **ci.cluster.local**
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Resource: `execute[generate-ssl-cert-ci.cluster.local]`
  - Common name: `ci.cluster.local`

- **status.cluster.local**
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Resource: `execute[generate-ssl-cert-status.cluster.local]`
  - Common name: `status.cluster.local`

Each certificate command is equivalent to:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout <site-key> \
  -out <site-certificate> \
  -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site-name>/emailAddress=admin@example.com"

chmod 640 <site-key>
chown root:ssl-cert <site-key>
```

- Certificate generation is skipped when both the certificate and key already exist.
- Private keys are owned by `root:ssl-cert` with mode `0640`.
- Each changed certificate or key notifies nginx to reload.

**Resource count**:

- Package: `1` resource declaration installing two packages
- Group: `1`
- Directory: `2`
- Execute: `3`
- Total resource declarations: `7`

### 5. Virtual-host site configuration

**Recipe**: `cookbooks/nginx-multisite/recipes/sites.rb`

The site loop expands to these exact virtual-host resources:

- **test.cluster.local**
  - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
  - Uses document root `/opt/server/test`.
  - Uses certificate `/etc/ssl/certs/test.cluster.local.crt`.
  - Uses private key `/etc/ssl/private/test.cluster.local.key`.
  - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.

- **ci.cluster.local**
  - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
  - Uses document root `/opt/server/ci`.
  - Uses certificate `/etc/ssl/certs/ci.cluster.local.crt`.
  - Uses private key `/etc/ssl/private/ci.cluster.local.key`.
  - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.

- **status.cluster.local**
  - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
  - Uses document root `/opt/server/status`.
  - Uses certificate `/etc/ssl/certs/status.cluster.local.crt`.
  - Uses private key `/etc/ssl/private/status.cluster.local.key`.
  - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.

All rendered site files use mode `0644`. The recipe also removes `/etc/nginx/sites-enabled/default`. Every changed template, link, and default-site removal notifies nginx to reload after `nginx -t` succeeds.

Each SSL-enabled virtual host provides:

- HTTP listener on port `80`
- HTTP-to-HTTPS redirect
- HTTPS listener on port `443`
- HTTP/2
- TLS 1.2 and TLS 1.3
- HSTS with `max-age=31536000; includeSubDomains`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- Content Security Policy limited to the site origin, with inline scripts and styles permitted
- Gzip compression
- `try_files $uri $uri/ =404`
- Denial of `.htaccess` paths
- Denial of `.git` and `.svn` paths
- Site-specific access and error logs

**Resource count**:

- Template: `3`
- Link: `3`
- File: `1`
- Total resource declarations: `7`

## Dependencies

**External cookbook dependencies**: None specified in the supplied metadata.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started; restarted when `/etc/fail2ban/jail.local` changes
- `nginx`: enabled and started; reloaded after configuration, site, symlink, or certificate changes
- `ssh`: restarted when root-login or password-authentication settings change

**Ansible collection dependencies**:

- `community.general` for UFW management
- `ansible.posix` for sysctl management
- `community.crypto` for certificate and private-key generation, if available

## Credentials

**Detection Summary**: No application credentials, passwords, API tokens, data bags, vault lookups, or external secret-manager integrations were detected. Three locally generated TLS private keys were identified as sensitive files.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### Self-signed TLS private keys

- **Variable(s)**:
  - `key_file`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; not stored in a data bag, Chef Vault, environment variable, or external secret manager
- **Usage context**: TLS termination for the three nginx HTTPS virtual hosts
- **Permissions**: Owner `root`, group `ssl-cert`, mode `0640`

### Certificate subject email

- **Variable(s)**: Literal `emailAddress=admin@example.com`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded non-secret certificate subject value
- **Usage context**: Subject metadata in each self-signed certificate
- **Security classification**: Not a password, token, or authentication credential

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, Vault URL, database connection string, API key, or environment-variable secret reference was detected.

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
- `/etc/nginx/sites-enabled/default` should be absent
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

No Unix sockets or application-specific IPC endpoints are configured.

**Templates rendered**:

- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Verify required packages.
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Verify managed services.
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active ssh

# Validate nginx configuration.
nginx -t
nginx -T | grep -E \
'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local|listen 80|listen 443'

grep -E 'worker_processes|worker_connections|access_log|error_log|gzip on' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|ssl_protocols|client_max_body_size' \
  /etc/nginx/conf.d/security.conf

# Verify test.cluster.local.
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
test -L /etc/nginx/sites-enabled/test.cluster.local

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -dates

# Verify ci.cluster.local.
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
test -L /etc/nginx/sites-enabled/ci.cluster.local

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -dates

# Verify status.cluster.local.
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
test -L /etc/nginx/sites-enabled/status.cluster.local

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -dates

# Verify listeners.
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Verify TLS and security headers.
curl -k -s -D - --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ -o /dev/null | \
  grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Referrer-Policy|Content-Security-Policy'

openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local -tls1_2 </dev/null

openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local -tls1_3 </dev/null

# Verify fail2ban.
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

grep -E 'bantime|findtime|maxretry|backend|enabled|logpath' \
  /etc/fail2ban/jail.local

# Verify UFW.
ufw status verbose
ufw status numbered

# Verify SSH hardening.
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t
systemctl status ssh

# Verify sysctl hardening.
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.icmp_echo_ignore_broadcasts
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv6.conf.default.disable_ipv6
sysctl net.ipv6.conf.lo.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries

# Verify the default nginx site was removed.
test ! -e /etc/nginx/sites-enabled/default
```