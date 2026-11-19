---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: `nginx-multisite` installs and configures nginx, Fail2ban, UFW, SSH hardening, and kernel security settings. It creates dynamic nginx virtual hosts, document roots, static index files, and optional self-signed TLS certificates from records in the `nginx_sites` Chef data bag. The supplied cookbook analysis does not expose the individual site names or confirm the contents of the attributes, template, or static-file sources; those inputs must be verified before the Ansible inventory and per-site variables are finalized.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**
  - Purpose: Web server hosting dynamically configured sites
  - Package: `nginx`
  - Configuration: `/etc/nginx/nginx.conf`
  - Security configuration: `/etc/nginx/conf.d/security.conf`
  - Site configurations: `/etc/nginx/sites-available/<site_name>`
  - Enabled site links: `/etc/nginx/sites-enabled/<site_name>`
  - PID file: `/run/nginx.pid`
  - Ports: TCP `80`; TCP `443` for SSL-enabled sites
  - Service state: enabled and started
  - Reload behavior: configuration changes trigger a delayed reload

- **fail2ban**
  - Purpose: Intrusion prevention for SSH and nginx
  - Package: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Service state: enabled and started
  - Restart behavior: configuration changes trigger a delayed restart
  - Jail names and thresholds: require verification from `fail2ban.jail.local.erb`

- **ufw**
  - Purpose: Host firewall
  - Package: `ufw`
  - Default policy: deny, as implemented by the recipe
  - Allowed services: SSH, HTTP, and HTTPS
  - Firewall state: enabled
  - Idempotence checks: inspect current UFW status before applying changes

- **sshd**
  - Purpose: SSH access
  - Configuration: `/etc/ssh/sshd_config`
  - Intended settings:
    - `PermitRootLogin no`
    - `PasswordAuthentication no`
  - Service behavior: restart is delayed when either setting changes
  - Port: TCP `22`

- **sysctl security configuration**
  - Purpose: Kernel network-security hardening
  - Configuration: `/etc/sysctl.d/99-security.conf`
  - Reload command: `sysctl -p /etc/sysctl.d/99-security.conf`
  - Reload behavior: delayed reload when the configuration changes

- **Dynamic nginx sites**
  - Purpose: Per-site virtual hosts, document roots, static content, and optional TLS
  - Source: `nginx_sites` Chef data bag
  - Confirmed site fields used by the recipes:
    - `document_root`
    - `ssl_enabled`
  - Site-name source: the plan identifies `config['id']`, but this requires confirmation from the structured data
  - Exact site names: not present in the supplied analysis; they must be obtained before migration
  - HTTP port: `80`
  - HTTPS port: `443` when `ssl_enabled` is `true`
  - Certificate path: `/etc/ssl/certs/<site_name>.crt`
  - Private key path: `/etc/ssl/private/<site_name>.key`
  - Virtual host path: `/etc/nginx/sites-available/<site_name>`
  - Enabled link: `/etc/nginx/sites-enabled/<site_name>`
  - Document root: value of `document_root`
  - Static source pattern: `<first_component_of_site_name>/index.html`
  - Static destination: `<document_root>/index.html`
  - Site-specific access log: `/var/log/nginx/<site_name>_access.log`
  - Site-specific error log: `/var/log/nginx/<site_name>_error.log`

  Site-specific loops cannot be expanded because no `nginx_sites` item names were supplied. Do not invent site names. The Ansible migration must obtain the exact data bag item names and values before creating site definitions.

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

