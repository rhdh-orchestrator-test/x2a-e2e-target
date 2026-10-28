---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and index files; generates self-signed certificates; renders and enables per-site Nginx configurations; removes the default site; and applies firewall, SSH, Fail2ban, and kernel security settings. The Ansible implementation must preserve the recipe order: security, Nginx installation and base configuration, SSL certificate generation, and site activation.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTPS port 443; HTTP port 80 if configured by the rendered template
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`

- **ci.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTPS port 443; HTTP port 80 if configured by the rendered template
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`

- **status.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTPS port 443; HTTP port 80 if configured by the rendered template
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`

**Security configuration areas**:

- **fail2ban**: Enabled; installs and starts `fail2ban`; renders `/etc/fail2ban/jail.local`
- **ufw**: Enabled; installs UFW; applies default-deny policy; allows SSH, HTTP, and HTTPS; enables the firewall
- **ssh**: Disables root login and password authentication by configuring `/etc/ssh/sshd_config`; defines an SSH service resource with action `nothing`

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

No static files are listed in the supplied directory listing. The cookbook references dynamically named `cookbook_file` resources for the following index files; verify that their source files exist before implementing Ansible copy tasks:

```text
test.cluster.local/index.html
ci.cluster.local/index.html
status.cluster.local/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes the four operational recipes in execution order.
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible play should preserve this ordering with imported task files or equivalent task blocks.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Applies UFW commands in this order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies the settings with `sysctl -p /etc/sysctl.d/99-security.conf` when the configuration changes. The Chef execution tree defines the reload command with action `nothing`.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` because `security.ssh.password_auth` is `false`.
   - Defines `service[ssh]` with action `nothing`; the Ansible implementation should reload or restart SSH when either setting changes.
   - Uses the `fail2ban`, `ufw`, and `ssh` service resources as described by the execution tree.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package without forcing a version.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates the document root and deploys an index file for `test.cluster.local`:
     - Creates `/opt/server/test`.
     - Copies `test.cluster.local/index.html` to `/opt/server/test/index.html`.
     - Sets the index file mode to `0644`.
   - Creates the document root and deploys an index file for `ci.cluster.local`:
     - Creates `/opt/server/ci`.
     - Copies `ci.cluster.local/index.html` to `/opt/server/ci/index.html`.
     - Sets the index file mode to `0644`.
   - Creates the document root and deploys an index file for `status.cluster.local`:
     - Creates `/opt/server/status`.
     - Copies `status.cluster.local/index.html` to `/opt/server/status/index.html`.
     - Sets the index file mode to `0644`.
   - The site loop executes exactly three directory resources and three `cookbook_file` resources.
   - No `group[www-data]` resource is confirmed by the supplied execution tree; it must not be treated as an analyzed Chef resource.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private`.
   - Any directory mode or group ownership requirements must be verified against the underlying recipe because they are not fully present in the supplied execution tree.
   - Generates a self-signed certificate and private key for `test.cluster.local`:
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
   - Generates a self-signed certificate and private key for `ci.cluster.local`:
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
   - Generates a self-signed certificate and private key for `status.cluster.local`:
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
   - Uses an OpenSSL command equivalent to:
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout <key_file> \
       -out <cert_file> \
       -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com"
     chmod 640 <key_file>
     chown root:ssl-cert <key_file>
     ```
   - Certificates are self-signed X.509 certificates with 2048-bit RSA keys and 365-day validity.
   - Private keys are unencrypted because `-nodes` is used.
   - Private keys are intended to use mode `0640`, owner `root`, and group `ssl-cert` based on the OpenSSL command.
   - Use idempotent Ansible certificate generation with `creates`, certificate modules, or explicit existence checks.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders and enables the site configuration for `test.cluster.local`:
     - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
     - Destination: `/etc/nginx/sites-available/test.cluster.local`
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
     - Mode: `0644`
     - Symlink: `/etc/nginx/sites-enabled/test.cluster.local`
   - Renders and enables the site configuration for `ci.cluster.local`:
     - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
     - Destination: `/etc/nginx/sites-available/ci.cluster.local`
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
     - Mode: `0644`
     - Symlink: `/etc/nginx/sites-enabled/ci.cluster.local`
   - Renders and enables the site configuration for `status.cluster.local`:
     - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
     - Destination: `/etc/nginx/sites-available/status.cluster.local`
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
     - Mode: `0644`
     - Symlink: `/etc/nginx/sites-enabled/status.cluster.local`
   - Deletes `/etc/nginx/sites-enabled/default`.
   - The site loop executes exactly three templates and three symlinks, followed by one default-site deletion.
   - Runs `nginx -t` after site changes and reloads Nginx only after successful validation.

## Dependencies

**External cookbook dependencies**: None specified.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**: `nginx`, `fail2ban`, `ssh`

The `ssh` service resource has action `nothing`; the execution tree does not show an SSH start or enable action.

## Credentials

**Detection Summary**: Two generated TLS artifact categories detected across `cookbooks/nginx-multisite/recipes/ssl.rb` and `cookbooks/nginx-multisite/recipes/sites.rb`. No application credentials, data bags, vault references, API keys, database passwords, or environment-variable secrets were detected.

**Source**:
  - **Provider**: None detected
  - **URL**: Not applicable
  - **Path**: Generated locally under `/etc/ssl/certs` and `/etc/ssl/private`

### TLS Private Keys

- **Variable(s)**: Dynamic `key_file` values derived from `node['nginx']['ssl']['private_key_path']` and the site name
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: Nginx TLS private keys for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Storage paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Protection**: Intended mode `0640`, owner `root`, and group `ssl-cert`; verify directory ownership and modes against the source recipe

### TLS Certificates

- **Variable(s)**: Dynamic `cert_file` values derived from `node['nginx']['ssl']['certificate_path']` and the site name
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: Nginx HTTPS virtual-host certificates
- **Storage paths**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Certificate properties**: Self-signed, RSA 2048-bit, valid for 365 days, with the matching site name as the Common Name and `admin@example.com` in the subject

No external certificate authority, vault, or certificate secret source is detected.

## Checks for the Migration

**Files to verify**:

- Cookbook source files:
  - `cookbooks/nginx-multisite/recipes/default.rb`
  - `cookbooks/nginx-multisite/recipes/security.rb`
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
  - `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
  - `cookbooks/nginx-multisite/templates/default/security.conf.erb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`
