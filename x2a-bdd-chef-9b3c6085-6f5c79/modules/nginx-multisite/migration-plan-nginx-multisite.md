---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a multi-site web server and applies host security controls, including Fail2ban, UFW, SSH hardening, sysctl settings, global nginx configuration, optional self-signed TLS certificates, and virtual-host configuration. The entry recipe executes `security`, `nginx`, `ssl`, and `sites` in that order. The supplied analysis does not expose the names or values of the `nginx_sites` data bag items, so no site instances can be enumerated accurately; those records must be supplied and explicitly defined before migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

No nginx site instance names were exposed by the supplied analysis. The actual `nginx_sites` data bag records must be provided before implementation. Do not invent site names.

**Primary service**: `nginx`

- Location/Path: `/etc/nginx`
- PID: `/run/nginx.pid`
- HTTP endpoint: TCP `80`
- HTTPS endpoint: TCP `443` when an SSL-enabled site exists
- Access log: `/var/log/nginx/access.log`
- Error log: `/var/log/nginx/error.log`

**Security components**:

- **fail2ban**
  - Package: `fail2ban`
  - Service: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Action: enabled and started
  - Configuration changes trigger a delayed service restart

- **ufw**
  - Package: `ufw`
  - Default policy: deny
  - Allowed services: SSH, HTTP, and HTTPS
  - Activation command: `ufw --force enable`

- **ssh**
  - Configuration: `/etc/ssh/sshd_config`
  - Root login: disabled when `security.ssh.disable_root` is `true`
  - Password authentication: disabled when `security.ssh.password_auth` is `false`
  - Service: `sshd`
  - Action: delayed restart only when SSH hardening changes the configuration

**Analyzed security components**:

- `fail2ban`
- `ufw`
- `ssh`

These are represented as separate resources and conditional blocks, not as a Chef iteration over a security collection.

**Site instance schema requiring source validation**:

The execution tree confirms iteration over `data_bag('nginx_sites')`, but does not validate the fields or meanings below. Confirm them against the Chef recipes before migration:

- `id`: expected site/server name
- `document_root`: expected nginx document root
- `ssl_enabled`: expected TLS enablement flag

Expected per-site paths, subject to source validation:

- Document root: `<document_root>`
- Index file: `<document_root>/index.html`
- Site configuration: `/etc/nginx/sites-available/<site_name>`
- Enabled-site link: `/etc/nginx/sites-enabled/<site_name>`
- Certificate when TLS is enabled: `/etc/ssl/certs/<site_name>.crt`
- Private key when TLS is enabled: `/etc/ssl/private/<site_name>.key`

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

No provider is used by the execution tree. The structural analysis mentions `resources/lineinfile.rb`, but it is not executed or referenced in the supplied execution tree and is excluded.

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

No static file path under `files/` was supplied. The `nginx.rb` recipe references dynamic `cookbook_file` sources such as `<site_folder>/index.html`, but corresponding static file paths are not present in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserve this execution order in Ansible.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Deploys `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures Fail2ban through the rendered template; jail names, retry limits, and log paths require verification against the source template.
   - Configures UFW with a default deny policy.
   - Allows SSH on TCP `22`, HTTP on TCP `80`, and HTTPS on TCP `443`.
   - Enables UFW with `ufw --force enable`.
   - Deploys `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` only after the sysctl template changes.
   - Changes `PermitRootLogin` to `no` when root-login hardening is enabled.
   - Changes `PasswordAuthentication` to `no` when password authentication is disabled.
   - Restarts `sshd` through delayed notifications when SSH configuration changes.
   - Use Ansible handlers for Fail2ban restart, sysctl reload, and SSH restart.
   - Template contents and exact sysctl values require source-template verification.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Deploys `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Deploys `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads encrypted Chef data bag item `nginx_secrets/site`.
   - Writes the `token` value to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`.
   - Iterates over `data_bag('nginx_sites')`; actual item names are unavailable and must be supplied explicitly.
   - Creates each validated site document root with owner `nginx`, group `nginx`, and mode `0755`.
   - Calculates the static content source directory from the first component of the site name.
   - Deploys the corresponding `index.html` file with owner `nginx`, group `nginx`, and mode `0644`.
   - Global template contents, including worker, logging, gzip, and include settings, require source-template verification.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Iterates over `data_bag('nginx_sites')` and processes only records whose validated `ssl_enabled` value is true.
   - Actual SSL-enabled site names are unavailable and must be supplied explicitly.
   - Generates a 365-day, 2048-bit RSA self-signed certificate and key for each validated SSL-enabled site.
   - Writes certificates to `/etc/ssl/certs/<site_name>.crt`.
   - Writes keys to `/etc/ssl/private/<site_name>.key`.
   - Changes private-key ownership to `root:ssl-cert` and mode to `0640`.
   - Does not regenerate certificates when both certificate and key already exist.
   - Notifies nginx for a delayed reload after certificate generation.
   - Self-signed certificate behavior requires confirmation as an intentional migration requirement.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Iterates over `data_bag('nginx_sites')`; actual site names are unavailable and must be supplied explicitly.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>`.
   - Creates `/etc/nginx/sites-enabled/<site_name>` pointing to `/etc/nginx/sites-available/<site_name>`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Reloads nginx after site configuration, link, or default-site changes.
   - Template behavior, including HTTP/HTTPS listeners, redirects, TLS settings, headers, logs, and security rules, requires source-template verification.

## Dependencies

**External cookbook dependencies**: None declared in the supplied `metadata.rb`; metadata analysis was not included and this must be verified.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

These package resources are confirmed by the execution analysis.

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd` — notification target only; no unconditional start or enable action

