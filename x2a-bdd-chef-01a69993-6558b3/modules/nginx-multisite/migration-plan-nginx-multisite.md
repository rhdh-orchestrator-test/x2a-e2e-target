---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook provisions an Nginx web server with data-bag-defined sites, installs and configures Fail2ban and UFW, applies sysctl and SSH hardening, generates self-signed TLS certificates for SSL-enabled sites, deploys site content, and renders enabled Nginx virtual hosts. Recipes execute in the order `security.rb`, `nginx.rb`, `ssl.rb`, and `sites.rb`. The supplied analysis does not contain the `nginx_sites` data-bag item names or values, so exact site instances, document roots, and SSL-enabled sites must be supplied before site-specific migration tasks can be finalized.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

No exact site instance names were supplied in the analyzed cookbook. Site definitions are read dynamically from the `nginx_sites` data bag.

Expected site attributes:

- `site_name`: Data-bag item name
- `document_root`: Site document root
- `ssl_enabled`: Whether a self-signed certificate is generated
- `site_folder`: Source directory for the site `index.html`

**Nginx**: Primary web server
- Location/Path: `/etc/nginx`
- Port/Socket: TCP ports 80 and 443 when configured
- Key Config:
  - Main configuration: `/etc/nginx/nginx.conf`
  - Security configuration: `/etc/nginx/conf.d/security.conf`
  - Available sites: `/etc/nginx/sites-available`
  - Enabled sites: `/etc/nginx/sites-enabled`
  - Secret token: `/etc/nginx/secrets/site_token`

**Fail2ban**: Intrusion-prevention service
- Location/Path: `/etc/fail2ban/jail.local`
- Port/Socket: None
- Key Config: Service is enabled and started

**UFW**: Host firewall
- Location/Path: System firewall configuration
- Port/Socket:
  - SSH service alias
  - TCP port 80 through the HTTP alias
  - TCP port 443 through the HTTPS alias
- Key Config:
  - Default incoming policy: deny
  - Firewall enabled

**SSH**: SSH service hardening
- Location/Path: `/etc/ssh/sshd_config`
- Port/Socket: Host-configured SSH port; the cookbook does not specify a numeric port
- Key Config:
  - `PermitRootLogin no` when `security.ssh.disable_root` is true
  - `PasswordAuthentication no` when `security.ssh.password_auth` is false

**SSL certificates**: Self-signed certificates for SSL-enabled sites
- Location/Path: `/etc/ssl/certs/<site_name>.crt`
- Port/Socket: Used by HTTPS on TCP port 443
- Key Config:
  - RSA 2048-bit key
  - 365-day validity
  - Common name equal to the site name
  - Self-signed
  - Private key: `/etc/ssl/private/<site_name>.key`

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

No provider files are used by the execution tree. The analyzed `resources/lineinfile.rb` custom resource is not invoked by an executed recipe and is excluded from the migration.

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

