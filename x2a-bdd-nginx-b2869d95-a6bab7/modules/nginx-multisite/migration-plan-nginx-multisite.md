---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and index files; generates self-signed certificates; configures HTTP-to-HTTPS redirects, TLS, HTTP/2, security headers, rate limiting, and filesystem protections; and applies SSH, firewall, sysctl, and fail2ban hardening. The Ansible implementation must preserve the recipe order, idempotent resource behavior, delayed notifications, and all three site definitions.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; logs `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; logs `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; logs `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`

Security defaults:

- `security.fail2ban.enabled`: `true`
- `security.ufw.enabled`: `true`
- `security.ssh.disable_root`: `true`
- `security.ssh.password_auth`: `false`

SSL defaults:

- Certificate directory: `/etc/ssl/certs`
- Private-key directory: `/etc/ssl/private`

## File Structure

The following files are used by the migration. Paths are relative to `cookbooks/nginx-multisite`.

### Recipes

```text
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

### Providers

```text
```

No provider files are included in the supplied directory listing.

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

No static files under `files/default/` or `files/` are included in the supplied directory listing. The recipes reference these dynamic `cookbook_file` sources:

```text
test/index.html
ci/index.html
status/index.html
```

These files must be supplied to the Ansible migration as equivalent static files if they exist in the source cookbook repository.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)
2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)
3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

### 1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- The Ansible role must preserve this execution sequence through task files or role dependencies.

### 2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts `service[fail2ban]`.
- Renders `templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configures fail2ban with:
  - Ban time `3600` seconds.
  - Find time `600` seconds.
  - Maximum retries `3`.
  - Backend `auto`.
  - SSH jail on `ssh`.
  - nginx HTTP authentication jail on `http,https`.
  - nginx request-rate jail on `http,https`.
  - nginx bot-search jail on `http,https`.
  - Authentication and nginx log paths defined by the template.
- Delayed-restarts fail2ban when its template changes.
- Applies UFW rules in this order:
  1. Set the default incoming policy to deny.
  2. Allow SSH, TCP `22`.
  3. Allow HTTP, TCP `80`.
  4. Allow HTTPS, TCP `443`.
  5. Enable UFW.
- The UFW operations are idempotent and should use `community.general.ufw` where available.
- Renders `templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Configures reverse-path filtering, ICMP redirect handling, source-routing protection, martian packet logging, ICMP protections, IPv6 disabling, TCP SYN cookies, TCP backlog, and retry settings.
- Defines `execute[reload_sysctl]` with action `nothing`; a changed sysctl template triggers a delayed execution of:
  ```bash
  sysctl -p /etc/sysctl.d/99-security.conf
  ```
- Because `security.ssh.disable_root` is `true`, enforces:
  ```text
  PermitRootLogin no
  ```
  in `/etc/ssh/sshd_config`.
- Because `security.ssh.password_auth` is `false`, enforces:
  ```text
  PasswordAuthentication no
  ```
  in `/etc/ssh/sshd_config`.
- A change to either SSH setting triggers a delayed restart of `sshd`.
- `service[sshd]` has action `nothing` and is restarted only through notifications.
- Delayed notifications are preserved:
  - Fail2ban template change → fail2ban restart.
  - Sysctl template change → sysctl reload.
  - Root-login change → sshd restart.
  - Password-authentication change → sshd restart.

### 3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package.
- Renders `templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Configures:
  - Worker user `nginx`.
  - Worker processes `auto`.
  - PID file `/run/nginx.pid`.
  - Worker connections `768`.
  - Keepalive timeout `65`.
  - Access log `/var/log/nginx/access.log`.
  - Error log `/var/log/nginx/error.log`.
  - Gzip.
  - `/etc/nginx/conf.d/*.conf`.
  - `/etc/nginx/sites-enabled/*`.
