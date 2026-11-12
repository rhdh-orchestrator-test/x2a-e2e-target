---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and enables nginx and fail2ban, configures UFW, generates development self-signed certificates, creates site document roots and placeholder index files, applies nginx TLS and security settings, configures HTTP-to-HTTPS redirects, applies kernel network hardening, and disables SSH root login and password authentication. No external cookbook dependencies or secret-management integrations were identified in the supplied plan. Some detailed template and attribute values require verification against the source files before production migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: nginx SSL virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`
  - Placeholder file: `/opt/server/test/index.html`, sourced from `test/index.html`
  - Logs: `/var/log/nginx/test.cluster.local_access.log`, `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: nginx SSL virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`
  - Placeholder file: `/opt/server/ci/index.html`, sourced from `ci/index.html`
  - Logs: `/var/log/nginx/ci.cluster.local_access.log`, `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: nginx SSL virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`
  - Placeholder file: `/opt/server/status/index.html`, sourced from `status/index.html`
  - Logs: `/var/log/nginx/status.cluster.local_access.log`, `/var/log/nginx/status.cluster.local_error.log`

**Security configuration**:

- Fail2ban is configured as enabled in the supplied plan.
- UFW is configured as enabled in the supplied plan.
- SSH root login is disabled.
- SSH password authentication is disabled.
- The exact security attribute values should be verified against `cookbooks/nginx-multisite/attributes/default.rb` before migration.

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
    ├── test/
    │   └── index.html
    ├── ci/
    │   └── index.html
    └── status/
        └── index.html
```

No custom providers are used. The supplied directory listing did not include static file entries, although the recipes reference `test/index.html`, `ci/index.html`, and `status/index.html`. Equivalent content must be provided for the three deployed index files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Establishes the migration sequence: host security, nginx installation, certificate generation, then site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts fail2ban.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures fail2ban jails for SSH, nginx HTTP authentication, nginx request limits, and nginx bot searches.
   - Applies UFW defaults and rules:
     - Default incoming policy: deny
     - SSH: `22/tcp`
     - HTTP: `80/tcp`
     - HTTPS: `443/tcp`
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Applies reverse-path filtering, redirect and source-route suppression, ICMP hardening, IPv6 disablement, martian logging, and TCP SYN-flood protection.
   - Reloads sysctl settings with `sysctl -p /etc/sysctl.d/99-security.conf`.
   - Updates `/etc/ssh/sshd_config` to set:
     - `PermitRootLogin no`
     - `PasswordAuthentication no`
   - Restarts the platform SSH service only when either SSH setting changes.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Configures nginx worker processes, worker connections, logging, gzip, keepalive behavior, included configuration paths, TLS protocols, TLS session settings, request limits, and security options.
   - Enables and starts nginx.
   - Reloads nginx when the main configuration or security configuration changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Evaluates the following three SSL-enabled sites:
     - **test.cluster.local**
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Key: `/etc/ssl/private/test.cluster.local.key`
       - Common name: `test.cluster.local`
     - **ci.cluster.local**
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Key: `/etc/ssl/private/ci.cluster.local.key`
       - Common name: `ci.cluster.local`
     - **status.cluster.local**
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Key: `/etc/ssl/private/status.cluster.local.key`
       - Common name: `status.cluster.local`
   - Generates missing certificates with OpenSSL using RSA 2048-bit keys and 365-day self-signed certificates.
   - Sets generated private keys to `root:ssl-cert` with mode `0640`.
   - Reloads nginx after newly generated certificates are installed.
   - Certificate and key generation is skipped when both files already exist.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled`, owned by `root:root` with mode `0755`.
   - Creates the following site document roots with owner/group `nginx:nginx` and mode `0755`:
     - `/opt/server/test`
     - `/opt/server/ci`
     - `/opt/server/status`
   - Deploys the following index files with owner/group `nginx:nginx` and mode `0644`:
     - `test/index.html` to `/opt/server/test/index.html`
     - `ci/index.html` to `/opt/server/ci/index.html`
     - `status/index.html` to `/opt/server/status/index.html`
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - **test.cluster.local** to `/etc/nginx/sites-available/test.cluster.local`
     - **ci.cluster.local** to `/etc/nginx/sites-available/ci.cluster.local`
     - **status.cluster.local** to `/etc/nginx/sites-available/status.cluster.local`
   - Creates enabled-site links:
     - `/etc/nginx/sites-enabled/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local`
   - Configures HTTP port `80` redirects to HTTPS port `443`, HTTP/2, TLS 1.2 and 1.3, HSTS, security headers, gzip, `try_files`, protected files, and per-site logging.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Reloads nginx after site configuration, symlink, or default-site changes.

## Dependencies

**External cookbook dependencies**: None listed.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started; restarted after jail configuration changes
- `nginx`: enabled and started; reloaded after nginx, certificate, site, symlink, or default-site changes
- `sshd` or `ssh`: restarted only after SSH hardening changes

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Network dependencies**:

- TCP `22`: SSH
- TCP `80`: HTTP
- TCP `443`: HTTPS
- No explicit bind address is configured.

## Credentials

**Detection Summary**: No external credential provider or secret-management integration was identified in the supplied plan. Complete credential-scan results for all recipes, templates, and attributes should be confirmed before migration.

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
- **Current storage**: Generated locally by OpenSSL; not retrieved from a data bag, vault, or external secret manager.
- **Usage context**: TLS private keys used by nginx HTTPS virtual hosts.
- **Permissions**: `root:ssl-cert`, mode `0640`.

### TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificates.
- **Usage context**: TLS certificates for the three nginx HTTPS virtual hosts.
- **Validity**: 365 days.
- **Subject email**: `admin@example.com`.
- **Sensitive status**: The email address is configuration data, not an authentication secret.

No password, API token, database credential, data bag, Chef Vault item, Conjur variable, CyberArk lookup, or environment-variable secret was identified in the supplied plan. This conclusion remains subject to verification against the source file contents.

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

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`

