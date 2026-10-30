---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, OpenSSL, CA certificates, Fail2ban, and UFW; applies Nginx, firewall, kernel, and SSH hardening; generates one self-signed certificate per site; deploys site document roots and index files; redirects HTTP to HTTPS; and enables the configured services.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80/tcp`; HTTPS `443/tcp`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80/tcp`; HTTPS `443/tcp`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80/tcp`; HTTPS `443/tcp`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH and Nginx logs
  - Key Config: Package installed; service enabled and started; SSH, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails enabled

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows SSH, HTTP `80/tcp`, and HTTPS `443/tcp`
  - Key Config: Default incoming policy denied; firewall enabled

- **ssh**: SSH hardening
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: SSH service port is not explicitly set by the cookbook
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`; service resource declared with action `nothing`

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

No provider files or executed custom resources are shown in the execution tree.

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

The execution tree uses `cookbook_file` three times for site index files, but the supplied file listing does not identify static source paths. Static source paths must be confirmed before the Ansible migration is implemented.

## Attributes

**Source**: `cookbooks/nginx-multisite/attributes/default.rb`

Configured values:

```yaml
nginx:
  sites:
    test.cluster.local:
      document_root: /opt/server/test
      ssl_enabled: true
    ci.cluster.local:
      document_root: /opt/server/ci
      ssl_enabled: true
    status.cluster.local:
      document_root: /opt/server/status
      ssl_enabled: true

  ssl:
    certificate_path: /etc/ssl/certs
    private_key_path: /etc/ssl/private

security:
  fail2ban:
    enabled: true
  ufw:
    enabled: true
  ssh:
    disable_root: true
    password_auth: false
```

