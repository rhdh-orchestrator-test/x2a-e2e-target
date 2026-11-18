---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with data-bag-defined sites, optional self-signed TLS certificates, HTTP-to-HTTPS redirects, security headers, rate limiting, fail2ban, UFW rules, SSH hardening, and kernel network-security settings. The entry recipe executes `security`, `nginx`, `ssl`, and `sites` in that order. The supplied analysis does not contain the actual `nginx_sites` data bag item names or values, so those items must be collected before site-specific Ansible tasks, inventory, and validation commands can be finalized.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Web server and TLS termination
  - Location/Path: `/etc/nginx/nginx.conf`
  - Port/Socket: TCP `80`, TCP `443`
  - Key Config: Worker user `nginx`, worker connections `768`, gzip enabled, security configuration at `/etc/nginx/conf.d/security.conf`, sites loaded from `/etc/nginx/sites-enabled/*`

- **fail2ban**: Intrusion prevention for SSH and nginx
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: SSH, HTTP, and HTTPS jails
  - Key Config: SSH, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails; default ban time `3600`; find time `600`

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, TCP `80`, and TCP `443`
  - Key Config: Default incoming policy `deny`; firewall enabled

- **sshd**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`

- **nginx_sites data bag collection**: Site definitions
  - Location/Path: Chef data bag `nginx_sites`
  - Port/Socket: Site-specific HTTP and optional HTTPS listeners
  - Key Config: Actual item names and values were not included in the supplied analysis. Required fields are `id`, `document_root`, and `ssl_enabled`.

### Site-specific values requiring collection

The following exact site instances must be obtained from the Chef `nginx_sites` data bag before migration:

- Data bag item name
- `id`, used as `site_name`
- `document_root`
- `ssl_enabled`
- Certificate path
- Private-key path
- Index source directory, calculated from the first component of `site_name`

The supplied analysis does not provide actual site names. No site names or values are invented in this plan.

Default site paths are:

- Document root: `document_root`
- Site configuration: `/etc/nginx/sites-available/<site_name>`
- Enabled-site symlink: `/etc/nginx/sites-enabled/<site_name>`
- Certificate: `/etc/ssl/certs/<site_name>.crt`
- Private key: `/etc/ssl/private/<site_name>.key`
- Access log: `/var/log/nginx/<site_name>_access.log`
- Error log: `/var/log/nginx/<site_name>_error.log`

Default SSL directories:

- Certificates: `/etc/ssl/certs`
- Private keys: `/etc/ssl/private`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

### Recipes

```text
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

### Providers

```text
```

No provider file is used by the execution tree.

### Templates

```text
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb
```

### Attributes

```text
attributes/default.rb
```

### Files

No static `files/default/*` or `files/*` files are listed in the supplied directory analysis.

The `nginx.rb` recipe deploys a dynamic `index.html` using `cookbook_file`. Its source is calculated from the first component of the site name:

```text
<first component of site_name>/index.html
```

Those source files must be located and added to the Ansible project separately.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Preserves the Chef dependency order in Ansible.
   - Resources: four `include_recipe` resources.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures SSH, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` fail2ban jails.
   - Sets UFW default incoming policy to deny.
   - Allows SSH, HTTP, and HTTPS.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies reverse-path filtering, redirect/source-route restrictions, martian logging, ICMP restrictions, IPv6 disablement, and TCP SYN protections.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` when SSH configuration changes.
   - Reloads sysctl settings when `/etc/sysctl.d/99-security.conf` changes.
   - Restarts `fail2ban` after jail configuration changes.
   - Resources: one `package` resource installing two packages, two `service` resources, two `template` resources, and **eight `execute` resources**:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - disable root login
     - disable password authentication

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID `/run/nginx.pid`, `768` worker connections, access/error logs, gzip, `conf.d`, and `sites-enabled` includes.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures version hiding, request limits, client buffer limits, timeouts, TLS 1.2/1.3, SSL ciphers, and preferred server ciphers.
   - Enables and starts nginx.
   - Creates `/etc/nginx/secrets` owned by `root:root` with mode `0700`.
   - Loads the encrypted data bag item using `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`.
   - Writes `site_secret['token']` to `/etc/nginx/secrets/site_token` as a sensitive file owned by `root:root` with mode `0600`.
   - Reads the `nginx_sites` data bag collection. Actual item names were not supplied, so dynamic site resource names cannot be expanded.
   - Creates each supplied site document root as `nginx:nginx` with mode `0755`.
   - Deploys the corresponding `<first component of site_name>/index.html` source to `<document_root>/index.html` as `nginx:nginx` with mode `0644`.
   - Resources: one package, two templates, one service, one fixed directory plus one dynamic directory per site, one secret file, and one dynamic `cookbook_file` per site.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Reads the `nginx_sites` data bag collection.
   - Generates certificates only for items whose `ssl_enabled` value is `true`.
   - Actual SSL-enabled site names were not supplied and therefore cannot be enumerated without inventing data.
   - Generates a 2048-bit RSA self-signed certificate valid for `365` days.
   - Writes keys to `/etc/ssl/private/<site_name>.key` and certificates to `/etc/ssl/certs/<site_name>.crt`.
   - Uses subject values including `CN=<site_name>` and `emailAddress=admin@example.com`.
   - Sets generated private keys to `root:ssl-cert` with mode `0640`.
   - Reloads nginx after certificate or key generation.
   - Recipe variable used for the private-key path: `key_file`.
   - Resources: one package resource installing two packages, one group, two directories, and one dynamic `execute` resource per SSL-enabled site.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` as `root:root` directories with mode `0755`.
   - Reads the `nginx_sites` data bag collection.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>`.
   - Uses `site_name`, `document_root`, `ssl_enabled`, `/etc/ssl/certs/<site_name>.crt`, and `/etc/ssl/private/<site_name>.key` as template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to `/etc/nginx/sites-available/<site_name>`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Adds security headers, gzip, static-file lookup, `.htaccess` denial, `.git` and `.svn` denial, and site-specific access/error logs.
   - SSL-enabled sites receive HTTP-to-HTTPS redirects and HTTPS HTTP/2 listeners with HSTS.
   - Non-SSL sites receive HTTP listeners.
   - Actual site names and template render counts cannot be expanded until the `nginx_sites` data bag contents are obtained.
   - Resources: two directories, one dynamic template per site, one dynamic link per site, and one file resource.