No static files under `files/` are listed in the supplied analysis. Site content is deployed through a dynamic `cookbook_file` resource whose source path and filename are constructed from the site definition.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes the component recipes in this order:
     1. `nginx-multisite::security`
     2. `nginx-multisite::nginx`
     3. `nginx-multisite::ssl`
     4. `nginx-multisite::sites`
   - The Ansible role must preserve this task-file order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Sets the UFW default policy to deny.
   - Allows the SSH service alias.
   - Allows HTTP through the HTTP service alias, normally TCP port 80.
   - Allows HTTPS through the HTTPS service alias, normally TCP port 443.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Declares `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; the supplied execution tree shows no notification that invokes it.
   - Changes `PermitRootLogin` to `no` when `node['security']['ssh']['disable_root']` is true. The default is true.
   - Changes `PasswordAuthentication` to `no` when `node['security']['ssh']['password_auth']` is false. The default is false.
   - Declares `service[sshd]` with action `nothing`.
   - Only the SSH hardening resources are evidenced as conditional. The `fail2ban.enabled` and `ufw.enabled` attributes exist, but the execution tree does not show conditions around the Fail2ban or UFW resources.
   - Execute resources: 6 total, consisting of 4 unconditional resources and 2 conditional SSH-hardening resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts `service[nginx]`.
   - Creates `/etc/nginx/secrets`.
   - Writes `site_secret['token']` to `/etc/nginx/secrets/site_token`.
   - Reads site definitions from `data_bag('nginx_sites')`.
   - The supplied analysis contains no data-bag item names, so no named site iterations can be expanded.
   - The dynamic site operations create the configured document root and deploy `index.html` from the configured `site_folder`.
   - No explicit Nginx reload or restart notification is shown for the rendered configuration or site files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private` with group `ssl-cert`.
   - Reads site definitions from `data_bag('nginx_sites')`.
   - Generates a certificate only when a site’s `ssl_enabled` value is true.
   - The supplied analysis contains no site names or `ssl_enabled` values, so no named SSL iterations can be expanded.
   - Generates `/etc/ssl/certs/<site_name>.crt`.
   - Generates `/etc/ssl/private/<site_name>.key`.
   - Uses a self-signed 2048-bit RSA certificate valid for 365 days.
   - Uses subject values `C=US`, `ST=Example`, `L=Example`, `O=Example Org`, `OU=IT`, `CN=<site_name>`, and `emailAddress=admin@example.com`.
   - Sets private-key mode to `0640`, owner `root`, and group `ssl-cert`.
   - Ansible should use `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate` where available, avoiding unnecessary certificate regeneration.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with mode `0755`.
   - Reads site definitions from `data_bag('nginx_sites')`.
   - The supplied analysis contains no site names, so no named site iterations can be expanded.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>`.
   - Passes `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` to the site template.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a link to `/etc/nginx/sites-available/<site_name>`.
   - Deletes `/etc/nginx/sites-enabled/default`.

## Dependencies

**External cookbook dependencies**: None exposed in the supplied metadata analysis. Verify `cookbooks/nginx-multisite/metadata.rb` before finalizing role dependencies.

**System package dependencies**:
- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: declared with action `nothing`; Ansible should restart or reload it only after SSH configuration changes
- `ssh`: may be the target service name on platforms where `sshd` is unavailable

**Ansible collection dependencies**:
- `community.general` for UFW management where available
- `community.crypto` for idempotent TLS key and certificate generation

## Credentials

**Detection Summary**: The analyzed files identify one site-token value and locally generated TLS private keys. No external secret-provider integration or credential-detection metadata was supplied.

**Source**:
  - **Provider**: No external provider detected
  - **URL**: Not applicable
  - **Path**: `site_secret['token']` is referenced by `cookbooks/nginx-multisite/recipes/nginx.rb`; TLS materials are generated locally by `cookbooks/nginx-multisite/recipes/ssl.rb`

### Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Provider and declaration are not present in the analyzed files
- **Destination**: `/etc/nginx/secrets/site_token`
- **File mode**: The execution-tree analysis does not confirm a mode; preserve the intended restricted mode of `0600` only after verifying the source resource
- **Usage context**: Site-related secret stored on the Nginx host
- **Source provider**: `site_secret` provider unknown; no external provider detected
- **Migration handling**: Store the value in Ansible Vault or retrieve it from the organization’s approved secret manager

### TLS Private Keys

- **Variable(s)**: `key_file`, derived from the SSL private-key path and `site_name`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL
- **Destination pattern**: `/etc/ssl/private/<site_name>.key`
- **Usage context**: TLS private key for an SSL-enabled Nginx site
- **Source provider**: Local OpenSSL generation
- **Permissions**: The recipe command sets mode `0640`, owner `root`, and group `ssl-cert`
- **Migration handling**: Protect keys with the same ownership and permissions and avoid unnecessary regeneration

### TLS Certificates

- **Variable(s)**: `cert_file`, derived from the SSL certificate path and `site_name`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally as self-signed certificates
- **Destination pattern**: `/etc/ssl/certs/<site_name>.crt`
- **Usage context**: HTTPS certificate for an SSL-enabled Nginx site
- **Source provider**: Local OpenSSL generation
- **Migration handling**: Preserve the 2048-bit RSA key, 365-day validity, and self-signed certificate behavior

## Checks for the Migration

**Files to verify**:
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
- `cookbooks/nginx-multisite/metadata.rb`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-enabled/default`
- `<document_root>/index.html`
- `/etc/nginx/sites-available/<site_name>`
- `/etc/nginx/sites-enabled/<site_name>`
- `/etc/ssl/certs/<site_name>.crt`
- `/etc/ssl/private/<site_name>.key`

