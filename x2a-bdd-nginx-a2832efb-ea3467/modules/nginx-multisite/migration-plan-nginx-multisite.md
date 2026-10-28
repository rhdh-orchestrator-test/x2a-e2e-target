---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a multi-site HTTPS web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and configures nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies kernel and SSH hardening; generates self-signed certificates; creates site document roots and static index files; renders three HTTPS virtual hosts with HTTP-to-HTTPS redirects; and exposes HTTP on port 80, HTTPS on port 443, and SSH on port 22.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH and nginx logs
  - Key Config: Enabled and started; default ban time `3600`; find time `600`; maximum retries `3`; backend `auto`

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Default incoming policy deny; firewall enabled

- **ssh**: Hardened SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`; restarted only when hardening changes

## File Structure

The following paths are relative to the cookbook root, `cookbooks/nginx-multisite`.

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── files/
│   └── [no static files listed]
├── providers/
│   └── [none]
├── recipes/
│   ├── default.rb
│   ├── security.rb
│   ├── nginx.rb
│   ├── ssl.rb
│   └── sites.rb
└── templates/
    └── default/
        ├── fail2ban.jail.local.erb
        ├── nginx.conf.erb
        ├── security.conf.erb
        ├── site.conf.erb
        └── sysctl-security.conf.erb
```

The recipes reference dynamic sources `test/index.html`, `ci/index.html`, and `status/index.html`. These files are not present in the supplied directory listing and must be added to the Ansible role's `files/` directory or replaced with explicitly managed content.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - The Ansible role entry point must include security, nginx installation, SSL generation, and site configuration tasks in this same order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban jails:
     - `sshd`: port `ssh`, log `/var/log/auth.log`, ban time `3600`, maximum retries `3`.
     - `nginx-http-auth`: ports `http,https`, filter `nginx-http-auth`, log `/var/log/nginx/*error.log`, ban time `3600`, maximum retries `3`.
     - `nginx-limit-req`: ports `http,https`, filter `nginx-limit-req`, log `/var/log/nginx/*error.log`, ban time `3600`, maximum retries `10`.
     - `nginx-botsearch`: ports `http,https`, filter `nginx-botsearch`, log `/var/log/nginx/*access.log`, ban time `3600`, maximum retries `2`.
   - Applies UFW rules in order:
     - Default incoming policy deny.
     - Allow SSH on `22/tcp`.
     - Allow HTTP on `80/tcp`.
     - Allow HTTPS on `443/tcp`.
     - Enable UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Reloads `/etc/sysctl.d/99-security.conf` with `sysctl -p` when the file changes.
   - Applies kernel security settings including reverse-path filtering, redirect and source-route suppression, martian logging, ICMP protections, IPv6 disabling, TCP SYN cookies, backlog `2048`, SYN-ACK retries `2`, and SYN retries `5`.
   - Changes SSH configuration to `PermitRootLogin no`.
   - Changes SSH configuration to `PasswordAuthentication no`.
   - Restarts SSH only when either SSH setting changes.
   - Resources in execution order:
     1. Package declaration for `fail2ban` and `ufw`.
     2. `fail2ban` service.
     3. `/etc/fail2ban/jail.local` template.
     4. UFW default-deny command.
     5. UFW SSH rule.
     6. UFW HTTP rule.
     7. UFW HTTPS rule.
     8. UFW enable command.
     9. `/etc/sysctl.d/99-security.conf` template.
     10. Sysctl reload command, initially disabled.
     11. Conditional root-login hardening command.
     12. Conditional password-authentication hardening command.
     13. SSH service, initially disabled.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Reloads nginx after either base configuration changes.
   - Configures worker user `www-data`, automatic worker processes, PID `/run/nginx.pid`, worker connections `768`, keepalive timeout `65`, gzip, standard access and error logs, and includes `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Applies nginx hardening including `server_tokens off`, login rate limit `10r/m`, API rate limit `30r/m`, small client buffers, maximum body size `1k`, request timeouts `10`, TLS `1.2` and `1.3`, SSL session cache `shared:SSL:10m`, SSL session timeout `10m`, the specified ECDHE/DHE cipher list, and server cipher preference.
   - Enables and starts the nginx service.
   - Creates `/opt/server/test` for `test.cluster.local`, owned by `www-data:www-data`, mode `0755`, recursively.
   - Deploys `test/index.html` to `/opt/server/test/index.html`, owned by `www-data:www-data`, mode `0644`.
   - Creates `/opt/server/ci` for `ci.cluster.local`, owned by `www-data:www-data`, mode `0755`, recursively.
   - Deploys `ci/index.html` to `/opt/server/ci/index.html`, owned by `www-data:www-data`, mode `0644`.
   - Creates `/opt/server/status` for `status.cluster.local`, owned by `www-data:www-data`, mode `0755`, recursively.
   - Deploys `status/index.html` to `/opt/server/status/index.html`, owned by `www-data:www-data`, mode `0644`.
   - Site document-root iteration is fully expanded into the three named sites above.
   - Resource counts: one package declaration, two templates, one service, three directories, and three cookbook files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root`, mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert`, mode `0710`.
   - Generates a self-signed certificate and RSA 2048-bit unencrypted private key for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
   - Generates a self-signed certificate and RSA 2048-bit unencrypted private key for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
   - Generates a self-signed certificate and RSA 2048-bit unencrypted private key for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
   - Each certificate action runs only when its certificate and key do not already exist.
   - Certificates are valid for `365` days and use the exact site name as the Common Name.
   - Certificate subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Sets each key to mode `0640`, owner `root`, and group `ssl-cert`.
   - Schedules a delayed nginx reload after each generated certificate.
   - Resource counts: one package declaration for two packages, one group, two directories, and three certificate-generation commands.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
   - Links `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
   - Links `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
   - Links `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Site template variables are `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file`.
   - Each site has an HTTP listener on port `80`, redirects HTTP to HTTPS, and has an HTTP/2 HTTPS listener on port `443`.
   - Each site uses its own document root, certificate, key, access log, and error log.
   - Configures `index.html`, `index.htm`, and `index.php`; TLS `1.2` and `1.3`; one-year HSTS with subdomains; security headers; gzip; `try_files $uri $uri/ =404`; and denial of `.htaccess`, `.git`, and `.svn` paths.
   - Resource counts: three templates, three links, and one file deletion.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**: `fail2ban` enabled and started; `nginx` enabled and started; `ssh` restarted only when hardening changes; UFW enabled after rules are applied.

