---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx for three SSL-enabled sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; creates self-signed TLS certificates; deploys static site content and virtual-host configurations; applies Nginx, kernel, firewall, and SSH security settings; enables the required services; and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; HTTPS uses HTTP/2; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`

- **ci.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; HTTPS uses HTTP/2; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`

- **status.cluster.local**: Static HTTPS site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; HTTP redirects to HTTPS; HTTPS uses HTTP/2; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`

Security attributes configure:

- Fail2ban enabled
- UFW enabled
- SSH root login disabled
- SSH password authentication disabled

The configured sites are represented by the following exact `nginx.sites` entries:

- `test.cluster.local`: document root `/opt/server/test`, SSL enabled
- `ci.cluster.local`: document root `/opt/server/ci`, SSL enabled
- `status.cluster.local`: document root `/opt/server/status`, SSL enabled

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No static file path is listed in the supplied cookbook directory listing. The recipes reference dynamic `cookbook_file` sources named `<site_folder>/index.html`; these source files must be supplied in the migrated deployment content, but their concrete paths are not present in the provided file list.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order: security, Nginx installation, certificate generation, and virtual-host deployment.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban defaults:
     - `bantime = 3600`
     - `findtime = 600`
     - `maxretry = 3`
     - `backend = auto`
   - Enables the `sshd` jail on `ssh` using `/var/log/auth.log`.
   - Enables `nginx-http-auth` and `nginx-limit-req` on `http,https` using `/var/log/nginx/*error.log`.
   - Enables `nginx-botsearch` on `http,https` using `/var/log/nginx/*access.log`.
   - Applies UFW commands:
     - `ufw --force default deny`
     - `ufw allow ssh`
     - `ufw allow http`
     - `ufw allow https`
     - `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, ICMP redirect and source-route protection, martian packet logging, ICMP protections, IPv6 disablement, and TCP SYN-flood protections.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as the `reload_sysctl` execute resource with action `nothing`; no triggering notification is shown.
   - Disables SSH root login with:
     ```bash
     sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
     ```
   - Disables SSH password authentication with:
     ```bash
     sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
     ```
   - Defines the `ssh` service with action `nothing`.
   - Resources: `package (1)`, `service (2)`, `template (2)`, `execute (8)`.
   - Execute resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`
   - Iterations: none.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `www-data`, automatic worker processes, PID file `/run/nginx.pid`, `768` worker connections, standard access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, request-rate zones `login: 10r/m` and `api: 30r/m`, request/header buffer limits, `client_max_body_size 1k`, request timeouts of `10`, TLS 1.2 and TLS 1.3, shared SSL cache `shared:SSL:10m`, a `10m` SSL session timeout, the configured ECDHE/DHE cipher list, and `ssl_prefer_server_ciphers on`.
   - Enables and starts the `nginx` service.
   - Site-content iterations:
     - **`test.cluster.local`**
       - Creates `/opt/server/test`.
       - Deploys `<site_folder>/index.html` to `/opt/server/test/index.html` with mode `0644`.
     - **`ci.cluster.local`**
       - Creates `/opt/server/ci`.
       - Deploys `<site_folder>/index.html` to `/opt/server/ci/index.html` with mode `0644`.
     - **`status.cluster.local`**
       - Creates `/opt/server/status`.
       - Deploys `<site_folder>/index.html` to `/opt/server/status/index.html` with mode `0644`.
   - Resources: `package (1)`, `template (2)`, `service (1)`, `directory (3)`, `cookbook_file (3)`.
   - Templates rendered:
     - `nginx.conf.erb`: 1 time
     - `security.conf.erb`: 1 time
   - No Nginx reload or restart notification is shown for configuration changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Certificate-generation iterations:
     - **`test.cluster.local`**
       - Generates `/etc/ssl/private/test.cluster.local.key` and `/etc/ssl/certs/test.cluster.local.crt`.
       - Uses RSA 2048-bit, self-signed X.509, valid for `365` days.
       - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
       - Sets the key to `root:ssl-cert` with mode `0640`.
     - **`ci.cluster.local`**
       - Generates `/etc/ssl/private/ci.cluster.local.key` and `/etc/ssl/certs/ci.cluster.local.crt`.
       - Uses RSA 2048-bit, self-signed X.509, valid for `365` days.
       - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`
       - Sets the key to `root:ssl-cert` with mode `0640`.
     - **`status.cluster.local`**
       - Generates `/etc/ssl/private/status.cluster.local.key` and `/etc/ssl/certs/status.cluster.local.crt`.
       - Uses RSA 2048-bit, self-signed X.509, valid for `365` days.
       - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`
       - Sets the key to `root:ssl-cert` with mode `0640`.
   - Resources: `package (1)`, `group (1)`, `directory (2)`, `execute (3)`.
   - Certificate generation must be idempotent in Ansible and must not regenerate existing valid key/certificate pairs on every run.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Virtual-host iterations:
     - **`test.cluster.local`**
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
       - Variables: `server_name=test.cluster.local`, `document_root=/opt/server/test`, `ssl_enabled=true`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
     - **`ci.cluster.local`**
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
       - Variables: `server_name=ci.cluster.local`, `document_root=/opt/server/ci`, `ssl_enabled=true`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
     - **`status.cluster.local`**
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
       - Variables: `server_name=status.cluster.local`, `document_root=/opt/server/status`, `ssl_enabled=true`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Each virtual host contains an HTTP port `80` listener redirecting to HTTPS, an HTTP/2 HTTPS port `443` listener, TLS 1.2 and TLS 1.3, HSTS, security headers, gzip, static-file routing with `try_files`, protected `.htaccess`, `.git`, and `.svn` paths, and site-specific access and error logs.
   - Resources: `template (3)`, `link (3)`, `file (1)`.
   - `site.conf.erb` renders 3 times: once for `test.cluster.local`, once for `ci.cluster.local`, and once for `status.cluster.local`.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: referenced with action `nothing`; no start, enable, restart, or reload action is shown

**Supported platforms from the supplied plan**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

UFW is normally associated with Ubuntu. Platform-specific conditions must be applied before running UFW commands on CentOS.

## Credentials

**Detection Summary**: No credentials were identified in the supplied analysis. The cookbook generates three sensitive TLS private keys locally but does not retrieve them from a credential provider. This conclusion should be rechecked against the complete recipe, template, and attribute scan during migration.

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
- **Current storage**: Locally generated files
- **Usage context**: Nginx HTTPS private keys
- **Permissions**: `root:ssl-cert`, mode `0640`

### Self-Signed TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated files
- **Usage context**: Nginx HTTPS server certificates
- **Properties**: Self-signed RSA 2048-bit certificates valid for `365` days, with subject email `admin@example.com`

The migration should determine whether these development certificates remain self-signed or are replaced by organizational CA certificates. Private keys transferred to hosts must use Ansible Vault or another protected deployment mechanism.

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

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- Unix sockets: None configured

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

## Pre-flight checks:

```bash
# Package and service checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl status ssh --no-pager

# Configuration checks
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
sshd -t

test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf
test ! -e /etc/nginx/sites-enabled/default

# Listener checks
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Firewall and Fail2ban checks
ufw status verbose
ufw status | grep -E '22|80|443'
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH hardening checks
grep -E '^[[:space:]]*PermitRootLogin|^[[:space:]]*PasswordAuthentication' \
  /etc/ssh/sshd_config

# Expected:
# PermitRootLogin no
# PasswordAuthentication no

# Sysctl checks
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6
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

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
# Expected: root:ssl-cert and mode 640
```

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

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
# Expected: root:ssl-cert and mode 640
```

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

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
# Expected: root:ssl-cert and mode 640
```

### Expected site behavior

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  -H 'Host: test.cluster.local' http://127.0.0.1/
# Expected: 301

curl -s -o /dev/null -w '%{http_code}\n' \
  -H 'Host: ci.cluster.local' http://127.0.0.1/
# Expected: 301

curl -s -o /dev/null -w '%{http_code}\n' \
  -H 'Host: status.cluster.local' http://127.0.0.1/
# Expected: 301

tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
```

The migration is complete when `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` each have their document root, static content, certificate, private key, virtual-host configuration, enabled link, HTTP-to-HTTPS redirect, HTTPS response, and site-specific logs, while Nginx, Fail2ban, UFW, SSH hardening, and sysctl settings match the intended Chef behavior.