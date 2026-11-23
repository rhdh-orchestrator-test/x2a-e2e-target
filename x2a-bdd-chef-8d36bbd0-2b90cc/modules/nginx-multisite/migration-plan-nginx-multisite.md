---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx multisite web server on Ubuntu `>= 18.04` or CentOS `>= 7.0`. It applies fail2ban, UFW, sysctl, and SSH hardening; installs and configures nginx; creates SSL directories and site directories; writes an encrypted site token to `/etc/nginx/secrets/site_token`; generates self-signed certificates for SSL-enabled sites; deploys site roots and `index.html` files; and renders one nginx virtual host per item in the external `nginx_sites` data bag. No concrete `nginx_sites` item names were supplied, so site-specific iterations remain inventory-driven and must be populated before migration execution.

## Service Type and Instances

**Service Type**: Web Server

**Supported Platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

No concrete nginx site instance names were supplied in the analyzed data. The migration must receive the complete `nginx_sites` data-bag contents as inventory variables or vaulted data. Each item must provide:

- `id`
- `document_root`
- `ssl_enabled`

The configured service endpoints are:

- **nginx HTTP**: TCP port `80`
- **nginx HTTPS**: TCP port `443` when an SSL-enabled site is configured
- **SSH**: TCP port `22`
- **fail2ban**: Protects SSH and nginx log sources; it does not expose a service port

Security defaults:

- fail2ban enabled
- UFW enabled with incoming traffic denied by default
- SSH root login disabled
- SSH password authentication disabled

## File Structure

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

No provider file is used by the execution tree. The analyzed `resources/lineinfile.rb` custom resource is not invoked by the listed recipes and is excluded from the migration execution file list.

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

No static `files/default/*` or `files/*` files are listed in the supplied cookbook structure. The Chef `cookbook_file` resource references site-specific `index.html` files, but those files must be supplied separately to the Ansible role.

## Module Explanation

The cookbook performs operations in this order:

1. `nginx-multisite::default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Has no direct package, file, or service resources.
   - Preserves the execution order required for security configuration, nginx installation, SSL preparation, and site configuration.
   - Iterations: none.

2. `nginx-multisite::security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures UFW with default deny incoming policy and allows SSH, HTTP, and HTTPS.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies sysctl settings through `sysctl -p /etc/sysctl.d/99-security.conf` when the configuration changes.
   - Disables root SSH login when `security.ssh.disable_root` is true.
   - Disables SSH password authentication when `security.ssh.password_auth` is false.
   - Restarts `sshd` only when SSH hardening changes.
   - Resources: one package declaration, two service declarations, two templates, and eight execute resources.
   - Iterations: none.

   The structured execution summary confirms the template destinations and resources. Detailed fail2ban jail values and sysctl directives require manual verification against the template contents before migration.

3. `nginx-multisite::nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs `nginx`.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root:root` and mode `0700`.
   - Loads `nginx_secrets`, item `site`, through `Chef::EncryptedDataBagItem.load(...)`.
   - Writes `site_secret['token']` to `/etc/nginx/secrets/site_token` with owner `root:root` and mode `0600`.
   - Reads site definitions from the external `nginx_sites` data bag.
   - For each supplied data-bag item, sets `site_name = site['id']`, creates `site['document_root']` with owner `nginx:nginx` and mode `0755`, and deploys `<document_root>/index.html` with owner `nginx:nginx` and mode `0644`.
   - Derives the static file source directory as `site_name.split('.').first`.
   - Iterations: no concrete site names were supplied; the migration must expand this operation from the supplied `nginx_sites` inventory.

   Detailed nginx directives, including TLS settings, request limits, security headers, gzip, and logging behavior, require manual verification against the template contents before migration.

