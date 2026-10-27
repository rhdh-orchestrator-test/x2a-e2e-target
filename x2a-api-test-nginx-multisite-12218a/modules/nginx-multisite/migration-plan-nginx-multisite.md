---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx as a multisite web server on Ubuntu or CentOS with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies SSH and kernel security settings; generates self-signed certificates; deploys site document roots and index files; configures HTTP-to-HTTPS redirects and HTTPS virtual hosts; enables the required services; and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; index file `/opt/server/test/index.html`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; index file `/opt/server/ci/index.html`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; index file `/opt/server/status/index.html`

The security configuration contains:

- Fail2ban enabled
- UFW enabled
- SSH root login disabled
- SSH password authentication disabled

These attribute values are referenced by the recipes and should be confirmed against `attributes/default.rb` during migration implementation.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No provider files are used. The `resources/lineinfile.rb` custom resource definition is not part of the supplied execution tree and is not included.

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
```text
```

No static `files/default/*` or `files/*` files are listed in the supplied directory listing. The recipes reference the following `cookbook_file` sources, but they are not present in the supplied file list:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)
2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)
3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

### 1. Default recipe (`cookbooks/nginx-multisite/recipes/default.rb`)

The recipe includes these recipes in order:

1. `nginx-multisite::security`
2. `nginx-multisite::nginx`
3. `nginx-multisite::ssl`
4. `nginx-multisite::sites`

This ordering ensures that security packages, Nginx, certificates, document roots, and site configurations are processed in sequence.

### 2. Security recipe (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs packages `fail2ban` and `ufw`.
- Enables and starts `service[fail2ban]`.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configures the reported Fail2ban defaults:
  - Ban time: `3600`
  - Find time: `600`
  - Maximum retries: `3`
  - Backend: `auto`
  - SSH, Nginx HTTP authentication, Nginx request-rate, and Nginx bot-search jails
- Executes five UFW commands to:
  - Set the default policy to deny
  - Allow SSH on `22/tcp`
  - Allow HTTP on `80/tcp`
  - Allow HTTPS on `443/tcp`
  - Enable UFW
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Declares `execute[reload_sysctl]` with action `nothing`; the reported reload command is:
  ```bash
  sysctl -p /etc/sysctl.d/99-security.conf
  ```
- Applies the reported SSH hardening:
  ```bash
  sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
  sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
  ```
- Declares `service[ssh]` with action `nothing`; SSH restart behavior must be confirmed against the recipe source.

**Resources**: `package` 1, `service` 2, `template` 2, `execute` 8.

The reported conditional UFW guards, file-existence guards for certificate generation, and notification relationships should be verified directly from the recipe source before implementation.

