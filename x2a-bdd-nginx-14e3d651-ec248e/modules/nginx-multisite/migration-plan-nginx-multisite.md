---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures Nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It creates the three document roots and index files, generates self-signed certificates, renders Nginx configurations, enables Fail2ban and UFW, applies security sysctl settings, disables SSH root login and password authentication, and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Nginx HTTPS virtual host serving static content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Site configuration: `/etc/nginx/sites-available/test.cluster.local`
  - Enabled-site link: `/etc/nginx/sites-enabled/test.cluster.local`
  - SSL: Enabled

- **ci.cluster.local**: Nginx HTTPS virtual host serving static content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Site configuration: `/etc/nginx/sites-available/ci.cluster.local`
  - Enabled-site link: `/etc/nginx/sites-enabled/ci.cluster.local`
  - SSL: Enabled

- **status.cluster.local**: Nginx HTTPS virtual host serving static content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Site configuration: `/etc/nginx/sites-available/status.cluster.local`
  - Enabled-site link: `/etc/nginx/sites-enabled/status.cluster.local`
  - SSL: Enabled

Security configuration namespaces:

- `fail2ban`
- `ufw`
- `ssh`

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

No static file path under `files/default/` or `files/` is listed. The Chef `cookbook_file` resources reference site-specific `index.html` files, but their source paths are not present in the supplied file listing and must be located separately.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible implementation must preserve this order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Executes `ufw --force default deny`.
   - Executes `ufw allow ssh`.
   - Executes `ufw allow http`.
   - Executes `ufw allow https`.
   - Executes `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Defines `reload_sysctl` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; the supplied execution tree shows no notification that activates it.
   - Because `security.ssh.disable_root` is `true`, sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Because `security.ssh.password_auth` is `false`, sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Defines the `ssh` service with action `nothing`; no automatic SSH restart or reload is shown.
   - Execute resources: 8 total—five UFW commands, one inactive sysctl reload command, and two conditional SSH commands.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates the document root for `test.cluster.local` at `/opt/server/test`.
   - Creates `/opt/server/test/index.html` with a Chef `cookbook_file`.
   - Creates the document root for `ci.cluster.local` at `/opt/server/ci`.
   - Creates `/opt/server/ci/index.html` with a Chef `cookbook_file`.
   - Creates the document root for `status.cluster.local` at `/opt/server/status`.
   - Creates `/opt/server/status/index.html` with a Chef `cookbook_file`.
   - The source paths for the three `index.html` files are not present in the supplied file listing and must be confirmed before migration.
   - Directory and file modes stated in the original plan require confirmation from the underlying Chef resources before being treated as authoritative.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private`.
   - Directory ownership and modes require confirmation from the underlying Chef resources; they are not exposed by the supplied structured execution summary.
   - For `test.cluster.local`, generates:
     - `/etc/ssl/private/test.cluster.local.key`
     - `/etc/ssl/certs/test.cluster.local.crt`
   - For `ci.cluster.local`, generates:
     - `/etc/ssl/private/ci.cluster.local.key`
     - `/etc/ssl/certs/ci.cluster.local.crt`
   - For `status.cluster.local`, generates:
     - `/etc/ssl/private/status.cluster.local.key`
     - `/etc/ssl/certs/status.cluster.local.crt`
   - All three certificate-generation iterations use SSL because `ssl_enabled` is `true` for all three sites.
   - Certificate generation uses self-signed X.509 certificates, RSA 2048 keys, no passphrase, and 365-day validity.
   - The intended subject common names are `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, respectively, with subject email `admin@example.com`; these subject details require confirmation from the underlying recipe before migration.
   - Sets each private key to mode `0640` and ownership `root:ssl-cert`.

   Iterations:
   - `test.cluster.local`
   - `ci.cluster.local`
   - `status.cluster.local`

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Links `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Links `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Links `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - The site template variables, certificate paths, and link targets should be confirmed against the underlying recipe and template files before final migration.

   Iterations:
   - `test.cluster.local`: document root `/opt/server/test`; certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`
   - `ci.cluster.local`: document root `/opt/server/ci`; certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`
   - `status.cluster.local`: document root `/opt/server/status`; certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`

## Dependencies

**External cookbook dependencies**: None specified.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: referenced with action `nothing`; no restart is shown

**Security and network dependencies**:

- UFW default incoming policy is deny.
- SSH is allowed through UFW.
- HTTP is allowed through UFW.
- HTTPS is allowed through UFW.
- SSH root login is disabled.
- SSH password authentication is disabled.

## Credentials

**Detection Summary**: No application credentials, data bags, vault references, API tokens, database passwords, or environment-variable secrets were detected. Three locally generated TLS private keys and three locally generated self-signed certificates are present.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL; not sourced from a vault or data bag.
- **Usage context**: TLS private keys for the three Nginx HTTPS virtual hosts.
- **Protection**: Explicitly set to owner `root`, group `ssl-cert`, mode `0640`.

### Self-Signed TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL; not sourced from a vault or data bag.
- **Usage context**: Public certificate files referenced by the Nginx site configurations.
- **Properties**:
  - Self-signed
  - RSA 2048
  - Valid for 365 days
  - Intended common name equal to the site hostname
  - Intended subject email `admin@example.com`; confirm against the underlying recipe

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, database connection string, or hardcoded password is shown.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/etc/nginx/sites-enabled/default
/opt/server/test
/opt/server/test/index.html
/opt/server/ci
/opt/server/ci/index.html
/opt/server/status
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
```

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH: UFW allows the SSH service; no custom SSH port is specified
- Unix sockets: None specified

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Nginx configuration
nginx -t
grep -E '^[[:space:]]*(include|user|worker_processes|events|http)' /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/security.conf

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

# Default-site removal
test ! -e /etc/nginx/sites-enabled/default

# TLS certificate inspection
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates

# TLS private-key permissions
stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Firewall
ufw status verbose
ufw status numbered

# SSH hardening
grep -E '^[[:space:]]*(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config

# Fail2ban
test -f /etc/fail2ban/jail.local
fail2ban-client status
journalctl -u fail2ban --no-pager -n 50

# Sysctl
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf

# Network listeners
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Nginx logs
journalctl -u nginx --no-pager -n 100
```

Expected results:

- `nginx` and `fail2ban` are active and enabled.
- `nginx -t` reports valid syntax and a successful configuration test.
- Each named site has its document root, index file, site configuration, enabled-site link, certificate, and private key.
- HTTP and HTTPS return valid responses for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
- `/etc/nginx/sites-enabled/default` is absent.
- Each certificate is self-signed and has a matching hostname subject, subject to confirmation against the underlying recipe.
- Each private key is owned by `root:ssl-cert` with mode `640`.
- UFW is active with default incoming policy deny and allows SSH, HTTP, and HTTPS.
- SSH configuration contains `PermitRootLogin no` and `PasswordAuthentication no`.
- Nginx listens on TCP ports `80` and `443`.
- No Nginx, certificate, permission, or Fail2ban startup errors are present.