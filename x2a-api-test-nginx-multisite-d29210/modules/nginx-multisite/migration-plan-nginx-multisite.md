---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three HTTPS virtual sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, kernel, and SSH hardening; generates self-signed certificates; deploys static site content; renders and enables three nginx virtual hosts; and redirects HTTP traffic to HTTPS. No external cookbook dependencies or externally supplied credentials were detected.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS static site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; static file `/opt/server/test/index.html`

- **ci.cluster.local**: HTTPS static site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; static file `/opt/server/ci/index.html`

- **status.cluster.local**: HTTPS static site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; static file `/opt/server/status/index.html`

**Security configuration**:

- **fail2ban**: Enabled; installed and started with SSH and nginx jails.
- **ufw**: Enabled; default-deny policy with SSH, HTTP, and HTTPS allowed.
- **ssh**: Root login disabled; password authentication disabled.

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
├── resources/
│   └── lineinfile.rb
└── templates/
    └── default/
        ├── fail2ban.jail.local.erb
        ├── nginx.conf.erb
        ├── security.conf.erb
        ├── site.conf.erb
        └── sysctl-security.conf.erb
```

The `resources/lineinfile.rb` file is mentioned by structural analysis but is not invoked by the execution tree. No provider files or static files were included in the supplied cookbook directory listing. The recipes reference dynamic cookbook-file sources `test/index.html`, `ci/index.html`, and `status/index.html`, but those files were not included in the supplied file structure.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The execution order must be preserved because later recipes depend on packages, directories, nginx installation, and the nginx service established earlier.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures fail2ban defaults: `bantime = 3600`, `findtime = 600`, `maxretry = 3`, and `backend = auto`.
   - Enables the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Applies UFW default-deny policy.
   - Allows SSH on `22/tcp`, HTTP on `80/tcp`, and HTTPS on `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Configures reverse-path filtering, redirect and source-route rejection, martian logging, ICMP restrictions, IPv6 disabling, SYN-cookie protection, and TCP SYN limits.
   - Reloads sysctl values with `sysctl -p /etc/sysctl.d/99-security.conf` after template changes.
   - Disables root SSH login by setting `PermitRootLogin no`.
   - Disables SSH password authentication by setting `PasswordAuthentication no`.
   - Delayed notifications restart `ssh` when SSH configuration changes.
   - Resources: one package resource, two service resources, two template resources, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Configures the `www-data` worker user, automatic worker processes, `/run/nginx.pid`, 768 worker connections, standard access and error logs, gzip, MIME types, and `conf.d` and `sites-enabled` includes.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Hides nginx version information.
   - Configures rate limits of `10r/m` for `login` and `30r/m` for `api`.
   - Configures request buffers, a maximum client body size of `1k`, client and header timeouts of `10`, send timeout of `10`, TLS 1.2 and TLS 1.3, a `10m` shared SSL session cache, and a `10m` SSL session timeout.
   - Enables and starts nginx, with support for reload, restart, and status.
   - Expands the site collection into these three directory and static-file iterations:
     - **test.cluster.local**:
       - Creates `/opt/server/test` recursively with owner and group `www-data` and mode `0755`.
       - Deploys source `test/index.html` to `/opt/server/test/index.html` with owner and group `www-data` and mode `0644`.
     - **ci.cluster.local**:
       - Creates `/opt/server/ci` recursively with owner and group `www-data` and mode `0755`.
       - Deploys source `ci/index.html` to `/opt/server/ci/index.html` with owner and group `www-data` and mode `0644`.
     - **status.cluster.local**:
       - Creates `/opt/server/status` recursively with owner and group `www-data` and mode `0755`.
       - Deploys source `status/index.html` to `/opt/server/status/index.html` with owner and group `www-data` and mode `0644`.
   - Resources: one package, two templates, one service, three directories, and three cookbook files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Expands certificate generation into these three enabled-site iterations:
     - **test.cluster.local**:
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Private key: `/etc/ssl/private/test.cluster.local.key`
       - Common name: `test.cluster.local`
     - **ci.cluster.local**:
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key: `/etc/ssl/private/ci.cluster.local.key`
       - Common name: `ci.cluster.local`
     - **status.cluster.local**:
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Private key: `/etc/ssl/private/status.cluster.local.key`
       - Common name: `status.cluster.local`
   - Generates each certificate with a self-signed 2048-bit RSA key valid for 365 days.
   - Uses subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site-name>/emailAddress=admin@example.com`.
   - Sets each private key to mode `0640` and owner `root:ssl-cert`.
   - Skips certificate generation only when both the certificate and private key already exist.
   - Sends a delayed nginx reload after certificate changes.
   - Resources: one package, one group, two directories, and three execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` and creates the corresponding enabled-site link for each site:
     - **test.cluster.local**:
       - Renders `/etc/nginx/sites-available/test.cluster.local`.
       - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to the available-site file.
       - Uses document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
     - **ci.cluster.local**:
       - Renders `/etc/nginx/sites-available/ci.cluster.local`.
       - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to the available-site file.
       - Uses document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
     - **status.cluster.local**:
       - Renders `/etc/nginx/sites-available/status.cluster.local`.
       - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to the available-site file.
       - Uses document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Each virtual host listens on port `80`, redirects HTTP to HTTPS, and listens on port `443` with SSL and HTTP/2.
   - Each virtual host configures TLS 1.2 and TLS 1.3, HSTS, security response headers, gzip, `try_files`, and denial of `.htaccess`, `.git`, and `.svn` paths.
   - Each virtual host has site-specific access and error logs.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Resources: three templates, three links, and one file deletion.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**Chef/platform compatibility**:

