---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an Nginx web server with three named virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies firewall and SSH hardening; renders security and Nginx configuration; creates locally generated self-signed TLS certificates; deploys one static `index.html` per site; enables the three virtual hosts; and removes the default Nginx site. The expected HTTP and HTTPS listeners are ports 80 and 443, subject to confirmation in `site.conf.erb`.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: Expected HTTP `80` and HTTPS `443`; confirm in `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; content `/opt/server/test/index.html`

- **ci.cluster.local**: Static HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: Expected HTTP `80` and HTTPS `443`; confirm in `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; content `/opt/server/ci/index.html`

- **status.cluster.local**: Static HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: Expected HTTP `80` and HTTPS `443`; confirm in `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; content `/opt/server/status/index.html`

**Security Configuration**:

- Fail2ban is configured as enabled and uses service `fail2ban`.
- UFW is configured as enabled with SSH, HTTP, and HTTPS allowed.
- SSH hardening sets `PermitRootLogin no` and `PasswordAuthentication no`.
- The supplied structured summary references these settings, but the complete attribute analysis was not supplied; verify the values against `cookbooks/nginx-multisite/attributes/default.rb`.

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
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
    └── default/
        └── [site-specific index.html source files not present in supplied listing]
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

No provider files are used by the execution tree. `resources/lineinfile.rb` is referenced by structural analysis but no custom-resource invocation appears in the execution tree.

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

No static files under `files/default/*` or `files/*` are present in the supplied directory listing. Equivalent source files must be provided for:

```text
/opt/server/test/index.html
/opt/server/ci/index.html
/opt/server/status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role entry point must import task files in this same order.

2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs packages `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Executes `ufw --force default deny`.
   - Executes `ufw allow ssh`.
   - Executes `ufw allow http`.
   - Executes `ufw allow https`.
   - Executes `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Defines `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; no triggering notification is shown.
   - Executes `sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config`.
   - Executes `sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config`.
   - Defines `service[sshd]` with action `nothing`; no SSH restart or reload is shown.
   - Resources: package `2`, service `2`, template `2`, execute `8`.
   - Ansible equivalents are `ansible.builtin.package`, `ansible.builtin.service`, `ansible.builtin.template`, `community.general.ufw`, `ansible.posix.sysctl`, and `ansible.builtin.lineinfile`.

3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs package `nginx`.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Iterates over `test.cluster.local`:
     - Creates `/opt/server/test`.
     - Deploys the site source to `/opt/server/test/index.html` with mode `0644`.
     - Uses the source expression `#{site_folder}/index.html`.
   - Iterates over `ci.cluster.local`:
     - Creates `/opt/server/ci`.
     - Deploys the site source to `/opt/server/ci/index.html` with mode `0644`.
     - Uses the source expression `#{site_folder}/index.html`.
   - Iterates over `status.cluster.local`:
     - Creates `/opt/server/status`.
     - Deploys the site source to `/opt/server/status/index.html` with mode `0644`.
     - Uses the source expression `#{site_folder}/index.html`.
   - Resources: package `1`, template `2`, service `1`, directory `3`, cookbook_file `3`.

4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs packages `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private`.
   - The supplied plan specifies mode `0755` for `/etc/ssl/certs` and mode `0710` for `/etc/ssl/private`; verify these modes against the source recipe because they are not exposed in the structured execution summary.
   - Iterates over `test.cluster.local`:
     - Generates `/etc/ssl/private/test.cluster.local.key`.
     - Generates `/etc/ssl/certs/test.cluster.local.crt`.
     - Uses RSA 2048-bit, self-signed OpenSSL generation valid for 365 days.
     - Uses subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`.
     - Sets key mode `0640` and ownership `root:ssl-cert`.
   - Iterates over `ci.cluster.local`:
     - Generates `/etc/ssl/private/ci.cluster.local.key`.
     - Generates `/etc/ssl/certs/ci.cluster.local.crt`.
     - Uses RSA 2048-bit, self-signed OpenSSL generation valid for 365 days.
     - Uses subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`.
     - Sets key mode `0640` and ownership `root:ssl-cert`.
   - Iterates over `status.cluster.local`:
     - Generates `/etc/ssl/private/status.cluster.local.key`.
     - Generates `/etc/ssl/certs/status.cluster.local.crt`.
     - Uses RSA 2048-bit, self-signed OpenSSL generation valid for 365 days.
     - Uses subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`.
     - Sets key mode `0640` and ownership `root:ssl-cert`.
   - Resources: package `1`, group `1`, directory `2`, execute `3`.
   - Ansible may use `ansible.builtin.command`, `ansible.builtin.shell`, or equivalent `community.crypto` modules.

5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
   - Uses `server_name: test.cluster.local`, `document_root: /opt/server/test`, `ssl_enabled: true`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - Creates link `/etc/nginx/sites-enabled/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
   - Uses `server_name: ci.cluster.local`, `document_root: /opt/server/ci`, `ssl_enabled: true`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - Creates link `/etc/nginx/sites-enabled/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
   - Uses `server_name: status.cluster.local`, `document_root: /opt/server/status`, `ssl_enabled: true`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Creates link `/etc/nginx/sites-enabled/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Resources: directory `2`, template `3`, link `3`, file deletion `1`.
   - The expected listeners are HTTP port `80` and HTTPS port `443`, but the supplied execution tree does not expose the `listen` directives. Confirm them in `cookbooks/nginx-multisite/templates/default/site.conf.erb`.
   - Validate the rendered configuration with `nginx -t` before reloading Nginx.

## Dependencies

**External cookbook dependencies**: None specified in the supplied metadata analysis.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: referenced for conditional configuration, but only declared with action `nothing`

**Operating-system assumptions**:

- Debian/Ubuntu-style paths are available:
  - `/etc/nginx`
  - `/etc/ssh/sshd_config`
  - `/etc/sysctl.d`
  - `/etc/ssl/certs`
  - `/etc/ssl/private`
- UFW is installed and available.
- SSH configuration supports `PermitRootLogin` and `PasswordAuthentication`.

## Credentials

**Detection Summary**: No application credentials, passwords, API keys, data bags, Chef Vault entries, external secret-manager references, or hardcoded attribute passwords were detected.

**Source**:

- **Provider**: None detected
- **URL**: None detected
- **Path**: None detected

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. The TLS keys are locally generated deployment artifacts and are documented separately below.

### TLS Private Keys

- **Variable(s)**: `key_file`; `node['nginx']['ssl']['private_key_path']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files
- **Usage context**: HTTPS private keys for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Permissions**: Mode `0640`, owned by `root:ssl-cert`

### TLS Certificates

- **Variable(s)**: `cert_file`; `node['nginx']['ssl']['certificate_path']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificates
- **Usage context**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Certificate details**: RSA 2048-bit certificates with 365-day validity and the corresponding site name in the subject CN.
- **Metadata**: The fixed email address `admin@example.com` is certificate metadata, not an authentication secret.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/etc/nginx/sites-enabled/default
/opt/server/test
/opt/server/test/index.html
/opt/server/ci
/opt/server/ci/index.html
/opt/server/status
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
```

`/etc/nginx/sites-enabled/default` must be absent after migration.

**Service endpoints to check**:

- SSH
- HTTP port `80`, subject to confirmation in `site.conf.erb`
- HTTPS port `443`, subject to confirmation in `site.conf.erb`
- No Unix socket or custom Nginx listening port is specified.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb` total: 3 renders

## Pre-flight checks

Run these checks after the Ansible migration.

### Service status

```bash
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-enabled fail2ban
```

Expected result: `nginx` and `fail2ban` are enabled and active.

### Configuration validation

```bash
nginx -t
nginx -T
sshd -t
```

Expected result:

- Nginx syntax validation succeeds.
- The expanded Nginx configuration contains `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
- SSH configuration validation succeeds.

### Global and security configuration

```bash
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf
grep -nE 'user|worker|include|events|http' /etc/nginx/nginx.conf
grep -nE 'limit|server_tokens|security|headers' /etc/nginx/conf.d/security.conf
grep -nE '^[[:space:]]*PermitRootLogin|^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config
```

Expected SSH settings:

```text
PermitRootLogin no
PasswordAuthentication no
```

### Site: test.cluster.local

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

curl -I --resolve test.cluster.local:80:127.0.0.1 \
  http://test.cluster.local/

curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
```

Expected result:

- The document root, static file, virtual-host file, enabled-site link, certificate, and private key exist.
- The certificate subject contains `CN=test.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.
- HTTP and HTTPS return an HTTP response if the corresponding listeners are defined in `site.conf.erb`.

### Site: ci.cluster.local

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

curl -I --resolve ci.cluster.local:80:127.0.0.1 \
  http://ci.cluster.local/

curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
```

Expected result:

- The document root, static file, virtual-host file, enabled-site link, certificate, and private key exist.
- The certificate subject contains `CN=ci.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.
- HTTP and HTTPS return an HTTP response if the corresponding listeners are defined in `site.conf.erb`.

### Site: status.cluster.local

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

curl -I --resolve status.cluster.local:80:127.0.0.1 \
  http://status.cluster.local/

curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected result:

- The document root, static file, virtual-host file, enabled-site link, certificate, and private key exist.
- The certificate subject contains `CN=status.cluster.local`.
- The private key is owned by `root:ssl-cert` with mode `640`.
- HTTP and HTTPS return an HTTP response if the corresponding listeners are defined in `site.conf.erb`.

### Default site removal

```bash
test ! -e /etc/nginx/sites-enabled/default
```

Expected result: the default site does not exist.

### TLS validation

```bash
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -text | grep -E 'Subject:|Not Before|Not After'

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -text | grep -E 'Subject:|Not Before|Not After'

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -text | grep -E 'Subject:|Not Before|Not After'
```

Expected result:

- Each certificate uses RSA 2048-bit generation.
- Each certificate has a one-year validity period.
- Each certificate contains its expected site name in the subject.

### Firewall validation

```bash
ufw status verbose
ufw status numbered
```

Expected result:

- Default incoming policy is deny.
- SSH, HTTP, and HTTPS are allowed.
- UFW is active.

### Fail2ban validation

```bash
fail2ban-client status
systemctl status fail2ban
test -f /etc/fail2ban/jail.local
```

Expected result:

- Fail2ban is active.
- The rendered jail configuration exists.
- Configured jails are visible.

### Sysctl validation

```bash
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf
```

Expected result: the file exists and applies without errors.

### Listening ports

```bash
ss -tlnp | grep -E ':(80|443)[[:space:]]'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN
```

Expected result: Nginx listens on the ports declared by `site.conf.erb`, expected to be `80` and `443`, with no unexpected process owning those ports.

### Logs

```bash
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
```

Check for Nginx configuration errors, certificate or permission errors, Fail2ban startup failures, and UFW-related failures.