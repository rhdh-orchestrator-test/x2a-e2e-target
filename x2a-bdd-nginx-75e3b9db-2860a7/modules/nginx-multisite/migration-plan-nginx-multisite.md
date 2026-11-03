---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook deploys and hardens an Nginx web server hosting three HTTPS-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; configures firewall and SSH hardening; applies security-related sysctl settings; generates self-signed TLS certificates; deploys site content and Nginx virtual-host configurations; and enables the Nginx and Fail2ban services.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP TCP `80`; HTTPS TCP `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

**Security configuration**:

- **fail2ban**: Enabled and started as the `fail2ban` service.
- **ufw**: Enabled with incoming traffic denied by default; SSH, HTTP, and HTTPS are allowed.
- **ssh**: Root login is disabled. Password authentication is also disabled because `password_auth` is configured as `false`.

## File Structure

The following files are relevant to cookbook execution and migration.

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

No provider file is used by the execution tree.

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

No static `cookbook_file` source files are listed in the supplied directory inventory. The recipes reference dynamically named `index.html` files, so their source files must be verified separately before implementing the Ansible role.

## Module Explanation

The cookbook performs operations in this order, as included by `cookbooks/nginx-multisite/recipes/default.rb`:

1. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default policy to deny incoming traffic.
   - Allows SSH, HTTP, and HTTPS through UFW.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; reload should occur only when the sysctl template changes unless source inspection confirms different notification behavior.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` because `security.ssh.disable_root` is `true`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` because `security.ssh.password_auth` is `false`.
   - Defines the `ssh` service with action `nothing`; no SSH restart or reload is shown in the execution tree.

2. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Iterates the configured sites with the following expanded resources:
     - **`test.cluster.local`**:
       - Creates `/opt/server/test` with mode `0755`.
       - Deploys `/opt/server/test/index.html` with mode `0644`.
     - **`ci.cluster.local`**:
       - Creates `/opt/server/ci` with mode `0755`.
       - Deploys `/opt/server/ci/index.html` with mode `0644`.
     - **`status.cluster.local`**:
       - Creates `/opt/server/status` with mode `0755`.
       - Deploys `/opt/server/status/index.html` with mode `0644`.
   - The cookbook-file sources are dynamically referenced as `#{site_folder}/index.html`; verify that the corresponding source files exist.

3. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates the following self-signed certificates because all three sites have `ssl_enabled: true`:
     - **`test.cluster.local`**:
       - Key: `/etc/ssl/private/test.cluster.local.key`
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Subject CN: `test.cluster.local`
     - **`ci.cluster.local`**:
       - Key: `/etc/ssl/private/ci.cluster.local.key`
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Subject CN: `ci.cluster.local`
     - **`status.cluster.local`**:
       - Key: `/etc/ssl/private/status.cluster.local.key`
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Subject CN: `status.cluster.local`
   - Certificate generation uses self-signed X.509 certificates, RSA 2048-bit keys, 365-day validity, and no passphrase.
   - All certificates use country `US`, state `Example`, locality `Example`, organization `Example Org`, organizational unit `IT`, and email `admin@example.com`.
   - Private keys are owned by `root:ssl-cert` with mode `0640`.

4. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **`test.cluster.local`** to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **`ci.cluster.local`** to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **`status.cluster.local`** to `/etc/nginx/sites-available/status.cluster.local`.
   - Uses the corresponding document roots, certificate paths, key paths, and `ssl_enabled: true` for each virtual host.
   - Creates enabled-site links:
     - `/etc/nginx/sites-enabled/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local`
   - Removes `/etc/nginx/sites-enabled/default`.
   - The execution tree does not show an Nginx reload or restart notification after site changes. Adding a validation-and-reload handler is an intentional migration improvement, not a direct resource translation.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata summary.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started by `security.rb`
- `nginx`: enabled and started by `nginx.rb`
- `ssh`: referenced with action `nothing`; its configuration is modified by the SSH hardening resources

**Firewall allowances**:

- SSH
- HTTP
- HTTPS

## Credentials

**Detection Summary**: No externally supplied application credentials were detected. Six generated TLS artifacts are sensitive: three private keys and three certificates across one source file.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

### Generated TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL; not retrieved from a data bag, Chef Vault, CyberArk, or another secret manager.
- **Usage context**: TLS private keys used by the Nginx virtual-host configurations.
- **Protection**: Owner `root`, group `ssl-cert`, mode `0640`.
- **Migration requirement**: Protect private-key values from logging and avoid regenerating them unnecessarily.

### Self-Signed TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL.
- **Usage context**: TLS certificates referenced by the Nginx site configurations.
- **Certificate properties**: Self-signed, RSA 2048-bit, 365-day validity, with common names matching the three site names.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/nginx/sites-enabled/default` must not exist

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH: normally TCP port `22`; UFW allows SSH by service name
- Unix sockets: none specified

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb` total: 3 renders

## Pre-flight checks:

```bash
# Security services and firewall
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
ufw status verbose
ufw status | grep -E '22|80|443|ssh|http|https'

# Security configuration
cat /etc/fail2ban/jail.local
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin|^[[:space:]]*PasswordAuthentication' \
  /etc/ssh/sshd_config
sshd -t
systemctl status ssh

# Nginx service and configuration
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
test ! -e /etc/nginx/sites-enabled/default

# Test site
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

# CI site
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

# Status site
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# Network listening checks
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
```

Expected results include:

- `PermitRootLogin no`
- `PasswordAuthentication no`
- Nginx and Fail2ban are enabled and active.
- Nginx listens on TCP ports `80` and `443`.
- Each named virtual host responds over HTTP and HTTPS.
- Each certificate has the expected common name.
- Each private key is owned by `root:ssl-cert` with mode `640`.
- The default Nginx site is absent.
- No Nginx configuration, certificate-read, virtual-host, or Fail2ban startup errors appear in the logs.