---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It applies security hardening, installs and starts Fail2ban and Nginx, configures UFW and kernel security settings, disables SSH root login and password authentication, creates site document roots and index files, generates self-signed certificates, and configures the three Nginx sites. The Ansible implementation must preserve the recipe order: security, Nginx installation, SSL generation, and site configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP TCP 80; HTTPS TCP 443
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP TCP 80; HTTPS TCP 443
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP TCP 80; HTTPS TCP 443
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

**Security configuration**:

- Fail2ban is enabled.
- UFW is enabled with default-deny policy and allowances for SSH, HTTP, and HTTPS.
- SSH root login is disabled.
- SSH password authentication is disabled.

## File Structure

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
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

**Providers**: None.

**Static files**: No static files under `files/default/` or `files/` are listed as deployed. The three site `index.html` files are deployed through `cookbook_file` resources using dynamically constructed source paths.

## Module Explanation

The cookbook performs operations in this order:

1. **Default recipe** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Uses four `include_recipe` resources.
   - This ordering applies security configuration before Nginx installation, generates certificates before site configuration, and creates site links last.

2. **Security configuration** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Applies the UFW default-deny policy with `ufw --force default deny`.
   - Allows SSH with `ufw allow ssh`, normally TCP port 22.
   - Allows HTTP with `ufw allow http`, normally TCP port 80.
   - Allows HTTPS with `ufw allow https`, normally TCP port 443.
   - Enables UFW with `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `reload_sysctl` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`.
   - No notification or subscription invokes `reload_sysctl` in the analyzed execution tree.
   - When `security.ssh.disable_root` is `true`, sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - When `security.ssh.password_auth` is `false`, sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Defines the `sshd` service with action `nothing`; no SSH restart or reload is shown.
   - Resources: one package resource installing two packages, two service resources, two templates, and eight execute resources.

3. **Nginx installation and site content** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Iterates over the following three sites:
     - **test.cluster.local**: creates `/opt/server/test` and `/opt/server/test/index.html`; the source is dynamically constructed as `test/index.html`; file mode is `0644`.
     - **ci.cluster.local**: creates `/opt/server/ci` and `/opt/server/ci/index.html`; the source is dynamically constructed as `ci/index.html`; file mode is `0644`.
     - **status.cluster.local**: creates `/opt/server/status` and `/opt/server/status/index.html`; the source is dynamically constructed as `status/index.html`; file mode is `0644`.
   - No Nginx reload notification is shown for configuration or content changes.
   - Resources: one package, two templates, one service, three directories, and three cookbook files.

4. **SSL certificate generation** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
   - Generates certificates for the following three SSL-enabled sites:
     - **test.cluster.local**:
       - Command resource: `generate-ssl-cert-test.cluster.local`
       - Key: `/etc/ssl/private/test.cluster.local.key`
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - 2048-bit RSA, self-signed, valid for 365 days
       - Subject common name: `test.cluster.local`
       - Subject email: `admin@example.com`
       - Key mode and ownership: `0640`, `root:ssl-cert`
     - **ci.cluster.local**:
       - Command resource: `generate-ssl-cert-ci.cluster.local`
       - Key: `/etc/ssl/private/ci.cluster.local.key`
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - 2048-bit RSA, self-signed, valid for 365 days
       - Subject common name: `ci.cluster.local`
       - Subject email: `admin@example.com`
       - Key mode and ownership: `0640`, `root:ssl-cert`
     - **status.cluster.local**:
       - Command resource: `generate-ssl-cert-status.cluster.local`
       - Key: `/etc/ssl/private/status.cluster.local.key`
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - 2048-bit RSA, self-signed, valid for 365 days
       - Subject common name: `status.cluster.local`
       - Subject email: `admin@example.com`
       - Key mode and ownership: `0640`, `root:ssl-cert`
   - The OpenSSL command uses `-x509 -nodes -days 365 -newkey rsa:2048` and creates unencrypted private keys.
   - The Ansible implementation should add an explicit certificate-existence or equivalent idempotence condition so certificates are not regenerated on every run.
   - Resources: one package resource installing two packages, one group, two directories, and three execute resources.

