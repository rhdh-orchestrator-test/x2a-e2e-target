---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx as a web server for three HTTPS-enabled sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, SSH, kernel, and Fail2ban hardening; creates site document roots and index files; generates 365-day self-signed RSA 2048-bit certificates; renders and enables one Nginx virtual host per site; and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: Document root `/opt/server/test`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; index file `/opt/server/test/index.html`

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: Document root `/opt/server/ci`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; index file `/opt/server/ci/index.html`

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: Document root `/opt/server/status`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; index file `/opt/server/status/index.html`

Security configuration includes enabled Fail2ban and UFW, disabled SSH root login, and disabled SSH password authentication.

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

No static `cookbook_file` source files are listed in the supplied directory analysis. The recipes reference dynamic `cookbook_file` sources under site-specific `site_folder` expressions; those source paths must be resolved from the original cookbook before implementation.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order: security, Nginx installation, SSL generation, and site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures UFW with default deny, then allows SSH, HTTP, and HTTPS, and enables the firewall:
     - `ufw --force default deny`
     - `ufw allow ssh`
     - `ufw allow http`
     - `ufw allow https`
     - `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Declares `sysctl -p /etc/sysctl.d/99-security.conf` with `action: nothing`; no execution notification is shown.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` because `node['security']['ssh']['disable_root']` is `true`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` because `node['security']['ssh']['password_auth']` is `false`.
   - Declares the SSH service with `action: nothing`; no restart notification is shown.
   - The Ansible implementation should use idempotent UFW and `lineinfile` operations and explicitly decide whether sysctl and SSH handlers are required.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Iterates over exactly these sites:
     - **test.cluster.local**:
       - Creates `/opt/server/test` with mode `0755`.
       - Deploys the site index source `#{site_folder}/index.html` to `/opt/server/test/index.html` with mode `0644`.
     - **ci.cluster.local**:
       - Creates `/opt/server/ci` with mode `0755`.
       - Deploys the site index source `#{site_folder}/index.html` to `/opt/server/ci/index.html` with mode `0644`.
     - **status.cluster.local**:
       - Creates `/opt/server/status` with mode `0755`.
       - Deploys the site index source `#{site_folder}/index.html` to `/opt/server/status/index.html` with mode `0644`.
   - The loop produces three directory resources and three `cookbook_file` resources.
   - No verified `www-data` group resource is included in the execution tree.
   - No Nginx reload or restart notification is shown.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Directory ownership and group relationships are not confirmed by the supplied execution tree and require verification against the original recipe.
   - Iterates over exactly these sites; all have `ssl_enabled: true`:
     - **test.cluster.local**:
       - Generates `/etc/ssl/private/test.cluster.local.key`.
       - Generates `/etc/ssl/certs/test.cluster.local.crt`.
       - Uses a self-signed certificate with RSA 2048-bit key, 365-day validity, and subject CN `test.cluster.local`.
       - Applies mode `0640` and ownership `root:ssl-cert` to the private key.
     - **ci.cluster.local**:
       - Generates `/etc/ssl/private/ci.cluster.local.key`.
       - Generates `/etc/ssl/certs/ci.cluster.local.crt`.
       - Uses a self-signed certificate with RSA 2048-bit key, 365-day validity, and subject CN `ci.cluster.local`.
       - Applies mode `0640` and ownership `root:ssl-cert` to the private key.
     - **status.cluster.local**:
       - Generates `/etc/ssl/private/status.cluster.local.key`.
       - Generates `/etc/ssl/certs/status.cluster.local.crt`.
       - Uses a self-signed certificate with RSA 2048-bit key, 365-day validity, and subject CN `status.cluster.local`.
       - Applies mode `0640` and ownership `root:ssl-cert` to the private key.
   - All certificates use subject email `admin@example.com`.
   - Certificate generation must be idempotent using `creates`, certificate modules, or an equivalent guard.
   - No service restart or Nginx reload is shown after certificate generation.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterates over exactly these sites:
     - **test.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
       - Passes `server_name: test.cluster.local`, `document_root: /opt/server/test`, `ssl_enabled: true`, `cert_file: /etc/ssl/certs/test.cluster.local.crt`, and `key_file: /etc/ssl/private/test.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/test.cluster.local` as a link to the corresponding file in `sites-available`.
     - **ci.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
       - Passes `server_name: ci.cluster.local`, `document_root: /opt/server/ci`, `ssl_enabled: true`, `cert_file: /etc/ssl/certs/ci.cluster.local.crt`, and `key_file: /etc/ssl/private/ci.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/ci.cluster.local` as a link to the corresponding file in `sites-available`.
     - **status.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
       - Passes `server_name: status.cluster.local`, `document_root: /opt/server/status`, `ssl_enabled: true`, `cert_file: /etc/ssl/certs/status.cluster.local.crt`, and `key_file: /etc/ssl/private/status.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/status.cluster.local` as a link to the corresponding file in `sites-available`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - No Nginx reload or restart notification is shown after site configuration changes.

