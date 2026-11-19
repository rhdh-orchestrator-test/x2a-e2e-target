---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook deploys and hardens an Nginx multisite web server. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; configures firewall and SSH security; creates shared SSL certificate directories; generates self-signed certificates for SSL-enabled sites; renders Nginx virtual-host configurations and enabled-site symlinks; and deploys site index files. The `nginx_sites` data bag item names and values were not supplied, so the exact site instances, document roots, SSL settings, and site folders must be recovered before migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

No exact `nginx_sites` item names were provided in the source analysis. The migration must explicitly define one site instance for every item in the `nginx_sites` data bag.

Each site instance requires:

- **Site name**: Data bag item name; used for the server name, certificate filenames, configuration filenames, and enabled-site symlink
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: HTTP TCP 80; HTTPS TCP 443 when SSL is enabled
  - Key Config: `document_root`, `ssl_enabled`, and `site_folder`

**Security services**:

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: None
  - Key Config: Enabled and started

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP 22, TCP 80, and TCP 443
  - Key Config: Default incoming policy deny; firewall enabled

- **sshd**: SSH daemon hardening
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP 22
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`
  - Service behavior: The Chef resource is declared with action `nothing`; no restart or reload is shown

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

No static files were explicitly listed. The `cookbook_file` resource references dynamic source paths of the form `<site_folder>/index.html`, but the source files were not included in the supplied directory analysis.

## Module Explanation

The cookbook performs operations in this order:

1. **Default entry recipe** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - Preserves the logical order: security, Nginx installation, SSL preparation, and site configuration.

2. **Security configuration** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Executes eight resources:
     - `ufw_default_deny`: `ufw --force default deny`
     - `ufw_allow_ssh`: `ufw allow ssh`
     - `ufw_allow_http`: `ufw allow http`
     - `ufw_allow_https`: `ufw allow https`
     - `ufw_enable`: `ufw --force enable`
     - `reload_sysctl`: declared as `execute[reload_sysctl]` with action `nothing`
     - `disable root login`: sets `PermitRootLogin no`
     - `disable password auth`: sets `PasswordAuthentication no`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Does not explicitly reload or restart SSH in the supplied execution tree.
   - Does not show a notification or explicit invocation of `reload_sysctl`; the migration must distinguish deployment of the sysctl file from application of its values.

3. **Nginx installation and base configuration** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner/group `root:root` and mode `0700`.
   - Creates `/etc/nginx/secrets/site_token` from the unconfirmed `site_secret['token']` expression with owner/group `root:root` and mode `0600`.
   - Iterates over the `nginx_sites` data bag:
     - Creates each configured `document_root` with mode `0755` and group `nginx`.
     - Deploys `<document_root>/index.html` from the dynamic cookbook source `<site_folder>/index.html` with mode `0644` and group `nginx`.
   - The exact data bag item names, document roots, and site folders were not supplied, so these loop iterations cannot be expanded by name.

4. **SSL preparation and certificate generation** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner/group `root:root` and mode `0755`.
   - Creates `/etc/ssl/private` with owner/group `root:ssl-cert` and mode `0710`.
   - Iterates over the `nginx_sites` data bag and generates a certificate only when `ssl_enabled` is true.
   - Each SSL-enabled site receives:
     - Private key: `/etc/ssl/private/<site_name>.key`
     - Certificate: `/etc/ssl/certs/<site_name>.crt`
   - Uses a self-signed RSA 2048-bit certificate valid for 365 days with Common Name `<site_name>` and email address `admin@example.com`.
   - Sets each private key to mode `0640` and owner/group `root:ssl-cert`.
   - The exact SSL-enabled site names were not supplied, so no named certificate-generation iterations can be listed.

5. **Nginx site configuration** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with mode `0755`.
   - Iterates over the `nginx_sites` data bag.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once per data bag item to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Passes the following template values:
     - `server_name`: `<site_name>`
     - `document_root`: `config['document_root']`
     - `ssl_enabled`: `config['ssl_enabled']`
     - `cert_file`: `/etc/ssl/certs/<site_name>.crt`
     - `key_file`: `/etc/ssl/private/<site_name>.key`
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to `/etc/nginx/sites-available/<site_name>` for every data bag item.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - The exact site names and loop count were not supplied.

## Dependencies

**External cookbook dependencies**: None were supplied. Confirm `metadata.rb` before finalizing role dependencies.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: hardening settings changed; no service reload or restart shown

**Data dependencies**:

- `nginx_sites` data bag
- `site_secret['token']` source requires verification against the actual Chef recipe and metadata

**Configured defaults** from `cookbooks/nginx-multisite/attributes/default.rb`:

```yaml
nginx_ssl_certificate_path: /etc/ssl/certs
nginx_ssl_private_key_path: /etc/ssl/private

