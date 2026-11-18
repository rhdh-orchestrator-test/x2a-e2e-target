---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx for dynamically defined virtual hosts loaded from the `nginx_sites` Chef data bag. It installs nginx, Fail2ban, UFW, OpenSSL, and CA certificates; configures nginx security, rate limiting, TLS, logging, static site content, firewall rules, SSH hardening, and kernel security parameters; and stores an encrypted site token from the `nginx_secrets` data bag. The supplied plan does not contain the actual `nginx_sites` item names or values, so those names, document roots, SSL settings, and static-content sources must be exported and supplied before migration. The cookbook may restart `sshd` when SSH configuration changes, but does not enable or start the SSH service.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

No concrete site instance names are present in the supplied migration data. Site instances are dynamically loaded from the `nginx_sites` data bag using:

```ruby
data_bag('nginx_sites').each do |item_name|
```

The migration must export the data bag and define one Ansible site object for every actual item. Each object must contain:

- `id`
- `document_root`
- `ssl_enabled`

For every exported site item:

- `id` is the nginx server name, configuration filename, certificate filename, and log filename.
- `document_root` is the site document root.
- `ssl_enabled` controls certificate generation and HTTPS configuration.
- The static-content source directory is the first component of the site name, calculated with `site_name.split('.').first`.
- Static source is `<site-folder>/index.html`.
- Static destination is `<document_root>/index.html`.

Each resolved site requires:

- A document-root directory owned by `nginx:nginx`, mode `0755`.
- `<document_root>/index.html` owned by `nginx:nginx`, mode `0644`.
- `/etc/nginx/sites-available/<site_name>`.
- `/etc/nginx/sites-enabled/<site_name>` pointing to the available-site configuration.
- `/etc/ssl/certs/<site_name>.crt` and `/etc/ssl/private/<site_name>.key` when `ssl_enabled` is `true`.

### Security Services

- **nginx**: Enabled and started.
- **fail2ban**: Enabled and started.
- **sshd**: SSH configuration is modified, and `sshd` may be restarted when SSH settings change. The cookbook does not enable or start `sshd`.

### Security Configuration

- **Fail2ban**: Installed and configured through `/etc/fail2ban/jail.local`.
- **UFW**: Installed, configured with default-deny incoming policy, allowed on TCP ports `22`, `80`, and `443`, and enabled.
- **SSH**: Root login is disabled and password authentication is disabled.
- **Kernel security**: Reverse-path filtering, redirect/source-route rejection, ICMP protections, IPv6 disabling, and TCP SYN-flood protections are configured.

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

No provider file is used by the execution tree.

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

