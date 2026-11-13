---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx for three HTTPS-enabled sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies kernel and SSH hardening; creates site document roots and static index files; generates locally stored self-signed certificates; configures HTTP-to-HTTPS virtual hosts; enables firewall rules for SSH, HTTP, and HTTPS; and removes the default Nginx site. The Ansible implementation must preserve recipe order, exact site names and paths, certificate permissions, firewall behavior, configuration validation, and delayed service reload or restart semantics.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled static Nginx site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; content `/opt/server/test/index.html`

- **ci.cluster.local**: HTTPS-enabled static Nginx site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; content `/opt/server/ci/index.html`

- **status.cluster.local**: HTTPS-enabled static Nginx site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; content `/opt/server/status/index.html`

**Supporting security services**:

- **fail2ban**: Enabled and started; configuration at `/etc/fail2ban/jail.local`
- **ufw**: Enabled with a default deny policy; allows SSH, HTTP, and HTTPS
- **sshd**: Hardened conditionally according to `security.ssh` attributes
- **sysctl**: Security parameters deployed to `/etc/sysctl.d/99-security.conf`

The exact values of `nginx.sites`, `security.ssh`, and SSL path attributes must be verified against `cookbooks/nginx-multisite/attributes/default.rb`. The supplied validation confirms three site entries and references these attributes but does not include the complete attribute file.

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

No static files under `files/default/` or `files/` are listed. The `cookbook_file` resources reference these source names, which must be supplied by the Ansible migration:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. `default`
2. `security`
3. `nginx`
4. `ssl`
5. `sites`

