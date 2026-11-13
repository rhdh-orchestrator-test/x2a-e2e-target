---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server hosting three HTTPS-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies nginx, kernel, firewall, and SSH security settings; generates self-signed certificates; deploys static index pages; configures HTTP-to-HTTPS redirects and HTTPS virtual hosts; and disables root SSH login and SSH password authentication. The Ansible migration must provide explicit sources for the three static index files, preserve recipe ordering and idempotency, and include a non-empty `ansible/Makefile` with a default `all` target that invokes `ansible-playbook`.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

All three sites have SSL enabled.

- **test.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; index file `/opt/server/test/index.html`; HTTP/2, HSTS, security headers, gzip, and site-specific logs

- **ci.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; index file `/opt/server/ci/index.html`; HTTP/2, HSTS, security headers, gzip, and site-specific logs

- **status.cluster.local**: HTTPS nginx virtual host serving static content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirected to HTTPS; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; index file `/opt/server/status/index.html`; HTTP/2, HSTS, security headers, gzip, and site-specific logs

Security configuration:

- **fail2ban**: Enabled and started
- **ufw**: Enabled with default-deny policy; SSH, HTTP, and HTTPS allowed
- **ssh**: Root login disabled; password authentication disabled

## File Structure

All paths below are relative to the cookbook root.

```text
Recipes:
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb

Providers:

Templates:
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb

Attributes:
cookbooks/nginx-multisite/attributes/default.rb

Files:
```

No provider files or static files are listed. The `cookbook_file` resources reference `test/index.html`, `ci/index.html`, and `status/index.html`, but those source files are absent from the supplied listing. The Ansible migration must provide equivalent static files or explicitly handle their absence.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Ansible must preserve this execution order through task-file imports or role dependencies.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban defaults: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Configures the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Applies UFW default deny, allows SSH on port `22`, allows HTTP on port `80`, allows HTTPS on port `443`, and enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, disabled ICMP redirects, disabled source routing, martian packet logging, ignored ICMP echo requests and broadcast pings, disabled IPv6, and TCP SYN flood protection.
   - Reloads `/etc/sysctl.d/99-security.conf` with `sysctl -p` when the sysctl template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` after SSH hardening changes.
   - Uses one package resource, two service resources, two template resources, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID file `/run/nginx.pid`, `768` worker connections, standard access and error logs, gzip, and the `conf.d` and `sites-enabled` include paths.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, request-rate zones for `login` and `api`, small client buffers, a `1k` client body limit, `10`-second connection timeouts, TLS 1.2 and TLS 1.3, a shared `10m` SSL session cache, a `10m` SSL session timeout, explicit ECDHE/DHE ciphers, and preferred server ciphers.
   - Enables and starts nginx.
   - Reloads nginx when the main or security configuration changes.
   - Creates `/opt/server/test` recursively with mode `0755` and deploys `test/index.html` to `/opt/server/test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` recursively with mode `0755` and deploys `ci/index.html` to `/opt/server/ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` recursively with mode `0755` and deploys `status/index.html` to `/opt/server/status/index.html` with mode `0644`.
   - The document roots and index files are owned by the nginx service user and group according to the recipe.
   - Uses one package, two templates, one service, three directory, and three cookbook-file resources.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a 2048-bit RSA self-signed certificate valid for 365 days for `test.cluster.local`.
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
     - Subject CN: `test.cluster.local`
   - Generates a 2048-bit RSA self-signed certificate valid for 365 days for `ci.cluster.local`.
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
     - Subject CN: `ci.cluster.local`
   - Generates a 2048-bit RSA self-signed certificate valid for 365 days for `status.cluster.local`.
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
     - Subject CN: `status.cluster.local`
   - Uses subject organization fields `C=US`, `ST=Example`, `L=Example`, `O=Example Org`, `OU=IT`, and `emailAddress=admin@example.com`.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Skips certificate generation only when both the certificate and private key already exist.
   - Reloads nginx after newly generated certificates.
   - The analyzed certificate command does not configure `subjectAltName`; validation must therefore check the certificate CN unless the Ansible implementation explicitly adds SAN entries.
   - Uses one package, one group, two directory, and three execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root:root` and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root:root` and mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
     - Document root: `/opt/server/test`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
   - Creates the symlink `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
     - Document root: `/opt/server/ci`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
   - Creates the symlink `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
     - Document root: `/opt/server/status`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
   - Creates the symlink `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Reloads nginx after site templates, symlinks, or default-site removal change.
   - Each HTTPS site listens on port `443`, enables HTTP/2, serves its site-specific document root, uses TLS 1.2 and TLS 1.3, sets HSTS and security headers, enables gzip, uses `try_files $uri $uri/ =404`, and denies `.htaccess`, `.git`, and `.svn` paths.
   - Configures site-specific access and error logs:
     - `/var/log/nginx/test.cluster.local_access.log`
     - `/var/log/nginx/test.cluster.local_error.log`
     - `/var/log/nginx/ci.cluster.local_access.log`
     - `/var/log/nginx/ci.cluster.local_error.log`
     - `/var/log/nginx/status.cluster.local_access.log`
     - `/var/log/nginx/status.cluster.local_error.log`
   - Uses two directory, three template, three link, and one file resources.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**: `fail2ban`, `nginx`, `sshd` or the platform-specific `ssh` service

