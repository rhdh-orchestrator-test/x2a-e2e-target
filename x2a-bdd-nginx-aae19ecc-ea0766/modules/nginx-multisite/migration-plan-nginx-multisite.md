---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies nginx, kernel, firewall, and SSH security hardening; generates local self-signed RSA certificates; creates site document roots and index files; enables SSH, HTTP, and HTTPS firewall access; disables SSH root login and password authentication; and enables all three nginx sites.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; destination `/opt/server/test/index.html`; `ssl_enabled: true`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; destination `/opt/server/ci/index.html`; `ssl_enabled: true`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; destination `/opt/server/status/index.html`; `ssl_enabled: true`

### Security components

- **fail2ban**: Intrusion-prevention service
  - Enabled: `true`
  - Configuration: `/etc/fail2ban/jail.local`
  - Service: `fail2ban`

- **ufw**: Host firewall
  - Enabled: `true`
  - Default incoming policy: deny
  - Allowed services: SSH, HTTP, and HTTPS
  - Allowed ports: `22/tcp`, `80/tcp`, and `443/tcp`

- **ssh**: SSH service hardening
  - Root login disabled: `true`
  - Password authentication disabled: `true`
  - Configuration: `/etc/ssh/sshd_config`
  - Service: `ssh`

## File Structure

Only files used by the execution flow are listed below.

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

No provider files or custom resources are used by the executed recipe flow.

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

The recipes deploy `test/index.html`, `ci/index.html`, and `status/index.html` through `cookbook_file`, but those static source files are not present in the supplied file listing. The Ansible migration must provide equivalent static files or otherwise preserve these source paths.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the ordering of security setup, nginx installation, certificate generation, and virtual-host configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban with a `3600`-second ban time, `600`-second find time, maximum retries of `3`, backend `auto`, SSH protection, nginx HTTP authentication protection, nginx request-limit protection, and nginx bot-search protection.
   - Configures UFW with default incoming policy `deny`, permits SSH, HTTP, and HTTPS, and enables the firewall.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies reverse-path filtering, disables IPv4 and IPv6 ICMP redirects, disables source routing, enables martian packet logging, ignores ICMP ping requests and directed broadcasts, disables IPv6 on all, default, and loopback interfaces, enables TCP SYN cookies, and configures TCP backlog and SYN retry settings.
   - Reloads `/etc/sysctl.d/99-security.conf` through a delayed `sysctl -p /etc/sysctl.d/99-security.conf` notification.
   - Changes `/etc/ssh/sshd_config` to `PermitRootLogin no` because `security.ssh.disable_root` is `true`.
   - Changes `/etc/ssh/sshd_config` to `PasswordAuthentication no` because `security.ssh.password_auth` is `false`.
   - Restarts `ssh` only when either SSH hardening setting changes.
   - Resources: one package resource installing two packages, two services (`fail2ban`, `ssh`), two templates, and eight execute resources (`ufw_default_deny`, `ufw_allow_ssh`, `ufw_allow_http`, `ufw_allow_https`, `ufw_enable`, `reload_sysctl`, `disable root login`, and `disable password auth`).

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `www-data`, automatic worker processes, PID file `/run/nginx.pid`, `768` worker connections, standard nginx access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, rate zones `login` (`10m`, `10r/m`) and `api` (`10m`, `30r/m`), small buffers, a `1k` maximum client body size, 10-second client body/header/send timeouts, TLS 1.2 and TLS 1.3, a shared 10 MB SSL session cache, a 10-minute SSL session timeout, explicit ECDHE/DHE ciphers, and preferred server ciphers.
   - Enables and starts the `nginx` service.
   - Creates document roots and static files in exactly these iterations:
     - **`test.cluster.local`**: creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`; deploys `test/index.html` to `/opt/server/test/index.html` owned by `www-data:www-data` with mode `0644`.
     - **`ci.cluster.local`**: creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`; deploys `ci/index.html` to `/opt/server/ci/index.html` owned by `www-data:www-data` with mode `0644`.
     - **`status.cluster.local`**: creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`; deploys `status/index.html` to `/opt/server/status/index.html` owned by `www-data:www-data` with mode `0644`.
   - Resources: one package, two templates, one service, three directories, and three `cookbook_file` resources.
   - Notifies nginx reload when nginx configuration changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates self-signed certificates using `openssl req -x509 -nodes -days 365 -newkey rsa:2048`.
   - Uses subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Generates certificates in exactly these iterations:
     - **`test.cluster.local`**: certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; RSA 2048-bit; validity 365 days; key mode `0640`, owner `root`, group `ssl-cert`.
     - **`ci.cluster.local`**: certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; RSA 2048-bit; validity 365 days; key mode `0640`, owner `root`, group `ssl-cert`.
     - **`status.cluster.local`**: certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; RSA 2048-bit; validity 365 days; key mode `0640`, owner `root`, group `ssl-cert`.
   - Skips certificate generation when both the certificate and key already exist.
   - Sends a delayed nginx reload notification after a new certificate is generated.
   - Resources: one package resource installing two packages, one group, two directories, and three execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` and creates an enabled-site symlink in exactly these iterations:
     - **`test.cluster.local`**:
       - Renders to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
       - Uses document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`, and `ssl_enabled: true`.
       - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
     - **`ci.cluster.local`**:
       - Renders to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
       - Uses document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`, and `ssl_enabled: true`.
       - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
     - **`status.cluster.local`**:
       - Renders to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
       - Uses document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`, and `ssl_enabled: true`.
       - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Each site has an HTTP listener on port `80` redirecting to HTTPS and an HTTP/2 HTTPS listener on port `443`.
   - Configures TLS 1.2 and TLS 1.3, one-year HSTS with subdomain inclusion, security headers, gzip, `try_files $uri $uri/ =404`, denial of `.htaccess`, `.git`, and `.svn` paths, and site-specific access and error logs.
   - Site log files are:
     - `/var/log/nginx/test.cluster.local_access.log`
     - `/var/log/nginx/test.cluster.local_error.log`
     - `/var/log/nginx/ci.cluster.local_access.log`
     - `/var/log/nginx/ci.cluster.local_error.log`
     - `/var/log/nginx/status.cluster.local_access.log`
     - `/var/log/nginx/status.cluster.local_error.log`
   - Resources: three templates, three links, and one file.
   - Template, link, and default-site removal changes notify nginx reload.

## Dependencies

**External cookbook dependencies**: None specified in the supplied metadata.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**: `fail2ban`, `nginx`, and `ssh`. The SSH service restarts only when SSH hardening configuration changes.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`.

