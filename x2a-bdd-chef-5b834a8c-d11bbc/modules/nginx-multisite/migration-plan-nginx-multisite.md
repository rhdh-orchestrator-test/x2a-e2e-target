---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with security hardening, UFW firewall rules, fail2ban, self-signed TLS certificates, and data-bag-driven virtual hosts. Execution order is `security` → `nginx` → `ssl` → `sites`. Site names, document roots, SSL flags, and static content source names are read at runtime from the `nginx_sites` data bag. The supplied analysis does not expose the individual site item names, so those names and values must be exported and recorded before migration. The nginx site token is loaded from encrypted Chef data bag `nginx_secrets`, item `site`.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **fail2ban**: Intrusion prevention service
  - Package: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - State: enabled and started
  - Restart trigger: changes to the jail template cause a delayed restart
  - Configured jails: `sshd`, `nginx-http-auth`, `nginx-limit-req`, `nginx-botsearch`
  - Global settings: `bantime = 3600`, `findtime = 600`, `maxretry = 3`, `backend = auto`

- **ufw**: Host firewall
  - Package: `ufw`
  - Policy: default deny
  - Allowed services: SSH, HTTP, HTTPS
  - Allowed ports: TCP `22`, `80`, and `443`
  - State: enabled

- **ssh**: SSH daemon hardening
  - Configuration: `/etc/ssh/sshd_config`
  - `PermitRootLogin`: `no`
  - `PasswordAuthentication`: `no`
  - Restart trigger: either SSH configuration change causes a delayed `sshd` restart

- **nginx**: Main web server
  - Package: `nginx`
  - Configuration: `/etc/nginx/nginx.conf`
  - Security configuration: `/etc/nginx/conf.d/security.conf`
  - Site configuration: `/etc/nginx/sites-available/<site_name>`
  - Enabled-site link: `/etc/nginx/sites-enabled/<site_name>`
  - Ports: TCP `80` and TCP `443`
  - User: `nginx`
  - State: enabled and started
  - Unix socket: none

- **nginx site instances**: Virtual hosts loaded from Chef data bag `nginx_sites`
  - Exact site names: not present in the supplied analysis and must be exported before migration
  - Site name source: data-bag item `id`
  - Document root source: `document_root`
  - SSL flag source: `ssl_enabled`
  - Document root ownership: `nginx:nginx`, mode `0755`
  - Static content destination: `<document_root>/index.html`
  - Static content source: `<site_folder>/index.html`, where `<site_folder>` is the first component of `<site_name>`
  - HTTP-only sites listen on TCP `80`
  - SSL-enabled sites listen on TCP `80` and TCP `443`, redirect HTTP to HTTPS, and use HTTP/2
  - Access log: `/var/log/nginx/<site_name>_access.log`
  - Error log: `/var/log/nginx/<site_name>_error.log`

**Migration prerequisite**: Export the `nginx_sites` data-bag item names and their `id`, `document_root`, and `ssl_enabled` values. The final Ansible inventory must contain one named site entry for every data-bag item. No actual site names are available in the supplied plan, so none can be truthfully expanded here.

## File Structure

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb

cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb

cookbooks/nginx-multisite/attributes/default.rb
```

No provider files are used.

No static files are listed in the supplied cookbook directory listing. Runtime `cookbook_file` resources reference `<site_folder>/index.html`, but those files are not present in the supplied inventory and must not be invented.

## Attributes

Source: `cookbooks/nginx-multisite/attributes/default.rb`

| Attribute | Default |
|---|---|
| `node['nginx']['ssl']['certificate_path']` | `/etc/ssl/certs` |
| `node['nginx']['ssl']['private_key_path']` | `/etc/ssl/private` |
| `node['security']['fail2ban']['enabled']` | `true` |
| `node['security']['ufw']['enabled']` | `true` |
| `node['security']['ssh']['disable_root']` | `true` |
| `node['security']['ssh']['password_auth']` | `false` |

The fail2ban and UFW attributes are defined but are not used as conditionals in `security.rb`; those components are installed and configured unconditionally.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/nginx-multisite/recipes/default.rb`)
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the dependency order: security, nginx installation, certificates, then virtual hosts.