### 3. Nginx recipe (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs package `nginx`.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Enables and starts `service[nginx]`.
- The reported main configuration includes:
  - User `www-data`
  - Worker processes `auto`
  - PID `/run/nginx.pid`
  - Worker connections `768`
  - Keepalive timeout `65`
  - Access log `/var/log/nginx/access.log`
  - Error log `/var/log/nginx/error.log`
  - Gzip enabled
  - Includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`
- The reported security configuration includes TLS 1.2 and TLS 1.3, request-rate zones, request-size limits, timeout restrictions, SSL session settings, and server-version hiding. Exact template values should be confirmed from `security.conf.erb`.

The recipe iterates over exactly these three sites:

- **test.cluster.local**
  - Creates `/opt/server/test` owned by `www-data:www-data`, mode `0755`
  - Deploys source `test/index.html` to `/opt/server/test/index.html`, owned by `www-data:www-data`, mode `0644`

- **ci.cluster.local**
  - Creates `/opt/server/ci` owned by `www-data:www-data`, mode `0755`
  - Deploys source `ci/index.html` to `/opt/server/ci/index.html`, owned by `www-data:www-data`, mode `0644`

- **status.cluster.local**
  - Creates `/opt/server/status` owned by `www-data:www-data`, mode `0755`
  - Deploys source `status/index.html` to `/opt/server/status/index.html`, owned by `www-data:www-data`, mode `0644`

**Resources**: `package` 1, `template` 2, `service` 1, `directory` 3, `cookbook_file` 3.

### 4. SSL recipe (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs packages `openssl` and `ca-certificates`.
- Creates group `ssl-cert`.
- Creates `/etc/ssl/certs` owned by `root:root`, mode `0755`.
- Creates `/etc/ssl/private` owned by `root:ssl-cert`, mode `0710`.

The SSL loop runs once for each of the following three sites:

- **test.cluster.local**
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Key: `/etc/ssl/private/test.cluster.local.key`
  - Reported certificate: self-signed RSA 2048-bit, valid for `365` days
  - Subject common name: `test.cluster.local`
  - Subject email: `admin@example.com`
  - Key ownership: `root:ssl-cert`
  - Key mode: `0640`

- **ci.cluster.local**
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Key: `/etc/ssl/private/ci.cluster.local.key`
  - Reported certificate: self-signed RSA 2048-bit, valid for `365` days
  - Subject common name: `ci.cluster.local`
  - Subject email: `admin@example.com`
  - Key ownership: `root:ssl-cert`
  - Key mode: `0640`

- **status.cluster.local**
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Key: `/etc/ssl/private/status.cluster.local.key`
  - Reported certificate: self-signed RSA 2048-bit, valid for `365` days
  - Subject common name: `status.cluster.local`
  - Subject email: `admin@example.com`
  - Key ownership: `root:ssl-cert`
  - Key mode: `0640`

The reported certificate command is equivalent to:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/<site>.key \
  -out /etc/ssl/certs/<site>.crt \
  -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site>/emailAddress=admin@example.com"
```

**Resources**: `package` 1, `group` 1, `directory` 2, `execute` 3.

The reported certificate existence guards and Nginx reload notifications should be confirmed from the recipe source.

### 5. Sites recipe (`cookbooks/nginx-multisite/recipes/sites.rb`)

The recipe renders `site.conf.erb` and creates one enabled-site link for each named site.

- **test.cluster.local**
  - Renders to `/etc/nginx/sites-available/test.cluster.local`
  - Document root: `/opt/server/test`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Key: `/etc/ssl/private/test.cluster.local.key`
  - SSL enabled: `true`
  - Links `/etc/nginx/sites-enabled/test.cluster.local` to the available-site file

- **ci.cluster.local**
  - Renders to `/etc/nginx/sites-available/ci.cluster.local`
  - Document root: `/opt/server/ci`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Key: `/etc/ssl/private/ci.cluster.local.key`
  - SSL enabled: `true`
  - Links `/etc/nginx/sites-enabled/ci.cluster.local` to the available-site file

- **status.cluster.local**
  - Renders to `/etc/nginx/sites-available/status.cluster.local`
  - Document root: `/opt/server/status`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Key: `/etc/ssl/private/status.cluster.local.key`
  - SSL enabled: `true`
  - Links `/etc/nginx/sites-enabled/status.cluster.local` to the available-site file

The recipe deletes:

```text
/etc/nginx/sites-enabled/default
```

The reported site template behavior includes:

- HTTP listener on port `80`
- HTTP-to-HTTPS redirect with status `301`
- HTTPS listener on port `443`
- HTTP/2
- Site-specific document roots, certificates, and logs
- TLS 1.2 and TLS 1.3
- HSTS and security headers
- Gzip compression
- `try_files $uri $uri/ =404`
- Denial of `.htaccess`, `.git`, and `.svn` paths

Exact directives should be verified against `templates/default/site.conf.erb`.

**Resources**: `template` 3, `link` 3, `file` 1.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `nginx`: enabled and started; configuration and certificate changes require reload behavior
- `fail2ban`: enabled and started; jail configuration changes require restart behavior
- `ssh`: remains active and is restarted when SSH hardening changes
- UFW: managed through command resources; no UFW service resource is declared

