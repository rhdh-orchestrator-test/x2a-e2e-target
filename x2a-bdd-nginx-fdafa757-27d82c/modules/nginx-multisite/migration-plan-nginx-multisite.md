---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a web server for three SSL-enabled sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts nginx, creates document roots and placeholder index files, generates self-signed certificates, configures HTTP-to-HTTPS redirects and security headers, deploys fail2ban and UFW protections, applies kernel security parameters, and disables SSH root login and password authentication.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/test`
  - HTTP port: `80`
  - HTTPS port: `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/ci`
  - HTTP port: `80`
  - HTTPS port: `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/status`
  - HTTP port: `80`
  - HTTPS port: `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`

**Security services and settings**:

- **fail2ban**
  - Enabled: `true`
  - Service: `fail2ban`
- **ufw**
  - Enabled: `true`
  - Default policy: deny
  - Allowed services: SSH, HTTP, HTTPS
- **ssh**
  - Root login disabled: `true`
  - Password authentication disabled: `true`

## File Structure

The following files are used by the cookbook according to the execution tree and structured analysis.

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

No provider files are used by the executed recipe flow.

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

No static file paths were provided in the supplied directory listing. The nginx recipe deploys `index.html` using `cookbook_file`, but its source path is dynamically constructed as `#{site_folder}/index.html`, and no corresponding static file path is listed.

## Module Explanation

The cookbook performs operations in this order:

1. `cookbooks/nginx-multisite/recipes/default.rb`
2. `cookbooks/nginx-multisite/recipes/security.rb`
3. `cookbooks/nginx-multisite/recipes/nginx.rb`
4. `cookbooks/nginx-multisite/recipes/ssl.rb`
5. `cookbooks/nginx-multisite/recipes/sites.rb`

### 1. Default recipe (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- Preserves the dependency order of security configuration, nginx installation, certificate generation, and site deployment.

### 2. Security recipe (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs the `fail2ban` and `ufw` packages through one package resource.
- Enables and starts the `fail2ban` service.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configures fail2ban with:
  - Ban time: `3600`
  - Find time: `600`
  - Maximum retries: `3`
  - Backend: `auto`
- Enables these fail2ban jails:
  - `sshd`: port `ssh`, log `/var/log/auth.log`, maximum retries `3`
  - `nginx-http-auth`: ports `http,https`, log `/var/log/nginx/*error.log`, maximum retries `3`
  - `nginx-limit-req`: ports `http,https`, log `/var/log/nginx/*error.log`, maximum retries `10`
  - `nginx-botsearch`: ports `http,https`, log `/var/log/nginx/*access.log`, maximum retries `2`
- Executes UFW commands in order:
  1. `ufw --force default deny`
  2. `ufw allow ssh`
  3. `ufw allow http`
  4. `ufw allow https`
  5. `ufw --force enable`
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Configures reverse-path filtering, redirect and source-route protections, martian packet logging, ICMP hardening, IPv6 disabling, TCP SYN cookies, and these TCP values:
  - `net.ipv4.tcp_max_syn_backlog = 2048`
  - `net.ipv4.tcp_synack_retries = 2`
  - `net.ipv4.tcp_syn_retries = 5`
- Defines `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`. The execution tree does not show a notification or subscription invoking it; the Ansible migration must explicitly decide whether to run this command or `sysctl --system` when the file changes.
- Replaces the SSH settings with:
  - `PermitRootLogin no`
  - `PasswordAuthentication no`
- Declares the `ssh` service with action `nothing`. No SSH restart or reload is shown in the execution tree. Key-based administrative access must be verified before disabling password authentication.
- Contains eight execute resources:
  - `ufw_default_deny`
  - `ufw_allow_ssh`
  - `ufw_allow_http`
  - `ufw_allow_https`
  - `ufw_enable`
  - `reload_sysctl`
  - Disable root login
  - Disable password authentication

