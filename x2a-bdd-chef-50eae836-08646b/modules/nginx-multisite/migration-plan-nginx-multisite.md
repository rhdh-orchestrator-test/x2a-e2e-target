---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: `nginx-multisite` deploys nginx as a multisite web server, installs Fail2ban, UFW, OpenSSL, and CA certificates, applies SSH and kernel hardening, generates self-signed certificates for SSL-enabled data-bag sites, and publishes nginx virtual hosts on ports 80 and 443. Site names and values are loaded dynamically from the `nginx_sites` Chef data bag; the supplied analysis does not contain the actual item names. The Ansible migration must export those items before deployment and validation.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The cookbook dynamically loads site instances from the `nginx_sites` Chef data bag. Exact site names were not included in the supplied analysis and must not be invented.

Each exported site item requires:

- `id`: Site hostname, virtual-host name, and configuration filename
- `document_root`: Web content directory
- `ssl_enabled`: Boolean controlling certificate generation and HTTPS configuration

Each site uses the following derived paths:

- Certificate: `/etc/ssl/certs/<site_name>.crt`
- Private key: `/etc/ssl/private/<site_name>.key`
- Available-site configuration: `/etc/nginx/sites-available/<site_name>`
- Enabled-site link: `/etc/nginx/sites-enabled/<site_name>`
- Access log: `/var/log/nginx/<site_name>_access.log`
- Error log: `/var/log/nginx/<site_name>_error.log`

The Ansible migration must create an explicit inventory of the exported site names before implementation. The supplied plan cannot provide exact site-instance entries because those names and values are absent from the source analysis.

### Security instances

- **fail2ban**: Protects SSH and nginx-related services.
  - Package: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - State: Enabled and started

- **ufw**: Host firewall.
  - Package: `ufw`
  - Default incoming policy: Deny
  - Allowed ports: `22/tcp`, `80/tcp`, and `443/tcp`
  - State: Enabled

- **sshd**: Hardened SSH service.
  - `PermitRootLogin no`
  - `PasswordAuthentication no`
  - Restarted only after a hardening change

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

No provider file is used by the execution tree. The structurally detected `resources/lineinfile.rb` is not executed by the supplied recipe flow and is excluded.

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

No static file path is listed in the supplied directory listing. `recipes/nginx.rb` references dynamic `cookbook_file` sources in the form `<site_folder>/index.html`; these source files must be supplied separately in the Ansible role or content deployment mechanism.

## Module Explanation

The cookbook performs operations in this order:

1. `default.rb`
2. `security.rb`
3. `nginx.rb`
4. `ssl.rb`
5. `sites.rb`

### 1. Default entry recipe

**`default`** (`cookbooks/nginx-multisite/recipes/default.rb`):

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- Preserves the execution order of security, nginx, SSL, and site configuration.

### 2. Security configuration

**`security`** (`cookbooks/nginx-multisite/recipes/security.rb`):

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts `fail2ban`.
- Deploys `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Configures UFW with default deny and permits SSH, HTTP, and HTTPS.
- Enables UFW.
- Deploys `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Reloads the sysctl configuration with `sysctl -p /etc/sysctl.d/99-security.conf` after changes.
- Applies the configured SSH hardening commands to `/etc/ssh/sshd_config`.
- Delays an `sshd` restart until SSH configuration changes are complete.
- Delays Fail2ban restart when `/etc/fail2ban/jail.local` changes.

The security recipe contains **8 execute resources**:

- 5 UFW commands
- 1 sysctl reload command
- 2 SSH-hardening commands

The supplied execution summary confirms the templates and destinations but does not independently substantiate the detailed Fail2ban jail definitions or sysctl directives. Verify those settings against the template source before implementation.

### 3. nginx installation and base configuration

**`nginx`** (`cookbooks/nginx-multisite/recipes/nginx.rb`):

- Installs the `nginx` package.
- Deploys `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Deploys `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Enables and starts the nginx service.
- Delays nginx reload when either nginx template changes.
- Creates `/etc/nginx/secrets` with owner `root:root` and mode `0700`.
- Loads the encrypted Chef data-bag item `nginx_secrets/site`.
- Writes the `token` field to `/etc/nginx/secrets/site_token` with owner `root:root`, mode `0600`, and sensitive handling.
- Reads the `nginx_sites` data bag.
- Creates one document-root directory and one `index.html` file for each exported site item.
- Derives `site_folder` from the first component of the site hostname and uses `<site_folder>/index.html` as the dynamic cookbook-file source.

