---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx as a multi-site web server on Ubuntu 18.04+ or CentOS 7+, installs fail2ban, UFW, OpenSSL, and CA certificates, applies SSH and kernel security hardening, creates nginx global and per-site configurations, and optionally generates self-signed certificates. Site definitions are loaded dynamically from the Chef `nginx_sites` data bag, while the nginx site token is loaded from the encrypted `nginx_secrets/site` data bag. The supplied analysis does not expose the individual site item names, document roots, or SSL flags; these values must be supplied as migration input and must not be invented.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

No exact site instance names are available in the supplied analysis. The migration must define one explicit site entry for every item in the Chef `nginx_sites` data bag with the following fields:

- `id`
- `document_root`
- `ssl_enabled`

Each configured site requires:

- A document-root directory owned by `nginx:nginx` with mode `0755`
- A static `index.html` owned by `nginx:nginx` with mode `0644`
- An nginx configuration at `/etc/nginx/sites-available/<site_name>`
- A symlink at `/etc/nginx/sites-enabled/<site_name>`
- A certificate at `/etc/ssl/certs/<site_name>.crt` when SSL is enabled
- A private key at `/etc/ssl/private/<site_name>.key` when SSL is enabled

**Site data source**: Chef data bag `nginx_sites`

**HTTP endpoint**: TCP port `80` as specified by the nginx configuration

**HTTPS endpoint**: TCP port `443` as specified by the nginx configuration

**SSH endpoint**: TCP port `22`

### Security Services

- **fail2ban**: Installed, enabled, and started; configuration at `/etc/fail2ban/jail.local`
- **ufw**: Installed, configured with a default deny policy, permits SSH/HTTP/HTTPS, and is enabled
- **sshd**: Root login is disabled and password authentication is disabled by default; the cookbook does not enable or start the service

## File Structure

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

No provider files are used by the execution tree.

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

No static files are listed in the supplied directory analysis. The `cookbook_file` resource dynamically references `<site_folder>/index.html`; the source files must be supplied separately for the Ansible migration.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)
2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)
3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

### 1. Default Recipe (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`
- Includes `nginx-multisite::nginx`
- Includes `nginx-multisite::ssl`
- Includes `nginx-multisite::sites`
- Preserves the execution order of security hardening, nginx configuration, SSL setup, and site configuration

### 2. Security Recipe (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs `fail2ban` and `ufw`
- Enables and starts the `fail2ban` service
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`
- Configures fail2ban defaults and nginx/SSH protection; detailed template settings must be verified against the source template
- Applies UFW default deny policy
- Allows SSH, HTTP, and HTTPS
- Enables UFW
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`
- Reloads the configured sysctl values after the sysctl file changes
- Sets `PermitRootLogin no` when `security.ssh.disable_root` is `true`
- Sets `PasswordAuthentication no` when `security.ssh.password_auth` is `false`
- Provides an `sshd` notification target; SSH restart behavior must be verified against the source resources
- Resource totals: 1 package resource containing 2 packages, 2 service resources, 2 template resources, 6 unconditional execute resources, and 2 conditional execute resources

### 3. nginx Recipe (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`
- Configures worker processes, worker connections, logging, gzip, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`; exact template behavior must be verified
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`
- Configures nginx security and TLS settings defined by the source template; exact values must be verified
- Enables and starts the `nginx` service
- Creates `/etc/nginx/secrets` owned by `root:root` with mode `0700`
- Loads `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`
- Writes `site_secret['token']` to `/etc/nginx/secrets/site_token` owned by `root:root` with mode `0600`
- Iterates over the item names returned by `data_bag('nginx_sites')`
- For every supplied site item:
  - Reads the item using `data_bag_item('nginx_sites', item_name)`
  - Uses `site['id']` as the site name
  - Creates `site['document_root']` recursively with owner `nginx`, group `nginx`, and mode `0755`
  - Deploys `<site_folder>/index.html` to `<document_root>/index.html` with owner `nginx`, group `nginx`, and mode `0644`
  - Uses the first dot-separated component of the site name as `site_folder`
- The exact site names and resulting loop expansions are unavailable and must be populated from the data bag before migration

### 4. SSL Recipe (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs `openssl` and `ca-certificates`
- Creates the `ssl-cert` group
- Creates `/etc/ssl/certs` owned by `root:root` with mode `0755`
- Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`
- Iterates over the items returned by `data_bag('nginx_sites')`
- Skips items whose `ssl_enabled` value is false
- For every supplied SSL-enabled site:
  - Generates `/etc/ssl/certs/<site_name>.crt`
  - Generates `/etc/ssl/private/<site_name>.key`
  - Uses a 365-day, RSA 2048-bit self-signed certificate
  - Uses the site name in the certificate subject common name
  - Sets the private key to `root:ssl-cert` with mode `0640`
  - Does not regenerate the certificate and key when both already exist
- The exact SSL-enabled site names cannot be expanded until the `nginx_sites` data is supplied
- Self-signed certificate behavior is development-oriented and should be replaced with approved certificate management for production deployments

### 5. Sites Recipe (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Creates `/etc/nginx/sites-available` owned by `root:root` with mode `0755`
- Creates `/etc/nginx/sites-enabled` owned by `root:root` with mode `0755`
- Iterates over the items returned by `data_bag('nginx_sites')`
- For every supplied site item:
  - Uses `site['id']` as the site name
  - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`
  - Passes the site name, document root, SSL flag, certificate path, and private-key path to the template
  - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to `/etc/nginx/sites-available/<site_name>`
