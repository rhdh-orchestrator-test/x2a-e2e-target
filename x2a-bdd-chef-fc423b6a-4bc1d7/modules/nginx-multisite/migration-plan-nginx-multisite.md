---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with dynamically defined virtual hosts sourced from the `nginx_sites` Chef data bag. It installs and configures nginx, Fail2ban, UFW, OpenSSL, SSH hardening, kernel security settings, self-signed certificates, virtual-host files, site document roots, and static `index.html` files. The exact site names, document roots, SSL flags, and static content sources are not present in the supplied analysis and must be provided explicitly before migration. Detailed template behavior, security attribute values, SSL path overrides, and the encrypted data-bag source require confirmation from the source files.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Primary web server and HTTPS termination service
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP `80`, TCP `443`; PID file `/run/nginx.pid`
  - Key Config: `/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/security.conf`, and enabled virtual-host files

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Protects SSH, HTTP, and HTTPS services
  - Key Config: Service state and jail configuration require confirmation from the template and attributes

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, TCP `80`, and TCP `443`
  - Key Config: Default incoming policy is intended to be deny; enabled state is configured by command execution

- **sshd**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: Root-login and password-authentication settings are controlled by `node['security']['ssh']` attributes and require confirmation

- **nginx_sites data-bag virtual hosts**: Dynamic nginx site instances
  - Location/Path: `/etc/nginx/sites-available/<site_name>` and `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: TCP `80`; TCP `443` when SSL is enabled
  - Key Config: Each item requires `id`, `document_root`, and `ssl_enabled`; exact item names and values are unavailable from the supplied analysis

The supplied analysis does not expose exact `nginx_sites` item names. No site names may be invented. Before implementation, provide an explicit site list containing the exact `id`, `document_root`, `ssl_enabled`, and static content source for every site.

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

No provider files are used by the execution tree. The analyzed `resources/lineinfile.rb` custom resource is not invoked by any recipe and is not an executed migration component.

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

No static files are listed because the directory listing contains no `files/default/*` or `files/*` entries. The `cookbook_file` resource expects dynamic source files such as `<site_folder>/index.html`; these files must be supplied separately in the Ansible role or deployment content.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The migration order is security, nginx installation and global configuration, SSL preparation, then virtual-host configuration.
   - Resources: four `include_recipe` calls.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `/etc/fail2ban/jail.local` from `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`.
   - Applies UFW default-deny policy and allows SSH, HTTP, and HTTPS.
   - Renders `/etc/sysctl.d/99-security.conf` from `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`.
   - Reloads sysctl settings after the sysctl template changes.
   - Applies conditional SSH hardening for `PermitRootLogin` and `PasswordAuthentication`; the controlling attribute values require confirmation from `cookbooks/nginx-multisite/attributes/default.rb`.
   - Restarts `sshd` after SSH hardening changes.
   - Resources: one package resource containing two packages, two service resources, two templates, five UFW `execute` resources, one sysctl reload `execute` resource, and two SSH hardening `execute` resources.
   - Total `execute` resources: eight.
   - Template-specific Fail2ban jail names, values, sysctl values, and other detailed settings require confirmation from the template contents.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `/etc/nginx/nginx.conf` from `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`.
   - Renders `/etc/nginx/conf.d/security.conf` from `cookbooks/nginx-multisite/templates/default/security.conf.erb`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads the encrypted `nginx_secrets` data-bag item named `site` if confirmed in the source analysis.
   - Writes the `token` value to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`.
   - Reads dynamic items from the `nginx_sites` data bag.
   - For every explicitly supplied site item, creates its configured document root with owner `nginx`, group `nginx`, and mode `0755`.
   - Derives the static source folder as the first component of the site name: `site_folder = site_name.split('.').first`.
   - Deploys `<site_folder>/index.html` to `<document_root>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - Dynamic iterations cannot be expanded because the exact data-bag item names are not present in the supplied analysis.
   - Resources: package, service, directory, file, dynamic directories, and dynamic `cookbook_file` operations.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Reads dynamic items from the `nginx_sites` data bag.
   - Processes only sites whose `ssl_enabled` value is true.
   - Generates a certificate and private key for each explicitly supplied SSL-enabled site.
   - Expected certificate paths are `/etc/ssl/certs/<site_name>.crt`; configured attribute overrides require confirmation.
   - Expected private-key paths are `/etc/ssl/private/<site_name>.key`; configured attribute overrides require confirmation.
   - Uses an execute resource named `generate-ssl-cert-<site_name>` for each SSL-enabled site.
   - The shell command uses OpenSSL to generate a 365-day, RSA 2048-bit self-signed certificate and sets the private key to mode `0640` with owner `root:ssl-cert`.
   - Certificate generation is skipped when both certificate and key already exist.
   - Certificate generation triggers a delayed nginx reload.
   - Dynamic iterations cannot be expanded because the exact SSL-enabled site names are not present in the supplied analysis.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Reads dynamic items from the `nginx_sites` data bag.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` for every explicitly supplied site.
   - Uses `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` as site template variables.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a link to `/etc/nginx/sites-available/<site_name>`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Changed site templates, links, and default-site removal trigger delayed nginx reloads.
   - Template behavior, including HTTP/HTTPS listeners, redirects, TLS settings, headers, rate limits, and log paths, requires confirmation from `cookbooks/nginx-multisite/templates/default/site.conf.erb`.
   - Dynamic iterations cannot be expanded because the exact site names are not present in the supplied analysis.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `sshd`: restarted only when SSH configuration changes.
- UFW: enabled through command execution.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Ansible collection dependencies**:

- `community.general` for UFW management.
- `community.crypto` for idempotent certificate generation, if selected.
- Built-in Ansible modules for packages, services, files, templates, links, and sysctl settings.

## Credentials

**Detection Summary**: 1 data-bag credential detected across 1 recipe and 1 destination file; generated TLS private keys are also sensitive locally generated files.

**Source**:

- **Provider**: Chef encrypted data bag provider, requiring confirmation from the source analysis
- **URL**: Not applicable
- **Path**: Encrypted data bag `nginx_secrets`, item `site`

### nginx site token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Destination**: `/etc/nginx/secrets/site_token`
- **Current storage**: Chef encrypted data bag
- **Source provider**: Chef encrypted data bag `nginx_secrets`, item `site`; the load operation and `token` field require confirmation from the structured analysis
- **Usage context**: The token is written as an nginx-related secret file
- **File protection**:
  - Owner: `root`
  - Group: `root`
  - Mode: `0600`
  - Chef resource marked `sensitive: true`

Store the equivalent token in Ansible Vault, AAP credentials, or an approved external secret manager. Deploy it with mode `0600`, owner `root`, and group `root`, and use `no_log: true` on tasks that consume it.

### TLS private keys

- **Variable(s)**: Generated per-site key path
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated on the target host
- **Usage context**: nginx HTTPS termination
- **Generation method**: OpenSSL self-signed certificate command
- **Expected path**: `/etc/ssl/private/<site_name>.key`; configured attribute overrides require confirmation
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`

The generated certificates are described as self-signed certificates with 365-day validity, RSA 2048-bit keys, subject organization `Example Org`, and email `admin@example.com`; these details require confirmation from the template and recipe contents.

### Other sensitive values

No database credentials, API keys, CyberArk references, Conjur variables, HashiCorp Vault paths, AWS Secrets Manager references, environment-variable secrets, or hardcoded passwords were identified.

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
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/etc/nginx/sites-available/<site_name>` for every explicitly supplied site
- `/etc/nginx/sites-enabled/<site_name>` for every explicitly supplied site
- `<document_root>/index.html` for every explicitly supplied site
- `/etc/ssl/certs/<site_name>.crt` for every explicitly supplied SSL-enabled site
- `/etc/ssl/private/<site_name>.key` for every explicitly supplied SSL-enabled site

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443` when an SSL-enabled site is configured
- nginx PID mechanism: `/run/nginx.pid`

**Logs to verify**:

- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/<site_name>_access.log`
- `/var/log/nginx/<site_name>_error.log`
- `/var/log/auth.log`
- system journal for `fail2ban`
- system journal for `nginx`
- system journal for `sshd`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: one render per explicitly supplied site
- Dynamic `index.html` deployment: one operation per explicitly supplied site

The exact number and names of dynamic renders cannot be determined until the `nginx_sites` item names and values are supplied.

## Pre-flight checks

```bash
# Confirm required packages
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Confirm service state
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# Validate nginx configuration
nginx -t
nginx -T | grep -E 'include /etc/nginx/(conf.d|sites-enabled)'

# Confirm firewall policy and allowed services
ufw status verbose
ufw status numbered

# Validate SSH configuration
sshd -t
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config
systemctl is-active sshd

# Validate Fail2ban configuration
fail2ban-client status
cat /etc/fail2ban/jail.local

# Validate sysctl configuration
sysctl -p /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# Validate secret-file permissions without printing secret contents
stat -c '%U %G %a %n' /etc/nginx/secrets
stat -c '%U %G %a %n' /etc/nginx/secrets/site_token

# Confirm listeners
ss -tlnp | grep -E ':(22|80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN
```

For every explicitly supplied non-SSL site, replace `<site_name>` and `<document_root>` with the exact configured values:

```bash
test -f /etc/nginx/sites-available/<site_name>
test -L /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>
test -f <document_root>/index.html

curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -s -H 'Host: <site_name>' http://127.0.0.1/ | head
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

For every explicitly supplied SSL-enabled site, replace `<site_name>` with the exact configured value:

```bash
test -f /etc/ssl/certs/<site_name>.crt
test -f /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
stat -c '%U %G %a %n' /etc/ssl/private/<site_name>.key

curl -k -I -H 'Host: <site_name>' https://127.0.0.1/
curl -I -H 'Host: <site_name>' http://127.0.0.1/
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

Expected SSL-site results:

- The certificate and private key exist.
- The private key is owned by `root:ssl-cert` with mode `640`.
- HTTPS responds successfully.
- HTTP redirects to HTTPS if that behavior is confirmed in `site.conf.erb`.
- The HTTPS response includes the configured TLS and security behavior.

The migration cannot be considered complete until the actual `nginx_sites` item names, document roots, SSL flags, static content sources, security attributes, template behavior, and encrypted data-bag source have been supplied and individually validated.