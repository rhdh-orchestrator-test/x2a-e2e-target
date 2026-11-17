---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with multiple data-bag-defined sites, optional self-signed HTTPS certificates, fail2ban, UFW, SSH hardening, kernel security settings, nginx security headers, protected site-token storage, per-site document roots, and virtual hosts. The fixed service instances are nginx, fail2ban, UFW, and sshd. Actual site names, document roots, and SSL settings are unavailable because they are stored in the `nginx_sites` Chef data bag and must be supplied to Ansible separately.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Web server hosting the configured sites
  - Location/Path: `/etc/nginx/nginx.conf`, `/etc/nginx/sites-available`, `/etc/nginx/sites-enabled`
  - Port/Socket: TCP `80`; TCP `443` when SSL-enabled sites exist; PID `/run/nginx.pid`
  - Key Config: Worker user `nginx`, worker processes `auto`, 768 worker connections, gzip enabled, TLS 1.2 and TLS 1.3, security headers, request limits, and per-site access/error logs

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors `/var/log/auth.log` and nginx logs
  - Key Config: `bantime=3600`, `findtime=600`, `maxretry=3`, SSH jail, nginx HTTP-auth, request-limit, and bot-search jails

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Default inbound policy deny; firewall enabled

- **sshd**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no` and `PasswordAuthentication no`

- **nginx site instances**: Runtime virtual hosts defined in the `nginx_sites` data bag
  - Location/Path: Site-specific document roots, `/etc/nginx/sites-available/<site_name>`, and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: TCP `80`; TCP `443` when `ssl_enabled` is true
  - Key Config: Each item supplies `id`, `document_root`, and `ssl_enabled`. Exact site names and attributes were not included in the source and must be provided as Ansible variables.

Runtime site paths are derived as follows:

- Document root: `config['document_root']`
- Index source: `<site_folder>/index.html`, where `site_folder` is the first component of `site_name.split('.')`
- Certificate: `/etc/ssl/certs/<site_name>.crt`
- Private key: `/etc/ssl/private/<site_name>.key`
- Virtual host: `/etc/nginx/sites-available/<site_name>`
- Enabled link: `/etc/nginx/sites-enabled/<site_name>`
- Access log: `/var/log/nginx/<site_name>_access.log`
- Error log: `/var/log/nginx/<site_name>_error.log`

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

No static file path is listed. The `nginx.rb` recipe references dynamic cookbook files such as `<site_folder>/index.html`; equivalent site index files must be supplied separately.

## Attributes

Source file:

```text
cookbooks/nginx-multisite/attributes/default.rb
```

Configured defaults:

```ruby
default['nginx']['ssl']['certificate_path'] = '/etc/ssl/certs'
default['nginx']['ssl']['private_key_path'] = '/etc/ssl/private'

default['security']['fail2ban']['enabled'] = true
default['security']['ufw']['enabled'] = true
default['security']['ssh']['disable_root'] = true
default['security']['ssh']['password_auth'] = false
```

Ansible equivalents:

```yaml
nginx_ssl_certificate_path: /etc/ssl/certs
nginx_ssl_private_key_path: /etc/ssl/private

security_fail2ban_enabled: true
security_ufw_enabled: true
security_ssh_disable_root: true
security_ssh_password_auth: false
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Ansible task-file inclusion must preserve this execution sequence.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures SSH, nginx HTTP-auth, nginx request-limit, and nginx bot-search fail2ban jails.
   - Applies UFW default deny and allows SSH, HTTP, and HTTPS.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-route rejection, martian logging, ICMP restrictions, IPv6 disabling, SYN cookies, TCP backlog, and retry parameters.
   - Applies `sysctl -p /etc/sysctl.d/99-security.conf` after sysctl configuration changes.
   - Sets `PermitRootLogin no` and `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` only when SSH hardening changes.
   - Resource summary: 1 package declaration, 2 services, 2 templates, and 8 execute resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs `nginx`.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts nginx.
   - Creates `/etc/nginx/secrets` as `root:root` with mode `0700`.
   - Loads token `site_secret['token']` from encrypted data bag `nginx_secrets`, item `site`.
   - Writes the token to `/etc/nginx/secrets/site_token` as `root:root` with mode `0600`; the resource is sensitive.
   - Reads runtime site items from the `nginx_sites` data bag.
   - Creates each supplied site’s configured document root as `nginx:nginx` with mode `0755`.
   - Derives the site-folder name from the first component of the site ID and deploys its `index.html` as `nginx:nginx` with mode `0644`.
   - Actual site item names are unavailable; no runtime site loop can be expanded with exact names from the supplied source.
   - Resource summary excluding unavailable runtime site count: 1 package, 2 templates, 1 service, 1 fixed directory plus 1 runtime directory per site, 1 file, and 1 runtime cookbook file per site.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` as `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert` with mode `0710`.
   - Reads SSL settings from the `nginx_sites` data bag.
   - For each unavailable runtime item whose `ssl_enabled` value is `true`, generates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Uses a 2048-bit RSA self-signed certificate valid for 365 days with the site name as the common name.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Skips generation when both certificate and key already exist.
   - Reloads nginx after generating a certificate or key.
   - No exact SSL-enabled site names were supplied, so runtime certificate iterations cannot be expanded.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` as `root:root` with mode `0755`.
   - The directory loop contains exactly:
     - `/etc/nginx/sites-available`
     - `/etc/nginx/sites-enabled`
   - Reads site definitions from the `nginx_sites` data bag.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a link to `/etc/nginx/sites-available/<site_name>`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - SSL-enabled sites listen on port `80`, redirect to HTTPS with status `301`, and listen on port `443` with `ssl`, `http2`, TLS 1.2/1.3, and HSTS.
   - Non-SSL sites serve HTTP on port `80` without an HTTPS server block.
   - Both branches configure document roots, index files, security headers, gzip, `try_files`, `.htaccess` and VCS-path denial, and site-specific logs.
   - Exact site names were not supplied, so runtime template and link iterations cannot be expanded.

