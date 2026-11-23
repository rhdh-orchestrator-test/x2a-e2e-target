---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with dynamically defined virtual hosts sourced from the `nginx_sites` Chef data bag. It installs nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies SSH and kernel security hardening; optionally generates self-signed TLS certificates; deploys site content and virtual-host configurations; and creates HTTP, HTTPS, firewall, logging, and security-header configuration. The execution order is `security`, `nginx`, `ssl`, and `sites`. The supplied analysis does not expose the actual `nginx_sites` item names or values, so site-specific Ansible tasks cannot be expanded until the Chef data bag is exported.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

No exact site instance names are available in the supplied analysis. Site instances are dynamically read from the `nginx_sites` data bag by the `nginx`, `ssl`, and `sites` recipes. Do not invent site names. Export the data bag before implementation and create one explicit Ansible site entry per item containing:

- `site_name`: data-bag item `id`
- `document_root`: `config['document_root']`
- `ssl_enabled`: `config['ssl_enabled']`
- `site_folder`: first component of `site_name.split('.')`, used for static content lookup

### Shared nginx configuration

- HTTP listener: TCP port `80`
- HTTPS listener: TCP port `443` for SSL-enabled sites
- Main configuration: `/etc/nginx/nginx.conf`
- Security configuration: `/etc/nginx/conf.d/security.conf`
- Available sites: `/etc/nginx/sites-available/<site_name>`
- Enabled site links: `/etc/nginx/sites-enabled/<site_name>`
- Site document roots: data-bag `document_root`
- Certificate directory: `/etc/ssl/certs`
- Private-key directory: `/etc/ssl/private`
- Site token: `/etc/nginx/secrets/site_token`

### Security instances

- **fail2ban**
  - Package: `fail2ban`
  - Service: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Enabled and started
- **ufw**
  - Package: `ufw`
  - Default incoming policy: deny
  - Allowed services: SSH, HTTP, and HTTPS
  - Firewall enabled
- **ssh**
  - Root login disabled
  - Password authentication disabled
  - Service resource: `sshd`
  - Configuration: `/etc/ssh/sshd_config`

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

No static `files/default/*` or `files/*` files were listed. The `cookbook_file` resource references dynamic `index.html` sources that must be located and migrated separately.

## Module Explanation

The cookbook performs operations in this order.

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Ansible task files must preserve this order.
   - Resources: four `include_recipe` declarations.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Applies UFW default-deny policy.
   - Allows SSH, HTTP TCP port `80`, and HTTPS TCP port `443`.
   - Enables UFW only after the SSH rule is present.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` after the sysctl file changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` only when SSH configuration changes.
   - The security execute-resource count is **8**: five UFW commands, one sysctl reload command, and two SSH hardening commands.
   - `service[sshd]` is a separate service resource with action `nothing`.
   - The `enabled` attributes for Fail2ban and UFW are defined but are not used as conditionals in the shown recipes; preserve the unconditional recipe behavior.
   - Template directive values and notification behavior require verification against the actual ERB source before migration because the supplied structured analysis identifies the templates but does not independently expose their contents.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads the encrypted data-bag item `nginx_secrets/site` through `Chef::EncryptedDataBagItem`.
   - Writes the token to `/etc/nginx/secrets/site_token`; the field name, permissions, and sensitivity settings require verification against the recipe source.
   - Reads site entries from the `nginx_sites` data bag.
   - For every exported site item, creates its configured document root with owner `nginx`, group `nginx`, and mode `0755`.
   - Derives the static content source directory from the first component of the site name.
   - Deploys the corresponding `index.html` to `<document_root>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - Dynamic loop expansion is pending because the supplied analysis contains no actual site item names.
   - Resources: one package, two templates, one service, one fixed directory, one secret file, one dynamic directory per site, and one dynamic `cookbook_file` per site.
   - Main nginx and security-template directives require source verification before being treated as confirmed migration requirements.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Reads SSL settings from the `nginx_sites` data bag.
   - For each exported site whose `ssl_enabled` value is true, generates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Uses a local self-signed RSA certificate generation command with 365-day validity; exact command parameters require verification against the recipe source.
   - Sets generated private keys to owner `root`, group `ssl-cert`, and mode `0640`.
   - Skips certificate generation when both certificate and key already exist.
   - A generated certificate or key triggers a delayed nginx reload.
   - Dynamic certificate names cannot be expanded until the actual data-bag site names are obtained.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` for every exported site item.
   - Uses the site name, document root, SSL flag, certificate path, and private-key path as template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symbolic link to the available-site configuration.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Site-template directives, redirects, TLS settings, headers, logging, and reload notifications require verification against the actual ERB source.
   - Dynamic template and link expansion is pending the actual `nginx_sites` item names.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: restarted only when SSH hardening changes
