---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an Nginx multi-site web server on Ubuntu `>= 18.04` or CentOS `>= 7.0`. The default recipe executes `security`, `nginx`, `ssl`, and `sites` in that order. It installs and hardens Nginx, configures Fail2ban and UFW, applies kernel and SSH hardening, creates per-site document roots and virtual hosts, and generates self-signed certificates for SSL-enabled sites. Site names and values are loaded dynamically from the `nginx_sites` Chef data bag; the supplied analysis does not expose the data bag item names, so those names and values require verification before migration.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **nginx**
  - Purpose: Main multi-site web server.
  - Package: `nginx`
  - Configuration: `/etc/nginx/nginx.conf`
  - Security configuration: `/etc/nginx/conf.d/security.conf`
  - Site configuration directory: `/etc/nginx/sites-available`
  - Enabled-site directory: `/etc/nginx/sites-enabled`
  - HTTP port: `80`
  - HTTPS port: `443`
  - Access log: `/var/log/nginx/access.log`
  - Error log: `/var/log/nginx/error.log`
  - Per-site access log: `/var/log/nginx/<site_name>_access.log`
  - Per-site error log: `/var/log/nginx/<site_name>_error.log`
  - Worker user: `nginx`

- **fail2ban**
  - Purpose: Protect SSH and Nginx endpoints from repeated authentication, request, and bot activity.
  - Service: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Action: Enabled and started.
  - Restart behavior: Restarted after the Fail2ban template changes.

- **ufw**
  - Purpose: Host firewall.
  - Package: `ufw`
  - Required policy: Default incoming deny.
  - Allowed ports: SSH `22`, HTTP `80`, HTTPS `443`.
  - Action: Enabled.

- **sshd**
  - Purpose: SSH daemon subject to hardening.
  - Configuration: `/etc/ssh/sshd_config`
  - Required settings: `PermitRootLogin no` and `PasswordAuthentication no`.
  - Action: Restarted only when SSH configuration changes.
  - Service name: `sshd` in Chef; Ubuntu commonly uses `ssh`.

- **Runtime sites from `nginx_sites`**
  - Purpose: Individual Nginx virtual hosts.
  - Exact instance names: Not exposed by the supplied analysis.
  - Required data bag attributes:
    - `id`
    - `document_root`
    - `ssl_enabled`
  - Per-site resources:
    - Document-root directory.
    - Static `index.html`.
    - Configuration under `/etc/nginx/sites-available/<site_name>`.
    - Symlink under `/etc/nginx/sites-enabled/<site_name>`.
    - Certificate and private key when `ssl_enabled` is `true`.
  - Migration requirement: Export the Chef data bag items into an Ansible variable such as `nginx_sites`, preserving the original values. Do not invent site names.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No statically named files are listed in the supplied cookbook directory. The `nginx.rb` recipe references dynamic `cookbook_file` sources using:

```text
#{site_folder}/index.html
```

The source filenames depend on the runtime `nginx_sites` data bag contents and require verification before implementation.

## Module Explanation

The cookbook performs operations in this order:

1. `nginx-multisite::default` (`cookbooks/nginx-multisite/recipes/default.rb`)
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - Execution order must be preserved.

2. `nginx-multisite::security` (`cookbooks/nginx-multisite/recipes/security.rb`)
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures UFW with default incoming policy `deny`, and allows SSH, HTTP, and HTTPS.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies the sysctl file when changed.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts the SSH service only when either SSH setting changes.
   - Uses 8 execute resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`
   - The execution tree confirms the `fail2ban`, `ufw`, and `ssh` security groups, but the supplied structured analysis does not confirm the values in `attributes/default.rb`. Verify those values before migration.
   - The listed Fail2ban and sysctl directives are implementation requirements from the original plan; template contents require source verification.

3. `nginx-multisite::nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` owned by `root:root` with mode `0700`.
   - Writes the site token to `/etc/nginx/secrets/site_token` with ownership `root:root` and mode `0600`.
   - Creates runtime document roots owned by `nginx:nginx` with mode `0755`.
   - Derives the static-file source directory using:
     ```ruby
     site_name.split('.').first
     ```
   - Deploys one dynamic `index.html` per runtime `nginx_sites` item with ownership `nginx:nginx` and mode `0644`.
   - The main and security Nginx templates each render once.
   - The dynamic `index.html` deployment renders once per runtime site item.
   - The detailed directives listed in the original plan require verification against the actual template files.

4. `nginx-multisite::ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Processes runtime `nginx_sites` items whose `ssl_enabled` value is `true`.
   - Creates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Uses the planned self-signed certificate parameters:
     - RSA `2048`
     - Validity `365` days
     - No passphrase
     - Subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Skips certificate generation when both files already exist.
   - Reloads Nginx after certificate creation.
   - The exact site names and SSL values require verification.

