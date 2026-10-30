---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures Nginx, Fail2ban, UFW, OpenSSL, and certificate authorities for three named sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It applies security configuration, creates site document roots and content, generates locally signed TLS certificates, renders Nginx virtual-host configurations, enables the sites, and removes the default site. Document roots, certificate paths, directory properties, SSH conditional outcomes, and listener ports require confirmation from the cookbook attributes and template contents where noted.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The `node['nginx']['sites']` collection contains the following three configured sites. The paths and SSL values below are attribute-derived and should be confirmed in `attributes/default.rb`.

- **test.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/test` — confirm from `attributes/default.rb`
  - Port/Socket: Expected HTTP `80` and HTTPS `443`; confirm in `templates/default/site.conf.erb`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`

- **ci.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/ci` — confirm from `attributes/default.rb`
  - Port/Socket: Expected HTTP `80` and HTTPS `443`; confirm in `templates/default/site.conf.erb`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`

- **status.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/status` — confirm from `attributes/default.rb`
  - Port/Socket: Expected HTTP `80` and HTTPS `443`; confirm in `templates/default/site.conf.erb`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`

**Security areas**:

- **fail2ban**: Installs `fail2ban`, renders `/etc/fail2ban/jail.local`, and enables and starts the service.
- **ufw**: Installs `ufw`, sets the default policy to deny, allows SSH/HTTP/HTTPS, and force-enables the firewall.
- **ssh**: Conditionally modifies `/etc/ssh/sshd_config` based on `node['security']['ssh']['disable_root']` and `node['security']['ssh']['password_auth']`. The SSH service is declared with action `nothing`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
attributes/default.rb
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

No static files are listed as deployed by a `cookbook_file` resource. The recipes deploy `index.html` files through dynamic `cookbook_file` resources, but their source files are not included in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - Preserves the execution order: security configuration, Nginx installation and web roots, certificate generation, and site configuration.
   - Resources: four `include_recipe` declarations.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the grouped package resource containing `fail2ban` and `ufw`; this is one package resource declaration containing two packages.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Executes UFW commands in this order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Declares `execute[reload_sysctl]` for `sysctl -p /etc/sysctl.d/99-security.conf` with action `nothing`.
   - Conditionally executes the root-login hardening command when `node['security']['ssh']['disable_root']` is true:
     ```bash
     sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
     ```
   - Conditionally executes the password-authentication hardening command when `node['security']['ssh']['password_auth'] == false`:
     ```bash
     sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
     ```
   - Declares the `ssh` service with action `nothing`; no SSH restart or reload is shown.
   - Resource summary: one package resource containing two packages, two services, two templates, and eight execute resources; 13 total resource declarations.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates the document root and deploys `index.html` for `test.cluster.local`:
     - Directory: `/opt/server/test`, mode `0755` — confirm mode and path from attributes.
     - File: `/opt/server/test/index.html`, mode `0644`.
     - Source: dynamically built as `#{site_folder}/index.html`.
   - Creates the document root and deploys `index.html` for `ci.cluster.local`:
     - Directory: `/opt/server/ci`, mode `0755` — confirm mode and path from attributes.
     - File: `/opt/server/ci/index.html`, mode `0644`.
     - Source: dynamically built as `#{site_folder}/index.html`.
   - Creates the document root and deploys `index.html` for `status.cluster.local`:
     - Directory: `/opt/server/status`, mode `0755` — confirm mode and path from attributes.
     - File: `/opt/server/status/index.html`, mode `0644`.
     - Source: dynamically built as `#{site_folder}/index.html`.
   - Resource summary: one package resource, two templates, one service, three directories, and three `cookbook_file` resources; 10 total resource declarations.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the grouped package resource containing `openssl` and `ca-certificates`; this is one package resource declaration containing two packages.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Directory ownership and group properties require confirmation from the resource property and attributes analysis.
   - Generates a self-signed certificate and private key for `test.cluster.local`:
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Command properties: RSA 2048-bit key, 365-day validity, CN `test.cluster.local`, and email `admin@example.com`.
     - Sets private-key mode to `0640` and ownership to `root:ssl-cert`.
   - Generates a self-signed certificate and private key for `ci.cluster.local`:
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Command properties: RSA 2048-bit key, 365-day validity, CN `ci.cluster.local`, and email `admin@example.com`.
     - Sets private-key mode to `0640` and ownership to `root:ssl-cert`.
   - Generates a self-signed certificate and private key for `status.cluster.local`:
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Command properties: RSA 2048-bit key, 365-day validity, CN `status.cluster.local`, and email `admin@example.com`.
     - Sets private-key mode to `0640` and ownership to `root:ssl-cert`.
   - Resource summary: one package resource containing two packages, one group, two directories, and three certificate-generation execute resources; seven total resource declarations.
   - The migration must make certificate generation idempotent and must not regenerate existing certificates on every run.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local`:
     - Destination: `/etc/nginx/sites-available/test.cluster.local`
     - Variables: `server_name=test.cluster.local`, `document_root=/opt/server/test`, `ssl_enabled=true`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
     - Mode: `0644`
   - Creates the enabled-site link `/etc/nginx/sites-enabled/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local`:
     - Destination: `/etc/nginx/sites-available/ci.cluster.local`
     - Variables: `server_name=ci.cluster.local`, `document_root=/opt/server/ci`, `ssl_enabled=true`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
     - Mode: `0644`
   - Creates the enabled-site link `/etc/nginx/sites-enabled/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local`:
     - Destination: `/etc/nginx/sites-available/status.cluster.local`
     - Variables: `server_name=status.cluster.local`, `document_root=/opt/server/status`, `ssl_enabled=true`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
     - Mode: `0644`
   - Creates the enabled-site link `/etc/nginx/sites-enabled/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Resource summary: three templates, three links, and one file resource; seven total resource declarations.
   - The supplied execution tree does not show an explicit Nginx reload or restart. The migration should notify an Nginx reload when site templates or links change.

