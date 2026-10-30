---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: `nginx-multisite` is a web-server cookbook for Ubuntu 18.04+ and CentOS 7+, configuring nginx with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, OpenSSL, CA certificates, Fail2ban, and UFW; applies security hardening; generates self-signed certificates; creates per-site document roots and index files; deploys nginx virtual-host configurations; enables the sites; and removes the default nginx site. The static sources `test/index.html`, `ci/index.html`, and `status/index.html` must be verified or supplied before migration completion.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled static nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

### Security Collection

- **fail2ban**
  - Package: `fail2ban`
  - Service: enabled and started
  - Configuration: `/etc/fail2ban/jail.local`

- **ufw**
  - Package: `ufw`
  - Policy: default deny
  - Allowed services: SSH, HTTP, and HTTPS
  - State: enabled

- **ssh**
  - Root login: disabled
  - Password authentication: disabled
  - Configuration: `/etc/ssh/sshd_config`
  - Restart: delayed when SSH configuration changes

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

No provider is used by the executed recipe flow.

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

The recipes invoke `cookbook_file` for these dynamic sources, but no static files are present in the supplied directory listing:

```text
test/index.html
ci/index.html
status/index.html
```

These files must be verified or supplied before completing the Ansible migration.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Imports `security`, `nginx`, `ssl`, and `sites`, in that order.
   - The Ansible role must preserve this execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban with ban time `3600`, find time `600`, maximum retries `3`, backend `auto`, SSH protection using `/var/log/auth.log`, and nginx HTTP-auth, request-limit, and bot-search jails.
   - Applies UFW default deny and allows SSH `22/tcp`, HTTP `80/tcp`, and HTTPS `443/tcp`; enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`, then reloads sysctl when changed.
   - Disables root SSH login and password authentication in `/etc/ssh/sshd_config`; restarts SSH only when either setting changes.
   - Resources: one package collection, services `fail2ban` and `ssh`, two templates, and **eight execute resources**: five UFW commands, one sysctl reload, and two SSH-hardening commands.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures worker user `www-data`, automatic worker processes, PID `/run/nginx.pid`, 768 worker connections, global access and error logs, gzip, and includes for `conf.d` and `sites-enabled`.
   - Applies `server_tokens off`, login rate limit `10r/m`, API rate limit `30r/m`, 1K body limits and buffers, 10-second client/header/send timeouts, TLS 1.2 and 1.3, a 10m shared SSL cache, and a 10m SSL session timeout.
   - Enables and starts nginx.
   - **Iteration: `test.cluster.local`**:
     - Creates `/opt/server/test` owned by `www-data:www-data`, mode `0755`.
     - Deploys `test/index.html` to `/opt/server/test/index.html`, owned by `www-data:www-data`, mode `0644`.
   - **Iteration: `ci.cluster.local`**:
     - Creates `/opt/server/ci` owned by `www-data:www-data`, mode `0755`.
     - Deploys `ci/index.html` to `/opt/server/ci/index.html`, owned by `www-data:www-data`, mode `0644`.
   - **Iteration: `status.cluster.local`**:
     - Creates `/opt/server/status` owned by `www-data:www-data`, mode `0755`.
     - Deploys `status/index.html` to `/opt/server/status/index.html`, owned by `www-data:www-data`, mode `0644`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root`, mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert`, mode `0710`.
   - All three sites have `ssl_enabled: true`.
   - **Iteration: `test.cluster.local`**:
     - Generates `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`.
   - **Iteration: `ci.cluster.local`**:
     - Generates `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`.
   - **Iteration: `status.cluster.local`**:
     - Generates `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`.
   - Certificates are self-signed, RSA 2048-bit, valid for 365 days, and use subject metadata with the site name and `admin@example.com`.
   - Keys are owned by `root:ssl-cert` with mode `0640`.
   - The source implementation must be confirmed to guard certificate generation when both certificate and key already exist. The Ansible implementation must preserve this idempotence explicitly.
   - Certificate changes notify a delayed nginx reload.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times and creates three enabled-site links.
   - **Iteration: `test.cluster.local`**:
     - Renders `/etc/nginx/sites-available/test.cluster.local` with document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
     - Links `/etc/nginx/sites-enabled/test.cluster.local` to the available-site file.
   - **Iteration: `ci.cluster.local`**:
     - Renders `/etc/nginx/sites-available/ci.cluster.local` with document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
     - Links `/etc/nginx/sites-enabled/ci.cluster.local` to the available-site file.
   - **Iteration: `status.cluster.local`**:
     - Renders `/etc/nginx/sites-available/status.cluster.local` with document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
     - Links `/etc/nginx/sites-enabled/status.cluster.local` to the available-site file.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Each virtual host provides HTTP port `80` to HTTPS redirection, HTTPS port `443` with HTTP/2, TLS 1.2 and 1.3, one-year HSTS with subdomains, security headers, gzip, `try_files $uri $uri/ =404`, denial of `.htaccess`, `.git`, and `.svn`, and per-site access and error logs.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**: `fail2ban` enabled and started; `nginx` enabled and started; `ssh` restarted only when SSH hardening changes are applied.

**Network dependencies**: UFW allows `22/tcp`, `80/tcp`, and `443/tcp`.

## Credentials

**Detection Summary**: 0 credentials detected across the analyzed files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No credentials or secrets were detected in this cookbook. No data bags, encrypted data bags, Chef Vault items, CyberArk or Conjur integrations, Vault paths, secret attributes, API keys, passwords, database credentials, or environment-variable secrets were found.

The literal `admin@example.com` is certificate subject metadata, not a credential. The generated certificates are self-signed development certificates.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
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
```

