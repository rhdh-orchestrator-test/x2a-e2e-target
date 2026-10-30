---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; configures firewall and SSH hardening; renders security and Nginx configuration; generates self-signed certificates; deploys site content; enables the three sites; and removes the default Nginx site. The Chef cookbook renders `/etc/sysctl.d/99-security.conf` but does not apply it during the analyzed execution because `execute[reload_sysctl]` has `action: nothing`. Applying those settings in Ansible is an intentional migration behavior change. Likewise, reloading or restarting SSH would be a migration-specific change because the source cookbook performs no SSH service action.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: TCP ports `80` and `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Nginx configuration: `/etc/nginx/sites-available/test.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: TCP ports `80` and `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Nginx configuration: `/etc/nginx/sites-available/ci.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: TCP ports `80` and `443`
  - SSL: Enabled
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Nginx configuration: `/etc/nginx/sites-available/status.cluster.local`
  - Enabled link: `/etc/nginx/sites-enabled/status.cluster.local`

Security components configured by `recipes/security.rb`:

- **fail2ban**: Intrusion-prevention service, enabled and started
- **ufw**: Firewall configured with default incoming deny and SSH, HTTP, and HTTPS allowed
- **ssh**: Root login and password authentication disabled; the source cookbook performs no SSH restart or reload

## File Structure

```text
cookbooks/nginx-multisite/
├── attributes/
│   └── default.rb
├── files/
│   └── default/
│       └── [dynamic site index.html sources not listed in supplied directory information]
├── recipes/
│   ├── default.rb
│   ├── security.rb
│   ├── nginx.rb
│   ├── ssl.rb
│   └── sites.rb
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── providers/
    └── [none]
```

No provider file is used by the execution tree. The recipe uses dynamic `cookbook_file` source expressions for the site `index.html` files, but the corresponding static file paths were not supplied.

## Module Explanation

The cookbook performs operations in this order.

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the dependency order required by the source cookbook.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures UFW in this order:
     1. Default incoming policy: deny.
     2. Allow SSH, TCP port `22`.
     3. Allow HTTP, TCP port `80`.
     4. Allow HTTPS, TCP port `443`.
     5. Enable UFW forcefully.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Declares `execute[reload_sysctl]` with `action: nothing`; the analyzed Chef execution does not apply the sysctl settings.
   - Conditionally disables root SSH login when `security.ssh.disable_root = true` by setting `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Conditionally disables SSH password authentication when `security.ssh.password_auth = false` by setting `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Declares `service[ssh]` with `action: nothing`; no SSH reload or restart occurs in the source execution.
   - Ansible may apply the sysctl settings or reload SSH only as explicitly documented migration enhancements.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Iterates over `nginx.sites` exactly three times:
     - **test.cluster.local**:
       - Creates `/opt/server/test`.
       - Deploys `/opt/server/test/index.html` using a dynamic `cookbook_file` source.
       - Sets the index file mode to `0644`.
     - **ci.cluster.local**:
       - Creates `/opt/server/ci`.
       - Deploys `/opt/server/ci/index.html` using a dynamic `cookbook_file` source.
       - Sets the index file mode to `0644`.
     - **status.cluster.local**:
       - Creates `/opt/server/status`.
       - Deploys `/opt/server/status/index.html` using a dynamic `cookbook_file` source.
       - Sets the index file mode to `0644`.
   - The exact static source paths for the three index files must be confirmed before migration.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Preserves the source resource ownership settings involving `root` and `ssl-cert`; the supplied analysis does not provide enough detail to state additional directory owner/group values exactly.
   - Iterates over `nginx.sites` exactly three times. All three sites have `ssl_enabled: true`:
     - **test.cluster.local**:
       - Generates `/etc/ssl/certs/test.cluster.local.crt`.
       - Generates `/etc/ssl/private/test.cluster.local.key`.
       - Uses RSA 2048, validity of 365 days, and subject CN `test.cluster.local`.
       - Sets the key mode to `0640` and ownership to `root:ssl-cert`.
     - **ci.cluster.local**:
       - Generates `/etc/ssl/certs/ci.cluster.local.crt`.
       - Generates `/etc/ssl/private/ci.cluster.local.key`.
       - Uses RSA 2048, validity of 365 days, and subject CN `ci.cluster.local`.
       - Sets the key mode to `0640` and ownership to `root:ssl-cert`.
     - **status.cluster.local**:
       - Generates `/etc/ssl/certs/status.cluster.local.crt`.
       - Generates `/etc/ssl/private/status.cluster.local.key`.
       - Uses RSA 2048, validity of 365 days, and subject CN `status.cluster.local`.
       - Sets the key mode to `0640` and ownership to `root:ssl-cert`.
   - Uses the self-signed certificate subject format `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.
   - Certificate generation should be guarded for idempotence in Ansible.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterates over `nginx.sites` exactly three times.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **test.cluster.local** to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **ci.cluster.local** to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **status.cluster.local** to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
   - Creates the link `/etc/nginx/sites-enabled/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Validates Nginx configuration and reloads Nginx after site changes in the Ansible implementation.

