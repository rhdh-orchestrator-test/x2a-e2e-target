---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, OpenSSL, CA certificates, Fail2ban, and UFW; configures SSH and kernel security settings; creates site document roots and index files; generates self-signed TLS certificates; deploys nginx security and virtual-host configuration; removes the default virtual host; and enables nginx and Fail2ban. The Ansible migration must preserve the recipe execution order and explicitly model all three sites and all security areas.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS nginx virtual host serving the test site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: TLS 1.2 and TLS 1.3; HTTP redirects to HTTPS; HTTP/2 enabled on HTTPS; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`; content source `test/index.html`

- **ci.cluster.local**: HTTPS nginx virtual host serving the CI site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: TLS 1.2 and TLS 1.3; HTTP redirects to HTTPS; HTTP/2 enabled on HTTPS; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`; content source `ci/index.html`

- **status.cluster.local**: HTTPS nginx virtual host serving the status site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: TLS 1.2 and TLS 1.3; HTTP redirects to HTTPS; HTTP/2 enabled on HTTPS; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`; content source `status/index.html`

**Security components**:

- Fail2ban with `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails
- UFW with default-deny incoming policy and TCP ports `22`, `80`, and `443` allowed
- SSH hardening with root login disabled and password authentication disabled
- Kernel security parameters managed through `/etc/sysctl.d/99-security.conf`

**Collection expansion**:

`nginx.sites` contains exactly:

- `test.cluster.local`
- `ci.cluster.local`
- `status.cluster.local`

The security configuration contains exactly:

- `fail2ban`
- `ufw`
- `ssh`

These areas are represented explicitly in Ansible variables and tasks rather than as a Chef loop.

## File Structure

The following complete directory listing is preserved from the original migration plan.

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

No provider files or custom resources are used by the execution tree.

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

No static files are listed in the supplied cookbook directory listing. The `nginx.rb` recipe references these dynamic `cookbook_file` sources:

```text
test/index.html
ci/index.html
status/index.html
```

These source files are not included in the supplied listing. The Ansible migration must provide equivalent files or otherwise make the content available before deploying the document roots.

## Module Explanation

The cookbook performs operations in this exact order:

1. `nginx-multisite::security` (`cookbooks/nginx-multisite/recipes/security.rb`)
2. `nginx-multisite::nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
3. `nginx-multisite::ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
4. `nginx-multisite::sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

The Ansible role should import task files in the same sequence.

### 1. Security configuration (`cookbooks/nginx-multisite/recipes/security.rb`)

- Install `fail2ban` and `ufw` with `ansible.builtin.package`.
- Enable and start the `fail2ban` service.
- Render `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configure Fail2ban defaults:
  - Ban time: `3600` seconds
  - Find time: `600` seconds
  - Maximum retries: `3`
  - Backend: `auto`
- Configure the following jails:
  - `sshd`: port `ssh`, log `/var/log/auth.log`, ban time `3600`, maximum retries `3`
  - `nginx-http-auth`: ports `http,https`, filter `nginx-http-auth`, ban time `3600`, maximum retries `3`
  - `nginx-limit-req`: ports `http,https`, filter `nginx-limit-req`, ban time `3600`, maximum retries `10`
  - `nginx-botsearch`: ports `http,https`, filter `nginx-botsearch`, ban time `3600`, maximum retries `2`
- Notify a delayed Fail2ban restart when `/etc/fail2ban/jail.local` changes.
- Configure UFW in this order:
  1. Set the default incoming policy to `deny`.
  2. Allow TCP port `22`.
  3. Allow TCP port `80`.
  4. Allow TCP port `443`.
  5. Enable UFW.
- Use `community.general.ufw` where possible. If shell commands are used, preserve the original guards and command order.
- Render `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Configure these kernel settings:
  - `net.ipv4.conf.default.rp_filter = 1`
  - `net.ipv4.conf.all.rp_filter = 1`
  - `net.ipv4.conf.all.accept_redirects = 0`
  - `net.ipv6.conf.all.accept_redirects = 0`
  - `net.ipv4.conf.default.accept_redirects = 0`
  - `net.ipv6.conf.default.accept_redirects = 0`
  - `net.ipv4.conf.all.accept_source_route = 0`
  - `net.ipv6.conf.all.accept_source_route = 0`
  - `net.ipv4.conf.default.accept_source_route = 0`
  - `net.ipv6.conf.default.accept_source_route = 0`
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
- Apply the settings with `ansible.posix.sysctl` or run `sysctl -p /etc/sysctl.d/99-security.conf` after the file changes.
- Notify a delayed sysctl reload when `/etc/sysctl.d/99-security.conf` changes.
- Set `PermitRootLogin no` in `/etc/ssh/sshd_config`.
- Set `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
- Use `ansible.builtin.lineinfile` instead of raw `sed`.
- Notify a delayed SSH restart only when either SSH setting changes.
- Use service name `ssh` on Ubuntu-family systems and `sshd` on CentOS-family systems.
- Preserve the observed execution behavior: Fail2ban and UFW resources are applied even though their `enabled` attributes are set to `true`.