4. `nginx-multisite::ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with owner `root:ssl-cert` and mode `0710`.
   - Reads the external `nginx_sites` data bag.
   - For each supplied item with `ssl_enabled: true`, generates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Uses a self-signed RSA certificate generated by `openssl`.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Skips certificate generation when both certificate and key already exist.
   - Iterations: no concrete SSL-enabled site names were supplied; the migration must expand this operation from the supplied `nginx_sites` inventory.

5. `nginx-multisite::sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` with owner `root:root` and mode `0755`.
   - Reads the external `nginx_sites` data bag.
   - For each supplied item, renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - Passes the site name, document root, SSL state, certificate path, and private-key path to the template.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to the corresponding available-site file.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Runs `nginx -t` before reloading nginx after site configuration changes.
   - Iterations: no concrete site names were supplied; the migration must expand this operation from the supplied `nginx_sites` inventory.

   Detailed virtual-host directives, including redirects, TLS behavior, headers, HSTS, gzip, and `try_files`, require manual verification against `cookbooks/nginx-multisite/templates/default/site.conf.erb`.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

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
- UFW: enabled through firewall commands

**External data sources**:

- Encrypted data bag: `nginx_secrets`, item `site`
- Standard data bag: `nginx_sites`

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe. The cookbook also uses an encrypted data bag for the credential and a standard data bag for site definitions.

**Source**:

- **Provider**: None detected; no provider files were analyzed or used. The token is loaded directly with `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`.
- **URL**: Not applicable
- **Path**: Encrypted Chef data bag `nginx_secrets`, item `site`

### Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Usage context**: Written to `/etc/nginx/secrets/site_token` for external application or site consumption; no consumer is shown in the analyzed recipes.
- **Destination**: `/etc/nginx/secrets/site_token`
- **Destination permissions**: `root:root`, mode `0600`
- **Ansible storage**: Ansible Vault or an external secret manager
- **Output handling**: The Ansible task must use `no_log: true`.

### Site Data-Bag Values

- **Variable(s)**: `site['id']`, `site['document_root']`, `site['ssl_enabled']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Standard Chef data bag `nginx_sites`
- **Usage context**: Site naming, document-root creation, SSL enablement, virtual-host rendering, and certificate naming
- **Sensitive status**: Configuration data, not credentials, unless additional undisclosed sensitive fields exist in the data bag

### TLS Material

- **Generated files**:
  - `/etc/ssl/certs/<site_name>.crt`
  - `/etc/ssl/private/<site_name>.key`
- **Source**: Locally generated with `openssl`
- **Current storage**: Filesystem
- **Usage context**: nginx HTTPS virtual hosts
- **Certificate type**: Self-signed RSA certificate with a `365`-day validity period
- **Private-key permissions**: `root:ssl-cert`, mode `0640`

No HashiCorp Vault, CyberArk, Conjur, AWS Secrets Manager, or environment-variable secret references were detected.

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
/etc/ssl/certs
/etc/ssl/private
/var/log/nginx/access.log
/var/log/nginx/error.log
<document_root>/index.html
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
```

No concrete site names were provided, so the placeholder paths must be replaced with the exact `id` values from `nginx_sites`.

**Service endpoints to check**:

- TCP `22`: SSH
- TCP `80`: nginx HTTP
- TCP `443`: nginx HTTPS when an SSL-enabled site exists
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
  - Renders once to `/etc/fail2ban/jail.local`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
  - Renders once to `/etc/nginx/nginx.conf`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`
  - Renders once to `/etc/nginx/conf.d/security.conf`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`
  - Renders once to `/etc/sysctl.d/99-security.conf`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Renders once per supplied `nginx_sites` item
  - Destination: `/etc/nginx/sites-available/<site_name>`

## Pre-flight checks

Replace `<site_name>` and `<document_root>` with every exact site value supplied through `nginx_sites`. No individual site checks can be enumerated until that inventory is available.

```bash
# Security services
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Firewall
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# SSH hardening
grep -E '^[# ]*PermitRootLogin|^[# ]*PasswordAuthentication' /etc/ssh/sshd_config
sshd -t
systemctl status sshd

# Sysctl
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
cat /etc/sysctl.d/99-security.conf

# nginx service and syntax
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
nginx -T
cat /etc/nginx/nginx.conf
cat /etc/nginx/conf.d/security.conf

# Listening ports
ss -tlnp | grep -E ':80|:443'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Site configuration; execute with every supplied site name
ls -l /etc/nginx/sites-available/<site_name>
ls -l /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -E 'listen|server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/<site_name>

# Confirm the default site was removed
test ! -e /etc/nginx/sites-enabled/default

# SSL material; execute for every SSL-enabled site
ls -l /etc/ssl/certs/<site_name>.crt
ls -l /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key

# Document root and static content; execute with every supplied site
ls -ld <document_root>
ls -l <document_root>/index.html
stat -c '%U:%G %a %n' <document_root>/index.html

# Secret file; never print its contents
ls -l /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token

# Site HTTP checks; execute with every supplied site
curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

Expected results:

- `fail2ban` and nginx are enabled and active.
- UFW is active with incoming traffic denied by default.
- TCP ports `22`, `80`, and `443` are allowed as configured.
- SSH contains `PermitRootLogin no` and `PasswordAuthentication no`.
- `sshd -t` and `nginx -t` succeed.
- Each supplied site has the expected available-site file and symlink.
- SSL-enabled sites have valid certificate and key files owned and permissioned as configured.
- Each document root is owned by `nginx:nginx` with mode `755`.
- Each `index.html` is owned by `nginx:nginx` with mode `644`.
- `/etc/nginx/secrets/site_token` is owned by `root:root` with mode `600`.
- No secret contents are printed during validation.
