---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with security hardening, UFW firewall rules, fail2ban, SSH hardening, optional self-signed TLS certificates, and data-bag-defined virtual hosts. Execution order is `security` → `nginx` → `ssl` → `sites`. The supplied plan does not contain the actual `nginx_sites` data-bag item names, so site-specific instances, document roots, and SSL-enabled sites must be supplied as migration variables and cannot be safely invented.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Primary web server
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP/80; TCP/443 for SSL-enabled sites
  - Key Config: `/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/security.conf`, `/etc/nginx/sites-available`, `/etc/nginx/sites-enabled`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH and nginx-related logs; no listening socket configured by this cookbook
  - Key Config: SSH, nginx HTTP authentication, request-limit, and bot-search jails

- **ufw**: Host firewall
  - Location/Path: System firewall configuration
  - Port/Socket: Allows TCP/22, TCP/80, and TCP/443
  - Key Config: Default incoming policy is deny; firewall is enabled

- **sshd**: Hardened SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP/22
  - Key Config: Root login disabled and password authentication disabled

- **nginx site instances**: Runtime virtual hosts loaded from the `nginx_sites` data bag
  - Location/Path: Site-specific `document_root` values supplied by the data-bag items
  - Port/Socket: TCP/80; TCP/443 when `ssl_enabled` is true
  - Key Config: Each item supplies `id`, `document_root`, and `ssl_enabled`
  - Exact instances: Not present in the supplied execution-tree analysis; no site names or document roots can be enumerated without inventing configuration

The migration must define the runtime site collection explicitly, for example:

```yaml
nginx_sites:
  # Populate with the actual Chef nginx_sites data-bag items.
  # No site names are present in the supplied analysis.
```

The security iteration collection contains these named items:

- **fail2ban**
- **ufw**
- **ssh**

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

```text
```

No static file path under `files/` is listed. The `nginx.rb` recipe uses a dynamic `cookbook_file` source such as `<site_folder>/index.html`; those source files must be located separately if they exist outside the supplied listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Ansible execution order must remain security, nginx, SSL, and sites.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures fail2ban defaults of ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Configures the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails.
   - Sets UFW default incoming policy to deny.
   - Allows SSH, HTTP, and HTTPS.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Configures reverse-path filtering, ICMP redirect and source-routing restrictions, martian logging, ICMP echo restrictions, IPv6 disablement, TCP SYN cookies, and TCP backlog/retry settings.
   - Applies SSH hardening in `/etc/ssh/sshd_config`: `PermitRootLogin no` and `PasswordAuthentication no`.
   - Declares `sshd` as a notification target and restarts it when SSH configuration changes.
   - Resources: one package resource, two service declarations, two templates, and eight execute resources.
   - The supplied validation notes state that notification timing and exact template contents require verification against source files.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs `nginx`.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Writes the site token to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`.
   - Loads site data from the `nginx_sites` data-bag collection.
   - Creates each configured site’s `document_root` with owner `nginx`, group `nginx`, and mode `0755`.
   - Derives the static source folder from the first component of the site name:
     ```ruby
     site_folder = site_name.split('.').first
     ```
   - Deploys `<site_folder>/index.html` to `<document_root>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - The exact site names and static source paths are not present in the supplied analysis; the dynamic site loop cannot be expanded into named instances.
   - The reported nginx settings include worker user `nginx`, worker processes `auto`, PID `/run/nginx.pid`, worker connections `768`, standard access and error logs, gzip, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`.
   - The reported security configuration includes version hiding, `login` and `api` request zones, small request buffers, maximum body size `1k`, ten-second client and send timeouts, TLS 1.2 and TLS 1.3, TLS session settings, and an explicit cipher list.
   - The supplied validation notes state that template contents, modes, notification relationships, and delayed reload behavior require verification against source files.
   - Resources: one package, two templates, one service, one fixed directory, one token file, and one dynamic directory plus one dynamic `cookbook_file` per actual site entry.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Reads the `nginx_sites` data-bag collection.
   - Processes only entries whose `ssl_enabled` value is `true`.
   - Generates self-signed RSA 2048-bit certificates valid for 365 days.
   - Writes certificates to `/etc/ssl/certs/<site_name>.crt`.
   - Writes private keys to `/etc/ssl/private/<site_name>.key`.
   - Sets generated private keys to owner `root`, group `ssl-cert`, and mode `0640`.
   - Uses the subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Skips certificate generation when both the certificate and key already exist.
   - Exact SSL-enabled site names are not present in the supplied analysis, so certificate-generation iterations cannot be expanded into named instances.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Reads the `nginx_sites` data-bag collection.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` for each actual site item.
   - Supplies `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symbolic link to `/etc/nginx/sites-available/<site_name>`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - SSL-enabled site configurations listen on HTTP and HTTPS, redirect HTTP to HTTPS, enable HTTP/2, configure certificate paths, TLS 1.2 and TLS 1.3, HSTS, security headers, gzip, static routing, and site-specific logs.
   - Non-SSL site configurations listen on HTTP without SSL directives or HTTPS redirection.
   - Exact site names are not present in the supplied analysis; the template and link iterations cannot be expanded into named instances.

## Attributes

**Source file**:

```text
cookbooks/nginx-multisite/attributes/default.rb
```

The original plan reports these defaults:

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

The validation notes indicate that the supplied structured analysis confirms references to these attributes but does not expose the attribute values. Verify the values directly from `attributes/default.rb` before implementation.

Although `fail2ban.enabled` and `ufw.enabled` are reported as enabled, the supplied `security.rb` flow unconditionally installs and configures both packages. Preserve the actual recipe behavior unless the migration intentionally introduces conditional execution.

## Dependencies

**External cookbook dependencies**: None are listed in the supplied metadata analysis; verify against cookbook metadata because metadata was not included in the validation evidence.

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

**Required runtime data sources**:

- Chef encrypted data bag: `nginx_secrets`, item `site`
- Chef data bag: `nginx_sites`

**Supported platforms**: The original plan reports Ubuntu `>= 18.04` and CentOS `>= 7.0`; these values require verification against cookbook metadata.

## Credentials

**Detection Summary**: 1 encrypted site token detected, plus generated TLS private keys and certificates.

**Source**:

- **Provider**: `Chef::EncryptedDataBagItem` / Chef encrypted data bag for the site token; local `openssl` generation for TLS material
- **URL**: None
- **Path**: `nginx_secrets`, item `site`; generated files under `/etc/ssl/certs` and `/etc/ssl/private`
- **Custom provider files**: None listed

The supplied validation notes state that the structured execution-tree evidence confirms the destination file but does not independently expose the encrypted data-bag load or token access. Confirm the source call in `cookbooks/nginx-multisite/recipes/nginx.rb`.

### Nginx site token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag `nginx_secrets`, item `site`
- **Destination**: `/etc/nginx/secrets/site_token`
- **Usage context**: Secret token file used by nginx-related site functionality
- **Permissions**: `0600`
- **Owner/group**: `root:root`
- **Migration storage**: Ansible Vault or an approved external secret provider
- **Migration handling**: Use `no_log: true`; do not place the token in plaintext inventory or normal task output

### TLS private keys

- **Variable/path**: `key_file`
- **Source files**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated by `openssl`
- **Destination pattern**: `/etc/ssl/private/<site_name>.key`
- **Usage context**: nginx HTTPS private key
- **Permissions**: `0640`
- **Owner/group**: `root:ssl-cert`
- **Migration handling**: Protect generated keys with equivalent permissions and prevent task-output disclosure

### TLS certificates

- **Variable/path**: `cert_file`
- **Source files**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate
- **Destination pattern**: `/etc/ssl/certs/<site_name>.crt`
- **Usage context**: nginx HTTPS certificate
- **Generation**: RSA 2048-bit, self-signed, valid for 365 days
- **Migration handling**: Preserve the idempotent existence check or replace it with a managed production certificate workflow

No HashiCorp Vault, CyberArk, AWS Secrets Manager, plaintext data-bag credential lookup, environment-variable secret, embedded database password, API key, or hardcoded token value was identified.

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
<document_root>/index.html
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
/var/log/auth.log
```

