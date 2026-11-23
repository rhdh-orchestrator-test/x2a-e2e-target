---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with dynamically discovered virtual sites from the `nginx_sites` Chef data bag. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies nginx, kernel, firewall, and SSH hardening; optionally creates self-signed certificates; renders HTTP or HTTPS virtual hosts; deploys site content; and manages nginx reloads and service notifications. The source analysis does not include the literal `nginx_sites` item names or template contents, so site-specific instances and several configuration values require confirmation from the cookbook source and data bags before migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**
  - Purpose: Web server and virtual-host service
  - Package: `nginx`
  - Configuration: `/etc/nginx/nginx.conf`
  - Security configuration: `/etc/nginx/conf.d/security.conf`
  - Service: `nginx`
  - Ports: TCP `80`; TCP `443` for SSL-enabled sites
  - Logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

- **fail2ban**
  - Purpose: Intrusion prevention for SSH and nginx
  - Package: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Service: `fail2ban`
  - Action: Enabled and started
  - Jails: `sshd`, `nginx-http-auth`, `nginx-limit-req`, `nginx-botsearch`

- **ufw**
  - Purpose: Host firewall
  - Package: `ufw`
  - Policy: Default incoming deny
  - Allowed services: SSH, HTTP, HTTPS
  - Port rules: TCP `22`, `80`, and `443`
  - Action: Enabled

- **sshd**
  - Purpose: SSH access
  - Configuration: `/etc/ssh/sshd_config`
  - Expected hardening: `PermitRootLogin no` and `PasswordAuthentication no`
  - Service behavior: Restarted when the corresponding configuration changes; not enabled or started by this cookbook

- **nginx_sites runtime instances**
  - Purpose: Data-bag-defined nginx virtual hosts
  - Source: Chef data bag `nginx_sites`
  - Exact item names: Not present in the supplied analysis and must be obtained before migration
  - Required attributes:
    - `id`: Site hostname and nginx `server_name`
    - `document_root`: Site content directory
    - `ssl_enabled`: Boolean controlling HTTPS configuration and certificate generation
  - HTTP port: `80`
  - HTTPS port: `443` when `ssl_enabled` is true
  - Configuration: `/etc/nginx/sites-available/<site_name>`
  - Enabled link: `/etc/nginx/sites-enabled/<site_name>`
  - Certificate: `/etc/ssl/certs/<site_name>.crt`
  - Private key: `/etc/ssl/private/<site_name>.key`
  - Access log: `/var/log/nginx/<site_name>_access.log`
  - Error log: `/var/log/nginx/<site_name>_error.log`
  - Content index: `<document_root>/index.html`
  - Content source: `<site_folder>/index.html`, where `site_folder` is the first component of the hostname before the first dot

## File Structure

The following files are used by the cookbook and are listed using paths relative to the cookbook root.

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

No provider file is used by the analyzed execution tree. The analyzed `resources/lineinfile.rb` custom resource is not invoked by the recipes and is excluded from the migration flow.

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

No static files under `files/` are listed in the supplied cookbook structure. The `cookbook_file` resource references dynamic site content sources such as `<site_folder>/index.html`; those files are not included in the supplied listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The migration must preserve this execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Applies UFW default-deny policy and allows SSH, HTTP, and HTTPS.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Reloads sysctl settings after the sysctl template changes.
   - Applies SSH hardening for root login and password authentication when the corresponding attributes enable those commands.
   - Restarts `sshd` after an SSH hardening change.
   - Template settings, command guards, file modes, and notification details require confirmation from the source files because they are not present in the structured validation data.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with restrictive ownership and permissions.
   - Loads the encrypted `nginx_secrets` data-bag item named `site` and writes its `token` value to `/etc/nginx/secrets/site_token`; this source-code detail requires confirmation.
   - Reads the runtime item names from the `nginx_sites` data bag.
   - For each runtime item name, reads the item, obtains `id` and `document_root`, creates the document root, derives the first hostname component as `site_folder`, and deploys `<site_folder>/index.html` to `<document_root>/index.html`.
   - Runtime site names and document roots are not present in the supplied analysis and cannot be expanded into literal instances.
   - Nginx template settings and notification semantics require confirmation from the template and recipe source files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private` with group `ssl-cert`.
   - Reads the runtime items from the `nginx_sites` data bag.
   - For each runtime item whose `ssl_enabled` value is true, generates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Skips certificate generation when both certificate and key already exist.
   - Applies the configured private-key ownership and permissions after generation.
   - Reloads nginx after a newly generated certificate or key.
   - The exact SSL-enabled site names and certificate command details require confirmation from the source recipe.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available`.
   - Creates `/etc/nginx/sites-enabled`.
   - Reads the runtime items from the `nginx_sites` data bag.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` for each runtime site.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` pointing to the corresponding available-site configuration.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Reloads nginx when a virtual-host template, enabled-site link, or default-site removal changes.
   - SSL-enabled sites are expected to redirect HTTP to HTTPS and listen on HTTPS port `443`; non-SSL sites serve directly on HTTP port `80`.
   - The exact template directives and notification behavior require confirmation from the source template and recipe files.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata analysis; metadata confirmation is required.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd` for conditional restarts

**External data sources**:

- Plain Chef data bag: `nginx_sites`
- Encrypted Chef data bag: `nginx_secrets`, item `site`

**Supported platforms**: Platform support was not included in the supplied structured analysis and requires metadata confirmation.

## Credentials

**Detection Summary**: 1 data-bag credential detected in `recipes/nginx.rb`, plus locally generated TLS private keys.

**Source**:
  - **Provider**: Chef encrypted data bag
  - **URL**: None
  - **Path**: `nginx_secrets`, item `site`
  - **Consumer**: `cookbooks/nginx-multisite/recipes/nginx.rb`
  - **Source-code confirmation**: The encrypted data-bag call and variable name require confirmation because the structured execution tree exposes only the destination file resource.

### Site Secret Token

- **Variable**: `site_secret['token']`, subject to source confirmation
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Source**: `nginx_secrets`, item `site`
- **Destination**: `/etc/nginx/secrets/site_token`
- **Current permissions**: Owner `root`, group `root`, mode `0600`
- **Usage context**: nginx-related site secret token
- **Migration storage**: Ansible Vault or an approved external secret manager
- **Migration handling**: Use `no_log: true` for secret-handling tasks and do not commit the value in plaintext

### TLS Private Keys

- **Variable**: `key_file`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated self-signed private key
- **Path**: `/etc/ssl/private/<site_name>.key`
- **Usage context**: nginx TLS private key
- **Expected ownership**: `root:ssl-cert`
- **Expected mode**: `0640`
- **Migration handling**: Production deployments should normally use managed certificates or externally supplied certificate and key material instead of development-style self-signed certificates.

No references were identified to HashiCorp Vault, CyberArk, Conjur, AWS Secrets Manager, environment-variable secrets, hardcoded API keys or passwords, database connection strings, or embedded TLS certificate data.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/ssl/certs
/etc/ssl/private
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
<document_root>/index.html
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
/var/log/auth.log
```

