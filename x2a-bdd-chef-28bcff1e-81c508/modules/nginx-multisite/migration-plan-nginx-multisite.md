---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook provisions an Nginx web server with security hardening, Fail2ban, UFW firewall rules, SSL certificate generation, and data-bag-driven virtual hosts. Execution occurs in the order `security`, `nginx`, `ssl`, and `sites`. The `nginx_sites` data bag supplies site names, document roots, SSL flags, and source folders, but no concrete data-bag item names or values were included in the supplied analysis. The Ansible migration must therefore model those records as explicit variables and populate them from the original Chef data source before deployment. The source of `site_secret['token']` is unknown and must be verified from the original cookbook.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**
  - Purpose: Web server and virtual-host service
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP ports `80` and `443`, depending on rendered site configuration
  - Key Config:
    - Main configuration: `/etc/nginx/nginx.conf`
    - Security configuration: `/etc/nginx/conf.d/security.conf`
    - Available sites: `/etc/nginx/sites-available`
    - Enabled sites: `/etc/nginx/sites-enabled`
    - Service enabled and started

- **fail2ban**
  - Purpose: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: None
  - Key Config:
    - Package: `fail2ban`
    - Service enabled and started

- **ufw**
  - Purpose: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows SSH, HTTP, and HTTPS
  - Key Config:
    - Default incoming policy: deny
    - SSH allowed
    - HTTP allowed on TCP port `80`
    - HTTPS allowed on TCP port `443`
    - Firewall enabled

- **sshd**
  - Purpose: SSH access service hardened by the cookbook
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: Existing SSH port, normally TCP port `22`
  - Key Config:
    - `PermitRootLogin no`
    - `PasswordAuthentication no`
    - Chef declares the service with `action :nothing`; no explicit restart or reload is shown

- **nginx_sites data-bag records**
  - Purpose: Dynamic site document roots, SSL certificates, and virtual hosts
  - Location/Path:
    - Document root: supplied by each record’s `document_root`
    - Virtual-host configuration: `/etc/nginx/sites-available/<site_name>`
    - Enabled-site link: `/etc/nginx/sites-enabled/<site_name>`
  - Port/Socket: HTTP and optionally HTTPS
  - Key Config:
    - Required variables:
      - `site_name`
      - `document_root`
      - `ssl_enabled`
      - `site_folder`
    - Certificate path: `/etc/ssl/certs/<site_name>.crt`
    - Private-key path: `/etc/ssl/private/<site_name>.key`

  No concrete `nginx_sites` item names were supplied. No site names, document roots, source folders, or SSL flags may be invented. The Ansible variable must be populated from the original `nginx_sites` data bag before implementation.

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

