---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a multi-site HTTPS web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and configures nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and self-signed certificates; deploys global and virtual-host nginx configuration; redirects HTTP to HTTPS; applies kernel and SSH hardening; and removes the default nginx site. The migration must preserve all three hostnames, paths, ports, security settings, certificate permissions, and site-specific content.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS nginx virtual host serving the test site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; logs `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS nginx virtual host serving the CI site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; logs `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS nginx virtual host serving the status site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; logs `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`

Security configuration includes:

- fail2ban enabled, installed, enabled, and started
- UFW enabled with default-deny behavior and allowances for SSH, HTTP, and HTTPS
- Root SSH login disabled
- SSH password authentication disabled

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

Static cookbook-file sources referenced by the recipes:

```text
test/index.html
ci/index.html
status/index.html
```

These static source files are not present in the supplied directory listing and must be obtained or separately provided during migration.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - Ansible execution order must remain security hardening, nginx installation and global configuration, SSL setup and certificate generation, then site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures bantime `3600`, findtime `600`, maxretry `3`, backend `auto`, and the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Restarts fail2ban after a changed jail configuration.
   - Configures UFW with default policy `deny`, allows SSH, HTTP, and HTTPS, and enables the firewall.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, disabled redirects and source routing, martian logging, ICMP protections, disabled IPv6, SYN cookies, and TCP backlog/retry settings.
   - Reloads `/etc/sysctl.d/99-security.conf` after a change.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts the SSH service only when either SSH setting changes.
   - Contains 8 execute resources: `ufw_default_deny`, `ufw_allow_ssh`, `ufw_allow_http`, `ufw_allow_https`, `ufw_enable`, `reload_sysctl`, `disable root login`, and `disable password auth`.
   - Ansible should use `community.general.ufw`, `ansible.posix.sysctl`, `ansible.builtin.lineinfile`, and handlers where available.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID `/run/nginx.pid`, 768 worker connections, standard access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, rate limits `login` at `10r/m` and `api` at `30r/m`, request and header limits, ten-second timeouts, TLS session settings, TLS 1.2 and TLS 1.3, and the explicit cipher configuration.
   - Enables and starts nginx and supports reload and restart operations.
   - Creates `/opt/server/test`, owned by `nginx:nginx` with mode `0755`, and deploys `test/index.html` to `/opt/server/test/index.html` owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/ci`, owned by `nginx:nginx` with mode `0755`, and deploys `ci/index.html` to `/opt/server/ci/index.html` owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/status`, owned by `nginx:nginx` with mode `0755`, and deploys `status/index.html` to `/opt/server/status/index.html` owned by `nginx:nginx` with mode `0644`.
   - Site-content iterations: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed 2048-bit RSA certificate valid for 365 days without a passphrase for `test.cluster.local`.
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Common name: `test.cluster.local`
   - Generates a self-signed 2048-bit RSA certificate valid for 365 days without a passphrase for `ci.cluster.local`.
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Common name: `ci.cluster.local`
   - Generates a self-signed 2048-bit RSA certificate valid for 365 days without a passphrase for `status.cluster.local`.
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Common name: `status.cluster.local`
   - Uses subject values country `US`, state `Example`, locality `Example`, organization `Example Org`, organizational unit `IT`, and email `admin@example.com`.
   - Sets every private key to mode `0640` and ownership `root:ssl-cert`.
   - Skips certificate generation when the corresponding certificate and key already exist.
   - Reloads nginx after certificate generation.
   - Certificate iterations: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`.
   - Ansible may use `community.crypto.openssl_privatekey`, `community.crypto.openssl_csr`, and `community.crypto.x509_certificate`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled`, owned by `root:root` with mode `0755`.
   - Processes the three configured sites in the site-directory/configuration loop: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
   - Creates symlink `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Creates symlink `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Creates symlink `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Configures HTTP port `80` redirects, HTTPS port `443` with HTTP/2, site-specific roots, index files, TLS 1.2 and 1.3, HSTS, security headers, gzip, static-file `try_files`, protected paths, and per-site logs.
   - Reloads nginx after changed site templates, symlinks, or default-site removal.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started; restarted after jail configuration changes
- `nginx`: enabled and started; reloaded after nginx configuration, site, symlink, or certificate changes
- `sshd` or `ssh`: restarted only after SSH hardening changes; not enabled or started by this cookbook

**Platform considerations**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`
- Account for package-manager differences, SSH service names, nginx worker-user differences, and UFW availability on CentOS.

