---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies nginx, kernel, firewall, and SSH security settings; generates self-signed 2048-bit certificates valid for 365 days; deploys one static index page per site; configures HTTP-to-HTTPS redirects; enables SSH, HTTP, and HTTPS firewall access; and disables root SSH login and SSH password authentication.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`; source file `test/index.html`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`; source file `ci/index.html`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443` with HTTP/2
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`; source file `status/index.html`

### Security components

- **fail2ban**
  - Package: `fail2ban`
  - Service: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Enabled by default: `true`

- **ufw**
  - Package: `ufw`
  - Rules: default deny, allow SSH, allow HTTP, allow HTTPS
  - Enabled by default: `true`
  - The analyzed execution tree confirms five UFW command resources. Guard conditions for those commands require verification; Ansible should implement the equivalent idempotently.

- **ssh**
  - Root login disabled by default: `true`
  - Password authentication disabled by default: `true`
  - Configuration file: `/etc/ssh/sshd_config`
  - Notified service: `sshd`

## File Structure

The following complete directory listing was supplied by the cookbook analysis.

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

No custom resource provider is used by the execution tree.

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

The recipes reference static `cookbook_file` sources `test/index.html`, `ci/index.html`, and `status/index.html`. These source files are not present in the supplied directory listing and must be verified or supplied separately.

## Attributes

**File:** `cookbooks/nginx-multisite/attributes/default.rb`

The analyzed site collection contains exactly these entries:

```ruby
default['nginx']['sites'] = {
  'test.cluster.local' => {
    'document_root' => '/opt/server/test',
    'ssl_enabled' => true
  },
  'ci.cluster.local' => {
    'document_root' => '/opt/server/ci',
    'ssl_enabled' => true
  },
  'status.cluster.local' => {
    'document_root' => '/opt/server/status',
    'ssl_enabled' => true
  }
}
```

The Ansible role should represent the sites as a dictionary keyed by hostname or as an equivalent list containing exactly:

- `test.cluster.local`
- `ci.cluster.local`
- `status.cluster.local`

The following values are specified by the migration plan but require confirmation against the detailed attribute analysis before implementation:

- Certificate directory: `/etc/ssl/certs`
- Private-key directory: `/etc/ssl/private`
- `security.fail2ban.enabled`: `true`
- `security.ufw.enabled`: `true`
- `security.ssh.disable_root`: `true`
- `security.ssh.password_auth`: `false`

## Module Explanation

The cookbook performs operations in this order:

1. `security`
2. `nginx`
3. `ssl`
4. `sites`

The entry recipe is `cookbooks/nginx-multisite/recipes/default.rb`. It includes the four recipes in that order. The Ansible role should preserve the order with task files such as `security.yml`, `nginx.yml`, `ssl.yml`, and `sites.yml` included from `tasks/main.yml`.