The Ansible variable structure must preserve the explicit collection keys `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Security tasks execute before Nginx installation and configuration.
   - SSL generation executes before site configuration references the certificates.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban with:
     - Ban time `3600`
     - Find time `600`
     - Maximum retries `3`
     - Backend `auto`
     - Enabled `sshd` jail on `ssh`
     - Enabled `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails on `http,https`
     - Log paths `/var/log/auth.log`, `/var/log/nginx/*error.log`, and `/var/log/nginx/*access.log`
   - Applies UFW operations in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect protection, source-route disabling, martian packet logging, ICMP protections, IPv6 disabling, and TCP SYN flood protection.
   - Defines `execute[reload_sysctl]` with action `nothing`; no notification or subscription invokes it in the execution tree. The Ansible migration must explicitly decide whether to reload the deployed sysctl configuration.
   - With the default `security.ssh.disable_root: true`, changes `/etc/ssh/sshd_config` to `PermitRootLogin no`.
   - With the default `security.ssh.password_auth: false`, changes `/etc/ssh/sshd_config` to `PasswordAuthentication no`.
   - Declares the SSH service with action `nothing`; no SSH restart or reload is shown.
   - Resource summary: one package resource, two service resources, two templates, and seven execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures:
     - Worker user `www-data`
     - Worker processes `auto`
     - PID file `/run/nginx.pid`
     - Worker connections `768`
     - `sendfile on`
     - `tcp_nopush on`
     - `tcp_nodelay on`
     - Keepalive timeout `65`
     - Access log `/var/log/nginx/access.log`
     - Error log `/var/log/nginx/error.log`
     - Gzip
     - Includes for `/etc/nginx/modules-enabled/*.conf`, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, `login` and `api` rate limits, 1k request buffers and body limits, ten-second client and send timeouts, TLS 1.2 and TLS 1.3, a 10m shared SSL session cache, a 10m SSL session timeout, and preferred server ciphers.
   - Enables and starts Nginx.
   - Creates document root `/opt/server/test` and cookbook file `/opt/server/test/index.html` with mode `0644`.
   - Creates document root `/opt/server/ci` and cookbook file `/opt/server/ci/index.html` with mode `0644`.
   - Creates document root `/opt/server/status` and cookbook file `/opt/server/status/index.html` with mode `0644`.
   - The concrete static source paths for the three `index.html` files are not identified in the supplied file listing and must be confirmed.
   - Resource summary: one package, two templates, one service, three directories, and three cookbook files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
   - Generates a self-signed RSA certificate and private key for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
     - Key size: `2048`
     - Validity: `365` days
     - No passphrase
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
     - Key ownership and mode: `root:ssl-cert`, `640`
   - Generates a self-signed RSA certificate and private key for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
     - Key size: `2048`
     - Validity: `365` days
     - No passphrase
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`
     - Key ownership and mode: `root:ssl-cert`, `640`
   - Generates a self-signed RSA certificate and private key for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
     - Key size: `2048`
     - Validity: `365` days
     - No passphrase
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`
     - Key ownership and mode: `root:ssl-cert`, `640`
   - The Chef commands do not specify idempotence guards. The Ansible implementation must use `creates` or an equivalent approach so existing certificates and keys are not overwritten unintentionally.
   - Resource summary: one package, one group, two directories, and three certificate-generation execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`, using:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`, using:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`, using:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - The site template renders HTTP virtual hosts on port `80` that redirect to HTTPS and HTTPS HTTP/2 virtual hosts on port `443`.
   - Site configuration includes document roots, index files, TLS 1.2 and TLS 1.3, one-year HSTS with `includeSubDomains`, security headers, gzip, `try_files $uri $uri/ =404`, denial of `.htaccess`, `.git`, and `.svn` paths, and site-specific access and error logs.
   - Resource summary: three templates, three links, and one file deletion.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**System package dependencies**: `nginx`, `openssl`, `ca-certificates`, `fail2ban`, `ufw`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no explicit restart or reload is shown

**Network dependencies**:
- `80/tcp`: HTTP for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- `443/tcp`: HTTPS for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- SSH: allowed by UFW using the service name `ssh`; the exact port is not explicitly configured
- Unix sockets: None configured

## Credentials

**Detection Summary**: No application credentials, passwords, API keys, data bags, vault references, or database credentials were detected. Three locally generated TLS private keys and one hardcoded certificate subject email were identified.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: No secret-manager path or data bag was found

### Self-signed TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files
- **Usage context**: TLS private keys for the three Nginx HTTPS virtual hosts
- **Protection**: Mode `640`, owner/group `root:ssl-cert`

### Certificate Subject Email

- **Variable**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate subject value
- **Usage context**: Email field in each self-signed certificate subject
- **Sensitivity**: Not a password, token, or authentication secret

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk integration, environment-variable secrets, or embedded database connection credentials were detected.

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
- `/etc/nginx/sites-enabled/default` must be absent
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

- `test.cluster.local`: `80/tcp`, `443/tcp`
- `ci.cluster.local`: `80/tcp`, `443/tcp`
- `status.cluster.local`: `80/tcp`, `443/tcp`
- SSH: UFW service rule `ssh`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Nginx service and configuration
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
nginx -T

# Security services
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
ufw status verbose

# SSH hardening
grep -E '^[#]?PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[#]?PasswordAuthentication' /etc/ssh/sshd_config
sshd -t

# Kernel security settings
cat /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# Listener checks
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Log checks
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log

# Default site removal
test ! -e /etc/nginx/sites-enabled/default
```

Expected security values include:

```text
PermitRootLogin no
PasswordAuthentication no
Reverse-path filtering: 1
Redirect acceptance: 0
Source-route acceptance: 0
ICMP echo ignore: 1
IPv6 disabled: 1
TCP SYN cookies: 1
TCP SYN backlog: 2048
```

### Instance: `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G %n' /etc/ssl/private/test.cluster.local.key
```

Expected results:

- HTTP returns `301` redirecting to HTTPS.
- HTTPS returns `200 OK` when `/opt/server/test/index.html` exists.
- HTTPS contains the configured security headers.
- The certificate subject contains `CN=test.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.

### Instance: `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G %n' /etc/ssl/private/ci.cluster.local.key
```

Expected results:

- HTTP returns `301` redirecting to HTTPS.
- HTTPS returns `200 OK` when `/opt/server/ci/index.html` exists.
- HTTPS contains the configured security headers.
- The certificate subject contains `CN=ci.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.

### Instance: `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G %n' /etc/ssl/private/status.cluster.local.key
```

Expected results:

- HTTP returns `301` redirecting to HTTPS.
- HTTPS returns `200 OK` when `/opt/server/status/index.html` exists.
- HTTPS contains the configured security headers.
- The certificate subject contains `CN=status.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.