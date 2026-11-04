---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx for three SSL-enabled virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs security and web-server packages, applies Fail2ban, UFW, sysctl, and SSH-hardening configuration, installs and starts Nginx, creates document roots and index files, generates self-signed certificates, renders virtual-host configurations, enables the sites, and removes the default site. The Ansible migration must preserve the recipe execution order, exact paths, ownership, permissions, site names, certificate settings, and idempotent behavior where confirmed by detailed source analysis.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The `node['nginx']['sites']` collection contains the following three sites. The supplied validation confirms the collection and site iteration structure; the attribute values below should be verified against `cookbooks/nginx-multisite/attributes/default.rb`.

- **test.cluster.local**: Nginx SSL virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP port `80`; HTTPS port `443`; no Unix socket
  - Key Config: SSL enabled is reported as `true`; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled-site link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: Nginx SSL virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP port `80`; HTTPS port `443`; no Unix socket
  - Key Config: SSL enabled is reported as `true`; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled-site link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: Nginx SSL virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP port `80`; HTTPS port `443`; no Unix socket
  - Key Config: SSL enabled is reported as `true`; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled-site link `/etc/nginx/sites-enabled/status.cluster.local`

Security configuration areas are `fail2ban`, `ufw`, and `ssh`. The recipes use these values as conditionals rather than iterating over them. The supplied plan reports Fail2ban and UFW as enabled, `disable_root` as `true`, and `password_auth` as `false`; these values require verification against the attributes analysis.

## File Structure

The following is the complete relevant cookbook file listing from the supplied plan.

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

