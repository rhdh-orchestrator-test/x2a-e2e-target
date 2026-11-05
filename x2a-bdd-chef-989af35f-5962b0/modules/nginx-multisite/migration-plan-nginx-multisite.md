---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a hardened multi-site web server with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates document roots and locally generated self-signed certificates; deploys nginx security and virtual-host configurations; redirects HTTP to HTTPS; applies kernel network-hardening settings; and disables SSH root login and password authentication.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**: Ubuntu `>= 18.04` and CentOS `>= 7.0`

**Configured Instances**:

- **test.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; source `test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; source `ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; source `status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

Security settings are configured as follows:

- Fail2ban enabled attribute: `true`
- UFW enabled attribute: `true`
- SSH root login disabled: `true`
- SSH password authentication disabled: `false`

Fail2ban and UFW resources execute according to the recipe flow. SSH configuration changes execute because the supplied SSH attribute conditions are active.

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

No provider files, custom resources, or static `cookbook_file` source files are listed. The recipes nevertheless deploy the following cookbook files, which must be supplied or otherwise accounted for in the Ansible migration:

- `test/index.html`
- `ci/index.html`
- `status/index.html`

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - This execution order must be preserved.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures fail2ban defaults: ban time `3600`, find time `600`, retry count `3`, and backend `auto`.
   - Enables the SSH, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Configures SSH monitoring on `/var/log/auth.log`.
   - Configures nginx error-log monitoring for HTTP authentication and request limiting.
   - Configures nginx access-log monitoring for bot searches.
   - Sets UFW default incoming policy to deny.
   - Allows SSH on `22/tcp`, HTTP on `80/tcp`, and HTTPS on `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Applies reverse-path filtering, redirect protection, source-route disabling, martian packet logging, ICMP protections, IPv6 disabling, SYN-cookie protection, TCP backlog settings, and TCP retry settings.
   - Reloads `/etc/sysctl.d/99-security.conf` only when the sysctl template changes.
   - Changes `/etc/ssh/sshd_config` to `PermitRootLogin no`.
   - Changes `/etc/ssh/sshd_config` to `PasswordAuthentication no`.
   - Restarts SSH only when either SSH setting changes.
   - Contains 8 execute resources in total: `ufw_default_deny`, `ufw_allow_ssh`, `ufw_allow_http`, `ufw_allow_https`, `ufw_enable`, `reload_sysctl`, `disable root login`, and `disable password auth`.
   - Two conditional SSH execute resources are active with the supplied attributes. `reload_sysctl` has `action :nothing` and runs only through notification.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Configures worker user `www-data`, automatic worker processes, PID file `/run/nginx.pid`, worker connections `768`, standard nginx access and error logs, gzip, and the modules, `conf.d`, and `sites-enabled` includes.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Hides the nginx version with `server_tokens off`.
   - Configures `login` rate limiting at `10r/m` and `api` rate limiting at `30r/m`, both with `10m` zones.
   - Applies request and header buffer restrictions, a `1k` maximum body size, and 10-second client body, header, and send timeouts.
   - Restricts TLS to `TLSv1.2 TLSv1.3`, configures a shared `10m` SSL session cache, a `10m` SSL session timeout, the configured cipher suite, and server cipher preference.
   - Enables and starts nginx.
   - Creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`, then deploys `/opt/server/test/index.html` from `test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`, then deploys `/opt/server/ci/index.html` from `ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`, then deploys `/opt/server/status/index.html` from `status/index.html` with mode `0644`.
   - Processes exactly three sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and the CA certificate package.
   - The structured execution tree reports the second package as `ca-cert`, while the recipe analysis reports `ca-certificates`. This source discrepancy must be confirmed against the actual recipe before migration; `ca-certificates` is the package name used in the migration dependency and verification commands.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate and key for `test.cluster.local`.
   - Generates a self-signed RSA 2048-bit certificate and key for `ci.cluster.local`.
   - Generates a self-signed RSA 2048-bit certificate and key for `status.cluster.local`.
   - Uses a validity period of 365 days and subject metadata `C=US`, `ST=Example`, `L=Example`, `O=Example Org`, `OU=IT`, and `emailAddress=admin@example.com`.
   - Stores keys with mode `0640` and ownership `root:ssl-cert`.
   - Skips certificate generation when the corresponding certificate and key already exist.
   - Delays an nginx reload when a certificate is newly generated.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Delayed nginx reloads occur after virtual-host template, link, or default-site changes.
   - Each site provides an HTTP listener on port `80`, redirects HTTP to HTTPS, and provides an HTTP/2 HTTPS listener on port `443`.
   - Each site enables TLS 1.2 and TLS 1.3, HSTS, security headers, gzip, `try_files` returning `404` for missing files, and denial of `.htaccess`, `.git`, and `.svn` paths.
   - Site-specific access and error logs are configured for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

## Dependencies

**External cookbook dependencies**: None listed.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates` according to the recipe analysis; the structured execution tree reports `ca-cert`, which must be verified before migration

