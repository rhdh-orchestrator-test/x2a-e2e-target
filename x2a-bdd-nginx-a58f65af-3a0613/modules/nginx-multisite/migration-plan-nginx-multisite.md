---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled static sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; configures HTTP-to-HTTPS redirects, self-signed certificates, security settings, firewall rules, SSH hardening, kernel parameters, and three nginx virtual hosts. The Ansible implementation must preserve the recipe execution order, explicitly manage all three site instances, retain the generated certificate and key properties, and verify template-level settings against the original source files.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/test`
  - HTTP endpoint: `80/tcp`, redirected to HTTPS
  - HTTPS endpoint: `443/tcp`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Static content: `/opt/server/test/index.html`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`
  - SSL enabled: `true`

- **ci.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/ci`
  - HTTP endpoint: `80/tcp`, redirected to HTTPS
  - HTTPS endpoint: `443/tcp`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Static content: `/opt/server/ci/index.html`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`
  - SSL enabled: `true`

- **status.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/status`
  - HTTP endpoint: `80/tcp`, redirected to HTTPS
  - HTTPS endpoint: `443/tcp`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Static content: `/opt/server/status/index.html`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`
  - SSL enabled: `true`

Security components:

- **fail2ban**: Installed and enabled through the `fail2ban` service.
- **ufw**: Installed and configured with default-deny behavior.
- **ssh**: Hardened by disabling root login and password authentication.

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
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
```

**Recipes:**
- `cookbooks/nginx-multisite/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/security.rb`
- `cookbooks/nginx-multisite/recipes/nginx.rb`
- `cookbooks/nginx-multisite/recipes/ssl.rb`
- `cookbooks/nginx-multisite/recipes/sites.rb`

**Providers:** None.

**Templates:**
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`

**Attributes:**
- `cookbooks/nginx-multisite/attributes/default.rb`

**Static files referenced by recipes:**
- `test/index.html` → `/opt/server/test/index.html`
- `ci/index.html` → `/opt/server/ci/index.html`
- `status/index.html` → `/opt/server/status/index.html`

The referenced static source files are not present in the supplied directory listing. The Ansible migration must provide equivalent files or preserve equivalent deployment behavior.

## Module Explanation

The cookbook performs operations in this order:

1. `nginx-multisite::security` (`cookbooks/nginx-multisite/recipes/security.rb`)
2. `nginx-multisite::nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
3. `nginx-multisite::ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
4. `nginx-multisite::sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

### 1. Security

**Recipe:** `cookbooks/nginx-multisite/recipes/security.rb`

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts the `fail2ban` service.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
- Deploys the sysctl configuration template `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
- Configures UFW with default-deny incoming behavior.
- Allows SSH on `22/tcp`.
- Allows HTTP on `80/tcp`.
- Allows HTTPS on `443/tcp`.
- Enables UFW.
- Disables root SSH login when `node['security']['ssh']['disable_root']` is `true`.
- Disables SSH password authentication when `node['security']['ssh']['password_auth'] == false`.
- Restarts SSH only when SSH configuration changes.
- Reloads sysctl settings only when `/etc/sysctl.d/99-security.conf` changes.
- Restarts fail2ban when `/etc/fail2ban/jail.local` changes.

The Ansible implementation should use `package`, `service`, `template`, `community.general.ufw`, `ansible.posix.sysctl`, and `lineinfile` where appropriate. Handlers should model the delayed Chef notifications.

The following fail2ban values and sysctl settings are recorded in the migration source but require verification against `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` and `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`:

- Fail2ban `bantime`: `3600`
- Fail2ban `findtime`: `600`
- Fail2ban `maxretry`: `3`
- Fail2ban backend: `auto`
- Enabled jails: `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch`
- Reverse-path filtering
- Disabled IPv4 and IPv6 ICMP redirects
- Disabled source routing
- Martian packet logging
- Ignored ICMP echo requests and broadcast pings
- Disabled IPv6 on all, default, and loopback interfaces
- TCP SYN-cookie protection
- TCP SYN backlog and retry settings

The UFW idempotence checks and SSH configuration guards are documented in the original plan but are not fully represented in the supplied structured analysis. Their exact guard behavior must be confirmed against the recipe source before implementation.

### 2. Nginx Installation and Base Configuration

**Recipe:** `cookbooks/nginx-multisite/recipes/nginx.rb`

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
- Enables and starts the `nginx` service.
- Creates the three site directories:
  - `/opt/server/test`
  - `/opt/server/ci`
  - `/opt/server/status`
