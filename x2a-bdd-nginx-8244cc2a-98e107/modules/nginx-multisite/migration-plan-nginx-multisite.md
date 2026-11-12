---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a multisite HTTPS web server with three virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and sample index-file destinations; generates self-signed certificates; deploys nginx virtual-host configurations; enables HTTP-to-HTTPS redirects; and applies SSH, firewall, sysctl, rate-limiting, and security-header hardening. The Ansible implementation must preserve the execution order: security, nginx base configuration, SSL setup, and site configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The `nginx.sites` collection contains exactly three configured sites. All three have SSL enabled.

- **test.cluster.local**: HTTPS nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

**Security services**:

- **fail2ban**
  - Package: `fail2ban`
  - Service: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Enabled and started by default: `true`

- **ufw**
  - Package: `ufw`
  - Firewall policy: default deny
  - Allowed services: SSH, HTTP, HTTPS
  - Enabled by default: `true`

- **ssh**
  - Root login disabled: `true`
  - Password authentication disabled: `true`
  - Configuration: `/etc/ssh/sshd_config`
  - Service notified: `sshd`

## File Structure

The following files are relevant to the migration and are listed using paths from the repository root.

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

No provider files are used by the execution tree. The structurally detected `resources/lineinfile.rb` is not part of the supplied execution tree and must not be included in the migration.

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

