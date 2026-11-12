---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures Nginx as a multisite HTTPS web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Fail2ban, UFW, Nginx, OpenSSL, and CA certificates; applies kernel and SSH hardening; creates self-signed TLS certificates; creates site document roots; renders Nginx and virtual-host configuration; enables the three sites; and removes the default site. The Ansible implementation must preserve the execution order: security, Nginx installation and base configuration, SSL certificate generation, and site configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP port `80`; HTTPS port `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP port `80`; HTTPS port `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP port `80`; HTTPS port `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

**Security configuration**:

- **fail2ban**: Enabled and started; package and service name `fail2ban`
- **ufw**: Enabled; package `ufw`; default incoming traffic denied; SSH, HTTP, and HTTPS allowed
- **ssh**: Conditional hardening commands set `PermitRootLogin no` and `PasswordAuthentication no` when the corresponding attributes evaluate to the configured values

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

**Providers:**
```text
```

No provider files or custom resources are used in the execution tree.

**Templates:**
```text
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb
```

**Attributes:**
```text
attributes/default.rb
```

**Files:**
```text
```

No static file path under `files/` is listed in the supplied cookbook structure. The `nginx.rb` recipe uses `cookbook_file` resources for the three site `index.html` files, but corresponding source files are not present in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `cookbooks/nginx-multisite/recipes/security.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/nginx.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Includes `cookbooks/nginx-multisite/recipes/sites.rb`.
   - Preserves the dependency order required by later Nginx, SSL, and site configuration steps.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `service[fail2ban]`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Executes, in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as `execute[reload_sysctl]` with action `nothing`; no explicit trigger is shown.
   - Conditionally executes `sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config` when the root-login attribute is enabled.
   - Conditionally executes `sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config` when password authentication is disabled.
   - Declares `service[sshd]` with action `nothing`; no restart is shown.
   - The analyzed resource counts are: one package resource containing two packages, two service resources, two template resources, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts `service[nginx]`.
   - Creates `/opt/server/test` and installs `/opt/server/test/index.html` using `cookbook_file` with mode `0644`; source expression is `#{site_folder}/index.html`.
   - Creates `/opt/server/ci` and installs `/opt/server/ci/index.html` using `cookbook_file` with mode `0644`; source expression is `#{site_folder}/index.html`.
   - Creates `/opt/server/status` and installs `/opt/server/status/index.html` using `cookbook_file` with mode `0644`; source expression is `#{site_folder}/index.html`.
   - The site loop is expanded for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - The analyzed resource counts are: one package, two templates, one service, three directories, and three `cookbook_file` resources.
   - No `nginx` group resource is included because the supplied execution tree does not show one.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates `group[ssl-cert]`.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate valid for 365 days for `test.cluster.local` using:
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Subject CN: `test.cluster.local`
   - Generates a self-signed RSA 2048-bit certificate valid for 365 days for `ci.cluster.local` using:
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Subject CN: `ci.cluster.local`
   - Generates a self-signed RSA 2048-bit certificate valid for 365 days for `status.cluster.local` using:
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Subject CN: `status.cluster.local`
   - Uses `openssl req -x509 -nodes -days 365 -newkey rsa:2048` with subject organization values `C=US`, `ST=Example`, `L=Example`, `O=Example Org`, `OU=IT`, and email address `admin@example.com`.
   - Sets each private-key mode to `0640` and ownership to `root:ssl-cert`.
   - The SSL loop is expanded for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - The analyzed resource counts are: one package resource containing two packages, one group, two directories, and three execute resources.
   - No additional directory ownership group resources are asserted because they are not present in the supplied execution tree.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with mode `0755`.
   - The analyzed tree reports three directory resources in the initial site-directory loop, although only the two shared directory paths above are identified in the supplied plan. The migration must reconcile the third resource against the actual recipe before implementation; it must not invent an unsupported path.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local` with:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local` with:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local` with:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - The site loop is expanded for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - The analyzed template/link counts are three templates and three links. The plan also includes two explicitly identified shared-directory resources and one deletion resource.

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
- `sshd`: declared with action `nothing`; no restart is shown

**Firewall services allowed**:
- SSH
- HTTP
- HTTPS

## Credentials

**Detection Summary**: No application credentials, passwords, API tokens, data bags, Chef Vault items, CyberArk references, or secret-manager integrations were detected. Three locally generated TLS private keys and three locally generated TLS certificates are created as deployment artifacts.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

### TLS Private Keys

- **Variable(s)**: `key_file`, derived from the site name and the configured private-key path
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by `openssl req`; not retrieved from a vault or data bag
- **Usage context**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: Mode `0640`, owned by `root:ssl-cert`

### TLS Certificates

- **Variable(s)**: `cert_file`, derived from the site name and the configured certificate path
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Self-signed certificates generated locally; not retrieved from a vault or data bag
- **Usage context**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`

