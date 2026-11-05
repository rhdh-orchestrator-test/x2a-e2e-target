---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx and Fail2ban, configures UFW and kernel security settings, hardens SSH, creates self-signed certificates, deploys static site roots and index files, and enables HTTP-to-HTTPS virtual-host redirection. The Ansible implementation must preserve the recipe execution order, exact site names, paths, ports, certificate locations, security settings, and resource behavior. Detailed rendered template behavior requires separate verification against the template files.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled static website
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

**Security services and settings**:

- **fail2ban**: Enabled; package `fail2ban`; service `fail2ban`; configuration `/etc/fail2ban/jail.local`
- **ufw**: Enabled; package `ufw`; default deny; SSH, HTTP, and HTTPS allowed
- **ssh**: Root login disabled; password authentication disabled; configuration `/etc/ssh/sshd_config`; managed service resource `ssh` has action `nothing`

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
    └── default/
```

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

No static files under `files/default/*` or `files/*` are listed. The three `cookbook_file` resources refer to dynamic source paths: `test/index.html`, `ci/index.html`, and `status/index.html`. Their contents must be obtained or defined separately.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - The Ansible role must preserve this logical order: host security, Nginx installation, SSL generation, then virtual-host deployment.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs packages `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Applies UFW commands in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `reload_sysctl` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`.
   - Configures `PermitRootLogin no` and `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Declares the `ssh` service with action `nothing`; no unconditional SSH restart or reload is present.
   - Important sysctl values include:
     - `net.ipv4.conf.default.rp_filter = 1`
     - `net.ipv4.conf.all.rp_filter = 1`
     - `net.ipv4.conf.all.accept_redirects = 0`
     - `net.ipv6.conf.all.accept_redirects = 0`
     - `net.ipv4.conf.all.send_redirects = 0`
     - `net.ipv4.conf.default.send_redirects = 0`
     - `net.ipv4.conf.all.accept_source_route = 0`
     - `net.ipv6.conf.all.accept_source_route = 0`
     - `net.ipv4.conf.all.log_martians = 1`
     - `net.ipv4.conf.default.log_martians = 1`
     - `net.ipv4.icmp_echo_ignore_all = 1`
     - `net.ipv4.icmp_echo_ignore_broadcasts = 1`
     - `net.ipv6.conf.all.disable_ipv6 = 1`
     - `net.ipv6.conf.default.disable_ipv6 = 1`
     - `net.ipv6.conf.lo.disable_ipv6 = 1`
     - `net.ipv4.tcp_syncookies = 1`
     - `net.ipv4.tcp_max_syn_backlog = 2048`
     - `net.ipv4.tcp_synack_retries = 2`
     - `net.ipv4.tcp_syn_retries = 5`
   - Resources: one package resource, two service resources, two templates, and eight execute resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs package `nginx`.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates document roots with mode `0755`:
     - `/opt/server/test`
     - `/opt/server/ci`
     - `/opt/server/status`
   - Deploys index files with mode `0644`:
     - `/opt/server/test/index.html` from `test/index.html`
     - `/opt/server/ci/index.html` from `ci/index.html`
     - `/opt/server/status/index.html` from `status/index.html`
   - The source index-file contents are not present in the supplied file listing and must be supplied separately.
   - The main configuration is documented as using worker user `www-data`, automatic worker processes, PID `/run/nginx.pid`, `768` worker connections, `65` second keepalive timeout, gzip, and the standard module, MIME, `conf.d`, and `sites-enabled` includes.
   - Exact rendered template settings, including buffer values, cipher lists, and other security directives, require separate verification against `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` and `security.conf.erb`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs packages `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with mode `0755` and group `root`.
   - Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
   - Generates certificates for the three explicit sites:
     - **test.cluster.local**:
       - Key `/etc/ssl/private/test.cluster.local.key`
       - Certificate `/etc/ssl/certs/test.cluster.local.crt`
       - Resource `generate-ssl-cert-test.cluster.local`
     - **ci.cluster.local**:
       - Key `/etc/ssl/private/ci.cluster.local.key`
       - Certificate `/etc/ssl/certs/ci.cluster.local.crt`
       - Resource `generate-ssl-cert-ci.cluster.local`
     - **status.cluster.local**:
       - Key `/etc/ssl/private/status.cluster.local.key`
       - Certificate `/etc/ssl/certs/status.cluster.local.crt`
       - Resource `generate-ssl-cert-status.cluster.local`
   - Each certificate is a 2048-bit RSA, self-signed certificate valid for `365` days with the site name as common name and `admin@example.com` as the subject email.
   - Each private key is mode `640`, owned by `root:ssl-cert`.
   - Certificate generation must be idempotent and must not regenerate existing certificates unnecessarily.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - **test.cluster.local** to `/etc/nginx/sites-available/test.cluster.local`, using document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
     - **ci.cluster.local** to `/etc/nginx/sites-available/ci.cluster.local`, using document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
     - **status.cluster.local** to `/etc/nginx/sites-available/status.cluster.local`, using document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Each rendered site has `ssl_enabled: true`.
   - Creates enabled links:
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
   - Deletes `/etc/nginx/sites-enabled/default`.
   - The supplied plan describes HTTP-to-HTTPS redirection, HTTPS on port `443`, TLS settings, headers, logging, and static-file handling. These rendered behaviors require separate verification against `cookbooks/nginx-multisite/templates/default/site.conf.erb`.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no explicit restart or reload

## Credentials

**Detection Summary**: No externally supplied application credentials, passwords, API tokens, data bags, vault references, or secret-manager integrations were detected. Three locally generated TLS private keys are created.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: No secret path or data bag detected

### TLS Private Keys

- **Variable(s)**: `/etc/ssl/private/test.cluster.local.key`, `/etc/ssl/private/ci.cluster.local.key`, `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`, `cookbooks/nginx-multisite/attributes/default.rb`
- **Current storage**: Locally generated files
- **Usage context**: Nginx TLS private keys for the three HTTPS virtual hosts
- **Protection**: Mode `640`, owner `root`, group `ssl-cert`

### Certificate Subject Email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded, non-secret certificate subject value
- **Usage context**: Email address in each self-signed certificate subject

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/etc/nginx/sites-enabled/default
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
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
/etc/ssh/sshd_config
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/test.cluster.local_access.log
/var/log/nginx/test.cluster.local_error.log
/var/log/nginx/ci.cluster.local_access.log
/var/log/nginx/ci.cluster.local_error.log
/var/log/nginx/status.cluster.local_access.log
/var/log/nginx/status.cluster.local_error.log
/var/log/auth.log
```

**Service endpoints to check**:
- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`

**Templates rendered**:
- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times, to the `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` site configurations

## Pre-flight checks

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
test ! -e /etc/nginx/sites-enabled/default

# Fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Firewall
ufw status verbose
ufw status numbered

# SSH and sysctl
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# TLS permissions
stat -c '%a %U %G %n' /etc/ssl/private
stat -c '%a %U %G %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Listening ports
ss -tlnp | grep -E ':(80|443)\b'
```

### `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates
```

Expected results: HTTP redirects to HTTPS, HTTPS returns a successful response when the index file is present, and the certificate subject contains `CN=test.cluster.local`.

### `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates
```

Expected results: HTTP redirects to HTTPS, HTTPS returns a successful response when the index file is present, and the certificate subject contains `CN=ci.cluster.local`.

### `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates
```

Expected results: HTTP redirects to HTTPS, HTTPS returns a successful response when the index file is present, and the certificate subject contains `CN=status.cluster.local`.

### Logs

```bash
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
tail -n 50 /var/log/auth.log
```

### Template verification

Verify the actual contents of these source templates before treating detailed rendered settings as migration facts:

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

This verification must confirm the Fail2ban jail values, Nginx buffer and TLS settings, cipher list, HTTP/2 behavior, HSTS and security headers, CSP rules, gzip configuration, and static-file handling.