No static files under `files/default/*` or `files/*` are listed. The `cookbook_file` resources require site-specific `index.html` files, but their existence and exact paths are unresolved migration inputs.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes the four recipes in execution order:
     1. `nginx-multisite::security`
     2. `nginx-multisite::nginx`
     3. `nginx-multisite::ssl`
     4. `nginx-multisite::sites`
   - Ansible task order must preserve security, nginx, TLS, and site configuration in that sequence.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Delays a Fail2ban restart when the jail configuration changes.
   - Applies UFW default-deny policy.
   - Allows SSH, HTTP, and HTTPS through UFW.
   - Enables UFW after checking whether it is already active.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Delays `sysctl -p /etc/sysctl.d/99-security.conf` when the sysctl file changes.
   - Applies SSH hardening:
     - Replaces the `PermitRootLogin` setting with `PermitRootLogin no`.
     - Replaces the `PasswordAuthentication` setting with `PasswordAuthentication no`.
     - Skips each command when the desired line already exists.
     - Delays the `sshd` restart when either command changes.
   - Declares `service[sshd]` with action `nothing` as the notification target.
   - Template render counts:
     - `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once
     - `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once
   - The exact Fail2ban jail names, thresholds, and sysctl values require verification from the template contents.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Delays an nginx reload when either global configuration template changes.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads the encrypted Chef data bag item `nginx_secrets/site`.
   - Writes the `token` field to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`.
   - Uses sensitive logging for the site-token file resource.
   - Reads runtime site records from the `nginx_sites` data bag.
   - Creates each discovered site document root with owner `nginx`, group `nginx`, and mode `0755`.
   - Derives the static source directory from `site_name.split('.').first`.
   - Copies the corresponding site-specific `index.html` to `<document_root>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - The exact site names and static source files are not present in the supplied analysis and must be supplied separately.
   - Dynamic resources:
     - One document-root directory per `nginx_sites` item
     - One `cookbook_file` per `nginx_sites` item
   - Template render counts:
     - `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once
     - `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Reads site records from the `nginx_sites` data bag.
   - Runs certificate generation only for records with `ssl_enabled: true`.
   - Generates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - Uses a 2048-bit RSA key and a 365-day self-signed certificate.
   - Skips generation when both certificate and key already exist.
   - Sets the private key to owner `root`, group `ssl-cert`, and mode `0640`.
   - Delays an nginx reload after generating a certificate.
   - Dynamic resources:
     - One certificate-generation command per SSL-enabled site
   - Exact SSL-enabled site names are unavailable and must be obtained from `nginx_sites`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` for each discovered site.
   - Supplies the site template with:
     - `server_name`
     - `document_root`
     - `ssl_enabled`
     - `cert_file`
     - `key_file`
   - Sets virtual-host files to mode `0644`.
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symbolic link to the corresponding file in `sites-available`.
   - Delays nginx reloads after virtual-host or link changes.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Template and link loops cannot be expanded because exact site names were not supplied.
   - Template render count:
     - `cookbooks/nginx-multisite/templates/default/site.conf.erb`: once per `nginx_sites` item
   - The template’s detailed directives, including redirects, HTTP/2, HSTS, headers, TLS settings, and logging, require verification from the template contents.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution analysis.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd` as a delayed notification target

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The recipe explicitly uses UFW. CentOS targets commonly use firewalld instead, so platform-specific firewall handling must be decided before migration.

**Attribute verification required**:

The supplied validation does not confirm the contents of `cookbooks/nginx-multisite/attributes/default.rb`. Verify these values before implementation:

- `node['nginx']['ssl']['certificate_path']`
- `node['nginx']['ssl']['private_key_path']`
- `node['security']['fail2ban']['enabled']`
- `node['security']['ufw']['enabled']`
- `node['security']['ssh']['disable_root']`
- `node['security']['ssh']['password_auth']`

The recipe references these attributes, but the supplied analysis does not verify their defaults. The `enabled` attributes must not be treated as feature gates unless that behavior is intentionally introduced during migration.

## Credentials

**Detection Summary**: 1 explicit credential detected across 1 recipe and 1 destination file. Site data bag records may contain additional sensitive values, but none are shown in the supplied analysis.

**Source**:

- **Provider**: Chef encrypted data bag
- **Data bag**: `nginx_secrets`
- **Item**: `site`
- **Secret field**: `token`
- **Destination**: `/etc/nginx/secrets/site_token`

### Site token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag item loaded with `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`
- **Usage context**: Written as the nginx site token to `/etc/nginx/secrets/site_token`
- **Owner and group**: `root:root`
- **Mode**: `0600`
- **Ansible migration**: Store the value in Ansible Vault or an external secret manager and use `no_log: true` when writing the file.

