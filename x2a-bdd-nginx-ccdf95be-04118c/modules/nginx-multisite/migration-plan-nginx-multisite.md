---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures Nginx for three sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`—with separate document roots, virtual-host configurations, and locally generated self-signed TLS certificates. It also installs and configures Fail2ban and UFW, applies security sysctl settings, disables root SSH login and SSH password authentication, deploys static index files, removes the default Nginx site, and enables Nginx. Execution order is security configuration, Nginx installation, SSL setup, and virtual-host deployment.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443` if confirmed by the rendered templates
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; Nginx configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; index file `/opt/server/test/index.html`

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443` if confirmed by the rendered templates
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; Nginx configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; index file `/opt/server/ci/index.html`

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443` if confirmed by the rendered templates
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; Nginx configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; index file `/opt/server/status/index.html`

**Security components**:

- Fail2ban
- UFW
- SSH configuration hardening
- Kernel security settings in `/etc/sysctl.d/99-security.conf`

The configured values for the `nginx.sites` collection and SSH attributes are identified by the plan but require verification against `cookbooks/nginx-multisite/attributes/default.rb`.

## File Structure

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── files/
├── providers/
├── recipes/
│   ├── default.rb
│   ├── security.rb
│   ├── nginx.rb
│   ├── ssl.rb
│   └── sites.rb
└── templates/
    └── default/
        ├── fail2ban.jail.local.erb
        ├── nginx.conf.erb
        ├── security.conf.erb
        ├── site.conf.erb
        └── sysctl-security.conf.erb
```

**Recipes:**

- `cookbooks/nginx-multisite/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/security.rb`
- `cookbooks/nginx-multisite/recipes/nginx.rb`
- `cookbooks/nginx-multisite/recipes/ssl.rb`
- `cookbooks/nginx-multisite/recipes/sites.rb`

**Providers:** None

**Files:** No static files were identified in the supplied directory listing. The `cookbook_file` source expression is `#{site_folder}/index.html`; the corresponding source files must be mapped after inspecting the source cookbook.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order: security, base Nginx configuration, SSL generation, and virtual-host deployment.
   - Resources: four `include_recipe` resources.

2. **`security`** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default incoming policy to deny.
   - Allows SSH, HTTP, and HTTPS through UFW.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; no invocation notification or subscription is shown.
   - Applies `PermitRootLogin no` when `node['security']['ssh']['disable_root']` is true. The analyzed configured value is `true`, but the attribute file requires verification.
   - Applies `PasswordAuthentication no` when `node['security']['ssh']['password_auth'] == false`. The analyzed configured value is `false`, but the attribute file requires verification.
   - Defines the `ssh` service with action `nothing`; no SSH restart or reload is shown.
   - Resources: one package resource, two service resources, two template resources, seven execute resources, and the two conditional SSH-hardening execute resources.
   - Ansible mapping: use package, service, template, UFW, sysctl, and `lineinfile` tasks while preserving the conditions and avoiding an automatic SSH restart unless a safe handler and alternate administrative session are confirmed.

3. **`nginx`** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` and deploys the unresolved source expression `#{site_folder}/index.html` to `/opt/server/test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` and deploys the unresolved source expression `#{site_folder}/index.html` to `/opt/server/ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` and deploys the unresolved source expression `#{site_folder}/index.html` to `/opt/server/status/index.html` with mode `0644`.
   - Does not require a `www-data` group task based on the structured execution tree; no `group[www-data]` resource was identified.
   - No explicit Nginx reload or restart notification is shown for global configuration or static-file changes.

