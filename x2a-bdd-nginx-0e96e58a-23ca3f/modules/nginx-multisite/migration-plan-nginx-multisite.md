---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Migrate the `nginx-multisite` cookbook as an Ubuntu-oriented Ansible role that installs and configures nginx, fail2ban, UFW, OpenSSL, and CA certificates; creates three SSL-enabled virtual hosts named `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; generates local self-signed certificates; deploys site content and nginx configurations; applies SSH and kernel hardening; and enables the required services. Detailed template directives, attribute values, guards, and notification relationships are reported by the original plan but require source verification because the structured analysis confirms resource sources and counts rather than complete file contents.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The configured site collection contains exactly three sites. The original plan reports `ssl_enabled: true` for all three sites; verify these values against `cookbooks/nginx-multisite/attributes/default.rb`.

- **test.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/test`
  - HTTP endpoint: Port `80`, redirected to HTTPS
  - HTTPS endpoint: Port `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Content file: `/opt/server/test/index.html`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/ci`
  - HTTP endpoint: Port `80`, redirected to HTTPS
  - HTTPS endpoint: Port `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Content file: `/opt/server/ci/index.html`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/status`
  - HTTP endpoint: Port `80`, redirected to HTTPS
  - HTTPS endpoint: Port `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Content file: `/opt/server/status/index.html`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`

### Security Collection

The analyzed plan reports the following security configuration. Attribute values and template behavior require verification against the source files.

