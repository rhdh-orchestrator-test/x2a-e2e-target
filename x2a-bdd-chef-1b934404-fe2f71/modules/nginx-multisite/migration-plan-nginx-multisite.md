---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: `nginx-multisite` configures nginx with security hardening, fail2ban, UFW, SSH restrictions, kernel network-security settings, optional self-signed TLS certificates, and data-bag-defined virtual hosts. Recipes execute in the order `security`, `nginx`, `ssl`, and `sites`, through `default.rb`. The `nginx_sites` data bag contents were not supplied, so exact virtual-host names, document roots, SSL-enabled sites, loop counts, and site-specific checks must be populated from the exported data before deployment.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**
  - Purpose: Main web server and virtual-host service
  - Location/Path: `/etc/nginx/nginx.conf`
  - Port/Socket: TCP `80`; TCP `443` when SSL-enabled sites exist; no Unix socket
  - Key Config: Worker user `nginx`, worker processes `auto`, worker connections `768`, gzip enabled, TLS 1.2/1.3, security headers, rate limiting, and per-site logs

- **fail2ban**
  - Purpose: Intrusion prevention for SSH and nginx
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH, HTTP, and HTTPS
  - Key Config: Enabled jails `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch`

- **ufw**
  - Purpose: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Default incoming policy `deny`; firewall enabled

- **sshd**
  - Purpose: SSH administration service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no` and `PasswordAuthentication no`

- **Virtual hosts from `nginx_sites`**
  - Purpose: Runtime-defined nginx sites
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443` when `ssl_enabled` is true
  - Key Config: `id`, `document_root`, and `ssl_enabled`
  - Exact instance names: Not present in the supplied migration source. The data-bag export must be obtained before creating the Ansible inventory or variable file.

The `nginx_sites` item attributes are used as follows:

- `id`: Virtual-host name, certificate filename, log filename, and static-content folder prefix.
- `document_root`: Site document root and nginx `root`.
- `ssl_enabled`: Enables certificate generation, HTTPS, HTTP-to-HTTPS redirection, and HSTS.

Global paths:

- Certificates: `/etc/ssl/certs`
- Private keys: `/etc/ssl/private`
- nginx secrets: `/etc/nginx/secrets`
- Available sites: `/etc/nginx/sites-available`
- Enabled sites: `/etc/nginx/sites-enabled`

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

No static files were identified in the supplied cookbook directory listing. Dynamic site content is referenced as:

```text
<site_folder>/index.html
```

The actual static-file paths must be discovered from the site-content layout.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the dependency order of security, nginx, certificates, and virtual-host configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban with:
     - `bantime = 3600`
     - `findtime = 600`
     - Default `maxretry = 3`
     - Backend `auto`
     - `sshd` on `ssh`, `/var/log/auth.log`, maximum retries `3`
     - `nginx-http-auth` on `http,https`, `/var/log/nginx/*error.log`, maximum retries `3`
     - `nginx-limit-req` on `http,https`, `/var/log/nginx/*error.log`, maximum retries `10`
     - `nginx-botsearch` on `http,https`, `/var/log/nginx/*access.log`, maximum retries `2`
   - Configures UFW with default deny and allows SSH, HTTP, and HTTPS.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies reverse-path filtering, redirect and source-route rejection, martian logging, ICMP protections, IPv6 disabling, SYN-cookie protection, and the configured TCP retry/backlog values.
   - Reloads sysctl settings with `sysctl -p /etc/sysctl.d/99-security.conf` when the template changes.
   - Sets `PermitRootLogin no` and `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Delays `fail2ban` and `sshd` restarts when their configuration changes.
   - Uses `community.general.ufw`, `ansible.posix.sysctl`, `ansible.builtin.lineinfile`, and service handlers in Ansible.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, `768` worker connections, standard HTTP settings, gzip, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, request-rate zones, request-buffer limits, timeouts, TLS session settings, TLS 1.2/1.3, and the specified cipher policy.
   - Enables and starts nginx.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`.
   - Writes the token to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, mode `0600`, and sensitive handling.
   - Reads the `nginx_sites` data-bag item names. Exact item names and loop counts were not supplied.
   - For each exported item, creates its `document_root` with owner `nginx`, group `nginx`, mode `0755`, and deploys `<document_root>/index.html` from `<site_folder>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - The site loop cannot be expanded with exact names until the `nginx_sites` data-bag export is provided.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Reads the `nginx_sites` data-bag item names.
   - Generates certificates only for items with `ssl_enabled: true`.
   - The exact SSL-enabled site names and iteration count were not supplied.
   - For each exported SSL-enabled site, creates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Uses a 365-day, RSA 2048-bit, self-signed certificate with Common Name `<site_name>`.
   - Preserves existing certificate/key pairs and does not regenerate them automatically.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Delays nginx reload after certificate generation.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Reads the `nginx_sites` data-bag item names.
   - The exact site names and iteration count were not supplied.
   - For each exported site, renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Passes `server_name`, `document_root`, `ssl_enabled`, `/etc/ssl/certs/<site_name>.crt`, and `/etc/ssl/private/<site_name>.key` to the template.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to `/etc/nginx/sites-available/<site_name>`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Configures HTTP, optional HTTPS, HTTP-to-HTTPS redirects, HTTP/2, HSTS, security headers, gzip, static-file lookup, access restrictions for `.htaccess`, `.git`, and `.svn`, and per-site access/error logs.
   - Delays nginx reload after template, link, or default-site changes.

Configured attribute defaults from `cookbooks/nginx-multisite/attributes/default.rb`:

```yaml
nginx_ssl_certificate_path: /etc/ssl/certs
nginx_ssl_private_key_path: /etc/ssl/private
security_fail2ban_enabled: true
security_ufw_enabled: true
security_ssh_disable_root: true
security_ssh_password_auth: false
```

The Chef execution tree installs and configures fail2ban and UFW directly; the migration must not assume their flags suppress those resources.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd`, restarted only when SSH hardening changes

