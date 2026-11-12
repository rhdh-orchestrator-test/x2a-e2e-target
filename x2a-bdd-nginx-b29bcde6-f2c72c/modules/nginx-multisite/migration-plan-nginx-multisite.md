---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and index files; generates self-signed RSA certificates and private keys; deploys Nginx configuration and enabled-site links; applies firewall, Fail2ban, sysctl, and SSH hardening settings; and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; available configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; available configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; available configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

**Security areas**:

- **fail2ban**: Enabled and started
- **ufw**: Configured with a default-deny incoming policy and enabled
- **ssh**: Runtime attributes indicate root login is disabled and password authentication is disabled. These values require confirmation from the cookbook attributes because the supplied attributes analysis is incomplete.

## File Structure

The following files are used by the execution tree and structured analysis.

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

No provider files or custom resources are used by the execution tree.

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

No static files under `files/` are listed in the supplied analysis. The `cookbook_file` resources deploy `index.html` files, but their source paths are dynamically constructed from the Chef expression `#{site_folder}/index.html`; no static source file paths were provided in the execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. `cookbooks/nginx-multisite/recipes/default.rb`
2. `cookbooks/nginx-multisite/recipes/security.rb`
3. `cookbooks/nginx-multisite/recipes/nginx.rb`
4. `cookbooks/nginx-multisite/recipes/ssl.rb`
5. `cookbooks/nginx-multisite/recipes/sites.rb`

### 1. Default entry recipe

**Recipe:** `cookbooks/nginx-multisite/recipes/default.rb`

- Includes `nginx-multisite::security`
- Includes `nginx-multisite::nginx`
- Includes `nginx-multisite::ssl`
- Includes `nginx-multisite::sites`
- Resources: four `include_recipe` declarations

The Ansible implementation must preserve this ordering.

### 2. Security configuration

**Recipe:** `cookbooks/nginx-multisite/recipes/security.rb`

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts the `fail2ban` service.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Executes the following UFW commands in order:
  1. `ufw --force default deny`
  2. `ufw allow ssh`
  3. `ufw allow http`
  4. `ufw allow https`
  5. `ufw --force enable`
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Declares `sysctl -p /etc/sysctl.d/99-security.conf` with action `nothing`; no invocation trigger is shown in the supplied execution tree. The migration should apply the sysctl settings after deployment unless strict behavioral compatibility requires retaining the inactive action.
- Runtime attribute values indicate `security.ssh.disable_root: true` and `security.ssh.password_auth: false`. Because the supplied attributes analysis is incomplete, these values must be confirmed before enabling the commands.
- When enabled by the runtime values, executes:
  - `sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config`
  - `sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config`
- Declares `service[sshd]` with action `nothing`; no restart or reload trigger is shown.
- Ansible must validate SSH configuration before reloading SSH.

### 3. Nginx installation and base configuration

**Recipe:** `cookbooks/nginx-multisite/recipes/nginx.rb`

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Enables and starts the `nginx` service.
- Iterates over the following sites:
  - **test.cluster.local**
    - Creates `/opt/server/test`
    - Deploys `/opt/server/test/index.html` from the dynamic source expression `#{site_folder}/index.html` with mode `0644`
  - **ci.cluster.local**
    - Creates `/opt/server/ci`
    - Deploys `/opt/server/ci/index.html` from the dynamic source expression `#{site_folder}/index.html` with mode `0644`
  - **status.cluster.local**
    - Creates `/opt/server/status`
    - Deploys `/opt/server/status/index.html` from the dynamic source expression `#{site_folder}/index.html` with mode `0644`

The site loop contains three directory resources and three `cookbook_file` resources. The supplied analysis does not conclusively provide the directory mode or ownership, so those properties must be confirmed before migration.

### 4. SSL package and certificate generation

**Recipe:** `cookbooks/nginx-multisite/recipes/ssl.rb`