The `default` recipe includes the remaining recipes in the listed order. The `ssl` and `sites` recipes reference the `nginx` service created by `nginx.rb`; preserve this dependency in Ansible handlers and task ordering.

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Ansible execution order must remain security, Nginx installation and configuration, SSL setup, and site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban defaults: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Enables SSH, Nginx HTTP authentication, Nginx request-rate, and Nginx bot-search protection.
   - References `/var/log/auth.log`, Nginx access logs, and Nginx error logs.
   - Restarts Fail2ban when its configuration changes.
   - Configures UFW with default incoming policy `deny`.
   - Allows TCP `22`, TCP `80`, and TCP `443`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies reverse-path filtering, redirect rejection, source-route rejection, martian packet logging, ICMP protections, IPv6 disabling, TCP SYN cookies, and TCP retry settings.
   - Important sysctl values include:
     - `net.ipv4.conf.default.rp_filter = 1`
     - `net.ipv4.conf.all.rp_filter = 1`
     - `net.ipv4.conf.all.accept_redirects = 0`
     - `net.ipv6.conf.all.accept_redirects = 0`
     - `net.ipv4.conf.all.send_redirects = 0`
     - `net.ipv4.conf.default.send_redirects = 0`
     - `net.ipv4.conf.all.accept_source_route = 0`
     - `net.ipv6.conf.all.accept_source_route = 0`
     - `net.ipv4.conf.all.log_martians = 1`
     - `net.ipv4.icmp_echo_ignore_all = 1`
     - `net.ipv4.icmp_echo_ignore_broadcasts = 1`
     - `net.ipv6.conf.all.disable_ipv6 = 1`
     - `net.ipv6.conf.default.disable_ipv6 = 1`
     - `net.ipv6.conf.lo.disable_ipv6 = 1`
     - `net.ipv4.tcp_syncookies = 1`
     - `net.ipv4.tcp_max_syn_backlog = 2048`
     - `net.ipv4.tcp_synack_retries = 2`
     - `net.ipv4.tcp_syn_retries = 5`
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` only when the sysctl template changes.
   - Applies `PermitRootLogin no` when `security.ssh.disable_root` is enabled.
   - Applies `PasswordAuthentication no` when `security.ssh.password_auth` is disabled.
   - Restarts `sshd` only when either SSH setting changes.
   - Ansible resources: packages, services, templates, UFW rules, sysctl settings, and SSH `lineinfile` tasks.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, worker processes `auto`, PID file `/run/nginx.pid`, worker connections `768`, access and error logs, gzip, MIME types, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures server-token suppression, request limits, client buffer limits, client body size, timeouts, TLS `1.2` and `1.3`, SSL session caching, SSL session timeout, the configured ECDHE/DHE ciphers, and preferred server ciphers.
   - Enables and starts the `nginx` service.
   - Reloads Nginx after configuration changes, after validating with `nginx -t`.
   - Creates document roots and deploys static files for these three iterations:
     - **test.cluster.local**
       - Directory: `/opt/server/test`
       - Content source: `test/index.html`
       - Destination: `/opt/server/test/index.html`
       - Expected directory ownership and mode from the supplied plan: `nginx:nginx`, `0755`; verify these values against the detailed resource analysis before treating them as authoritative.
       - File ownership and mode: `nginx:nginx`, `0644`
     - **ci.cluster.local**
       - Directory: `/opt/server/ci`
       - Content source: `ci/index.html`
       - Destination: `/opt/server/ci/index.html`
       - Expected directory ownership and mode from the supplied plan: `nginx:nginx`, `0755`; verify these values against the detailed resource analysis before treating them as authoritative.
       - File ownership and mode: `nginx:nginx`, `0644`
     - **status.cluster.local**
       - Directory: `/opt/server/status`
       - Content source: `status/index.html`
       - Destination: `/opt/server/status/index.html`
       - Expected directory ownership and mode from the supplied plan: `nginx:nginx`, `0755`; verify these values against the detailed resource analysis before treating them as authoritative.
       - File ownership and mode: `nginx:nginx`, `0644`

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` as `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert` with mode `0710`.
   - Evaluates SSL configuration for these three iterations:
     - **test.cluster.local**
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Private key: `/etc/ssl/private/test.cluster.local.key`
       - Common Name: `test.cluster.local`
     - **ci.cluster.local**
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key: `/etc/ssl/private/ci.cluster.local.key`
       - Common Name: `ci.cluster.local`
     - **status.cluster.local**
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Private key: `/etc/ssl/private/status.cluster.local.key`
       - Common Name: `status.cluster.local`
   - Generates each certificate only when its certificate or key is absent.
   - Uses RSA `2048`, self-signed validity of `365` days, and subject values:
     - Country: `US`
     - State: `Example`
     - Locality: `Example`
     - Organization: `Example Org`
     - Organizational unit: `IT`
     - Email: `admin@example.com`
     - Common Name: site hostname
   - Sets private keys to `root:ssl-cert` with mode `0640`.
   - Reloads Nginx after certificate or key material changes.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates three site-related directory resources from the `nginx.sites` loop. The supplied validation confirms three directory resources but does not provide their exact recipe-defined paths; verify those paths directly in `cookbooks/nginx-multisite/recipes/sites.rb` before implementation.
   - The previously described two-directory loop over `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` is not authoritative and must not be used unless confirmed by the recipe.
   - Renders and enables virtual hosts for these three iterations:
     - **test.cluster.local**
       - Template destination: `/etc/nginx/sites-available/test.cluster.local`
       - Link: `/etc/nginx/sites-enabled/test.cluster.local`
       - Root: `/opt/server/test`
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Private key: `/etc/ssl/private/test.cluster.local.key`
     - **ci.cluster.local**
       - Template destination: `/etc/nginx/sites-available/ci.cluster.local`
       - Link: `/etc/nginx/sites-enabled/ci.cluster.local`
       - Root: `/opt/server/ci`
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key: `/etc/ssl/private/ci.cluster.local.key`
     - **status.cluster.local**
       - Template destination: `/etc/nginx/sites-available/status.cluster.local`
       - Link: `/etc/nginx/sites-enabled/status.cluster.local`
       - Root: `/opt/server/status`
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Private key: `/etc/ssl/private/status.cluster.local.key`
   - Uses `cookbooks/nginx-multisite/templates/default/site.conf.erb`.
   - Configures HTTP port `80`, HTTP-to-HTTPS redirects, HTTPS port `443`, HTTP/2, site-specific server names and roots, TLS protocols `TLSv1.2` and `TLSv1.3`, HSTS, security headers, gzip, `try_files`, and blocking of `.htaccess`, `.git`, and `.svn`.
   - Configures site-specific access and error logs.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Reloads Nginx after template, link, or default-site changes.
   - Total analyzed resources: 10—three directory resources, three template resources, three link resources, and one file resource.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata and execution tree.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: restarted only when SSH hardening changes
