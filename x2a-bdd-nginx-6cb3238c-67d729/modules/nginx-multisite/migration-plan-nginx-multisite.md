---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: `nginx-multisite` configures nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies kernel and SSH hardening; generates self-signed TLS certificates; deploys static index pages; and creates and enables nginx virtual-host configurations. The Ansible implementation must preserve the execution order: security hardening, nginx installation and base configuration, SSL setup, then virtual-host configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; logs `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; logs `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; logs `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`

- **fail2ban**: Host intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: N/A
  - Key Config: Enabled, started, and configured with `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails

- **ufw**: Host firewall
  - Location/Path: System firewall configuration
  - Port/Socket: Allows `22/tcp`, `80/tcp`, and `443/tcp`
  - Key Config: Enabled with default incoming policy `deny`

- **ssh**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: SSH, normally `22/tcp`
  - Key Config: Root login disabled; password authentication disabled

## File Structure

All paths below are relative to the cookbook root.

**Recipes:**
```text
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

**Providers:**
```text
```

No provider files are used by the execution tree.

**Templates:**
```text
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb
```

**Attributes:**
```text
attributes/default.rb
```

**Files:**
```text
```

No static file paths are listed in the supplied cookbook directory listing. The `nginx.rb` recipe references `cookbook_file` sources derived from `test/index.html`, `ci/index.html`, and `status/index.html`; those source files must be accounted for separately in the Ansible migration because their cookbook-relative paths were not provided in the analyzed file set.

## Module Explanation

The cookbook performs operations in this exact order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`, `nginx.rb`, `ssl.rb`, and `sites.rb` in that order.
   - The Ansible playbook must preserve this inclusion order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban defaults of `bantime = 3600`, `findtime = 600`, `maxretry = 3`, and `backend = auto`.
   - Enables the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Configures UFW with default deny and allows SSH, HTTP, and HTTPS.
   - Renders `templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies reverse-path filtering, redirect and source-route suppression, martian packet logging, ICMP and broadcast-ping suppression, IPv6 disabling, TCP SYN cookies, and TCP retry/backlog settings.
   - Reloads `/etc/sysctl.d/99-security.conf` with `sysctl -p` after changes.
   - Disables root SSH login and password authentication in `/etc/ssh/sshd_config`.
   - Restarts SSH after SSH configuration changes.
   - Resources: 1 package, 2 services, 2 templates, and 8 execute resources; total Chef resources: 13.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures `www-data`, automatic worker processes, PID `/run/nginx.pid`, 768 worker connections, standard HTTP optimizations, gzip, logging, and the `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*` includes.
   - Renders `templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, `login` and `api` rate-limit zones, restrictive client buffer and timeout settings, SSL session settings, TLS 1.2 and TLS 1.3, and the configured ECDHE/DHE cipher list.
   - Enables and starts nginx, supporting reload, restart, and status operations.
   - Creates document roots and deploys index files:
     - `test.cluster.local`: `/opt/server/test`, `/opt/server/test/index.html`, source `test/index.html`
     - `ci.cluster.local`: `/opt/server/ci`, `/opt/server/ci/index.html`, source `ci/index.html`
     - `status.cluster.local`: `/opt/server/status`, `/opt/server/status/index.html`, source `status/index.html`
   - All document roots use owner `www-data`, group `www-data`, and mode `0755`.
   - All index files use owner `www-data`, group `www-data`, and mode `0644`.
   - The site loop expands to exactly `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resources: 1 package, 2 templates, 1 service, 3 directories, and 3 cookbook files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` as `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert` with mode `0710`.
   - Generates self-signed 2048-bit RSA certificates for:
     - `test.cluster.local`: `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local`: `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`
   - Generates certificates only when both the certificate and private key are absent.
   - Uses `openssl req -x509 -nodes -days 365 -newkey rsa:2048`.
   - Uses subjects containing the corresponding site name as CN and `admin@example.com` as the email address.
   - Secures each key with mode `0640` and ownership `root:ssl-cert`.
   - The certificate loop expands to exactly `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `templates/default/site.conf.erb` and creates an enabled-site link for each site:
     - `test.cluster.local`: `/etc/nginx/sites-available/test.cluster.local` linked to `/etc/nginx/sites-enabled/test.cluster.local`, root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local`: `/etc/nginx/sites-available/ci.cluster.local` linked to `/etc/nginx/sites-enabled/ci.cluster.local`, root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: `/etc/nginx/sites-available/status.cluster.local` linked to `/etc/nginx/sites-enabled/status.cluster.local`, root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
   - Each site listens on HTTP port `80` and HTTPS port `443`.
   - Redirects HTTP to HTTPS and enables HTTP/2.
   - Configures TLS 1.2 and TLS 1.3, HSTS, security headers, gzip, `try_files $uri $uri/ =404`, and denial of `.htaccess`, `.git`, and `.svn` paths.
   - Configures site-specific access and error logs.
   - Removes `/etc/nginx/sites-enabled/default`.
   - The site loop expands to exactly `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Renders 3 virtual-host templates and creates 3 symbolic links.

