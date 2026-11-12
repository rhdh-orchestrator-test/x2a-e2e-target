---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a multisite HTTPS web server on Ubuntu `>= 18.04` or CentOS `>= 7.0`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates three site document roots and idempotent self-signed TLS certificates; deploys nginx, security, fail2ban, sysctl, and virtual-host configuration; hardens SSH; enables firewall rules for SSH, HTTP, and HTTPS; and redirects HTTP traffic to HTTPS for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. The Ansible implementation must preserve recipe order, file paths, certificate permissions, delayed service handlers, and all three site definitions.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **test.cluster.local**: HTTPS nginx virtual host serving static test content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS nginx virtual host serving static CI content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS nginx virtual host serving static status content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

**Security services and settings**:

- **fail2ban**: Enabled and started; configuration at `/etc/fail2ban/jail.local`
- **ufw**: Enabled with default deny policy; allows SSH, HTTP, and HTTPS
- **sshd**: Root login disabled and password authentication disabled
- **sysctl**: Kernel network-security settings deployed through `/etc/sysctl.d/99-security.conf`

## File Structure

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── files/
│   └── default/
│       └── (no files listed)
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

No provider files are used by the execution tree. `resources/lineinfile.rb` is not used by any recipe.

No static files under `files/default/*` or `files/*` were listed. The recipes reference these cookbook file sources, which must be supplied by the Ansible migration:

```text
test/index.html
ci/index.html
status/index.html
```

Destination paths:

```text
/opt/server/test/index.html
/opt/server/ci/index.html
/opt/server/status/index.html
```

## Module Explanation

The cookbook executes recipes in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in this exact order.
   - The Ansible role should import task files in the same order:
     1. Security setup
     2. nginx installation and base configuration
     3. TLS packages, directories, and certificates
     4. Site directories and virtual hosts

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban global values: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Enables the `sshd` jail for `/var/log/auth.log`.
   - Enables the `nginx-http-auth` jail for `/var/log/nginx/*error.log` on `http,https`, with maximum retries `3`.
   - Enables the `nginx-limit-req` jail for `/var/log/nginx/*error.log` on `http,https`, with maximum retries `10`.
   - Enables the `nginx-botsearch` jail for `/var/log/nginx/*access.log` on `http,https`, with maximum retries `2`.
   - Notifies a delayed fail2ban restart when `/etc/fail2ban/jail.local` changes.
   - Enforces UFW default deny with `ufw --force default deny`.
   - Allows SSH on port `22`, HTTP on port `80`, and HTTPS on port `443` before enabling UFW.
   - Enables UFW with `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-route rejection, martian logging, ICMP suppression, IPv6 disabling, TCP SYN cookies, backlog, and retry values, including:
     - `net.ipv4.conf.default.rp_filter = 1`
     - `net.ipv4.conf.all.rp_filter = 1`
     - `net.ipv4.conf.all.accept_redirects = 0`
     - `net.ipv6.conf.all.accept_redirects = 0`
     - `net.ipv4.conf.all.send_redirects = 0`
     - `net.ipv4.conf.default.send_redirects = 0`
     - `net.ipv4.conf.all.accept_source_route = 0`
     - `net.ipv6.conf.all.accept_source_route = 0`
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
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` only when notified by a changed sysctl template.
   - Enforces `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Enforces `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Notifies a delayed SSH service restart when either SSH setting changes.
   - Declares the SSH service without starting it unconditionally.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures user `nginx`, worker processes `auto`, PID `/run/nginx.pid`, worker connections `768`, standard access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures `server_tokens off`, request-rate zones `login` (`10m`, `10r/m`) and `api` (`10m`, `30r/m`), small request buffers, `client_max_body_size 1k`, client and send timeouts of `10`, TLS session cache `shared:SSL:10m`, TLS session timeout `10m`, TLS `1.2` and `1.3`, explicit ECDHE/DHE ciphers, and preferred server ciphers.
   - Enables and starts nginx.
   - Provides a delayed nginx reload handler for changed nginx configuration.
   - Creates `/opt/server/test` owned by `nginx:nginx` with mode `0755`, then deploys `/opt/server/test/index.html` from `test/index.html` owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/ci` owned by `nginx:nginx` with mode `0755`, then deploys `/opt/server/ci/index.html` from `ci/index.html` owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/status` owned by `nginx:nginx` with mode `0755`, then deploys `/opt/server/status/index.html` from `status/index.html` owned by `nginx:nginx` with mode `0644`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate for `test.cluster.local` only when both certificate and key files do not already exist:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
   - Generates a self-signed RSA 2048-bit certificate for `ci.cluster.local` only when both certificate and key files do not already exist:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
   - Generates a self-signed RSA 2048-bit certificate for `status.cluster.local` only when both certificate and key files do not already exist:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
   - Uses `openssl req -x509 -nodes -days 365 -newkey rsa:2048`, sets the Common Name to the site hostname, and sets subject email to `admin@example.com`.
   - Sets each private key to mode `0640`, owner `root`, and group `ssl-cert`.
   - Notifies a delayed nginx reload when a certificate is generated.
   - Must not regenerate certificates on subsequent runs when both files exist.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` owned by `root:root` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` owned by `root:root` with mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - `/etc/nginx/sites-available/test.cluster.local` with `server_name: test.cluster.local`, `document_root: /opt/server/test`, `ssl_enabled: true`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
     - `/etc/nginx/sites-available/ci.cluster.local` with `server_name: ci.cluster.local`, `document_root: /opt/server/ci`, `ssl_enabled: true`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
     - `/etc/nginx/sites-available/status.cluster.local` with `server_name: status.cluster.local`, `document_root: /opt/server/status`, `ssl_enabled: true`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Creates these three symlinks:
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Notifies nginx for a delayed reload when a site template, symlink, or default-site deletion changes.
   - Each virtual host listens on HTTP `80`, redirects HTTP to HTTPS, listens on HTTPS `443` with HTTP/2, serves its site-specific document root, enables TLS `1.2` and `1.3`, sets one-year HSTS, applies security headers, enables gzip, uses `try_files $uri $uri/ =404`, blocks `.htaccess`, `.git`, and `.svn` paths, and writes site-specific access and error logs.