**External data sources**:

- Chef encrypted data bag: `nginx_secrets`, item `site`
- Chef data bag: `nginx_sites`

**Platform support**: Ubuntu `>= 18.04` and CentOS `>= 7.0` were stated in the original plan but are not validated by the supplied analysis. Confirm them from `metadata.rb`.

## Credentials

**Detection Summary**: 1 encrypted data-bag credential detected, plus dynamically generated TLS private keys. Site configuration data is loaded from a Chef data bag.

**Source**:

- **Provider**: Chef encrypted data bag
- **URL**: None detected
- **Path**: `nginx_secrets` data bag, item `site`

### nginx site token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag loaded with `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`
- **Destination**: `/etc/nginx/secrets/site_token`
- **File permissions**: owner `root`, group `root`, mode `0600`
- **Usage context**: written to `/etc/nginx/secrets/site_token` for local consumption
- **Ansible migration**: store in Ansible Vault or an approved AAP credential/secret system; do not place it in plaintext inventory or ordinary vars files.

### TLS private keys

- **Paths**: `/etc/ssl/private/<site_name>.key`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: generated on the target host by `openssl`
- **Permissions**: owner `root`, group `ssl-cert`, mode `0640`
- **Usage context**: nginx HTTPS configuration
- **Validity**: associated self-signed certificate is generated for 365 days
- **Ansible migration**: use `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate`, or preserve the shell command only when exact compatibility is required.

### TLS certificates

- **Paths**: `/etc/ssl/certs/<site_name>.crt`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: generated on the target host by `openssl`
- **Usage context**: nginx HTTPS configuration
- **Certificate subject**: the generated command specifies `CN=<site_name>` and example organization fields.
- **Ansible migration**: replace with managed certificate material or an ACME workflow for production use unless self-signed certificates are intentional.

### Site definitions

- **Variables**: Site fields are stated as `id`, `document_root`, and `ssl_enabled`, but their usage requires validation against the Chef source.
- **Source files**:
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Chef data bag `nginx_sites`
- **Usage context**: site names, document roots, static content, certificate generation decisions, and nginx site configuration, subject to source validation
- **Ansible migration**: convert every actual data bag item into an explicitly named `nginx_sites` variable entry.

No HashiCorp Vault, CyberArk, AWS Secrets Manager, environment-variable secrets, hardcoded API keys, database credentials, or embedded database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-enabled/default` — must be absent
- `/etc/ssl/certs`
- `/etc/ssl/private`

Site-specific paths cannot be listed until the actual `nginx_sites` records are supplied:

- `<document_root>`
- `<document_root>/index.html`
- `/etc/nginx/sites-available/<site_name>`
- `/etc/nginx/sites-enabled/<site_name>`
- `/etc/ssl/certs/<site_name>.crt`
- `/etc/ssl/private/<site_name>.key`

**Service endpoints to check**:

- TCP `80`: nginx HTTP
- TCP `443`: nginx HTTPS when an SSL-enabled site exists
- TCP `22`: SSH firewall allowance
- `/run/nginx.pid`: nginx PID file

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: one render per supplied `nginx_sites` record

## Pre-flight checks:

No named nginx site instances are available for individual site checks. Populate `nginx_sites` with the exact data bag records before running the site-specific commands.

```bash
# Package checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service checks
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# Configuration validation
nginx -t
nginx -T | grep -E \
  'include /etc/nginx/(conf.d|sites-enabled)|worker_processes|worker_connections|gzip'

# Security configuration
cat /etc/fail2ban/jail.local
fail2ban-client status
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# Kernel configuration
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# Network listeners
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
ss -tlnp | grep ':22 '

# Service endpoints
curl -I http://127.0.0.1/
curl -k -I https://127.0.0.1/

# Secret metadata; do not print the token
test -f /etc/nginx/secrets/site_token
stat -c '%U %G %a %n' /etc/nginx/secrets/site_token

# nginx reload and enablement
systemctl reload nginx
systemctl is-active nginx
systemctl is-enabled nginx
```

Expected results:

- `nginx -t` reports a successful syntax check.
- nginx is active and enabled.
- Fail2ban is active.
- UFW is active with a default deny policy.
- TCP ports `22`, `80`, and `443` are allowed.
- SSH contains `PermitRootLogin no` and `PasswordAuthentication no` when the corresponding settings are enabled.
- nginx listens on TCP port `80`.
- nginx listens on TCP port `443` when at least one validated site has TLS enabled.
- `/etc/nginx/secrets/site_token` is owned by `root:root` with mode `0600`.
- The nginx default site is absent.

After actual site names and document roots are supplied, run these checks separately for every named site.

```bash
# Replace placeholders with an actual validated site record.
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
test -d <document_root>
test -f <document_root>/index.html

# Required only when the validated site has ssl_enabled=true.
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 \
  https://<site_name>/

# Required for all named sites.
curl -I -H 'Host: <site_name>' http://127.0.0.1/
ls -l /var/log/nginx/<site_name>_access.log
ls -l /var/log/nginx/<site_name>_error.log
```

Run the Ansible playbook a second time and verify that:

- Existing certificates are not regenerated.
- Existing UFW rules are not duplicated.
- nginx reloads only when configuration changes.
- Fail2ban restarts only when `/etc/fail2ban/jail.local` changes.
- SSH restarts only when `/etc/ssh/sshd_config` changes.
- The nginx default site remains absent.