2. **`security`** (`cookbooks/nginx-multisite/recipes/security.rb`)
   - Installs packages `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`, mode `0644`.
   - Configures fail2ban jails:
     - `sshd`: port `ssh`, log `/var/log/auth.log`, bantime `3600`, max retries `3`.
     - `nginx-http-auth`: ports `http,https`, log `/var/log/nginx/*error.log`, bantime `3600`, max retries `3`.
     - `nginx-limit-req`: ports `http,https`, log `/var/log/nginx/*error.log`, bantime `3600`, max retries `10`.
     - `nginx-botsearch`: ports `http,https`, log `/var/log/nginx/*access.log`, bantime `3600`, max retries `2`.
   - Applies UFW rules:
     - Default deny.
     - Allow SSH.
     - Allow HTTP.
     - Allow HTTPS.
     - Enable UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`, mode `0644`.
   - Configures reverse-path filtering, redirect and source-route protection, martian logging, ICMP protections, IPv6 disabling, and TCP SYN flood protection.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` after configuration changes.
   - Sets `PermitRootLogin no` when `node['security']['ssh']['disable_root']` is true.
   - Sets `PasswordAuthentication no` when `node['security']['ssh']['password_auth']` is false.
   - Restarts `sshd` only when SSH hardening changes the configuration.
   - Resource summary: package collection with 2 packages, 2 services, 2 templates, and **8 execute resources**.

3. **`nginx`** (`cookbooks/nginx-multisite/recipes/nginx.rb`)
   - Installs package `nginx`.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`, mode `0644`.
   - Configures user `nginx`, automatic worker processes, PID `/run/nginx.pid`, 768 worker connections, standard access and error logs, gzip, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`, mode `0644`.
   - Configures server-token hiding, `login` and `api` rate-limit zones, request buffer limits, `client_max_body_size 1k`, ten-second client/header/send timeouts, TLS 1.2 and 1.3, shared SSL session cache, ten-minute SSL session timeout, the specified ECDHE/DHE cipher list, and server cipher preference.
   - Enables and starts `nginx`.
   - Creates `/etc/nginx/secrets`, owned by `root:root`, mode `0700`.
   - Loads encrypted data-bag item `nginx_secrets/site` and writes `site_secret['token']` to `/etc/nginx/secrets/site_token`, owned by `root:root`, mode `0600`.
   - Reads site entries from `nginx_sites`.
   - For each named data-bag site, creates its configured document root recursively as `nginx:nginx`, mode `0755`.
   - Derives `site_folder` from `site_name.split('.').first`.
   - Deploys `<site_folder>/index.html` to `<document_root>/index.html`, owned by `nginx:nginx`, mode `0644`.
   - Exact site iterations cannot be expanded until the data-bag inventory is supplied.

4. **`ssl`** (`cookbooks/nginx-multisite/recipes/ssl.rb`)
   - Installs the source-analysis package names `openssl` and `ca-cert`.
   - On platforms where `ca-cert` is not a literal package name, map it explicitly to the platform package `ca-certificates`; do not silently omit the dependency.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` as `root:root`, mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert`, mode `0710`.
   - Reads SSL-enabled entries from `nginx_sites`.
   - For each named SSL-enabled site, generates:
     - Certificate: `/etc/ssl/certs/<site_name>.crt`
     - Private key: `/etc/ssl/private/<site_name>.key`
   - Uses a 2048-bit RSA self-signed certificate valid for 365 days with subject `CN=<site_name>`.
   - Sets private-key ownership to `root:ssl-cert`, mode `0640`.
   - Skips generation when both certificate and key already exist.
   - Reloads nginx after newly generated certificates.
   - Exact SSL-enabled site iterations cannot be expanded until the data-bag inventory is supplied.

5. **`sites`** (`cookbooks/nginx-multisite/recipes/sites.rb`)
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled`, both owned by `root:root`, mode `0755`.
   - Reads site entries from `nginx_sites`.
   - For every named site, renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>`, mode `0644`.
   - Passes `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` to the template.
   - SSL-enabled sites receive HTTP-to-HTTPS redirection, an HTTPS listener with HTTP/2, generated certificate paths, one-year HSTS including subdomains, security headers, gzip, `try_files`, and `.htaccess`, `.git`, and `.svn` protection.
   - HTTP-only sites receive an HTTP listener and the same content and security settings without TLS.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symbolic link to `/etc/nginx/sites-available/<site_name>`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Reloads nginx after template, link, or default-site changes.
   - Exact site template and link iterations cannot be expanded until the data-bag inventory is supplied.

## Dependencies

**External cookbook dependencies**: None declared.

