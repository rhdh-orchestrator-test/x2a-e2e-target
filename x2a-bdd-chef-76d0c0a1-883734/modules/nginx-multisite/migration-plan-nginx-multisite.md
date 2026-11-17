---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an Nginx web server with security hardening, Fail2ban, UFW, SSH restrictions, sysctl settings, optional self-signed TLS certificates, and data-bag-defined virtual hosts. Execution order is security, Nginx, SSL, and sites. The supplied plan does not contain the `nginx_sites` data-bag item names or values, so site instances, document roots, SSL flags, certificate commands, static-file sources, and per-site validation checks remain pending. These values must be obtained before implementing the site loop in Ansible.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH and Nginx log sources
  - Key Config: Enabled and started; configured jails and exact settings require source verification

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: TCP `22`, `80`, and `443`
  - Key Config: Default incoming policy deny; SSH, HTTP, and HTTPS allowed; firewall enabled

- **sshd**: SSH daemon
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`; restarted when configuration changes

- **nginx**: Primary web server
  - Location/Path: `/etc/nginx/nginx.conf`
  - Port/Socket: TCP `80` and TCP `443` where SSL is enabled; PID file `/run/nginx.pid`
  - Key Config: Enabled and started; configuration reloads after relevant changes

- **nginx_sites data-bag sites**: Dynamic virtual-host instances
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: TCP `80`; TCP `443` when `ssl_enabled` is `true`
  - Key Config: Site name, document root, SSL flag, and static-file source are sourced from the `nginx_sites` data bag
  - Instance status: No exact site names or values were supplied; the Ansible inventory must not use an unresolved generic site item

- **SSL certificate and key instances**: Dynamic SSL material for SSL-enabled sites
  - Location/Path: `/etc/ssl/certs/<site_name>.crt` and `/etc/ssl/private/<site_name>.key`
  - Port/Socket: Used by Nginx HTTPS virtual hosts on TCP `443`
  - Key Config: Self-signed RSA 2048-bit certificates, valid for 365 days, generated only when both files are absent

Security attributes identified in the supplied plan:

- `node['security']['fail2ban']['enabled']`: `true`
- `node['security']['ufw']['enabled']`: `true`
- `node['security']['ssh']['disable_root']`: `true`
- `node['security']['ssh']['password_auth']`: `false`

These values and the SSL path attributes require verification against `cookbooks/nginx-multisite/attributes/default.rb` before migration.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

### Recipes

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

### Providers

```text
```

No provider file is used by the execution tree. SSH hardening uses `execute` resources in the recipe and should be implemented with `ansible.builtin.lineinfile`. No `resources/lineinfile.rb` file is included.

### Templates

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

### Attributes

```text
cookbooks/nginx-multisite/attributes/default.rb
```

### Files

No static files are listed in the supplied directory listing. The `cookbook_file` resource references dynamic source paths in the form `<site_folder>/index.html`; those source files were not provided.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role must preserve this order: security, Nginx, SSL, then virtual hosts.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures UFW with default deny and allows SSH, HTTP, and HTTPS.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Applies the sysctl configuration with `sysctl -p /etc/sysctl.d/99-security.conf`.
   - Uses SSH hardening conditions to set `PermitRootLogin no` and `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Notifies a delayed `sshd` restart when SSH settings change.
   - Detailed Fail2ban and sysctl values require verification against the source templates before migration.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Reads the encrypted `nginx_secrets/site` data-bag item and writes `site_secret['token']` to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`.
   - Reads the `nginx_sites` data bag and consumes `id`, `document_root`, and `ssl_enabled`.
   - Creates each supplied site document root with owner `nginx`, group `nginx`, and mode `0755`.
   - Calculates the static source directory as the first component of the site name. For a supplied site name, `site_folder` is the value before the first dot.
   - Deploys the corresponding `<site_folder>/index.html` to `<document_root>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - Exact site names, document roots, and source directories are unavailable and must be supplied before this loop is implemented.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Processes only explicitly identified sites whose `ssl_enabled` value is `true`.
   - Generates `/etc/ssl/certs/<site_name>.crt` and `/etc/ssl/private/<site_name>.key` when both files are absent.
   - Uses an RSA 2048-bit self-signed certificate valid for 365 days.
   - Sets the private key to mode `0640`, owner `root`, and group `ssl-cert`.
   - Notifies a delayed Nginx reload after certificate creation.
   - No SSL-enabled site names were supplied, so no certificate-generation tasks can be expanded yet.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Reads each explicitly supplied `nginx_sites` item.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>`.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symbolic link to the available-site file.
   - Uses `/etc/ssl/certs/<site_name>.crt` and `/etc/ssl/private/<site_name>.key` for SSL-enabled sites.
   - Reloads Nginx after virtual-host or link changes.
   - Exact site names and SSL flags are unavailable; the dynamic template and link tasks must remain pending until the data-bag contents are obtained.

## Dependencies

**External cookbook dependencies**: None shown in `metadata.rb`

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`