## Credentials

**Detection Summary**: No external credentials or secret-manager integrations detected. Three locally generated private TLS keys and three locally generated self-signed certificates are created.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed TLS private keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by OpenSSL; not stored in a data bag, vault, environment variable, or attribute
- **Usage context**: nginx HTTPS private keys
- **Permissions**: `0640`, owner `root`, group `ssl-cert`

### Self-signed TLS certificates

- **Variable(s)**: `cert_file`; `/etc/ssl/certs/test.cluster.local.crt`; `/etc/ssl/certs/ci.cluster.local.crt`; `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: nginx HTTPS certificate files

`admin@example.com` is embedded in the certificate subject and is not an authentication secret.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/opt/server/test
/opt/server/test/index.html
/opt/server/ci
/opt/server/ci/index.html
/opt/server/status
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
/etc/nginx/sites-enabled/default
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/test.cluster.local_access.log
/var/log/nginx/test.cluster.local_error.log
/var/log/nginx/ci.cluster.local_access.log
/var/log/nginx/ci.cluster.local_error.log
/var/log/nginx/status.cluster.local_access.log
/var/log/nginx/status.cluster.local_error.log
/run/nginx.pid
```

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: TCP `22`
- nginx PID: `/run/nginx.pid`
- Application Unix socket: none configured

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

**Total template render operations**: 7

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban
pgrep -a nginx
cat /run/nginx.pid

# Nginx configuration
nginx -t
nginx -T

# Firewall
ufw status verbose
ufw status | grep "22/tcp"
ufw status | grep "80/tcp"
ufw status | grep "443/tcp"

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t
systemctl status sshd || systemctl status ssh

# Kernel security
cat /etc/sysctl.d/99-security.conf
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

# Ports and processes
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Site directories and links
ls -ld /opt/server/test /opt/server/ci /opt/server/status
ls -l /opt/server/test/index.html
ls -l /opt/server/ci/index.html
ls -l /opt/server/status/index.html
ls -l /etc/nginx/sites-enabled/test.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
```

### test.cluster.local checks

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

grep -E 'server_name|listen|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/test.cluster.local

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject | grep 'CN = test.cluster.local'
stat -c '%A %U:%G %n' /etc/ssl/private/test.cluster.local.key
```

Expected results: HTTP returns `301` to HTTPS; HTTPS serves the test content from `/opt/server/test`; security and HSTS headers are present; the certificate common name is `test.cluster.local`; the key is `root:ssl-cert` with mode `0640`.

### ci.cluster.local checks

```bash
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

grep -E 'server_name|listen|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/ci.cluster.local

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject | grep 'CN = ci.cluster.local'
stat -c '%A %U:%G %n' /etc/ssl/private/ci.cluster.local.key
```

Expected results: HTTP returns `301` to HTTPS; HTTPS serves the CI content from `/opt/server/ci`; security and HSTS headers are present; the certificate common name is `ci.cluster.local`; the key is `root:ssl-cert` with mode `0640`.

### status.cluster.local checks

```bash
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

grep -E 'server_name|listen|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/status.cluster.local

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject | grep 'CN = status.cluster.local'
stat -c '%A %U:%G %n' /etc/ssl/private/status.cluster.local.key
```

Expected results: HTTP returns `301` to HTTPS; HTTPS serves the status content from `/opt/server/status`; security and HSTS headers are present; the certificate common name is `status.cluster.local`; the key is `root:ssl-cert` with mode `0640`.

Migration is complete when nginx and fail2ban are enabled and running, all three named sites respond over HTTPS, HTTP redirects to HTTPS, all certificates and keys exist with the expected permissions, the default site is absent, firewall rules are active, and SSH and kernel hardening settings are applied.