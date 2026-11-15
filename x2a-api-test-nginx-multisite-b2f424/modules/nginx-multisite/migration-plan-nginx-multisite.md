---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three HTTPS-enabled virtual sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and locally generated self-signed certificates; deploys global nginx security settings and per-site virtual-host configurations; redirects HTTP to HTTPS; applies firewall, kernel, SSH, and fail2ban hardening; and enables nginx and fail2ban.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS virtual host serving the test site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS virtual host serving the CI site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS virtual host serving the status site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

Security namespaces configured by the cookbook are `fail2ban`, `ufw`, and `ssh`. The original attributes identify fail2ban and UFW as enabled, root SSH login as disabled, and SSH password authentication as disabled; these exact attribute values should be verified against the source attributes during migration.

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

No static files are listed in the supplied cookbook directory structure. The nginx recipe references these cookbook-file sources, which must be supplied or recreated for the Ansible migration:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role must preserve this logical execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures fail2ban defaults of `bantime=3600`, `findtime=600`, `maxretry=3`, and backend `auto`.
   - Enables the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails with their configured ports, log paths, and retry limits.
   - Sets the UFW default policy to deny.
   - Allows SSH on `22/tcp`, HTTP on `80/tcp`, and HTTPS on `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Configures reverse-path filtering, disables ICMP redirects and source routing, enables martian packet logging and TCP SYN cookies, disables IPv6, and applies the configured TCP retry and backlog values.
   - Reloads sysctl with `sysctl -p /etc/sysctl.d/99-security.conf` when the sysctl template changes.
   - When enabled by the source attributes, sets `PermitRootLogin no` and `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Notifies delayed restarts of `fail2ban` and `sshd` when their configuration changes.
   - Resources: package (1 resource containing 2 packages), service (2), template (2), execute (8).

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Configures the nginx worker user, automatic worker processes, PID file `/run/nginx.pid`, `worker_connections 768`, keepalive timeout `65`, access and error logs, gzip, and the `conf.d` and `sites-enabled` include paths.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Configures version hiding, rate-limit zones, small client buffers, a `1k` maximum client body size, client/header/send timeouts of `10`, TLS 1.2 and TLS 1.3, the configured cipher list, a shared SSL session cache of `10m`, and an SSL session timeout of `10m`.
   - Enables and starts nginx.
   - Iterates over **test.cluster.local**:
     - Creates `/opt/server/test` owned by `nginx:nginx` with mode `0755`.
     - Deploys `/opt/server/test/index.html` from `test/index.html`, owned by `nginx:nginx` with mode `0644`.
   - Iterates over **ci.cluster.local**:
     - Creates `/opt/server/ci` owned by `nginx:nginx` with mode `0755`.
     - Deploys `/opt/server/ci/index.html` from `ci/index.html`, owned by `nginx:nginx` with mode `0644`.
   - Iterates over **status.cluster.local**:
     - Creates `/opt/server/status` owned by `nginx:nginx` with mode `0755`.
     - Deploys `/opt/server/status/index.html` from `status/index.html`, owned by `nginx:nginx` with mode `0644`.
   - The global nginx templates notify a delayed nginx reload. The cookbook-file resources do not notify a reload.
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3).

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` as `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert` with mode `0710`.
   - Iterates over **test.cluster.local**:
     - Generates `/etc/ssl/certs/test.cluster.local.crt`.
     - Generates `/etc/ssl/private/test.cluster.local.key`.
     - Uses a 2048-bit RSA self-signed certificate valid for 365 days with CN `test.cluster.local`.
     - Sets the private key to `root:ssl-cert` with mode `0640`.
   - Iterates over **ci.cluster.local**:
     - Generates `/etc/ssl/certs/ci.cluster.local.crt`.
     - Generates `/etc/ssl/private/ci.cluster.local.key`.
     - Uses a 2048-bit RSA self-signed certificate valid for 365 days with CN `ci.cluster.local`.
     - Sets the private key to `root:ssl-cert` with mode `0640`.
   - Iterates over **status.cluster.local**:
     - Generates `/etc/ssl/certs/status.cluster.local.crt`.
     - Generates `/etc/ssl/private/status.cluster.local.key`.
     - Uses a 2048-bit RSA self-signed certificate valid for 365 days with CN `status.cluster.local`.
     - Sets the private key to `root:ssl-cert` with mode `0640`.
   - Certificate generation is skipped when both the certificate and key already exist.
   - Each generated certificate notifies a delayed nginx reload.
   - Resources: package (1 resource containing 2 packages), group (1), directory (2), execute (3).

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Executes one directory loop containing 3 directory resources, as indicated by the structured execution tree. The supplied validation does not establish that this recipe creates `/etc/nginx/sites-available` or `/etc/nginx/sites-enabled`; those paths must not be attributed to this recipe without source confirmation.
   - Iterates over **test.cluster.local**:
     - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
     - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to the available-site configuration.
   - Iterates over **ci.cluster.local**:
     - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
     - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to the available-site configuration.
   - Iterates over **status.cluster.local**:
     - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
     - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to the available-site configuration.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Each site template and symbolic link notifies a delayed nginx reload.
   - Each virtual host listens on port `80`, redirects HTTP to HTTPS with status `301`, listens on port `443` with HTTP/2, and uses its site-specific document root, certificate, private key, logs, security headers, gzip, static-file routing, and `.git`, `.svn`, and `.htaccess` denial rules.
   - Resources: directory (3), template (3), link (3), file deletion (1).
   - `cookbooks/nginx-multisite/templates/default/site.conf.erb` renders 3 times:
     - Once for `/etc/nginx/sites-available/test.cluster.local`
     - Once for `/etc/nginx/sites-available/ci.cluster.local`
     - Once for `/etc/nginx/sites-available/status.cluster.local`

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**:
- `nginx`: enabled and started; reloaded when nginx configuration, site configuration, site links, or certificates change
- `fail2ban`: enabled and started; restarted when `/etc/fail2ban/jail.local` changes
- `sshd`: restarted when SSH hardening settings change

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`

