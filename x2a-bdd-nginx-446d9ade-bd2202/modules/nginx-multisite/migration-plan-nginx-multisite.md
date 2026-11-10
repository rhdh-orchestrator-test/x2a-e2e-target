---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures Nginx with three HTTPS-enabled sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It applies Fail2ban, UFW, SSH, and kernel security hardening; installs Nginx and SSL packages; generates self-signed RSA certificates; creates site content and virtual hosts; enables the sites; and removes the default Nginx site. The migration must preserve the recipe order: security, Nginx installation, SSL generation, and site configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: None
  - Key Config: Package installed; service enabled and started

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows SSH `22`, HTTP `80`, and HTTPS `443`
  - Key Config: Default policy denied; firewall forcibly enabled

- **ssh**: SSH daemon hardening
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: SSH `22`
  - Key Config: Root login disabled; password authentication disabled; `sshd` resource declared with action `nothing`; no explicit restart or reload is shown

## File Structure

The following files are relevant to this migration and are listed relative to the cookbook root.

**Recipes:**
```text
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

**Providers:**
```text
```

No provider files are used by the execution tree.

**Templates:**
```text
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb
```

**Attributes:**
```text
attributes/default.rb
```

**Files:**
```text
```

No static file paths are listed in the supplied directory listing. The recipes use `cookbook_file` resources for site index files with dynamic source paths based on the site folder.

## Attributes

`cookbooks/nginx-multisite/attributes/default.rb` defines:

- `default['nginx']['sites']['test.cluster.local']['document_root']`: `/opt/server/test`
- `default['nginx']['sites']['test.cluster.local']['ssl_enabled']`: `true`
- `default['nginx']['sites']['ci.cluster.local']['document_root']`: `/opt/server/ci`
- `default['nginx']['sites']['ci.cluster.local']['ssl_enabled']`: `true`
- `default['nginx']['sites']['status.cluster.local']['document_root']`: `/opt/server/status`
- `default['nginx']['sites']['status.cluster.local']['ssl_enabled']`: `true`
- `default['nginx']['ssl']['certificate_path']`: `/etc/ssl/certs`
- `default['nginx']['ssl']['private_key_path']`: `/etc/ssl/private`
- `default['security']['fail2ban']['enabled']`: `true`
- `default['security']['ufw']['enabled']`: `true`
- `default['security']['ssh']['disable_root']`: `true`
- `default['security']['ssh']['password_auth']`: `false`

The Ansible implementation must retain all three site names and document roots as distinct entries.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Executes `security.rb`, `nginx.rb`, `ssl.rb`, and `sites.rb` in that order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default policy to deny.
   - Allows SSH, HTTP, and HTTPS through UFW.
   - Forces UFW to become enabled.
   - Renders `templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Declares `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; no notification is shown.
   - Executes root SSH login hardening because `node['security']['ssh']['disable_root']` is `true`:
     ```bash
     sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
     ```
   - Executes SSH password-authentication hardening because `node['security']['ssh']['password_auth']` is `false`:
     ```bash
     sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
     ```
   - Declares `service[sshd]` with action `nothing`; no explicit restart or reload is shown.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` with mode `0755`.
   - Deploys `/opt/server/test/index.html` from the dynamic source `test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` with mode `0755`.
   - Deploys `/opt/server/ci/index.html` from the dynamic source `ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` with mode `0755`.
   - Deploys `/opt/server/status/index.html` from the dynamic source `status/index.html` with mode `0644`.
   - Does not show an explicit Nginx reload or restart notification after configuration or content changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
   - Generates the certificate for **test.cluster.local** using an execute resource named `generate-ssl-cert-test.cluster.local`:
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - RSA key size: `2048`
     - Validity: `365` days
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
     - Key owner and group: `root:ssl-cert`
     - Key mode: `0640`
   - Generates the certificate for **ci.cluster.local** using an execute resource named `generate-ssl-cert-ci.cluster.local`:
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - RSA key size: `2048`
     - Validity: `365` days
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`
     - Key owner and group: `root:ssl-cert`
     - Key mode: `0640`
   - Generates the certificate for **status.cluster.local** using an execute resource named `generate-ssl-cert-status.cluster.local`:
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - RSA key size: `2048`
     - Validity: `365` days
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`
     - Key owner and group: `root:ssl-cert`
     - Key mode: `0640`
   - The migration should use idempotent certificate-generation modules or guarded commands that do not overwrite existing certificates on every run.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with mode `0755`.
   - Does not include a `group[root]` resource; no corresponding Ansible group task should be added.
   - Renders `templates/default/site.conf.erb` for **test.cluster.local** to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`, using:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `templates/default/site.conf.erb` for **ci.cluster.local** to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`, using:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `templates/default/site.conf.erb` for **status.cluster.local** to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`, using:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.

## Dependencies

**External cookbook dependencies**: None shown in the supplied execution tree or directory listing.

**System package dependencies**: `fail2ban`, `ufw`, `nginx`, `openssl`, `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: declared with action `nothing`; no explicit restart or reload is shown

