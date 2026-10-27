---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures Nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It creates self-signed RSA certificates, deploys site content and virtual-host configurations, and applies host security controls through Fail2ban, UFW, sysctl settings, and SSH hardening. The Ansible implementation must preserve the recipe execution order: security, Nginx installation and base configuration, SSL setup and certificate generation, and virtual-host deployment.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS virtual host serving the test site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTPS `443`; HTTP `80` is allowed by UFW
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS virtual host serving the CI site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTPS `443`; HTTP `80` is allowed by UFW
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS virtual host serving the status site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTPS `443`; HTTP `80` is allowed by UFW
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

The `nginx.sites` collection contains exactly three entries: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. All three sites have `ssl_enabled: true`.

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

No provider files or custom resources are used in the execution tree.

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

No static files under `files/default/` or `files/` are listed in the supplied cookbook structure. The three `index.html` files are referenced by `cookbook_file` resources, but their source paths are not present in the directory listing and must be obtained separately rather than invented.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - Uses four `include_recipe` resources.
   - The Ansible role must preserve this execution order through task files or role task imports.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Applies the UFW default-deny policy with `ufw --force default deny`.
   - Allows SSH with `ufw allow ssh`.
   - Allows HTTP with `ufw allow http`.
   - Allows HTTPS with `ufw allow https`.
   - Enables UFW with `ufw --force enable`.
   - Preserves the order of UFW commands so that allow rules are applied before UFW is enabled.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` through the `reload_sysctl` execute resource with action `nothing`; the migration must inspect notification semantics before adding a reload handler.
   - When `node['security']['ssh']['disable_root']` is true, changes `/etc/ssh/sshd_config` to set `PermitRootLogin no`.
   - When `node['security']['ssh']['password_auth'] == false`, changes `/etc/ssh/sshd_config` to set `PasswordAuthentication no`.
   - References the `ssh` service with action `nothing`; no unconditional SSH restart, reload, enable, or start should be added.
   - Resource count: 1 package resource installing two packages, 2 service resources, 2 template resources, and 8 execute resources. The complete count is 13 resources, or 11 when the two conditional SSH execute resources are excluded.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` with mode `0755`.
   - Deploys `/opt/server/test/index.html` with mode `0644`; the source path is `#{site_folder}/index.html` and must be obtained separately.
   - Creates `/opt/server/ci` with mode `0755`.
   - Deploys `/opt/server/ci/index.html` with mode `0644`; the source path is `#{site_folder}/index.html` and must be obtained separately.
   - Creates `/opt/server/status` with mode `0755`.
   - Deploys `/opt/server/status/index.html` with mode `0644`; the source path is `#{site_folder}/index.html` and must be obtained separately.
   - The site iteration runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - No Nginx reload or restart is shown in the execution tree. Add a handler only if the target migration explicitly validates and reloads Nginx after configuration changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Generates a certificate and private key for `test.cluster.local`:
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Common name: `test.cluster.local`
   - Generates a certificate and private key for `ci.cluster.local`:
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Common name: `ci.cluster.local`
   - Generates a certificate and private key for `status.cluster.local`:
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Common name: `status.cluster.local`
   - Uses self-signed RSA 2048-bit certificates valid for 365 days.
   - Sets private key ownership to `root:ssl-cert` and mode `0640`.
   - Uses the command structure:
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout <key_file> \
       -out <cert_file> \
       -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com"

     chmod 640 <key_file>
     chown root:ssl-cert <key_file>
     ```
   - The Ansible implementation should make certificate generation idempotent by checking for both the certificate and key before invoking the shell command.
   - Resource count: 1 package resource installing two packages, 1 group resource, 2 directory resources, and 3 execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` as a link.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` as a link.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` as a link.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Template variables for `test.cluster.local`:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - Template variables for `ci.cluster.local`:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - Template variables for `status.cluster.local`:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`

## Dependencies

**External cookbook dependencies**: None identified.

**System package dependencies**:
- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: referenced with action `nothing`; no active restart or reload is shown

**Security dependencies and controls**:
- UFW default-deny incoming policy
- UFW SSH allow rule
- UFW HTTP allow rule
- UFW HTTPS allow rule
- Root SSH login disabled
- SSH password authentication disabled
- Sysctl settings from `/etc/sysctl.d/99-security.conf`

## Credentials

**Detection Summary**: No application credentials, data bags, vault references, API keys, database passwords, or environment-variable secrets were detected. Three locally generated TLS private keys and three locally generated self-signed certificates are present.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

### TLS Private Keys

- **Variable(s)**: `key_file`, derived from the SSL private-key path and site name
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files
- **Usage context**: Used by the Nginx HTTPS virtual hosts
- **Files**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: Mode `0640`
- **Ownership**: `root:ssl-cert`

### TLS Certificates

- **Variable(s)**: `cert_file`, derived from the SSL certificate path and site name
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificates
- **Usage context**: Used by the Nginx HTTPS virtual hosts
- **Files**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`

No Vault, CyberArk, AWS Secrets Manager, Chef data bag, encrypted data bag, or hardcoded password source was identified.

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
- `/etc/nginx/sites-enabled/default` should not exist
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
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
- SSH: the configured SSH service port
- Unix sockets: none specified
- Nginx binding: not specified in the execution tree

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: 1 render to `/etc/fail2ban/jail.local`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: 1 render to `/etc/nginx/nginx.conf`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: 1 render to `/etc/nginx/conf.d/security.conf`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: 1 render to `/etc/sysctl.d/99-security.conf`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: 3 renders:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates
systemctl status nginx
systemctl status fail2ban
systemctl status ssh

# Nginx configuration validation
nginx -t
cat /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/security.conf

# Verify all virtual-host configurations
grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local' \
  /etc/nginx/sites-available/test.cluster.local \
  /etc/nginx/sites-available/ci.cluster.local \
  /etc/nginx/sites-available/status.cluster.local

# Verify test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# Verify ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# Verify status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Verify certificate ownership and permissions
stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Verify Fail2ban and UFW
systemctl status fail2ban
fail2ban-client status
ufw status verbose
ufw status numbered

# Verify SSH hardening
sshd -T | grep -E 'permitrootlogin|passwordauthentication'
grep -E '^[[:space:]]*PermitRootLogin|^[[:space:]]*PasswordAuthentication' \
  /etc/ssh/sshd_config

# Verify sysctl configuration
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Verify network listeners
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Verify default site removal
test ! -e /etc/nginx/sites-enabled/default

# Review service logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

Expected results:

- `nginx` is installed, enabled, running, and passes `nginx -t`.
- `fail2ban` is installed, enabled, and running.
- UFW is enabled with default incoming policy `deny`, while SSH, HTTP, and HTTPS are allowed.
- `PermitRootLogin` is `no`.
- `PasswordAuthentication` is `no`.
- All three certificates contain their corresponding common names and are valid for 365 days.
- All three private keys are owned by `root:ssl-cert` with mode `640`.
- Nginx responds on ports `80` and `443`.
- The three named virtual hosts return HTTP responses over HTTPS.
- `/etc/nginx/sites-enabled/default` does not exist.
- Sysctl settings load successfully and service logs contain no configuration, certificate, or startup errors.