The `<site_name>` and `<document_root>` paths must be replaced with every actual item supplied in `nginx_sites`. No named runtime site instances are available in the supplied plan.

**Service endpoints to check**:

- nginx HTTP: TCP/80
- SSL-enabled nginx sites: TCP/443
- sshd: TCP/22
- UFW rules for SSH, HTTP, and HTTPS
- Unix sockets: None configured by this cookbook

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 time
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 time
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 time
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 time
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: once per actual `nginx_sites` item; names are unavailable

## Pre-flight checks

```bash
# Package and service status
nginx -v
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# nginx configuration validation
nginx -t
nginx -T

# Core nginx configuration
grep -E 'user nginx|worker_processes|worker_connections|access_log|error_log|sites-enabled' \
  /etc/nginx/nginx.conf

# nginx security configuration
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Security files
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf
grep -E 'PermitRootLogin no|PasswordAuthentication no' /etc/ssh/sshd_config

# fail2ban jails
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# UFW policy and rules
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# Kernel settings
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# Secret permissions
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token
# Expected: root:root 600 /etc/nginx/secrets/site_token

# Listening ports
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
ss -tlnp | grep ':22'

# Service logs
journalctl -u fail2ban --no-pager -n 50
journalctl -u nginx --no-pager -n 50
journalctl -u sshd --no-pager -n 50

# nginx logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log

# Default site removal
test ! -e /etc/nginx/sites-enabled/default
```

No site-specific pre-flight block can be enumerated because the supplied plan contains no actual `nginx_sites` item names. After the site variable is populated, run the following checks separately for every named site:

```bash
# Replace <site_name> and <document_root> with an actual configured item
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
test -f <document_root>/index.html

stat -c '%U:%G %a %n' <document_root>/index.html

grep -E 'listen|server_name|root|ssl_certificate|ssl_certificate_key|access_log|error_log' \
  /etc/nginx/sites-available/<site_name>

# Run only for a site whose ssl_enabled value is true
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key
curl -k -I https://<site_name>/

# Run for a non-SSL site
curl -I -H 'Host: <site_name>' http://127.0.0.1/

# Run for an SSL-enabled site to verify HTTP redirection
curl -I -H 'Host: <site_name>' http://127.0.0.1/
# Expected: HTTP 301 with Location pointing to https://<site_name>/
```

Migration validation must confirm that:

- Security tasks execute before nginx installation.
- nginx is enabled and started before site configuration is applied.
- SSL directories exist before certificate generation.
- Certificate generation is skipped when both expected files exist.
- Site configuration is rendered only from actual `nginx_sites` entries.
- Every supplied site has its own document root, static `index.html`, available-site configuration, and enabled-site link.
- Configuration, certificate, and link changes trigger the intended reload behavior after that behavior is verified against the source.
- The encrypted site token is stored through Ansible Vault or an equivalent provider and is never printed.