No static `cookbook_file` source files were listed. The recipe references dynamic files such as `<site_folder>/index.html`, but the concrete source paths were not supplied and must be obtained from the original cookbook or data source.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role must preserve this execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Applies UFW operations in this order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Declares `sysctl -p /etc/sysctl.d/99-security.conf` as an inactive reload action. No notification causing it to run is shown.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` because `security.ssh.disable_root` is `true`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` because `security.ssh.password_auth` is `false`.
   - Declares the SSH service with `action :nothing`; no restart or reload is shown.
   - The structured summary does not evidence most resource modes, groups, or ownership values. Any such values used by Ansible must be verified from the detailed cookbook before being treated as source behavior.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the Nginx service.
   - Creates `/etc/nginx/secrets`.
   - Writes `site_secret['token']` to `/etc/nginx/secrets/site_token`.
   - The token source is unknown; it is not confirmed to be a data bag, encrypted data bag, Chef Vault item, attribute, or another backend.
   - The token deployment must use a protected variable source, `no_log: true`, owner `root`, group `root`, and mode `0600`.
   - Reads site records from `data_bag('nginx_sites')`.
   - For every concrete `nginx_sites` record imported into Ansible:
     - Creates the record’s `document_root`.
     - Deploys `<site_folder>/index.html` to `<document_root>/index.html`.
   - No concrete site records were supplied, so the `.each` loop cannot be expanded with actual names from the provided input.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Uses the attribute-defined certificate directory `/etc/ssl/certs`.
   - Uses the attribute-defined private-key directory `/etc/ssl/private`.
   - Reads site records from `data_bag('nginx_sites')`.
   - For every concrete site whose `ssl_enabled` value is `true`:
     - Generates `/etc/ssl/certs/<site_name>.crt`.
     - Generates `/etc/ssl/private/<site_name>.key`.
     - Uses a self-signed RSA 2048-bit certificate.
     - Uses a validity period of 365 days.
     - Uses no passphrase.
     - Sets the common name to the exact site name.
     - Uses the subject values:
       - Country: `US`
       - State: `Example`
       - Locality: `Example`
       - Organization: `Example Org`
       - Organizational unit: `IT`
       - Email: `admin@example.com`
     - Sets the private key to mode `0640`, owner `root`, and group `ssl-cert` if these values are confirmed from the detailed source.
   - The actual SSL-enabled site names were not supplied and must be obtained from the migrated data-bag records.
   - Ansible should use `community.crypto` modules where possible while preserving the certificate semantics above.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available`.
   - Creates `/etc/nginx/sites-enabled`.
   - Reads site records from `data_bag('nginx_sites')`.
   - For every concrete site record:
     - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>`.
     - Passes the following values to the template:
       - `server_name`: site name
       - `document_root`: record’s document root
       - `ssl_enabled`: record’s SSL flag
       - `cert_file`: `/etc/ssl/certs/<site_name>.crt`
       - `key_file`: `/etc/ssl/private/<site_name>.key`
     - Creates `/etc/nginx/sites-enabled/<site_name>` as a link to `/etc/nginx/sites-available/<site_name>`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - No concrete site names were supplied, so the dynamic template and link iterations cannot be expanded with actual names from the provided input.

## Dependencies

**External cookbook dependencies**: Not specified in the supplied metadata analysis. Do not assume external cookbook dependencies.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: configuration hardened, but no explicit restart, reload, or start action is shown

**External Chef data sources**:

- `nginx_sites` data bag
- `site_secret['token']`, with storage backend not identified by the supplied analysis

## Credentials

**Detection Summary**: One credential-like token was detected, in addition to locally generated TLS private keys. The token’s backend is unknown. No Vault, CyberArk, AWS Secrets Manager, Chef Vault, encrypted data bag, or other confirmed secret provider was identified.

**Source**:
  - **Provider**: Unknown; the supplied analysis does not identify whether `site_secret` is a regular data bag, encrypted data bag, Chef Vault item, attribute, or another Chef variable.
  - **URL**: Not applicable
  - **Path**: `cookbooks/nginx-multisite/recipes/nginx.rb`

### Nginx Site Token

- **Variable**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: External Chef variable or data-bag-like object; the exact backend is not shown
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **Destination requirements**:
  - Directory: `/etc/nginx/secrets`
  - File: `/etc/nginx/secrets/site_token`
  - Required protection: directory mode `0700`, file mode `0600`, owner `root`, group `root` if confirmed from the detailed source
- **Migration handling**:
  - Store the token in Ansible Vault or an approved external secret manager.
  - Use `no_log: true` on the deployment task.
  - Do not print the token during validation.

### SSL Private Keys

