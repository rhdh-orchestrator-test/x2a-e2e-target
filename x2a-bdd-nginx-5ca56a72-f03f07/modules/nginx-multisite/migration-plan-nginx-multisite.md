---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx for three SSL-enabled sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx, deploys global and per-site configuration, creates document roots and index files, generates self-signed certificates, configures Fail2ban and UFW, applies sysctl security settings, and disables SSH root login and password authentication. The migration must preserve the recipe execution order, site-specific paths, ports, certificate settings, file permissions, and security configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static SSL-enabled Nginx site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; index file `/opt/server/test/index.html`

- **ci.cluster.local**: Static SSL-enabled Nginx site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; index file `/opt/server/ci/index.html`

- **status.cluster.local**: Static SSL-enabled Nginx site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; index file `/opt/server/status/index.html`

Security configuration areas implemented by `recipes/security.rb`:

- **fail2ban**
- **ufw**
- **ssh**

## File Structure

```text
attributes/default.rb
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

### Providers

```text
```

No provider files are used by the execution tree.

### Templates

```text
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb
```

### Attributes

```text
attributes/default.rb
```

### Files

No static files under `files/default/` or `files/` are listed in the supplied cookbook structure. The `cookbook_file` resources reference these per-site source files, but the files are not included in the supplied directory listing:

```text
test.cluster.local/index.html
ci.cluster.local/index.html
status.cluster.local/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The migration must preserve this sequence: host security, Nginx installation and document roots, certificate generation, then virtual-host deployment.
   - Resources: four `include_recipe` declarations.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default incoming policy to deny with `ufw --force default deny`.
   - Allows SSH with `ufw allow ssh`.
   - Allows HTTP with `ufw allow http`.
   - Allows HTTPS with `ufw allow https`.
   - Enables UFW with `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines a sysctl reload command using `sysctl -p /etc/sysctl.d/99-security.conf`; the original resource has action `nothing`, so the Ansible migration must explicitly attach the reload to the template change if that behavior is intended.
   - Because `disable_root` is configured as `true` in the supplied plan, changes `/etc/ssh/sshd_config` to `PermitRootLogin no`.
   - Because `password_auth` is configured as `false` in the supplied plan, changes `/etc/ssh/sshd_config` to `PasswordAuthentication no`.
   - References the `ssh` service with action `nothing`; no explicit restart or reload is shown in the execution tree.
   - Resources: one package declaration installing two packages, two services, two templates, and seven execute resources.
   - Recommended Ansible resources are `ansible.builtin.package`, `ansible.builtin.template`, `community.general.ufw`, `ansible.posix.sysctl` or a sysctl template with handler, and `ansible.builtin.lineinfile`.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` with mode `0755`.
   - Deploys `test.cluster.local/index.html` to `/opt/server/test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` with mode `0755`.
   - Deploys `ci.cluster.local/index.html` to `/opt/server/ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` with mode `0755`.
   - Deploys `status.cluster.local/index.html` to `/opt/server/status/index.html` with mode `0644`.
   - Resources: one package, two templates, one service, three directories, and three `cookbook_file` resources.
   - The supplied execution tree does not show a `www-data` group resource; no such resource should be migrated without separate source verification.
   - The Ansible role should use a handler to run `nginx -t` and reload Nginx when configuration changes.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
     - Validity: `365` days
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
     - Key ownership and mode: `root:ssl-cert`, `0640`
   - Generates a self-signed RSA 2048-bit certificate for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
     - Validity: `365` days
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`
     - Key ownership and mode: `root:ssl-cert`, `0640`
   - Generates a self-signed RSA 2048-bit certificate for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
     - Validity: `365` days
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`
     - Key ownership and mode: `root:ssl-cert`, `0640`
   - The certificate command is equivalent to:
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout /etc/ssl/private/SITE.key \
       -out /etc/ssl/certs/SITE.crt \
       -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=SITE/emailAddress=admin@example.com"
     ```
   - Resources: one package declaration installing two packages, one group, two directories, and three execute resources.
   - The Ansible migration should use `community.crypto.openssl_privatekey`, `community.crypto.openssl_csr`, and `community.crypto.x509_certificate` where available, ensuring existing certificates are not regenerated on every run.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local` with:
     - `server_name`: `test.cluster.local`
     - `document_root`: `/opt/server/test`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/test.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/test.cluster.local.key`
     - Mode `0644`
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` as a link to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local` with:
     - `server_name`: `ci.cluster.local`
     - `document_root`: `/opt/server/ci`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/ci.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/ci.cluster.local.key`
     - Mode `0644`
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` as a link to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local` with:
     - `server_name`: `status.cluster.local`
     - `document_root`: `/opt/server/status`
     - `ssl_enabled`: `true`
     - `cert_file`: `/etc/ssl/certs/status.cluster.local.crt`
     - `key_file`: `/etc/ssl/private/status.cluster.local.key`
     - Mode `0644`
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` as a link to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Resources: three templates, three links, and one file deletion.
   - The Ansible role should validate Nginx with `nginx -t` before reloading or restarting it.

## Dependencies

**External cookbook dependencies**: Not verified from the supplied analysis; no `metadata.rb` analysis was provided.

**Chef runtime and supported platforms**: Not verified from the supplied analysis; no validated `metadata.rb` or platform metadata was provided.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: referenced with action `nothing`; the recipe modifies `/etc/ssh/sshd_config` without showing an explicit restart or reload
- UFW: enabled with `ufw --force enable`

## Credentials

**Detection Summary**: No application credentials, passwords, API tokens, data bags, Chef Vault items, CyberArk references, or external secret-manager integrations were detected. Three locally generated TLS private keys and three locally generated TLS certificates are sensitive artifacts.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### TLS Private Keys

- **Variable(s)**: Dynamic paths based on the SSL private-key directory and site names
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/attributes/default.rb`
- **Current storage**: Generated locally by `openssl req`
- **Usage context**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
  - Ownership must be `root:ssl-cert`.
  - Permissions must be `0640`.
  - The Ansible migration must protect the key contents and avoid exposing them in logs or task output.

