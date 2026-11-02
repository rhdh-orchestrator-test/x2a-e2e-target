---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS-enabled sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx and Fail2ban, configures UFW to deny inbound traffic by default while allowing SSH, HTTP, and HTTPS, applies kernel security settings, disables SSH root login and password authentication, generates self-signed RSA certificates, deploys site-specific Nginx virtual hosts, enables the sites, and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; virtual host `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; virtual host `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; virtual host `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Not applicable
  - Key Config: Package installed; service enabled and started

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows SSH `22`, HTTP `80`, and HTTPS `443`
  - Key Config: Default inbound policy is deny; firewall enabled

- **ssh**: Hardened SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: Root login disabled; password authentication disabled; Chef service resource has action `nothing`

The configured attributes are:

- `nginx.sites`: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- `nginx.ssl.certificate_path`: `/etc/ssl/certs`
- `nginx.ssl.private_key_path`: `/etc/ssl/private`
- `security.fail2ban.enabled`: `true`
- `security.ufw.enabled`: `true`
- `security.ssh.disable_root`: `true`
- `security.ssh.password_auth`: `false`

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

No static files under `files/default/*` or `files/*` are listed in the supplied cookbook directory. The `nginx.rb` recipe references dynamically constructed `cookbook_file` sources such as `#{site_folder}/index.html`; those source files are not present in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - Execution order must be preserved because later recipes depend on packages, directories, certificates, and base Nginx configuration created earlier.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default inbound policy to deny with `ufw --force default deny`.
   - Allows SSH with `ufw allow ssh`.
   - Allows HTTP with `ufw allow http`.
   - Allows HTTPS with `ufw allow https`.
   - Enables UFW with `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as `execute[reload_sysctl]` with action `nothing`; no triggering notification is shown.
   - Disables SSH root login by setting `PermitRootLogin no`.
   - Disables SSH password authentication by setting `PasswordAuthentication no`.
   - Declares `service[ssh]` with action `nothing`; no SSH restart or reload is shown.
   - Resources: one package resource, two service resources, two template resources, and seven execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Iterates over the following three sites:
     - **test.cluster.local**:
       - Creates `/opt/server/test`.
       - Deploys `/opt/server/test/index.html` with mode `0644`.
       - Uses a dynamically constructed `cookbook_file` source of `#{site_folder}/index.html`.
     - **ci.cluster.local**:
       - Creates `/opt/server/ci`.
       - Deploys `/opt/server/ci/index.html` with mode `0644`.
       - Uses a dynamically constructed `cookbook_file` source of `#{site_folder}/index.html`.
     - **status.cluster.local**:
       - Creates `/opt/server/status`.
       - Deploys `/opt/server/status/index.html` with mode `0644`.
       - Uses a dynamically constructed `cookbook_file` source of `#{site_folder}/index.html`.
   - Resources: one package, two templates, one service, three directories, and three cookbook files.
   - No verified `group[www-data]` resource is included in the migration.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
   - Generates certificates for the following three sites:
     - **test.cluster.local**:
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Private key: `/etc/ssl/private/test.cluster.local.key`
       - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
       - Self-signed X.509, RSA 2048-bit, valid for 365 days, generated with `-nodes`.
       - Key mode `0640`, ownership `root:ssl-cert`.
     - **ci.cluster.local**:
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key: `/etc/ssl/private/ci.cluster.local.key`
       - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`
       - Self-signed X.509, RSA 2048-bit, valid for 365 days, generated with `-nodes`.
       - Key mode `0640`, ownership `root:ssl-cert`.
     - **status.cluster.local**:
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Private key: `/etc/ssl/private/status.cluster.local.key`
       - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`
       - Self-signed X.509, RSA 2048-bit, valid for 365 days, generated with `-nodes`.
       - Key mode `0640`, ownership `root:ssl-cert`.
   - Certificate-generation execute resources have no `creates` guard, so the current Chef semantics permit execution on every convergence. The Ansible implementation must explicitly choose between preserving that behavior and generating certificates only when absent.
   - Resources: one package, one group, two directories, and three execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders and enables one virtual-host configuration for each site:
     - **test.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
       - Variables: `server_name=test.cluster.local`, `document_root=/opt/server/test`, `ssl_enabled=true`, `cert_file=/etc/ssl/certs/test.cluster.local.crt`, `key_file=/etc/ssl/private/test.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/test.cluster.local`.
     - **ci.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
       - Variables: `server_name=ci.cluster.local`, `document_root=/opt/server/ci`, `ssl_enabled=true`, `cert_file=/etc/ssl/certs/ci.cluster.local.crt`, `key_file=/etc/ssl/private/ci.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/ci.cluster.local`.
     - **status.cluster.local**:
       - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
       - Variables: `server_name=status.cluster.local`, `document_root=/opt/server/status`, `ssl_enabled=true`, `cert_file=/etc/ssl/certs/status.cluster.local.crt`, `key_file=/etc/ssl/private/status.cluster.local.key`.
       - Creates `/etc/nginx/sites-enabled/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Renders `site.conf.erb` three times total.
   - No Nginx reload or restart is shown after virtual-host deployment.
   - Resources: three templates, three links, and one file deletion.

## Dependencies

**External cookbook dependencies**: None shown.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no restart or reload shown

**Security collections represented**: `fail2ban`, `ufw`, `ssh`.

## Credentials

**Detection Summary**: 3 sensitive TLS private keys detected across the SSL and site recipes. No application passwords, API tokens, data bags, Chef Vault entries, CyberArk references, or secret-manager integrations were detected.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: No secret-management path detected

### Self-signed TLS private key for `test.cluster.local`

- **Variable(s)**: `key_file`, resolved to `/etc/ssl/private/test.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated file
- **Usage context**: TLS private key for the `test.cluster.local` Nginx virtual host
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`

### Self-signed TLS private key for `ci.cluster.local`

- **Variable(s)**: `key_file`, resolved to `/etc/ssl/private/ci.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated file
- **Usage context**: TLS private key for the `ci.cluster.local` Nginx virtual host
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`

### Self-signed TLS private key for `status.cluster.local`

- **Variable(s)**: `key_file`, resolved to `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated file
- **Usage context**: TLS private key for the `status.cluster.local` Nginx virtual host
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`

### Certificate subject email

- **Variable/value**: `admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command
- **Usage context**: Subject email embedded in all three self-signed certificates
- **Sensitivity**: Not an authentication credential; make configurable if environment-specific certificate metadata is required.

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
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
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

**Service endpoints to check**: SSH TCP `22`; HTTP TCP `80`; HTTPS TCP `443`.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

## Pre-flight checks:

```bash
dpkg-query -W nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban

nginx -t
ss -tlnp | grep -E ':(80|443)\b'
ss -tlnp | grep ':22\b'

ufw status verbose
ufw status numbered

test -f /etc/fail2ban/jail.local
fail2ban-client status

grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t

test -f /etc/sysctl.d/99-security.conf
sysctl --system
```

### `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%A %U:%G %n' /etc/ssl/private/test.cluster.local.key
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
```

Expected result: The document root, index file, certificate, private key, virtual-host file, and symlink exist. The key is owned by `root:ssl-cert` with mode `0640`, and HTTPS responds successfully with certificate verification disabled.

### `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%A %U:%G %n' /etc/ssl/private/ci.cluster.local.key
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
```

Expected result: The document root, index file, certificate, private key, virtual-host file, and symlink exist. The certificate subject contains `CN=ci.cluster.local`, and HTTPS responds successfully with certificate verification disabled.

### `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%A %U:%G %n' /etc/ssl/private/status.cluster.local.key
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
```

Expected result: The document root, index file, certificate, private key, virtual-host file, and symlink exist. The certificate subject contains `CN=status.cluster.local`, and HTTPS responds successfully with certificate verification disabled.

### Default site, certificates, firewall, and logs

```bash
test ! -e /etc/nginx/sites-enabled/default

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates

journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
journalctl -u ssh --no-pager -n 50
```

Expected result: The default site does not exist; all three certificates are self-signed, RSA 2048-bit certificates valid for approximately 365 days; UFW is active with default incoming policy deny and SSH, HTTP, and HTTPS allowed; and service logs contain no configuration or startup errors.