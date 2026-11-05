---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, OpenSSL, CA certificates, Fail2ban, and UFW; applies SSH and sysctl hardening; generates self-signed TLS certificates; deploys static site content; enables HTTP-to-HTTPS redirects; and configures nginx security settings, TLS, headers, rate limits, and per-site logs. The execution order is security, nginx installation, SSL setup, and virtual-host configuration.

## Service Type and Instances

**Service Type**: Web Server

The cookbook also manages host security controls through Fail2ban, UFW, sysctl, and SSH configuration.

**Configured Instances**:

- **test.cluster.local**: Static nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`
  - Index file: `/opt/server/test/index.html`

- **ci.cluster.local**: Static nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`
  - Index file: `/opt/server/ci/index.html`

- **status.cluster.local**: Static nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`
  - Index file: `/opt/server/status/index.html`

**Security services and settings**:

- **fail2ban**
  - Enabled and started
  - Configuration: `/etc/fail2ban/jail.local`

- **ufw**
  - Enabled
  - Default policy: deny
  - Allowed services: SSH, HTTP, and HTTPS

- **ssh**
  - Root login disabled
  - Password authentication disabled
  - Service is declared for notification-based restart but is not enabled or started by this cookbook

**Platform and dependency metadata**: The supplied validation does not include `metadata.rb` analysis. Ubuntu `>= 18.04`, CentOS `>= 7.0`, and the absence of external cookbook dependencies require verification against `metadata.rb`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
    └── [directory listing not supplied; cookbook_file sources are test/index.html, ci/index.html, and status/index.html]
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

No provider files or executed custom resources are present in the execution tree.

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

The supplied directory listing does not include a `files/` directory or static file paths, although the recipes deploy `test/index.html`, `ci/index.html`, and `status/index.html` with `cookbook_file` resources.

## Module Explanation

The cookbook performs operations in this order, as defined by `cookbooks/nginx-multisite/recipes/default.rb`:

1. `nginx-multisite::security`
2. `nginx-multisite::nginx`
3. `nginx-multisite::ssl`
4. `nginx-multisite::sites`

The Ansible implementation should preserve this order using task files or role imports.

1. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban defaults: ban time `3600`, find time `600`, max retries `3`, and backend `auto`.
   - Configures SSH, nginx HTTP authentication, nginx request-limit, and nginx bot-search jails.
   - Configures UFW with default deny and allows SSH, HTTP, and HTTPS using idempotent rules.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies reverse-path filtering, redirect and source-routing restrictions, martian logging, ICMP restrictions, IPv6 disablement, TCP SYN cookies, TCP SYN backlog `2048`, TCP SYN-ACK retries `2`, and TCP SYN retries `5`.
   - Applies sysctl settings after changes with `sysctl -p /etc/sysctl.d/99-security.conf`.
   - Changes `/etc/ssh/sshd_config` to set `PermitRootLogin no` and `PasswordAuthentication no`.
   - Restarts `ssh` only when SSH configuration changes.
   - Resources: one package resource installing two packages, two services, two templates, and eight execute resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`

2. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts nginx and provides reload, restart, and status support.
   - Configures worker user `www-data`, automatic worker processes, PID file `/run/nginx.pid`, worker connections `768`, keepalive timeout `65`, global access log `/var/log/nginx/access.log`, global error log `/var/log/nginx/error.log`, gzip, and standard nginx include paths.
   - Configures nginx security settings including disabled server tokens, login rate limit `10r/m`, API rate limit `30r/m`, client buffer and timeout restrictions, maximum client body size `1k`, TLS 1.2 and TLS 1.3, shared SSL session cache `SSL:10m`, SSL session timeout `10m`, and preferred server ciphers.
   - Creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`, then deploys `test/index.html` to `/opt/server/test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`, then deploys `ci/index.html` to `/opt/server/ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`, then deploys `status/index.html` to `/opt/server/status/index.html` with mode `0644`.
   - The site preparation loop executes three directory resources and three cookbook file resources.

3. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed certificate and RSA 2048 private key for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Common name: `test.cluster.local`
   - Generates a self-signed certificate and RSA 2048 private key for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Common name: `ci.cluster.local`
   - Generates a self-signed certificate and RSA 2048 private key for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Common name: `status.cluster.local`
   - Uses 365-day certificates generated with `openssl req -x509 -nodes -days 365 -newkey rsa:2048`.
   - Sets private-key mode to `0640` and ownership to `root:ssl-cert`.
   - Skips certificate generation when both certificate and key already exist.
   - Schedules a delayed nginx reload when a certificate is generated.
   - Resources: one package resource installing two packages, one group, two directories, and three certificate-generation executions.

4. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Links `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders the same template for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Links `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders the same template for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Links `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Each virtual host uses its site-specific document root, certificate, key, access log, and error log.
   - Each SSL-enabled virtual host provides HTTP port `80`, an HTTP-to-HTTPS redirect, HTTPS port `443`, HTTP/2, TLS 1.2 and TLS 1.3, HSTS, security headers, gzip, `try_files`, `.htaccess` blocking, `.git` and `.svn` blocking, and static-file handling.
   - Resources: three template executions, three link executions, and one file deletion.
   - Template render count:
     - `test.cluster.local`: one
     - `ci.cluster.local`: one
     - `status.cluster.local`: one