## Dependencies

**External cookbook dependencies**: None shown in the supplied execution tree or metadata summary.

**System package dependencies**: `fail2ban`, `ufw`, `nginx`, `openssl`, `ca-certificates`

**Service dependencies**: 
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with `action: nothing`; no restart is shown

**Firewall allowances**: SSH port `22`, HTTP port `80`, and HTTPS port `443`

## Credentials

**Detection Summary**: 0 external credentials detected across the supplied cookbook files. Three generated TLS private keys and three generated certificates are created locally.

**Source**:
  - **Provider**: Internal OpenSSL generation
  - **URL**: None
  - **Path**: `/etc/ssl/private/test.cluster.local.key`, `/etc/ssl/private/ci.cluster.local.key`, `/etc/ssl/private/status.cluster.local.key`

### Generated TLS Private Keys

- **Variable(s)**: `key_file`, derived from `node['nginx']['ssl']['private_key_path']` and each site name
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; referenced by `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL; not stored in Chef Vault, a data bag, or an external secret manager
- **Usage context**: TLS private keys for the HTTPS virtual hosts
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`

### Self-Signed TLS Certificates

- **Variable(s)**: `cert_file`, derived from `node['nginx']['ssl']['certificate_path']` and each site name
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; referenced by `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: TLS certificates for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Validity**: 365 days
- **Certificate subject email**: `admin@example.com`

No data bag, Chef Vault, Conjur, CyberArk, or external secret-manager integration is shown.

## Checks for the Migration

**Files to verify**: `/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/security.conf`, `/etc/nginx/sites-available/test.cluster.local`, `/etc/nginx/sites-available/ci.cluster.local`, `/etc/nginx/sites-available/status.cluster.local`, `/etc/nginx/sites-enabled/test.cluster.local`, `/etc/nginx/sites-enabled/ci.cluster.local`, `/etc/nginx/sites-enabled/status.cluster.local`, `/opt/server/test/index.html`, `/opt/server/ci/index.html`, `/opt/server/status/index.html`, `/etc/ssl/certs/test.cluster.local.crt`, `/etc/ssl/certs/ci.cluster.local.crt`, `/etc/ssl/certs/status.cluster.local.crt`, `/etc/ssl/private/test.cluster.local.key`, `/etc/ssl/private/ci.cluster.local.key`, `/etc/ssl/private/status.cluster.local.key`, `/etc/fail2ban/jail.local`, `/etc/sysctl.d/99-security.conf`, `/etc/ssh/sshd_config`; `/etc/nginx/sites-enabled/default` must be absent.

**Service endpoints to check**: SSH `22`, HTTP `80`, HTTPS `443`, Nginx service `nginx`, Fail2ban service `fail2ban`

**Templates rendered**:
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`:
  - `/etc/nginx/sites-available/test.cluster.local`: 1 render
  - `/etc/nginx/sites-available/ci.cluster.local`: 1 render
  - `/etc/nginx/sites-available/status.cluster.local`: 1 render
  - Total: 3 renders

## Pre-flight checks:
```bash
# Nginx service status and configuration
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf

# Fail2ban service and configuration
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
test -f /etc/fail2ban/jail.local
fail2ban-client ping
fail2ban-client status

# Verify test.cluster.local
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%a %U %G %n' /etc/ssl/private/test.cluster.local.key

# Verify ci.cluster.local
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%a %U %G %n' /etc/ssl/private/ci.cluster.local.key

# Verify status.cluster.local
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%a %U %G %n' /etc/ssl/private/status.cluster.local.key

# Verify the default site is removed
test ! -e /etc/nginx/sites-enabled/default

# Verify listening ports
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Verify firewall rules
ufw status verbose
ufw status | grep -E '22|80|443'

# Verify SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
systemctl status ssh

# Verify sysctl configuration
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Review service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
```

The expected result is valid Nginx configuration, active Nginx and Fail2ban services, listening ports `80` and `443`, permitted firewall ports `22`, `80`, and `443`, successful HTTP and HTTPS responses for all three named hosts, and valid certificate/key pairs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.