- Chef: `>= 16.0`
- Ubuntu: `>= 18.04`
- CentOS: `>= 7.0`

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `ssh`: restarted when SSH hardening changes.
- UFW: enabled through command execution.

## Credentials

**Detection Summary**: No externally stored credentials detected. Three locally generated TLS private keys are created for the HTTPS sites. The certificates are self-signed development certificates rather than externally supplied credentials.

**Source**:

- **Provider**: None detected
- **URL**: None detected
- **Path**: None detected

### Self-signed TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by `openssl req`
- **Usage context**: nginx TLS private keys for the three HTTPS virtual hosts
- **Handling**:
  - RSA 2048-bit keys
  - Valid for 365 days
  - Mode `0640`
  - Owner `root`
  - Group `ssl-cert`

### Certificate subject email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded, non-secret certificate subject value
- **Usage context**: Subject email address in all three self-signed certificates

No data bag, encrypted data bag, Chef Vault, Conjur, CyberArk, HashiCorp Vault, AWS Secrets Manager, environment-variable secret, database password, API key, or embedded database connection credential was detected.

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
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
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
- SSH: TCP `22`
- nginx PID file: `/run/nginx.pid`
- No application-specific Unix sockets are configured.

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 rendering
- `nginx.conf.erb`: 1 rendering
- `security.conf.erb`: 1 rendering
- `sysctl-security.conf.erb`: 1 rendering
- `site.conf.erb`: 3 renderings

## Pre-flight checks:

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh
systemctl is-enabled nginx
systemctl is-active nginx

# Firewall and SSH hardening
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config

# Kernel security settings
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies

# nginx configuration
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# TLS and security headers
curl -k -s -D - --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ -o /dev/null | \
  grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Referrer-Policy'

openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local -tls1_2 </dev/null

openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local -tls1_3 </dev/null

# Ports and processes
ss -tlnp | grep -E ':80|:443'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN
ps aux | grep '[n]ginx'
cat /run/nginx.pid

# Logs
tail -n 20 /var/log/nginx/access.log
tail -n 20 /var/log/nginx/error.log
tail -n 20 /var/log/nginx/test.cluster.local_access.log
tail -n 20 /var/log/nginx/test.cluster.local_error.log
tail -n 20 /var/log/nginx/ci.cluster.local_access.log
tail -n 20 /var/log/nginx/ci.cluster.local_error.log
tail -n 20 /var/log/nginx/status.cluster.local_access.log
tail -n 20 /var/log/nginx/status.cluster.local_error.log
tail -n 20 /var/log/auth.log
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50

# Default site removal
test ! -e /etc/nginx/sites-enabled/default
```

Expected results:

- `nginx -t` succeeds.
- nginx is enabled, active, and listening on TCP ports `80` and `443`.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` each redirect HTTP to HTTPS and serve content over HTTPS.
- Each certificate subject contains the matching site common name.
- Each private key is owned by `root:ssl-cert` with mode `640`.
- SSH reports `PermitRootLogin no` and `PasswordAuthentication no`.
- UFW permits TCP ports `22`, `80`, and `443` while using a default-deny policy.
- TLS 1.2 and TLS 1.3 connections succeed.
- HSTS and configured security headers are present.
- The default nginx site is absent.
- nginx and fail2ban logs contain no configuration or certificate errors.