No static files under `files/default/*` or `files/*` were included in the supplied cookbook file listing. The Nginx recipe references these dynamic `cookbook_file` sources, which must be preserved if the source files exist in the complete cookbook content:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. `nginx-multisite::security` (`cookbooks/nginx-multisite/recipes/security.rb`)
2. `nginx-multisite::nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
3. `nginx-multisite::ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
4. `nginx-multisite::sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

### 1. Default entry recipe

**Recipe:** `cookbooks/nginx-multisite/recipes/default.rb`

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.

The Ansible implementation should import task files or roles in this exact order.

### 2. Security configuration

**Recipe:** `cookbooks/nginx-multisite/recipes/security.rb`

The recipe installs security packages, configures Fail2ban and UFW, renders sysctl configuration, and conditionally applies SSH hardening.

- Installs packages `fail2ban` and `ufw`.
- Enables and starts the `fail2ban` service.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Applies the UFW default-deny policy:
  ```bash
  ufw --force default deny
  ```
- Allows SSH:
  ```bash
  ufw allow ssh
  ```
- Allows HTTP:
  ```bash
  ufw allow http
  ```
- Allows HTTPS:
  ```bash
  ufw allow https
  ```
- Enables UFW:
  ```bash
  ufw --force enable
  ```
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Reloads sysctl with:
  ```bash
  sysctl -p /etc/sysctl.d/99-security.conf
  ```
- When `node['security']['ssh']['disable_root'] == true`, changes `/etc/ssh/sshd_config` to:
  ```text
  PermitRootLogin no
  ```
- When `node['security']['ssh']['password_auth'] == false`, changes `/etc/ssh/sshd_config` to:
  ```text
  PasswordAuthentication no
  ```
- Uses the `ssh` service as the restart target. The supplied detailed plan reports that SSH restarts only after either SSH setting changes; this notification and guard behavior requires verification against the source.
- The structured analysis identifies **8 execute resources**:
  1. `ufw_default_deny`
  2. `ufw_allow_ssh`
  3. `ufw_allow_http`
  4. `ufw_allow_https`
  5. `ufw_enable`
  6. `reload_sysctl`
  7. `disable root login`
  8. `disable password auth`

Ansible should use package, service, UFW, sysctl, and SSH configuration modules where possible. Preserve UFW idempotency guards, sysctl reload-on-change behavior, SSH setting guards, and delayed service notifications only after confirming them in the recipe source.

### 3. Nginx installation and document roots

**Recipe:** `cookbooks/nginx-multisite/recipes/nginx.rb`

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Enables and starts the `nginx` service.
- Uses the Nginx service for reload notifications.
- Creates the following document roots and index files:

#### `test.cluster.local`

- Creates `/opt/server/test` recursively.
- Directory owner/group: `www-data:www-data`
- Directory mode: `0755`
- Deploys `/opt/server/test/index.html`.
- Cookbook source: `test/index.html`
- File owner/group: `www-data:www-data`
- File mode: `0644`

#### `ci.cluster.local`

- Creates `/opt/server/ci` recursively.
- Directory owner/group: `www-data:www-data`
- Directory mode: `0755`
- Deploys `/opt/server/ci/index.html`.
- Cookbook source: `ci/index.html`
- File owner/group: `www-data:www-data`
- File mode: `0644`

#### `status.cluster.local`

- Creates `/opt/server/status` recursively.
- Directory owner/group: `www-data:www-data`
- Directory mode: `0755`
- Deploys `/opt/server/status/index.html`.
- Cookbook source: `status/index.html`
- File owner/group: `www-data:www-data`
- File mode: `0644`

The structured analysis does not identify a separate `group[www-data]` resource. `www-data` is only the owner and group applied to the directory and index-file resources.

### 4. SSL package, directories, and certificates

**Recipe:** `cookbooks/nginx-multisite/recipes/ssl.rb`

- Installs `openssl` and `ca-certificates`.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
- Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
- Evaluates the following three SSL-enabled sites:

#### `test.cluster.local`

- Certificate: `/etc/ssl/certs/test.cluster.local.crt`
- Private key: `/etc/ssl/private/test.cluster.local.key`
- Common name: `test.cluster.local`
- Generates an RSA 2048-bit, 365-day self-signed certificate.
- Sets the private key to owner `root:ssl-cert` and mode `0640`.

#### `ci.cluster.local`

- Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
- Private key: `/etc/ssl/private/ci.cluster.local.key`
- Common name: `ci.cluster.local`
- Generates an RSA 2048-bit, 365-day self-signed certificate.
- Sets the private key to owner `root:ssl-cert` and mode `0640`.

#### `status.cluster.local`

- Certificate: `/etc/ssl/certs/status.cluster.local.crt`
- Private key: `/etc/ssl/private/status.cluster.local.key`
- Common name: `status.cluster.local`
- Generates an RSA 2048-bit, 365-day self-signed certificate.
- Sets the private key to owner `root:ssl-cert` and mode `0640`.

The certificate subject includes the non-secret administrative email address `admin@example.com`. Certificate generation is reported as conditional on the certificate and key both being absent; preserve this behavior only after confirming the guard in the source recipe. Certificate creation should notify an Nginx reload after verification of the source notification behavior.

### 5. Nginx virtual-host configuration

**Recipe:** `cookbooks/nginx-multisite/recipes/sites.rb`

The recipe renders and enables three site configurations using `cookbooks/nginx-multisite/templates/default/site.conf.erb`.

#### `test.cluster.local`

- Renders `/etc/nginx/sites-available/test.cluster.local` with:
  - `server_name`: `test.cluster.local`
  - `document_root`: `/opt/server/test`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/test.cluster.local.key`
- Sets mode `0644`.
- Creates `/etc/nginx/sites-enabled/test.cluster.local` as a symbolic link to `/etc/nginx/sites-available/test.cluster.local`.

#### `ci.cluster.local`

- Renders `/etc/nginx/sites-available/ci.cluster.local` with:
  - `server_name`: `ci.cluster.local`
  - `document_root`: `/opt/server/ci`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
- Sets mode `0644`.
- Creates `/etc/nginx/sites-enabled/ci.cluster.local` as a symbolic link to `/etc/nginx/sites-available/ci.cluster.local`.

#### `status.cluster.local`

- Renders `/etc/nginx/sites-available/status.cluster.local` with:
  - `server_name`: `status.cluster.local`
  - `document_root`: `/opt/server/status`
  - `ssl_enabled`: `true`
  - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
  - `key_file`: `/etc/ssl/private/status.cluster.local.key`
