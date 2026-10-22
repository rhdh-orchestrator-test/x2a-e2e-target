---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS virtual sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx and Fail2ban, configures UFW with a deny-by-default policy while allowing SSH, HTTP, and HTTPS, applies kernel and SSH hardening, creates self-signed 2048-bit certificates, deploys three Nginx virtual-host configurations and document roots, and removes the default enabled Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: TCP ports `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: TCP ports `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: TCP ports `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: No dedicated application port
  - Key Config: Enabled and started; package `fail2ban`

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows SSH `22`, HTTP `80`, and HTTPS `443`
  - Key Config: Enabled with default incoming policy `deny`

- **ssh**: Hardened SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP port `22`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`; no explicit restart or reload is defined

## File Structure

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── files/
├── recipes/
│   ├── default.rb
│   ├── security.rb
│   ├── nginx.rb
│   ├── ssl.rb
│   └── sites.rb
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── providers/
```

No provider files or static files under `files/` are shown as deployed by the execution tree. The three `cookbook_file` resources refer to `test/index.html`, `ci/index.html`, and `status/index.html`; those source files must be supplied by the migration project or another explicitly defined content source.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the ordering of security configuration, Nginx installation, certificate generation, and virtual-host deployment.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw` using one package collection.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures UFW in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as a deferred reload action.
   - Applies SSH hardening:
     - Sets `PermitRootLogin no`.
     - Sets `PasswordAuthentication no`.
   - Uses an `ssh` service resource with action `nothing`; no explicit SSH restart or reload is shown.
   - Ansible should use idempotent UFW modules, `lineinfile`, and a handler for sysctl reload where appropriate.
   - Resources: one package resource for two packages, two service resources, two templates, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates the document root and deploys the index file for `test.cluster.local`:
     - Directory: `/opt/server/test`
     - File: `/opt/server/test/index.html`
     - Source: `test/index.html`
     - Mode: `0644`
   - Creates the document root and deploys the index file for `ci.cluster.local`:
     - Directory: `/opt/server/ci`
     - File: `/opt/server/ci/index.html`
     - Source: `ci/index.html`
     - Mode: `0644`
   - Creates the document root and deploys the index file for `status.cluster.local`:
     - Directory: `/opt/server/status`
     - File: `/opt/server/status/index.html`
     - Source: `status/index.html`
     - Mode: `0644`
   - Resources: one package, two templates, one service, three directories, and three cookbook files.
   - Ansible should run `nginx -t` before restarting or reloading Nginx after configuration changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate for `test.cluster.local`:
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Validity: 365 days
     - Subject email: `admin@example.com`
   - Generates a self-signed RSA 2048-bit certificate for `ci.cluster.local`:
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Validity: 365 days
     - Subject email: `admin@example.com`
   - Generates a self-signed RSA 2048-bit certificate for `status.cluster.local`:
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Validity: 365 days
     - Subject email: `admin@example.com`
   - All certificates use subject values `US`, `Example`, `Example`, `Example Org`, `IT`, and the corresponding site name as the common name.
   - Sets every private key to mode `0640` and ownership `root:ssl-cert`.
   - Certificate generation must be idempotent in Ansible and must not regenerate existing certificates on every run.
   - Resources: one package resource for two packages, one group, two directories, and three execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to the following files:
     - `/etc/nginx/sites-available/test.cluster.local`, using document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
     - `/etc/nginx/sites-available/ci.cluster.local`, using document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
     - `/etc/nginx/sites-available/status.cluster.local`, using document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Creates enabled links:
     - `/etc/nginx/sites-enabled/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local`
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Resources: three templates, three links, and one file deletion.
   - Ansible should validate the complete configuration with `nginx -t` before reloading or restarting Nginx.

## Dependencies

**External cookbook dependencies**: None shown in the execution tree.

**System package dependencies**:
- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started by `security.rb`
- `nginx`: enabled and started by `nginx.rb`
- `ssh`: referenced with action `nothing`; no explicit restart or reload is defined

**Configuration dependencies**:
- UFW permits SSH, HTTP, and HTTPS.
- Nginx virtual-host configuration depends on certificates generated by `ssl.rb`.
- Virtual hosts depend on document roots created by `nginx.rb`.
- Recipe execution order places certificate generation before virtual-host deployment.

## Credentials

**Detection Summary**: No external credentials or secret-management integrations were detected in this cookbook.

**Source**:
- **Provider**: None detected
- **URL**: None detected
- **Path**: None detected

The TLS private keys are sensitive files, but they are generated locally rather than retrieved from a data bag, vault, environment variable, or secret manager.

### Self-signed SSL private keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files, not stored in a Chef data bag or vault
- **Usage context**: TLS private keys for the three Nginx HTTPS virtual hosts
- **Permissions**: Mode `0640`, owned by `root:ssl-cert`

### Certificate subject email

- **Variable/value**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate subject value
- **Usage context**: Embedded in each self-signed certificate subject; not an authentication credential, password, API key, or token

## Checks for the Migration

**Files to verify**:
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
- `/etc/nginx/sites-enabled/default` must not exist
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`

**Service endpoints to check**:
- SSH: TCP port `22`
- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- No separate application port or Unix socket is specified

**Templates rendered**:
- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb`: 3 renders total

## Pre-flight checks:

```bash
# Verify installed packages
dpkg -l nginx fail2ban ufw openssl ca-certificates

# Verify service status and enablement
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Validate Nginx configuration
nginx -t

# Verify global Nginx configuration
grep -E '^[[:space:]]*(user|worker_processes|events|http)' /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/security.conf

# Verify Fail2ban
cat /etc/fail2ban/jail.local
fail2ban-client ping
fail2ban-client status

# Verify UFW
ufw status verbose
ufw status numbered

# Expected: incoming policy deny; SSH, HTTP, and HTTPS allowed

# Verify kernel security and SSH hardening
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config

# Expected:
# PermitRootLogin no
# PasswordAuthentication no

# Verify test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout \
  -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# Verify ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout \
  -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# Verify status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout \
  -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Verify the default site was removed
test ! -e /etc/nginx/sites-enabled/default

# Verify all private-key ownership and permissions
stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Expected:
# root:ssl-cert
# 640

# Verify listening ports
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Verify HTTP behavior for every site
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/

# Verify HTTPS behavior for every site
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Review service and application logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
tail -n 100 /var/log/nginx/access.log
tail -n 100 /var/log/nginx/error.log
```