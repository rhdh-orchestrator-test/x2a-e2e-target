---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and hardens Nginx, configures three HTTPS-enabled virtual hosts (`ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`), deploys static site content, generates self-signed certificates, and applies Fail2ban, UFW, sysctl, and SSH hardening. It also retrieves an encrypted Nginx site token from the `nginx_secrets/site` data bag and writes it to `/etc/nginx/secrets/site_token`.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **ci.cluster.local**: HTTPS-enabled static Nginx virtual host
  - Location/Path: `/var/www/ci.cluster.local`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - HTTP virtual-host configuration: `/etc/nginx/sites-available/ci.cluster.local`
  - Enabled configuration link: `/etc/nginx/sites-enabled/ci.cluster.local`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Static content: `/var/www/ci.cluster.local/index.html`
  - Key Config: `ssl_enabled: true`, document root `/var/www/ci.cluster.local`

- **status.cluster.local**: HTTPS-enabled static Nginx virtual host
  - Location/Path: `/var/www/status.cluster.local`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - HTTP virtual-host configuration: `/etc/nginx/sites-available/status.cluster.local`
  - Enabled configuration link: `/etc/nginx/sites-enabled/status.cluster.local`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Static content: `/var/www/status.cluster.local/index.html`
  - Key Config: `ssl_enabled: true`, document root `/var/www/status.cluster.local`

- **test.cluster.local**: HTTPS-enabled static Nginx virtual host
  - Location/Path: `/var/www/test.cluster.local`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - HTTP virtual-host configuration: `/etc/nginx/sites-available/test.cluster.local`
  - Enabled configuration link: `/etc/nginx/sites-enabled/test.cluster.local`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Static content: `/var/www/test.cluster.local/index.html`
  - Key Config: `ssl_enabled: true`, document root `/var/www/test.cluster.local`

**Security Configuration**:

- Fail2ban enabled
- UFW enabled with default inbound deny
- SSH root login disabled
- SSH password authentication disabled
- SSH, HTTP, and HTTPS allowed through UFW

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

No provider files are used by the reachable execution tree. The analyzed `resources/lineinfile.rb` custom resource is not referenced by the reachable recipes and is excluded from migration scope.

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

No static file paths under `files/` were supplied. The `cookbook_file` resources expect site-specific `index.html` files in the cookbook file area; verify and add the source files to the Ansible role if they exist in the source repository.