**Firewall allowances**: SSH, HTTP, HTTPS

## Credentials

**Detection Summary**: No externally supplied authentication credentials, passwords, API tokens, data bags, Chef Vault references, CyberArk integrations, or secret-manager integrations were detected.

The three TLS private keys are sensitive generated artifacts, not externally supplied credentials. They are generated locally and stored under `/etc/ssl/private` with mode `0640` and group `ssl-cert`.

**Source**:
  - **Provider**: None detected
  - **URL**: Not applicable
  - **Path**: Local generated files under `/etc/ssl/private`

### TLS Private Keys
- **Variable(s)**: No credential variable detected
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/attributes/default.rb`
- **Current storage**: Locally generated private-key files
- **Usage context**: TLS private keys for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`

The certificate subject contains the literal email address `admin@example.com`; this is certificate metadata, not an authentication secret.

## Checks for the Migration

**Files to verify**:
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/nginx/sites-enabled/default` must not exist

**Service endpoints to check**:
- HTTP: port `80`
- HTTPS: port `443`
- SSH: port `22`
- Nginx Unix socket: none specified
- Hostnames: `test.cluster.local`, `ci.cluster.local`, `status.cluster.local`

**Templates rendered**:
- `templates/default/fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `templates/default/nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `templates/default/security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `templates/default/sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `templates/default/site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:
```bash
# Package verification
dpkg-query -W fail2ban ufw nginx openssl ca-certificates

# Service verification
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx

systemctl status sshd
nginx -t

# Firewall verification
ufw status verbose
ufw status numbered

# Expected:
# - UFW is active with default incoming policy deny.
# - SSH, HTTP, and HTTPS are allowed.
# - fail2ban and nginx are enabled and active.

# Security configuration verification
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
grep -v '^[[:space:]]*#' /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Expected:
# PermitRootLogin no
# PasswordAuthentication no
# Verify an alternate administrative session before terminating the current session.

# test.cluster.local content and TLS verification
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%A %U:%G %n' /etc/ssl/private/test.cluster.local.key
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
curl -I --resolve test.cluster.local:80:127.0.0.1 http://test.cluster.local/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# Expected:
# Certificate CN is test.cluster.local, validity is approximately 365 days,
# key ownership is root:ssl-cert, key mode is 0640, and the enabled link targets
# /etc/nginx/sites-available/test.cluster.local.

# ci.cluster.local content and TLS verification
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%A %U:%G %n' /etc/ssl/private/ci.cluster.local.key
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
curl -I --resolve ci.cluster.local:80:127.0.0.1 http://ci.cluster.local/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# Expected:
# Certificate CN is ci.cluster.local, validity is approximately 365 days,
# key ownership is root:ssl-cert, key mode is 0640, and the enabled link targets
# /etc/nginx/sites-available/ci.cluster.local.

# status.cluster.local content and TLS verification
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%A %U:%G %n' /etc/ssl/private/status.cluster.local.key
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
curl -I --resolve status.cluster.local:80:127.0.0.1 http://status.cluster.local/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Expected:
# Certificate CN is status.cluster.local, validity is approximately 365 days,
# key ownership is root:ssl-cert, key mode is 0640, and the enabled link targets
# /etc/nginx/sites-available/status.cluster.local.

# Default-site removal
test ! -e /etc/nginx/sites-enabled/default

# Listening-port verification
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
ss -tlnp | grep ':22 '

# Expected:
# Nginx listens on ports 80 and 443, and SSH listens on port 22.

# Log verification
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u sshd --no-pager -n 100

# Validate the Nginx error-log path rendered by nginx.conf and security.conf.
```