## Dependencies

**External cookbook dependencies**: None.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started; restarted when `/etc/fail2ban/jail.local` changes
- `nginx`: enabled and started; reloaded when nginx configuration, certificates, site templates, symlinks, or default-site deletion changes
- `sshd` or Ubuntu’s `ssh` service: restarted when SSH hardening settings change

**Firewall ports**:

- SSH: `22`
- HTTP: `80`
- HTTPS: `443`

## Credentials

**Detection Summary**: No application credentials, passwords, API tokens, data bags, Chef Vault items, CyberArk references, Conjur variables, or database credentials were detected. Three locally generated TLS private keys and three locally generated TLS certificates are managed as sensitive TLS material.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### Self-signed TLS private keys

- **Variable(s)**:
  - `key_file`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated files; not stored in a data bag, vault, environment variable, or attribute
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts
- **Permissions**: `/etc/ssl/private` mode `0710`; key files mode `0640`, owned by `root:ssl-cert`

### Self-signed TLS certificates

- **Variable(s)**:
  - `cert_file`
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated certificate files
- **Usage context**: TLS certificates for the three nginx HTTPS virtual hosts
- **Certificate properties**: Self-signed, RSA 2048-bit, valid for 365 days, site hostname as Common Name, and subject email `admin@example.com`
- **Secret-management usage**: No hardcoded passwords, API keys, database credentials, secret environment variables, `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, CyberArk, or Conjur usage was detected.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/opt/server/test
/opt/server/test/index.html
/opt/server/ci
/opt/server/ci/index.html
/opt/server/status
/opt/server/status/index.html
/etc/ssl/certs
/etc/ssl/private
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/test.cluster.local_access.log
/var/log/nginx/test.cluster.local_error.log
/var/log/nginx/ci.cluster.local_access.log
/var/log/nginx/ci.cluster.local_error.log
/var/log/nginx/status.cluster.local_access.log
/var/log/nginx/status.cluster.local_error.log
/var/log/auth.log
```

`/etc/nginx/sites-enabled/default` must not exist after migration.

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`; HTTPS `443`
- `ci.cluster.local`: HTTP `80`; HTTPS `443`
- `status.cluster.local`: HTTP `80`; HTTPS `443`
- Unix sockets: None
- Network binding: nginx listens on all available interfaces; no specific bind address is configured

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: three times to:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Detect installed packages on Debian-family or Red Hat-family systems.
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Verify service status. Ubuntu may use ssh instead of sshd.
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active sshd 2>/dev/null || systemctl is-active ssh

# Validate nginx configuration.
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Verify base nginx configuration and security settings.
grep -E 'user nginx|worker_processes|worker_connections|access_log|error_log|gzip on|sites-enabled' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Verify fail2ban, firewall, sysctl, and SSH hardening.
test -f /etc/fail2ban/jail.local
fail2ban-client status
ufw status verbose
grep -E 'rp_filter|accept_redirects|send_redirects|accept_source_route|log_martians|icmp_echo|disable_ipv6|tcp_syncookies|tcp_max_syn_backlog|tcp_synack_retries|tcp_syn_retries' \
  /etc/sysctl.d/99-security.conf
grep -E '^PermitRootLogin no$|^PasswordAuthentication no$' /etc/ssh/sshd_config

# Verify test.cluster.local.
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test "$(readlink /etc/nginx/sites-enabled/test.cluster.local)" = "/etc/nginx/sites-available/test.cluster.local"
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -I --resolve test.cluster.local:80:127.0.0.1 http://test.cluster.local/

# Verify ci.cluster.local.
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test "$(readlink /etc/nginx/sites-enabled/ci.cluster.local)" = "/etc/nginx/sites-available/ci.cluster.local"
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -I --resolve ci.cluster.local:80:127.0.0.1 http://ci.cluster.local/

# Verify status.cluster.local.
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test "$(readlink /etc/nginx/sites-enabled/status.cluster.local)" = "/etc/nginx/sites-available/status.cluster.local"
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -I --resolve status.cluster.local:80:127.0.0.1 http://status.cluster.local/

# Verify certificate and private-key permissions.
stat -c '%a %U:%G %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Verify the default nginx site was removed.
test ! -e /etc/nginx/sites-enabled/default

# Verify firewall ports.
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
```