- Deploys the three static index files:
  - `test/index.html` → `/opt/server/test/index.html`
  - `ci/index.html` → `/opt/server/ci/index.html`
  - `status/index.html` → `/opt/server/status/index.html`

The recorded resource properties are:

- Site directory owner: `www-data`
- Site directory group: `www-data`
- Site directory mode: `0755`
- Static file owner: `www-data`
- Static file group: `www-data`
- Static file mode: `0644`

These ownership and mode values require confirmation against the source recipe because they are not included in the supplied structured analysis.

Recorded nginx base settings requiring verification against `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` and `cookbooks/nginx-multisite/templates/default/security.conf.erb` include:

- Worker user: `www-data`
- Worker processes: `auto`
- PID file: `/run/nginx.pid`
- Worker connections: `768`
- Access log: `/var/log/nginx/access.log`
- Error log: `/var/log/nginx/error.log`
- Gzip enabled
- Includes for:
  - `/etc/nginx/modules-enabled/*.conf`
  - `/etc/nginx/conf.d/*.conf`
  - `/etc/nginx/sites-enabled/*`
- `server_tokens off`
- Request-rate zones:
  - `login`: `10r/m`
  - `api`: `30r/m`
- TLS versions: `TLSv1.2 TLSv1.3`
- Shared SSL session cache: `shared:SSL:10m`
- SSL session timeout: `10m`

### 3. SSL Package, Directories, and Certificate Generation

**Recipe:** `cookbooks/nginx-multisite/recipes/ssl.rb`

- Installs:
  - `openssl`
  - `ca-certificates`
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
- Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.

Certificate generation iterations:

- **test.cluster.local**
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Key: `/etc/ssl/private/test.cluster.local.key`
  - RSA key size: `2048` bits
  - Validity: `365` days
  - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
  - Key owner: `root`
  - Key group: `ssl-cert`
  - Key mode: `0640`
  - Reloads nginx after certificate changes.

- **ci.cluster.local**
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Key: `/etc/ssl/private/ci.cluster.local.key`
  - RSA key size: `2048` bits
  - Validity: `365` days
  - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`
  - Key owner: `root`
  - Key group: `ssl-cert`
  - Key mode: `0640`
  - Reloads nginx after certificate changes.

- **status.cluster.local**
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Key: `/etc/ssl/private/status.cluster.local.key`
  - RSA key size: `2048` bits
  - Validity: `365` days
  - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`
  - Key owner: `root`
  - Key group: `ssl-cert`
  - Key mode: `0640`
  - Reloads nginx after certificate changes.

All three sites have `ssl_enabled: true`, so all three certificate-generation iterations execute. The original plan states that certificate generation is skipped when both the certificate and key already exist; the supplied structured analysis does not confirm this existence guard. The Ansible implementation must verify the recipe and preserve the actual idempotence behavior.

Use `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate` where appropriate, while preserving the one-year validity, RSA 2048-bit key size, subject fields, ownership, group, and modes. Existing certificate/key pairs must not be overwritten unless renewal is explicitly required.

### 4. Virtual Host Configuration

**Recipe:** `cookbooks/nginx-multisite/recipes/sites.rb`

- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb`.
- Creates one configuration and one enabled symlink for each named site.
- Removes `/etc/nginx/sites-enabled/default`.
- Reloads nginx after virtual host or symlink changes.

Virtual host iterations:

- **test.cluster.local**
  - Configuration: `/etc/nginx/sites-available/test.cluster.local`
  - Symlink: `/etc/nginx/sites-enabled/test.cluster.local`
  - Document root: `/opt/server/test`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - `ssl_enabled`: `true`
  - Mode: `0644`

- **ci.cluster.local**
  - Configuration: `/etc/nginx/sites-available/ci.cluster.local`
  - Symlink: `/etc/nginx/sites-enabled/ci.cluster.local`
  - Document root: `/opt/server/ci`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - `ssl_enabled`: `true`
  - Mode: `0644`

- **status.cluster.local**
  - Configuration: `/etc/nginx/sites-available/status.cluster.local`
  - Symlink: `/etc/nginx/sites-enabled/status.cluster.local`
  - Document root: `/opt/server/status`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - `ssl_enabled`: `true`
  - Mode: `0644`

The following rendered behavior is recorded but requires verification against `cookbooks/nginx-multisite/templates/default/site.conf.erb`:

- Port `80` redirects to HTTPS with status `301`.
- Port `443` uses SSL and HTTP/2.
- TLS versions are `TLSv1.2` and `TLSv1.3`.
- HSTS is enabled with `max-age=31536000; includeSubDomains`.
- Static content is served from the configured document root.
- `try_files $uri $uri/ =404` is used.
- Access to `.htaccess`, `.git`, and `.svn` paths is denied.
- Security headers include:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - A restrictive Content Security Policy.
- Gzip compression is enabled.
- Site-specific access and error logs are configured.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `ssh`: restarted only when SSH configuration changes.
- UFW: enabled through firewall configuration or equivalent commands.

**Network ports**:

- `22/tcp`: SSH
- `80/tcp`: HTTP
- `443/tcp`: HTTPS

**Supported platforms recorded by the cookbook**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: No externally supplied passwords, API tokens, data bags, encrypted data bags, Chef Vault references, CyberArk references, Conjur references, or external secret-manager URLs were detected. Three locally generated TLS private keys and one hardcoded certificate subject email were identified across the SSL recipe and attributes.

**Source**:

- **Provider**: None detected.
- **URL**: None detected.
- **Path**: None detected.

### Self-signed TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/attributes/default.rb`
- **Current storage**: Generated locally by the OpenSSL command; not stored in a Chef data bag or vault.
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts.
- **Protection**:
  - Owner: `root`
  - Group: `ssl-cert`
  - Mode: `0640`