- **fail2ban**
  - Enabled: `true`
  - Service: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`

- **ufw**
  - Enabled: `true`
  - Default policy: deny
  - Allowed services: SSH, HTTP, HTTPS

- **ssh**
  - Disable root login: `true`
  - Disable password authentication: `true`
  - Configuration: `/etc/ssh/sshd_config`
  - Service resource: `ssh`

## File Structure

Only files used by the cookbook execution flow are listed below.

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

No custom resource provider is used by the executed recipes.

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

No static file paths are listed in the supplied cookbook directory listing. The `nginx.rb` recipe uses `cookbook_file` resources with dynamically derived source names:

```text
test/index.html
ci/index.html
status/index.html
```

These source files must be supplied in the Ansible role or deployment artifact.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)
2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)
3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

### 1. `default` recipe (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- The Ansible role should import task files in the same order:
  - `tasks/security.yml`
  - `tasks/nginx.yml`
  - `tasks/ssl.yml`
  - `tasks/sites.yml`

### 2. `security` recipe (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts the `fail2ban` service.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
- The original plan reports these fail2ban settings, which require template-source verification:
  - `bantime`: `3600`
  - `findtime`: `600`
  - `maxretry`: `3`
  - Backend: `auto`
  - SSH jail on `ssh`
  - SSH log: `/var/log/auth.log`
  - nginx HTTP authentication, request-limit, and bot-search jails
  - nginx HTTP jail ports: `http,https`
  - nginx error logs: `/var/log/nginx/*error.log`
  - nginx access logs: `/var/log/nginx/*access.log`
  - nginx request-limit `maxretry`: `10`
  - nginx bot-search `maxretry`: `2`
- Applies the following UFW commands, subject to source verification of guards:
  - `ufw --force default deny`
  - `ufw allow ssh`
  - `ufw allow http`
  - `ufw allow https`
  - `ufw --force enable`
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- The original plan reports kernel settings for reverse-path filtering, redirect and source-route rejection, martian logging, ICMP restrictions, IPv6 disablement, SYN cookies, and TCP retry/backlog values. Verify the template before migration.
- The original plan reports a delayed `sysctl -p /etc/sysctl.d/99-security.conf` action. Verify the notification relationship before implementation.
- When enabled by the source attributes, changes SSH configuration using:
  - `PermitRootLogin no`
  - `PasswordAuthentication no`
- The `ssh` service is declared with action `nothing` and is reportedly restarted through delayed notifications. Verify guards and notifications in the recipe.
- Reported resource counts:
  - One package resource containing two packages
  - One `fail2ban` service resource
  - Two template resources
  - Five UFW execute resources
  - One sysctl reload execute resource
  - Two conditional SSH hardening execute resources
  - One `ssh` service resource

### 3. `nginx` recipe (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Declares the `nginx` service with enable and start actions and restart, reload, and status support.
- The original plan reports the following nginx settings; verify them against the templates:
  - Worker user: `www-data`
  - Worker processes: `auto`
  - PID file: `/run/nginx.pid`
  - Worker connections: `768`
  - Access log: `/var/log/nginx/access.log`
  - Error log: `/var/log/nginx/error.log`
  - `sendfile on`
  - `tcp_nopush on`
  - `tcp_nodelay on`
  - Keepalive timeout: `65`
  - Gzip enabled
  - Includes `/etc/nginx/conf.d/*.conf`
  - Includes `/etc/nginx/sites-enabled/*`
  - `server_tokens off`
  - Rate-limit zones `login` at `10r/m` and `api` at `30r/m`
  - Client body and header buffer limits
  - Client body, header, and send timeouts of `10`
  - SSL session cache `shared:SSL:10m`
  - SSL session timeout `10m`
  - TLS protocols `TLSv1.2 TLSv1.3`
  - Configured ECDHE/DHE cipher list and server cipher preference
- Creates the following document roots and content files:

  - **test.cluster.local**
    - Creates `/opt/server/test` as `www-data:www-data` with mode `0755`.
    - Deploys `/opt/server/test/index.html` from source `test/index.html` as `www-data:www-data` with mode `0644`.

  - **ci.cluster.local**
    - Creates `/opt/server/ci` as `www-data:www-data` with mode `0755`.
    - Deploys `/opt/server/ci/index.html` from source `ci/index.html` as `www-data:www-data` with mode `0644`.

  - **status.cluster.local**
    - Creates `/opt/server/status` as `www-data:www-data` with mode `0755`.
    - Deploys `/opt/server/status/index.html` from source `status/index.html` as `www-data:www-data` with mode `0644`.

- Iterations:
  - Document-root loop: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`
  - Directory resources: 3
  - Content resources: 3

### 4. `ssl` recipe (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs the `openssl` and `ca-certificates` packages.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` as `root:root` with mode `0755`.
- Creates `/etc/ssl/private` as `root:ssl-cert` with mode `0710`.
- Evaluates the following three SSL-enabled sites:

  - **test.cluster.local**
    - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
    - Key: `/etc/ssl/private/test.cluster.local.key`
    - Reported execute resource: `generate-ssl-cert-test.cluster.local`

  - **ci.cluster.local**
    - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
    - Key: `/etc/ssl/private/ci.cluster.local.key`
    - Reported execute resource: `generate-ssl-cert-ci.cluster.local`

  - **status.cluster.local**
    - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
    - Key: `/etc/ssl/private/status.cluster.local.key`
    - Reported execute resource: `generate-ssl-cert-status.cluster.local`

- The original plan reports self-signed certificate generation with:
  - RSA `2048` keys
  - Validity of `365` days
  - Common name matching the exact site name
  - Subject email `admin@example.com`
  - Private-key ownership `root:ssl-cert`
  - Private-key mode `0640`
- Certificate existence checks and nginx reload notifications are reported but are not confirmed by the structured analysis; verify them in the recipe.
- Iterations:
  - Certificate loop: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`
  - Certificate-generation execute resources: 3

### 5. `sites` recipe (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once per named site.
- Creates one symlink per named site from `sites-enabled` to `sites-available`.
- Iterations:

  - **test.cluster.local**
    - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
    - Destination: `/etc/nginx/sites-available/test.cluster.local`
    - Document root: `/opt/server/test`
    - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
    - Private key: `/etc/ssl/private/test.cluster.local.key`
    - Symlink: `/etc/nginx/sites-enabled/test.cluster.local`
    - Target: `/etc/nginx/sites-available/test.cluster.local`

  - **ci.cluster.local**
    - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
    - Destination: `/etc/nginx/sites-available/ci.cluster.local`
    - Document root: `/opt/server/ci`
    - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
    - Private key: `/etc/ssl/private/ci.cluster.local.key`
    - Symlink: `/etc/nginx/sites-enabled/ci.cluster.local`
    - Target: `/etc/nginx/sites-available/ci.cluster.local`

  - **status.cluster.local**
    - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
    - Destination: `/etc/nginx/sites-available/status.cluster.local`
    - Document root: `/opt/server/status`
    - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
    - Private key: `/etc/ssl/private/status.cluster.local.key`
    - Symlink: `/etc/nginx/sites-enabled/status.cluster.local`
    - Target: `/etc/nginx/sites-available/status.cluster.local`

- Removes `/etc/nginx/sites-enabled/default`.
- The original plan reports that each virtual host provides:
  - HTTP on port `80`
  - HTTP-to-HTTPS redirection
  - HTTPS on port `443` with HTTP/2
  - TLS 1.2 and TLS 1.3
  - HSTS with one-year max age and `includeSubDomains`
  - `index.html`, `index.htm`, and `index.php`
  - Security headers
  - Gzip compression
  - `try_files $uri $uri/ =404`
  - `.htaccess`, `.git`, and `.svn` denial
  - Per-site access and error logs
- Verify these directives against `cookbooks/nginx-multisite/templates/default/site.conf.erb`.
- Reported resource counts:
  - Template: 3
  - Link: 3
  - Default-site file deletion: 1

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: restartable through reported delayed notifications; no explicit start or enable action is reported

**Supported operating systems from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The recipes use Ubuntu-oriented names and paths, including `ufw`, the `ssh` service name, `www-data`, `/var/log/auth.log`, and `/etc/nginx/sites-enabled`. Validate these assumptions before supporting CentOS in Ansible.

## Credentials

**Detection Summary**: No credentials or secret stores detected across the analyzed files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, Vault, secret-manager attribute, secret-related environment variable, password, API key, or access token was detected.

The generated SSL private keys are sensitive files but are created locally rather than retrieved from a credential store.

### SSL Private Keys

- **Variable(s)**: Site-derived certificate and key paths
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files
- **Usage context**: nginx TLS private keys for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Required protection**:
  - Owner: `root`
  - Group: `ssl-cert`
  - Mode: `0640`
  - Private-key directory: `/etc/ssl/private`
  - Directory owner and group: `root:ssl-cert`
  - Directory mode: `0710`

## Checks for the Migration

**Files to verify**:

### Cookbook source files

- `cookbooks/nginx-multisite/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/security.rb`
- `cookbooks/nginx-multisite/recipes/nginx.rb`
- `cookbooks/nginx-multisite/recipes/ssl.rb`
- `cookbooks/nginx-multisite/recipes/sites.rb`
- `cookbooks/nginx-multisite/attributes/default.rb`
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`
- `test/index.html`
- `ci/index.html`
- `status/index.html`

### Deployed configuration and content files

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
- `/etc/nginx/sites-enabled/default` — must not exist
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

### Logs

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

- `test.cluster.local`: HTTP port `80`, HTTPS port `443`
- `ci.cluster.local`: HTTP port `80`, HTTPS port `443`
- `status.cluster.local`: HTTP port `80`, HTTPS port `443`
- SSH: port `22`
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `sysctl-security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

Verify all reported guards, delayed notifications, template directives, and attribute values against the cookbook source before finalizing the Ansible implementation.

## Pre-flight checks:

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# SSH service and configuration
systemctl status ssh
sshd -t
grep '^PermitRootLogin no' /etc/ssh/sshd_config
grep '^PasswordAuthentication no' /etc/ssh/sshd_config

# nginx configuration
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'

# test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
tail -n 20 /var/log/nginx/test.cluster.local_access.log
tail -n 20 /var/log/nginx/test.cluster.local_error.log

# ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
tail -n 20 /var/log/nginx/ci.cluster.local_access.log
tail -n 20 /var/log/nginx/ci.cluster.local_error.log

# status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
tail -n 20 /var/log/nginx/status.cluster.local_access.log
tail -n 20 /var/log/nginx/status.cluster.local_error.log

# Listener and firewall checks
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
ufw status verbose

# fail2ban checks
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E '^(bantime|findtime|maxretry|backend)' /etc/fail2ban/jail.local

# Sysctl checks
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# SSL permissions
stat -c '%U:%G %a %n' /etc/ssl/certs
stat -c '%U:%G %a %n' /etc/ssl/private
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# Removed default site
test ! -e /etc/nginx/sites-enabled/default
```

Expected endpoint behavior:

- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` return an HTTP `301` redirect from port `80` to HTTPS.
- Each HTTPS endpoint on port `443` responds successfully, normally with `200 OK`.
- Each HTTPS response serves its corresponding `/opt/server/<site>/index.html`.
- nginx listens on ports `80` and `443`.
- UFW is active with default incoming policy `deny` and allows SSH, HTTP, and HTTPS.
- The `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails are loaded if those jails are confirmed in the template.
- Reported sysctl values include:
  - `net.ipv4.conf.all.rp_filter = 1`
  - `net.ipv4.conf.default.rp_filter = 1`
  - `net.ipv4.icmp_echo_ignore_all = 1`
  - `net.ipv4.tcp_syncookies = 1`
  - `net.ipv4.tcp_max_syn_backlog = 2048`
  - `net.ipv6.conf.all.disable_ipv6 = 1`
- `/etc/ssl/certs` is `root:root` mode `755`.
- `/etc/ssl/private` is `root:ssl-cert` mode `710`.
- All three private keys are `root:ssl-cert` mode `640`.