- Sets mode `0644`.
- Creates `/etc/nginx/sites-enabled/status.cluster.local` as a symbolic link to `/etc/nginx/sites-available/status.cluster.local`.

After all three site configurations are processed, removes:

```text
/etc/nginx/sites-enabled/default
```

All site-template, link, and default-site changes should use a shared Nginx reload handler. Run `nginx -t` before reloading where practical.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: restart target for SSH hardening; otherwise no action

**Security and networking behavior**:

- UFW default incoming policy: deny
- Allowed services:
  - SSH: `22/tcp`
  - HTTP: `80/tcp`
  - HTTPS: `443/tcp`
- No Unix sockets are configured.
- No specific bind address is defined in the analyzed recipes. Verify bind behavior in `nginx.conf.erb` and `site.conf.erb`.

## Credentials

**Detection Summary**: No credentials or secret-management integrations detected. One non-secret administrative email address is embedded in the self-signed certificate subject. Three sensitive private keys are generated locally at runtime.

**Source**:

- **Provider**: None detected
- **URL**: None detected
- **Path**: None detected

### Self-signed certificate subject email

- **Variable(s)**: Literal `admin@example.com`; no Chef attribute variable
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate subject metadata
- **Usage context**: Used as the `emailAddress` field during self-signed certificate generation
- **Sensitive credential**: No; this is certificate metadata, not a password or token

### Generated private keys

- **Variable(s)**: No variable; generated at runtime
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Local filesystem
- **Usage context**: TLS private keys for the three Nginx virtual hosts
- **Files**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: `0640`
- **Ownership**: `root:ssl-cert`

No data bags, encrypted data bags, Chef Vault, Conjur, CyberArk, Vault attributes, environment-variable secrets, database credentials, API keys, or hardcoded passwords were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` — should be absent
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`

**Service endpoints to check**:

- HTTP: `80`
- HTTPS: `443`
- SSH: `22/tcp`
- Unix sockets: none

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

**Total template render operations**: 7

## Pre-flight checks:

```bash
# Security services
systemctl status fail2ban
systemctl is-enabled fail2ban
fail2ban-client status

# Firewall policy and rules
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# Expected:
# Default incoming policy: deny
# 22/tcp allowed
# 80/tcp allowed
# 443/tcp allowed

# Sysctl configuration
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# SSH hardening
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config
# Expected:
# PermitRootLogin no
# PasswordAuthentication no
systemctl status ssh

# Nginx service and syntax
systemctl status nginx
systemctl is-enabled nginx
nginx -t

# Nginx global configuration
ls -l /etc/nginx/nginx.conf
ls -l /etc/nginx/conf.d/security.conf

# Enabled site links
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default
```

### Site-specific checks

```bash
# test.cluster.local
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
stat -c '%U:%G %a %n' /opt/server/test /opt/server/test/index.html
grep -E 'server_name|root|ssl|listen' /etc/nginx/sites-available/test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# ci.cluster.local
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
stat -c '%U:%G %a %n' /opt/server/ci /opt/server/ci/index.html
grep -E 'server_name|root|ssl|listen' /etc/nginx/sites-available/ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# status.cluster.local
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
stat -c '%U:%G %a %n' /opt/server/status /opt/server/status/index.html
grep -E 'server_name|root|ssl|listen' /etc/nginx/sites-available/status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
```

### Network, permissions, and logs

```bash
ss -tlnp | grep -E ':(80|443)\b'
ss -tlnp | grep ':22\b'

journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100

stat -c '%U:%G %a %n' /etc/ssl/certs
stat -c '%U:%G %a %n' /etc/ssl/private
```

### Expected migration behavior

- Existing certificates and keys are not regenerated.
- UFW rules are not duplicated on repeated runs.
- Nginx reloads only after relevant configuration, certificate, site-link, or default-site changes, subject to source verification.
- Fail2ban restarts only when `/etc/fail2ban/jail.local` changes, subject to source verification.
- SSH restarts only when `PermitRootLogin` or `PasswordAuthentication` changes, subject to source verification.
- All three exact site names, document roots, certificate paths, key paths, ports, ownership values, and permissions remain unchanged.