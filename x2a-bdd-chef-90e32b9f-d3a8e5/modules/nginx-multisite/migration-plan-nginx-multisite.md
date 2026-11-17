---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: `nginx-multisite` installs and configures Nginx for dynamically defined sites from the Chef `nginx_sites` data bag. It applies host security controls with Fail2ban, UFW, sysctl, and SSH hardening; installs Nginx and shared security configuration; generates optional self-signed certificates; creates site document roots and index files; renders virtual hosts; and enables them in this order: `security` → `nginx` → `ssl` → `sites`. The supplied analysis does not include the runtime `nginx_sites` item names, so exact site instances must be provided as Ansible input rather than invented.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**
  - Purpose: Main web server and virtual-host service
  - Location/Path: `/etc/nginx/nginx.conf`
  - Port/Socket: `80/tcp`, `443/tcp`; PID file `/run/nginx.pid`
  - Key Config: Worker user `nginx`, `worker_processes auto`, `worker_connections 768`, gzip enabled, configuration includes `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`

- **fail2ban**
  - Purpose: Intrusion-prevention and log-monitoring service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH and Nginx logs; SSH protection uses port `22`
  - Key Config: Ban time `3600` seconds, find time `600` seconds, maximum retries `3`, backend `auto`

- **ufw**
  - Purpose: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows `22/tcp`, `80/tcp`, and `443/tcp`
  - Key Config: Default incoming policy `deny`; firewall enabled

- **sshd**
  - Purpose: SSH access service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: `22/tcp`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`

- **sysctl security configuration**
  - Purpose: Kernel and network security settings
  - Location/Path: `/etc/sysctl.d/99-security.conf`
  - Port/Socket: Not applicable
  - Key Config: Redirect protection, reverse-path filtering, source-route disabling, martian logging, ICMP restrictions, IPv6 disabling, SYN-cookie protection, and TCP backlog/retry settings

- **Runtime Nginx sites**
  - Purpose: Dynamically configured virtual hosts from the Chef `nginx_sites` data bag
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: HTTP `80/tcp`; HTTPS `443/tcp` when `ssl_enabled: true`
  - Key Config: Each item must provide `id`, `document_root`, and `ssl_enabled`
  - Instance names: Not present in the supplied source analysis; Ansible input must provide the exact site names and values

Recommended site input:

```yaml
nginx_sites:
  - id: example.invalid
    document_root: /var/www/example.invalid
    ssl_enabled: true
```

Default variables:

```yaml
nginx_ssl_certificate_path: /etc/ssl/certs
nginx_ssl_private_key_path: /etc/ssl/private

security_fail2ban_enabled: true
security_ufw_enabled: true
security_ssh_disable_root: true
security_ssh_password_auth: false

nginx_sites: []
```

## File Structure

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
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
    └── default/
        └── (no static files listed)
```

**Providers:**

```text
No provider files are used by the executed recipes.
```

The recipes use `cookbook_file` dynamically for site index files. The source filenames and site names depend on the runtime site data and were not included in the supplied analysis.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order `security` → `nginx` → `ssl` → `sites`.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban defaults and Nginx and SSH jails.
   - Sets the UFW default incoming policy to deny.
   - Allows SSH, HTTP, and HTTPS.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Reloads sysctl settings with `sysctl -p /etc/sysctl.d/99-security.conf` after changes.
   - Disables root SSH login with `PermitRootLogin no` when `security.ssh.disable_root` is enabled.
   - Disables SSH password authentication with `PasswordAuthentication no` when `security.ssh.password_auth` is disabled.
   - Restarts `sshd` only after either SSH setting changes.
   - Resources: 1 package resource, 2 service resources, 2 template resources, 8 execute resources total:
     - 5 UFW commands
     - 1 sysctl reload command
     - 1 root-login command
     - 1 password-authentication command

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures the `nginx` worker, logging, gzip, PID, and include settings.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, request-rate zones, request limits, timeouts, TLS 1.2 and TLS 1.3, SSL session caching, and cipher preferences.
   - Enables and starts `nginx`.
   - Creates `/etc/nginx/secrets` owned by `root:root` with mode `0700`.
   - Loads encrypted data-bag item `nginx_secrets/site` with `Chef::EncryptedDataBagItem.load`.
   - Writes `site_secret['token']` to `/etc/nginx/secrets/site_token` owned by `root:root` with mode `0600`.
   - Reads site definitions from the non-encrypted Chef data bag `nginx_sites`.
   - Derives `site_folder` from the portion of `site['id']` before the first dot.
   - Creates each supplied site’s `document_root` recursively, owned by `nginx:nginx` with mode `0755`.
   - Deploys each supplied site’s `index.html` with `cookbook_file`, owned by `nginx:nginx` with mode `0644`.
   - Runtime site names and source index filenames are unavailable from the supplied analysis and must be supplied to Ansible.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Processes runtime sites whose `ssl_enabled` value is `true`.
   - Generates `/etc/ssl/certs/<site_name>.crt` and `/etc/ssl/private/<site_name>.key` when the certificate/key pair does not already exist.
   - Uses a 2048-bit RSA self-signed certificate valid for 365 days.
   - Preserves the analyzed subject command, including the duplicate locality component:
     ```text
     /C=US/ST=Example/L=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com
     ```
   - Sets generated private keys to mode `0640` and ownership `root:ssl-cert`.
   - Notifies `nginx` for a delayed reload after certificate generation.
   - Exact SSL-enabled site names are unavailable from the supplied analysis.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` owned by `root:root` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` owned by `root:root` with mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to `/etc/nginx/sites-available/<site_name>`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Notifies `nginx` for a delayed reload after site templates, links, or default-site removal change.
   - Non-SSL sites receive an HTTP virtual host on port `80`.
   - SSL-enabled sites receive an HTTP-to-HTTPS redirect on port `80` and an HTTP/2 HTTPS virtual host on port `443`.
   - Site configurations include security headers, gzip, static-file `try_files`, `.ht` denial, `.git` and `.svn` denial, and site-specific access and error logs.
   - Exact runtime site names cannot be expanded because the contents of `nginx_sites` were not supplied.