The certificate subject contains the fixed email address `admin@example.com`; this is certificate metadata, not an authentication credential.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/opt/server/test
/opt/server/test/index.html
/opt/server/ci
/opt/server/ci/index.html
/opt/server/status
/opt/server/status/index.html
/etc/ssl/certs
/etc/ssl/private
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
```

The following file must be absent:

```text
/etc/nginx/sites-enabled/default
```

**Service endpoints to check**:
- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH service port, allowed by UFW
- Unix sockets: none identified

**Templates rendered**:
- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

`site.conf.erb` renders three times total.

## Pre-flight checks:

```bash
# Package installation
dpkg-query -W fail2ban ufw nginx openssl ca-certificates

# Service status
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-enabled nginx
systemctl is-active nginx
systemctl status fail2ban
systemctl status nginx

# Nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
stat -c '%a %U:%G %n' /etc/nginx/nginx.conf /etc/nginx/conf.d/security.conf

# Test site
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test "$(readlink -f /etc/nginx/sites-enabled/test.cluster.local)" = \
  /etc/nginx/sites-available/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# CI site
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test "$(readlink -f /etc/nginx/sites-enabled/ci.cluster.local)" = \
  /etc/nginx/sites-available/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# Status site
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test "$(readlink -f /etc/nginx/sites-enabled/status.cluster.local)" = \
  /etc/nginx/sites-available/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# TLS certificates
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -text | grep 'Public-Key'
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -text | grep 'Public-Key'
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -text | grep 'Public-Key'

stat -c '%a %U:%G %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Listening ports
ss -tlnp | grep -E ':(80|443)\b'

# Firewall
ufw status verbose
ufw status numbered

# Fail2ban
fail2ban-client status
cat /etc/fail2ban/jail.local
journalctl -u fail2ban --no-pager -n 50

# SSH configuration
sshd -t
sshd -T | grep -E 'permitrootlogin|passwordauthentication'
grep -E '^[[:space:]]*(PermitRootLogin|PasswordAuthentication)' \
  /etc/ssh/sshd_config

# Kernel security configuration
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf

# Logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u ssh --no-pager -n 100 || journalctl -u sshd --no-pager -n 100
```

Expected results:

- `fail2ban` and `nginx` are installed, enabled, and active.
- Nginx configuration validation reports `syntax is ok`.
- All three virtual hosts and their enabled links exist.
- `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` resolve to their respective document roots.
- All three certificates are self-signed, use RSA 2048-bit keys, contain the expected common name, and are valid for approximately 365 days.
- All private keys have mode `0640` and ownership `root:ssl-cert`.
- Nginx listens on ports `80` and `443` when configured by the rendered templates.
- UFW is active with a default-deny incoming policy and allows SSH, HTTP, and HTTPS.
- Fail2ban configuration is present and accepted without service errors.
- Effective SSH settings are `permitrootlogin no` and `passwordauthentication no` when the corresponding conditional attributes are enabled.
- The sysctl file exists and loads successfully.
- No Nginx, certificate permission, Fail2ban, SSH, or firewall activation errors appear in the logs.