Ownership, modes, notifications, and service capabilities listed below should be confirmed against the detailed resource analysis before being treated as verified Chef behavior.

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Contains no direct package, file, or service resources.
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - Ansible equivalent:
     - `include_tasks: security.yml`
     - `include_tasks: nginx.yml`
     - `include_tasks: ssl.yml`
     - `include_tasks: sites.yml`

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Manages the `fail2ban` service as enabled and started.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local`.
   - Configures fail2ban defaults: bantime `3600`, findtime `600`, and maxretry `3`.
   - Configures the SSH jail on port `ssh` using `/var/log/auth.log`.
   - Configures the nginx HTTP authentication jail on `http,https` using `/var/log/nginx/*error.log`, with max retries `3`.
   - Configures the nginx request-limit jail on `http,https` using `/var/log/nginx/*error.log`, with max retries `10`.
   - Configures the nginx bot-search jail on `http,https` using `/var/log/nginx/*access.log`, with max retries `2`.
   - Restarts fail2ban when `/etc/fail2ban/jail.local` changes.
   - Applies UFW operations in this order:
     1. Set default incoming policy to deny.
     2. Allow SSH.
     3. Allow HTTP.
     4. Allow HTTPS.
     5. Enable UFW.
   - Ansible should allow SSH before enabling UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf`.
   - Configures reverse-path filtering, ICMP redirect and source-route rejection, martian logging, ICMP suppression, IPv6 disabling, SYN-cookie protection, and TCP retry/backlog settings.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` when the sysctl template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` when root-login disabling is enabled.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` when password authentication is disabled.
   - Restarts `sshd` only when either SSH configuration changes.
   - Resource counts with supplied defaults:
     - One grouped `package` resource installing two packages.
     - Two `service` resources: `fail2ban` and `sshd`.
     - Two `template` resources.
     - Eight `execute` resources when both conditional SSH resources execute:
       - `ufw_default_deny`
       - `ufw_allow_ssh`
       - `ufw_allow_http`
       - `ufw_allow_https`
       - `ufw_enable`
       - `reload_sysctl`
       - Disable root login
       - Disable password authentication

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf`.
   - Configures worker user `nginx`, worker processes `auto`, PID `/run/nginx.pid`, worker connections `768`, keepalive timeout `65`, gzip, and the main access and error logs.
   - Includes `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf`.
   - Configures `server_tokens off`, rate-limit zones `login` and `api`, small client buffers, client body limits, request timeouts, TLS versions `TLSv1.2 TLSv1.3`, SSL session caching, and preferred server ciphers.
   - Manages nginx as enabled and started.
   - Reloads nginx when the main or security configuration changes.
   - Creates the document root and static file for **test.cluster.local**:
     - Directory: `/opt/server/test`
     - Static file: `/opt/server/test/index.html`
     - Source: `test/index.html`
   - Creates the document root and static file for **ci.cluster.local**:
     - Directory: `/opt/server/ci`
     - Static file: `/opt/server/ci/index.html`
     - Source: `ci/index.html`
   - Creates the document root and static file for **status.cluster.local**:
     - Directory: `/opt/server/status`
     - Static file: `/opt/server/status/index.html`
     - Source: `status/index.html`
   - The three document roots are owned by `nginx:nginx` with mode `0755`; static files are owned by `nginx:nginx` with mode `0644`, subject to confirmation from detailed resource analysis.
   - Iterations: the site loop runs exactly three times for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resource counts:
     - One package resource.
     - Two template resources.
     - One service resource.
     - Three directory resources.
     - Three `cookbook_file` resources.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root:root` and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root:ssl-cert` and mode `0710`.
   - Generates certificates because SSL is enabled for all three sites.
   - For **test.cluster.local**:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
   - For **ci.cluster.local**:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
   - For **status.cluster.local**:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
   - Each certificate uses RSA `2048`, is valid for `365` days, and has subject email `admin@example.com`.
   - Each private key is assigned to `root:ssl-cert` with mode `0640`.
   - Certificate generation is skipped when both output files already exist.
   - A generated certificate triggers a delayed nginx reload.
   - Ansible should use `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate` where available, or guarded commands with output-file checks where exact shell behavior is required.
   - Iterations: certificate generation runs three times for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resource counts:
     - One grouped package resource installing two packages.
     - One group resource.
     - Two directory resources.
     - Three certificate-generation resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - The structured execution tree confirms one directory loop with three document-root directory resources for:
     - `/opt/server/test`
     - `/opt/server/ci`
     - `/opt/server/status`
   - The supplied execution analysis does not confirm Chef-managed resources for `/etc/nginx/sites-available` or `/etc/nginx/sites-enabled`; those shared directories must be verified or created explicitly by the Ansible migration.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for **test.cluster.local** to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for **ci.cluster.local** to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for **status.cluster.local** to `/etc/nginx/sites-available/status.cluster.local`.
   - Creates these enabled-site links:
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
   - Removes `/etc/nginx/sites-enabled/default`.
   - Each site configuration provides an HTTP listener on port `80`, an HTTP-to-HTTPS redirect, an HTTPS listener on port `443` with HTTP/2, the site-specific document root, TLS files, HSTS, security headers, gzip, `try_files`, and access denial for `.htaccess`, `.git`, and `.svn`.
   - Uses site-specific access and error logs.
   - Site template and link changes trigger a delayed nginx reload.
   - Iterations: the site-template loop runs exactly three times for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resource counts confirmed by the structured tree:
     - Three document-root directory resources.
     - Three template resources.
     - Three link resources.
     - One file deletion resource.
   - The three shared nginx directory resources require source verification before being attributed to this recipe.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata or execution tree.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd`

**Network services**:

- SSH: port `22`
- HTTP: port `80`
- HTTPS: port `443`

## Credentials

**Detection Summary**: 0 application credentials or externally supplied secrets detected across the analyzed cookbook files.

The cookbook generates self-signed TLS keys locally. These keys are generated artifacts rather than externally supplied credentials.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed TLS private keys

- **Variable(s)**: `key_file`, derived from `site_name`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by the OpenSSL certificate-generation command
- **Usage context**: TLS private keys for nginx HTTPS virtual hosts
- **Generated paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: `root:ssl-cert`, mode `0640`

### Self-signed TLS certificates

- **Variable(s)**: `cert_file`, derived from `site_name`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by the OpenSSL certificate-generation command
- **Usage context**: TLS certificates for nginx HTTPS virtual hosts
- **Generated paths**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`

The certificate subject contains the hardcoded administrative email `admin@example.com`. This is configuration metadata, not an authentication secret.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
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
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
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

- SSH: `22/tcp`
- `test.cluster.local:80`
- `test.cluster.local:443`
- `ci.cluster.local:80`
- `ci.cluster.local:443`
- `status.cluster.local:80`
- `status.cluster.local:443`

**Unix sockets**: None configured by this cookbook.

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: rendered once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: rendered once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: rendered once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: rendered once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: rendered once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: rendered once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: rendered once

Total `site.conf.erb` renders: `3`.

## Pre-flight checks

```bash
# Verify required packages
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Verify service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# Validate nginx configuration
nginx -t
nginx -T | grep -E \
'test.cluster.local|ci.cluster.local|status.cluster.local|listen 80|listen 443'

# Verify nginx main configuration
grep -E \
'^(user|worker_processes|pid|worker_connections|keepalive_timeout|access_log|error_log|gzip)' \
/etc/nginx/nginx.conf

grep -E \
'include /etc/nginx/(conf.d|sites-enabled)' \
/etc/nginx/nginx.conf

# Verify nginx security configuration
grep -E \
'server_tokens|limit_req_zone|client_body_buffer_size|client_header_buffer_size|client_max_body_size|ssl_protocols|ssl_session_cache' \
/etc/nginx/conf.d/security.conf

# Verify firewall rules before testing services
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# Verify SSH hardening
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config

# Verify kernel security configuration
grep -E \
'rp_filter|accept_redirects|send_redirects|accept_source_route|log_martians|icmp_echo_ignore|disable_ipv6|tcp_syncookies|tcp_max_syn_backlog|tcp_synack_retries|tcp_syn_retries' \
/etc/sysctl.d/99-security.conf

# Verify the test.cluster.local instance
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
ls -l /etc/ssl/certs/test.cluster.local.crt
ls -l /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates
test -f /var/log/nginx/test.cluster.local_access.log
test -f /var/log/nginx/test.cluster.local_error.log

# Verify the ci.cluster.local instance
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
ls -l /etc/ssl/certs/ci.cluster.local.crt
ls -l /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates
test -f /var/log/nginx/ci.cluster.local_access.log
test -f /var/log/nginx/ci.cluster.local_error.log

# Verify the status.cluster.local instance
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
ls -l /etc/ssl/certs/status.cluster.local.crt
ls -l /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates
test -f /var/log/nginx/status.cluster.local_access.log
test -f /var/log/nginx/status.cluster.local_error.log

# Verify enabled-site links
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

# Expected link targets:
# /etc/nginx/sites-available/test.cluster.local
# /etc/nginx/sites-available/ci.cluster.local
# /etc/nginx/sites-available/status.cluster.local

# Verify default site removal
test ! -e /etc/nginx/sites-enabled/default

# Verify TLS certificates for every named instance
openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates

openssl s_client -connect 127.0.0.1:443 \
  -servername ci.cluster.local </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates

openssl s_client -connect 127.0.0.1:443 \
  -servername status.cluster.local </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates
```