## Dependencies

**External cookbook dependencies**: None specified.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**: `fail2ban`, `nginx`, `ssh`.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`.

**Network dependencies**:
- `22/tcp`: SSH
- `80/tcp`: HTTP and HTTP-to-HTTPS redirects
- `443/tcp`: HTTPS for all three sites

## Credentials

**Detection Summary**: No externally supplied credentials were detected. Three generated private TLS keys are created on the managed host and must be treated as sensitive files.

**Source**:
  - **Provider**: None detected for externally managed secrets
  - **URL**: None detected
  - **Path**: No data bag, vault, CyberArk, Conjur, or secret-manager path detected

### Generated private TLS key for test.cluster.local

- **Variable(s)**: `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated on the managed host by OpenSSL
- **Storage path**: `/etc/ssl/private/test.cluster.local.key`
- **Usage context**: nginx HTTPS private key
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`

### Generated private TLS key for ci.cluster.local

- **Variable(s)**: `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated on the managed host by OpenSSL
- **Storage path**: `/etc/ssl/private/ci.cluster.local.key`
- **Usage context**: nginx HTTPS private key
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`

### Generated private TLS key for status.cluster.local

- **Variable(s)**: `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated on the managed host by OpenSSL
- **Storage path**: `/etc/ssl/private/status.cluster.local.key`
- **Usage context**: nginx HTTPS private key
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`

The fixed certificate subject email `admin@example.com` is not an authentication credential. No data bags, encrypted data bags, Chef Vault items, Conjur variables, environment-variable secrets, database passwords, API tokens, or hardcoded authentication passwords were detected.

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
- `/etc/nginx/sites-enabled/default` must be absent
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`

**Service endpoints to check**:

- `test.cluster.local`: ports `80` and `443`
- `ci.cluster.local`: ports `80` and `443`
- `status.cluster.local`: ports `80` and `443`

**Unix sockets**: None configured.

**Network interfaces**: No specific bind address is configured; nginx listens on default interfaces.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

Total `site.conf.erb` renders: 3.

## Pre-flight checks

```bash
# Verify required packages and services
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active ssh

# Validate nginx and SSH configuration
nginx -t
sshd -t

# Verify firewall policy and allowed ports
ufw status verbose
ufw status numbered

# Verify nginx listeners
ss -tlnp | grep -E ':(80|443)\b'

# Verify fail2ban jails
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Verify kernel security settings
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv6.conf.default.disable_ipv6
sysctl net.ipv6.conf.lo.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries

# Verify SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# Verify certificate subjects and validity
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates

# Verify private-key security
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

### Instance-specific checks

#### test.cluster.local

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink /etc/nginx/sites-enabled/test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
```

Expected result: HTTP redirects to HTTPS, and HTTPS returns the static page from `/opt/server/test/index.html`.

#### ci.cluster.local

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink /etc/nginx/sites-enabled/ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
```

Expected result: HTTP redirects to HTTPS, and HTTPS returns the static page from `/opt/server/ci/index.html`.

#### status.cluster.local

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink /etc/nginx/sites-enabled/status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
```

Expected result: HTTP redirects to HTTPS, and HTTPS returns the static page from `/opt/server/status/index.html`.

### Expected security values

- UFW is active with default incoming policy `deny`.
- SSH, HTTP, and HTTPS are allowed.
- Root SSH login and password authentication are disabled.
- nginx and fail2ban are enabled and active.
- The three certificates are self-signed, contain their corresponding site names, and are valid for 365 days.
- Private keys are `root:ssl-cert` with mode `0640`.
- `/etc/ssl/certs` is `root:root` with mode `0755`.
- `/etc/ssl/private` is `root:ssl-cert` with mode `0710`.
- `/etc/nginx/sites-enabled/default` does not exist.
- All three sites listen on ports `80` and `443`, with HTTP redirected to HTTPS.