### TLS Certificates

- **Variable(s)**: Dynamic paths based on the SSL certificate directory and site names
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/attributes/default.rb`
- **Current storage**: Locally generated self-signed certificates
- **Usage context**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
  - Referenced by the three Nginx site configurations.
  - The subject contains the non-secret address `admin@example.com`.

## Checks for the Migration

**Files to verify**:

Cookbook source files:

- `cookbooks/nginx-multisite/attributes/default.rb`
- `cookbooks/nginx-multisite/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/security.rb`
- `cookbooks/nginx-multisite/recipes/nginx.rb`
- `cookbooks/nginx-multisite/recipes/ssl.rb`
- `cookbooks/nginx-multisite/recipes/sites.rb`
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`

Deployed global and security files:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

Per-site Nginx files:

- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default`

Document roots and index files:

- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
- `/opt/server/status/index.html`

TLS files:

- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`

No Unix sockets or custom listen ports are defined.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: one render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: one render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: one render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: one render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: one render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: one render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: one render
- `site.conf.erb` total: three renders

## Pre-flight checks

```bash
# Package checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service checks
systemctl status nginx
systemctl status fail2ban
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Nginx configuration checks
nginx -t
nginx -T | grep -E \
'server_name (test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local)'

test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test ! -e /etc/nginx/sites-enabled/default

grep -nE 'worker|events|http|include|security' /etc/nginx/nginx.conf
grep -nE 'server_tokens|limit|headers|ssl|security' /etc/nginx/conf.d/security.conf

# Listening ports and processes
ss -tlnp | grep -E ':(80|443)\b'
netstat -tulpn | grep -E ':(80|443)\b'
pgrep -a nginx

# Firewall checks
ufw status verbose
ufw status numbered

# Fail2ban checks
test -f /etc/fail2ban/jail.local
fail2ban-client status

# Sysctl and SSH checks
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
grep -E '^PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t

# Logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u ssh --no-pager -n 100
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

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout \
  -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

curl --resolve test.cluster.local:80:127.0.0.1 \
  -I http://test.cluster.local/

curl -k --resolve test.cluster.local:443:127.0.0.1 \
  -I https://test.cluster.local/
```

Expected results:

- The document root and index file exist.
- The enabled-site link resolves to `/etc/nginx/sites-available/test.cluster.local`.
- The key is owned by `root:ssl-cert` with mode `640`.
- HTTP and HTTPS return valid responses, normally `200 OK`.

### `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout \
  -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

curl --resolve ci.cluster.local:80:127.0.0.1 \
  -I http://ci.cluster.local/

curl -k --resolve ci.cluster.local:443:127.0.0.1 \
  -I https://ci.cluster.local/
```

Expected results:

- The document root and index file exist.
- The enabled-site link resolves to `/etc/nginx/sites-available/ci.cluster.local`.
- The key is owned by `root:ssl-cert` with mode `640`.
- HTTP and HTTPS return valid responses, normally `200 OK`.

### `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout \
  -subject -issuer -dates

stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

curl --resolve status.cluster.local:80:127.0.0.1 \
  -I http://status.cluster.local/

curl -k --resolve status.cluster.local:443:127.0.0.1 \
  -I https://status.cluster.local/
```

Expected results:

- The document root and index file exist.
- The enabled-site link resolves to `/etc/nginx/sites-available/status.cluster.local`.
- The key is owned by `root:ssl-cert` with mode `640`.
- HTTP and HTTPS return valid responses, normally `200 OK`.

### Security validation

```bash
ufw status verbose
ufw status numbered
systemctl status fail2ban
test -f /etc/fail2ban/jail.local
fail2ban-client status

test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
grep -E '^PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t
```

Verify that:

- UFW is active.
- The default incoming policy is deny.
- SSH, HTTP, and HTTPS are allowed.
- Fail2ban is active and its configuration exists.
- The sysctl configuration applies without errors.
- `PermitRootLogin no` is present.
- `PasswordAuthentication no` is present.
- `sshd -t` reports valid SSH configuration.

### Completion criteria

- Nginx is enabled, active, and listening on ports `80` and `443`.
- Fail2ban is enabled and active.
- All three named sites have document roots, index files, certificates, private keys, site configurations, and enabled-site links.
- The default Nginx site is absent.
- Nginx configuration validation succeeds.
- HTTP and HTTPS checks succeed for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
- No Nginx, Fail2ban, UFW, sysctl, or SSH errors remain in the relevant logs.