The supplied validation confirms recipe order, loop site names, resource types, package names, service resources, template destinations, and certificate-generation executions. Exact template contents, exact attribute definitions, and metadata claims require separate source verification.

## Dependencies

**External cookbook dependencies**: None listed in the supplied analysis; verify against `metadata.rb`.

**System package dependencies**:

- `nginx`
- `openssl`
- `ca-certificates`
- `fail2ban`
- `ufw`

**Service dependencies**:

- `fail2ban`: Enabled and started; delayed restart after `/etc/fail2ban/jail.local` changes
- `nginx`: Enabled and started; delayed reload after nginx configuration, certificate, virtual-host, or link changes
- `ssh`: Declared but not started or enabled by this cookbook; delayed restart after SSH hardening changes

## Credentials

**Detection Summary**: No external credentials were detected. Three locally generated TLS private keys and three locally generated self-signed certificates are created by the cookbook.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated files; not stored in a data bag, vault, environment variable, or external secret manager
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`

### TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: TLS certificates for the three nginx HTTPS virtual hosts
- **Validity**: `365` days
- **Key type**: RSA `2048`

No data bag, encrypted data bag, Chef Vault, Conjur, CyberArk, secret-manager URL, password, API token, database credential, or secret environment variable was detected.

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
- SSH: port `22`
- Unix sockets: None

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 time
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 time
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 time
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 time
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 time
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 time
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 time

**Total template render executions**: `8`

## Pre-flight checks:

```bash
# Verify installed packages
dpkg -l nginx openssl ca-certificates fail2ban ufw 2>/dev/null || \
rpm -q nginx openssl ca-certificates fail2ban ufw

# Verify service status
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl status ssh

# Validate nginx configuration
nginx -t
nginx -T

# Verify listeners
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
ss -tlnp | grep ':22'

# Verify the default site was removed
test ! -e /etc/nginx/sites-enabled/default

# Verify UFW state and rules
ufw status verbose
ufw status verbose | grep 'Default: deny'
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# Validate SSH configuration
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t

# Validate Fail2ban
fail2ban-client -t
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Validate sysctl configuration
cat /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# Verify global nginx logs
tail -n 20 /var/log/nginx/access.log
tail -n 20 /var/log/nginx/error.log
```

### `test.cluster.local`

```bash
ls -l /opt/server/test/index.html
ls -l /etc/nginx/sites-available/test.cluster.local
ls -l /etc/nginx/sites-enabled/test.cluster.local
ls -l /etc/ssl/certs/test.cluster.local.crt
ls -l /etc/ssl/private/test.cluster.local.key

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -dates

tail -n 20 /var/log/nginx/test.cluster.local_access.log
tail -n 20 /var/log/nginx/test.cluster.local_error.log
```

Expected results: HTTP returns `301` to HTTPS; HTTPS typically returns `200 OK`; the certificate subject contains `CN=test.cluster.local`.

### `ci.cluster.local`

```bash
ls -l /opt/server/ci/index.html
ls -l /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
ls -l /etc/ssl/certs/ci.cluster.local.crt
ls -l /etc/ssl/private/ci.cluster.local.key

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -dates

tail -n 20 /var/log/nginx/ci.cluster.local_access.log
tail -n 20 /var/log/nginx/ci.cluster.local_error.log
```

Expected results: HTTP returns `301` to HTTPS; HTTPS typically returns `200 OK`; the certificate subject contains `CN=ci.cluster.local`.

### `status.cluster.local`

```bash
ls -l /opt/server/status/index.html
ls -l /etc/nginx/sites-available/status.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
ls -l /etc/ssl/certs/status.cluster.local.crt
ls -l /etc/ssl/private/status.cluster.local.key

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -dates

tail -n 20 /var/log/nginx/status.cluster.local_access.log
tail -n 20 /var/log/nginx/status.cluster.local_error.log
```

Expected results: HTTP returns `301` to HTTPS; HTTPS typically returns `200 OK`; the certificate subject contains `CN=status.cluster.local`.

Migration is complete when all three named virtual hosts have functioning document roots, index files, certificates, private keys, enabled-site links, HTTP redirects, HTTPS responses, and site-specific logs.