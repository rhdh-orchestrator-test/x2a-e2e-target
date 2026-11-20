---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server for data-bag-defined virtual hosts, optional self-signed TLS certificates, static site content, security headers, rate limits, fail2ban, UFW firewall rules, SSH hardening, and kernel security parameters. Recipes execute in the order `security` → `nginx` → `ssl` → `sites`. The supplied analysis does not contain the names or attributes of the `nginx_sites` data-bag items, so the Ansible migration must receive the site collection explicitly before site-specific tasks can be expanded.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Primary web server and virtual-host service
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP/80 and TCP/443; PID file `/run/nginx.pid`
  - Key Config: `/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/security.conf`, `/etc/nginx/sites-available`, and `/etc/nginx/sites-enabled`

- **fail2ban**: Intrusion-prevention service for SSH and nginx-related jails
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH on `ssh` and nginx traffic on `http,https`
  - Key Config: `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP/22, TCP/80, and TCP/443
  - Key Config: Default-deny policy; UFW enabled

- **sshd**: SSH service managed for host hardening
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP/22
  - Key Config: `PermitRootLogin no` and `PasswordAuthentication no`

- **nginx_sites runtime collection**: Virtual-host instances loaded from the Chef `nginx_sites` data bag
  - Location/Path: Site-specific paths are derived at runtime
  - Port/Socket: TCP/80; TCP/443 for SSL-enabled sites
  - Key Config: Each item supplies `id`, `document_root`, and `ssl_enabled`

No exact `nginx_sites` item names are present in the supplied analysis. The Ansible migration must define them explicitly, for example:

```yaml
nginx_sites:
  - name: example.com
    document_root: /var/www/example.com
    ssl_enabled: true
```

For a supplied site named `<site_name>`, the cookbook derives:

- Site configuration: `/etc/nginx/sites-available/<site_name>`
- Enabled-site link: `/etc/nginx/sites-enabled/<site_name>`
- Certificate: `/etc/ssl/certs/<site_name>.crt`
- Private key: `/etc/ssl/private/<site_name>.key`
- Access log: `/var/log/nginx/<site_name>_access.log`
- Error log: `/var/log/nginx/<site_name>_error.log`
- Static content: `<document_root>/index.html`
- Static source directory: first hostname component from `site_name.split('.').first`

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
├── resources/
│   └── lineinfile.rb
└── templates/
    └── default/
        ├── fail2ban.jail.local.erb
        ├── nginx.conf.erb
        ├── security.conf.erb
        ├── site.conf.erb
        └── sysctl-security.conf.erb
```

### Recipes

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

### Providers

```text
```

No provider file is used by the execution tree. `resources/lineinfile.rb` is not invoked by any listed recipe and is excluded from the migration file list.

### Templates

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

### Attributes

```text
cookbooks/nginx-multisite/attributes/default.rb
```

### Dynamic static files

The recipe references dynamic static-file sources:

```text
<site_folder>/index.html
```