- A changed main configuration triggers a delayed nginx reload.
- Renders `templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Configures:
  - `server_tokens off`.
  - Login rate limit `10r/m`.
  - API rate limit `30r/m`.
  - Maximum request body size `1k`.
  - Client-header, client-body, and send timeouts of `10`.
  - TLS `TLSv1.2 TLSv1.3`.
  - The configured ECDHE/DHE cipher suite.
  - SSL session cache `shared:SSL:10m`.
  - SSL session timeout `10m`.
- A changed security configuration triggers a delayed nginx reload.
- Enables and starts `service[nginx]`; restart, reload, and status actions remain supported.
- Creates these document roots with owner `nginx`, group `nginx`, mode `0755`, and recursive creation:
  - `/opt/server/test`
  - `/opt/server/ci`
  - `/opt/server/status`
- Deploys these index files with owner `nginx`, group `nginx`, and mode `0644`:
  - `test/index.html` → `/opt/server/test/index.html`
  - `ci/index.html` → `/opt/server/ci/index.html`
  - `status/index.html` → `/opt/server/status/index.html`
- The source directory is derived from the first DNS label:
  - `test.cluster.local` → `test/index.html`
  - `ci.cluster.local` → `ci/index.html`
  - `status.cluster.local` → `status/index.html`
- Iterations:
  - `directory`: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`.
  - `cookbook_file`: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`.

### 4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs `openssl` and `ca-certificates`.
- Creates group `ssl-cert`.
- Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
- Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
- Generates self-signed RSA 2048-bit certificates valid for `365` days when the corresponding certificate and key do not already exist.
- Uses subject fields:
  ```text
  /C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site>/emailAddress=admin@example.com
  ```
- Sets each private key to mode `0640` and owner `root:ssl-cert`.
- A certificate-generation change triggers a delayed nginx reload.
- Iterations:
  - **test.cluster.local**
    - Key: `/etc/ssl/private/test.cluster.local.key`
    - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
    - Common name: `test.cluster.local`
  - **ci.cluster.local**
    - Key: `/etc/ssl/private/ci.cluster.local.key`
    - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
    - Common name: `ci.cluster.local`
  - **status.cluster.local**
    - Key: `/etc/ssl/private/status.cluster.local.key`
    - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
    - Common name: `status.cluster.local`

### 5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
- Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
- Renders `templates/default/site.conf.erb` three times:
  - **test.cluster.local**
    - Destination: `/etc/nginx/sites-available/test.cluster.local`
    - Document root: `/opt/server/test`
    - SSL enabled: `true`
    - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
    - Key: `/etc/ssl/private/test.cluster.local.key`
  - **ci.cluster.local**
    - Destination: `/etc/nginx/sites-available/ci.cluster.local`
    - Document root: `/opt/server/ci`
    - SSL enabled: `true`
    - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
    - Key: `/etc/ssl/private/ci.cluster.local.key`
  - **status.cluster.local**
    - Destination: `/etc/nginx/sites-available/status.cluster.local`
    - Document root: `/opt/server/status`
    - SSL enabled: `true`
    - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
    - Key: `/etc/ssl/private/status.cluster.local.key`
- Creates these symbolic links:
  - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
- Deletes `/etc/nginx/sites-enabled/default`.
- Each site template change, symbolic-link change, or default-site deletion triggers a delayed nginx reload.
- Each virtual host contains:
  - HTTP listener on port `80`.
  - HTTP-to-HTTPS redirect.
  - HTTPS listener on port `443` with HTTP/2.
  - Site-specific document root.
  - Site-specific certificate and private key.
  - TLS 1.2 and TLS 1.3.
  - One-year HSTS with subdomain inclusion.
  - `X-Frame-Options: DENY`.
  - `X-Content-Type-Options: nosniff`.
  - `X-XSS-Protection`.
  - `Referrer-Policy`.
  - Content-Security-Policy.
  - Gzip compression.
  - Static-file resolution with `try_files`.
  - Denial of `.htaccess`, `.git`, and `.svn` paths.
  - Site-specific access and error logs.
- Iterations:
  - `template`: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`.
  - `link`: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`.

## Dependencies

**External cookbook dependencies**: None specified in the supplied metadata.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `sshd`: restarted only when SSH hardening changes.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Network dependencies**:

- TCP `22`: SSH, allowed by UFW.
- TCP `80`: HTTP and redirect listeners, allowed by UFW.
- TCP `443`: HTTPS and HTTP/2 listeners, allowed by UFW.

## Credentials

**Detection Summary**: No application credentials, data bags, vault integrations, API keys, database passwords, or external secret-manager references were detected. Three locally generated TLS private keys and one non-secret certificate subject email were identified.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### Self-signed TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; not stored in Chef Vault, a data bag, an environment variable, or an external secret manager.
- **Usage context**: nginx TLS private keys.
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`.

