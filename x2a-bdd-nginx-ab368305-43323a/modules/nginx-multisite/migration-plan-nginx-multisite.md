---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, SSH, and kernel-security hardening; deploys global and per-site Nginx configuration; creates three document roots and index files; generates self-signed certificates; and enables the three virtual hosts. The Ansible implementation must preserve the execution order: security, Nginx installation and base configuration, SSL certificate generation, and site virtual-host configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; index file `/opt/server/test/index.html`

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; index file `/opt/server/ci/index.html`

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; index file `/opt/server/status/index.html`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: None specified
  - Key Config: Enabled and started; configuration deployed from `fail2ban.jail.local.erb`

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: SSH, HTTP `80`, HTTPS `443`
  - Key Config: Enabled with default-deny policy; SSH, HTTP, and HTTPS allowed

- **ssh**: SSH service hardening
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: Standard SSH port
  - Key Config: Root login disabled; password authentication disabled

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

No provider files are used by the execution tree. `resources/lineinfile.rb` is mentioned in structural analysis but is not executed or referenced and is therefore excluded.

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

No static files are present in the supplied directory listing. The recipes deploy `test/index.html`, `ci/index.html`, and `status/index.html`; equivalent Ansible source files must be supplied or those deployments must otherwise be preserved.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - The Ansible role must preserve this execution order through task files or role includes.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Applies UFW commands in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as an execute resource with action `nothing`; no automatic notification is shown.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Declares `service[ssh]` with action `nothing`; no SSH restart or reload notification is shown.
   - Uses idempotent Ansible UFW and `lineinfile` tasks where available.
   - Resources: one package resource, two service resources, two templates, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` with mode `0755`.
   - Deploys `test/index.html` to `/opt/server/test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` with mode `0755`.
   - Deploys `ci/index.html` to `/opt/server/ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` with mode `0755`.
   - Deploys `status/index.html` to `/opt/server/status/index.html` with mode `0644`.
   - Iterations: `nginx.sites` contains exactly `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - No executed `group[www-data]` resource is shown; it must not be added without separate source verification.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755` and group `root`.
   - Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
   - Generates a self-signed 2048-bit RSA certificate valid for 365 days for `test.cluster.local`:
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
     - Key mode and ownership: `0640`, `root:ssl-cert`
   - Generates a self-signed 2048-bit RSA certificate valid for 365 days for `ci.cluster.local`:
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`
     - Key mode and ownership: `0640`, `root:ssl-cert`
   - Generates a self-signed 2048-bit RSA certificate valid for 365 days for `status.cluster.local`:
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`
     - Key mode and ownership: `0640`, `root:ssl-cert`
   - Iterations: certificate generation runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; all three have `ssl_enabled: true`.
   - Resources: one package resource installing two packages, one group, two directories, and three certificate-generation execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times with mode `0644`.
   - For `test.cluster.local`, renders `/etc/nginx/sites-available/test.cluster.local` with:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` linking to the available-site configuration.
   - For `ci.cluster.local`, renders `/etc/nginx/sites-available/ci.cluster.local` with:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` linking to the available-site configuration.
   - For `status.cluster.local`, renders `/etc/nginx/sites-available/status.cluster.local` with:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` linking to the available-site configuration.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Iterations: site configuration runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - No explicit Nginx reload or restart notification is shown; use a handler only if the intended operational behavior is approved.

## Dependencies

**External cookbook dependencies**: Not specified.

**System package dependencies**:
- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started by `cookbooks/nginx-multisite/recipes/security.rb`
- `nginx`: enabled and started by `cookbooks/nginx-multisite/recipes/nginx.rb`
- `ssh`: declared with action `nothing`; no automatic restart or reload is shown

## Credentials

**Detection Summary**: No credentials or secret values detected.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### TLS Private Keys

- **Variable(s)**: `/etc/ssl/private/test.cluster.local.key`, `/etc/ssl/private/ci.cluster.local.key`, `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; not stored in a data bag, vault, environment variable, or secret attribute.
- **Usage context**: Nginx HTTPS private keys generated with OpenSSL, owned by `root:ssl-cert`, and assigned mode `0640`.

### TLS Certificates

- **Variable(s)**: `/etc/ssl/certs/test.cluster.local.crt`, `/etc/ssl/certs/ci.cluster.local.crt`, `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate files.
- **Usage context**: Nginx HTTPS virtual-host certificates valid for 365 days.

No data bags, encrypted data bags, Chef Vault items, Conjur variables, CyberArk integrations, environment-variable secret references, database credentials, API tokens, or hardcoded passwords were identified.

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

**Service endpoints to check**:
- HTTP: port `80`
- HTTPS: port `443`
- SSH: standard SSH port
- Unix sockets: none specified

**Templates rendered**:
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once, to `/etc/fail2ban/jail.local`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once, to `/etc/nginx/nginx.conf`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once, to `/etc/nginx/conf.d/security.conf`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once, to `/etc/sysctl.d/99-security.conf`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: three times, to:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Nginx configuration
nginx -t
nginx -T

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# TLS key ownership and permissions
stat -c '%A %U:%G %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# TLS certificate metadata
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Firewall
ufw status verbose
ufw status numbered

# Fail2ban
fail2ban-client status
test -f /etc/fail2ban/jail.local

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t

# Sysctl
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Listening ports
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Default site removal
test ! -e /etc/nginx/sites-enabled/default
```

Expected results:

- `nginx` and `fail2ban` are enabled and active.
- `nginx -t` succeeds and the expanded configuration contains `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
- Each site has its document root, index file, available-site configuration, enabled link, certificate, and private key.
- Each site responds over HTTP and HTTPS with a valid response.
- Private keys have mode `0640` and ownership `root:ssl-cert`.
- Certificates have the expected site name and one-year validity.
- UFW is active with a default-deny policy and allows SSH, HTTP, and HTTPS.
- Fail2ban is running and `/etc/fail2ban/jail.local` exists.
- SSH configuration contains `PermitRootLogin no` and `PasswordAuthentication no`; `sshd -t` succeeds.
- `/etc/sysctl.d/99-security.conf` exists and loads without errors.
- Nginx listens on ports `80` and `443`.
- `/etc/nginx/sites-enabled/default` is absent.