No static `files/default/*` or `files/*` files were listed. The `index.html` sources are referenced dynamically by `cookbook_file`, but their paths and contents are not included in the supplied execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Equivalent Ansible execution order is security configuration, nginx installation/configuration, OpenSSL and certificate generation, then site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local`, mode `0644`.
   - Configures Fail2ban defaults: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Enables the `sshd` jail on port `ssh` with `/var/log/auth.log`.
   - Enables `nginx-http-auth` on `http,https` with `/var/log/nginx/*error.log`.
   - Enables `nginx-limit-req` on `http,https` with maximum retries `10`.
   - Enables `nginx-botsearch` on `http,https` with `/var/log/nginx/*access.log` and maximum retries `2`.
   - Restarts Fail2ban after changes to `/etc/fail2ban/jail.local`.
   - Configures UFW with default incoming deny and allows TCP ports `22`, `80`, and `443`; UFW is enabled.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf`, mode `0644`.
   - Configures reverse-path filtering, redirect and source-route rejection, martian logging, ICMP protections, IPv6 disabling on `all`, `default`, and `lo`, and TCP SYN-flood protections:
     - `net.ipv4.tcp_syncookies = 1`
     - `net.ipv4.tcp_max_syn_backlog = 2048`
     - `net.ipv4.tcp_synack_retries = 2`
     - `net.ipv4.tcp_syn_retries = 5`
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` after sysctl template changes.
   - Sets `PermitRootLogin no` because `disable_root` is `true`.
   - Sets `PasswordAuthentication no` because `password_auth` is `false`.
   - May restart `sshd` after either SSH configuration change; the final `service[sshd]` resource has action `nothing` and is only a notification target.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf`, mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID `/run/nginx.pid`, `768` worker connections, sendfile, TCP optimizations, keepalive timeout `65`, standard access/error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Reloads nginx after changes to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf`, mode `0644`.
   - Configures `server_tokens off`, login rate limiting at `10r/m`, API rate limiting at `30r/m`, request/header buffer limits, `client_max_body_size 1k`, ten-second client body/header/send timeouts, TLS `1.2` and `1.3`, a shared `SSL` session cache of `10m`, a ten-minute TLS session timeout, the configured ECDHE/DHE ciphers, and preferred server ciphers.
   - Reloads nginx after changes to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts nginx.
   - Creates `/etc/nginx/secrets`, owned by `root:root`, mode `0700`.
   - Loads `site_secret['token']` from the encrypted data bag item `nginx_secrets/site` and writes it to `/etc/nginx/secrets/site_token`, owned by `root:root`, mode `0600`, marked sensitive.
   - Reads the dynamically supplied `nginx_sites` collection.
   - For each exported site object, creates its `document_root`, deploys `<site-folder>/index.html` to `<document_root>/index.html`, and applies ownership `nginx:nginx` and mode `0644` to the file.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`, owned by `root:root`, mode `0755`.
   - Creates `/etc/ssl/private`, owned by `root:ssl-cert`, mode `0710`.
   - Processes the exported `nginx_sites` collection and generates certificates only for objects with `ssl_enabled: true`.
   - Uses `/etc/ssl/certs/<site_name>.crt` and `/etc/ssl/private/<site_name>.key`.
   - Executes `generate-ssl-cert-<site_name>` using `openssl req`.
   - Generates a self-signed RSA `2048` certificate valid for `365` days with subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Sets the private key to mode `640`, owned by `root:ssl-cert`.
   - Skips generation when both certificate and key already exist.
   - Reloads nginx after certificate generation.
   - These are development self-signed certificates and should only be preserved in Ansible when explicitly required.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled`, both owned by `root:root`, mode `0755`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Processes the exported `nginx_sites` collection.
   - For each exported site object, renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once to `/etc/nginx/sites-available/<site_name>`, mode `0644`.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to `/etc/nginx/sites-available/<site_name>`.
   - Reloads nginx after site configuration, symlink, or default-site changes.
   - Configures HTTP port `80`, HTTPS port `443` when SSL is enabled, HTTP-to-HTTPS redirection, HTTP/2, site roots, index files, TLS settings, HSTS, security headers, gzip, `try_files`, `.htaccess` denial, `.git` and `.svn` denial, and per-site access and error logs.
   - Uses `/var/log/nginx/<site_name>_access.log` and `/var/log/nginx/<site_name>_error.log`.

Because the supplied input contains no actual data bag item names, no site-specific `.each` iterations can be expanded into literal site names without inventing configuration.

## Dependencies

**External cookbook dependencies**: None listed.

**Chef platform support**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `nginx`: enabled and started by the cookbook.
- `fail2ban`: enabled and started by the cookbook.
- `sshd`: configuration is modified and the service may be restarted on changes; enablement and startup are not managed.

**Required external data**:

- Encrypted data bag `nginx_secrets`, item `site`, field `token`.
- Standard data bag `nginx_sites`, with fields `id`, `document_root`, and `ssl_enabled`.
- Dynamic static `index.html` source files referenced by `cookbook_file`.

## Credentials

**Detection Summary**: 2 sensitive credential categories detected across the nginx and SSL recipes: the encrypted nginx site token and generated private keys. Generated TLS certificates are public artifacts, not sensitive credentials.

**Source**:

  - **Provider**: `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')` for the site token; `openssl req` executed by `cookbooks/nginx-multisite/recipes/ssl.rb` for generated certificates and private keys.
  - **URL**: None detected.
  - **Path**: `/etc/nginx/secrets/site_token`, `/etc/ssl/certs/<site_name>.crt`, and `/etc/ssl/private/<site_name>.key`.

### nginx Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag `nginx_secrets`, item `site`
- **Usage context**: Written for nginx/site use at `/etc/nginx/secrets/site_token`
- **File protection**: `root:root`, mode `0600`; Chef marks the resource sensitive
- **Migration storage**: Ansible Vault or an approved external secret provider; do not store plaintext in ordinary inventory or group variables

### Per-site Private Keys

- **Variable(s)**: `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by `openssl req`
- **Source provider**: `openssl req` executed by `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Destination**: `/etc/ssl/private/<site_name>.key`
- **Usage context**: Private key for the self-signed nginx TLS certificate
- **Generation**: RSA `2048`, valid for `365` days, generated only when the certificate or key is absent
- **File protection**: Mode `640`, owner `root`, group `ssl-cert`; parent directory mode `0710`

### TLS Certificates

- **Variable(s)**: `cert_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally; not retrieved from a vault
- **Source provider**: `openssl req` executed by `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Destination**: `/etc/ssl/certs/<site_name>.crt`
- **Usage context**: Public certificate for the nginx HTTPS virtual host
- **Certificate type**: Self-signed development certificate
- **Validity**: `365` days
- **Subject**: Uses the site name as the common name

No HashiCorp Vault, CyberArk, AWS Secrets Manager, Conjur, `data_bag_item` credential lookup, environment-variable secret, hardcoded password, API key, or database credential was detected.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/ssl/certs
/etc/ssl/private
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
<document_root>
<document_root>/index.html
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
/var/log/auth.log
```

The `<site_name>` and `<document_root>` placeholders must be replaced with every actual exported `nginx_sites` item before execution.

**Service endpoints to check**:

- SSH: TCP port `22`
- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: `1` render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: `1` render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: `1` render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: `1` render
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: one render for each resolved `nginx_sites` item

The numeric site-template count cannot be determined because the supplied input contains no `nginx_sites` item names.

## Pre-flight checks

Before running site-specific commands, export the actual `nginx_sites` item names and replace `<site_name>` and `<document_root>` with those exact values. No concrete site names were supplied, so individually named site commands cannot be generated without inventing data.

```bash
# Package status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Managed service status
systemctl status nginx
systemctl status fail2ban

# The cookbook does not enable or start sshd, but it may restart it after changes
systemctl status sshd

# nginx configuration validation
nginx -t
nginx -T | grep -E 'listen (80|443)|server_name|ssl_certificate|ssl_certificate_key'

# Global nginx configuration
grep -E 'worker_processes|worker_connections|access_log|error_log|gzip|sites-enabled' \
  /etc/nginx/nginx.conf

# nginx security configuration
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Site configuration and enablement
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -E 'listen 80|listen 443|server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/<site_name>

# SSL-enabled site checks
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -issuer -dates
stat -c '%A %U:%G %n' /etc/ssl/private/<site_name>.key

# Non-SSL site check
grep -q 'listen 80' /etc/nginx/sites-available/<site_name>

# Static content
test -d <document_root>
test -f <document_root>/index.html
stat -c '%A %U:%G %n' <document_root>/index.html

# Site endpoints
curl -I -H 'Host: <site_name>' http://127.0.0.1/

# Use this for SSL-enabled sites
curl -k -I --resolve <site_name>:443:127.0.0.1 \
  https://<site_name>/

# Secret permissions; do not print the token
test -f /etc/nginx/secrets/site_token
stat -c '%A %U:%G %n' /etc/nginx/secrets/site_token

# Firewall
ufw status verbose
ufw status numbered

# SSH hardening and syntax
grep -E '^[# ]*PermitRootLogin|^[# ]*PasswordAuthentication' \
  /etc/ssh/sshd_config
sshd -t

# Fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Kernel security
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# Listening ports and logs
ss -tlnp | grep -E ':(22|80|443)\b'
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
journalctl -u sshd --no-pager -n 50
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
```

Expected results:

- `nginx` and `fail2ban` are active.
- SSH configuration contains `PermitRootLogin no` and `PasswordAuthentication no`.
- UFW is active with default incoming deny and TCP ports `22`, `80`, and `443` allowed.
- SSL-enabled sites redirect HTTP to HTTPS and return HTTP `200` over HTTPS when `index.html` exists.
- Non-SSL sites serve HTTP without requiring certificate files.
- Site content is owned by `nginx:nginx` with mode `0644`.
- The site token is owned by `root:root` with mode `0600`.
- Every exported site has its available configuration, enabled symlink, document root, and static content.
- Every exported SSL-enabled site has a valid certificate and private key.
