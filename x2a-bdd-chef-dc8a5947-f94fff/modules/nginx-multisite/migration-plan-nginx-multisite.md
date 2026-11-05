---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook provisions Nginx with three HTTPS-enabled virtual hosts—**test.cluster.local**, **ci.cluster.local**, and **status.cluster.local**. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, SSH, kernel, and Fail2ban hardening; creates site document roots and index files; generates self-signed TLS certificates; renders and enables one Nginx virtual-host configuration per site; and removes the default Nginx site. The Ansible migration should preserve the execution order: security preparation, Nginx installation and base configuration, certificate generation, and virtual-host activation.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Key Config: Self-signed RSA 2048-bit certificate, valid for 365 days

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Key Config: Self-signed RSA 2048-bit certificate, valid for 365 days

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Key Config: Self-signed RSA 2048-bit certificate, valid for 365 days

**Security components**:

- **fail2ban**
  - Package: `fail2ban`
  - Service: `fail2ban`
  - State: Enabled and started

- **ufw**
  - Package: `ufw`
  - Policy: Default deny for incoming traffic
  - Allowed traffic: SSH, HTTP, and HTTPS
  - State: Enabled

- **ssh**
  - Root login: Disabled
  - Password authentication: Disabled
  - Service resource: Declared with action `nothing`; no restart or reload is shown

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

No concrete static file paths are listed in the supplied directory analysis. The `nginx.rb` recipe deploys an `index.html` through `cookbook_file`, but its source is dynamically constructed as `#{site_folder}/index.html`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Serves as the entry recipe.
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Resources used: four `include_recipe` resources.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Configures UFW in this order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Uses execute resources named `ufw_default_deny`, `ufw_allow_ssh`, `ufw_allow_http`, `ufw_allow_https`, and `ufw_enable`.
   - Declares `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf`; its action is `nothing`, and no notification or subscription is shown.
   - Disables SSH root login when `security.ssh.disable_root` is `true`:
     ```bash
     sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
     ```
   - Disables SSH password authentication when `security.ssh.password_auth` is `false`:
     ```bash
     sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
     ```
   - Declares `service[ssh]` with action `nothing`; no SSH restart or reload notification is shown.
   - Resource summary: one package collection resource, two service resources, two template resources, and eight execute resources.
   - Reported file modes are `0644` for `/etc/fail2ban/jail.local` and `/etc/sysctl.d/99-security.conf`; these mode details require source verification because they are not present in the structured execution metadata.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts `service[nginx]`.
   - Iterates over the following exact sites:
     - **test.cluster.local**
       - Creates `/opt/server/test`.
       - Deploys `/opt/server/test/index.html` using a `cookbook_file` source dynamically constructed as `#{site_folder}/index.html`.
       - Site setting: `ssl_enabled: true`.
     - **ci.cluster.local**
       - Creates `/opt/server/ci`.
       - Deploys `/opt/server/ci/index.html` using a `cookbook_file` source dynamically constructed as `#{site_folder}/index.html`.
       - Site setting: `ssl_enabled: true`.
     - **status.cluster.local**
       - Creates `/opt/server/status`.
       - Deploys `/opt/server/status/index.html` using a `cookbook_file` source dynamically constructed as `#{site_folder}/index.html`.
       - Site setting: `ssl_enabled: true`.
   - Resource summary: one package resource, two template resources, one service resource, three directory resources, and three `cookbook_file` resources.
   - Reported template modes and index-file modes are `0644`; these mode details require source verification because they are not present in the structured execution metadata.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private`.
   - Generates certificates only for sites with `ssl_enabled: true`. All three configured sites have SSL enabled:
     - **test.cluster.local**
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Private key: `/etc/ssl/private/test.cluster.local.key`
       - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
       - Generation command uses `openssl req -x509 -nodes -days 365 -newkey rsa:2048`.
       - Applies mode `0640` and ownership `root:ssl-cert` to the private key.
     - **ci.cluster.local**
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key: `/etc/ssl/private/ci.cluster.local.key`
       - Subject includes `CN=ci.cluster.local/emailAddress=admin@example.com`.
       - Generation command uses `openssl req -x509 -nodes -days 365 -newkey rsa:2048`.
       - Applies mode `0640` and ownership `root:ssl-cert` to the private key.
     - **status.cluster.local**
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Private key: `/etc/ssl/private/status.cluster.local.key`
       - Subject includes `CN=status.cluster.local/emailAddress=admin@example.com`.
       - Generation command uses `openssl req -x509 -nodes -days 365 -newkey rsa:2048`.
       - Applies mode `0640` and ownership `root:ssl-cert` to the private key.
   - Resource summary: one package collection resource, one group resource, two directory resources, and three execute resources.
   - The certificates are self-signed, RSA 2048-bit, valid for 365 days, and generated without a passphrase because `-nodes` is used.
   - Reported directory modes are `0755` for `/etc/ssl/certs` and `0710` for `/etc/ssl/private`; directory ownership details require source verification because they are not present in the structured execution metadata.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for each configured site.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` to the template.
   - **test.cluster.local**
     - Renders to `/etc/nginx/sites-available/test.cluster.local`.
     - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to the available-site configuration.
   - **ci.cluster.local**
     - Renders to `/etc/nginx/sites-available/ci.cluster.local`.
     - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to the available-site configuration.
   - **status.cluster.local**
     - Renders to `/etc/nginx/sites-available/status.cluster.local`.
     - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to the available-site configuration.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Resource summary: three template resources, three link resources, and one file resource.
   - No Nginx reload or restart notification is shown. The Ansible migration should add controlled `nginx -t` validation and a reload handler if operationally required.