**Firewall endpoints to check**:

- SSH TCP `22`
- HTTP TCP `80`
- HTTPS TCP `443`

**Logs to verify**:

- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`
- `/var/log/auth.log`

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `sysctl-security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks

```bash
systemctl status nginx
systemctl status fail2ban
systemctl status sshd || systemctl status ssh
systemctl is-enabled nginx
systemctl is-enabled fail2ban

nginx -t
nginx -T
test ! -e /etc/nginx/sites-enabled/default

grep -E 'worker_processes|worker_connections|access_log|error_log|gzip' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

grep '^PermitRootLogin no' /etc/ssh/sshd_config
grep '^PasswordAuthentication no' /etc/ssh/sshd_config
sshd -t 2>/dev/null || sshd -t

sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
```

### `test.cluster.local`

```bash
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
stat -c '%U:%G %a %n' /opt/server/test /opt/server/test/index.html
readlink -f /etc/nginx/sites-enabled/test.cluster.local

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

openssl x509 -noout -modulus \
  -in /etc/ssl/certs/test.cluster.local.crt | openssl sha256
openssl rsa -noout -modulus \
  -in /etc/ssl/private/test.cluster.local.key | openssl sha256
```

Expected values:

- Document root: `/opt/server/test`
- Index ownership and mode: `nginx:nginx`, `0644`
- Root ownership and mode: `nginx:nginx`, `0755`
- Symlink target: `/etc/nginx/sites-available/test.cluster.local`
- HTTP response: `301` redirect to `https://test.cluster.local/`
- HTTPS response: successful response with HSTS and nginx security headers
- Key ownership and mode: `root:ssl-cert`, `0640`

### `ci.cluster.local`

```bash
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
stat -c '%U:%G %a %n' /opt/server/ci /opt/server/ci/index.html
readlink -f /etc/nginx/sites-enabled/ci.cluster.local

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

openssl x509 -noout -modulus \
  -in /etc/ssl/certs/ci.cluster.local.crt | openssl sha256
openssl rsa -noout -modulus \
  -in /etc/ssl/private/ci.cluster.local.key | openssl sha256
```

Expected values:

- Document root: `/opt/server/ci`
- Index ownership and mode: `nginx:nginx`, `0644`
- Root ownership and mode: `nginx:nginx`, `0755`
- Symlink target: `/etc/nginx/sites-available/ci.cluster.local`
- HTTP response: `301` redirect to `https://ci.cluster.local/`
- HTTPS response: successful response with HSTS and nginx security headers
- Key ownership and mode: `root:ssl-cert`, `0640`

### `status.cluster.local`

```bash
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
stat -c '%U:%G %a %n' /opt/server/status /opt/server/status/index.html
readlink -f /etc/nginx/sites-enabled/status.cluster.local

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

openssl x509 -noout -modulus \
  -in /etc/ssl/certs/status.cluster.local.crt | openssl sha256
openssl rsa -noout -modulus \
  -in /etc/ssl/private/status.cluster.local.key | openssl sha256
```

Expected values:

- Document root: `/opt/server/status`
- Index ownership and mode: `nginx:nginx`, `0644`
- Root ownership and mode: `nginx:nginx`, `0755`
- Symlink target: `/etc/nginx/sites-available/status.cluster.local`
- HTTP response: `301` redirect to `https://status.cluster.local/`
- HTTPS response: successful response with HSTS and nginx security headers
- Key ownership and mode: `root:ssl-cert`, `0640`

### Log and configuration checks

```bash
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
tail -n 50 /var/log/auth.log

grep -E 'bantime|findtime|maxretry|backend' \
  /etc/fail2ban/jail.local
grep -E 'rp_filter|accept_redirects|send_redirects|accept_source_route|disable_ipv6|tcp_syncookies|tcp_max_syn_backlog' \
  /etc/sysctl.d/99-security.conf
```

All three certificate/key modulus hash pairs must match. The nginx configuration must pass `nginx -t`, all three enabled-site links must resolve to their corresponding available-site files, and the default nginx site must be absent.