The literal `<site_name>` and `<document_root>` values must be replaced with every item obtained from `nginx_sites`.

**Service endpoints to check**:

- TCP `22` for SSH
- TCP `80` for HTTP
- TCP `443` for SSL-enabled sites
- Unix socket: None configured by this cookbook

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
  - Render count: 1
  - Destination: `/etc/fail2ban/jail.local`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
  - Render count: 1
  - Destination: `/etc/nginx/nginx.conf`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`
  - Render count: 1
  - Destination: `/etc/nginx/conf.d/security.conf`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`
  - Render count: 1
  - Destination: `/etc/sysctl.d/99-security.conf`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Render count: One per runtime `nginx_sites` item
  - Destination: `/etc/nginx/sites-available/<site_name>`

## Pre-flight checks

The literal site names and attributes must be obtained from the `nginx_sites` data bag before running site-specific checks.

```bash
# Package checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service checks
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# nginx syntax and includes
nginx -t
nginx -T | grep -E 'include /etc/nginx/(conf.d|sites-enabled)|listen (80|443)'
grep -E 'worker_processes|worker_connections|keepalive_timeout|access_log|error_log|gzip' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Firewall checks
ufw status verbose
ufw status numbered

# fail2ban checks
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E '^(bantime|findtime|maxretry|backend)|^\[(sshd|nginx-http-auth|nginx-limit-req|nginx-botsearch)\]' \
  /etc/fail2ban/jail.local

# Kernel checks
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
cat /etc/sysctl.d/99-security.conf

# SSH checks
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config
sshd -t
systemctl is-active sshd

# SSL directory checks
ls -ld /etc/ssl/certs /etc/ssl/private
getent group ssl-cert

# Listener checks
ss -tlnp | grep -E ':(80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# General log checks
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
journalctl -u nginx --since "10 minutes ago"
journalctl -u fail2ban --since "10 minutes ago"
```

For every actual site obtained from `nginx_sites`, substitute its literal hostname and document root in the following checks:

```bash
# Site content and links
test -d <document_root>
test -f <document_root>/index.html
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -E 'server_name|listen|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/<site_name>

# Site-specific logs
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

For every site with `ssl_enabled: true`:

```bash
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -issuer -dates
openssl rsa -in /etc/ssl/private/<site_name>.key -check -noout
stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key
curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
```

Expected SSL-enabled behavior:

- HTTP returns `301`.
- HTTPS returns a successful response when site content exists.
- The certificate and key paths are configured.
- The private key is owned by `root:ssl-cert` with mode `0640`, subject to source confirmation.
- The HTTPS response includes the configured security headers and HSTS header, subject to template confirmation.

For every site with `ssl_enabled: false`:

```bash
curl -I -H 'Host: <site_name>' http://127.0.0.1/
```

Expected non-SSL behavior:

- HTTP serves the site directly.
- No HTTPS certificate configuration is rendered for that site.

Migration completion requires the complete `nginx_sites` data-bag contents, confirmation of the cookbook attributes, validation of the recipe source details, and validation of the template contents before site-specific Ansible variables and tasks are generated.