- **Variable(s)**: `/etc/ssl/private/<site_name>.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally with OpenSSL
- **Usage context**: Referenced by Nginx virtual-host configurations for SSL-enabled sites
- **Generation details**:
  - RSA 2048-bit
  - Self-signed
  - No passphrase
  - Valid for 365 days
- **Permissions**:
  - Mode `0640`
  - Owner `root`
  - Group `ssl-cert`
- **Site names**: Not supplied; derive from the migrated `nginx_sites` records.

### TLS Certificates

- **Variable(s)**: `/etc/ssl/certs/<site_name>.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally with OpenSSL
- **Usage context**: Referenced by Nginx virtual-host configurations for SSL-enabled sites
- **Certificate subject**:
  - Country: `US`
  - State: `Example`
  - Locality: `Example`
  - Organization: `Example Org`
  - Organizational unit: `IT`
  - Common name: exact site name
  - Email: `admin@example.com`

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets`
- `/etc/nginx/secrets/site_token`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-enabled/default`, which should be absent
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/etc/ssl/certs/<site_name>.crt` for each SSL-enabled migrated site
- `/etc/ssl/private/<site_name>.key` for each SSL-enabled migrated site
- `<document_root>/index.html` for each migrated site

The concrete site names and document roots must be obtained from the `nginx_sites` data-bag migration.

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443` when SSL-enabled sites are configured
- SSH: existing SSH port, normally TCP port `22`
- Unix sockets: none shown in the execution tree

**Templates rendered**:

- `fail2ban.jail.local.erb`: once, to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once, to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once, to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once, to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: once per migrated `nginx_sites` record, to `/etc/nginx/sites-available/<site_name>`

## Pre-flight checks

```bash
# Nginx and Fail2ban service status
systemctl status nginx --no-pager
systemctl status fail2ban --no-pager
systemctl is-enabled nginx
systemctl is-enabled fail2ban

# Nginx configuration validation
nginx -t
nginx -T

# Base and security configuration inspection
grep -E '^[[:space:]]*(user|worker_processes|events|http)' /etc/nginx/nginx.conf
grep -E '^[[:space:]]*(server_tokens|add_header|ssl_protocols|ssl_ciphers)' /etc/nginx/conf.d/security.conf

# HTTP endpoint
curl -I http://127.0.0.1/
ss -tlnp | grep ':80'

# HTTPS endpoint, when at least one SSL-enabled site exists
curl -k -I https://127.0.0.1/
ss -tlnp | grep ':443'

# Secret file checks without printing token contents
test -d /etc/nginx/secrets
test -f /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token

# Firewall checks
ufw status verbose
ufw status numbered

# Fail2ban checks
fail2ban-client status
fail2ban-client status sshd

# SSH configuration validation
sshd -t
sshd -T | grep -E 'permitrootlogin|passwordauthentication'
grep -E '^[[:space:]]*(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config

# Sysctl configuration checks
sysctl --system
sysctl -a | grep -E '(^|\.)(net|kernel)\.'
cat /etc/sysctl.d/99-security.conf

# Service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u ssh --no-pager -n 100
```

Expected security results:

```text
permitrootlogin no
passwordauthentication no
```

Expected secret-file result, subject to confirmation from the detailed source:

```text
root:root 600 /etc/nginx/secrets/site_token
```

Expected firewall behavior:

- Default incoming policy is deny.
- SSH is allowed.
- HTTP is allowed.
- HTTPS is allowed.
- UFW is active.

For every named site added to the Ansible `nginx_sites` variable, add an individually named check block using its actual values:

```bash
# Site: <site_name>
test -d "<document_root>"
test -f "<document_root>/index.html"
test -f "/etc/nginx/sites-available/<site_name>"
test -L "/etc/nginx/sites-enabled/<site_name>"
readlink -f "/etc/nginx/sites-enabled/<site_name>"
```

For every named site whose `ssl_enabled` value is `true`, also run:

```bash
# SSL site: <site_name>
test -f "/etc/ssl/certs/<site_name>.crt"
test -f "/etc/ssl/private/<site_name>.key"
stat -c '%U:%G %a %n' "/etc/ssl/private/<site_name>.key"
openssl x509 -in "/etc/ssl/certs/<site_name>.crt" -noout -subject -dates
```

Expected private-key permissions, subject to confirmation from the detailed source:

```text
root:ssl-cert 640
```

The exact expected sysctl keys must be taken from the rendered `sysctl-security.conf.erb`; they are not exposed in the supplied structured analysis. Inspect the Nginx log paths defined by the rendered configuration and site templates rather than assuming filenames not present in those templates.