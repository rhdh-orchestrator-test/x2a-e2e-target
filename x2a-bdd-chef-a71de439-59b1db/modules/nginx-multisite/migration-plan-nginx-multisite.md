---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This Chef cookbook configures nginx as a multi-site HTTPS web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and index files; generates self-signed TLS certificates; configures nginx security headers, rate limits, and TLS; enables SSH, HTTP, and HTTPS firewall rules; applies kernel security settings; and disables root SSH login and SSH password authentication.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled static web site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; logs `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`; index file `/opt/server/test/index.html`

- **ci.cluster.local**: HTTPS-enabled static web site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; logs `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`; index file `/opt/server/ci/index.html`

- **status.cluster.local**: HTTPS-enabled static web site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; logs `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`; index file `/opt/server/status/index.html`

Security configuration includes:

- **fail2ban**: Enabled and started
- **ufw**: Enabled with default incoming policy `deny`; SSH, HTTP, and HTTPS allowed
- **ssh**: Root login disabled and password authentication disabled

All sites use:

- Document roots under `/opt/server`
- TLS certificate path `/etc/ssl/certs`
- TLS private-key path `/etc/ssl/private`
- `ssl_enabled: true`
- TLS protocols `TLSv1.2` and `TLSv1.3`
- HTTP-to-HTTPS redirection
- HTTP/2 on HTTPS listeners

## File Structure

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

No provider files are used by the execution tree. A structural analysis mentions `resources/lineinfile.rb`, but it is not part of the execution tree and must not be migrated as an executed component.

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

No static files are present in the supplied directory listing. The `nginx.rb` recipe references these cookbook file sources, which were not supplied:

```text
test/index.html
ci/index.html
status/index.html
```

The Ansible migration must provide or otherwise account for these referenced source files.

## Module Explanation

The cookbook performs operations in this order:

1. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures fail2ban defaults: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Enables the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Configures SSH logging through `/var/log/auth.log`.
   - Configures nginx authentication and rate-limit jails using `/var/log/nginx/*error.log`.
   - Configures the nginx bot-search jail using `/var/log/nginx/*access.log`.
   - Sets the UFW default policy to deny.
   - Allows `22/tcp`, `80/tcp`, and `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Applies reverse-path filtering, redirect protection, source-route disabling, martian packet logging, ICMP protections, IPv6 disabling, and TCP SYN flood protection.
   - Reloads the sysctl configuration with `sysctl -p /etc/sysctl.d/99-security.conf` when the template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` only when either SSH setting changes.
   - Realized resources with the supplied defaults: 1 package resource, 2 service resources, 2 templates, and 8 execute resources. The execute resources are five UFW commands, one sysctl reload command, and two conditional SSH commands.

2. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Configures worker user `nginx`, automatic worker processes, PID file `/run/nginx.pid`, `768` worker connections, sendfile, TCP optimizations, keepalive timeout `65`, global access and error logs, gzip, and the `conf.d` and `sites-enabled` includes.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Configures `server_tokens off`, request-limit zones for `login` and `api`, small client buffers and body limits, client and send timeouts of `10`, TLS session caching, TLS session timeout `10m`, TLS protocols `TLSv1.2 TLSv1.3`, the configured cipher list, and preferred server ciphers.
   - Enables and starts nginx.
   - Deploys the following cookbook file sources:
     - `test/index.html` to `/opt/server/test/index.html`, owned by `nginx:nginx`, mode `0644`
     - `ci/index.html` to `/opt/server/ci/index.html`, owned by `nginx:nginx`, mode `0644`
     - `status/index.html` to `/opt/server/status/index.html`, owned by `nginx:nginx`, mode `0644`
   - Supports nginx reload and restart notifications from configuration, certificate, site, and link changes.

3. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed certificate and private key for `test.cluster.local` unless both files already exist:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Resource: `execute[generate-ssl-cert-test.cluster.local]`
   - Generates a self-signed certificate and private key for `ci.cluster.local` unless both files already exist:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Resource: `execute[generate-ssl-cert-ci.cluster.local]`
   - Generates a self-signed certificate and private key for `status.cluster.local` unless both files already exist:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Resource: `execute[generate-ssl-cert-status.cluster.local]`
   - Uses `openssl req -x509 -nodes -days 365 -newkey rsa:2048`.
   - Uses certificate subjects containing the corresponding hostname and `admin@example.com`.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Notifies `service[nginx]` for a delayed reload after newly generating a certificate.

4. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` owned by `root:root` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` owned by `root:root` with mode `0755`.
   - Creates `/opt/server/test` owned by `nginx:nginx` with mode `0755` and recursive creation enabled.
   - Creates `/opt/server/ci` owned by `nginx:nginx` with mode `0755` and recursive creation enabled.
   - Creates `/opt/server/status` owned by `nginx:nginx` with mode `0755` and recursive creation enabled.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` as a link to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` as a link to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` as a link to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Delays an nginx reload when site templates, links, or the default-site deletion changes.
   - Renders an HTTP virtual host on port `80` with an HTTPS redirect for each named site.
   - Renders an HTTPS virtual host on port `443` with HTTP/2 for each named site.
   - Configures `index.html`, `index.htm`, and `index.php`; HSTS; `X-Frame-Options DENY`; `X-Content-Type-Options nosniff`; `X-XSS-Protection`; a strict referrer policy; a Content Security Policy; gzip; `try_files $uri $uri/ =404`; `.htaccess` denial; `.git` and `.svn` denial; and site-specific access and error logs.
   - Realized resources: 5 directories, 3 templates, 3 links, and 1 deleted file.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: Enabled and started; restarted when `/etc/fail2ban/jail.local` changes.
- `nginx`: Enabled and started; reloaded when nginx configuration, certificates, site templates, site links, or default-site deletion changes.
- `sshd`: Not started or enabled by this cookbook; restarted only when SSH hardening settings change.

**Platform support from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The migration must preserve the UFW-based firewall behavior while accounting for the metadata support for CentOS.

## Credentials

**Detection Summary**: No credentials or external secret-manager integrations were detected across the analyzed files.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

### Self-signed TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; not stored in a data bag, vault, environment variable, or hardcoded secret attribute.
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts.
- **Protection**: Owner `root`, group `ssl-cert`, mode `0640`; parent directory `/etc/ssl/private` mode `0710`.

These are sensitive cryptographic files, but the cookbook generates development self-signed certificates. The fixed certificate subject email address `admin@example.com` is not a credential.

No data bag, Chef Vault, Conjur, CyberArk, Vault URL, database credential, API token, password attribute, or secret environment variable was detected.

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
- `/etc/nginx/sites-enabled/default` should be absent
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

**Service endpoints to check**:

- SSH: TCP `22`
- `test.cluster.local`: HTTP TCP `80`, HTTPS TCP `443`
- `ci.cluster.local`: HTTP TCP `80`, HTTPS TCP `443`
- `status.cluster.local`: HTTP TCP `80`, HTTPS TCP `443`

**Unix sockets**: None configured.

**Network interfaces**: No specific bind address is configured. nginx uses the default listen behavior on ports `80` and `443`.

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 time
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 time
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 time
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 time
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 time
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 time
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 time

**Total rendered template instances**: 7

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Firewall
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# Listening ports
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t
systemctl status sshd
```

Expected results:

- nginx and fail2ban are enabled and active.
- `nginx -t` succeeds.
- The nginx configuration contains `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
- UFW is active with default incoming policy `deny`.
- UFW allows `22/tcp`, `80/tcp`, and `443/tcp`.
- nginx listens on TCP ports `80` and `443`.
- The four configured fail2ban jails are available and enabled.
- Root SSH login is disabled.
- SSH password authentication is disabled.
- `sshd -t` succeeds.

### `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -ks --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head
```

Expected results:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200 OK` when the index file is present.
- The HTTPS response uses the `test.cluster.local` certificate.
- The response includes HSTS, `X-Frame-Options`, and `X-Content-Type-Options`.

### `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -ks --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head
```

Expected results:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200 OK` when the index file is present.
- The HTTPS response uses the `ci.cluster.local` certificate.
- The response includes HSTS, `X-Frame-Options`, and `X-Content-Type-Options`.

### `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -ks --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head
```

Expected results:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200 OK` when the index file is present.
- The HTTPS response uses the `status.cluster.local` certificate.
- The response includes HSTS, `X-Frame-Options`, and `X-Content-Type-Options`.

### TLS certificate validation

```bash
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected results:

- Each certificate is valid for 365 days from generation.
- Each certificate subject contains its corresponding site name.
- Each private key is owned by `root:ssl-cert` with mode `640`.