No static files are listed in the supplied cookbook directory listing. The recipe references `cookbook_file` resources for site-specific `index.html` files, but their source files are not included in the supplied file structure and must not be invented.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible entry point must import task files in the same order: `security.yml`, `nginx.yml`, `ssl.yml`, and `sites.yml`.
   - Do not reorder SSL and site configuration because the site templates reference the certificate and key paths established by the SSL tasks.
   - Resources: four `include_recipe` resources.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the exact packages `fail2ban` and `ufw` with no pinned versions.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban with a 3,600-second ban time, 600-second find time, three retries, the `auto` backend, SSH protection, nginx HTTP-auth protection, request-rate protection, bot-search protection, and nginx error/access-log patterns.
   - Uses `/var/log/auth.log`, `/var/log/nginx/*error.log`, and `/var/log/nginx/*access.log`.
   - Restarts fail2ban through a delayed handler when the jail configuration changes.
   - Configures UFW with a default incoming policy of deny.
   - Allows SSH on TCP `22`, HTTP on TCP `80`, and HTTPS on TCP `443`.
   - Enables UFW only after the default policy and all three allow rules are present.
   - Uses idempotent firewall tasks equivalent to:
     - `ufw --force default deny`
     - `ufw allow ssh`
     - `ufw allow http`
     - `ufw allow https`
     - `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, disabled IPv4 and IPv6 ICMP redirects, disabled source routing, martian packet logging, ignored ICMP echo requests and broadcast pings, disabled IPv6 on all/default/loopback interfaces, TCP SYN cookies, and TCP backlog/retry values.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` only through a notification handler when the sysctl template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` because `security.ssh.disable_root` is `true`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` because `security.ssh.password_auth` is `false`.
   - Restarts the platform-appropriate SSH service only when either SSH setting changes. The Chef resource explicitly names `sshd`; validate whether the target distribution uses `sshd` or `ssh`.
   - Security resources: one package collection containing `fail2ban` and `ufw`, two service resources, two templates, seven execute resources, and two conditional SSH configuration resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Preserves the nginx user `nginx`, automatic worker processes, PID `/run/nginx.pid`, 768 worker connections, standard access/error logs, 65-second keepalive timeout, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Preserves `server_tokens off`, the `login` request-rate zone at `10m` and `10r/m`, the `api` zone at `10m` and `30r/m`, 1K client buffers, a 1K maximum body size, TLS 1.2 and 1.3, the shared `SSL:10m` session cache, the 10-minute SSL session timeout, the configured ECDHE/DHE ciphers, and server cipher preference.
   - Reloads nginx through a delayed handler when either nginx template changes.
   - Enables and starts nginx.
   - Creates the following document roots and index-file destinations:
     - **test.cluster.local**:
       - Directory `/opt/server/test`, owner `nginx`, group `nginx`, mode `0755`, recursive creation.
       - Source `test/index.html` to `/opt/server/test/index.html`, owner `nginx`, group `nginx`, mode `0644`.
     - **ci.cluster.local**:
       - Directory `/opt/server/ci`, owner `nginx`, group `nginx`, mode `0755`, recursive creation.
       - Source `ci/index.html` to `/opt/server/ci/index.html`, owner `nginx`, group `nginx`, mode `0644`.
     - **status.cluster.local**:
       - Directory `/opt/server/status`, owner `nginx`, group `nginx`, mode `0755`, recursive creation.
       - Source `status/index.html` to `/opt/server/status/index.html`, owner `nginx`, group `nginx`, mode `0644`.
   - The static source files are not present in the supplied file structure and must be obtained or provided separately.
   - Resources: one package, two templates, one service, three directory iterations, and three `cookbook_file` iterations.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Generates certificates for all three SSL-enabled sites:
     - **test.cluster.local**:
       - Certificate `/etc/ssl/certs/test.cluster.local.crt`
       - Private key `/etc/ssl/private/test.cluster.local.key`
       - Common Name `test.cluster.local`
     - **ci.cluster.local**:
       - Certificate `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key `/etc/ssl/private/ci.cluster.local.key`
       - Common Name `ci.cluster.local`
     - **status.cluster.local**:
       - Certificate `/etc/ssl/certs/status.cluster.local.crt`
       - Private key `/etc/ssl/private/status.cluster.local.key`
       - Common Name `status.cluster.local`
   - Each certificate is self-signed, uses an RSA 2048-bit key, is valid for 365 days, uses `-nodes`, and has subject email `admin@example.com`.
   - Each private key is mode `0640`, owned by `root`, and assigned to group `ssl-cert`.
   - Certificate generation occurs only when both the certificate and key are absent. Existing certificate/key pairs must not be regenerated.
   - Certificate generation for each of the three sites notifies the nginx reload handler.
   - Resources: one package collection containing two packages, one group, two directories, and three conditional certificate-generation executions.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates the nginx site-directory resources represented by the structured analysis, with three directory-resource iterations keyed by:
     - **test.cluster.local**
     - **ci.cluster.local**
     - **status.cluster.local**
   - The recipe also ensures the nginx configuration directories `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` exist with owner `root`, group `root`, and mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` exactly three times:
     - **test.cluster.local**:
       - Destination `/etc/nginx/sites-available/test.cluster.local`
       - `server_name`: `test.cluster.local`
       - `document_root`: `/opt/server/test`
       - `ssl_enabled`: `true`
       - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
       - `key_file`: `/etc/ssl/private/test.cluster.local.key`
     - **ci.cluster.local**:
       - Destination `/etc/nginx/sites-available/ci.cluster.local`
       - `server_name`: `ci.cluster.local`
       - `document_root`: `/opt/server/ci`
       - `ssl_enabled`: `true`
       - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
       - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
     - **status.cluster.local**:
       - Destination `/etc/nginx/sites-available/status.cluster.local`
       - `server_name`: `status.cluster.local`
       - `document_root`: `/opt/server/status`
       - `ssl_enabled`: `true`
       - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
       - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Each rendered site file has mode `0644`.
   - Each site listens on HTTP `80`, redirects HTTP to HTTPS with status `301`, and listens on HTTPS `443` with SSL and HTTP/2.
   - Each site serves its configured document root, uses `index.html`, `index.htm`, and `index.php`, enables TLS 1.2 and 1.3 and HSTS, adds the configured security headers, enables gzip, returns `404` for missing files, denies `.htaccess`, `.git`, and `.svn` paths, and writes site-specific access and error logs.
   - Creates these enabled-site links:
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
   - Removes `/etc/nginx/sites-enabled/default`.
   - Changes to site templates, links, or default-site removal notify the nginx reload handler.
   - Sites recipe resources: three directory resources from the site iteration, three template resources, three links, and one file-removal resource.

## Dependencies

**External cookbook dependencies**: None identified in the supplied metadata or execution tree.