The supplied execution summary confirms the templates and destinations but does not independently verify the detailed nginx directives. Verify the worker settings, gzip settings, rate limits, TLS settings, and security directives against the template source.

### 4. SSL package, directories, and certificate generation

**`ssl`** (`cookbooks/nginx-multisite/recipes/ssl.rb`):

- Installs `openssl` and `ca-certificates`.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` with owner `root:root` and mode `0755`.
- Creates `/etc/ssl/private` with owner `root:ssl-cert` and mode `0710`.
- Reads the `nginx_sites` data bag.
- Generates certificates only for exported site items with `ssl_enabled == true`.
- Skips generation when both the certificate and private key already exist.
- Generates self-signed RSA 2048-bit certificates valid for 365 days.
- Uses the site hostname as the certificate Common Name.
- Sets generated private keys to owner `root:ssl-cert` and mode `0640`.
- Delays nginx reload after certificate generation.

The original command uses:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout <key_file> \
  -out <cert_file> \
  -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com"

chmod 640 <key_file>
chown root:ssl-cert <key_file>
```

The Ansible implementation should preferably use `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate`, or retain the command with an existence guard.

### 5. Site directories, virtual hosts, and enabled links

**`sites`** (`cookbooks/nginx-multisite/recipes/sites.rb`):

- Creates `/etc/nginx/sites-available` with owner `root:root` and mode `0755`.
- Creates `/etc/nginx/sites-enabled` with owner `root:root` and mode `0755`.
- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for each exported site item.
- Writes each site configuration to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
- Creates `/etc/nginx/sites-enabled/<site_name>` as a symbolic link to the corresponding available-site configuration.
- Deletes `/etc/nginx/sites-enabled/default`.
- Delays nginx reload after site configuration or link changes.

The static directory loop is expanded as:

1. `/etc/nginx/sites-available`
2. `/etc/nginx/sites-enabled`

Dynamic site loops cannot be expanded into exact names because the supplied analysis contains no `nginx_sites` item names. The Ansible role must obtain and record those names before deployment.

The site template receives:

- `server_name`: Site hostname
- `document_root`: Site document root
- `ssl_enabled`: SSL flag
- `cert_file`: `/etc/ssl/certs/<site_name>.crt`
- `key_file`: `/etc/ssl/private/<site_name>.key`

The execution summary confirms that `site.conf.erb` is rendered and identifies its destination, but does not independently verify the detailed HTTP, HTTPS, TLS, security-header, gzip, or access-control directives. Verify those settings against the template source before migration.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: Enabled and started
- `nginx`: Enabled and started
- `sshd`: Restarted only after SSH hardening changes

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The recipes use UFW and Debian-style nginx site directories while also referencing CentOS behavior. Verify package names, service names, filesystem paths, and firewall tooling for every target operating system.

## Attributes

Source file:

```text
cookbooks/nginx-multisite/attributes/default.rb
```

The supplied validation states that the attribute file contents were not included in the structured analysis. The following values and mappings are therefore **unverified and require source-file confirmation**:

| Chef attribute | Reported default | Proposed Ansible equivalent | Status |
|---|---:|---|---|
| `node['nginx']['ssl']['certificate_path']` | `/etc/ssl/certs` | `nginx_ssl_certificate_path` | Unverified |
| `node['nginx']['ssl']['private_key_path']` | `/etc/ssl/private` | `nginx_ssl_private_key_path` | Unverified |
| `node['security']['fail2ban']['enabled']` | `true` | `security_fail2ban_enabled` | Unverified |
| `node['security']['ufw']['enabled']` | `true` | `security_ufw_enabled` | Unverified |
| `node['security']['ssh']['disable_root']` | `true` | `security_ssh_disable_root` | Unverified |
| `node['security']['ssh']['password_auth']` | `false` | `security_ssh_password_auth` | Unverified |

