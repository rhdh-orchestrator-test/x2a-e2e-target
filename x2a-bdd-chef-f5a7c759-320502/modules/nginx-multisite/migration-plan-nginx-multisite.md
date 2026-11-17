---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook provisions nginx for data-bag-defined virtual hosts, applies nginx, SSH, fail2ban, UFW, and kernel security hardening, generates self-signed certificates for SSL-enabled sites, and deploys static `index.html` files. Execution order is security, nginx installation, SSL preparation, and site configuration. Site names and attributes are loaded dynamically from the `nginx_sites` data bag; the supplied source does not identify those item names, document roots, or SSL states, so the complete site inventory must be obtained before migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Web server and virtual-host service
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP `80`; TCP `443` when SSL-enabled sites exist; PID file `/run/nginx.pid`
  - Key Config: `/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/security.conf`, `/etc/nginx/sites-available`, and `/etc/nginx/sites-enabled`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH, HTTP, and HTTPS logs
  - Key Config: SSH jail, nginx authentication jail, nginx request-limit jail, and nginx bot-search jail

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Default incoming policy is deny; firewall is enabled

- **sshd**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`

- **Kernel network security**: Sysctl hardening
  - Location/Path: `/etc/sysctl.d/99-security.conf`
  - Port/Socket: Not applicable
  - Key Config: Reverse-path filtering, redirect and source-route protection, martian logging, ICMP restrictions, IPv6 disablement, and SYN-flood protection

- **`nginx_sites` data-bag sites**: Dynamic nginx virtual hosts
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: TCP `80`; TCP `443` when `ssl_enabled` is true
  - Key Config: `id`, `document_root`, and `ssl_enabled`
  - Site names: Not supplied in the analyzed source; exact item names must be obtained before migration

The required site data-bag fields are:

- `id`: Hostname used as `server_name`
- `document_root`: Site content directory
- `ssl_enabled`: Controls certificate generation and HTTPS behavior

Site-specific paths are:

- Certificate: `/etc/ssl/certs/<site_name>.crt`
- Private key: `/etc/ssl/private/<site_name>.key`
- Static source: `<first_component_of_site_name>/index.html`
- Static destination: `<document_root>/index.html`

The explicitly enumerated security namespaces are `fail2ban`, `ufw`, and `ssh`; these are not nginx site instances.

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

No provider files are used by the execution tree. The analyzed `resources/lineinfile.rb` custom resource is not invoked by an executed recipe and is excluded from the migration file list.

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

No static files are present in the supplied directory listing.

The recipes reference dynamic `cookbook_file` sources in this form:

```text
<site_folder>/index.html
```

Those source files must be obtained and packaged before implementing the Ansible `copy` task.

## Module Explanation

The cookbook performs operations in this order.

1. **Default entry recipe** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Ansible execution order must be `security.yml`, `nginx.yml`, `ssl.yml`, then `sites.yml`.

2. **Security configuration** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs packages `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local`, mode `0644`.
   - Configures fail2ban defaults: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Configures the `sshd` jail on port `ssh` using `/var/log/auth.log`.
   - Configures `nginx-http-auth` on `http,https` using `/var/log/nginx/*error.log`.
   - Configures `nginx-limit-req` on `http,https` using `/var/log/nginx/*error.log`, with maximum retries `10`.
   - Configures `nginx-botsearch` on `http,https` using `/var/log/nginx/*access.log`, with maximum retries `2`.
   - Delayed-restarts `fail2ban` when `jail.local` changes.
   - Sets UFW default incoming policy to deny.
   - Allows SSH TCP `22`, HTTP TCP `80`, and HTTPS TCP `443`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf`, mode `0644`.
   - Configures reverse-path filtering:
     - `net.ipv4.conf.default.rp_filter = 1`
     - `net.ipv4.conf.all.rp_filter = 1`
   - Disables IPv4 and IPv6 ICMP redirects and source routing.
   - Enables IPv4 martian logging.
   - Sets `net.ipv4.icmp_echo_ignore_all = 1`.
   - Sets `net.ipv4.icmp_echo_ignore_broadcasts = 1`.
   - Disables IPv6 on `all`, `default`, and `lo`.
   - Enables SYN cookies and sets the TCP SYN backlog and retry values.
   - Delayed-executes `sysctl -p /etc/sysctl.d/99-security.conf` when the sysctl template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Delayed-restarts `sshd` when either SSH setting changes.
   - Both SSH hardening resources execute by default because `disable_root` is `true` and `password_auth` is `false`.

3. **nginx installation and base configuration** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf`, mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID `/run/nginx.pid`, `768` worker connections, standard sendfile and TCP settings, 65-second keepalive, access and error logs, gzip, module includes, `conf.d` includes, and `sites-enabled` includes.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf`, mode `0644`.
   - Configures `server_tokens off`, login and API rate-limit zones, restrictive client buffers and timeouts, TLS `1.2` and `1.3`, SSL session settings, the configured cipher list, and `ssl_prefer_server_ciphers on`.
   - Enables and starts the `nginx` service.
   - Delayed-reloads nginx when either nginx template changes.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads the encrypted data-bag item `nginx_secrets/site`.
   - Writes its `token` value to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, mode `0600`, and sensitive output handling.
   - Reads all item names from the `nginx_sites` data bag; the supplied source does not provide the names.
   - Uses each discovered item’s `id` as `site_name` and its `document_root` as the content directory.
   - Creates each discovered document root recursively with owner `nginx`, group `nginx`, and mode `0755`.
   - Computes `site_folder` as the first component of `site_name` split on `.`.
   - Deploys `<site_folder>/index.html` to `<document_root>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - The exact dynamic site iterations cannot be expanded until the `nginx_sites` data-bag inventory is obtained.

4. **SSL package, directories, and certificate generation** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` from `node['nginx']['ssl']['certificate_path']`, owner `root`, group `root`, mode `0755`.
   - Creates `/etc/ssl/private` from `node['nginx']['ssl']['private_key_path']`, owner `root`, group `ssl-cert`, mode `0710`.
   - Reads the `nginx_sites` data bag.
   - Sites with `ssl_enabled` false do not receive certificates.
   - Each site with `ssl_enabled` true receives:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Uses a 2048-bit RSA, 365-day self-signed certificate with subject `CN=<site_name>` and `emailAddress=admin@example.com`.
   - Sets the private key to mode `0640` and ownership `root:ssl-cert`.
   - Skips certificate generation when both files already exist.
   - Delayed-reloads nginx after generating a certificate.
   - The exact SSL-enabled site iterations cannot be expanded until the `nginx_sites` data-bag inventory is obtained.

5. **Site directories, virtual hosts, links, and default-site removal** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once per discovered `nginx_sites` item to `/etc/nginx/sites-available/<site_name>`, mode `0644`.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` template variables.
   - SSL-enabled sites listen on port `80`, redirect HTTP to `https://$server_name$request_uri`, and listen on port `443` with SSL and HTTP/2.
   - SSL-enabled sites use the generated certificate and key, TLS `1.2` and `1.3`, and one-year HSTS including subdomains.
   - Non-SSL sites listen on port `80` and serve directly from their document root.
   - Both site branches configure index files, security headers, gzip, `try_files $uri $uri/ =404`, `.htaccess` denial, `.git` and `.svn` denial, and per-site access and error logs.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a link to `/etc/nginx/sites-available/<site_name>` for each discovered site.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Delayed-reloads nginx after a virtual-host template, link, or default-site deletion changes.
   - The exact site template and link iterations cannot be expanded until the `nginx_sites` data-bag inventory is obtained.

## Dependencies

**External cookbook dependencies**: None reported by the supplied metadata.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The recipe assumes UFW commands, Debian-style nginx site directories, and `/var/log/auth.log`. These assumptions require validation on CentOS. The recipe explicitly creates the site directories because Fedora’s nginx package does not create Debian-style directories.

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

**Network ports**:

- TCP `22`: SSH
- TCP `80`: HTTP
- TCP `443`: HTTPS

## Credentials

**Detection Summary**: 1 credential detected across 1 recipe and 1 encrypted data-bag reference. The encrypted data-bag lookup is identified by the recipe behavior and requires source-code verification because the supplied structured execution analysis does not explicitly show the lookup provider.

**Source**:
  - **Provider**: Chef encrypted data bag
  - **Lookup**: `encrypted_data_bag_item('nginx_secrets', 'site')`
  - **URL**: None
  - **Path**: `nginx_secrets/site`

### Site token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **File ownership and mode**: `root:root`, `0600`
- **Ansible migration**: Store the token in Ansible Vault or an AAP-supported credential/secret store. Do not place it in plaintext variables, templates, task output, or source control.
- **Source verification**: Confirm the encrypted lookup in the recipe before migration because the structured execution analysis only shows the destination file resource.

No HashiCorp Vault, CyberArk, AWS Secrets Manager, `chef_vault_item`, Conjur, or environment-variable secret references were detected.

### TLS private keys

The SSL recipe generates private keys locally:

```text
/etc/ssl/private/<site_name>.key
```

- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by `openssl`
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`
- **Usage context**: nginx TLS termination
- **Ansible migration**: Preserve self-signed certificate generation only when appropriate for the target environment. Production deployments should use managed certificates and protect private keys with Ansible Vault or an external certificate-management system.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-enabled/default
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
<document_root>/index.html
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
/var/log/auth.log
```

The `<site_name>` and `<document_root>` values must be replaced with the exact data-bag values before execution.

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: one render per `nginx_sites` data-bag item

The exact site render count and names cannot be determined until the data-bag inventory is supplied.

## Pre-flight checks

```bash
# Package status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# nginx configuration
nginx -t
nginx -T | grep -E 'include /etc/nginx/conf.d|include /etc/nginx/sites-enabled'
grep -E 'user|worker_processes|worker_connections|access_log|error_log|gzip' \
  /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols' \
  /etc/nginx/conf.d/security.conf

# fail2ban and firewall
cat /etc/fail2ban/jail.local
fail2ban-client status
fail2ban-client status sshd
ufw status verbose

# Kernel security
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies

# SSH hardening
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config

# Secret file metadata; do not print contents
stat -c '%U:%G %a %n' /etc/nginx/secrets /etc/nginx/secrets/site_token
test -s /etc/nginx/secrets/site_token

# Listener checks
ss -tlnp | grep -E ':(22|80|443)\s'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Service logs
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
```

Expected baseline results:

- `nginx`, `fail2ban`, `ufw`, `openssl`, and `ca-certificates` are installed.
- `nginx`, `fail2ban`, and `sshd` are active.
- UFW is active with default deny, SSH allowed, HTTP allowed, and HTTPS allowed.
- SSH contains `PermitRootLogin no` and `PasswordAuthentication no`.
- `nginx -t` reports `syntax is ok` and `test is successful`.
- `/etc/nginx/secrets` is `root:root` mode `700`.
- `/etc/nginx/secrets/site_token` is `root:root` mode `600`.
- `/etc/nginx/sites-enabled/default` does not exist.
- nginx listens on TCP `80`.
- nginx listens on TCP `443` when at least one SSL-enabled site exists.

The complete site inventory must be obtained before running instance-specific checks. After the exact names and attributes are known, create a separately named validation block for every site containing:

```bash
# Site: <site_name>
test -d <document_root>
test -f <document_root>/index.html
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -n "server_name <site_name>" /etc/nginx/sites-available/<site_name>
grep -n "root <document_root>" /etc/nginx/sites-available/<site_name>
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

For every site whose `ssl_enabled` value is `true`, also run:

```bash
# Site: <site_name>, SSL enabled
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
grep -nE 'listen 443 ssl http2|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/<site_name>
curl -I http://<site_name>
curl -k -I https://<site_name>
```

Expected SSL results are an HTTP `301` redirect to HTTPS, a successful HTTPS response, and a certificate subject containing `CN=<site_name>`.

For every site whose `ssl_enabled` value is `false`, also run:

```bash
# Site: <site_name>, SSL disabled
grep -nE 'listen 80|root <document_root>' \
  /etc/nginx/sites-available/<site_name>
curl -I http://<site_name>
```

Expected non-SSL results are direct HTTP service from the configured document root and no required certificate or private-key files.

After changing nginx configuration, validate and reload:

```bash
nginx -t && systemctl reload nginx
systemctl is-active nginx
```

The nginx service must remain active after validation and reload.