## Credentials

**Detection Summary**: No credentials, passwords, API tokens, data bags, vault references, or secret-manager integrations were detected across the cookbook files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. The certificate subject contains the non-secret email address `admin@example.com`.

The cookbook generates self-signed development certificates locally rather than retrieving private credentials. The generated private keys are operationally sensitive:

- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`

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
- `/etc/nginx/sites-enabled/default` should be absent
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
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
- SSH: `22`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: three times
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks:

```bash
# Check installed packages
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Check service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh

# Check nginx configuration syntax
nginx -t

# Check enabled sites individually
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Check nginx configuration
grep -E 'user |worker_processes|worker_connections|access_log|error_log|gzip ' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|ssl_protocols|ssl_ciphers|client_body_timeout|send_timeout' \
  /etc/nginx/conf.d/security.conf
nginx -T | grep -A 20 -B 5 'server_name test.cluster.local'
nginx -T | grep -A 20 -B 5 'server_name ci.cluster.local'
nginx -T | grep -A 20 -B 5 'server_name status.cluster.local'

# Check test.cluster.local document root and content
ls -ld /opt/server/test
ls -l /opt/server/test/index.html

# Check ci.cluster.local document root and content
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html

# Check status.cluster.local document root and content
ls -ld /opt/server/status
ls -l /opt/server/status/index.html

# Check test.cluster.local certificate and key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%A %U:%G %n' /etc/ssl/private/test.cluster.local.key

# Check ci.cluster.local certificate and key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%A %U:%G %n' /etc/ssl/private/ci.cluster.local.key

# Check status.cluster.local certificate and key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%A %U:%G %n' /etc/ssl/private/status.cluster.local.key

# Check certificate common names
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject

# Check HTTP-to-HTTPS redirect for test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/

# Check HTTP-to-HTTPS redirect for ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/

# Check HTTP-to-HTTPS redirect for status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/

# Expected result for each HTTP request:
# HTTP/1.1 301 Moved Permanently
# Location: https://<site_name>/

# Check HTTPS response for test.cluster.local
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# Check HTTPS response for ci.cluster.local
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# Check HTTPS response for status.cluster.local
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Check HTTPS content for test.cluster.local
curl -k --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# Check HTTPS content for ci.cluster.local
curl -k --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# Check HTTPS content for status.cluster.local
curl -k --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Check listening ports
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
ss -tlnp | grep ':22 '

# Check firewall status and rules
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# Check fail2ban configuration and jails
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Check kernel security settings
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# Check SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# Check nginx logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log

# Check service logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
journalctl -u ssh --no-pager -n 50
```

The Ansible implementation should use handlers for:

- Reloading nginx when `/etc/nginx/nginx.conf` changes.
- Reloading nginx when `/etc/nginx/conf.d/security.conf` changes.
- Reloading nginx when any site configuration or enabled-site symlink changes.
- Reloading nginx after a new certificate is generated.
- Restarting fail2ban when `/etc/fail2ban/jail.local` changes.
- Reloading sysctl settings when `/etc/sysctl.d/99-security.conf` changes.
- Restarting SSH when either SSH hardening setting changes.