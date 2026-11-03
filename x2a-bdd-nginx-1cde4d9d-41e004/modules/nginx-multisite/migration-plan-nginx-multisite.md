---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook provisions Nginx for three HTTPS sites—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx and Fail2ban, configures UFW to deny inbound traffic by default while allowing SSH, HTTP, and HTTPS, applies kernel and SSH hardening, generates self-signed certificates, deploys per-site Nginx configurations and document roots, and removes the default Nginx site. The three static `index.html` source files are referenced by the cookbook but are not present in the supplied file listing and must be supplied or separately validated before migration completion.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: TCP ports `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: TCP ports `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: TCP ports `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

Security areas configured by attributes are:

- **fail2ban**: enabled
- **ufw**: enabled
- **ssh**: root login disabled and password authentication disabled

These attribute-derived values and the certificate, key, directory, and mode values should be verified against the cookbook attributes before migration because they are not fully represented in the supplied structured analysis.

## File Structure

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb

Providers:
(no provider files)

cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb

cookbooks/nginx-multisite/attributes/default.rb
```

No static files under `files/` are listed. The cookbook references these `cookbook_file` sources, but their presence is unresolved and must not be assumed:

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
   - This ordering applies security configuration first, installs and configures Nginx second, generates certificates third, and deploys site configurations last.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default policy to deny using `ufw --force default deny`.
   - Allows SSH with `ufw allow ssh`.
   - Allows HTTP with `ufw allow http`.
   - Allows HTTPS with `ufw allow https`.
   - Enables UFW with `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as an action-`nothing` resource; preserve conditional or handler-based behavior rather than running it unconditionally.
   - Disables root SSH login with:
     ```bash
     sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
     ```
   - Disables SSH password authentication with:
     ```bash
     sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
     ```
   - Defines the `ssh` service with action `nothing`.
   - Resources: one package resource installing two packages, two services, two templates, and eight execute resources.
   - Execute resources: `ufw_default_deny`, `ufw_allow_ssh`, `ufw_allow_http`, `ufw_allow_https`, `ufw_enable`, `reload_sysctl`, `disable root login`, and `disable password auth`.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package with no pinned version.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` with mode `0755`.
   - Deploys the unresolved `test.cluster.local/index.html` source to `/opt/server/test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` with mode `0755`.
   - Deploys the unresolved `ci.cluster.local/index.html` source to `/opt/server/ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` with mode `0755`.
   - Deploys the unresolved `status.cluster.local/index.html` source to `/opt/server/status/index.html` with mode `0644`.
   - No `www-data` group resource is present in the validated execution tree.
   - Iterations:
     - **test.cluster.local**: document root `/opt/server/test`; SSL enabled.
     - **ci.cluster.local**: document root `/opt/server/ci`; SSL enabled.
     - **status.cluster.local**: document root `/opt/server/status`; SSL enabled.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate for **test.cluster.local**:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Validity: 365 days
     - Common name: `test.cluster.local`
     - Email: `admin@example.com`
     - Key mode: `0640`
     - Key owner/group: `root:ssl-cert`
   - Generates a self-signed RSA 2048-bit certificate for **ci.cluster.local**:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Validity: 365 days
     - Common name: `ci.cluster.local`
     - Email: `admin@example.com`
     - Key mode: `0640`
     - Key owner/group: `root:ssl-cert`
   - Generates a self-signed RSA 2048-bit certificate for **status.cluster.local**:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Validity: 365 days
     - Common name: `status.cluster.local`
     - Email: `admin@example.com`
     - Key mode: `0640`
     - Key owner/group: `root:ssl-cert`
   - The SSL loop is active for all three named sites because each has `ssl_enabled: true`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **test.cluster.local** to `/etc/nginx/sites-available/test.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `site.conf.erb` for **ci.cluster.local** to `/etc/nginx/sites-available/ci.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `site.conf.erb` for **status.cluster.local** to `/etc/nginx/sites-available/status.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Removes `/etc/nginx/sites-enabled/default`.
   - Site variables are the exact site name, document root, `ssl_enabled: true`, and the corresponding certificate and key paths.
   - Templates are rendered three times, once for each named site.
   - The supplied execution tree does not show an explicit Nginx reload or restart notification. Use a controlled validation and reload handler only when configuration files or links change.

## Dependencies

**External cookbook dependencies**: None identified in the supplied metadata analysis.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

No package versions are pinned.

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: referenced with action `nothing`

## Credentials

**Detection Summary**: No passwords, API keys, data bags, encrypted data bags, Chef Vault items, CyberArk references, Conjur variables, or database credentials were detected. Three locally generated TLS private keys are present.

**Source**:

- **Provider**: None detected
- **URL**: Not applicable
- **Path**: Generated locally by `openssl`

### Self-Signed TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally; not sourced from a vault or data bag
- **Usage context**: TLS private keys for the three Nginx HTTPS sites
- **Protection**: Mode `0640`, owner/group `root:ssl-cert`

The `admin@example.com` certificate subject field is metadata, not an authentication secret.

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
- `/etc/nginx/sites-enabled/default` must be absent
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
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

The three `index.html` files are unresolved inputs because their cookbook source files are absent from the supplied listing. They must be supplied or separately validated before migration completion.

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH: TCP port `22`
- Unix sockets: none specified

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: 1 render to `/etc/nginx/nginx.conf`
- `security.conf.erb`: 1 render to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: 1 render to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: 3 renders:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Verify required packages
dpkg-query -W fail2ban ufw nginx openssl ca-certificates

# Verify services
systemctl status fail2ban
systemctl status nginx

# Verify Fail2ban
fail2ban-client status
test -f /etc/fail2ban/jail.local

# Verify UFW policy and allowed services
ufw status verbose
ufw status verbose | grep -E 'Default:.*deny'
ufw status | grep -E '22|ssh'
ufw status | grep -E '80|http'
ufw status | grep -E '443|https'

# Verify SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config
sshd -t

# Verify kernel security configuration
test -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Validate Nginx
nginx -t
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test ! -e /etc/nginx/sites-enabled/default

# Verify listeners
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
ss -tlnp | grep ':22'

# Review service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u ssh --no-pager -n 100
```

### Instance check: `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
```

### Instance check: `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
```

### Instance check: `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
```

### Migration acceptance criteria

- `nginx`, `fail2ban`, and `ufw` are installed.
- `nginx` and `fail2ban` are enabled and running.
- UFW denies traffic by default and permits SSH, HTTP, and HTTPS.
- Root SSH login and SSH password authentication are disabled.
- All three document roots exist.
- The three `index.html` files are supplied and validated before completion.
- All three Nginx site configurations exist and are enabled.
- `/etc/nginx/sites-enabled/default` is absent.
- All three certificates and private keys exist with the required ownership and mode.
- `nginx -t` succeeds.
- HTTP and HTTPS checks succeed for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.