Also verify that `/etc/nginx/sites-enabled/default` does not exist and that the three source files `test/index.html`, `ci/index.html`, and `status/index.html` are available to the migration.

**Service endpoints to check**: `test.cluster.local` HTTP `80` and HTTPS `443`; `ci.cluster.local` HTTP `80` and HTTPS `443`; `status.cluster.local` HTTP `80` and HTTPS `443`; SSH firewall port `22/tcp`. No Unix socket is configured.

**Templates rendered**:
- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times, to the `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` site files

## Pre-flight checks

```bash
# Verify services
systemctl is-active nginx
systemctl is-enabled nginx
systemctl is-active fail2ban
systemctl is-enabled fail2ban

# Verify packages
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Validate nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Verify site files, links, and removal of the default site
test -f /etc/nginx/sites-available/test.cluster.local
test -f /etc/nginx/sites-available/ci.cluster.local
test -f /etc/nginx/sites-available/status.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Verify test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
test -d /opt/server/test
test -f /opt/server/test/index.html
stat -c '%U:%G %a %n' /opt/server/test/index.html
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

# Verify ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
test -d /opt/server/ci
test -f /opt/server/ci/index.html
stat -c '%U:%G %a %n' /opt/server/ci/index.html
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

# Verify status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
test -d /opt/server/status
test -f /opt/server/status/index.html
stat -c '%U:%G %a %n' /opt/server/status/index.html
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# Verify listeners
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Verify UFW
ufw status verbose
ufw status numbered | grep '22/tcp'
ufw status numbered | grep '80/tcp'
ufw status numbered | grep '443/tcp'

# Verify SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
systemctl is-active ssh

# Verify security configuration
cat /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies

# Verify Fail2ban jails
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Verify nginx and site logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
```

Expected results include:

- Each HTTP endpoint returns `301 Moved Permanently` with an HTTPS location.
- Each HTTPS endpoint returns `200 OK` and serves its correct document root.
- Index files are owned by `www-data:www-data` with mode `0644`.
- Each certificate is self-signed, uses the correct site name, has an RSA 2048-bit key, and is valid for approximately 365 days.
- Each private key is owned by `root:ssl-cert` with mode `0640`.
- nginx listens on ports `80` and `443`.
- UFW is active with default incoming policy `deny` and rules for SSH, HTTP, and HTTPS.
- SSH contains `PermitRootLogin no` and `PasswordAuthentication no`.
- Fail2ban, nginx, and all four expected jails are active and configured.