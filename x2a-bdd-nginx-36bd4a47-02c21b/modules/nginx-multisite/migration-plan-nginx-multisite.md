---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS virtual hosts—**test.cluster.local**, **ci.cluster.local**, and **status.cluster.local**—including site document roots, index files, self-signed TLS certificates, virtual-host configurations, enabled-site links, and removal of the default site. It also installs and configures Fail2ban, UFW, SSH hardening, and a security-related sysctl file. The site paths, modes, ownership, attribute values, and link targets must be verified against the original cookbook because they are not fully represented in the supplied structured analysis. The dynamically referenced index-file sources must also be supplied or replaced with explicit Ansible content.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTPS, conventionally `443`; confirm from rendered configuration
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; SSL enabled value requires verification

- **ci.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTPS, conventionally `443`; confirm from rendered configuration
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; SSL enabled value requires verification

- **status.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTPS, conventionally `443`; confirm from rendered configuration
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; SSL enabled value requires verification

**Security components**:

- **fail2ban**: Enabled, installed, and started
- **ufw**: Enabled with default-deny policy and SSH, HTTP, and HTTPS allowances
- **ssh**: Root-login hardening is configured as enabled in the supplied plan; password-authentication behavior requires verification against the actual attribute value and conditional command
- **sysctl**: Security configuration rendered to `/etc/sysctl.d/99-security.conf`

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

No static `cookbook_file` source files are listed. The three dynamically referenced `index.html` sources must be supplied separately or replaced with explicit Ansible templates or content tasks.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - Preserve this order so security configuration precedes Nginx installation, SSL provisioning, and site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Applies UFW commands in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Declares `sysctl -p /etc/sysctl.d/99-security.conf` as `execute[reload_sysctl]` with action `nothing`; immediate application requires explicit migration design.
   - Executes root-login hardening when the verified value of `node['security']['ssh']['disable_root']` is true:
     ```bash
     sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
     ```
   - Evaluates the password-authentication command only according to the actual Chef condition and verified attribute value:
     ```bash
     sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
     ```
   - Declares `service[ssh]` with action `nothing`; no automatic SSH restart or reload is shown.
   - Do not add automatic Fail2ban or SSH restarts without confirming the intended migration behavior.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates the following document roots; directory modes require verification:
     - `/opt/server/test` for `test.cluster.local`
     - `/opt/server/ci` for `ci.cluster.local`
     - `/opt/server/status` for `status.cluster.local`
   - Deploys the following index files using dynamically derived `cookbook_file` sources; source files are currently absent from the supplied file listing:
     - `/opt/server/test/index.html` from `test/index.html`
     - `/opt/server/ci/index.html` from `ci/index.html`
     - `/opt/server/status/index.html` from `status/index.html`
   - The three document-root iterations are explicitly `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` and `/etc/ssl/private`; directory modes and ownership require verification.
   - Generates a self-signed RSA 2048-bit certificate for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
     - Common Name: `test.cluster.local`
     - Validity: 365 days
     - Key mode and ownership from the command: `0640`, `root:ssl-cert`
   - Generates a self-signed RSA 2048-bit certificate for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
     - Common Name: `ci.cluster.local`
     - Validity: 365 days
     - Key mode and ownership from the command: `0640`, `root:ssl-cert`
   - Generates a self-signed RSA 2048-bit certificate for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
     - Common Name: `status.cluster.local`
     - Validity: 365 days
     - Key mode and ownership from the command: `0640`, `root:ssl-cert`
   - Add an idempotency guard equivalent to `creates` before using an Ansible command task; the Chef command does not show an explicit guard.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for each named site.
   - For `test.cluster.local`, renders `/etc/nginx/sites-available/test.cluster.local` with:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: value requiring verification
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - For `ci.cluster.local`, renders `/etc/nginx/sites-available/ci.cluster.local` with:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: value requiring verification
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - For `status.cluster.local`, renders `/etc/nginx/sites-available/status.cluster.local` with:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: value requiring verification
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Creates enabled-site links at:
     - `/etc/nginx/sites-enabled/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local`
   - Verify that each enabled-site link targets its corresponding file in `/etc/nginx/sites-available/`; the target relationship is not explicit in the supplied structured analysis.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Validate with `nginx -t`; no Nginx reload or restart is shown after rendering.