**Service dependencies**:

- `fail2ban`: enabled and started; restarted after `/etc/fail2ban/jail.local` changes
- `nginx`: enabled and started; reloaded after nginx configuration, certificate, virtual-host, or symlink changes
- `ssh`: restarted only after SSH authentication configuration changes

## Credentials

**Detection Summary**: 0 externally sourced credentials detected across the cookbook files.

No passwords, API tokens, data bags, encrypted data bags, Chef Vault items, CyberArk integrations, Conjur variables, or external secret-manager references were detected.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

The following are security-sensitive generated TLS artifacts, not externally supplied credentials.

### Generated TLS Private Keys

- **Variable(s)**: `key_file`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated filesystem keys; not stored in a data bag, vault, or secret manager
- **Usage context**: HTTPS private keys for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Permissions**: `root:ssl-cert`, mode `0640`

### Generated TLS Certificates

- **Variable(s)**: `cert_file`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated self-signed certificates
- **Usage context**: HTTPS certificates for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Validity**: 365 days
- **Subject email**: `admin@example.com`
- **Credential status**: Not a password, token, or externally sourced authentication secret

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
- SSH: `22`
- Nginx PID: `/run/nginx.pid`
- Unix socket: None configured

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

`site.conf.erb` is rendered 3 times in total.

## Pre-flight checks

```bash
# Verify required packages.
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Verify required services.
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Validate nginx configuration.
nginx -t

# Verify security and nginx configuration values.
grep -E 'user|worker_processes|worker_connections|access_log|error_log|gzip' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Verify SSH hardening.
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# Verify fail2ban and sysctl configuration.
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf
systemctl status fail2ban

# Verify test.cluster.local.
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
grep -E 'listen 80|listen 443 ssl http2|server_name test.cluster.local|root /opt/server/test|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: test.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: test.cluster.local' https://127.0.0.1/ | head

# Verify ci.cluster.local.
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
grep -E 'listen 80|listen 443 ssl http2|server_name ci.cluster.local|root /opt/server/ci|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: ci.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: ci.cluster.local' https://127.0.0.1/ | head

# Verify status.cluster.local.
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
grep -E 'listen 80|listen 443 ssl http2|server_name status.cluster.local|root /opt/server/status|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: status.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: status.cluster.local' https://127.0.0.1/ | head

# Verify certificates and private-key permissions.
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout \
  -subject -issuer -dates -ext subjectAltName
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout \
  -subject -issuer -dates -ext subjectAltName
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout \
  -subject -issuer -dates -ext subjectAltName

stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# Verify security headers.
curl -k -s -D - -o /dev/null \
  -H 'Host: test.cluster.local' \
  https://127.0.0.1/ | grep -E \
  'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection|Referrer-Policy|Content-Security-Policy'

# Verify firewall state and required rules.
ufw status verbose
ufw status numbered
```

Expected results:

- `nginx`, `fail2ban`, `ufw`, `openssl`, and the confirmed CA certificate package are installed.
- `nginx` and `fail2ban` are enabled and active.
- `nginx -t` succeeds.
- All three HTTP requests return a `301` redirect to HTTPS.
- HTTPS requests for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` return `200 OK` and serve their respective static index files.
- Each enabled-site symlink resolves to its corresponding `sites-available` file.
- All three certificates are parseable, self-signed, and valid for 365 days from generation.
- All three private keys are owned by `root:ssl-cert` with mode `640`.
- HSTS, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, XSS protection, referrer policy, and Content Security Policy headers are present.
- UFW reports `Status: active`.
- UFW default incoming policy is `deny`.
- UFW rules allow SSH on `22/tcp`, HTTP on `80/tcp`, and HTTPS on `443/tcp`.