### Certificate subject email

- **Variable**: `admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL subject string.
- **Usage context**: Certificate subject metadata only; not used for authentication.

Production private keys must be supplied through an approved Ansible Automation Platform credential, encrypted variable, or external certificate-management process rather than plain Ansible variables.

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
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

**Service endpoints to check**:

- `test.cluster.local:80`
- `test.cluster.local:443`
- `ci.cluster.local:80`
- `ci.cluster.local:443`
- `status.cluster.local:80`
- `status.cluster.local:443`
- SSH on `22/tcp`
- No Unix socket is configured.

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Package and service checks
dpkg -l fail2ban ufw nginx openssl ca-certificates 2>/dev/null || \
rpm -q fail2ban ufw nginx openssl ca-certificates

systemctl status fail2ban
systemctl status nginx
systemctl status ssh

# Fail2ban checks
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

grep -E '^(bantime|findtime|maxretry|backend|enabled|port|logpath)' \
  /etc/fail2ban/jail.local

# UFW checks
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# SSH hardening checks
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t
systemctl is-active ssh

# Kernel security checks
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Nginx validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
nginx -T | grep -E 'listen 80|listen 443 ssl http2'
systemctl is-enabled nginx
systemctl is-active nginx

# Site directories and files
ls -ld /opt/server/test
ls -ld /opt/server/ci
ls -ld /opt/server/status

ls -l /opt/server/test/index.html
ls -l /opt/server/ci/index.html
ls -l /opt/server/status/index.html

stat -c '%U:%G %a %n' /opt/server/test/index.html
stat -c '%U:%G %a %n' /opt/server/ci/index.html
stat -c '%U:%G %a %n' /opt/server/status/index.html

# Virtual host links
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Certificate and key checks
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected security results:

- UFW default incoming policy is deny.
- `22/tcp`, `80/tcp`, and `443/tcp` are allowed.
- UFW is active.
- SSH contains:
  - `PermitRootLogin no`
  - `PasswordAuthentication no`
- The `fail2ban` jails are `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch`.
- Nginx validation reports `syntax is ok` and `test is successful`.
- Static files are owned by `www-data:www-data` with mode `0644`.
- TLS keys are owned by `root:ssl-cert` with mode `0640`.
- Certificate common names are:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

### Site-specific HTTP redirect checks

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
```

Expected result for each site:

```text
HTTP/1.1 301 Moved Permanently
Location: https://<site-name>/
```

### test.cluster.local HTTPS checks

```bash
curl --insecure -I \
  --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

curl --insecure -s \
  --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | head

curl --insecure -s -D - -o /dev/null \
  --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
```

Verify that HTTPS succeeds, the response contains content from `/opt/server/test/index.html`, the response includes HSTS and security headers, and the certificate is for `test.cluster.local`.

### ci.cluster.local HTTPS checks

```bash
curl --insecure -I \
  --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

curl --insecure -s \
  --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ | head

curl --insecure -s -D - -o /dev/null \
  --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
```

Verify that HTTPS succeeds, the response contains content from `/opt/server/ci/index.html`, the response includes HSTS and security headers, and the certificate is for `ci.cluster.local`.

### status.cluster.local HTTPS checks

```bash
curl --insecure -I \
  --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

curl --insecure -s \
  --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ | head

curl --insecure -s -D - -o /dev/null \
  --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
```

Verify that HTTPS succeeds, the response contains content from `/opt/server/status/index.html`, the response includes HSTS and security headers, and the certificate is for `status.cluster.local`.