## Dependencies

**External cookbook dependencies**: None shown.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: action `nothing`; no explicit start, restart, or reload

**Firewall allowances**:

- SSH, conventionally port `22`
- HTTP, conventionally port `80`
- HTTPS, conventionally port `443`

Confirm the actual Nginx listen ports from the rendered site configurations.

## Credentials

**Detection Summary**: 0 credentials detected across the analyzed files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

No data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, secret-manager URLs, environment-variable secrets, hardcoded passwords, API keys, or database credentials were detected.

The generated TLS private keys are sensitive locally generated files rather than externally supplied credentials. Preserve the intended protections where confirmed:

- `/etc/ssl/private`: mode `0710`
- TLS private keys: mode `0640`
- TLS private-key owner/group: `root:ssl-cert`

## Checks for the Migration

**Files to verify**:

- `cookbooks/nginx-multisite/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/security.rb`
- `cookbooks/nginx-multisite/recipes/nginx.rb`
- `cookbooks/nginx-multisite/recipes/ssl.rb`
- `cookbooks/nginx-multisite/recipes/sites.rb`
- `cookbooks/nginx-multisite/attributes/default.rb`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
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
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

**Service endpoints to check**:

- `test.cluster.local`: HTTPS, conventionally `443`; confirm from `listen`
- `ci.cluster.local`: HTTPS, conventionally `443`; confirm from `listen`
- `status.cluster.local`: HTTPS, conventionally `443`; confirm from `listen`
- HTTP: conventionally `80`
- SSH: conventionally `22`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb`: 3 total renders

## Pre-flight checks:

```bash
# Verify services
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx

systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

systemctl status ssh

# Validate Nginx configuration
nginx -t

# Verify global Nginx configuration
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
cat /etc/nginx/conf.d/security.conf

# Verify test.cluster.local
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
grep -E 'server_name|root|listen|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
stat -c '%A %U:%G %n' /opt/server/test /opt/server/test/index.html
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout \
  -subject -issuer -dates
stat -c '%A %U:%G %n' \
  /etc/ssl/certs/test.cluster.local.crt \
  /etc/ssl/private/test.cluster.local.key
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# Verify ci.cluster.local
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
grep -E 'server_name|root|listen|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
stat -c '%A %U:%G %n' /opt/server/ci /opt/server/ci/index.html
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout \
  -subject -issuer -dates
stat -c '%A %U:%G %n' \
  /etc/ssl/certs/ci.cluster.local.crt \
  /etc/ssl/private/ci.cluster.local.key
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# Verify status.cluster.local
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
grep -E 'server_name|root|listen|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
stat -c '%A %U:%G %n' /opt/server/status /opt/server/status/index.html
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout \
  -subject -issuer -dates
stat -c '%A %U:%G %n' \
  /etc/ssl/certs/status.cluster.local.crt \
  /etc/ssl/private/status.cluster.local.key
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Verify default-site removal
test ! -e /etc/nginx/sites-enabled/default

# Verify certificate names
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject

# Verify Fail2ban
test -f /etc/fail2ban/jail.local
fail2ban-client -t
fail2ban-client status

# Verify UFW
ufw status verbose
ufw status numbered

# Verify SSH hardening
grep -E '^[# ]*PermitRootLogin|^[# ]*PasswordAuthentication' \
  /etc/ssh/sshd_config

# Verify sysctl configuration
test -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf

# Verify listening ports
ss -tlnp | grep -E ':(80|443|22)\b'
```