**Service endpoints to check**:
- SSH service alias and the host-configured SSH port
- HTTP: TCP port 80
- HTTPS: TCP port 443 when SSL-enabled sites are configured

**Templates rendered**:
- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: one render per item in `nginx_sites`; exact count unavailable because item names were not supplied

## Pre-flight checks

```bash
# Package and service status
dpkg -l fail2ban ufw nginx openssl ca-certificates 2>/dev/null || \
rpm -q fail2ban ufw nginx openssl ca-certificates

systemctl status fail2ban
systemctl status nginx
fail2ban-client status

# Firewall policy and rules
ufw status verbose
ufw status numbered

# Verify deny-by-default and required access
# SSH service alias is allowed
# HTTP/TCP 80 is allowed
# HTTPS/TCP 443 is allowed
# UFW is active

# SSH configuration validation
grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config
sshd -t
systemctl status sshd || systemctl status ssh

# Expected SSH settings under the default attributes:
# PermitRootLogin no
# PasswordAuthentication no

# Sysctl configuration
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Nginx configuration
nginx -t
systemctl status nginx
cat /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/security.conf

# Secret directory and token
stat -c '%A %U:%G %n' /etc/nginx/secrets
stat -c '%A %U:%G %n' /etc/nginx/secrets/site_token

# Site collection validation
# Load the nginx_sites collection before executing named-site checks.
# For every supplied site definition, verify its configured document root,
# index.html, available-site configuration, and enabled-site link.
test -d <document_root>
test -f <document_root>/index.html
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>

# The default site must be absent
test ! -e /etc/nginx/sites-enabled/default

# SSL validation for each supplied SSL-enabled site
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key

openssl x509 \
  -in /etc/ssl/certs/<site_name>.crt \
  -noout \
  -subject \
  -issuer \
  -dates

stat -c '%A %U:%G %n' /etc/ssl/private/<site_name>.key

# Expected private-key ownership and mode:
# -rw-r----- root:ssl-cert /etc/ssl/private/<site_name>.key

# HTTP endpoint validation for each supplied site
curl -I -H 'Host: <site_name>' http://127.0.0.1/

# HTTPS endpoint validation for each supplied SSL-enabled site
curl -k -I --resolve <site_name>:443:127.0.0.1 \
  https://<site_name>/

# Listening sockets
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
grep -R -E 'access_log|error_log' \
  /etc/nginx/nginx.conf \
  /etc/nginx/conf.d \
  /etc/nginx/sites-available
```

Expected results:

- `fail2ban` is installed, enabled, and active.
- `nginx` is installed, enabled, and active.
- UFW is active with a default incoming policy of deny.
- SSH, HTTP, and HTTPS are allowed.
- `sshd -t` completes successfully.
- Nginx configuration validation reports `syntax is ok` and `test is successful`.
- Each supplied site has its configured document root, `index.html`, available-site configuration, and enabled-site link.
- `/etc/nginx/sites-enabled/default` does not exist.
- Each supplied SSL-enabled site has a self-signed 2048-bit RSA certificate valid for 365 days.
- Nginx listens on TCP port 80 and listens on TCP port 443 when SSL-enabled sites are configured.