### TLS private keys

- **Variables**: `key_file`, derived from `site_name`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL; not loaded from a data bag or vault
- **Usage context**: nginx TLS private key
- **Path pattern**: `/etc/ssl/private/<site_name>.key`
- **Owner and group**: `root:ssl-cert`
- **Mode**: `0640`
- **Ansible migration**: Use `community.crypto.openssl_privatekey` or preserve the existing OpenSSL command. Do not expose key material in task output.

### TLS certificates

- **Variables**: `cert_file`, derived from `site_name`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally as self-signed certificates
- **Usage context**: nginx TLS certificate
- **Path pattern**: `/etc/ssl/certs/<site_name>.crt`
- **Properties**:
  - RSA key size: `2048`
  - Validity: `365` days
  - Certificate type: self-signed
- **Ansible migration**: Preserve the self-signed behavior unless a separate certificate-authority or ACME migration is approved.

No HashiCorp Vault, CyberArk, AWS Secrets Manager, Conjur, environment-variable secrets, database passwords, or hardcoded API tokens were detected.

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
/var/log/nginx/access.log
/var/log/nginx/error.log
/run/nginx.pid
```

For every actual site name obtained from `nginx_sites`, also verify:

```text
<document_root>
<document_root>/index.html
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
```

Certificate and key paths apply only to SSL-enabled sites.

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443` for SSL-enabled sites
- SSH: TCP port `22`
- Unix socket: none specified
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: once
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: once
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: once per `nginx_sites` item

The numeric render count for `site.conf.erb` cannot be determined until the data bag item names are supplied.

## Pre-flight checks:

```bash
# Service status
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-active sshd

# Fail2ban configuration
fail2ban-client status
fail2ban-client status sshd

# Add these checks when the verified jail names are available:
# fail2ban-client status <verified_jail_name>

# UFW state and rules
ufw status verbose
ufw status numbered

# SSH configuration validation
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config
sshd -t

# Kernel configuration reload and validation
sysctl -p /etc/sysctl.d/99-security.conf

# nginx configuration validation
nginx -t
nginx -T

# Listening ports
ss -tlnp | grep -E ':(22|80|443)\b'

# Global nginx files
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -f /run/nginx.pid

# Secret metadata; do not print the token
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token

# Default site must be absent
test ! -e /etc/nginx/sites-enabled/default
```

For each actual site name and site record obtained from `nginx_sites`, run a named check using its verified values:

```bash
# Replace placeholders with the verified site name and document root.
ls -ld <document_root>
ls -l <document_root>/index.html
ls -l /etc/nginx/sites-available/<site_name>
ls -l /etc/nginx/sites-enabled/<site_name>
readlink -f /etc/nginx/sites-enabled/<site_name>

grep -E 'listen|server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/<site_name>

curl -I -H 'Host: <site_name>' http://127.0.0.1/
```

For an SSL-enabled site, also run:

```bash
ls -l /etc/ssl/certs/<site_name>.crt
ls -l /etc/ssl/private/<site_name>.key
openssl x509 -in /etc/ssl/certs/<site_name>.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
```

Expected SSL-enabled-site results:

- HTTP is available on port `80`.
- HTTPS is available on port `443`.
- The certificate and private key exist.
- The private key is owned by `root:ssl-cert` with mode `0640`.
- The HTTPS request succeeds when the site has static content.
- The site’s certificate and key paths match the verified site name.

For a non-SSL site, verify:

- HTTP is available on port `80`.
- The site does not require a certificate or private key.
- The site’s document root and `index.html` exist.
- The HTTP request returns the expected static-file response.

Check service logs after testing:

```bash
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
```

For each actual site name, also inspect:

```bash
tail -n 50 /var/log/nginx/<site_name>_access.log
tail -n 50 /var/log/nginx/<site_name>_error.log
```

The site names, document roots, SSL flags, and static-file paths must be resolved before these per-site checks can be executed.