- UFW: enabled with `ufw --force enable`

**Network ports**:

- TCP `22`: SSH
- TCP `80`: HTTP
- TCP `443`: HTTPS

## Credentials

**Detection Summary**: No external application credentials, passwords, API tokens, data bags, Chef Vault items, or external secret-manager integrations are identified in the supplied execution tree. The supplied validation notes that this conclusion requires confirmation from the complete attribute and credential analysis.

**Source**:
  - **Provider**: None detected in the supplied analysis; verify against the complete cookbook
  - **URL**: None detected
  - **Path**: None detected

### Self-signed TLS private keys

- **Variable(s)**: SSL private-key path attributes referenced by `ssl.rb` and `sites.rb`; exact attribute definitions require verification in `cookbooks/nginx-multisite/attributes/default.rb`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated filesystem key files
- **Usage context**: Nginx HTTPS private keys for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Files**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: `root:ssl-cert`, mode `0640`

### Self-signed TLS certificates

- **Variable(s)**: SSL certificate path attributes referenced by `ssl.rb` and `sites.rb`; exact attribute definitions require verification in `cookbooks/nginx-multisite/attributes/default.rb`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: Nginx HTTPS certificates for the three configured virtual hosts
- **Files**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Validity**: `365` days
- **Subject**: Site-specific Common Name with the configured `US`, `Example`, `Example Org`, `IT`, and `admin@example.com` subject fields

No hardcoded passwords, API keys, database credentials, or authentication tokens are identified in the supplied execution tree. This conclusion remains subject to verification against the complete attributes and credential analysis.

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
- `/etc/nginx/sites-enabled/default` does not exist
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
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/opt/server/test`
- `/opt/server/ci`
- `/opt/server/status`
- The three site-directory paths created by the `nginx.sites` loop in `sites.rb`, after verifying their exact recipe-defined paths

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: TCP `22`
- Nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb` total: 3 renders

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban
systemctl status sshd

# Configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
grep -E 'worker_processes|worker_connections|keepalive_timeout|access_log|error_log|gzip' /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' /etc/nginx/conf.d/security.conf

# Nginx listeners
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Firewall
ufw status verbose
ufw status numbered

# Fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.default.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.icmp_echo_ignore_broadcasts
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv6.conf.default.disable_ipv6
sysctl net.ipv6.conf.lo.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries
```

### Instance: `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
```

Expected result: HTTP returns `301`, HTTPS returns `200 OK`, the certificate contains `CN=test.cluster.local`, and the key is `root:ssl-cert` with mode `640`.

### Instance: `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
```

Expected result: HTTP returns `301`, HTTPS returns `200 OK`, the certificate contains `CN=ci.cluster.local`, and the key is `root:ssl-cert` with mode `640`.

### Instance: `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected result: HTTP returns `301`, HTTPS returns `200 OK`, the certificate contains `CN=status.cluster.local`, and the key is `root:ssl-cert` with mode `640`.

### Security and service validation

```bash
systemctl is-active nginx
systemctl is-active fail2ban
ufw status verbose
cat /etc/fail2ban/jail.local
nginx -t
test ! -e /etc/nginx/sites-enabled/default
```

Expected result: Nginx and Fail2ban are active, UFW is active with default deny and TCP ports `22`, `80`, and `443` allowed, all required Fail2ban jails are configured, Nginx configuration validation succeeds, and the default site is absent.