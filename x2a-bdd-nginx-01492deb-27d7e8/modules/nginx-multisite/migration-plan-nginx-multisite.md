---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx and Fail2ban, configures UFW with a default-deny policy while allowing SSH, HTTP, and HTTPS, applies kernel security settings, disables root SSH login and SSH password authentication, generates self-signed certificates for all three sites, deploys site content, and enables the Nginx virtual-host links.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP port `80`; HTTPS port `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP port `80`; HTTPS port `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP port `80`; HTTPS port `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: None
  - Key Config: Package installed; service enabled and started

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows SSH, HTTP port `80`, and HTTPS port `443`
  - Key Config: Default inbound policy denied; firewall enabled with `ufw --force enable`

- **ssh**: Hardened SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: SSH port `22`
  - Key Config: Root login disabled; password authentication disabled; Chef service resource has action `nothing`, and no SSH restart is shown

## File Structure

The following complete directory listing is relevant to cookbook execution and migration.

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

No static files are listed in the supplied cookbook file listing. The recipes deploy `index.html` through `cookbook_file`, but the source static files are not included in the provided execution-tree file list.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - Preserves the execution order: security controls, Nginx installation, SSL dependencies and certificates, then site-specific configuration.
   - Resources: `include_recipe` four times.
   - Iterations: None.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Sets the UFW default inbound policy to deny.
   - Allows SSH, HTTP, and HTTPS through UFW.
   - Enables UFW with `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Declares `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`.
   - Disables root SSH login with:
     ```bash
     sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
     ```
   - Disables SSH password authentication with:
     ```bash
     sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
     ```
   - Declares the SSH service with action `nothing`; the Chef execution tree does not show an SSH restart.
   - Resources: package (1), service (2), template (2), execute (8).
   - Execute resources: `ufw_default_deny`, `ufw_allow_ssh`, `ufw_allow_http`, `ufw_allow_https`, `ufw_enable`, `reload_sysctl`, `disable root login`, and `disable password auth`.
   - Iterations: The security collection contains exactly `fail2ban`, `ufw`, and `ssh`, represented by separate resources and conditionals.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` and deploys `/opt/server/test/index.html` for `test.cluster.local`.
   - Creates `/opt/server/ci` and deploys `/opt/server/ci/index.html` for `ci.cluster.local`.
   - Creates `/opt/server/status` and deploys `/opt/server/status/index.html` for `status.cluster.local`.
   - Uses a dynamic cookbook-file source based on the site folder: `#{site_folder}/index.html`.
   - Iterations: Three site-content iterations, for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3).
   - The execution tree does not show an Nginx reload notification for base templates, directories, or content files.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private`.
   - Generates a self-signed certificate and private key for `test.cluster.local`.
   - Generates a self-signed certificate and private key for `ci.cluster.local`.
   - Generates a self-signed certificate and private key for `status.cluster.local`.
   - Uses an OpenSSL command equivalent to:
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout <site-private-key> \
       -out <site-certificate> \
       -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site-name>/emailAddress=admin@example.com"
     chmod 640 <site-private-key>
     chown root:ssl-cert <site-private-key>
     ```
   - `test.cluster.local` outputs `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`.
   - `ci.cluster.local` outputs `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`.
   - `status.cluster.local` outputs `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`.
   - All three certificate subjects contain the corresponding site name as the common name.
   - All private keys are changed to mode `0640` and ownership `root:ssl-cert`.
   - Iterations: Three SSL-enabled iterations, for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. No certificate-generation branch is skipped.
   - Resources: package (1), group (1), directory (2), execute (3).
   - Certificate validity, key type, and subject values are derived from the OpenSSL command and should be verified against the source recipe during migration.
   - Certificate generation should be made idempotent in Ansible so certificates are not regenerated on every run unless required.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local`.
   - Creates enabled-site links for all three virtual hosts.
   - Removes `/etc/nginx/sites-enabled/default`.
   - `test.cluster.local` uses document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - `ci.cluster.local` uses document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - `status.cluster.local` uses document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Iterations: Three site-configuration iterations, for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resources: template (3), link (3), file (1).
   - The execution tree does not show an Nginx reload resource. The Ansible implementation should validate the configuration with `nginx -t` before reloading Nginx.

## Dependencies

**External cookbook dependencies**: None shown in the supplied execution tree or structured analysis.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no restart is shown
- `ufw`: enabled through `ufw --force enable`, not through a service resource

**Network access configured**:

- SSH, normally port `22`
- HTTP, normally port `80`
- HTTPS, normally port `443`

## Credentials

**Detection Summary**: No application credentials, passwords, API tokens, data bags, Chef Vault references, or secret-manager integrations were detected across the supplied cookbook analysis. Three locally generated TLS private keys and three locally generated self-signed certificates are security-sensitive artifacts.

**Source**:
  - **Provider**: None detected
  - **URL**: Not applicable
  - **Path**: Not applicable

### TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files
- **Usage context**: Private keys used by the three Nginx HTTPS virtual hosts
- **Permissions**: Mode `0640`
- **Ownership**: `root:ssl-cert`

### Self-Signed TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: TLS certificates for the three Nginx HTTPS virtual hosts
- **Validity**: 365 days, based on the analyzed OpenSSL command
- **Key type**: RSA 2048-bit, based on the analyzed OpenSSL command

No hardcoded passwords, data bags, encrypted data bags, Chef Vault items, Conjur variables, CyberArk data bags, or secret environment variables were identified.

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
- `/etc/nginx/sites-enabled/default` should be absent
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

- SSH: port `22`
- HTTP: port `80`
- HTTPS: port `443`
- Unix sockets: none specified
- Nginx bind address: not specified

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

`site.conf.erb` renders three times in total.

## Pre-flight checks:

```bash
# Security services
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# Fail2ban configuration
test -f /etc/fail2ban/jail.local
stat -c '%a %n' /etc/fail2ban/jail.local

# Firewall policy and allowed services
ufw status verbose
ufw status | grep -E '22|80|443'

# Nginx configuration
nginx -t
nginx -T

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/nginx/sites-available/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/nginx/sites-available/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/nginx/sites-available/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# Firewall and listening ports
ss -tlnp | grep ':22 '
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# SSL directories and group
ls -ld /etc/ssl/certs
ls -ld /etc/ssl/private
getent group ssl-cert
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# Sysctl configuration
test -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Service logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
journalctl -u ssh --no-pager -n 50
```

Expected validation results:

- `nginx -t` succeeds.
- `nginx` and `fail2ban` are enabled and active.
- SSH root login and password authentication are disabled.
- UFW denies inbound traffic by default and allows SSH, HTTP, and HTTPS.
- The three Nginx site configurations and enabled links exist.
- `/etc/nginx/sites-enabled/default` is absent.
- Each site document root contains its `index.html`.
- Each certificate and private key exists with the expected name.
- Each private key has ownership `root:ssl-cert` and mode `640`.
- `test.cluster.local` presents a certificate containing `CN=test.cluster.local`.
- `ci.cluster.local` presents a certificate containing `CN=ci.cluster.local`.
- `status.cluster.local` presents a certificate containing `CN=status.cluster.local`.
- HTTP port `80`, HTTPS port `443`, and SSH port `22` are listening as applicable.