- Installs `openssl` and `ca-certificates`.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` and `/etc/ssl/private`. The supplied execution tree does not confirm their modes, owners, or groups; these properties require verification.
- Iterates over the following sites:
  - **test.cluster.local**
    - Generates `/etc/ssl/private/test.cluster.local.key`
    - Generates `/etc/ssl/certs/test.cluster.local.crt`
    - Uses a self-signed RSA 2048-bit certificate valid for 365 days
    - Uses CN `test.cluster.local` and email `admin@example.com`
    - Sets the private key to mode `0640` and ownership `root:ssl-cert`
  - **ci.cluster.local**
    - Generates `/etc/ssl/private/ci.cluster.local.key`
    - Generates `/etc/ssl/certs/ci.cluster.local.crt`
    - Uses a self-signed RSA 2048-bit certificate valid for 365 days
    - Uses CN `ci.cluster.local` and email `admin@example.com`
    - Sets the private key to mode `0640` and ownership `root:ssl-cert`
  - **status.cluster.local**
    - Generates `/etc/ssl/private/status.cluster.local.key`
    - Generates `/etc/ssl/certs/status.cluster.local.crt`
    - Uses a self-signed RSA 2048-bit certificate valid for 365 days
    - Uses CN `status.cluster.local` and email `admin@example.com`
    - Sets the private key to mode `0640` and ownership `root:ssl-cert`

The certificate commands use `openssl req -x509 -nodes -days 365 -newkey rsa:2048`. The `-nodes` option creates unencrypted private keys without passphrases.

### 5. Nginx site configuration

**Recipe:** `cookbooks/nginx-multisite/recipes/sites.rb`

- Creates `/etc/nginx/sites-available`.
- Creates `/etc/nginx/sites-enabled`.
- The supplied analysis reports three directory resource executions resolving to these two unique paths. Confirm whether duplicate loop executions are retained in the migrated implementation.
- Iterates over the following sites:
  - **test.cluster.local**
    - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`
    - Uses `server_name: test.cluster.local`
    - Uses `document_root: /opt/server/test`
    - Uses `ssl_enabled: true`
    - Uses certificate `/etc/ssl/certs/test.cluster.local.crt`
    - Uses private key `/etc/ssl/private/test.cluster.local.key`
    - Creates `/etc/nginx/sites-enabled/test.cluster.local` linked to the available-site configuration
  - **ci.cluster.local**
    - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`
    - Uses `server_name: ci.cluster.local`
    - Uses `document_root: /opt/server/ci`
    - Uses `ssl_enabled: true`
    - Uses certificate `/etc/ssl/certs/ci.cluster.local.crt`
    - Uses private key `/etc/ssl/private/ci.cluster.local.key`
    - Creates `/etc/nginx/sites-enabled/ci.cluster.local` linked to the available-site configuration
  - **status.cluster.local**
    - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`
    - Uses `server_name: status.cluster.local`
    - Uses `document_root: /opt/server/status`
    - Uses `ssl_enabled: true`
    - Uses certificate `/etc/ssl/certs/status.cluster.local.crt`
    - Uses private key `/etc/ssl/private/status.cluster.local.key`
    - Creates `/etc/nginx/sites-enabled/status.cluster.local` linked to the available-site configuration
- Deletes `/etc/nginx/sites-enabled/default`.

## Dependencies

**External cookbook dependencies**: None specified in the supplied metadata analysis.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: declared with action `nothing`
- UFW: enabled through `ufw --force enable`

**Custom resources/providers**: None.

## Credentials

**Detection Summary**: No externally stored credentials, passwords, API tokens, data bags, Chef Vault items, CyberArk references, Conjur variables, or secret-manager integrations were detected. Three locally generated TLS private keys are sensitive artifacts and must be protected during migration.

**Source**:

- **Provider**: None detected
- **URL**: None detected
- **Path**: None detected

### TLS Private Keys

- **Variable(s):**
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s):** `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage:** Locally generated files; not stored in a data bag, vault, or external secret manager
- **Usage context:** TLS private keys for the three Nginx HTTPS virtual hosts
- **Permissions:** Mode `0640`, ownership `root:ssl-cert`

### TLS Certificates

- **Variable(s):**
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s):**
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage:** Locally generated self-signed certificate files
- **Usage context:** TLS certificates referenced by the Nginx site configurations
- **Validity:** 365 days
- **Certificate type:** Self-signed RSA 2048-bit certificates

The subject email address `admin@example.com` is embedded in the OpenSSL command but is not a password, token, or other credential.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/etc/nginx/sites-enabled/default
/etc/sysctl.d/99-security.conf
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/private/status.cluster.local.key
/opt/server/test/index.html
/opt/server/ci/index.html
/opt/server/status/index.html
```

Expected state:

- `/etc/nginx/sites-enabled/default` does not exist.
- Each enabled-site path links to its corresponding available-site file.
- `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status` exist.
- Private keys have mode `0640` and ownership `root:ssl-cert`.
- Certificate files exist under `/etc/ssl/certs`.

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

## Pre-flight checks:

```bash
# Confirm required packages
dpkg -l fail2ban ufw nginx openssl ca-certificates

# Security services and firewall
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
ufw status verbose
ufw status numbered

# Expected:
# - Default incoming policy is deny
# - SSH is allowed
# - HTTP is allowed
# - HTTPS is allowed
# - UFW is enabled

# SSH configuration validation
sshd -t
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Expected:
# permitrootlogin no
# passwordauthentication no

# Sysctl configuration
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Nginx service and syntax
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
nginx -T

# Expected:
# syntax is ok
# test is successful

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
stat -c '%A %U:%G %n' /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
grep -E 'server_name|root' /etc/nginx/sites-available/test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
stat -c '%A %U:%G %n' /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
grep -E 'server_name|root' /etc/nginx/sites-available/ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
stat -c '%A %U:%G %n' /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
grep -E 'server_name|root' /etc/nginx/sites-available/status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Network listeners
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
test -f /var/log/nginx/access.log
test -f /var/log/nginx/error.log
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
```

Expected TLS state for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`:

- Private key mode `0640`
- Private key ownership `root:ssl-cert`
- RSA 2048-bit certificate
- Self-signed issuer
- Approximately 365-day validity
- Common Name matching the corresponding hostname
- HTTP available on port `80`
- HTTPS available on port `443`
- Response content served from the corresponding document root

Before endpoint checks, ensure the local resolver or `/etc/hosts` maps all three hostnames to the migrated server.