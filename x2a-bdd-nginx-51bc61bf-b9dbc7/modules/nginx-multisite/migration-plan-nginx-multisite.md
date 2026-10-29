---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies kernel and SSH hardening; creates self-signed 2048-bit certificates; deploys static site content; and enables HTTP-to-HTTPS virtual hosts with HTTP/2 on port 443.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **test.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

**Security configuration**:

- **fail2ban**: Enabled and started; jails are `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch`
- **ufw**: Enabled with a default deny policy; SSH, HTTP, and HTTPS are allowed
- **ssh**: Root login disabled; password authentication disabled

## File Structure

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── recipes/
│   ├── default.rb
│   ├── nginx.rb
│   ├── security.rb
│   ├── sites.rb
│   └── ssl.rb
├── resources/
│   └── [none identified]
└── templates/
    └── default/
        ├── fail2ban.jail.local.erb
        ├── nginx.conf.erb
        ├── security.conf.erb
        ├── site.conf.erb
        └── sysctl-security.conf.erb
```

No provider files or custom resources were identified in the supplied structured analysis.

No static files are included in the supplied directory listing. The recipe references these dynamic `cookbook_file` sources, whose physical source paths must be verified separately:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. `cookbooks/nginx-multisite/recipes/default.rb`
2. `cookbooks/nginx-multisite/recipes/security.rb`
3. `cookbooks/nginx-multisite/recipes/nginx.rb`
4. `cookbooks/nginx-multisite/recipes/ssl.rb`
5. `cookbooks/nginx-multisite/recipes/sites.rb`

### 1. Default recipe

**Recipe**: `cookbooks/nginx-multisite/recipes/default.rb`

- Includes `nginx-multisite::security`
- Includes `nginx-multisite::nginx`
- Includes `nginx-multisite::ssl`
- Includes `nginx-multisite::sites`
- Resources: four `include_recipe` declarations
- Ansible task ordering must remain security, Nginx, SSL, and site activation.

### 2. Security configuration

**Recipe**: `cookbooks/nginx-multisite/recipes/security.rb`

- Installs `fail2ban` and `ufw`.
- Enables and starts `fail2ban`.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configures Fail2ban defaults:
  - Ban time: `3600`
  - Find time: `600`
  - Maximum retries: `3`
  - Backend: `auto`
- Configures the `sshd` jail:
  - Port: `ssh`
  - Log path: `/var/log/auth.log`
  - Ban time: `3600`
  - Maximum retries: `3`
- Configures the `nginx-http-auth` jail:
  - Filter: `nginx-http-auth`
  - Ports: `http,https`
  - Log path: `/var/log/nginx/*error.log`
  - Ban time: `3600`
  - Maximum retries: `3`
- Configures the `nginx-limit-req` jail:
  - Filter: `nginx-limit-req`
  - Ports: `http,https`
  - Log path: `/var/log/nginx/*error.log`
  - Ban time: `3600`
  - Maximum retries: `10`
- Configures the `nginx-botsearch` jail:
  - Filter: `nginx-botsearch`
  - Ports: `http,https`
  - Log path: `/var/log/nginx/*access.log`
  - Ban time: `3600`
  - Maximum retries: `2`
- A change to `jail.local` causes a delayed Fail2ban restart.
- Sets the UFW default inbound policy to deny.
- Allows SSH on port `22`, HTTP on port `80`, and HTTPS on port `443`.
- Enables UFW.
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Configures reverse-path filtering, redirect protection, source-routing protection, martian logging, ICMP protection, IPv6 disabling, and TCP SYN flood protection:
  - `net.ipv4.conf.default.rp_filter = 1`
  - `net.ipv4.conf.all.rp_filter = 1`
  - Redirect acceptance disabled for IPv4 and IPv6
  - Source routing disabled for IPv4 and IPv6
  - Martian packet logging enabled
  - ICMP echo requests ignored
  - Broadcast ping protection enabled
  - IPv6 disabled on `net.ipv6.conf.all`, `net.ipv6.conf.default`, and `net.ipv6.conf.lo`
  - `net.ipv4.tcp_syncookies = 1`
  - `net.ipv4.tcp_max_syn_backlog = 2048`
  - `net.ipv4.tcp_synack_retries = 2`
  - `net.ipv4.tcp_syn_retries = 5`
- A change to the sysctl template causes a delayed execution of:
  ```bash
  sysctl -p /etc/sysctl.d/99-security.conf
  ```
- Sets `/etc/ssh/sshd_config` to `PermitRootLogin no`.
- Sets `/etc/ssh/sshd_config` to `PasswordAuthentication no`.
- A change to either SSH setting causes a delayed SSH service restart.
- The SSH service is declared with an initial action of `nothing`.

**Resources**:

- `package`: one declaration installing two packages
- `service`: `fail2ban` and `ssh`
- `template`: two templates
- `execute`: six unconditional commands:
  - `ufw_default_deny`
  - `ufw_allow_ssh`
  - `ufw_allow_http`
  - `ufw_allow_https`
  - `ufw_enable`
  - `reload_sysctl`
- `execute`: two conditional SSH commands:
  - `disable root login`
  - `disable password auth`
- Total execute resources with the default attributes enabled: `8`

### 3. Nginx installation and base configuration

**Recipe**: `cookbooks/nginx-multisite/recipes/nginx.rb`

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Configures:
  - Worker user: `www-data`
  - Worker processes: `auto`
  - PID file: `/run/nginx.pid`
  - Worker connections: `768`
  - Access log: `/var/log/nginx/access.log`
  - Error log: `/var/log/nginx/error.log`
  - `sendfile on`
  - `tcp_nopush on`
  - `tcp_nodelay on`
  - Keepalive timeout: `65`
  - Gzip enabled
  - Module include: `/etc/nginx/modules-enabled/*.conf`
  - Configuration include: `/etc/nginx/conf.d/*.conf`
  - Site include: `/etc/nginx/sites-enabled/*`
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Configures Nginx version hiding, request-rate zones, request buffer limits, request timeouts, TLS session settings, TLS `1.2` and `1.3`, an explicit ECDHE/DHE cipher list, and server cipher preference.
- A change to either Nginx template causes a delayed Nginx reload.
- Enables and starts the `nginx` service.

**Expanded site iterations**:

- **test.cluster.local**
  - Creates `/opt/server/test` recursively with owner `www-data`, group `www-data`, and mode `0755`.
  - Deploys `test/index.html` to `/opt/server/test/index.html` with owner `www-data`, group `www-data`, and mode `0644`.

- **ci.cluster.local**
  - Creates `/opt/server/ci` recursively with owner `www-data`, group `www-data`, and mode `0755`.
  - Deploys `ci/index.html` to `/opt/server/ci/index.html` with owner `www-data`, group `www-data`, and mode `0644`.

- **status.cluster.local**
  - Creates `/opt/server/status` recursively with owner `www-data`, group `www-data`, and mode `0755`.
  - Deploys `status/index.html` to `/opt/server/status/index.html` with owner `www-data`, group `www-data`, and mode `0644`.

No separate `www-data` group-management task is required based on the supplied execution tree.

### 4. SSL package and certificate setup

**Recipe**: `cookbooks/nginx-multisite/recipes/ssl.rb`

- Installs `openssl` and `ca-certificates`.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
- Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
- Generates certificates only when the corresponding certificate and key do not already exist.
- Certificate generation uses a 2048-bit RSA key, 365-day validity, and a self-signed X.509 certificate.
- All certificates use the subject components:
  - Country: `US`
  - State: `Example`
  - Locality: `Example`
  - Organization: `Example Org`
  - Organizational unit: `IT`
  - Email: `admin@example.com`

**Expanded SSL iterations**:

- **test.cluster.local**
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Common name: `test.cluster.local`
  - Key mode: `0640`
  - Key ownership: `root:ssl-cert`

- **ci.cluster.local**
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Common name: `ci.cluster.local`
  - Key mode: `0640`
  - Key ownership: `root:ssl-cert`

- **status.cluster.local**
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Common name: `status.cluster.local`
  - Key mode: `0640`
  - Key ownership: `root:ssl-cert`

A newly generated certificate causes a delayed Nginx reload. The recipe contains three possible certificate-generation commands and three possible delayed reload notifications.

### 5. Virtual-host configuration and activation

**Recipe**: `cookbooks/nginx-multisite/recipes/sites.rb`

The recipe renders `cookbooks/nginx-multisite/templates/default/site.conf.erb`, creates site links, and removes the default site.

**Expanded site iterations**:

- **test.cluster.local**
  - Renders to `/etc/nginx/sites-available/test.cluster.local`.
  - Document root: `/opt/server/test`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.

- **ci.cluster.local**
  - Renders to `/etc/nginx/sites-available/ci.cluster.local`.
  - Document root: `/opt/server/ci`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.

- **status.cluster.local**
  - Renders to `/etc/nginx/sites-available/status.cluster.local`.
  - Document root: `/opt/server/status`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.

Each virtual host contains:

- HTTP server block on port `80`
- Redirect from HTTP to HTTPS
- HTTPS server block on port `443`
- HTTP/2 enabled on HTTPS
- Site-specific document root, certificate, and private key
- One-year HSTS header
- `X-Frame-Options DENY`
- `X-Content-Type-Options nosniff`
- `X-XSS-Protection`
- `Referrer-Policy`
- Content Security Policy
- Gzip compression
- `try_files $uri $uri/ =404`
- Denial of `.htaccess`, `.git`, and `.svn` paths
- Site-specific access and error logs

The site-specific logs are:

- `test.cluster.local`: `/var/log/nginx/test.cluster.local_access.log` and `/var/log/nginx/test.cluster.local_error.log`
- `ci.cluster.local`: `/var/log/nginx/ci.cluster.local_access.log` and `/var/log/nginx/ci.cluster.local_error.log`
- `status.cluster.local`: `/var/log/nginx/status.cluster.local_access.log` and `/var/log/nginx/status.cluster.local_error.log`

The recipe deletes `/etc/nginx/sites-enabled/default`. Changes to site templates, links, or default-site removal cause a delayed Nginx reload.

**Resources**:

- `template`: three renders
- `link`: three links
- `file`: one default-site deletion

## Dependencies

**External cookbook dependencies**: None identified.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: Enabled and started; restarted when `/etc/fail2ban/jail.local` changes
- `nginx`: Enabled and started; reloaded when Nginx configuration, certificates, virtual-host files, links, or default-site removal changes
- `ssh`: Restarted when either SSH hardening setting changes

## Credentials

**Detection Summary**: No application credentials or externally supplied secrets detected. Three generated TLS private keys and three generated self-signed certificates are present as locally generated security artifacts.

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
- **Current storage**: Generated locally by `openssl req`
- **Usage context**: Nginx HTTPS private keys
- **Permissions**: Directory mode `0710`; key mode `0640`; ownership `root:ssl-cert`

### Self-signed TLS certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed X.509 certificates
- **Usage context**: Nginx HTTPS certificate files

No data bags, Chef Vault items, Conjur variables, Vault attributes, secret-manager URLs, environment-variable secrets, passwords, API tokens, or database credentials were detected. The `admin@example.com` certificate subject value is not an authentication credential.

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
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
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

- `test.cluster.local`: HTTP `80` returns `301`; HTTPS `443` returns `200`
- `ci.cluster.local`: HTTP `80` returns `301`; HTTPS `443` returns `200`
- `status.cluster.local`: HTTP `80` returns `301`; HTTPS `443` returns `200`
- SSH: port `22` remains reachable before UFW is enabled

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb`: 3 total renders

## Pre-flight checks

```bash
# Package status
dpkg-query -W nginx fail2ban ufw openssl ca-certificates

# Use this command on RPM-based systems
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh

# Nginx syntax and loaded virtual hosts
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'

# Main and security configuration
grep -E 'user www-data|worker_processes auto|worker_connections 768|gzip on' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens off|limit_req_zone|client_max_body_size|TLSv1.2|TLSv1.3' \
  /etc/nginx/conf.d/security.conf

# test.cluster.local
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
ls -l /etc/ssl/certs/test.cluster.local.crt
ls -l /etc/ssl/private/test.cluster.local.key
ls -l /etc/nginx/sites-available/test.cluster.local
ls -l /etc/nginx/sites-enabled/test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
curl -I --resolve test.cluster.local:80:127.0.0.1 http://test.cluster.local/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# ci.cluster.local
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
ls -l /etc/ssl/certs/ci.cluster.local.crt
ls -l /etc/ssl/private/ci.cluster.local.key
ls -l /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
curl -I --resolve ci.cluster.local:80:127.0.0.1 http://ci.cluster.local/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# status.cluster.local
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
ls -l /etc/ssl/certs/status.cluster.local.crt
ls -l /etc/ssl/private/status.cluster.local.key
ls -l /etc/nginx/sites-available/status.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
curl -I --resolve status.cluster.local:80:127.0.0.1 http://status.cluster.local/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# UFW
ufw status verbose

# SSH hardening
grep -E '^PermitRootLogin no$|^PasswordAuthentication no$' /etc/ssh/sshd_config

# Kernel hardening
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# Listening services
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
```

Expected results include:

- `nginx -t`: syntax is valid and the test is successful
- HTTP requests for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`: HTTP `301` with HTTPS `Location` headers
- HTTPS requests for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`: HTTP `200`
- UFW: default deny, SSH/HTTP/HTTPS allowed, status active
- SSH configuration: `PermitRootLogin no` and `PasswordAuthentication no`
- `net.ipv4.conf.default.rp_filter = 1`
- `net.ipv4.conf.all.rp_filter = 1`
- `net.ipv4.conf.all.accept_redirects = 0`
- `net.ipv6.conf.all.disable_ipv6 = 1`
- `net.ipv4.tcp_syncookies = 1`
- `net.ipv4.tcp_max_syn_backlog = 2048`