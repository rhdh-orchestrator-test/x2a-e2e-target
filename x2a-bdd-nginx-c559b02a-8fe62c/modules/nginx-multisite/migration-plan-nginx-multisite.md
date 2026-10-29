---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a hardened web server hosting three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts nginx, creates site document roots and static index files, generates self-signed RSA certificates, renders nginx virtual-host configurations with HTTP-to-HTTPS redirects, and applies fail2ban, UFW, SSH, sysctl, and nginx security hardening. Preserve the recipe execution order: security, nginx, SSL, then sites.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - HTTP endpoint: `test.cluster.local:80`
  - HTTPS endpoint: `test.cluster.local:443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Static file: `/opt/server/test/index.html`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - HTTP endpoint: `ci.cluster.local:80`
  - HTTPS endpoint: `ci.cluster.local:443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Static file: `/opt/server/ci/index.html`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - HTTP endpoint: `status.cluster.local:80`
  - HTTPS endpoint: `status.cluster.local:443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Static file: `/opt/server/status/index.html`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`

Security settings include enabled fail2ban and UFW, disabled SSH root login, and disabled SSH password authentication.

## File Structure

### Recipes

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

### Providers

```text
```

No provider files are used by the execution tree.

### Templates

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

### Attributes

```text
cookbooks/nginx-multisite/attributes/default.rb
```

### Files

No static files are listed in the supplied cookbook directory listing. The `nginx.rb` recipe references `test/index.html`, `ci/index.html`, and `status/index.html` through `cookbook_file`, but those source files are not present in the supplied file list.

## Module Explanation

The cookbook performs operations in this order, as defined by `cookbooks/nginx-multisite/recipes/default.rb`:

1. `nginx-multisite::security`
2. `nginx-multisite::nginx`
3. `nginx-multisite::ssl`
4. `nginx-multisite::sites`

1. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with bantime `3600`, findtime `600`, maxretry `3`, SSH protection, nginx authentication protection, request-rate protection, and bot-search protection.
   - Configures UFW default deny and allows SSH, HTTP, and HTTPS before enabling UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with reverse-path filtering, disabled redirects and source routing, martian logging, disabled IPv6, SYN cookies, and TCP hardening.
   - Reloads sysctl settings when the sysctl template changes.
   - Disables `PermitRootLogin` and `PasswordAuthentication` in `/etc/ssh/sshd_config`, restarting SSH only after changes.
   - Resources: package, service, template, and execute resources.

2. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Configures `www-data`, automatic worker processes, PID `/run/nginx.pid`, 768 worker connections, gzip, global logs, included `conf.d` files, and included enabled sites.
   - Configures nginx version hiding, request-rate zones (`login` at `10r/m`, `api` at `30r/m`), buffer restrictions, 10-second timeouts, TLS 1.2/1.3, and the configured cipher list.
   - Enables and starts nginx.
   - Creates `/opt/server/test` owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/test/index.html` from `test/index.html`, mode `0644`.
   - Creates `/opt/server/ci` owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/ci/index.html` from `ci/index.html`, mode `0644`.
   - Creates `/opt/server/status` owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/status/index.html` from `status/index.html`, mode `0644`.

3. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` as `root:root`, mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert`, mode `0710`.
   - Generates a self-signed 2048-bit RSA certificate for `test.cluster.local` at `/etc/ssl/certs/test.cluster.local.crt` with key `/etc/ssl/private/test.cluster.local.key`.
   - Generates a self-signed 2048-bit RSA certificate for `ci.cluster.local` at `/etc/ssl/certs/ci.cluster.local.crt` with key `/etc/ssl/private/ci.cluster.local.key`.
   - Generates a self-signed 2048-bit RSA certificate for `status.cluster.local` at `/etc/ssl/certs/status.cluster.local.crt` with key `/etc/ssl/private/status.cluster.local.key`.
   - All certificates are valid for `365` days and use the corresponding hostname as CN with subject email `admin@example.com`.
   - Certificate generation is skipped when both certificate and key exist.
   - Private keys use mode `0640` and owner/group `root:ssl-cert`.
   - Certificate creation triggers a delayed nginx reload.

4. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - Links `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - Links `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Links `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Each virtual host provides HTTP port `80`, redirect to HTTPS, HTTPS port `443`, HTTP/2, TLS 1.2/1.3, HSTS, security headers, gzip, `try_files`, protected `.htaccess`, `.git`, and `.svn` paths, and site-specific access and error logs.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**:
- `fail2ban`, enabled and started
- `nginx`, enabled and started
- `ssh`, restarted only when SSH hardening changes the configuration

## Credentials

**Detection Summary**: No application credentials, passwords, API keys, data bags, Chef Vault items, CyberArk references, or secret-manager integrations were detected. Three locally generated TLS private keys were identified.

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
- **Current storage**: Locally generated files; no secret manager or data bag is used.
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts.
- **Protection**: Directory mode `0710`; key mode `0640`; owner/group `root:ssl-cert`.

The certificate subject email `admin@example.com` is non-secret. The self-signed development certificates should be replaced with managed production certificates.

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

**Service endpoints to check**: SSH `22/tcp`; HTTP `test.cluster.local:80`, `ci.cluster.local:80`, `status.cluster.local:80`; HTTPS `test.cluster.local:443`, `ci.cluster.local:443`, `status.cluster.local:443`.

**Templates rendered**:
- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 rendering
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 rendering
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 rendering
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 rendering
- `site.conf.erb` → each of the three site configurations: 3 renderings total

## Pre-flight checks:

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Configuration validation
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'

# test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates

# ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates

# status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Document roots and enabled sites
test -f /opt/server/test/index.html
test -f /opt/server/ci/index.html
test -f /opt/server/status/index.html
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Network and process checks
ss -tlnp | grep ':22'
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
ps aux | grep '[n]ginx'

# UFW and SSH hardening
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'
grep '^PermitRootLogin no' /etc/ssh/sshd_config
grep '^PasswordAuthentication no' /etc/ssh/sshd_config

# Kernel hardening
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# Fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
journalctl -u nginx -n 50 --no-pager
journalctl -u fail2ban -n 50 --no-pager

# Ownership and permissions
stat -c '%U:%G %a %n' /opt/server/test
stat -c '%U:%G %a %n' /opt/server/ci
stat -c '%U:%G %a %n' /opt/server/status
stat -c '%U:%G %a %n' /etc/ssl/private
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected results include HTTP-to-HTTPS redirects, `200 OK` HTTPS responses for all three sites, matching certificate CNs, active UFW with default deny, allowed ports `22/tcp`, `80/tcp`, and `443/tcp`, disabled SSH root login and password authentication, active fail2ban jails, nginx listeners on ports `80` and `443`, and document roots owned by `www-data:www-data` with mode `0755`.