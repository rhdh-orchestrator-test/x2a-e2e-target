---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook deploys an Nginx web server with three HTTPS virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies firewall and SSH hardening; creates document roots and index files; generates self-signed certificates; renders and enables three Nginx site configurations; and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: TCP `443` for HTTPS; HTTP support on TCP `80`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: TCP `443` for HTTPS; HTTP support on TCP `80`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: TCP `443` for HTTPS; HTTP support on TCP `80`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

**Security configuration**:

- **fail2ban**: Installed as `fail2ban`, enabled, and started; configuration at `/etc/fail2ban/jail.local`
- **ufw**: Installed as `ufw`; inbound traffic denied by default; SSH, HTTP, and HTTPS allowed; firewall enabled
- **ssh**: Root login disabled and password authentication disabled; the SSH service is declared with `action: :nothing`, and no restart or reload is shown

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

No static files under `files/default/*` or `files/*` are listed in the supplied analysis. The `index.html` files are deployed with `cookbook_file`, but their source paths are dynamic and no corresponding static file paths were provided.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - Preserves the execution order: security, base Nginx installation, SSL generation, and virtual-host configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Executes the UFW commands in order:
     - `ufw --force default deny`
     - `ufw allow ssh`
     - `ufw allow http`
     - `ufw allow https`
     - `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Declares `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; the execution tree does not show it being invoked.
   - Executes SSH hardening because the configured attributes enable it:
     - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
     - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Declares `service[ssh]` with action `nothing`; no SSH restart or reload is shown.
   - Resources: one package resource, two service resources, two templates, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Iterates over the configured sites with the following expanded items:
     - **test.cluster.local**:
       - Creates `/opt/server/test`.
       - Deploys `/opt/server/test/index.html` with mode `0644`.
       - Uses the dynamic cookbook source `#{site_folder}/index.html`.
     - **ci.cluster.local**:
       - Creates `/opt/server/ci`.
       - Deploys `/opt/server/ci/index.html` with mode `0644`.
       - Uses the dynamic cookbook source `#{site_folder}/index.html`.
     - **status.cluster.local**:
       - Creates `/opt/server/status`.
       - Deploys `/opt/server/status/index.html` with mode `0644`.
       - Uses the dynamic cookbook source `#{site_folder}/index.html`.
   - No Nginx reload or restart notification is shown for the global templates or document files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Does not attribute `root:ssl-cert` ownership to the certificate directories; that ownership is explicitly applied only to generated private-key files.
   - Iterates over the configured sites with the following expanded items:
     - **test.cluster.local**:
       - Generates a 2048-bit RSA, self-signed certificate valid for 365 days.
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Private key: `/etc/ssl/private/test.cluster.local.key`
       - Common Name: `test.cluster.local`
       - Subject email: `admin@example.com`
       - Applies mode `640` and ownership `root:ssl-cert` to the private key.
     - **ci.cluster.local**:
       - Generates a 2048-bit RSA, self-signed certificate valid for 365 days.
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key: `/etc/ssl/private/ci.cluster.local.key`
       - Common Name: `ci.cluster.local`
       - Subject email: `admin@example.com`
       - Applies mode `640` and ownership `root:ssl-cert` to the private key.
     - **status.cluster.local**:
       - Generates a 2048-bit RSA, self-signed certificate valid for 365 days.
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Private key: `/etc/ssl/private/status.cluster.local.key`
       - Common Name: `status.cluster.local`
       - Subject email: `admin@example.com`
       - Applies mode `640` and ownership `root:ssl-cert` to the private key.
   - Uses the command form:
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout <key_file> \
       -out <cert_file> \
       -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com"
     chmod 640 <key_file>
     chown root:ssl-cert <key_file>
     ```
   - No certificate renewal timer or service reload notification is shown.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterates over the configured sites with the following expanded items:
     - **test.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
       - Uses `server_name` `test.cluster.local`, document root `/opt/server/test`, SSL enabled, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/test.cluster.local` linking to `/etc/nginx/sites-available/test.cluster.local`.
     - **ci.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
       - Uses `server_name` `ci.cluster.local`, document root `/opt/server/ci`, SSL enabled, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/ci.cluster.local` linking to `/etc/nginx/sites-available/ci.cluster.local`.
     - **status.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
       - Uses `server_name` `status.cluster.local`, document root `/opt/server/status`, SSL enabled, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/status.cluster.local` linking to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - No Nginx reload or restart notification is shown after site configuration changes.

