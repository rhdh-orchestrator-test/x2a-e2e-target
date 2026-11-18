---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server for dynamically defined virtual sites loaded from the `nginx_sites` Chef data bag. It installs and configures nginx, Fail2ban, UFW, SSH hardening, kernel security parameters, optional self-signed TLS certificates, HTTP-to-HTTPS redirects, security headers, rate limiting, per-site logs, and static `index.html` content. Execution order is `security` → `nginx` → `ssl` → `sites`. The supplied analysis does not contain the actual `nginx_sites` item names or attributes, so those values must be supplied and verified before migration.

## Service Type and Instances

**Service Type**: Web Server

**Supported Platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **nginx**: Primary web server and virtual-host service
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP `80`; TCP `443` when SSL-enabled sites exist
  - Key Config: `/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/security.conf`, `/etc/nginx/sites-enabled/*`
  - PID: `/run/nginx.pid`
  - Status: Enabled and started

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH and nginx logs
  - Key Config: `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails
  - Status: Enabled and started

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Default incoming policy `deny`; firewall enabled
  - Status: Enabled after rules are applied

- **sshd**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`
  - Status: Restarted after applicable configuration changes

- **nginx_sites runtime collection**: Dynamically defined virtual hosts
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: TCP `80`; TCP `443` when `ssl_enabled` is true
  - Key Config: `id`, `document_root`, and `ssl_enabled`
  - Exact site names: Not supplied in the analyzed data; migration must obtain them from the original `nginx_sites` data bag
  - Required per-site values: Data bag item name, `id`, `document_root`, and `ssl_enabled`

For every supplied `nginx_sites` entry, the resulting paths are:

- Certificate: `/etc/ssl/certs/<site_name>.crt`
- Private key: `/etc/ssl/private/<site_name>.key`
- Site configuration: `/etc/nginx/sites-available/<site_name>`
- Enabled-site link: `/etc/nginx/sites-enabled/<site_name>`
- Access log: `/var/log/nginx/<site_name>_access.log`
- Error log: `/var/log/nginx/<site_name>_error.log`
- Static content: `<document_root>/index.html`

The actual site names cannot be inferred from the supplied cookbook analysis and must not be invented.

## File Structure

The following files are relevant to the migration and are relative to the cookbook root.

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── recipes/
│   ├── default.rb
│   ├── security.rb
│   ├── nginx.rb
│   ├── ssl.rb
│   └── sites.rb
├── resources/
│   └── lineinfile.rb
└── templates/
    └── default/
        ├── fail2ban.jail.local.erb
        ├── nginx.conf.erb
        ├── security.conf.erb
        ├── site.conf.erb
        └── sysctl-security.conf.erb