5. `nginx-multisite::sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)
   - Creates `/etc/nginx/sites-available` owned by `root:root` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` owned by `root:root` with mode `0755`.
   - These are the two statically known loop items:
     - `/etc/nginx/sites-available`
     - `/etc/nginx/sites-enabled`
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for every runtime site item to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a link to the corresponding available-site configuration.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Reloads Nginx after site configuration, link, or default-site changes.
   - The site template render count is one per runtime `nginx_sites` item.
   - The detailed virtual-host directives in the original plan require verification against `site.conf.erb`.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: Enabled and started; restarted after jail configuration changes.
- `nginx`: Enabled and started; reloaded after configuration, site, link, or certificate changes.
- `sshd` or `ssh`: Not enabled or started by this cookbook; restarted after SSH hardening changes.
- UFW: Enabled through the firewall configuration tasks.

## Credentials

**Detection Summary**: 1 credential reference requires source verification across 1 recipe and 1 generated file.

**Source**:

- **Provider**: Chef encrypted data bag, requiring verification against the source recipe
- **URL**: Not detected
- **Path**: Data bag `nginx_secrets`, item `site`, field `token`

### Nginx site token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Reported as a Chef encrypted data bag
- **Data bag reference requiring verification**:
  ```ruby
  Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')
  ```
- **Destination**: `/etc/nginx/secrets/site_token`
- **Permissions**: `root:root`, mode `0600`
- **Usage context**: A secret token stored on the Nginx host. The supplied plan does not show it being consumed by Nginx templates or command resources.
- **Migration storage**: Ansible Vault, an Ansible Automation Platform credential, or an external secret manager.
- **Migration handling**: Write the file with `no_log: true`; never place the plaintext token in an ordinary variable file or task output.

TLS private keys are generated locally as self-signed keys and are not imported credentials.

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-enabled/default` — must be absent
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- Runtime document roots from `nginx_sites`
- Runtime site `index.html` files
- `/etc/ssl/certs/<site_name>.crt` for SSL-enabled runtime sites
- `/etc/ssl/private/<site_name>.key` for SSL-enabled runtime sites

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`

**Unix sockets**: None configured by this cookbook.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 time
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 time
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 time
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 time
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: 1 time per runtime `nginx_sites` item
- Dynamic `index.html`: 1 deployment per runtime `nginx_sites` item

## Pre-flight checks:

```bash
# Package checks
dpkg-query -W nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service checks
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl status nginx
systemctl status fail2ban

# Use sshd on systems that provide that service name.
systemctl status sshd 2>/dev/null || systemctl status ssh

# Nginx configuration
nginx -t
nginx -T | grep -E 'listen (80|443)|server_name|ssl_certificate|ssl_certificate_key'
grep -E 'worker_processes|worker_connections|access_log|error_log|gzip|sites-enabled|conf.d' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Endpoint checks
ss -tlnp | grep -E ':(22|80|443)\b'
curl -I http://127.0.0.1/
curl -k -I https://127.0.0.1/

# Individual runtime site checks.
# Replace <site_name> and <document_root> with every verified nginx_sites item.
curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
test -f <document_root>/index.html
test -f /var/log/nginx/<site_name>_access.log
test -f /var/log/nginx/<site_name>_error.log

# SSL-enabled runtime site checks.
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Secret file
test -f /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token
# Do not print the token contents.

# Fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime|findtime|maxretry|backend|enabled|port|logpath' \
  /etc/fail2ban/jail.local

# UFW
ufw status verbose
ufw status numbered

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries

grep -E 'rp_filter|accept_redirects|send_redirects|accept_source_route|log_martians|icmp_echo|disable_ipv6|tcp_syncookies|tcp_max_syn_backlog|tcp_synack_retries|tcp_syn_retries' \
  /etc/sysctl.d/99-security.conf

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

Expected results include:

- Nginx is enabled, active, and passes `nginx -t`.
- Fail2ban is enabled and active.
- UFW is active with default incoming deny and ports `22`, `80`, and `443` allowed.
- The default Nginx site is absent.
- Every verified runtime site has its available configuration, enabled-site link, document-root index, and site-specific logs.
- SSL-enabled sites redirect HTTP to HTTPS and present their generated certificate over HTTPS.
- SSL private keys have ownership `root:ssl-cert` and mode `0640`.
- The site token has ownership `root:root` and mode `0600`.
- SSH reports `permitrootlogin no` and `passwordauthentication no`.
- Nginx, Fail2ban, UFW, SSH, TLS, and document-root logs contain no configuration or permission errors.