---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx for multiple virtual hosts with HTTP/HTTPS support, self-signed SSL certificates, static index files, nginx hardening, Fail2ban, UFW firewall rules, sysctl security settings, and SSH hardening. Security and base nginx configuration are applied before SSL preparation and virtual-host setup. Site definitions are loaded dynamically from the `nginx_sites` Chef data bag; the supplied analysis does not contain the item names, document roots, or SSL flags, so those values must be supplied explicitly to the Ansible migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Web server and virtual-host service
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP `80`, TCP `443`; PID file `/run/nginx.pid`
  - Key Config: `/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/security.conf`, `/etc/nginx/sites-available/*`, `/etc/nginx/sites-enabled/*`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Protects SSH, HTTP, and HTTPS
  - Key Config: SSH, nginx HTTP authentication, nginx request-limit, and nginx bot-search jails

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Default incoming policy deny; firewall enabled

- **sshd**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`

- **nginx sites**: Dynamically configured virtual hosts
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: TCP `80`; TCP `443` when `ssl_enabled` is true
  - Key Config: Site names, document roots, and SSL settings are loaded from the `nginx_sites` data bag. Exact site names were not supplied and cannot be enumerated without inventing configuration.

Expected site attributes are:

- `id`: Site/server name
- `document_root`: nginx document root
- `ssl_enabled`: Controls HTTPS configuration and self-signed certificate generation

Calculated site paths are:

- Configuration: `/etc/nginx/sites-available/<site_name>`
- Enabled link: `/etc/nginx/sites-enabled/<site_name>`
- Certificate: `/etc/ssl/certs/<site_name>.crt`
- Private key: `/etc/ssl/private/<site_name>.key`
- Access log: `/var/log/nginx/<site_name>_access.log`
- Error log: `/var/log/nginx/<site_name>_error.log`
- Static source directory: first component of `<site_name>`
- Static destination: `<document_root>/index.html`

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

No provider files or static files were listed in the supplied analysis. The `nginx.rb` recipe uses a dynamic `cookbook_file` source calculated as `<site_folder>/index.html`, but the corresponding site names and source paths were not supplied.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - The Ansible migration must preserve this execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban with bantime `3600`, findtime `600`, maxretry `3`, SSH protection on `ssh`, nginx HTTP authentication on `http,https`, nginx request-limit protection on `http,https`, and nginx bot-search protection on `http,https`.
   - Uses `/var/log/auth.log`, `/var/log/nginx/*error.log`, and `/var/log/nginx/*access.log` as log sources.
   - Sets the UFW default incoming policy to deny.
   - Allows TCP ports `22`, `80`, and `443`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-route disabling, martian logging, ICMP and broadcast-ping protections, IPv6 disabling on `all`, `default`, and `lo`, and TCP SYN flood protection.
   - Reloads the sysctl file with `sysctl -p /etc/sysctl.d/99-security.conf` when the template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` only when either SSH setting changes.
   - The Ansible implementation should use `community.general.ufw`, `ansible.posix.sysctl`, `ansible.builtin.lineinfile`, and service handlers.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures user `nginx`, automatic worker processes, PID `/run/nginx.pid`, `768` worker connections, access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, login and API rate limits, request-size limits, ten-second client/header/send timeouts, TLS 1.2 and TLS 1.3, the defined cipher suite, a `10m` shared SSL session cache, a `10m` SSL session timeout, and preferred server ciphers.
   - Enables and starts nginx.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads the `token` field from the Chef encrypted data bag item `nginx_secrets/site`.
   - Writes the token to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`.
   - Handles the token as sensitive data.
   - Reads the runtime `nginx_sites` collection.
   - Creates each runtime site's configured `document_root` recursively with owner `nginx`, group `nginx`, and mode `0755`.
   - Calculates the static source directory from the first component of the runtime site's `id`.
   - Deploys the corresponding `<site_folder>/index.html` to `<document_root>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - The supplied analysis does not contain site item names, so the dynamic directory and `cookbook_file` instances cannot be expanded into exact names or paths.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Reads the runtime `nginx_sites` collection.
   - Generates a self-signed 2048-bit RSA certificate for each runtime site whose `ssl_enabled` value is true.
   - Stores the certificate at `/etc/ssl/certs/<site_name>.crt`.
   - Stores the private key at `/etc/ssl/private/<site_name>.key`.
   - Generates certificates valid for `365` days with subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Sets the private-key mode to `0640` and ownership to `root:ssl-cert`.
   - Skips generation when both certificate and key already exist.
   - Reloads nginx after newly generated certificate or key files.
   - Exact SSL-enabled site names cannot be expanded because the `nginx_sites` data bag item list was not supplied.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Reads the runtime `nginx_sites` collection.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` to the template.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a link to `/etc/nginx/sites-available/<site_name>`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Reloads nginx after site configuration, link, or default-site changes.
   - SSL-enabled sites listen on port `80`, redirect HTTP to HTTPS with status `301`, listen on port `443` with HTTP/2, use the generated certificate and key, enable TLS 1.2 and TLS 1.3, and enable HSTS with `max-age=31536000` and `includeSubDomains`.
   - Non-SSL sites serve HTTP on port `80` without an HTTPS listener or certificate paths.
   - Both site types configure index files, security headers, gzip, `try_files $uri $uri/ =404`, `.htaccess` denial, `.git` and `.svn` denial, and site-specific access and error logs.
   - Exact site names and render/link counts are unavailable because the data bag items were not supplied.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**: `fail2ban`, `nginx`, `sshd` or the platform-equivalent SSH service.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`.

**Firewall dependencies**: TCP ports `22`, `80`, and `443`.

## Credentials

**Detection Summary**: 1 credential detected across 1 recipe and 1 generated file.

**Source**:
  - **Provider**: Chef
  - **API/mechanism**: `Chef::EncryptedDataBagItem.load`
  - **Data bag**: `nginx_secrets`
  - **Item**: `site`
  - **Field**: `token`
  - **URL**: None detected
  - **Path**: `cookbooks/nginx-multisite/recipes/nginx.rb`

### nginx Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Destination**: `/etc/nginx/secrets/site_token`
- **File permissions**: `0600`
- **File owner**: `root:root`
- **Usage context**: The token is written as an nginx-related site secret. The supplied recipe does not show another consumer of the file.
- **Migration storage**: Ansible Vault or an AAP credential/secret integration
- **Migration handling**: Deploy with `ansible.builtin.copy` or `ansible.builtin.template`, use `no_log: true`, and preserve owner `root`, group `root`, and mode `0600`.

The encrypted data bag access should be confirmed against the underlying recipe analysis. The supplied execution summary shows the resulting directory and file resources but does not independently evidence the data bag load. If the recipe does not contain this access, the credential claim must be qualified or removed.

No other data-bag credential, Chef Vault integration, CyberArk or Conjur integration, HashiCorp Vault integration, AWS Secrets Manager integration, external secret-manager URL, hardcoded password, API key, or database connection string was detected. SSL private keys are generated locally and are not retrieved from a credential store.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/etc/nginx/sites-available/<site_name>` for every supplied site item
- `/etc/nginx/sites-enabled/<site_name>` for every supplied site item
- `<document_root>/index.html` for every supplied site item
- `/etc/ssl/certs/<site_name>.crt` for every SSL-enabled site item
- `/etc/ssl/private/<site_name>.key` for every SSL-enabled site item
- `/var/log/nginx/<site_name>_access.log` for every supplied site item
- `/var/log/nginx/<site_name>_error.log` for every supplied site item

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`
- nginx PID mechanism: `/run/nginx.pid`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: once per runtime `nginx_sites` item; exact count unavailable because the data bag item list was not supplied

## Pre-flight checks

```bash
# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# nginx instance
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -f /run/nginx.pid

# fail2ban instance
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
test -f /etc/fail2ban/jail.local

# ufw instance
ufw status verbose
ufw status numbered
# Expected: enabled, default incoming deny, TCP 22/80/443 allowed

# sshd instance
systemctl status sshd || systemctl status ssh
grep -E '^PermitRootLogin[[:space:]]+no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication[[:space:]]+no$' /etc/ssh/sshd_config
test -f /etc/ssh/sshd_config

# Sysctl security
test -f /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# nginx secret
stat -c '%U:%G %a %n' /etc/nginx/secrets
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token
# Expected token: root:root 600

# SSL directories
stat -c '%U:%G %a %n' /etc/ssl/certs
stat -c '%U:%G %a %n' /etc/ssl/private
# Expected /etc/ssl/certs: root:root 755
# Expected /etc/ssl/private: root:ssl-cert 710

# Site directories and default-site removal
ls -ld /etc/nginx/sites-available
ls -ld /etc/nginx/sites-enabled
test ! -e /etc/nginx/sites-enabled/default

# Listening endpoints
ss -tlnp | grep -E ':(22|80|443)\b'
netstat -tulpn 2>/dev/null | grep -E ':(22|80|443)\b'

# Base HTTP and HTTPS responses
curl -I http://127.0.0.1/
curl -k -I https://127.0.0.1/

# nginx logs
ls -l /var/log/nginx/access.log
ls -l /var/log/nginx/error.log
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log

# Service logs
journalctl -u fail2ban --no-pager -n 50
journalctl -u nginx --no-pager -n 50

# Site-specific checks must be instantiated with the exact supplied site values.
# Site configuration:
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>

# Document root and static content:
test -d <document_root>
test -f <document_root>/index.html
stat -c '%U:%G %a %n' <document_root>/index.html

# Site logs:
test -f /var/log/nginx/<site_name>_access.log
test -f /var/log/nginx/<site_name>_error.log

# HTTP virtual-host response:
curl -I -H 'Host: <site_name>' http://127.0.0.1/

# SSL-enabled site checks:
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
```