**Data bags:**
```text
data_bags/nginx_secrets/site.json
data_bags/nginx_sites/ci.cluster.local.json
data_bags/nginx_sites/status.cluster.local.json
data_bags/nginx_sites/test.cluster.local.json
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`, `nginx.rb`, `ssl.rb`, and `sites.rb` in that order.
   - The Ansible role should invoke equivalent task files in the same order.
   - Security is applied before Nginx configuration, certificates are generated before site configurations reference them, and site links are created last.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Executes UFW commands in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as `execute[reload_sysctl]` with action `nothing`; no triggering notification is shown and no automatic reload should be added without confirmation.
   - With `security.ssh.disable_root = true`, sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - With `security.ssh.password_auth = false`, sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Declares `service[sshd]` with action `nothing`; no SSH restart is shown.
   - Resource summary: one package resource installing two packages, two service resources, two template resources, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs `nginx`.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets`.
   - Reads encrypted data bag item `nginx_secrets/site` and writes its `token` field to `/etc/nginx/secrets/site_token`.
   - Preserve the analyzed permissions and ownership where confirmed; otherwise verify them against the source recipe before migration. The token must be stored with mode `0600`, owned by `root:root`, and must not be exposed in task output.
   - Site content iterations:
     - **ci.cluster.local**:
       - Reads `nginx_sites/ci.cluster.local`.
       - Creates `/var/www/ci.cluster.local`.
       - Deploys `index.html` to `/var/www/ci.cluster.local/index.html`.
       - Uses `document_root: /var/www/ci.cluster.local` and `ssl_enabled: true`.
     - **status.cluster.local**:
       - Reads `nginx_sites/status.cluster.local`.
       - Creates `/var/www/status.cluster.local`.
       - Deploys `index.html` to `/var/www/status.cluster.local/index.html`.
       - Uses `document_root: /var/www/status.cluster.local` and `ssl_enabled: true`.
     - **test.cluster.local**:
       - Reads `nginx_sites/test.cluster.local`.
       - Creates `/var/www/test.cluster.local`.
       - Deploys `index.html` to `/var/www/test.cluster.local/index.html`.
       - Uses `document_root: /var/www/test.cluster.local` and `ssl_enabled: true`.
   - The site content loop runs exactly three times and creates three directories and three `cookbook_file` resources.
   - No Nginx reload or restart is shown for base configuration or site content changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
   - Preserve root ownership where confirmed; verify any unspecified ownership before migration.
   - Certificate-generation iterations:
     - **ci.cluster.local**:
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Key: `/etc/ssl/private/ci.cluster.local.key`
       - Common Name: `ci.cluster.local`
     - **status.cluster.local**:
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Key: `/etc/ssl/private/status.cluster.local.key`
       - Common Name: `status.cluster.local`
     - **test.cluster.local**:
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Key: `/etc/ssl/private/test.cluster.local.key`
       - Common Name: `test.cluster.local`
   - Each iteration generates a self-signed RSA 2048-bit certificate valid for 365 days and sets the key ownership to `root:ssl-cert` with mode `0640`.
   - Use an idempotent Ansible certificate-generation approach and prevent regeneration on every run.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with mode `0755`.
   - Site configuration iterations:
     - **ci.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb`.
       - Destination: `/etc/nginx/sites-available/ci.cluster.local`.
       - Variables: `server_name=ci.cluster.local`, `document_root=/var/www/ci.cluster.local`, `ssl_enabled=true`, `cert_file=/etc/ssl/certs/ci.cluster.local.crt`, and `key_file=/etc/ssl/private/ci.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/ci.cluster.local`.
     - **status.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb`.
       - Destination: `/etc/nginx/sites-available/status.cluster.local`.
       - Variables: `server_name=status.cluster.local`, `document_root=/var/www/status.cluster.local`, `ssl_enabled=true`, `cert_file=/etc/ssl/certs/status.cluster.local.crt`, and `key_file=/etc/ssl/private/status.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/status.cluster.local`.
     - **test.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb`.
       - Destination: `/etc/nginx/sites-available/test.cluster.local`.
       - Variables: `server_name=test.cluster.local`, `document_root=/var/www/test.cluster.local`, `ssl_enabled=true`, `cert_file=/etc/ssl/certs/test.cluster.local.crt`, and `key_file=/etc/ssl/private/test.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/test.cluster.local`.
   - The virtual-host loop runs exactly three times and creates three templates and three links.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - No automatic Nginx reload or restart is shown.

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
- `sshd`: declared with action `nothing`; no restart shown

**Firewall ports permitted**:

- SSH, normally TCP `22`
- HTTP, TCP `80`
- HTTPS, TCP `443`

## Credentials

**Detection Summary**: 4 sensitive or security-related items detected across the Nginx recipe, SSL recipe, attributes, and data bags.

**Source**:

- **Provider**: Chef encrypted data bag `nginx_secrets/site` for the Nginx site token; local OpenSSL generation in `cookbooks/nginx-multisite/recipes/ssl.rb` for TLS material; Chef attributes in `cookbooks/nginx-multisite/attributes/default.rb` for SSH hardening settings
- **URL**: None detected
- **Path**: `data_bags/nginx_secrets/site.json`

### Nginx Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `data_bags/nginx_secrets/site.json`
- **Current storage**: Chef encrypted data bag item `nginx_secrets/site`
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **Permissions**: Mode `0600`, owner/group `root:root`
- **Migration handling**: Store in Ansible Vault or an approved AAP credential or external secret integration. Do not print the value.