**Chef version requirement**: Chef `>= 16.0`

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: restartable through delayed notifications; not started or enabled by this cookbook

**Network service dependencies**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`

## Credentials

**Detection Summary**: 0 credential-store credentials detected across the supplied cookbook files. Generated TLS private keys are sensitive files but are created locally and are not retrieved from a credential store.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

### Self-signed TLS private keys

- **Variable(s)**:
  - `key_file`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; not stored in a vault or data bag
- **Usage context**: nginx TLS private keys
- **Permissions**: mode `0640`, owner `root`, group `ssl-cert`

### Certificate subject email

- **Variable/value**: `admin@example.com`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded non-secret certificate subject value
- **Usage context**: Subject email in each self-signed certificate

No database credentials, SSH private keys, application passwords, API keys, or embedded connection strings were detected.

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
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/ssl/certs`
- `/etc/ssl/private`

**Service endpoints to check**:

- **test.cluster.local**: HTTP TCP `80`; HTTPS TCP `443`
- **ci.cluster.local**: HTTP TCP `80`; HTTPS TCP `443`
- **status.cluster.local**: HTTP TCP `80`; HTTPS TCP `443`
- SSH firewall allowance: TCP `22`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

**Total template render operations**: 7

**Handlers to verify**:

- **Reload nginx**:
  - Triggered by `/etc/nginx/nginx.conf`
  - Triggered by `/etc/nginx/conf.d/security.conf`
  - Triggered by all three site templates
  - Triggered by all three enabled-site links
  - Triggered by removal of `/etc/nginx/sites-enabled/default`
  - Triggered after generation of any of the three certificate/key pairs
- **Restart fail2ban**:
  - Triggered by `/etc/fail2ban/jail.local`
- **Reload sysctl**:
  - Triggered by `/etc/sysctl.d/99-security.conf`
- **Restart sshd**:
  - Triggered by changes to `PermitRootLogin`
  - Triggered by changes to `PasswordAuthentication`

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# SSH service name and hardening
systemctl status sshd || systemctl status ssh
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no$' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no$' /etc/ssh/sshd_config

# Firewall policy and rules
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# Sysctl configuration
test -f /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.tcp_syncookies

# nginx configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
grep -E 'user nginx|worker_processes|worker_connections|access_log|error_log|gzip on|sites-enabled' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Site directories, links, and default-site removal
ls -ld /etc/nginx/sites-available /etc/nginx/sites-enabled
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# SSL files and permissions
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%a %U:%G %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key
```

Expected service state:

- nginx is active and enabled.
- fail2ban is active and enabled.
- UFW is active with default incoming policy deny.
- SSH, HTTP, and HTTPS firewall rules are present.

### test.cluster.local

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: test.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: test.cluster.local' https://127.0.0.1/ | head
```

Expected result:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200 OK` when `/opt/server/test/index.html` exists.
- The HTTPS response contains HSTS and the configured security headers.

### ci.cluster.local

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: ci.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: ci.cluster.local' https://127.0.0.1/ | head
```

Expected result:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200 OK` when `/opt/server/ci/index.html` exists.
- The HTTPS response contains HSTS and the configured security headers.

### status.cluster.local

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: status.cluster.local' https://127.0.0.1/
curl -k -s -H 'Host: status.cluster.local' https://127.0.0.1/ | head
```

Expected result:

- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200 OK` when `/opt/server/status/index.html` exists.
- The HTTPS response contains HSTS and the configured security headers.

### Port and log checks

```bash
ss -ltnp | grep -E ':(80|443)\b'
tail -n 20 /var/log/nginx/test.cluster.local_access.log
tail -n 20 /var/log/nginx/test.cluster.local_error.log
tail -n 20 /var/log/nginx/ci.cluster.local_access.log
tail -n 20 /var/log/nginx/ci.cluster.local_error.log
tail -n 20 /var/log/nginx/status.cluster.local_access.log
tail -n 20 /var/log/nginx/status.cluster.local_error.log
```

Expected result:

- nginx listens on TCP ports `80` and `443`.
- Each named site writes to its own access and error logs.