These source files are not present in the supplied file listing and must be supplied separately to the Ansible role when static site content is required.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order: security, nginx, SSL, then virtual-host sites.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures global fail2ban values:
     - `bantime = 3600`
     - `findtime = 600`
     - `maxretry = 3`
     - Backend `auto`
   - Enables the `sshd` jail on port `ssh`, using `/var/log/auth.log`, bantime `3600`, and max retry `3`.
   - Enables the `nginx-http-auth` jail on ports `http,https`, using `/var/log/nginx/*error.log`, bantime `3600`, and max retry `3`.
   - Enables the `nginx-limit-req` jail on ports `http,https`, using `/var/log/nginx/*error.log`, bantime `3600`, and max retry `10`.
   - Enables the `nginx-botsearch` jail on ports `http,https`, using `/var/log/nginx/*access.log`, bantime `3600`, and max retry `2`.
   - Restarts `fail2ban` after a changed jail configuration.
   - Applies the UFW default-deny policy.
   - Allows SSH, HTTP, and HTTPS through UFW:
     - `ufw allow ssh`
     - `ufw allow http`
     - `ufw allow https`
   - Enables UFW with `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect protection, source-route disabling, martian packet logging, ICMP protection, IPv6 disabling, and TCP SYN flood protection.
   - Reloads the sysctl configuration with `sysctl -p /etc/sysctl.d/99-security.conf` after template changes.
   - Disables root SSH login by setting `PermitRootLogin no`.
   - Disables SSH password authentication by setting `PasswordAuthentication no`.
   - Restarts `sshd` after either SSH hardening setting changes.
   - Resources used: 1 package declaration, 2 services, 2 templates, and 8 execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID file `/run/nginx.pid`, 768 worker connections, sendfile, TCP optimizations, keepalive timeout `65`, MIME types, global access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, `login` and `api` rate-limit zones, request buffer limits, client timeouts, TLS 1.2 and TLS 1.3, the explicit cipher list, SSL session cache, SSL session timeout, and preferred server ciphers.
   - Enables and starts the `nginx` service with restart, reload, and status support.
   - Creates `/etc/nginx/secrets` owned by `root:root` with mode `0700`.
   - Loads `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`.
   - Writes `site_secret['token']` to `/etc/nginx/secrets/site_token`, owned by `root:root` with mode `0600`, and marks the file resource sensitive.
   - Reads the runtime `nginx_sites` collection.
   - For each explicitly supplied site item, creates its `document_root` recursively, owned by `nginx:nginx` with mode `0755`.
   - For each explicitly supplied site item, deploys the dynamic source `<site_folder>/index.html` to `<document_root>/index.html`, owned by `nginx:nginx` with mode `0644`.
   - The supplied analysis contains no exact site item names, so no site-loop iterations can be expanded until the Ansible site variables are provided.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Reads the runtime `nginx_sites` collection.
   - For each explicitly supplied site with `ssl_enabled: true`, generates a self-signed RSA 2048 certificate valid for 365 days.
   - Writes certificates to `/etc/ssl/certs/<site_name>.crt`.
   - Writes private keys to `/etc/ssl/private/<site_name>.key`.
   - Uses the subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Skips certificate generation when both the certificate and key already exist.
   - Names dynamic commands `generate-ssl-cert-<site_name>`.
   - Reloads nginx after newly generated certificates or keys.
   - The supplied analysis contains no exact SSL-enabled site names, so no SSL loop iterations can be expanded until the Ansible site variables are provided.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` owned by `root:root` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` owned by `root:root` with mode `0755`.
   - Reads the runtime `nginx_sites` collection.
   - For each explicitly supplied site item, renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Supplies the template values `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file`.
   - SSL-enabled sites listen on HTTP/80, redirect HTTP to HTTPS, listen on HTTPS/443 with HTTP/2, use the generated certificate and key, and enable HSTS with `max-age=31536000; includeSubDomains`.
   - Non-SSL sites listen on HTTP/80 without SSL redirect behavior.
   - Both site branches configure index files, security headers, gzip, `try_files $uri $uri/ =404`, `.htaccess` denial, `.git` and `.svn` denial, and site-specific access and error logs.
   - For each explicitly supplied site item, creates `/etc/nginx/sites-enabled/<site_name>` as a link to `/etc/nginx/sites-available/<site_name>`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Reloads nginx after site template, link, or default-site changes.
   - The supplied analysis contains no exact site item names, so no site-template or link iterations can be expanded until the Ansible site variables are provided.

### Defined attributes

Source: `cookbooks/nginx-multisite/attributes/default.rb`

- `node['nginx']['ssl']['certificate_path']`: `/etc/ssl/certs`
- `node['nginx']['ssl']['private_key_path']`: `/etc/ssl/private`
- `node['security']['fail2ban']['enabled']`: `true`
- `node['security']['ufw']['enabled']`: `true`
- `node['security']['ssh']['disable_root']`: `true`
- `node['security']['ssh']['password_auth']`: `false`

The security namespaces are `fail2ban`, `ufw`, and `ssh`. They are not recipe iteration items.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**: `fail2ban`, `ufw`, `nginx`, `openssl`, `ca-certificates`.

**Service dependencies**: `fail2ban`, `nginx`, `sshd`.

**Data dependencies**:

- Chef encrypted data bag item `nginx_secrets/site`
- Standard Chef data bag collection `nginx_sites`

## Credentials

**Detection Summary**: 1 credential detected across 1 recipe and 1 destination file.

**Source**:

- **Provider**: `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`
- **Provider type**: Chef encrypted data bag
- **URL**: Not applicable
- **Path**: `cookbooks/nginx-multisite/recipes/nginx.rb`

### Site token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag `nginx_secrets`, item `site`
- **Destination**: `/etc/nginx/secrets/site_token`
- **File permissions**: `0600`
- **File owner**: `root`
- **File group**: `root`
- **Usage context**: Written to `/etc/nginx/secrets/site_token` for downstream use. The analyzed files do not identify a subsequent consumer.
- **Sensitive handling**: The Chef file resource is marked `sensitive true`.
- **Migration storage**: Use Ansible Vault, an AAP credential, or an approved external secret manager. Do not store the token in plaintext variables or display it in task output.

### TLS private keys

- **Variable(s)**: Runtime site name
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL
- **Path**: `/etc/ssl/private/<site_name>.key`
- **Usage context**: nginx HTTPS private keys
- **Permissions**: `0640`
- **Owner**: `root`
- **Group**: `ssl-cert`
- **Provider**: None; locally generated

### TLS certificates

- **Variable(s)**: Runtime site name
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL
- **Path**: `/etc/ssl/certs/<site_name>.crt`
- **Usage context**: nginx HTTPS server certificates
- **Validity**: 365 days
- **Provider**: None; locally generated self-signed certificates

No HashiCorp Vault, CyberArk, AWS Secrets Manager, Conjur, `data_bag_item` password, `chef_vault_item`, or environment-variable secret reference was detected.

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
/etc/ssl/certs
/etc/ssl/private
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
<document_root>/index.html
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
/var/log/auth.log
```