- Nginx configuration:
  - `/etc/nginx/nginx.conf`
  - `/etc/nginx/conf.d/security.conf`
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`
  - `/etc/nginx/sites-enabled/test.cluster.local`
  - `/etc/nginx/sites-enabled/ci.cluster.local`
  - `/etc/nginx/sites-enabled/status.cluster.local`
  - `/etc/nginx/sites-enabled/default` should not exist
- Document roots and index files:
  - `/opt/server/test`
  - `/opt/server/test/index.html`
  - `/opt/server/ci`
  - `/opt/server/ci/index.html`
  - `/opt/server/status`
  - `/opt/server/status/index.html`
- TLS files:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/certs/status.cluster.local.crt`
  - `/etc/ssl/private/status.cluster.local.key`
- Security files:
  - `/etc/fail2ban/jail.local`
  - `/etc/sysctl.d/99-security.conf`
  - `/etc/ssh/sshd_config`

**Service endpoints to check**: HTTP port 80 if configured; HTTPS port 443; SSH port 22 unless the existing SSH configuration uses another port; no Unix sockets are specified.

**Templates rendered**:

- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl status nginx
systemctl is-enabled nginx

# Configuration validation
nginx -t
sshd -t
sysctl -p /etc/sysctl.d/99-security.conf

# Base configuration files
ls -l /etc/nginx/nginx.conf
ls -l /etc/nginx/conf.d/security.conf
ls -l /etc/fail2ban/jail.local
ls -l /etc/sysctl.d/99-security.conf
ls -l /etc/ssh/sshd_config

# Firewall checks
ufw status verbose
ufw status numbered

# SSH hardening checks
grep -E '^[#]*PermitRootLogin|^[#]*PasswordAuthentication' /etc/ssh/sshd_config

# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Listener checks
ss -tlnp | grep -E ':(80|443)\b'
```

### `test.cluster.local`

```bash
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
ls -l /etc/nginx/sites-available/test.cluster.local
ls -l /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
ls -l /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
```

Verify that the document root, index file, site configuration, symlink, certificate, and private key exist; the symlink resolves to the matching configuration; the certificate contains `CN=test.cluster.local`; and the HTTPS request returns an Nginx response.

### `ci.cluster.local`

```bash
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
ls -l /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
ls -l /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
```

Verify that the document root, index file, site configuration, symlink, certificate, and private key exist; the symlink resolves to the matching configuration; the certificate contains `CN=ci.cluster.local`; and the HTTPS request returns an Nginx response.

### `status.cluster.local`

```bash
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
ls -l /etc/nginx/sites-available/status.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
ls -l /etc/ssl/private/status.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
```

Verify that the document root, index file, site configuration, symlink, certificate, and private key exist; the symlink resolves to the matching configuration; the certificate contains `CN=status.cluster.local`; and the HTTPS request returns an Nginx response.

### TLS certificate validation

```bash
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | \
  grep -E 'Subject:|Public-Key:|Not Before|Not After'

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | \
  grep -E 'Subject:|Public-Key:|Not Before|Not After'

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | \
  grep -E 'Subject:|Public-Key:|Not Before|Not After'
```

Verify that all certificates use 2048-bit RSA keys, are valid for approximately 365 days, and contain the matching site name in the subject.

### Security and service logs

```bash
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
cat /etc/sysctl.d/99-security.conf
```

Verify that UFW has a default-deny incoming policy with SSH, HTTP, and HTTPS allowed; UFW is active; SSH has `PermitRootLogin no` and `PasswordAuthentication no`; and Nginx listens on the ports configured by the rendered site templates.