security_fail2ban_enabled: true
security_ufw_enabled: true
security_ssh_disable_root: true
security_ssh_password_auth: false
```

## Credentials

**Detection Summary**: 1 explicit secret expression detected, plus generated TLS private keys. The origin of the explicit token was not confirmed by the structured execution summary.

**Source**:
  - **Provider**: Unknown; verify whether the Chef source is a data bag, Chef Vault, encrypted attributes, or another secret provider
  - **URL**: None identified
  - **Path**: The confirmed destination is `/etc/nginx/secrets/site_token`; the originating provider and source path require verification

### Nginx Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb` according to the supplied plan; the expression must be confirmed against the actual recipe
- **Current storage**: Unknown Chef secret mechanism
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **File permissions**: `0600`
- **Owner/group**: `root:root`
- **Migration handling**: Store in Ansible Vault or an external secret manager and deploy without exposing the value in repository content

### Generated SSL Private Keys

- **Variable(s)**: `key_file`, derived from `<site_name>`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by `openssl req`
- **Usage context**: TLS private keys for SSL-enabled Nginx sites
- **Path pattern**: `/etc/ssl/private/<site_name>.key`
- **Permissions**: `0640`
- **Owner/group**: `root:ssl-cert`
- **Certificate pairing**: `/etc/ssl/certs/<site_name>.crt`

The `nginx_sites` data bag may contain additional sensitive values. Inspect all recovered items for passwords, tokens, certificates, or other secrets before migration.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-enabled/default` must be absent
- `/etc/ssl/certs`
- `/etc/ssl/private`
- One `/etc/nginx/sites-available/<site_name>` per recovered `nginx_sites` item
- One `/etc/nginx/sites-enabled/<site_name>` symlink per recovered `nginx_sites` item
- One `<document_root>/index.html` per recovered `nginx_sites` item
- One `/etc/ssl/certs/<site_name>.crt` per SSL-enabled recovered site
- One `/etc/ssl/private/<site_name>.key` per SSL-enabled recovered site

**Service endpoints to check**:

- SSH: TCP 22
- HTTP: TCP 80
- HTTPS: TCP 443
- UFW status and rules
- Fail2ban service status
- Nginx service status

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: once per recovered `nginx_sites` item

The exact site count and names cannot be determined until the `nginx_sites` data bag is recovered.

## Pre-flight checks:

```bash
# Security services
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status

# Firewall
ufw status verbose
ufw status numbered

# SSH configuration
grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config
sshd -t

# Sysctl configuration
test -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf
# Run only if the migration is intended to apply the values:
sysctl --system

# Nginx service and configuration
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
nginx -T

# Nginx directories and default-site removal
test -d /etc/nginx/sites-available
test -d /etc/nginx/sites-enabled
test ! -e /etc/nginx/sites-enabled/default

# HTTP and HTTPS listeners
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Basic endpoint checks
curl -I http://127.0.0.1/
curl -k -I https://127.0.0.1/

# Secret file metadata; do not print its contents
stat -c '%A %U:%G %n' /etc/nginx/secrets/site_token
test "$(stat -c '%a' /etc/nginx/secrets/site_token)" = "600"

# Service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
tail -n 100 /var/log/nginx/access.log
tail -n 100 /var/log/nginx/error.log

# Network and firewall verification
ss -tlnp | grep -E ':(22|80|443) '
ufw status verbose
```

No exact site instances were supplied, so per-site pre-flight commands cannot be enumerated by name. After recovering the `nginx_sites` data bag, add an individual validation block for every item covering its exact configuration file, symlink, document root, index file, and—when `ssl_enabled` is true—certificate and private key:

```bash
# Replace placeholders only after recovering the exact data bag item values.
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>

test -d <document_root>
test -f <document_root>/index.html
stat -c '%A %U:%G %n' <document_root>
stat -c '%A %U:%G %n' <document_root>/index.html

# Run for SSL-enabled sites only.
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -text | grep 'Public-Key'
stat -c '%A %U:%G %n' /etc/ssl/private/<site_name>.key
```

Expected site properties:

- Document root mode `0755`, group `nginx`
- `index.html` mode `0644`, group `nginx`
- SSL certificate self-signed, RSA 2048-bit, and valid for approximately 365 days
- Certificate Common Name matching the site name
- Private key mode `0640`, owner/group `root:ssl-cert`