**System package dependencies**: `fail2ban`, `ufw`, `nginx`, `openssl`, `ca-certificates`

**Service dependencies**:
- `fail2ban`: Enabled and started; restarted when `/etc/fail2ban/jail.local` changes
- `nginx`: Enabled and started; reloaded after configuration, certificate, virtual-host, link, or default-site changes
- `sshd`: Restarted when SSH hardening changes; not enabled or started by this cookbook

## Credentials

**Detection Summary**: 1 direct credential detected across 1 recipe and 1 generated file, plus locally generated TLS private keys and certificates.

**Source**:
  - **Provider**: Chef encrypted data bag for the site token; locally generated OpenSSL material for TLS keys and certificates
  - **URL**: None
  - **Path**: Data bag `nginx_secrets`, item `site`; generated TLS paths under `/etc/ssl/certs` and `/etc/ssl/private`

### Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag `nginx_secrets/site`
- **Usage context**: Written to `/etc/nginx/secrets/site_token` for Nginx-related site use; the supplied plan does not show a reference from the Nginx templates
- **Destination permissions**: Owner `root`, group `root`, mode `0600`
- **Ansible storage**: Ansible Vault, Ansible Automation Platform credentials, or an approved external secret manager; never store as plaintext

### TLS Private Keys

- **Variable(s)**: `node['nginx']['ssl']['private_key_path']`; dynamic path `/etc/ssl/private/<site_name>.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: TLS private keys for SSL-enabled Nginx virtual hosts
- **Permissions**: Owner `root`, group `ssl-cert`, mode `0640`
- **Ansible storage**: Prefer Ansible Vault or AAP credentials for managed keys; if preserving local generation, use `community.crypto` or an equivalent idempotent implementation

### TLS Certificates

- **Variable(s)**: `node['nginx']['ssl']['certificate_path']`; dynamic path `/etc/ssl/certs/<site_name>.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificates
- **Usage context**: Certificates for SSL-enabled Nginx virtual hosts
- **Validity**: 365 days
- **Subject**: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`

## Checks for the Migration

**Files to verify**:
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-enabled/default` must be absent
- `/etc/ssl/certs`
- `/etc/ssl/private`
- Dynamic site files after the site manifest is supplied:
  - `/etc/nginx/sites-available/<site_name>`
  - `/etc/nginx/sites-enabled/<site_name>`
  - `<document_root>/index.html`
  - `/etc/ssl/certs/<site_name>.crt` for SSL-enabled sites
  - `/etc/ssl/private/<site_name>.key` for SSL-enabled sites

**Service endpoints to check**:
- TCP `22` for SSH
- TCP `80` for HTTP
- TCP `443` for SSL-enabled sites
- Nginx PID file `/run/nginx.pid`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/auth.log`

**Templates rendered**:
- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 time
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 time
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 time
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 time
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: one rendering per explicitly supplied `nginx_sites` item; exact count is pending

## Pre-flight checks

```bash
# Service status
systemctl status fail2ban
systemctl status nginx
systemctl status sshd

# Fail2ban configuration
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# UFW configuration
ufw status verbose
ufw status | grep 'Default: deny'
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# Sysctl configuration
test -f /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# SSH hardening
grep '^PermitRootLogin no' /etc/ssh/sshd_config
grep '^PasswordAuthentication no' /etc/ssh/sshd_config
sshd -t

# Nginx configuration
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
nginx -t
test -f /run/nginx.pid
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Nginx secret permissions; do not print the token
stat -c '%U %G %a %n' /etc/nginx/secrets
stat -c '%U %G %a %n' /etc/nginx/secrets/site_token

# Site manifest requirement
# Obtain the nginx_sites data-bag contents before creating site tasks.
# Record one named entry per site with:
#   id, document_root, ssl_enabled, site_folder
```

Per-site validation cannot be expanded into named checks until the exact `nginx_sites` item names are supplied. After they are available, validate each named site’s document root, `index.html`, virtual-host file, enabled-site link, logs, HTTP response, and—when `ssl_enabled` is true—certificate, private key, HTTPS listener, and HTTP-to-HTTPS redirect.