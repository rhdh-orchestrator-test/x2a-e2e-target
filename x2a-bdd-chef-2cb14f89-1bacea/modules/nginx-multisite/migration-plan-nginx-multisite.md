---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx as a multisite web server with HTTP/HTTPS virtual hosts, development self-signed certificates, UFW firewall rules, Fail2ban, SSH hardening, kernel security parameters, and an encrypted Nginx site token. Execution order is `security` → `nginx` → `ssl` → `sites`. The supplied source does not contain the `nginx_sites` data bag entries, so exact site names, document roots, SSL flags, rendered site counts, and site-specific pre-flight checks remain unresolved migration inputs.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

No exact site instances are present in the supplied source. Site definitions must be imported from the `nginx_sites` Chef data bag before migration execution.

The site data must provide:

- **Site name**: Data bag field `id`
  - Virtual-host path: `/etc/nginx/sites-available/<site_name>`
  - Enabled-link path: `/etc/nginx/sites-enabled/<site_name>`
  - Certificate: `/etc/ssl/certs/<site_name>.crt`
  - Private key: `/etc/ssl/private/<site_name>.key`
  - Log names: `/var/log/nginx/<site_name>_access.log` and `/var/log/nginx/<site_name>_error.log`
  - Certificate Common Name: `<site_name>`

- **Document root**: Data bag field `document_root`
  - Nginx `root` value
  - Site directory
  - Static file destination: `<document_root>/index.html`

- **SSL status**: Data bag field `ssl_enabled`
  - Determines whether a self-signed certificate is generated.
  - Determines whether HTTPS and HTTP-to-HTTPS redirect configuration is rendered.

The security configuration contains these named collections:

- **fail2ban**: Enabled by default.
- **ufw**: Enabled by default.
- **ssh**:
  - `disable_root: true`
  - `password_auth: false`

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

No static files are included in the supplied directory listing. The recipes deploy a dynamic `index.html` through `cookbook_file`; its source files are not listed and must be supplied separately.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order: security, Nginx, SSL, then sites.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures Fail2ban defaults:
     - Ban time: `3600`
     - Find time: `600`
     - Maximum retries: `3`
     - Backend: `auto`
   - Enables SSH, Nginx HTTP authentication, Nginx request-limit, and Nginx bot-search jails.
   - Configures SSH jail on `ssh` with `/var/log/auth.log`.
   - Configures Nginx authentication and request-limit jails on `http,https` with `/var/log/nginx/*error.log`.
   - Configures the bot-search jail on `http,https` with `/var/log/nginx/*access.log`.
   - Restarts Fail2ban after changes to `/etc/fail2ban/jail.local`.
   - Applies UFW rules:
     - Default deny.
     - Allow TCP `22`.
     - Allow TCP `80`.
     - Allow TCP `443`.
     - Enable UFW after the allow rules are present.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect and source-routing protection, martian logging, ICMP restrictions, IPv6 disablement, TCP SYN cookies, and TCP retry/backlog values.
   - Reloads `/etc/sysctl.d/99-security.conf` through `sysctl -p` after changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts the platform SSH service after SSH configuration changes.
   - Resource totals: package `1` grouped resource, service `2`, template `2`, execute `8`.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID `/run/nginx.pid`, `768` worker connections, standard access and error logs, keepalive timeout `65`, gzip, and the `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*` includes.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures server-token protection, login and API rate-limit zones, request-size and timeout restrictions, SSL session settings, TLS `1.2` and `1.3`, the configured ECDHE/DHE cipher list, and server cipher preference.
   - Enables and starts the Nginx service.
   - Reloads Nginx after global or security configuration changes.
   - Creates `/etc/nginx/secrets` owned by `root:root` with mode `0700`.
   - Loads the encrypted data bag item `nginx_secrets/site`, reads field `token`, and writes it to `/etc/nginx/secrets/site_token`.
   - Deploys `/etc/nginx/secrets/site_token` as `root:root` with mode `0600` and suppresses sensitive output.
   - Reads site definitions from the `nginx_sites` data bag.
   - Derives `site_folder` from the first component of the site name.
   - Creates every supplied document root as `nginx:nginx` with mode `0755`.
   - Deploys `<document_root>/index.html` from the corresponding `<site_folder>/index.html` source with ownership `nginx:nginx` and mode `0644`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` as `root:root` with mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert` with mode `0710`.
   - Reads site definitions from the `nginx_sites` data bag.
   - Generates certificates only for entries whose `ssl_enabled` value is enabled.
   - Uses `/etc/ssl/certs/<site_name>.crt` and `/etc/ssl/private/<site_name>.key`.
   - Generates self-signed RSA `2048` certificates valid for `365` days.
   - Uses subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Skips generation when both certificate and key already exist.
   - Reloads Nginx after newly generated certificates or keys.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` as `root:root` with mode `0755`.
   - Reads site definitions from the `nginx_sites` data bag.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to `/etc/nginx/sites-available/<site_name>`.
   - Reloads Nginx after site-template or symlink changes.
   - Removes `/etc/nginx/sites-enabled/default` and reloads Nginx after removal.
   - SSL-enabled sites listen on HTTP `80`, redirect HTTP to HTTPS with status `301`, and listen on HTTPS `443` with HTTP/2.
   - SSL-enabled sites configure the document root, index files, TLS settings, HSTS, security headers, gzip, `try_files`, protected `.htaccess`, `.git`, and `.svn` paths, and per-site access and error logs.
   - Non-SSL sites provide HTTP-only configuration. The rendered configuration must be validated with `nginx -t` because the source ERB conditional structure may produce invalid server-block syntax when SSL is disabled.
   - No actual site names or loop iterations can be expanded until the `nginx_sites` data bag is supplied.

## Dependencies

**External cookbook dependencies**: None shown in `metadata.rb`.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: Enabled and started; restarted after jail configuration changes.
- `nginx`: Enabled and started; reloaded after configuration, certificate, site, symlink, or default-site changes.
- `sshd`: Restarted after SSH hardening changes. Ubuntu commonly names this service `ssh`, so the Ansible service variable must be platform-dependent.

**Source attributes** (`cookbooks/nginx-multisite/attributes/default.rb`):

```yaml
nginx:
  ssl:
    certificate_path: /etc/ssl/certs
    private_key_path: /etc/ssl/private

