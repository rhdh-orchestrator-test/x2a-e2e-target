---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an Nginx web server with dynamically defined HTTP and HTTPS sites, optional self-signed TLS certificates, static site roots, UFW firewall rules, Fail2ban protection, SSH hardening, kernel network hardening, and an encrypted site token. The entry recipe executes `security`, `nginx`, `ssl`, and `sites` in that order. Site names, document roots, and SSL settings are loaded from the `nginx_sites` Chef data bag, but the supplied analysis does not identify the actual data bag item names. Those values must be supplied explicitly before migration; no site names should be invented.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**
  - Purpose: Web server and virtual-host service
  - Location/Path: `/etc/nginx/nginx.conf`
  - Port/Socket: TCP `80`; TCP `443` when SSL-enabled sites exist
  - Key Config: Includes `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`; enabled and started as a system service

- **fail2ban**
  - Purpose: Protects SSH and Nginx-related log events
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH, HTTP, and HTTPS-related events
  - Key Config: Enabled jails are `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch`; service enabled and started

- **ufw**
  - Purpose: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Default incoming policy is deny; firewall is enabled

- **sshd**
  - Purpose: SSH administration
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: Root login disabled and password authentication disabled; service restarts only when SSH configuration changes

- **nginx site instances**
  - Purpose: Dynamically configured virtual hosts and static site roots
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: TCP `80`; TCP `443` when `ssl_enabled` is true
  - Key Config: Site data is loaded from the `nginx_sites` data bag. The supplied analysis does not provide exact site names, document roots, or SSL flags. The migration must define one explicit entry per actual data bag item before deployment.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

### Recipes

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

### Providers

```text
```

No provider files are used.

### Templates

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

### Attributes

```text
cookbooks/nginx-multisite/attributes/default.rb
```

### Files

No static files under `files/` are listed in the supplied cookbook directory. The `cookbook_file` resource references site-specific files such as `<site_folder>/index.html`, but those files are not present in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order: security, Nginx, TLS, then sites.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs packages `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures the security collection items:
     - **fail2ban**: service enabled and started; configuration protects SSH and Nginx log events.
     - **ufw**: default incoming policy deny; allows SSH, HTTP, and HTTPS; enables the firewall.
     - **ssh**: disables root login and password authentication when the corresponding attributes are enabled.
   - Applies UFW commands for default deny, SSH, HTTP, HTTPS, and firewall enablement with idempotence guards.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` when the kernel security template changes.
   - Updates `/etc/ssh/sshd_config` to set `PermitRootLogin no` and `PasswordAuthentication no`.
   - Restarts `sshd` only when either SSH hardening command changes the configuration.
   - Contains 1 package resource, 2 service resources, 2 template resources, and 8 execute resources.
   - The detailed template directives and attribute values require confirmation because they are not included in the supplied structured analysis.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads the encrypted Chef data bag item `nginx_secrets/site`.
   - Writes the `token` value to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`.
   - Creates one document root per actual `nginx_sites` data bag item, using the item’s `document_root` value, owner `nginx:nginx`, and mode `0755`.
   - Deploys one `index.html` file per actual site to its document root with owner `nginx:nginx` and mode `0644`.
   - Derives the static file source directory from the first component of the site name.
   - The site data fields `id`, `document_root`, and `ssl_enabled` are implementation assumptions requiring validation against the actual recipes and data bag.
   - Site item names and document roots are unavailable in the supplied analysis and must be added explicitly before migration.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Evaluates the SSL setting for each actual `nginx_sites` data bag item.
   - Creates no certificate-generation resource for sites with SSL disabled.
   - For SSL-enabled sites, generates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Uses an execute resource named `generate-ssl-cert-<site_name>`.
   - Generates self-signed RSA 2048-bit certificates valid for 365 days when both files do not already exist.
   - Sets generated key ownership to `root:ssl-cert` and mode `0640`.
   - Reloads Nginx after generating a certificate.
   - Exact SSL-enabled site names are unavailable and must be supplied from the actual data bag.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - The directory iteration contains exactly:
     - `/etc/nginx/sites-available`
     - `/etc/nginx/sites-enabled`
   - Renders one `site.conf.erb` template per actual `nginx_sites` item to `/etc/nginx/sites-available/<site_name>`.
   - Creates one symlink per actual site at `/etc/nginx/sites-enabled/<site_name>` pointing to its available configuration.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Reloads Nginx when a site template, site symlink, or default-site deletion changes.
   - Uses the following template variables:
     - `server_name`
     - `document_root`
     - `ssl_enabled`
     - `cert_file`
     - `key_file`
   - Exact site names and render counts remain undetermined until the real `nginx_sites` data bag is supplied.

## Dependencies

**External cookbook dependencies**: None declared in the supplied `metadata.rb`.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**: `nginx`, `fail2ban`, `sshd`.

**Required external data sources**:

- Plain Chef data bag `nginx_sites`
- Encrypted Chef data bag `nginx_secrets`, item `site`
- Site-specific static files referenced by `cookbook_file`

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`.

