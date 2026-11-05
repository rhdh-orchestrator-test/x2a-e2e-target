---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a multisite HTTPS web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates document roots and static pages; generates local self-signed certificates; deploys global, security, and per-site nginx configuration; enables firewall and SSH hardening; and starts nginx and fail2ban. No external cookbook dependency or credential-management integration is declared. Template contents, metadata, command details, and credential-scan results require verification against the cookbook source.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; content `/opt/server/test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; content `/opt/server/ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; content `/opt/server/status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

**Security components**:

- **fail2ban**: Package `fail2ban`; enabled and started; configuration `/etc/fail2ban/jail.local`
- **ufw**: Package `ufw`; default deny; allows SSH, HTTP, and HTTPS; enabled
- **ssh**: Root login disabled; password authentication disabled; restart delayed until SSH configuration changes

## File Structure

The following files are used by the cookbook and are listed relative to `cookbooks/nginx-multisite`.

### Recipes

```text
attributes/default.rb
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

### Providers

```text
```

No provider files are used by the execution tree.

### Templates

```text
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb
```

### Attributes

```text
attributes/default.rb
```

### Files

No static files are shown as deployed by a `cookbook_file` resource in the supplied file listing. The recipes reference these dynamic cookbook files:

```text
test/index.html
ci/index.html
status/index.html
```

Their presence is not verifiable from the supplied analysis and must be confirmed before migration.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Sets UFW default incoming policy to deny.
   - Allows SSH on `22/tcp`, HTTP on `80/tcp`, and HTTPS on `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Reloads sysctl settings after the security configuration changes.
   - Disables `PermitRootLogin` and `PasswordAuthentication` in `/etc/ssh/sshd_config` when configured values require it.
   - Restarts SSH only after an SSH hardening change.
   - Template and command notification timing should be verified against the recipe source.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts nginx.
   - Creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`.
   - Deploys `test/index.html` to `/opt/server/test/index.html` with owner `www-data`, group `www-data`, and mode `0644`.
   - Creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`.
   - Deploys `ci/index.html` to `/opt/server/ci/index.html` with owner `www-data`, group `www-data`, and mode `0644`.
   - Creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`.
   - Deploys `status/index.html` to `/opt/server/status/index.html` with owner `www-data`, group `www-data`, and mode `0644`.
   - The three static source files must be verified before deployment.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a 2048-bit RSA, 365-day self-signed certificate and key for `test.cluster.local`.
   - Generates a 2048-bit RSA, 365-day self-signed certificate and key for `ci.cluster.local`.
   - Generates a 2048-bit RSA, 365-day self-signed certificate and key for `status.cluster.local`.
   - Stores certificate files under `/etc/ssl/certs` and private keys under `/etc/ssl/private`.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Certificate generation is skipped when the corresponding certificate and key already exist.
   - Certificate subjects use the configured example organization values and the site hostname as CN; command and subject details require source verification.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with the `test.cluster.local` document root and certificate paths.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with the `ci.cluster.local` document root and certificate paths.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with the `status.cluster.local` document root and certificate paths.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Configures HTTP-to-HTTPS redirects, HTTPS on port `443`, HTTP/2, TLS 1.2 and TLS 1.3, HSTS, security headers, gzip, `try_files`, protected-path denials, and per-site logs.
   - Site templates and links notify nginx of delayed reloads; notification timing requires source verification.

## Dependencies

**External cookbook dependencies**: None shown in `metadata.rb`; metadata analysis requires source verification.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**:
- `nginx`: enabled and started; reloads after configuration, certificate, site-link, or default-site changes
- `fail2ban`: enabled and started; restarts after jail configuration changes
- `ssh`: defined with action `nothing`; restarts after SSH hardening changes

**Supported platforms requiring verification**: Ubuntu `>= 18.04`; CentOS `>= 7.0`

## Credentials

**Detection Summary**: No external credential-management integration was identified in the supplied plan. Credential-scan results for all recipes were not supplied, so the absence of hardcoded credentials, environment-variable secrets, data bags, vault references, or secret-manager references remains unverified.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

### Self-signed TLS private keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files, not a vault or data bag
- **Usage context**: TLS private keys for the `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` nginx HTTPS virtual hosts
- **Permissions**: `root:ssl-cert`, mode `0640`

### Certificate subject email address

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Reported as hardcoded in the OpenSSL command; source verification required
- **Usage context**: Subject email address in the self-signed certificates
- **Security impact**: Not an authentication credential, password, or API token

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
- `/etc/nginx/sites-enabled/default` must not exist
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`
- `/var/log/auth.log`

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: `22/tcp`
- nginx PID file: `/run/nginx.pid`
- Application Unix socket: none configured

**Templates rendered**:

- `fail2ban.jail.local.erb`: once, `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once, `/etc/nginx/nginx.conf`
- `security.conf.erb`: once, `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once, `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
  rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active ssh

# Configuration validation
nginx -t
sshd -t
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf

# Enabled-site links and removed default site
test -L /etc/nginx/sites-enabled/test.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl --insecure -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout \
  -subject -issuer -dates
test -f /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /opt/server/test/index.html \
  /etc/ssl/private/test.cluster.local.key

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl --insecure -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout \
  -subject -issuer -dates
test -f /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /opt/server/ci/index.html \
  /etc/ssl/private/ci.cluster.local.key

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl --insecure -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout \
  -subject -issuer -dates
test -f /etc/ssl/private/status.cluster.local.key
stat -c '%U:%G %a %n' /opt/server/status/index.html \
  /etc/ssl/private/status.cluster.local.key

# Firewall
ufw status verbose
ufw status numbered

# fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# Kernel settings
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# Listening ports and logs
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```