### 3. Nginx installation and base configuration (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Configures:
  - Worker user: `www-data`
  - Worker processes: `auto`
  - PID file: `/run/nginx.pid`
  - Worker connections: `768`
  - Access log: `/var/log/nginx/access.log`
  - Error log: `/var/log/nginx/error.log`
  - Keepalive timeout: `65`
  - Gzip: enabled
  - Modules: `/etc/nginx/modules-enabled/*.conf`
  - MIME types: `/etc/nginx/mime.types`
  - Additional configuration: `/etc/nginx/conf.d/*.conf`
  - Enabled sites: `/etc/nginx/sites-enabled/*`
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Configures nginx version hiding, rate limiting, request buffers, request size limits, timeouts, TLS 1.2, TLS 1.3, the configured cipher list, and preferred server ciphers.
- Enables and starts the `nginx` service.
- Creates the following document roots with mode `0755`:
  - `/opt/server/test` for `test.cluster.local`
  - `/opt/server/ci` for `ci.cluster.local`
  - `/opt/server/status` for `status.cluster.local`
- Deploys the following placeholder index files with mode `0644`:
  - `/opt/server/test/index.html`
  - `/opt/server/ci/index.html`
  - `/opt/server/status/index.html`
- Uses dynamically constructed `cookbook_file` source paths of `#{site_folder}/index.html`.
- Does not include a confirmed `www-data` group resource; the supplied execution tree contains only the nginx package, two templates, service, three directories, and three cookbook files.

### 4. SSL certificate setup (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs the `openssl` and `ca-certificates` packages.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` with mode `0755`.
- Creates `/etc/ssl/private` with mode `0710`, owned by `root:ssl-cert`.
- Generates a self-signed RSA 2048-bit certificate and non-encrypted private key for `test.cluster.local`:
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Key: `/etc/ssl/private/test.cluster.local.key`
  - Common name: `test.cluster.local`
  - Validity: `365` days
  - Key mode: `0640`
  - Key owner/group: `root:ssl-cert`
- Generates a self-signed RSA 2048-bit certificate and non-encrypted private key for `ci.cluster.local`:
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Key: `/etc/ssl/private/ci.cluster.local.key`
  - Common name: `ci.cluster.local`
  - Validity: `365` days
  - Key mode: `0640`
  - Key owner/group: `root:ssl-cert`
- Generates a self-signed RSA 2048-bit certificate and non-encrypted private key for `status.cluster.local`:
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Key: `/etc/ssl/private/status.cluster.local.key`
  - Common name: `status.cluster.local`
  - Validity: `365` days
  - Key mode: `0640`
  - Key owner/group: `root:ssl-cert`
- Uses this certificate subject format:
  ```text
  /C=US/ST=Example/L=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com
  ```
- Uses `openssl req -x509` to generate self-signed certificates.

### 5. Nginx site configuration (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with variables:
  - `server_name`: `test.cluster.local`
  - `document_root`: `/opt/server/test`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/test.cluster.local.key`
- Creates `/etc/nginx/sites-enabled/test.cluster.local` as a link to `/etc/nginx/sites-available/test.cluster.local`.
- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with variables:
  - `server_name`: `ci.cluster.local`
  - `document_root`: `/opt/server/ci`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
- Creates `/etc/nginx/sites-enabled/ci.cluster.local` as a link to `/etc/nginx/sites-available/ci.cluster.local`.
- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with variables:
  - `server_name`: `status.cluster.local`
  - `document_root`: `/opt/server/status`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/status.cluster.local.key`