## Credentials

**Detection Summary**: 1 direct credential detected across 1 recipe, plus locally generated TLS private keys and certificates.

**Source**:
  - **Provider**: Chef encrypted data bag provider
  - **URL**: None
  - **Path**: `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`, called from `cookbooks/nginx-multisite/recipes/nginx.rb`

### Nginx Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag `nginx_secrets`, item `site`
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **File permissions**: Owner `root`, group `root`, mode `0600`
- **Migration handling**: Store the value in Ansible Vault or retrieve it from an approved secret manager. Do not place cleartext in ordinary Git-managed variables.

### TLS Private Keys

- **Variable(s)**: `/etc/ssl/private/<site_name>.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL; not retrieved from a vault
- **Usage context**: Nginx HTTPS private keys
- **Permissions**: Owner `root`, group `ssl-cert`, mode `0640`
- **Migration handling**: Preserve local self-signed generation only for development. Production deployments should use an approved certificate authority or secret store.

### TLS Certificates

- **Variable(s)**: `/etc/ssl/certs/<site_name>.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated self-signed certificates
- **Usage context**: Nginx HTTPS certificates
- **Validity**: 365 days
- **Common name**: Site name

No HashiCorp Vault, CyberArk, Conjur, AWS Secrets Manager, environment-variable credential, embedded database password, API key, or additional hardcoded token was detected.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs
/etc/ssl/private
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
<document_root>/index.html
```

**Service endpoints to check**:

- TCP `80`: Nginx HTTP
- TCP `443`: Nginx HTTPS for SSL-enabled sites
- TCP `22`: SSH
- Unix sockets: None

**Templates rendered**:

- `nginx.conf.erb`: once
- `security.conf.erb`: once
- `fail2ban.jail.local.erb`: once
- `sysctl-security.conf.erb`: once
- `site.conf.erb`: once per actual `nginx_sites` data bag item; exact count is unavailable because the item list was not supplied

## Pre-flight checks

```bash
# Package checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service checks for every named service instance
systemctl status nginx --no-pager
systemctl status fail2ban --no-pager
systemctl status sshd --no-pager

# Nginx configuration checks
nginx -t
nginx -T | grep -E 'include /etc/nginx/conf.d|include /etc/nginx/sites-enabled'
grep -E 'worker_processes|worker_connections|keepalive_timeout|gzip' /etc/nginx/nginx.conf
grep -E 'server_tokens|ssl_protocols|ssl_session_cache|client_max_body_size' \
  /etc/nginx/conf.d/security.conf

# Firewall checks
ufw status verbose
ufw status numbered

# Fail2ban checks
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH checks
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t

# Kernel checks
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# Listener checks for each configured endpoint
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
ss -tlnp | grep ':22 '

# Secret-file checks; never print the token
test -f /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token

# Service log checks
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
```

Expected results:

- `nginx`, `fail2ban`, and `sshd` are installed and active.
- Nginx configuration validation succeeds.
- UFW is active with default incoming deny and allows TCP `22`, `80`, and `443`.
- Fail2ban reports the four configured jails.
- Root SSH login and password authentication are disabled.
- Kernel hardening values match the validated template once the template contents are confirmed.
- Nginx listens on TCP `80` and listens on TCP `443` when at least one SSL-enabled site exists.
- `/etc/nginx/secrets/site_token` has mode `0600` and owner `root:root`.

No exact site instances were supplied in the source analysis. Before site-specific validation can be executed, obtain the real `nginx_sites` item names and values, then create one explicit check block per named site covering its document root, `index.html`, available configuration, enabled symlink, HTTP behavior, and—when SSL is enabled—certificate, key, HTTPS behavior, and certificate subject.