- Deletes `/etc/nginx/sites-enabled/default`
- The template provides HTTP and conditional HTTPS virtual-host behavior; exact directives must be verified against the source template
- The exact site names and template/link loop expansions cannot be listed until the data bag contents are supplied

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: Enabled and started; restarted when its configuration changes if confirmed by the source resource
- `nginx`: Enabled and started; reload behavior for configuration, certificate, template, and link changes must be verified
- `sshd`: Not enabled or started by this cookbook; configuration changes may require a restart

## Credentials

**Detection Summary**: 3 credential or sensitive-data categories detected across 4 files and 2 Chef data sources.

**Source**:

- **Provider**: N/A — no custom provider files were analyzed
- **URL**: None detected
- **Path**: Chef data bags `nginx_secrets/site` and `nginx_sites`

### Site Token

- **Variable**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Source provider**: N/A — no provider files were analyzed
- **Current storage**: Chef encrypted data bag `nginx_secrets`, item `site`
- **Destination**: `/etc/nginx/secrets/site_token`
- **Ownership and mode**: `root:root`, `0600`
- **Usage context**: Local nginx-related site token file; consumption by the supplied templates is not shown
- **Migration storage**: Ansible Vault or an approved external secrets system
- **Migration handling**: Write the token with `no_log: true`

### nginx Site Definitions

- **Variable/data source**: `data_bag('nginx_sites')` and `data_bag_item('nginx_sites', item_name)`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Source provider**: N/A — no provider files were analyzed
- **Current storage**: Chef data bag `nginx_sites`
- **Usage context**: Site IDs, document roots, SSL flags, virtual-host generation, static content deployment, and certificate generation
- **Migration requirement**: Convert every data bag item into an explicit Ansible site variable containing `id`, `document_root`, and `ssl_enabled`
- **Known limitation**: Individual item names and values were not included in the supplied analysis

### TLS Private Keys

- **Variables**: `key_file`, derived from `site_name`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Source provider**: N/A — no provider files were analyzed
- **Current storage**: Generated locally by OpenSSL
- **Destination**: `/etc/ssl/private/<site_name>.key`
- **Usage context**: nginx TLS private key for SSL-enabled sites
- **Ownership and mode**: `root:ssl-cert`, `0640`

### TLS Certificates

- **Variables**: `cert_file`, derived from `site_name`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Source provider**: N/A — no provider files were analyzed
- **Current storage**: Generated locally by OpenSSL
- **Destination**: `/etc/ssl/certs/<site_name>.crt`
- **Usage context**: nginx TLS certificate for SSL-enabled sites
- **Validity**: 365 days
- **Certificate type**: Self-signed development certificate

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
/etc/ssl/certs
/etc/ssl/private
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

**Service endpoints to check**:

- TCP `22` — SSH
- TCP `80` — HTTP
- TCP `443` — HTTPS
- `/run/nginx.pid` — nginx PID file

**Templates rendered**:

- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: once per item in `nginx_sites`; exact count unavailable because item names were not supplied

## Pre-flight checks

Populate the explicit site list before running site-specific checks. The supplied analysis does not contain exact site names, document roots, or SSL flags, so no site can be named without inventing migration data.

```bash
# Package status
dpkg-query -W nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# nginx configuration
nginx -t
nginx -T
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -d /etc/nginx/sites-available
test -d /etc/nginx/sites-enabled

# Security configuration
fail2ban-client status
ufw status verbose
sysctl -p /etc/sysctl.d/99-security.conf
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config

# Firewall rules
ufw status numbered
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# nginx listeners and PID
ss -tlnp | grep ':22'
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
test -f /run/nginx.pid
cat /run/nginx.pid

# Secrets
test -d /etc/nginx/secrets
test -f /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/nginx/secrets
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token
```

For each explicitly supplied site, substitute its actual name and document root:

```bash
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
grep -E 'listen 80|listen 443|server_name|root ' \
  /etc/nginx/sites-available/<site_name>
test -d <document_root>
test -f <document_root>/index.html
stat -c '%U:%G %a %n' <document_root>/index.html
curl -I -H 'Host: <site_name>' http://127.0.0.1/
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

For each explicitly supplied site with `ssl_enabled: true`:

```bash
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key
curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
```

Expected results:

- nginx configuration validation succeeds
- nginx and fail2ban are active
- UFW is active with default deny policy
- TCP ports `22`, `80`, and `443` have the expected firewall allowances
- SSH configuration contains `PermitRootLogin no` and `PasswordAuthentication no`
- Every supplied site has a configuration, enabled-site symlink, document root, and static index file
- SSL-enabled sites have a certificate and private key with the expected ownership and permissions
- HTTP requests return site content or redirect to HTTPS according to the site SSL flag
- The site token is owned by `root:root`, has mode `0600`, and is not exposed in migration logs