## Dependencies

**External cookbook dependencies**: None listed.

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
- `sshd`

**Network dependencies**:

- SSH: `22/tcp`
- HTTP: `80/tcp`
- HTTPS: `443/tcp`

**Nginx IPC/socket details**:

- PID file: `/run/nginx.pid`
- Unix socket: None configured
- Upstream application socket: None configured

## Credentials

**Detection Summary**: 1 credential detected across the Nginx recipe and encrypted data-bag reference.

**Source**:
  - **Provider**: Chef encrypted data bag
  - **URL**: Not applicable
  - **Path**: Data bag `nginx_secrets`, item `site`

### Nginx Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Source provider**: Chef encrypted data bag, `nginx_secrets/site`
- **Current storage**: Chef encrypted data bag
- **Destination**: `/etc/nginx/secrets/site_token`
- **Usage context**: Written for Nginx-related site use; the supplied recipes do not consume the token elsewhere
- **File protection**: Owner `root`, group `root`, mode `0600`
- **Migration storage**: Ansible Vault or an AAP credential/secret-management integration
- **Requirement**: Do not place the plaintext token in ordinary variables or source-controlled files

### TLS Private Keys

- **Variable(s)**: `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL
- **Path**: `/etc/ssl/private/<site_name>.key`
- **Usage context**: Nginx HTTPS private key
- **Permissions**: Owner `root`, group `ssl-cert`, mode `0640`
- **Migration storage**: Preserve local generation and file permissions unless externally managed certificates are required

### TLS Certificates

- **Variable(s)**: `cert_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL
- **Path**: `/etc/ssl/certs/<site_name>.crt`
- **Usage context**: Nginx HTTPS certificate
- **Validity**: `365` days
- **Subject CN**: Runtime site name
- **Migration storage**: Preserve self-signed certificate generation unless certificates from an external CA are required

No HashiCorp Vault, CyberArk, AWS Secrets Manager, Conjur, environment-variable secret, database credential, or hardcoded API token was detected.

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
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs
/etc/ssl/private
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
<document_root>
<document_root>/index.html
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
```

Concrete `<site_name>` and `<document_root>` values must be supplied through `nginx_sites`.

**Service endpoints to check**:

- `22/tcp` — SSH
- `80/tcp` — HTTP
- `443/tcp` — HTTPS
- No Unix service socket

**Templates rendered**:

| Template | Destination | Render count |
|---|---|---:|
| `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` | `/etc/fail2ban/jail.local` | 1 |
| `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` | `/etc/nginx/nginx.conf` | 1 |
| `cookbooks/nginx-multisite/templates/default/security.conf.erb` | `/etc/nginx/conf.d/security.conf` | 1 |
| `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` | `/etc/sysctl.d/99-security.conf` | 1 |
| `cookbooks/nginx-multisite/templates/default/site.conf.erb` | `/etc/nginx/sites-available/<site_name>` | 1 per supplied runtime site |

## Pre-flight checks

```bash
# Service status: fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl status fail2ban --no-pager

# Service status: nginx
systemctl is-enabled nginx
systemctl is-active nginx
systemctl status nginx --no-pager

# Service status: sshd
systemctl is-enabled sshd
systemctl is-active sshd
systemctl status sshd --no-pager

# Fail2ban configuration
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# UFW policy and rules
ufw status verbose
ufw status numbered
ss -tlnp | grep ':22 '
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# SSH validation
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t

# Sysctl validation
sysctl -p /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# Nginx validation
nginx -t
nginx -T
grep -E 'user nginx|worker_processes auto|worker_connections 768|gzip on' /etc/nginx/nginx.conf
grep -E 'server_tokens off|ssl_protocols TLSv1.2 TLSv1.3|ssl_session_cache shared:SSL:10m' /etc/nginx/conf.d/security.conf

# Secret validation without displaying the token
stat -c '%U %G %a %n' /etc/nginx/secrets/site_token
test -s /etc/nginx/secrets/site_token

# Default site removal
test ! -e /etc/nginx/sites-enabled/default
```

For the exact runtime site names supplied to Ansible, validate each named site with its concrete values:

```bash
# Replace <site_name> and <document_root> with values from nginx_sites
test -d <document_root>
test -f <document_root>/index.html
stat -c '%U %G %a %n' <document_root>
stat -c '%U %G %a %n' <document_root>/index.html

test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -E 'server_name <site_name>|root <document_root>' \
  /etc/nginx/sites-available/<site_name>

curl -I -H 'Host: <site_name>' http://127.0.0.1/
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

For a site with `ssl_enabled: false`, HTTP must respond on port `80` without an HTTPS redirect.

For a site with `ssl_enabled: true`, validate the certificate and HTTPS endpoint:

```bash
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
stat -c '%U %G %a %n' /etc/ssl/certs/<site_name>.crt
stat -c '%U %G %a %n' /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates

curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
openssl s_client -connect 127.0.0.1:443 \
  -servername <site_name> </dev/null 2>/dev/null |
  openssl x509 -noout -subject -issuer -dates
```

Expected SSL-enabled site results:

- HTTP redirects to `https://<site_name>/` with status `301`.
- HTTPS responds on port `443`.
- The certificate subject contains `CN=<site_name>`.
- The response includes HSTS and configured security headers.
- The site serves content from its configured document root.
- The private key is owned by `root:ssl-cert` with mode `640`.
- The certificate and key are not regenerated when both already exist.