**Firewall dependencies**: SSH port `22`, HTTP port `80`, HTTPS port `443`

## Credentials

**Detection Summary**: No external credentials or secret-management integrations detected. Three locally generated TLS private keys are sensitive files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No data bags, encrypted data bags, Chef Vault, Conjur, CyberArk, Vault attributes, environment-variable secrets, hardcoded passwords, API tokens, or database credentials are used. The literal `admin@example.com` value is a certificate contact field, not a credential.

### Self-signed TLS private keys

- **Variable(s)**: `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by `openssl req`
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts
- **Paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Required permissions**: Owner `root`, group `ssl-cert`, mode `0640`; parent directory `/etc/ssl/private` mode `0710`

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/etc/nginx/sites-enabled/default
/opt/server/test/index.html
/opt/server/ci/index.html
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/opt/server/test
/opt/server/ci
/opt/server/status
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/test.cluster.local_access.log
/var/log/nginx/test.cluster.local_error.log
/var/log/nginx/ci.cluster.local_access.log
/var/log/nginx/ci.cluster.local_error.log
/var/log/nginx/status.cluster.local_access.log
/var/log/nginx/status.cluster.local_error.log
```

**Service endpoints to check**:

- `test.cluster.local`: ports `80` and `443`
- `ci.cluster.local`: ports `80` and `443`
- `status.cluster.local`: ports `80` and `443`
- SSH: port `22`
- No application-specific Unix sockets or IPC endpoints are configured.

**Templates rendered**:

- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

The Ansible migration must also include a non-empty `ansible/Makefile` with a default `all` target that invokes `ansible-playbook`. The migration project must preserve this requirement in both `INPUT-AGENTS.md` and `EXPORT-AGENTS.md`.

## Pre-flight checks:

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
  rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl status nginx
systemctl status fail2ban
systemctl status sshd || systemctl status ssh

# Nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
grep -E 'user nginx|worker_processes|worker_connections|access_log|error_log|sites-enabled' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|ssl_protocols|ssl_ciphers|client_max_body_size' \
  /etc/nginx/conf.d/security.conf

# test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -text | grep -E 'Subject:|Public-Key'
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
test -f /opt/server/test/index.html
stat -c '%U:%G %a %n' /opt/server/test/index.html
readlink -f /etc/nginx/sites-enabled/test.cluster.local

# ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -text | grep -E 'Subject:|Public-Key'
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
test -f /opt/server/ci/index.html
stat -c '%U:%G %a %n' /opt/server/ci/index.html
readlink -f /etc/nginx/sites-enabled/ci.cluster.local

# status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -text | grep -E 'Subject:|Public-Key'
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
test -f /opt/server/status/index.html
stat -c '%U:%G %a %n' /opt/server/status/index.html
readlink -f /etc/nginx/sites-enabled/status.cluster.local

# Expected HTTP behavior for test.cluster.local, ci.cluster.local,
# and status.cluster.local:
# - HTTP returns 301
# - Location redirects to the corresponding https:// hostname
# - HTTPS returns 200 OK with security headers and HSTS
# - Each index file has mode 0644
# - Each private key has ownership root:ssl-cert and mode 640

# Site links and default-site removal
test ! -e /etc/nginx/sites-enabled/default
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

# Firewall
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
# Verify default deny, SSH/HTTP/HTTPS allowed, and UFW active.

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t 2>/dev/null || sshd -T

# Kernel security
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies

# Expected values:
# net.ipv4.conf.all.rp_filter = 1
# net.ipv4.conf.all.accept_redirects = 0
# net.ipv6.conf.all.disable_ipv6 = 1
# net.ipv4.tcp_syncookies = 1

# Fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Expected result: Server replied: pong, with all four jails enabled.

# Listening ports
ss -tlnp | grep -E ':(80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Logs
journalctl -u nginx --since "-10 minutes"
journalctl -u fail2ban --since "-10 minutes"
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
```