**Data dependencies**:

- Chef encrypted data bag `nginx_secrets`, item `site`
- Chef data bag `nginx_sites`

## Credentials

**Detection Summary**: 1 credential detected across 1 recipe and 1 deployed file.

**Source**:

- **Provider**: `Chef::EncryptedDataBagItem`
- **URL**: None
- **Path**: Encrypted data bag `nginx_secrets`, item `site`, attribute `token`

### Site token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - Destination: `/etc/nginx/secrets/site_token`
- **Current storage**: Chef encrypted data bag
- **Usage context**: Written as a secret token file for nginx-related site use.
- **Data-bag loader**: `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`
- **File ownership and permissions**: `root:root`, mode `0600`
- **Ansible storage**: Ansible Vault, AAP secret credential, or another approved secret-management integration
- **Ansible deployment**: Use `ansible.builtin.copy` with `no_log: true`, owner `root`, group `root`, and mode `0600`

No external secret provider, hardcoded password, database credential, API key, environment-variable secret, or embedded TLS private-key content was detected. Runtime-generated TLS private keys must be retained at `/etc/ssl/private/<site_name>.key` with owner `root`, group `ssl-cert`, and mode `0640`.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-enabled/default
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
<document_root>/index.html
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
```

`/etc/nginx/sites-enabled/default` must be absent. The `<site_name>` and `<document_root>` values must be replaced with the exact values from the `nginx_sites` export.

**Service endpoints to check**:

- TCP `22` for SSH
- TCP `80` for HTTP
- TCP `443` for HTTPS when SSL-enabled sites exist
- `/run/nginx.pid`
- No Unix socket

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 time
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 time
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 time
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 time
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: once per exported `nginx_sites` item; exact count and names unavailable until the data bag is exported

## Pre-flight checks:

```bash
# Package verification
dpkg-query -W nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx --no-pager
systemctl status fail2ban --no-pager
systemctl status sshd --no-pager

# nginx configuration
nginx -t
nginx -T | grep -E 'server_name|listen 80|listen 443|ssl_certificate|ssl_certificate_key'
grep -E 'user nginx|worker_processes auto|worker_connections 768|keepalive_timeout 65' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens off|limit_req_zone|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Firewall
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# Kernel settings
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.icmp_echo_ignore_broadcasts
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries
cat /etc/sysctl.d/99-security.conf

# SSH hardening
grep '^PermitRootLogin no$' /etc/ssh/sshd_config
grep '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t
systemctl is-active sshd

# Secret metadata; do not print the token
stat -c '%U %G %a %n' /etc/nginx/secrets/site_token

# Required secret metadata
# Expected: root root 600 /etc/nginx/secrets/site_token

# Site directories and files
# Replace placeholders with every exact exported site name.
ls -l /etc/nginx/sites-available/<site_name>
ls -l /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
test ! -e /etc/nginx/sites-enabled/default

# Expected symlink target:
/etc/nginx/sites-available/<site_name>

# HTTP-only site validation
curl -i -H 'Host: <http_site_name>' http://127.0.0.1/
curl -s -o /dev/null -w '%{http_code}\n' \
  -H 'Host: <http_site_name>' \
  http://127.0.0.1/

# SSL-enabled site validation
curl -i -H 'Host: <ssl_site_name>' http://127.0.0.1/
curl -k -i --resolve <ssl_site_name>:443:127.0.0.1 \
  https://<ssl_site_name>/

# SSL certificate and key validation
ls -l /etc/ssl/certs/<ssl_site_name>.crt
ls -l /etc/ssl/private/<ssl_site_name>.key
openssl x509 -in /etc/ssl/certs/<ssl_site_name>.crt \
  -noout -subject -issuer -dates
stat -c '%U %G %a %n' /etc/ssl/private/<ssl_site_name>.key

# Expected key metadata:
# root ssl-cert 640 /etc/ssl/private/<ssl_site_name>.key

# Listening ports
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
journalctl -u sshd --no-pager -n 50
```

HTTP-only sites must return `200` and serve their deployed `index.html`. SSL-enabled sites must return `301` from HTTP, return `200` from HTTPS, include HSTS, and serve their deployed `index.html`. The migration is complete when the `nginx_sites` data-bag names have been explicitly populated and validated, nginx configuration passes, every named site has the expected files and symlink, required listeners and firewall rules are active, fail2ban and SSH hardening are applied, and sensitive files retain their required ownership and permissions.