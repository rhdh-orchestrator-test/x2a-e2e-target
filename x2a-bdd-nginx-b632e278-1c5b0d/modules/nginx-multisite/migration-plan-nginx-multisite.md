---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook deploys and secures an Nginx web server hosting three HTTPS-enabled sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; configures firewall rules, kernel security settings, and SSH hardening; creates self-signed TLS certificates; deploys one Nginx virtual-host configuration and `index.html` per site; enables Nginx and Fail2ban; and removes the default Nginx site. Values attributed to `nginx.sites`, `nginx.ssl`, and `security.ssh` should be verified against `cookbooks/nginx-multisite/attributes/default.rb`, because the supplied analysis confirms the attribute names but not all configured values.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Nginx HTTPS virtual host
  - Document root: `/opt/server/test`
  - Port: HTTP `80`, HTTPS `443`
  - SSL enabled: `true`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Nginx configuration: `/etc/nginx/sites-available/test.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: Nginx HTTPS virtual host
  - Document root: `/opt/server/ci`
  - Port: HTTP `80`, HTTPS `443`
  - SSL enabled: `true`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Nginx configuration: `/etc/nginx/sites-available/ci.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: Nginx HTTPS virtual host
  - Document root: `/opt/server/status`
  - Port: HTTP `80`, HTTPS `443`
  - SSL enabled: `true`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Nginx configuration: `/etc/nginx/sites-available/status.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/status.cluster.local`

- **fail2ban**: Host intrusion-prevention service
  - Package: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Service: enabled and started

- **ufw**: Host firewall
  - Package: `ufw`
  - Default inbound policy: deny
  - Allowed services: SSH, HTTP, and HTTPS
  - Firewall: enabled

- **ssh**: SSH service hardening
  - Root login: disabled because `security.ssh.disable_root` is `true`
  - Password authentication: disabled because `security.ssh.password_auth` is `false`
  - Service action: `nothing`; no restart or reload is shown in the execution tree

## File Structure

Only files shown as executed or referenced by the supplied execution tree and structured analysis are listed.

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

The execution tree references dynamic `cookbook_file` resources for the site `index.html` files, but no corresponding static file paths are listed in the supplied directory listing or structured analysis. Verify the cookbook contents before implementing the Ansible `copy` tasks; source paths must not be invented.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order: security, Nginx installation, TLS generation, and virtual-host configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default inbound policy to deny.
   - Allows SSH, HTTP, and HTTPS through UFW.
   - Enables UFW after the SSH rule is present.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as an action-`nothing` resource. The execution tree shows no notification or subscription invoking it.
   - When `security.ssh.disable_root` is `true`, sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - When `security.ssh.password_auth == false`, sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Declares the `ssh` service with action `nothing`; no restart or reload is shown.
   - Resources: 1 package, 2 services, 2 templates, and 7 execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` and deploys `/opt/server/test/index.html` for `test.cluster.local`.
   - Creates `/opt/server/ci` and deploys `/opt/server/ci/index.html` for `ci.cluster.local`.
   - Creates `/opt/server/status` and deploys `/opt/server/status/index.html` for `status.cluster.local`.
   - The three dynamic `cookbook_file` resources use mode `0644`; verify their static source layout before migration.
   - No Nginx reload or restart notification is shown for configuration or content changes.
   - Resources: 1 package, 2 templates, 1 service, 3 directories, and 3 cookbook files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private`.
   - Generates a self-signed RSA 2048-bit certificate for `test.cluster.local`, valid for 365 days, using subject email `admin@example.com`.
   - Generates a self-signed RSA 2048-bit certificate for `ci.cluster.local`, valid for 365 days, using subject email `admin@example.com`.
   - Generates a self-signed RSA 2048-bit certificate for `status.cluster.local`, valid for 365 days, using subject email `admin@example.com`.
   - Stores certificates under `/etc/ssl/certs`.
   - Stores private keys under `/etc/ssl/private` with mode `640`, owner `root`, and group `ssl-cert`.
   - Preserve the three explicit certificate-generation operations while making the Ansible implementation idempotent by avoiding regeneration when the existing key and certificate are valid, unless regeneration is intentionally required.
   - Resources: 1 package, 1 group, 2 directories, and 3 execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local` with:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` as a link to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local` with:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` as a link to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local` with:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` as a link to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Renders `site.conf.erb` three times: once for each named site.
   - Resources: 3 templates, 3 links, and 1 file deletion.

## Dependencies

**External cookbook dependencies**: None were identified in the supplied structured analysis. Verify `metadata.rb` separately because its contents were not provided.

**System package dependencies**:
- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no restart or reload is shown

**Network access configured**:
- SSH through the UFW SSH service rule
- HTTP through the UFW HTTP service rule
- HTTPS through the UFW HTTPS service rule

## Credentials

**Detection Summary**: 3 sensitive generated TLS private keys detected across 1 recipe file. No passwords, API tokens, data bags, encrypted data bags, Chef Vault items, CyberArk references, Conjur variables, or external secret-manager references were detected. The certificate subject email is hardcoded but is not an authentication secret.

**Source**:
  - **Provider**: None detected; private keys are generated locally by OpenSSL, and the certificate email is hardcoded in the recipe.
  - **URL**: Not applicable
  - **Path**: `cookbooks/nginx-multisite/recipes/ssl.rb`

### Generated TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files; not stored in a credential provider.
- **Usage context**: Private keys for the three self-signed Nginx HTTPS virtual hosts.
- **Permissions and ownership**: Mode `640`, owner `root`, group `ssl-cert`.

### Certificate Subject Email

- **Variable**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL subject string.
- **Usage context**: Subject email address for all three generated self-signed certificates.
- **Credential classification**: Not a password, token, or authentication secret.
- **Source provider**: Recipe source; no external provider.

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
- `/etc/nginx/sites-enabled/default` must be absent
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`

**Service endpoints to check**:
- `test.cluster.local`: HTTP port `80`, HTTPS port `443`
- `ci.cluster.local`: HTTP port `80`, HTTPS port `443`
- `status.cluster.local`: HTTP port `80`, HTTPS port `443`
- SSH: existing SSH port, normally `22`
- Unix sockets: none identified

**Templates rendered**:
- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

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
systemctl is-enabled nginx
systemctl is-active nginx
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Nginx configuration validation
nginx -t

# Main Nginx configuration
ls -l /etc/nginx/nginx.conf
ls -l /etc/nginx/conf.d/security.conf

# test.cluster.local
ls -l /etc/nginx/sites-available/test.cluster.local
ls -l /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /opt/server/test/index.html
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G' /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject | grep 'CN = test.cluster.local'
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# ci.cluster.local
ls -l /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /opt/server/ci/index.html
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G' /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject | grep 'CN = ci.cluster.local'
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# status.cluster.local
ls -l /etc/nginx/sites-available/status.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /opt/server/status/index.html
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G' /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject | grep 'CN = status.cluster.local'
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Fail2ban
test -f /etc/fail2ban/jail.local
fail2ban-client -t

# UFW
ufw status verbose
ufw status | grep -E '22|ssh'
ufw status | grep -E '80|http'
ufw status | grep -E '443|https'

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# Sysctl security settings
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Listening ports and processes
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
ps aux | grep '[n]ginx'

# Logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```