- Creates `/etc/nginx/sites-enabled/status.cluster.local` as a link to `/etc/nginx/sites-available/status.cluster.local`.
- Deletes `/etc/nginx/sites-enabled/default`.
- Configures each site with:
  - HTTP listener on port `80`
  - HTTP-to-HTTPS redirect
  - HTTPS listener on port `443` with HTTP/2
  - Site-specific document root, certificates, keys, and logs
  - TLS 1.2 and TLS 1.3
  - One-year HSTS including subdomains
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - Content Security Policy
  - Gzip compression
  - `try_files $uri $uri/ =404`
  - Access restrictions for `.htaccess`, `.git`, and `.svn`

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `nginx`: enabled and started
- `fail2ban`: enabled and started
- `ssh`: declared with action `nothing`; no restart or reload is shown

**Operating system support**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The UFW commands are Ubuntu-oriented. A CentOS migration requires an explicit decision about firewall implementation because UFW is not the native firewall tool on that platform.

## Credentials

**Detection Summary**: No passwords, API tokens, data bags, Chef Vault items, CyberArk references, Conjur variables, or secret environment variables were detected. Three locally generated TLS private keys were identified; they are not retrieved from a secret manager.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### Generated TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files; not stored in a data bag, vault, or secret manager
- **Usage context**: nginx TLS private keys
- **Protection**: Mode `0640`, owner `root`, group `ssl-cert`

### Certificate subject email

- **Variable**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded non-secret certificate subject value
- **Usage context**: Email address in the self-signed certificate subject
- **Sensitive data**: Not a password, token, or authentication credential

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
- `/etc/nginx/sites-enabled/default` is absent
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
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`

**Service endpoints to check**:

- `test.cluster.local`: TCP ports `80` and `443`
- `ci.cluster.local`: TCP ports `80` and `443`
- `status.cluster.local`: TCP ports `80` and `443`
- SSH firewall access: TCP port `22`

**Unix sockets**: None configured.

**Network interfaces**: No explicit bind address is configured. nginx listens on all available interfaces through `listen 80` and `listen 443 ssl http2`.

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`
- `sysctl-security.conf.erb`: 1 render

## Pre-flight checks

```bash
# Verify service state
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Validate nginx configuration
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'

# Verify listeners
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Verify firewall policy
ufw status verbose
ufw status numbered

# Verify security configuration
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols' \
  /etc/nginx/conf.d/security.conf
grep -E 'rp_filter|accept_redirects|accept_source_route|log_martians|disable_ipv6|tcp_syncookies' \
  /etc/sysctl.d/99-security.conf
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config

# Verify fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
```

Expected results:

- nginx and fail2ban are active and enabled.
- `nginx -t` succeeds.
- All three server names appear in the expanded nginx configuration.
- nginx listens on TCP ports `80` and `443`.
- UFW denies unsolicited inbound traffic while allowing SSH, HTTP, and HTTPS.
- `PermitRootLogin no` and `PasswordAuthentication no` are present.
- All four fail2ban jails are enabled and operational.

### test.cluster.local

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head

test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%a %U:%G' /etc/ssl/private/test.cluster.local.key
```

Expected results:

- HTTP returns `301`.
- HTTPS returns a successful response, normally `200`.
- Security headers are present.
- The response body is served from `/opt/server/test/index.html`.
- The private key reports `640 root:ssl-cert`.

### ci.cluster.local

```bash
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head

test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%a %U:%G' /etc/ssl/private/ci.cluster.local.key
```

Expected results:

- HTTP returns `301`.
- HTTPS returns a successful response, normally `200`.
- Security headers are present.
- The response body is served from `/opt/server/ci/index.html`.
- The private key reports `640 root:ssl-cert`.

### status.cluster.local

```bash
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head

test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%a %U:%G' /etc/ssl/private/status.cluster.local.key
```

Expected results:

- HTTP returns `301`.
- HTTPS returns a successful response, normally `200`.
- Security headers are present.
- The response body is served from `/opt/server/status/index.html`.
- The private key reports `640 root:ssl-cert`.

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
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

Expected results:

- nginx starts without configuration errors.
- Requests to `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` appear in their respective access logs.
- No recurring certificate, permission, or upstream errors appear in the nginx error logs.