**Operating system considerations**: Metadata supports Ubuntu `>= 18.04` and CentOS `>= 7.0`, but the implementation uses Ubuntu-oriented paths, commands, service names, `/var/log/auth.log`, `ufw`, `www-data`, and `ssh`. Validate these assumptions before targeting CentOS.

## Credentials

**Detection Summary**: No externally supplied application credentials, passwords, API keys, data bags, Chef Vault items, or secret-manager integrations were detected. Three locally generated TLS private keys and one hardcoded certificate-subject email address are present.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed TLS private keys

- **Variable(s)**: `/etc/ssl/private/test.cluster.local.key`, `/etc/ssl/private/ci.cluster.local.key`, `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts
- **Permissions**: Mode `0640`, owned by `root:ssl-cert`

### Certificate subject email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command
- **Usage context**: Email address in each self-signed certificate subject

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, `node['vault']`, or `node['secrets']` usage was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` must not exist
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: TCP `22`

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `sysctl-security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders, one each for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`

## Pre-flight checks:

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh
ufw status verbose

# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates

# Nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Verify all site roots and index files
ls -ld /opt/server/test /opt/server/ci /opt/server/status
ls -l /opt/server/test/index.html /opt/server/ci/index.html /opt/server/status/index.html

# Verify all enabled site links and absence of the default site
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Verify test.cluster.local certificate, key, redirect, and HTTPS content
ls -l /etc/ssl/certs/test.cluster.local.crt /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# Verify ci.cluster.local certificate, key, redirect, and HTTPS content
ls -l /etc/ssl/certs/ci.cluster.local.crt /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# Verify status.cluster.local certificate, key, redirect, and HTTPS content
ls -l /etc/ssl/certs/status.cluster.local.crt /etc/ssl/private/status.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Expected key ownership and mode for all sites
# root:ssl-cert 640
stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Certificate properties
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates

# Security headers for test.cluster.local
curl -k -s -D - --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ -o /dev/null

# Security headers for ci.cluster.local
curl -k -s -D - --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ -o /dev/null

# Security headers for status.cluster.local
curl -k -s -D - --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ -o /dev/null

# Verify listeners
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
ss -tlnp | grep ':22 '

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t

# UFW
ufw status verbose
ufw status numbered

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E '^(bantime|findtime|maxretry|backend)' /etc/fail2ban/jail.local
grep -E '^\[(sshd|nginx-http-auth|nginx-limit-req|nginx-botsearch)\]' /etc/fail2ban/jail.local

# Sysctl
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# Logs for all three sites and services
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

Expected results:

- nginx and fail2ban are enabled and active.
- SSH is active with root login and password authentication disabled.
- UFW is active with default incoming deny and TCP ports `22`, `80`, and `443` allowed.
- nginx configuration validation succeeds.
- Each named site has its own document root, certificate, key, enabled-site link, access log, and error log.
- HTTP requests redirect with status `301` to the corresponding HTTPS hostname.
- HTTPS requests return status `200` and the expected site content.
- Each certificate is self-signed, has the corresponding Common Name, is valid for approximately `365` days, and uses an RSA 2048-bit key.
- Each private key is owned by `root:ssl-cert` with mode `0640`.
- Required security headers are present for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
- nginx listens on TCP ports `80` and `443`, and SSH listens on TCP port `22`.
- The `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` fail2ban jails are enabled.
- Required sysctl values are active, including reverse-path filtering, TCP SYN cookies, backlog `2048`, and IPv6 disabled on `all`.
- Separate access and error logs are produced for all three sites.