**Supported platforms**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:
- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-cert` as recorded in the source analysis; map to `ca-certificates` where required by the target platform

**Service dependencies**:
- `fail2ban`
- `nginx`
- `sshd`, restarted only after SSH hardening changes

**External data dependencies**:
- Encrypted Chef data bag `nginx_secrets`, item `site`
- Chef data bag `nginx_sites`
- Runtime cookbook files named `<site_folder>/index.html`

## Credentials

**Detection Summary**: 1 credential source detected across `cookbooks/nginx-multisite/recipes/nginx.rb`.

**Source**:
- **Provider**: Internal Chef encrypted data bag
- **URL**: Not detected
- **Path**: Data bag `nginx_secrets`, item `site`

### Site Token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **Destination ownership**: `root:root`
- **Destination mode**: `0600`
- **Migration storage**: Ansible Vault or an approved external secret manager
- **Secret-manager endpoint**: Not detected

### TLS Private Keys

- **Variable/path**: `key_file`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally with OpenSSL
- **Usage context**: TLS private key for each SSL-enabled site
- **Path**: `/etc/ssl/private/<site_name>.key`
- **Ownership**: `root:ssl-cert`
- **Mode**: `0640`

Corresponding self-signed certificates are generated at `/etc/ssl/certs/<site_name>.crt`.

No HashiCorp Vault, CyberArk, AWS Secrets Manager, Conjur, plaintext password, API key, database credential, or environment-variable secret reference was detected.

## Checks for the Migration

**Files to verify**:
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available/`
- `/etc/nginx/sites-enabled/`
- `/etc/ssl/certs/`
- `/etc/ssl/private/`
- `<document_root>/index.html`
- `/etc/nginx/sites-available/<site_name>`
- `/etc/nginx/sites-enabled/<site_name>`
- `/etc/ssl/certs/<site_name>.crt`
- `/etc/ssl/private/<site_name>.key`
- `/var/log/nginx/<site_name>_access.log`
- `/var/log/nginx/<site_name>_error.log`

**Service endpoints to check**:
- TCP `22`: SSH firewall allowance
- TCP `80`: nginx HTTP listener
- TCP `443`: nginx HTTPS listener for SSL-enabled sites
- No Unix sockets

**Templates rendered**:
- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: 1 render per named `nginx_sites` item; exact count requires the data-bag inventory

## Pre-flight checks

Run these checks after replacing the site placeholders with the actual named entries exported from `nginx_sites`.

```bash
# Package status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# Configuration validation
nginx -t
nginx -T | grep -E 'listen (80|443)|server_name|ssl_certificate|ssl_certificate_key'

# Listening endpoints
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Firewall
ufw status verbose
ufw status numbered
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH hardening
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Kernel security
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# Secret permissions; never print the token
test -f /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token

# Default site removal
test ! -e /etc/nginx/sites-enabled/default
```

For every actual HTTP-only site, verify individually:

```bash
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -E 'server_name|root|listen|access_log|error_log' \
  /etc/nginx/sites-available/<site_name>
test -d <document_root>
test -f <document_root>/index.html
stat -c '%U:%G %a %n' <document_root> <document_root>/index.html
curl -I -H 'Host: <site_name>' http://127.0.0.1/
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

Expected HTTP-only results:
- HTTP responds with the intended nginx response.
- The site root is owned by `nginx:nginx`, mode `0755`.
- `index.html` is owned by `nginx:nginx`, mode `0644`.
- The enabled-site link resolves to the corresponding available-site file.

For every actual SSL-enabled site, verify individually:

```bash
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key

curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/

openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout \
  -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

Expected SSL results:
- HTTP returns a `301` redirect to `https://<site_name>/`.
- HTTPS succeeds with `-k` because the certificate is self-signed.
- The HTTPS response includes HSTS.
- The certificate subject contains `CN=<site_name>`.
- The certificate is valid for 365 days from generation.
- The private key is owned by `root:ssl-cert`, mode `0640`.

Additional validation:

```bash
grep -E 'bantime|findtime|maxretry|backend' /etc/fail2ban/jail.local
grep -A7 '^\[sshd\]' /etc/fail2ban/jail.local
grep -A7 '^\[nginx-http-auth\]' /etc/fail2ban/jail.local
grep -A7 '^\[nginx-limit-req\]' /etc/fail2ban/jail.local
grep -A7 '^\[nginx-botsearch\]' /etc/fail2ban/jail.local

journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
journalctl -u sshd --no-pager -n 50

tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
```

The migration is complete only after the actual `nginx_sites` inventory has been converted into named Ansible site variables and every named site has passed its individual configuration, content, endpoint, and applicable TLS checks.