## Dependencies

**External cookbook dependencies**: None listed.

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

**Data dependencies**:

- Encrypted data bag `nginx_secrets`, item `site`
- Normal data bag `nginx_sites`

**Platform support from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The recipes use UFW and Debian-style nginx site directories, so the Ansible role must validate the target platform before applying those tasks.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file. Generated TLS keys and certificates are local OpenSSL artifacts, not externally sourced credentials.

**Source**:
  - **Provider**: `Chef::EncryptedDataBagItem`
  - **URL**: Not applicable
  - **Path**: `cookbooks/nginx-multisite/recipes/nginx.rb`
  - **Data bag**: `nginx_secrets`
  - **Item**: `site`

### Nginx Site Token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Destination**: `/etc/nginx/secrets/site_token`
- **Owner and group**: `root:root`
- **Mode**: `0600`
- **Usage context**: Secret token made available to nginx through a protected local file
- **Sensitivity handling**: Chef file resource marked `sensitive true`
- **Migration storage**: Ansible Vault or an AAP-supported secret-management integration
- **Logging requirement**: Do not log the token while writing the destination file

### TLS Private Keys

- **Variable/path pattern**: `/etc/ssl/private/<site_name>.key`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Source provider**: Local OpenSSL generation
- **Current storage**: Generated locally, not loaded from a secret store
- **Usage context**: nginx TLS private key
- **Generation**: `openssl req -x509 -nodes -days 365 -newkey rsa:2048`
- **Owner and group**: `root:ssl-cert`
- **Mode**: `0640`

### TLS Certificates

- **Variable/path pattern**: `/etc/ssl/certs/<site_name>.crt`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Source provider**: Local OpenSSL generation
- **Current storage**: Generated locally
- **Usage context**: nginx TLS certificate
- **Validity**: 365 days
- **Subject**: Site name as common name and `admin@example.com` as email address

No Vault, CyberArk, AWS Secrets Manager, Conjur, plaintext password, API key, database credential, or environment-variable secret reference was detected.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets/site_token
/etc/nginx/sites-enabled/default
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/secrets
/etc/ssl/certs
/etc/ssl/private
/run/nginx.pid
<document_root>/index.html
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
```

**Service endpoints to check**:

- nginx HTTP: TCP `80`
- nginx HTTPS: TCP `443` when an SSL-enabled site is configured
- SSH: TCP `22`
- nginx PID: `/run/nginx.pid`
- nginx access log: `/var/log/nginx/access.log`
- nginx error log: `/var/log/nginx/error.log`
- fail2ban SSH input: `/var/log/auth.log`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: 1 render per supplied `nginx_sites` item

## Pre-flight checks

Populate the Ansible site list with the exact `nginx_sites` data bag items before running runtime site checks. The source plan contains no actual site names, so `<site_name>` and `<document_root>` must be replaced with supplied values.

```bash
# Package checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# nginx instance
systemctl status nginx
nginx -t
nginx -T
ss -tlnp | grep ':80'
curl -I http://127.0.0.1/

# fail2ban instance
systemctl status fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# ufw instance
ufw status verbose
ufw status numbered
# Expected: active, default deny, and allowed 22/tcp, 80/tcp, and 443/tcp

# sshd instance
systemctl status sshd
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
ss -tlnp | grep ':22'

# Kernel security configuration
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# Site-specific HTTP instance
curl -I -H 'Host: <site_name>' http://127.0.0.1/
ls -ld <document_root>
ls -l <document_root>/index.html
ls -l /etc/nginx/sites-available/<site_name>
ls -l /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
tail -n 100 /var/log/nginx/<site_name>_access.log
tail -n 100 /var/log/nginx/<site_name>_error.log

# Site-specific HTTPS instance, when ssl_enabled is true
ss -tlnp | grep ':443'
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
curl -k -I -H 'Host: <site_name>' http://127.0.0.1/
ls -l /etc/ssl/certs/<site_name>.crt
ls -l /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -text | \
  grep -E 'Subject:|Not Before|Not After'

# Secret file; do not print contents
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token

# Service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u sshd --no-pager -n 100
tail -n 100 /var/log/nginx/access.log
tail -n 100 /var/log/nginx/error.log
tail -n 100 /var/log/auth.log

# Network listeners
ss -tlnp | grep -E ':(22|80|443)\b'
lsof -iTCP:22 -sTCP:LISTEN
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN
```

Expected results include:

- `nginx -t` reports `syntax is ok` and `test is successful`.
- nginx listens on TCP `80`.
- nginx listens on TCP `443` when an SSL-enabled site exists.
- HTTP requests serve the configured document root.
- SSL-enabled sites redirect HTTP with `301` and serve HTTPS with HSTS.
- Generated certificates use a 2048-bit RSA key, 365-day validity, and the site name as the common name.
- `/etc/nginx/secrets/site_token` is `root:root` with mode `600`.
- SSH listens on TCP `22`.
- UFW is active with default inbound deny and explicit SSH, HTTP, and HTTPS allows.

Notification behavior to preserve:

- nginx configuration, security configuration, site virtual host, site link, default-site deletion, or generated certificate changes reload nginx.
- fail2ban configuration changes restart fail2ban.
- sysctl configuration changes run `sysctl -p /etc/sysctl.d/99-security.conf`.
- SSH hardening changes restart sshd.