## Dependencies

**External cookbook dependencies**: Not specified in the supplied structured analysis.

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
- `ufw`: enabled through `ufw --force enable`

## Credentials

**Detection Summary**: No application credentials, passwords, API keys, data bags, Chef Vault entries, CyberArk references, Conjur variables, or secret-manager integrations were detected. Three locally generated TLS private keys and three locally generated self-signed certificates were identified as sensitive TLS materials.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: None detected

### Self-signed TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files
- **Usage context**: Nginx TLS private keys
- **Permissions and ownership**: Mode `0640`, owner `root`, group `ssl-cert`

### TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated self-signed certificates
- **Usage context**: Nginx HTTPS virtual hosts
- **Certificate details**: RSA 2048-bit, valid for 365 days, subject email `admin@example.com`

No hardcoded passwords, tokens, database credentials, or API keys were identified.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
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
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` — must be absent

**Service endpoints to check**:

- HTTP: port `80`
- HTTPS: port `443`
- SSH: permitted by UFW; the cookbook does not change the SSH listening port
- Unix sockets: none specified
- Network interfaces: none specified

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

**Total template render operations**: 7

## Pre-flight checks:

```bash
# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban

# Confirm enabled services
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Nginx configuration validation
nginx -t

# Base configuration files
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf

# Security configuration
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# test.cluster.local files and endpoints
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: test.cluster.local' https://127.0.0.1/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%a %U:%G' /etc/ssl/private/test.cluster.local.key

# ci.cluster.local files and endpoints
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: ci.cluster.local' https://127.0.0.1/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%a %U:%G' /etc/ssl/private/ci.cluster.local.key

# status.cluster.local files and endpoints
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I -H 'Host: status.cluster.local' https://127.0.0.1/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%a %U:%G' /etc/ssl/private/status.cluster.local.key

# The default site must be removed
test ! -e /etc/nginx/sites-enabled/default

# Expected TLS private-key result
# mode should be 640 and ownership should be root:ssl-cert

# Firewall status
ufw status verbose
ufw status | grep -E '22|80|443'

# Expected firewall behavior
# Default policy should deny incoming traffic.
# SSH, HTTP, and HTTPS should be allowed.

# Fail2ban status
fail2ban-client status

# Apply and verify sysctl configuration
sysctl -p /etc/sysctl.d/99-security.conf

# Listening ports
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

The `cookbooks/nginx-multisite/attributes/default.rb` declarations should be independently verified during migration because the supplied structured analysis does not include a separate attributes-analysis section. Reported file modes and ownership for non-key resources should likewise be verified against the original cookbook source.