### TLS certificate subject email

- **Variable**: `admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL subject string.
- **Usage context**: Subject email field in the three self-signed development certificates.
- **Credential status**: Identifying certificate metadata, not an authentication secret.

No ERB environment-variable references such as `ENV['...']` were detected.

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
/opt/server/test/index.html
/opt/server/ci/index.html
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
```

The following file must be absent:

```text
/etc/nginx/sites-enabled/default
```

**Service endpoints to check**:

- `test.cluster.local`: HTTP TCP `80`; HTTPS TCP `443`
- `ci.cluster.local`: HTTP TCP `80`; HTTPS TCP `443`
- `status.cluster.local`: HTTP TCP `80`; HTTPS TCP `443`

**Unix sockets**: None configured or referenced.

**Templates rendered**:

- `fail2ban.jail.local.erb`: once → `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once → `/etc/nginx/nginx.conf`
- `security.conf.erb`: once → `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once → `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Security services
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Firewall
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
systemctl status sshd

# nginx service and syntax
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'

# Listening ports
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Main configuration
grep -E 'user nginx|worker_processes auto|worker_connections 768|keepalive_timeout 65' /etc/nginx/nginx.conf
grep -E 'server_tokens off|TLSv1.2 TLSv1.3|client_max_body_size 1k|limit_req_zone' /etc/nginx/conf.d/security.conf

# Site links and default-site removal
test ! -e /etc/nginx/sites-enabled/default
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

# Logs
journalctl -u nginx --since "-15 minutes"
journalctl -u fail2ban --since "-15 minutes"
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
```

Expected symbolic-link targets:

```text
/etc/nginx/sites-enabled/test.cluster.local
→ /etc/nginx/sites-available/test.cluster.local

/etc/nginx/sites-enabled/ci.cluster.local
→ /etc/nginx/sites-available/ci.cluster.local

/etc/nginx/sites-enabled/status.cluster.local
→ /etc/nginx/sites-available/status.cluster.local
```

Expected nginx syntax result:

```text
syntax is ok
test is successful
```

### test.cluster.local

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

test -d /opt/server/test
test -f /opt/server/test/index.html
ls -ld /opt/server/test
ls -l /opt/server/test/index.html

test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
```

Expected results:

- HTTP returns `301` to `https://test.cluster.local/...`.
- HTTPS normally returns `200`.
- The certificate subject includes `CN=test.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.

### ci.cluster.local

```bash
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

test -d /opt/server/ci
test -f /opt/server/ci/index.html
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html

test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
```

Expected results:

- HTTP returns `301` to `https://ci.cluster.local/...`.
- HTTPS normally returns `200`.
- The certificate subject includes `CN=ci.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.

### status.cluster.local

```bash
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

test -d /opt/server/status
test -f /opt/server/status/index.html
ls -ld /opt/server/status
ls -l /opt/server/status/index.html

test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
```

Expected results:

- HTTP returns `301` to `https://status.cluster.local/...`.
- HTTPS normally returns `200`.
- The certificate subject includes `CN=status.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.

The Ansible implementation must preserve delayed nginx reload behavior for certificate creation, main nginx configuration changes, security configuration changes, virtual-host template changes, symbolic-link changes, and removal of the default site. Configuration changes should reload nginx rather than unnecessarily restarting it.