```

**Providers:**

```text
```

No provider is used by the execution tree. `resources/lineinfile.rb` is not invoked and is excluded from the migration execution plan.

**Static files:**

```text
```

No deployed static files are present in the supplied directory listing. `recipes/nginx.rb` references dynamic cookbook content using `<site_folder>/index.html`; the original site content must be obtained separately.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the execution order: security preparation, nginx installation, TLS preparation, and virtual-host configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures Fail2ban defaults:
     - `bantime = 3600`
     - `findtime = 600`
     - `maxretry = 3`
     - `backend = auto`
   - Configures the `sshd` jail for `/var/log/auth.log`, port `ssh`, and maximum retries `3`.
   - Configures the `nginx-http-auth` jail for `/var/log/nginx/*error.log`, ports `http,https`, and maximum retries `3`.
   - Configures the `nginx-limit-req` jail for `/var/log/nginx/*error.log`, ports `http,https`, and maximum retries `10`.
   - Configures the `nginx-botsearch` jail for `/var/log/nginx/*access.log`, ports `http,https`, and maximum retries `2`.
   - Schedules a delayed Fail2ban restart when `/etc/fail2ban/jail.local` changes.
   - Applies UFW rules in this order:
     1. Default incoming policy `deny`.
     2. Allow SSH.
     3. Allow HTTP.
     4. Allow HTTPS.
     5. Enable UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Configures reverse-path filtering, redirect handling, source-route handling, martian logging, ICMP protections, IPv6 disabling, and TCP SYN-flood protections.
   - Reloads `/etc/sysctl.d/99-security.conf` after changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Schedules a delayed `sshd` restart when either SSH setting changes.
   - Security loop items are **fail2ban**, **ufw**, and **ssh**.
   - Resource counts: one package resource, two service resources, two template resources, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Configures worker user `nginx`, automatic worker processes, PID `/run/nginx.pid`, `worker_connections 768`, standard send and keepalive settings, access and error logs, gzip, and includes for `conf.d` and `sites-enabled`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Configures `server_tokens off`, `login` and `api` request-rate zones, request buffer limits, timeouts, TLS 1.2 and 1.3, cipher settings, SSL session caching, and preferred server ciphers.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Reads the `token` field from encrypted data bag `nginx_secrets`, item `site`.
   - Writes the token to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`; the resource is sensitive.
   - Reads the runtime `nginx_sites` collection.
   - For each supplied runtime site entry:
     - Uses `site['id']` as `site_name`.
     - Uses `site['document_root']` as the document root.
     - Creates the document root with owner `nginx`, group `nginx`, and mode `0755`.
     - Derives `site_folder` from the first component of `site_name` split on `.`.
     - Deploys `<document_root>/index.html` from `<site_folder>/index.html`.
     - Sets the deployed file owner to `nginx`, group to `nginx`, and mode `0644`.
   - Exact runtime site names and document roots are not present in the supplied analysis and must be provided before migration.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates the certificate directory from `node['nginx']['ssl']['certificate_path']`, defaulting to `/etc/ssl/certs`, with mode `0755`.
   - Creates the private-key directory from `node['nginx']['ssl']['private_key_path']`, defaulting to `/etc/ssl/private`, owned by `root:ssl-cert`, with mode `0710`.
   - Reads the runtime `nginx_sites` collection.
   - Processes only runtime site entries whose `ssl_enabled` value is true.
   - For every supplied SSL-enabled site:
     - Generates `/etc/ssl/certs/<site_name>.crt`.
     - Generates `/etc/ssl/private/<site_name>.key`.
     - Uses a self-signed RSA 2048-bit certificate valid for 365 days.
     - Uses the site name as the certificate common name.
     - Uses `admin@example.com` as the certificate email.
     - Sets the private key owner to `root`, group to `ssl-cert`, and mode to `0640`.
     - Skips generation when both certificate and key already exist.
     - Schedules a delayed nginx reload when a certificate is generated.
   - Exact SSL-enabled site names are not present in the supplied analysis and must be provided before migration.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Reads each supplied runtime entry from `nginx_sites`.
   - Uses `site['id']` as `site_name`, `site['document_root']` as the root, and `site['ssl_enabled']` to select the virtual-host behavior.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Passes `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` to the template.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symbolic link to `/etc/nginx/sites-available/<site_name>`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Schedules delayed nginx reloads when site templates, links, or the default-site removal change.
   - SSL-enabled sites listen on port `80`, redirect HTTP to HTTPS with status `301`, and listen on port `443` with SSL and HTTP/2.
   - SSL-enabled sites use the generated certificate and key and enable one-year HSTS including subdomains.
   - Non-SSL sites listen on port `80` and serve content directly.
   - Both site types configure the document root, index files, security headers, gzip, `try_files`, `.htaccess` denial, `.git` and `.svn` denial, and per-site access and error logs.
   - Exact site names are not present in the supplied analysis and must be provided before migration.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd`

**Runtime data dependencies**:

- Encrypted Chef data bag `nginx_secrets`, item `site`
- Plain Chef data bag `nginx_sites`
- Required `nginx_sites` fields: item name, `id`, `document_root`, and `ssl_enabled`
- Original site content for `<site_folder>/index.html`

**Migration variable defaults**:

- `nginx_ssl_certificate_path`: `/etc/ssl/certs`
- `nginx_ssl_private_key_path`: `/etc/ssl/private`
- `security_fail2ban_enabled`: `true`
- `security_ufw_enabled`: `true`
- `security_ssh_disable_root`: `true`
- `security_ssh_password_auth`: `false`

The attribute definitions and defaults require verification against `cookbooks/nginx-multisite/attributes/default.rb`. The execution tree indicates that package installation and UFW commands execute unconditionally, regardless of the `fail2ban.enabled` and `ufw.enabled` attributes.

## Credentials

**Detection Summary**: 1 explicit credential detected in 1 recipe, plus locally generated TLS private keys for SSL-enabled runtime sites.

**Source**:

- **Provider**: Encrypted Chef data bag for the site token; local filesystem generation for TLS private keys
- **URL**: None detected
- **Path**: `nginx_secrets/site`; generated keys under `/etc/ssl/private/<site_name>.key`
- **Verification status**: The supplied execution summary confirms the output file but does not independently show the encrypted data bag lookup. Verify the source recipe before migration.

### Site token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Encrypted Chef data bag
- **Data bag**: `nginx_secrets`
- **Data bag item**: `site`
- **Output path**: `/etc/nginx/secrets/site_token`
- **Usage context**: Writes the nginx site token to disk for use by the deployed nginx configuration or related site components.
- **File permissions**: Owner `root`, group `root`, mode `0600`
- **Chef handling**: File resource marked `sensitive`
- **Ansible storage**: Ansible Vault variable in encrypted group or host variables
- **Ansible handling**: Use `no_log: true`; deploy with `ansible.builtin.copy` or `ansible.builtin.template`

### TLS private keys

- **Variable/path**: `/etc/ssl/private/<site_name>.key`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by `openssl`
- **Usage context**: nginx TLS private key
- **Certificate type**: Self-signed development certificate
- **Validity**: 365 days
- **Permissions**: Owner `root`, group `ssl-cert`, mode `0640`
- **Handling**: Treat as sensitive in Ansible even though the cookbook does not use a vault for these keys

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-available/<site_name>`
- `/etc/nginx/sites-enabled/<site_name>`
- `<document_root>/index.html`
- `/etc/ssl/certs/<site_name>.crt` for SSL-enabled sites
- `/etc/ssl/private/<site_name>.key` for SSL-enabled sites
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/<site_name>_access.log`
- `/var/log/nginx/<site_name>_error.log`

The `<site_name>` and `<document_root>` values must be replaced with every exact entry obtained from the original `nginx_sites` data bag. No exact site names were supplied.

**Service endpoints to check**:

- nginx HTTP: TCP `80`
- nginx HTTPS: TCP `443` when an SSL-enabled site exists
- SSH: TCP `22`
- nginx PID: `/run/nginx.pid`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`
  - Renders once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`
  - Renders once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`
  - Renders once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`
  - Renders once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/<site_name>`
  - Renders once per supplied `nginx_sites` item
  - Exact rendering count cannot be finalized until the data bag item list is obtained

## Pre-flight checks

The following checks must be run after replacing `<site_name>` and `<document_root>` with the exact migrated site values. Migration cannot be considered complete until the missing `nginx_sites` item names and attributes are supplied.

### Service status commands

```bash
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx

systemctl is-enabled fail2ban
systemctl is-active fail2ban

systemctl is-enabled sshd
systemctl is-active sshd
```

### nginx configuration validation

```bash
nginx -t
nginx -T | grep -E 'server_name|listen 80|listen 443|ssl_certificate|ssl_certificate_key'

grep -E 'worker_processes|worker_connections|keepalive_timeout|access_log|error_log|gzip' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf
```

### nginx instance validation

```bash
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -d /etc/nginx/sites-available
test -d /etc/nginx/sites-enabled
test ! -e /etc/nginx/sites-enabled/default
test -f /run/nginx.pid
```

### fail2ban instance validation

```bash
test -f /etc/fail2ban/jail.local
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

grep -E 'bantime|findtime|maxretry|backend' /etc/fail2ban/jail.local
```

### ufw instance validation

```bash
ufw status verbose
ufw status numbered
```

Expected results:

- Status: active
- Default incoming policy: deny
- SSH allowed on `22/tcp`
- HTTP allowed on `80/tcp`
- HTTPS allowed on `443/tcp`

### sshd instance validation

```bash
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config
sshd -t
systemctl status sshd
```

Expected settings:

```text
PermitRootLogin no
PasswordAuthentication no
```

### Runtime site validation

For each exact site name supplied from `nginx_sites`, substitute its actual value for `<site_name>`:

```bash
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>

grep -E 'server_name|listen|root|ssl_certificate|ssl_certificate_key|access_log|error_log' \
  /etc/nginx/sites-available/<site_name>
```

For the exact document root associated with that site:

```bash
test -d <document_root>
test -f <document_root>/index.html

stat -c '%U:%G %a %n' <document_root>
stat -c '%U:%G %a %n' <document_root>/index.html
```

Expected permissions:

- Document root: `nginx:nginx`, mode `0755`
- `index.html`: `nginx:nginx`, mode `0644`

### SSL-enabled site validation

For each exact site whose `ssl_enabled` value is true:

```bash
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key

openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -text | grep -E 'Public-Key|Subject:'

stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key
```

Expected private-key permissions:

```text
root:ssl-cert 640
```

Validate HTTPS behavior:

```bash
curl -k -I --resolve <site_name>:443:127.0.0.1 \
  https://<site_name>/
```

Expected results:

- HTTP status `200`
- `Strict-Transport-Security` header present
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Content-Security-Policy` header present

Validate HTTP redirection:

```bash
curl -I -H 'Host: <site_name>' http://127.0.0.1/
```

Expected results:

- HTTP status `301`
- `Location` points to `https://<site_name>/`

### Non-SSL site validation

For each exact site whose `ssl_enabled` value is false:

```bash
curl -I -H 'Host: <site_name>' http://127.0.0.1/
```

Expected result:

- HTTP status `200` when `<document_root>/index.html` exists

### Secret-file validation

```bash
test -f /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token
```

Expected result:

```text
root:root 600 /etc/nginx/secrets/site_token
```

Do not print the token contents.

### Kernel security validation

```bash
test -f /etc/sysctl.d/99-security.conf

grep -E 'rp_filter|accept_redirects|send_redirects|accept_source_route|log_martians|icmp_echo|disable_ipv6|tcp_syncookies|tcp_max_syn_backlog|tcp_synack_retries|tcp_syn_retries' \
  /etc/sysctl.d/99-security.conf

sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
```

### Network listening validation

```bash
ss -tlnp | grep ':22'
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
```

Expected listeners:

- `sshd` on TCP port `22`
- nginx on TCP port `80`
- nginx on TCP port `443` when SSL-enabled site configurations exist

### Log validation

```bash
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
journalctl -u nginx --since "15 minutes ago"
journalctl -u fail2ban --since "15 minutes ago"
journalctl -u sshd --since "15 minutes ago"
```

For each exact migrated site:

```bash
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

The exact site-specific commands cannot be expanded until the original `nginx_sites` data bag item names are obtained.