5. **Nginx site directories and virtual hosts** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - The analyzed execution tree contains one three-item directory loop over the site document roots:
     - **test.cluster.local**: creates `/opt/server/test` with mode `0755`.
     - **ci.cluster.local**: creates `/opt/server/ci` with mode `0755`.
     - **status.cluster.local**: creates `/opt/server/status` with mode `0755`.
   - The execution tree does not show resources creating `/etc/nginx/sites-available` or `/etc/nginx/sites-enabled`. Their existence is therefore assumed or must be provided separately in the migration.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` and creates an enabled link for:
     - **test.cluster.local**:
       - Destination: `/etc/nginx/sites-available/test.cluster.local`
       - Document root: `/opt/server/test`
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Private key: `/etc/ssl/private/test.cluster.local.key`
       - Enabled link: `/etc/nginx/sites-enabled/test.cluster.local`
       - Mode: `0644`
     - **ci.cluster.local**:
       - Destination: `/etc/nginx/sites-available/ci.cluster.local`
       - Document root: `/opt/server/ci`
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key: `/etc/ssl/private/ci.cluster.local.key`
       - Enabled link: `/etc/nginx/sites-enabled/ci.cluster.local`
       - Mode: `0644`
     - **status.cluster.local**:
       - Destination: `/etc/nginx/sites-available/status.cluster.local`
       - Document root: `/opt/server/status`
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Private key: `/etc/ssl/private/status.cluster.local.key`
       - Enabled link: `/etc/nginx/sites-enabled/status.cluster.local`
       - Mode: `0644`
   - Deletes `/etc/nginx/sites-enabled/default`.
   - No service reload or restart is shown after rendering site templates or creating links.
   - Resources: three directories, three templates, three links, and one file deletion.

## Dependencies

**External cookbook dependencies**: None specified.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `sshd`: defined with action `nothing`; no restart, reload, or start action is shown.

**Network access configured by UFW**:

- SSH service `ssh`, normally TCP port 22.
- HTTP service `http`, normally TCP port 80.
- HTTPS service `https`, normally TCP port 443.

## Credentials

**Detection Summary**: Three sensitive TLS private keys are generated locally. No external credentials, data bags, vault integrations, API tokens, database passwords, environment-variable secrets, or secret-manager integrations were detected.

**Source**:

- **Provider**: Locally generated by OpenSSL
- **URL**: None
- **Path**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`

### TLS private key for `test.cluster.local`

- **Variable(s)**: Dynamically generated `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated, unencrypted private key because the OpenSSL command uses `-nodes`
- **Usage context**: TLS private key for the `test.cluster.local` Nginx virtual host
- **Permissions and ownership**: `0640`, `root:ssl-cert`

### TLS private key for `ci.cluster.local`

- **Variable(s)**: Dynamically generated `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated, unencrypted private key because the OpenSSL command uses `-nodes`
- **Usage context**: TLS private key for the `ci.cluster.local` Nginx virtual host
- **Permissions and ownership**: `0640`, `root:ssl-cert`

### TLS private key for `status.cluster.local`

- **Variable(s)**: Dynamically generated `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated, unencrypted private key because the OpenSSL command uses `-nodes`
- **Usage context**: TLS private key for the `status.cluster.local` Nginx virtual host
- **Permissions and ownership**: `0640`, `root:ssl-cert`

The certificate subject contains the fixed email address `admin@example.com`, which is certificate metadata rather than an authentication credential.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` — must be absent
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

- `test.cluster.local`: TCP 80 and TCP 443
- `ci.cluster.local`: TCP 80 and TCP 443
- `status.cluster.local`: TCP 80 and TCP 443
- SSH firewall allowance: TCP 22
- Unix sockets: none specified

**Templates rendered**:

- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Security services and firewall
systemctl status fail2ban
systemctl is-enabled fail2ban
ufw status verbose
ufw status numbered

# Expected allowances:
# SSH / TCP 22
# HTTP / TCP 80
# HTTPS / TCP 443

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# Kernel security configuration
test -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf
sysctl -a 2>/dev/null | grep -E 'net\.ipv4|kernel\.' | head -50

# Run only if the migration explicitly invokes the reload
sysctl -p /etc/sysctl.d/99-security.conf

# Nginx service and configuration
systemctl status nginx
systemctl is-enabled nginx
nginx -t
nginx -T

# Parent directories are assumed or must be supplied separately
test -d /etc/nginx/sites-available
test -d /etc/nginx/sites-enabled

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
stat -c '%A %U:%G %n' /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
stat -c '%A %U:%G %n' /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
stat -c '%A %U:%G %n' /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Default-site removal
test ! -e /etc/nginx/sites-enabled/default

# Listening ports
ss -tlnp | grep -E ':(80|443)\b'
netstat -tulpn | grep -E ':(80|443)\b'

# Service diagnostics
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100

# Verify all private-key permissions and ownership
stat -c '%A %U:%G %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key
```

Expected results:

- Nginx syntax validation succeeds.
- Nginx listens on TCP ports 80 and 443.
- All three site links resolve to their corresponding site configurations.
- HTTP and HTTPS requests for all three hostnames return an HTTP response, normally `200 OK`.
- Each certificate contains the matching hostname in its subject.
- All private keys have mode `0640` and ownership `root:ssl-cert`.
- The default Nginx site is absent.
- Fail2ban is enabled, running, and free of startup errors.
- SSH configuration contains `PermitRootLogin no` and `PasswordAuthentication no`.