4. **`ssl`** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - No separate directory ownership or group resources are confirmed by the structured execution tree.
   - Generates a 2048-bit RSA, self-signed certificate valid for 365 days for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
     - Subject CN: `test.cluster.local`
     - Key mode: `640`
     - Key ownership: `root:ssl-cert`
   - Generates a 2048-bit RSA, self-signed certificate valid for 365 days for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
     - Subject CN: `ci.cluster.local`
     - Key mode: `640`
     - Key ownership: `root:ssl-cert`
   - Generates a 2048-bit RSA, self-signed certificate valid for 365 days for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
     - Subject CN: `status.cluster.local`
     - Key mode: `640`
     - Key ownership: `root:ssl-cert`
   - Uses the subject format `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Prefer `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate` for the Ansible implementation.

5. **`sites`** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `True`, subject to attribute verification
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `True`, subject to attribute verification
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `True`, subject to attribute verification
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Resources: three template resources, three link resources, and one file resource.
   - No explicit Nginx reload or restart is shown after virtual-host deployment.

## Dependencies

**External cookbook dependencies**: None identified.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `ssh`: referenced with action `nothing`; no restart or start action is shown.

**Network access configured through UFW**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`

The Nginx listen directives and bind addresses require verification in `nginx.conf.erb` and `site.conf.erb`.

## Credentials

**Detection Summary**: No external application credentials, passwords, API tokens, data bags, Chef Vault items, or secret-manager integrations were detected in the analyzed cookbook.

**Source**:

- **Provider**: None detected
- **URL**: None detected
- **Path**: None detected

### TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; no external secret store.
- **Usage context**: TLS private keys for the three Nginx HTTPS virtual hosts.
- **Permissions**: `640`
- **Ownership**: `root:ssl-cert`

### TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate files.
- **Usage context**: TLS certificates for the three Nginx HTTPS virtual hosts.
- **Properties**:
  - RSA 2048-bit key
  - Self-signed
  - Valid for 365 days
  - Subject email `admin@example.com`

No hardcoded passwords, API keys, database credentials, encrypted data bags, Chef Vault calls, CyberArk calls, Conjur variables, or secret environment variables were identified.

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` must not exist
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

- TCP `22`: SSH
- TCP `80`: HTTP, if confirmed by rendered Nginx configuration
- TCP `443`: HTTPS, if confirmed by rendered Nginx configuration
- Unix sockets: None identified
- Network interfaces: Not specified

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: **1 render**
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: **1 render**
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: **1 render**
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: **1 render**
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: **1 render**
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: **1 render**
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: **1 render**
- `site.conf.erb`: **3 total renders**

The exact Nginx listener behavior, Fail2ban jails, and sysctl keys require inspection of the template contents.

## Pre-flight checks

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates

systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx

systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Security and firewall validation
ufw status verbose
ufw status numbered
test -f /etc/fail2ban/jail.local
fail2ban-client status

grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config
sshd -t

test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Global Nginx validation
nginx -t
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test ! -e /etc/nginx/sites-enabled/default

# Nginx listeners
ss -tlnp | grep -E ':(80|443)\b' || true

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ || true
curl -I --resolve test.cluster.local:80:127.0.0.1 http://test.cluster.local/ || true

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ || true
curl -I --resolve ci.cluster.local:80:127.0.0.1 http://ci.cluster.local/ || true

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ || true
curl -I --resolve status.cluster.local:80:127.0.0.1 http://status.cluster.local/ || true

# TLS key permissions
stat -c '%a %U:%G %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u ssh --no-pager -n 100
```

Expected TLS key permissions:

```text
640 root:ssl-cert /etc/ssl/private/test.cluster.local.key
640 root:ssl-cert /etc/ssl/private/ci.cluster.local.key
640 root:ssl-cert /etc/ssl/private/status.cluster.local.key
```

Expected security results:

```text
PermitRootLogin no
PasswordAuthentication no
```

Expected service and firewall results:

- Nginx is installed, enabled, active, and passes `nginx -t`.
- Fail2ban is installed, enabled, active, and loads its configured jails without errors.
- UFW is active with default incoming policy `deny`.
- SSH, HTTP, and HTTPS are allowed by UFW.
- The three document roots, index files, certificates, site configurations, and enabled-site links exist.
- `/etc/nginx/sites-enabled/default` is absent.
- HTTP and HTTPS checks must be treated as conditional until the rendered Nginx templates confirm listeners on ports `80` and `443`.