Until `attributes/default.rb` is analyzed, preserve the behavior explicitly implemented by the recipes: Fail2ban and UFW are declared, SSH root login is disabled, and SSH password authentication is disabled.

## Credentials

**Detection Summary**: 1 credential detected across 1 recipe and 1 generated secret file.

**Source**:

- **Provider**: Chef encrypted data bag
- **URL**: None detected
- **Path**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Data bag**: `nginx_secrets`
- **Item**: `site`

### Nginx site token

- **Variable**: `site_secret['token']`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Destination**: `/etc/nginx/secrets/site_token`
- **Usage context**: Provides an nginx site token for deployed nginx configuration or site content.
- **Owner and group**: `root:root`
- **Mode**: `0600`
- **Chef handling**: Sensitive resource

The Ansible implementation must retrieve this value from Ansible Vault, an AAP credential, or an approved external secret manager. The task writing the token must use `no_log: true`.

### TLS private keys

Certificates and private keys are generated locally rather than retrieved from a secret provider:

- `/etc/ssl/certs/<site_name>.crt`
- `/etc/ssl/private/<site_name>.key`

Private-key protection:

- Owner: `root`
- Group: `ssl-cert`
- Mode: `0640`
- Private-key directory mode: `0710`

No CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, ordinary data bag, database credential, API key, or environment-variable secret reference was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-enabled/default` must be absent
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `<document_root>/index.html` for every exported site item
- `/etc/nginx/sites-available/<site_name>` for every exported site item
- `/etc/nginx/sites-enabled/<site_name>` for every exported site item
- `/var/log/nginx/<site_name>_access.log` for every exported site item
- `/var/log/nginx/<site_name>_error.log` for every exported site item
- `/etc/ssl/certs/<site_name>.crt` for every SSL-enabled exported site item
- `/etc/ssl/private/<site_name>.key` for every SSL-enabled exported site item

**Service endpoints to check**:

- SSH: TCP port `22`
- HTTP: TCP port `80`
- HTTPS: TCP port `443` when at least one site has `ssl_enabled: true`
- Unix sockets: None configured

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 time
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 time
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 time
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 time
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: once per exported `nginx_sites` item; exact count unavailable until the data-bag inventory is supplied

## Pre-flight checks

Before deployment, export the `nginx_sites` data-bag contents and record the exact site names, document roots, and SSL flags. The supplied analysis does not contain enough information to create named site-specific checks without inventing values.

```bash
# Service status
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl status sshd

# Configuration validation
nginx -t
nginx -T
sshd -t

# Firewall validation
ufw status verbose
ufw status numbered

# Required listeners
ss -tlnp | grep ':22 '
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Fail2ban validation
fail2ban-client ping
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# Kernel and SSH hardening
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config

# Global nginx files
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test ! -e /etc/nginx/sites-enabled/default

# Secret file; do not print its contents
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token
test -s /etc/nginx/secrets/site_token

# Site inventory and configuration
find /etc/nginx/sites-available -maxdepth 1 -type f -printf '%f\n'
find /etc/nginx/sites-enabled -maxdepth 1 -type l -printf '%f -> %l\n'

# TLS material
find /etc/ssl/certs -maxdepth 1 -name '*.crt' -printf '%f\n'
find /etc/ssl/private -maxdepth 1 -name '*.key' -printf '%f\n'

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
journalctl -u nginx --since "10 minutes ago"
journalctl -u fail2ban --since "10 minutes ago"
```

Expected results:

- nginx and Fail2ban are enabled and active.
- SSH configuration passes validation and the SSH service remains active.
- `nginx -t` succeeds.
- UFW is active with default incoming policy deny.
- Ports `22/tcp`, `80/tcp`, and `443/tcp` are permitted.
- The site token exists with ownership `root:root` and mode `0600`.
- The default nginx site is absent.
- Every exported site has a document root, `index.html`, available-site configuration, enabled-site link, and dedicated access and error logs.
- Every SSL-enabled exported site has a certificate and private key.
- Every HTTP request is routed to the correct site.
- SSL-enabled sites redirect HTTP to HTTPS and serve valid certificates.
- HTTP-only sites do not require certificate files.
- No nginx, Fail2ban, SSH, or firewall configuration errors are reported.