**Iterations**: None. The security areas `fail2ban`, `ufw`, and `ssh` must be represented as explicit Ansible tasks.

**Resources represented**:

- Package installation containing `fail2ban` and `ufw`
- Services `fail2ban` and `ssh`
- Templates for `/etc/fail2ban/jail.local` and `/etc/sysctl.d/99-security.conf`
- Five UFW operations
- Sysctl reload
- Conditional SSH root-login and password-authentication updates

### 2. nginx installation and site content (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Install the `nginx` package.
- Render `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Configure:
  - Worker user: `www-data`
  - Worker processes: `auto`
  - PID file: `/run/nginx.pid`
  - Worker connections: `768`
  - `sendfile on`
  - `tcp_nopush on`
  - `tcp_nodelay on`
  - Keepalive timeout: `65`
  - Access log: `/var/log/nginx/access.log`
  - Error log: `/var/log/nginx/error.log`
  - Gzip enabled
  - Includes `/etc/nginx/modules-enabled/*.conf`
  - Includes `/etc/nginx/mime.types`
  - Includes `/etc/nginx/conf.d/*.conf`
  - Includes `/etc/nginx/sites-enabled/*`
- Render `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Configure:
  - `server_tokens off`
  - Login rate-limit zone `login`, size `10m`, rate `10r/m`
  - API rate-limit zone `api`, size `10m`, rate `30r/m`
  - Request body buffer `1K`
  - Request header buffer `1k`
  - Maximum body size `1k`
  - Large header buffers `2 1k`
  - Body, header, and send timeouts of `10`
  - TLS protocols `TLSv1.2 TLSv1.3`
  - TLS session cache `shared:SSL:10m`
  - TLS session timeout `10m`
  - The configured cipher suite:
    - `ECDHE-RSA-AES256-GCM-SHA512`
    - `DHE-RSA-AES256-GCM-SHA512`
    - `ECDHE-RSA-AES256-GCM-SHA384`
    - `DHE-RSA-AES256-GCM-SHA384`
    - `ECDHE-RSA-AES256-SHA384`
  - Server cipher preference enabled
- Enable and start the `nginx` service.
- Notify a delayed nginx reload when the main configuration, security configuration, site configurations, site links, or certificates change.

**Iterations**: The site-content collection runs exactly three times:

1. `test.cluster.local`
   - Create `/opt/server/test` owned by `www-data:www-data`, mode `0755`, with recursive creation.
   - Deploy source `test/index.html` to `/opt/server/test/index.html`.
   - Set the index file owner and group to `www-data:www-data`, mode `0644`.

2. `ci.cluster.local`
   - Create `/opt/server/ci` owned by `www-data:www-data`, mode `0755`, with recursive creation.
   - Deploy source `ci/index.html` to `/opt/server/ci/index.html`.
   - Set the index file owner and group to `www-data:www-data`, mode `0644`.

3. `status.cluster.local`
   - Create `/opt/server/status` owned by `www-data:www-data`, mode `0755`, with recursive creation.
   - Deploy source `status/index.html` to `/opt/server/status/index.html`.
   - Set the index file owner and group to `www-data:www-data`, mode `0644`.

**Resources represented**:

- One nginx package
- Two nginx configuration templates
- One nginx service
- Three document-root directories
- Three index files

### 3. SSL package and certificate generation (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Install `openssl` and `ca-certificates`.
- Create the `ssl-cert` group.
- Create `/etc/ssl/certs` owned by `root:root`, mode `0755`.
- Create `/etc/ssl/private` owned by `root:ssl-cert`, mode `0710`.
- Process the three SSL-enabled sites explicitly:
  1. `test.cluster.local`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
  2. `ci.cluster.local`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
  3. `status.cluster.local`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
- Do not skip any of the three sites because all have `ssl_enabled: true`.
- Generate a certificate only when both the certificate and private-key files do not already exist.
- Generate each certificate as a self-signed RSA certificate with:
  - Validity: `365` days
  - Key size: `2048`
  - No passphrase
  - Country: `US`
  - State: `Example`
  - Locality: `Example`
  - Organization: `Example Org`
  - Organizational unit: `IT`
  - Common name: the site hostname
  - Subject email: `admin@example.com`
- Set each private key to mode `0640` and ownership `root:ssl-cert`.
- Notify a delayed nginx reload after newly generated or changed certificate material.
- Prefer `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate`; an explicitly guarded command is acceptable when preserving exact behavior.

**Iterations**: Certificate generation runs exactly three times:

- `test.cluster.local`
- `ci.cluster.local`
- `status.cluster.local`

### 4. nginx virtual hosts (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Process the three virtual hosts explicitly:
  1. `test.cluster.local`
     - Render `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
     - Use document root `/opt/server/test`.
     - Use certificate `/etc/ssl/certs/test.cluster.local.crt`.
     - Use private key `/etc/ssl/private/test.cluster.local.key`.
     - Create `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.

  2. `ci.cluster.local`
     - Render `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
     - Use document root `/opt/server/ci`.
     - Use certificate `/etc/ssl/certs/ci.cluster.local.crt`.
     - Use private key `/etc/ssl/private/ci.cluster.local.key`.
     - Create `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.

  3. `status.cluster.local`
     - Render `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
     - Use document root `/opt/server/status`.
     - Use certificate `/etc/ssl/certs/status.cluster.local.crt`.
     - Use private key `/etc/ssl/private/status.cluster.local.key`.
     - Create `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
- Remove `/etc/nginx/sites-enabled/default`.
- Notify a delayed nginx reload when a site template, site link, or default-site removal changes.
- For all three sites, render:
  - An HTTP server listening on port `80`
  - An HTTP-to-HTTPS redirect using `return 301 https://$server_name$request_uri;`
  - An HTTPS server listening on port `443` with HTTP/2
  - The configured document root
  - The generated certificate and private-key paths
  - TLS 1.2 and TLS 1.3
  - HSTS: `max-age=31536000; includeSubDomains`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - A Content Security Policy primarily restricting resources to `'self'`
  - Gzip compression
  - `try_files $uri $uri/ =404;`
  - Host-specific access and error logs
  - Denial of `.ht` files
  - Denial of `.git` and `.svn` paths

**Iterations**: The virtual-host collection runs exactly three times:

- `test.cluster.local`
- `ci.cluster.local`
- `status.cluster.local`

**Resources represented**:

- Three site templates
- Three site links
- One default-site removal

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

- `nginx`
- `openssl`
- `ca-certificates`
- `fail2ban`
- `ufw`

**Service dependencies**:

- `nginx`
- `fail2ban`
- `ssh` on Ubuntu-family systems
- `sshd` on CentOS-family systems

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Network dependencies**:

- SSH TCP `22`
- HTTP TCP `80`
- HTTPS TCP `443`

## Credentials

**Detection Summary**: No externally stored credentials were detected. Three locally generated TLS private keys are created for the development self-signed certificates. The certificate subject email is a hardcoded identity string and is not a credential.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### Generated TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by the `openssl req` command
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts
- **Permissions**: Mode `0640`
- **Owner/group**: `root:ssl-cert`
- **Migration guidance**: Treat the files as sensitive, do not expose their contents in Ansible output, and prefer Ansible Vault or an external certificate-management workflow for production certificates. Preserve local self-signed generation only for development environments.

### Certificate subject email

- **Variable**: `admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate subject value
- **Usage context**: Subject email field of the generated self-signed certificates
- **Sensitive credential**: No; this is an identity string, not a password or token.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk integration, Vault URL, API key, database credential, password, or secret environment variable was detected.

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

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: **1 render**
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: **1 render**
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: **1 render**
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: **1 render**
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: **1 render**
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: **1 render**
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: **1 render**
- `site.conf.erb` total: **3 renders**

## Pre-flight checks

```bash
# Verify required packages.
dpkg-query -W nginx openssl ca-certificates fail2ban ufw 2>/dev/null || \
rpm -q nginx openssl ca-certificates fail2ban ufw

# Verify service state.
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active ssh 2>/dev/null || systemctl is-active sshd

# Validate nginx configuration and confirm all listeners and hostnames.
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
nginx -T | grep -E 'listen 80|listen 443 ssl http2'

# Verify security configuration.
grep -E 'PermitRootLogin no|PasswordAuthentication no' /etc/ssh/sshd_config
ufw status verbose
sysctl -p /etc/sysctl.d/99-security.conf

# Verify the default virtual host was removed.
test ! -e /etc/nginx/sites-enabled/default
```

### `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: test.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: test.cluster.local' https://127.0.0.1/ | head

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
```

Expected results:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200` when the index file is present.
- The certificate subject contains `CN=test.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.

### `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: ci.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: ci.cluster.local' https://127.0.0.1/ | head

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
```

Expected results:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200` when the index file is present.
- The certificate subject contains `CN=ci.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.

### `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: status.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: status.cluster.local' https://127.0.0.1/ | head

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected results:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200` when the index file is present.
- The certificate subject contains `CN=status.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.