---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with security hardening, UFW firewall rules, fail2ban, SSH hardening, sysctl settings, optional HTTPS, self-signed certificates, and data-bag-driven virtual hosts. Execution order is `security` → `nginx` → `ssl` → `sites`. The supplied analysis does not include the individual `nginx_sites` data-bag item names or template contents, so site instances and template-specific settings require verification from the source data before migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Web server and virtual-host service
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP `80`, TCP `443`; PID file `/run/nginx.pid`
  - Key Config: `/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/security.conf`, `/etc/nginx/sites-enabled/*`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH and nginx logs
  - Key Config: Enabled and started; configured jails and settings require verification from `fail2ban.jail.local.erb`

- **ufw**: Host firewall
  - Location/Path: System firewall configuration
  - Port/Socket: Allows `22/tcp`, `80/tcp`, and `443/tcp`
  - Key Config: Default incoming policy deny; enabled state and detailed rule behavior require verification

- **sshd**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no` and `PasswordAuthentication no`, subject to source verification

- **nginx_sites runtime virtual hosts**: Site definitions loaded from the `nginx_sites` Chef data bag
  - Location/Path: Site-specific document roots and `/etc/nginx/sites-available/<site_name>`
  - Port/Socket: TCP `80`; TCP `443` when `ssl_enabled` is true
  - Key Config: Each item supplies `id`, `document_root`, and `ssl_enabled`
  - Instance names: Not present in the supplied analysis; actual data-bag item names must be supplied before migration

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No provider file is used by the execution tree.

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

No static `files/default/*` or `files/*` files were listed. The `cookbook_file` resource references dynamic site content such as `<site_folder>/index.html`; these source files must be provided separately.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - The Ansible role should preserve this order through task-file imports from `tasks/main.yml`.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures UFW with default incoming deny and allows SSH, HTTP, and HTTPS.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Reloads sysctl settings after the sysctl template changes.
   - Updates `/etc/ssh/sshd_config` to disable root login and password authentication when the corresponding defaults are enabled.
   - Restarts `sshd` only after SSH configuration changes.
   - Detailed fail2ban settings, sysctl values, file modes, and notification behavior require verification from the template and recipe source.

   **Iterations:** No collection loop is identified.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts nginx.
   - Creates `/etc/nginx/secrets`.
   - Loads the `nginx_secrets/site` encrypted data-bag item when confirmed by the source recipe.
   - Writes its `token` value to `/etc/nginx/secrets/site_token` with protected permissions.
   - Reads runtime items from the `nginx_sites` data bag.
   - Uses each item’s `id` as `site_name`, its `document_root` as the document root, and its `ssl_enabled` value to control HTTPS behavior.
   - Creates each runtime site document root and deploys its `index.html` from the site-specific source folder derived from the portion of `site_name` before the first dot.
   - The individual site names and template-specific nginx settings are not present in the supplied analysis and require source verification.

   **Iterations:** Runtime `nginx_sites` items are not named in the supplied data. They must be expanded after the data-bag contents are provided.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` and `/etc/ssl/private`.
   - Generates development self-signed certificates for runtime sites whose `ssl_enabled` value is true.
   - Writes certificates to `/etc/ssl/certs/<site_name>.crt`.
   - Writes private keys to `/etc/ssl/private/<site_name>.key`.
   - Uses 2048-bit RSA keys and 365-day certificates when the source behavior is confirmed.
   - Sets generated private-key ownership to `root:ssl-cert` and mode `0640` when confirmed.
   - Triggers an nginx reload after certificate or key creation.

   **Iterations:** SSL-enabled site names are not present in the supplied data. The certificate-generation tasks must be expanded after the `nginx_sites` collection is supplied.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available`.
   - Creates `/etc/nginx/sites-enabled`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` for runtime site items.
   - Creates `/etc/nginx/sites-enabled/<site_name>` symlinks targeting the corresponding files in `sites-available`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Triggers nginx reloads after site configuration or link changes.
   - Site template behavior, TLS directives, headers, logging, and security settings require verification from `site.conf.erb`.

   **Iterations:** The directory loop contains these exact items:
   - `/etc/nginx/sites-available`
   - `/etc/nginx/sites-enabled`

   Runtime site iterations cannot be expanded because the supplied analysis does not contain the `nginx_sites` item names.

## Dependencies

**External cookbook dependencies**: Not available for validation; `metadata.rb` and dependency analysis were not supplied.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`  
These package requirements are stated by the recipe analysis but require source verification.

**Service dependencies**: `nginx`, `fail2ban`, `sshd`

**Firewall dependencies**: `22/tcp`, `80/tcp`, `443/tcp`

**Platform support**: Claims for Ubuntu `>= 18.04` and CentOS `>= 7.0` require verification from `metadata.rb` or platform analysis.

## Credentials

**Detection Summary**: 1 explicit credential requiring source verification, plus runtime site configuration that may contain sensitive deployment information.

**Source**:
  - **Provider**: Chef encrypted data bag
  - **Bag**: `nginx_secrets`
  - **Item**: `site`
  - **URL**: Not applicable
  - **Path**: `cookbooks/nginx-multisite/recipes/nginx.rb`
  - **Verification status**: The supplied execution analysis shows only `file[/etc/nginx/secrets/site_token]`; the encrypted data-bag load must be confirmed in the underlying recipe.

### Site Token

- **Variable**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag `nginx_secrets`, item `site`
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **Current file ownership**: `root:root`
- **Current file mode**: `0600`
- **Sensitive handling**: Chef resource is reported as `sensitive true`
- **Ansible migration**: Store the value in Ansible Vault or an approved external secret manager and use `no_log: true` for tasks that handle or write it.

### nginx Site Configuration

- **Variable(s)**: `site['id']`, `site['document_root']`, `site['ssl_enabled']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Chef data bag `nginx_sites`
- **Usage context**: Determines site names, document roots, certificate generation, and virtual-host configuration
- **Credential status**: No password or token field is shown for these records; treat them as configuration unless the source data bag contains additional sensitive fields.

### TLS Private Keys

- **Variable(s)/paths**:
  - `/etc/ssl/private/<site_name>.key`
  - `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: nginx HTTPS private keys
- **Expected ownership and mode**: `root:ssl-cert`, `0640`
- **Ansible migration**: Preserve restrictive permissions and do not expose key contents in task output.

### TLS Certificates

- **Variable(s)/paths**:
  - `/etc/ssl/certs/<site_name>.crt`
  - `cert_file`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificates
- **Usage context**: nginx HTTPS certificates
- **Validity**: Reported as 365 days; requires template/recipe verification
- **Subject**: Reported to use the site name as the Common Name

No custom provider, HashiCorp Vault, CyberArk, AWS Secrets Manager, `chef_vault_item`, Conjur variable, environment-variable secret, database connection string, or hardcoded API key was identified in the supplied analysis.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/ssl/certs
/etc/ssl/private
/run/nginx.pid
<document_root>/index.html
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
```

Actual `<site_name>` and `<document_root>` values must be supplied from `nginx_sites`.

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: once per runtime `nginx_sites` item; exact count cannot be determined without the data-bag contents

## Pre-flight checks:

```bash
# Package availability
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# nginx configuration
nginx -t
nginx -T | grep -E 'listen (80|443)|server_name|ssl_certificate|ssl_certificate_key'

# Secret directory and token
ls -ld /etc/nginx/secrets
stat -c '%U:%G %a %n' /etc/nginx/secrets /etc/nginx/secrets/site_token

# Firewall
ufw status verbose
ufw status numbered

# fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH configuration
grep -E '^[# ]*PermitRootLogin|^[# ]*PasswordAuthentication' \
  /etc/ssh/sshd_config
sshd -t

# Kernel settings
sysctl -p /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.default.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.icmp_echo_ignore_broadcasts
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries

# Listening ports
ss -tlnp | grep -E ':(80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN
```

For each named site supplied from `nginx_sites`, run the following individually:

```bash
test -d <document_root>
stat -c '%U:%G %a %n' <document_root>
test -f <document_root>/index.html

test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>

grep -E 'listen 80|listen 443|server_name|root |access_log|error_log' \
  /etc/nginx/sites-available/<site_name>

curl -I -H "Host: <site_name>" http://127.0.0.1/
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

For each SSL-enabled site supplied from `nginx_sites`, additionally run:

```bash
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key

openssl x509 \
  -in /etc/ssl/certs/<site_name>.crt \
  -noout -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key

curl -k -I --resolve <site_name>:443:127.0.0.1 \
  https://<site_name>/
```

Expected SSL checks, subject to source verification:

```text
root:ssl-cert 0640
HTTP/1.1 301 Moved Permanently
Location: https://<site_name>/
```

Validate service notifications after changes:

```bash
nginx -t
systemctl is-active nginx
systemctl is-active fail2ban
systemctl is-active sshd
```

Expected notification behavior requires verification from the recipe and template contents:

- nginx configuration change → nginx reload
- site configuration or link change → nginx reload
- certificate generation → nginx reload
- fail2ban configuration change → fail2ban restart
- sysctl configuration change → sysctl reload
- SSH hardening change → sshd restart