- UFW: enabled through command execution

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

Validate package names, service names, SSH service naming, firewall implementation, and nginx site-directory behavior on every target platform. The cookbook uses UFW commands and Debian-style nginx site directories despite declaring CentOS support.

## Credentials

**Detection Summary**: 1 data-bag credential detected, referenced from 1 recipe and written to 1 protected file. Locally generated TLS private keys are also sensitive material but are not retrieved from a credential provider.

**Source**:
  - **Provider**: Chef encrypted data bag via `Chef::EncryptedDataBagItem`
  - **URL**: Not applicable
  - **Path**: Data bag `nginx_secrets`, item `site`

### Nginx Site Token

- **Variable**: `site_secret['token']`; field name requires verification against `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Source provider**: Chef encrypted data bag via `Chef::EncryptedDataBagItem`
- **Source**: Data bag `nginx_secrets`, item `site`
- **Destination**: `/etc/nginx/secrets/site_token`
- **Destination permissions**: Verify owner, group, mode, and `sensitive` setting against the recipe source
- **Usage context**: Secret token file for nginx or site configuration
- **Ansible migration**: Store the token in Ansible Vault or an approved AAP credential integration. Do not place cleartext in inventory, defaults, templates, or source control.

### TLS Private Keys

- **Variable(s)**: Dynamic site-specific certificate and key paths
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files
- **Certificate path**: `/etc/ssl/certs/<site_name>.crt`
- **Private-key path**: `/etc/ssl/private/<site_name>.key`
- **Generation method**: Local `openssl req -x509` command; parameters require source verification
- **Usage context**: nginx HTTPS virtual hosts
- **Private-key permissions**: Expected `root:ssl-cert` with mode `0640`; verify against the recipe

No HashiCorp Vault, CyberArk, AWS Secrets Manager, `chef_vault_item`, Conjur, or environment-variable secret references were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets`
- `/etc/nginx/secrets/site_token`
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-enabled/default` must be absent
- `/etc/ssl/certs/<site_name>.crt` for every exported SSL-enabled site
- `/etc/ssl/private/<site_name>.key` for every exported SSL-enabled site
- `<document_root>/index.html` for every exported site
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/<site_name>_access.log`
- `/var/log/nginx/<site_name>_error.log`

**Service endpoints to check**:

- TCP port `80`
- TCP port `443` for SSL-enabled sites
- SSH TCP port `22`
- UFW TCP ports `22`, `80`, and `443`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: one render per exported `nginx_sites` item

Exact site-specific file paths, endpoints, and individual checks cannot be enumerated until the data-bag item names and values are supplied.

## Pre-flight checks

```bash
# Package checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service checks
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban
systemctl is-active nginx
systemctl is-active fail2ban
systemctl status sshd 2>/dev/null || systemctl status ssh

# nginx validation
nginx -t
ls -la /etc/nginx/sites-available
ls -la /etc/nginx/sites-enabled
test ! -e /etc/nginx/sites-enabled/default

# Firewall validation
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
ufw status | grep -q 'Default: deny'

# Fail2ban validation
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Kernel security validation
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# SSH validation
grep -E '^PermitRootLogin no$|^PasswordAuthentication no$' \
  /etc/ssh/sshd_config
sshd -t

# Secret-file validation without displaying contents
stat -c '%U %G %a %n' /etc/nginx/secrets
stat -c '%U %G %a %n' /etc/nginx/secrets/site_token

# TLS and listener validation
ss -tlnp | grep -E ':80|:443'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Service logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
```

After exporting the `nginx_sites` data bag, run a separate named validation block for every actual site item:

```bash
# Replace placeholders with the exported site's actual values.
test -d <document_root>
test -f <document_root>/index.html
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
test -f /var/log/nginx/<site_name>_access.log
test -f /var/log/nginx/<site_name>_error.log
```

For every exported SSL-enabled site:

```bash
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key

openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -checkend 2592000
stat -c '%U %G %a %n' /etc/ssl/private/<site_name>.key

curl -I --resolve <site_name>:80:127.0.0.1 \
  http://<site_name>/

curl -k -I --resolve <site_name>:443:127.0.0.1 \
  https://<site_name>/
```

For every exported non-SSL site:

```bash
curl -I --resolve <site_name>:80:127.0.0.1 \
  http://<site_name>/
```

Before implementation, obtain and record:

- Every `nginx_sites` data-bag item name
- Every site `id` and hostname
- Every `document_root`
- Every `ssl_enabled` value
- Every required static `<site_folder>/index.html`
- The encrypted `nginx_secrets/site` token
- Source verification for all ERB template directives
- Source verification for the token field, permissions, and sensitivity settings