## Credentials

**Detection Summary**: 0 runtime credentials detected across the analyzed cookbook files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed TLS private keys
- **Variable(s)**: `/etc/ssl/private/test.cluster.local.key`, `/etc/ssl/private/ci.cluster.local.key`, `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files
- **Usage context**: nginx HTTPS private keys
- **Generation method**: `openssl req -x509 -nodes -days 365 -newkey rsa:2048`
- **Permissions**: `root:ssl-cert`, mode `0640`

### TLS certificates
- **Variable(s)**: `/etc/ssl/certs/test.cluster.local.crt`, `/etc/ssl/certs/ci.cluster.local.crt`, `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: nginx HTTPS certificate configuration
- **Validity**: 365 days
- **Certificate subject email**: `admin@example.com`

No data bags, Chef Vault, Conjur, CyberArk, Vault, AWS Secrets Manager, environment-variable secrets, service passwords, or database credentials were detected.

## Checks for the Migration

**Files to verify**:
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
- `/opt/server/status/index.html`
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
- `test.cluster.local:80`
- `test.cluster.local:443`
- `ci.cluster.local:80`
- `ci.cluster.local:443`
- `status.cluster.local:80`
- `status.cluster.local:443`
- SSH `22/tcp`
- No cookbook-specific Unix socket

**Templates rendered**:
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

## Pre-flight checks:

```bash
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-active nginx
systemctl is-active fail2ban
systemctl is-active sshd

nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

ufw status verbose
ufw status numbered
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

sshd -t
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config

sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries

test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected site behavior:

- HTTP requests to `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` return a `301` redirect to HTTPS.
- HTTPS requests return successfully when the corresponding index file exists.
- Each certificate contains its matching site name as the common name.
- Each private key is owned by `root:ssl-cert` with mode `0640`.
- nginx listens on TCP ports `80` and `443`.
- UFW is active with a default deny policy and allows SSH, HTTP, and HTTPS.