The default enabled site must be absent. Site-specific paths must be generated from the explicitly supplied Ansible `nginx_sites` collection.

**Service endpoints to check**:

- TCP/80: HTTP
- TCP/443: HTTPS when an SSL-enabled site is configured
- TCP/22: SSH
- `/run/nginx.pid`: nginx PID file

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: one render per supplied `nginx_sites` item

The exact number of site-template renders, SSL certificate commands, document roots, static files, and enabled links cannot be determined until the site collection is supplied.

## Pre-flight checks

```bash
# Service status: nginx
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx

# Service status: fail2ban
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Service status: sshd
systemctl status sshd
systemctl is-active sshd

# Package verification
dpkg-query -W nginx fail2ban ufw openssl ca-certificates
# On RPM-based systems:
rpm -q nginx fail2ban ufw openssl ca-certificates

# nginx configuration validation
nginx -t
nginx -T
grep -E 'worker_processes|worker_connections|access_log|error_log|conf.d|sites-enabled' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|client_body_timeout|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# UFW verification
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# fail2ban verification
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime|findtime|maxretry|backend|logpath|enabled|port' \
  /etc/fail2ban/jail.local

# Kernel security verification
sysctl -p /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# SSH hardening verification
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config
sshd -t

# Secret metadata verification; do not print the token
stat -c '%U %G %a %n' /etc/nginx/secrets/site_token

# nginx listener verification
ss -tlnp | grep -E ':80|:443'
ss -tlnp | grep ':22'

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Global log verification
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log

# fail2ban log verification
journalctl -u fail2ban --since "15 minutes ago"
fail2ban-client status
```

The supplied migration input contains no exact site names, so individual site pre-flight commands cannot be instantiated. After `nginx_sites` is supplied, generate the following checks separately for every named site:

```bash
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -E 'listen|server_name|root|ssl_certificate|ssl_certificate_key|access_log|error_log' \
  /etc/nginx/sites-available/<site_name>

test -d <document_root>
test -f <document_root>/index.html
stat -c '%U %G %a %n' <document_root>/index.html

tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

For every supplied site with `ssl_enabled: true`, also run:

```bash
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
stat -c '%U %G %a %n' /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -issuer -dates
grep -E 'ssl_certificate|ssl_certificate_key|listen 443|return 301' \
  /etc/nginx/sites-available/<site_name>

curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
curl -k -s -D - --resolve <site_name>:443:127.0.0.1 https://<site_name>/ -o /dev/null \
  | grep -E 'X-Frame-Options|X-Content-Type-Options|X-XSS-Protection|Referrer-Policy|Content-Security-Policy|Strict-Transport-Security'
```

For every supplied site, run:

```bash
curl -I -H 'Host: <site_name>' http://127.0.0.1/
```

Expected behavior:

- SSL-enabled sites redirect HTTP to HTTPS with status `301`.
- Non-SSL sites serve the configured HTTP response.
- SSL-enabled sites respond on HTTPS and include the HSTS header.
- Static index files are owned by `nginx:nginx` with mode `0644`.
- SSL private keys are owned by `root:ssl-cert` with mode `0640`.