### Generated TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
  - `/etc/ssl/private/test.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: TLS private keys for the three Nginx virtual hosts
- **Permissions**: Mode `0640`, owner/group `root:ssl-cert`
- **Migration handling**: Generate or provision securely and do not place private keys in plaintext variables or logs.

### Generated Self-Signed Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
  - `/etc/ssl/certs/test.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: TLS certificates for the three Nginx virtual hosts
- **Certificate properties**: Self-signed, RSA 2048-bit, valid for 365 days, organization `Example Org`, email `admin@example.com`
- **Migration handling**: Use idempotent Ansible certificate tasks. Replace with CA-issued certificates if required by production policy.

### SSH Hardening Settings

- **Variable(s)**:
  - `node['security']['ssh']['disable_root']`
  - `node['security']['ssh']['password_auth']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/security.rb`
- **Current storage**: Non-secret Chef cookbook attributes
- **Usage context**: Sets `PermitRootLogin no` and `PasswordAuthentication no`
- **Migration handling**: Represent as ordinary Ansible boolean variables and manage SSH configuration idempotently.

No HashiCorp Vault, CyberArk, AWS Secrets Manager, Conjur, environment-variable secret, or hardcoded password/API key was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/secrets/site_token`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/var/www/ci.cluster.local`
- `/var/www/ci.cluster.local/index.html`
- `/var/www/status.cluster.local`
- `/var/www/status.cluster.local/index.html`
- `/var/www/test.cluster.local`
- `/var/www/test.cluster.local/index.html`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/nginx/sites-enabled/default` must be absent

**Service endpoints to check**:

- HTTP TCP port `80`
- HTTPS TCP port `443`
- SSH TCP port `22`
- Nginx Unix sockets: none specified
- Hostnames:
  - `ci.cluster.local`
  - `status.cluster.local`
  - `test.cluster.local`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render

Total `site.conf.erb` renders: 3.

## Pre-flight checks:

```bash
# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Nginx and Fail2ban validation
nginx -t
fail2ban-client ping
fail2ban-client status

# Firewall validation
ufw status verbose
ufw status | grep -E '22|80|443'

# SSH and sysctl validation
grep -nE 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Base Nginx configuration
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
grep -nE 'listen|server_name|include' /etc/nginx/nginx.conf
grep -nE 'listen|server_name|ssl|security' /etc/nginx/conf.d/security.conf

# Secret validation without printing the value
test -d /etc/nginx/secrets
test -f /etc/nginx/secrets/site_token
stat -c '%a %U:%G %n' /etc/nginx/secrets/site_token
test "$(stat -c '%a' /etc/nginx/secrets/site_token)" = "600"
test "$(stat -c '%U:%G' /etc/nginx/secrets/site_token)" = "root:root"

# Site: ci.cluster.local
test -d /var/www/ci.cluster.local
test -f /var/www/ci.cluster.local/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl --resolve ci.cluster.local:80:127.0.0.1 -I http://ci.cluster.local/
curl --resolve ci.cluster.local:443:127.0.0.1 -k -I https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates

# Site: status.cluster.local
test -d /var/www/status.cluster.local
test -f /var/www/status.cluster.local/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl --resolve status.cluster.local:80:127.0.0.1 -I http://status.cluster.local/
curl --resolve status.cluster.local:443:127.0.0.1 -k -I https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates

# Site: test.cluster.local
test -d /var/www/test.cluster.local
test -f /var/www/test.cluster.local/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl --resolve test.cluster.local:80:127.0.0.1 -I http://test.cluster.local/
curl --resolve test.cluster.local:443:127.0.0.1 -k -I https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates

# Confirm the default site was removed
test ! -e /etc/nginx/sites-enabled/default

# Network listening checks
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
ss -tlnp | grep ':22'

# Logs and recent errors
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
grep -iE 'error|emerg|crit|alert' /var/log/nginx/error.log | tail -20
```