security:
  fail2ban:
    enabled: true
  ufw:
    enabled: true
  ssh:
    disable_root: true
    password_auth: false
```

The source recipes execute the package, service, firewall, and Fail2ban resources shown above despite the enabled flags. The migration should preserve that behavior unless intentionally correcting it.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe, with 1 sensitive file deployment.

**Source**:

- **Provider**: Chef encrypted data bag
- **Data bag**: `nginx_secrets`
- **Item**: `site`
- **Secret field**: `token`
- **URL**: None detected
- **Ansible storage**: Ansible Vault, AAP Credentials, or an approved external secret manager

### Nginx Site Token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag loaded with `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`
- **Destination**: `/etc/nginx/secrets/site_token`
- **Ownership**: `root:root`
- **Mode**: `0600`
- **Usage context**: Secret token stored for Nginx/site use.
- **Migration handling**:
  - Store the value encrypted.
  - Use `no_log: true` on tasks that could expose it.
  - Do not commit the clear-text token to Git.

The certificate subject email `admin@example.com` is a fixed development certificate field, not a credential.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets/site_token
/etc/ssl/certs
/etc/ssl/private
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
<document_root>/index.html
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
/var/log/auth.log
```

No concrete `<site_name>` or `<document_root>` values were supplied.

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443` when an SSL-enabled site exists
- Nginx PID file: `/run/nginx.pid`
- Nginx configuration includes:
  - `/etc/nginx/conf.d/*.conf`
  - `/etc/nginx/sites-enabled/*`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once.
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once.
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once.
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once.
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: once per `nginx_sites` data bag item; exact count unavailable because the data bag contents were not supplied.

## Pre-flight checks

The commands below validate all fixed services and paths. Site-specific commands require the actual data bag entries before execution.

```bash
# Package status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd 2>/dev/null || systemctl status ssh

# Nginx configuration
nginx -t
nginx -T > /tmp/nginx-rendered.conf

grep -E 'user nginx|worker_processes auto|worker_connections 768|access_log|error_log|gzip on' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens off|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Firewall
ufw status verbose
ufw status numbered

# Fail2ban
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t

# Secret permissions; do not print contents
stat -c '%U %G %a %n' /etc/nginx/secrets/site_token

# SSL directory permissions
stat -c '%U %G %a %n' /etc/ssl/certs
stat -c '%U %G %a %n' /etc/ssl/private

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Listening ports
ss -tlnp | grep -E ':(80|443)[[:space:]]'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
tail -n 100 /var/log/nginx/access.log
tail -n 100 /var/log/nginx/error.log
tail -n 100 /var/log/auth.log
```

For the supplied site data, generate one named check block per actual site:

```bash
# Replace <site_name> and <document_root> with values from nginx_sites.

test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>

grep -E 'server_name|root|listen|ssl_certificate|access_log|error_log' \
  /etc/nginx/sites-available/<site_name>

test -d <document_root>
test -f <document_root>/index.html
stat -c '%U %G %a %n' <document_root>
stat -c '%U %G %a %n' <document_root>/index.html

tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

For each site whose data has `ssl_enabled` enabled, also run:

```bash
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -checkend 0
stat -c '%U %G %a %n' /etc/ssl/private/<site_name>.key
curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
```

Expected SSL-site behavior:

- HTTP returns `301`.
- The `Location` header points to `https://<site_name>/`.
- HTTPS returns a successful response when `<document_root>/index.html` exists.
- Certificate key permissions are `root:ssl-cert` with mode `0640`.

For each site whose data has `ssl_enabled` disabled, run:

```bash
curl -I -H 'Host: <site_name>' http://127.0.0.1/
```

Expected non-SSL-site behavior:

- HTTP serves the configured document root.
- No HTTPS endpoint is expected for that site.

The exact site names, document roots, SSL-enabled entries, and individual site check blocks must be populated from the missing `nginx_sites` data bag before the migration can be considered complete.