## Dependencies

**External cookbook dependencies**: None declared in the supplied cookbook metadata inspection.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd`

**Supported platforms from separate metadata inspection**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

Platform differences requiring validation include nginx package behavior, nginx service naming, SSH service naming, UFW availability, fail2ban behavior, nginx user/group availability, and `/var/log/auth.log` availability.

## Credentials

**Detection Summary**: 1 externally sourced credential and 1 runtime-generated sensitive credential category detected across `cookbooks/nginx-multisite/recipes/nginx.rb` and `cookbooks/nginx-multisite/recipes/ssl.rb`.

**Source**:
  - **Provider**: `Chef::EncryptedDataBagItem.load`
  - **URL**: Not applicable
  - **Path**: Data bag `nginx_secrets`, item `site`
  - **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`

### nginx Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag `nginx_secrets/site`
- **Usage context**: Secret token written for the nginx multisite deployment
- **Destination**: `/etc/nginx/secrets/site_token`
- **Owner and mode**: `root:root`, `0600`
- **Migration handling**: Store in Ansible Vault or an approved external secret manager and use `no_log: true` when writing the file.

### TLS Private Keys

- **Variable(s)**: `key_file`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally on the managed host by `openssl req`
- **Usage context**: nginx HTTPS termination
- **Destination**: `/etc/ssl/private/<site_name>.key`
- **Owner and mode**: `root:ssl-cert`, `0640`
- **Migration handling**: Do not print generated key material or expose it in task output.

No CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, plaintext password, API key, database credential, or environment-variable secret reference was detected.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-enabled/default
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
<document_root>/index.html
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
/var/log/auth.log
```

`<site_name>` and `<document_root>` must be replaced with every actual value obtained from the `nginx_sites` data bag.

**Service endpoints to check**:

- TCP `22`: SSH
- TCP `80`: HTTP
- TCP `443`: HTTPS
- Unix sockets: None configured

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: once per actual `nginx_sites` data bag item; exact count is unavailable because item names were not supplied

## Pre-flight checks

```bash
# Package checks
dpkg-query -W nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service checks
systemctl status nginx
systemctl status fail2ban
systemctl status sshd || systemctl status ssh

# nginx configuration
nginx -t
nginx -T | grep -E 'server_name|listen 80|listen 443|ssl_certificate|ssl_certificate_key'
grep -E 'user nginx|worker_processes|worker_connections|access_log|error_log|gzip on|sites-enabled' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|client_body_timeout|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Firewall
ufw status verbose
ufw status numbered
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
ufw status | grep -q 'Status: active'
ufw status | grep -q 'Default: deny'

# fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime|findtime|maxretry|backend|enabled|port|logpath' \
  /etc/fail2ban/jail.local

# SSH hardening
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t

# Kernel security
sysctl -p /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv4.tcp_synack_retries
sysctl net.ipv4.tcp_syn_retries

# Secret file without displaying contents
test -f /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token

# Listening ports
ss -tlnp | grep -E ':(22|80|443)\b'

# Service logs
journalctl -u nginx --since "15 minutes ago"
journalctl -u fail2ban --since "15 minutes ago"
journalctl -u sshd --since "15 minutes ago" || journalctl -u ssh --since "15 minutes ago"
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
```

After obtaining the actual `nginx_sites` data bag contents, run the following commands with every exact site name and document root substituted:

```bash
# HTTP site validation
curl -I -H 'Host: <site_name>' http://127.0.0.1/

# HTTPS site validation for an SSL-enabled site
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/

# Site configuration and symlink
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -E 'server_name|root|listen|access_log|error_log' \
  /etc/nginx/sites-available/<site_name>

# Document root and index
test -d <document_root>
test -f <document_root>/index.html
stat -c '%U:%G %a %n' <document_root>
stat -c '%U:%G %a %n' <document_root>/index.html

# TLS certificate and key for an SSL-enabled site
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
test -f /etc/ssl/private/<site_name>.key
stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key

# Site-specific logs
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

Expected site-specific permissions:

```text
Document root: nginx:nginx 0755
index.html: nginx:nginx 0644
TLS private key: root:ssl-cert 0640
```

Expected SSL-enabled behavior:

```text
HTTP returns 301 with an HTTPS Location header.
HTTPS responds successfully.
Strict-Transport-Security is present.
X-Frame-Options: DENY is present.
X-Content-Type-Options: nosniff is present.
```

Verify the default site is absent:

```bash
test ! -e /etc/nginx/sites-enabled/default
```