**Supported platforms reported by the cookbook**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

These platform claims should be confirmed against cookbook metadata during migration.

## Credentials

**Detection Summary**: No externally supplied passwords, API keys, data bags, Chef Vault items, CyberArk integrations, Conjur variables, database credentials, or environment-variable secrets were detected. Three locally generated private keys and three locally generated self-signed certificates are deployed.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### TLS certificates and private keys

- **Variable(s)**:
  - `node['nginx']['ssl']['certificate_path']`
  - `node['nginx']['ssl']['private_key_path']`
  - Per-site certificate and key paths derived from site names
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate and private-key files
- **Usage context**: Nginx TLS termination for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Paths**:
  - Certificates: `/etc/ssl/certs/<site>.crt`
  - Private keys: `/etc/ssl/private/<site>.key`
- **Key protection**:
  - Private-key mode: `0640`
  - Private-key owner and group: `root:ssl-cert`
  - Private-key directory mode: `0710`

The migration should decide whether to retain these self-signed certificates or replace them with managed certificates.

### Hardcoded certificate subject email

- **Variable(s)**: Literal `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded non-secret value
- **Usage context**: Subject email in the three generated self-signed certificates

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
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`

**Service endpoints to check**:

- `test.cluster.local`: ports `80` and `443`
- `ci.cluster.local`: ports `80` and `443`
- `status.cluster.local`: ports `80` and `443`
- SSH: port `22`
- UFW: allowed ports `22`, `80`, and `443`

**Unix sockets**: None configured.

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 rendering
- `nginx.conf.erb`: 1 rendering
- `security.conf.erb`: 1 rendering
- `sysctl-security.conf.erb`: 1 rendering
- `site.conf.erb`: 3 renderings:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Package and service status
dpkg-query -W nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-active nginx
systemctl is-active fail2ban
systemctl is-active ssh

# Nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Main and security configuration
grep -E 'user www-data|worker_processes auto|worker_connections 768|keepalive_timeout 65|gzip on' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens off|ssl_protocols TLSv1\.2 TLSv1\.3|client_max_body_size 1k|send_timeout 10' \
  /etc/nginx/conf.d/security.conf

# test.cluster.local
curl -k -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: test.cluster.local' https://127.0.0.1/
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
test -f /var/log/nginx/test.cluster.local_access.log
test -f /var/log/nginx/test.cluster.local_error.log

# ci.cluster.local
curl -k -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: ci.cluster.local' https://127.0.0.1/
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
test -f /var/log/nginx/ci.cluster.local_access.log
test -f /var/log/nginx/ci.cluster.local_error.log

# status.cluster.local
curl -k -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: status.cluster.local' https://127.0.0.1/
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
test -f /var/log/nginx/status.cluster.local_access.log
test -f /var/log/nginx/status.cluster.local_error.log

# Enabled sites and default site removal
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Listening ports
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
ss -tlnp | grep ':22 '

# TLS certificate selection
echo | openssl s_client -connect 127.0.0.1:443 -servername test.cluster.local 2>/dev/null \
  | openssl x509 -noout -subject -issuer
echo | openssl s_client -connect 127.0.0.1:443 -servername ci.cluster.local 2>/dev/null \
  | openssl x509 -noout -subject -issuer
echo | openssl s_client -connect 127.0.0.1:443 -servername status.cluster.local 2>/dev/null \
  | openssl x509 -noout -subject -issuer

# Firewall
ufw status verbose
ufw status numbered

# Fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime = 3600|findtime = 600|maxretry = 3|backend = auto' \
  /etc/fail2ban/jail.local

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t
systemctl is-active ssh

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
test -f /etc/sysctl.d/99-security.conf

# Service logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
journalctl -u ssh --no-pager -n 50
```