## Dependencies

**External cookbook dependencies**: None provided or shown in the execution tree.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no explicit restart or reload is shown

## Credentials

**Detection Summary**: No credentials or secret-management integrations were detected in this cookbook.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, Vault attributes, environment-variable secrets, database credentials, API tokens, or hardcoded passwords were identified. The TLS certificates and private keys are generated locally by the cookbook and are not sourced from a credential provider. The `admin@example.com` value is certificate subject metadata, not an authentication credential.

## Checks for the Migration

**Files to verify**:

- Cookbook files:
  - `cookbooks/nginx-multisite/recipes/default.rb`
  - `cookbooks/nginx-multisite/recipes/security.rb`
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
  - `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
  - `cookbooks/nginx-multisite/templates/default/security.conf.erb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`
- Security configuration:
  - `/etc/fail2ban/jail.local`
  - `/etc/sysctl.d/99-security.conf`
  - `/etc/ssh/sshd_config`
- Nginx global configuration:
  - `/etc/nginx/nginx.conf`
  - `/etc/nginx/conf.d/security.conf`
- Site configurations:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`
- Enabled-site links:
  - `/etc/nginx/sites-enabled/test.cluster.local`
  - `/etc/nginx/sites-enabled/ci.cluster.local`
  - `/etc/nginx/sites-enabled/status.cluster.local`
- Document roots and index files:
  - `/opt/server/test`
  - `/opt/server/test/index.html`
  - `/opt/server/ci`
  - `/opt/server/ci/index.html`
  - `/opt/server/status`
  - `/opt/server/status/index.html`
- TLS files:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/certs/status.cluster.local.crt`
  - `/etc/ssl/private/status.cluster.local.key`
- Removed default site:
  - `/etc/nginx/sites-enabled/default` should not exist.

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH: TCP port `22`
- `test.cluster.local`
- `ci.cluster.local`
- `status.cluster.local`
- No Unix sockets are specified.

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
# Confirm installed packages
dpkg -l nginx fail2ban ufw openssl ca-certificates

# Nginx service
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx

# Fail2ban service
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# UFW status and expected rules
ufw status verbose
ufw status numbered
# Expected: default incoming deny; SSH, HTTP, and HTTPS allowed

# SSH hardening
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config
# Expected:
# PermitRootLogin no
# PasswordAuthentication no

# SSH service and endpoint
systemctl status ssh
ss -tlnp | grep ':22'

# Sysctl and Fail2ban configuration
cat /etc/sysctl.d/99-security.conf
cat /etc/fail2ban/jail.local
fail2ban-client status
```

### Site: `test.cluster.local`

```bash
ls -ld /opt/server/test
ls -l /opt/server/test/index.html

ls -l /etc/nginx/sites-available/test.cluster.local
ls -l /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local

ls -l /etc/ssl/certs/test.cluster.local.crt
ls -l /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates

grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/test.cluster.local

curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
```

### Site: `ci.cluster.local`

```bash
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html

ls -l /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local

ls -l /etc/ssl/certs/ci.cluster.local.crt
ls -l /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates

grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/ci.cluster.local

curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
```

### Site: `status.cluster.local`

```bash
ls -ld /opt/server/status
ls -l /opt/server/status/index.html

ls -l /etc/nginx/sites-available/status.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

ls -l /etc/ssl/certs/status.cluster.local.crt
ls -l /etc/ssl/private/status.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates

grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/status.cluster.local

curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
```

### Global Nginx validation

```bash
nginx -t

grep -E 'include|listen|user|worker' /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/security.conf

test ! -e /etc/nginx/sites-enabled/default

test -L /etc/nginx/sites-enabled/test.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local

ss -tlnp | grep -E ':(80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

curl -I http://127.0.0.1/
curl -k -I https://127.0.0.1/
```

### Logs and operational checks

```bash
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u nginx --no-pager | grep -Ei 'error|failed|emerg'

stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key
```