## Dependencies

**External cookbook dependencies**: None shown. The contents of `metadata.rb` were not supplied, so no additional cookbook dependency can be confirmed.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `nginx`: enabled and started
- `fail2ban`: enabled and started
- `ssh`: referenced with `action: nothing`; no source restart or reload
- `ufw`: configured and enabled through firewall commands

## Credentials

**Detection Summary**: 0 external credentials detected across the supplied recipes, attributes, templates, and execution analysis.

Generated TLS private keys are sensitive artifacts but are created locally and are not retrieved from a credential provider.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: No secret path, data bag path, vault path, or secret-manager path detected

### Generated TLS Private Keys

- **Variable(s)**: `key_file` for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by `openssl req`
- **Usage context**: TLS private keys for the three Nginx HTTPS virtual hosts
- **Paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`

### Self-Signed TLS Certificates

- **Variable(s)**: `cert_file` for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally; not sourced from a vault or data bag
- **Usage context**: Certificate files referenced by the Nginx site configurations
- **Paths**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Certificate metadata**: The subject includes the static email address `admin@example.com`; this is certificate metadata, not an authentication credential.

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` must not exist
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`

**Service endpoints to check**:

- SSH: TCP port `22`
- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- No Unix socket or explicit bind IP is specified.

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: 3 renders
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks

### Service status

```bash
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban
```

Expected result: Nginx and Fail2ban are active and enabled.

### Nginx configuration and listeners

```bash
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
curl -I http://127.0.0.1/
curl -k -I https://127.0.0.1/
```

Expected result: Nginx configuration validates, all three server names appear, and Nginx listens on TCP ports `80` and `443`.

### `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
```

Expected result: The document root, content, site configuration, enabled link, certificate, and key exist; the link resolves to `/etc/nginx/sites-available/test.cluster.local`; the certificate contains `CN=test.cluster.local`; and HTTPS returns an intentional HTTP response.

### `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
```

Expected result: The document root, content, site configuration, enabled link, certificate, and key exist; the link resolves to `/etc/nginx/sites-available/ci.cluster.local`; the certificate contains `CN=ci.cluster.local`; and HTTPS returns an intentional HTTP response.

### `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
```

Expected result: The document root, content, site configuration, enabled link, certificate, and key exist; the link resolves to `/etc/nginx/sites-available/status.cluster.local`; the certificate contains `CN=status.cluster.local`; and HTTPS returns an intentional HTTP response.

### Firewall

```bash
ufw status verbose
ufw status numbered
```

Expected result: UFW is active, the default incoming policy is `deny`, and SSH, HTTP, and HTTPS are allowed.

### Fail2ban

```bash
fail2ban-client status
test -f /etc/fail2ban/jail.local
journalctl -u fail2ban --no-pager -n 50
```

Expected result: Fail2ban is running, its configuration exists, and recent logs contain no startup or configuration errors.

### SSH hardening

```bash
sshd -t
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
```

Expected result: SSH configuration validation succeeds, root login is disabled, and password authentication is disabled. No SSH reload or restart is expected when matching the source cookbook behavior.

### Sysctl configuration

```bash
test -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf
```

Expected result: The sysctl configuration file exists and contains the expected settings. The source Chef execution does not apply these settings because `execute[reload_sysctl]` is disabled.

If applying sysctl settings is an intentional Ansible migration enhancement, additionally run:

```bash
sysctl -p /etc/sysctl.d/99-security.conf
```

### TLS key permissions

```bash
stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key
```

Expected result:

```text
root:ssl-cert 640 /etc/ssl/private/test.cluster.local.key
root:ssl-cert 640 /etc/ssl/private/ci.cluster.local.key
root:ssl-cert 640 /etc/ssl/private/status.cluster.local.key
```

### Removed default site

```bash
test ! -e /etc/nginx/sites-enabled/default
```

Expected result: The command succeeds because the default Nginx site has been deleted.