## Dependencies

**External cookbook dependencies**: None specified.

**System package dependencies**:
- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no restart or reload is shown

**Security configuration dependencies**:
- UFW must deny incoming traffic by default.
- UFW must allow SSH, HTTP, and HTTPS.
- The system must support `/etc/sysctl.d/99-security.conf`.
- SSH configuration is stored in `/etc/ssh/sshd_config`.

## Credentials

**Detection Summary**: No external credentials, passwords, API tokens, data bags, Chef Vault items, CyberArk variables, or environment-based secrets were detected. Three locally generated TLS private keys and three self-signed certificates are created.

**Source**:
  - **Provider**: None detected; certificates are generated locally with OpenSSL
  - **URL**: None
  - **Path**: `/etc/ssl/certs` and `/etc/ssl/private`

### Generated TLS Private Keys

- **Variable(s)**: Dynamic `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files, not a data bag, vault, environment variable, or external secret store
- **Usage context**: TLS private keys for the three Nginx HTTPS virtual hosts
- **Permissions and ownership**: Mode `0640`, owner `root`, group `ssl-cert`

### Self-Signed TLS Certificates

- **Variable(s)**: Dynamic `cert_file`; `/etc/ssl/certs/test.cluster.local.crt`; `/etc/ssl/certs/ci.cluster.local.crt`; `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files
- **Usage context**: Public certificates referenced by the three Nginx HTTPS site configurations
- **Certificate subject values**: Country `US`, State `Example`, Locality `Example`, Organization `Example Org`, Organizational Unit `IT`, corresponding site name as Common Name, and email `admin@example.com`

No hardcoded passwords, database credentials, API keys, Chef Vault references, encrypted data bags, or secret-manager integrations were detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/nginx-multisite/attributes/default.rb`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
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

**Service endpoints to check**:
- Expected HTTP port: `80`; confirm in `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- Expected HTTPS port: `443`; confirm in `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- SSH service and firewall allowance
- `nginx` service
- `fail2ban` service
- No Unix sockets are specified in the execution tree

**Templates rendered**:
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` — 1 time
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` — 1 time
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` — 1 time
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` — 1 time
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` — 3 times:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks:

```bash
# Package verification
dpkg -l nginx
dpkg -l fail2ban
dpkg -l ufw
dpkg -l openssl
dpkg -l ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Nginx configuration syntax
nginx -t

# Global configuration files
ls -l /etc/nginx/nginx.conf
ls -l /etc/nginx/conf.d/security.conf
cat /etc/nginx/conf.d/security.conf

# Test site: test.cluster.local
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
ls -l /etc/nginx/sites-available/test.cluster.local
ls -l /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
ls -l /etc/ssl/certs/test.cluster.local.crt
ls -l /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# CI site: ci.cluster.local
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
ls -l /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
ls -l /etc/ssl/certs/ci.cluster.local.crt
ls -l /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# Status site: status.cluster.local
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
ls -l /etc/nginx/sites-available/status.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
ls -l /etc/ssl/certs/status.cluster.local.crt
ls -l /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Firewall checks
ufw status verbose
ufw status numbered
ufw status verbose | grep -E 'Default: deny|22|80|443'

# SSH hardening checks
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t

# Sysctl checks
ls -l /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Network listening checks
ss -tlnp | grep -E ':80|:443'
lsof -i :80
lsof -i :443

# Service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -k --no-pager -n 100
```

Migration is complete when the three named sites have their confirmed document roots, rendered configurations, enabled-site links, certificates, and private keys; Nginx passes `nginx -t`; the configured HTTP and HTTPS ports are listening; UFW has the required rules; and any enabled SSH hardening conditions are active.