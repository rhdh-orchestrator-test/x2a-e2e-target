---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual hosts: `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`. It installs Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; creates site document roots and index files; generates self-signed RSA 2048-bit certificates; configures HTTP and HTTPS firewall access; applies Fail2ban and kernel security settings; disables root SSH login and SSH password authentication; and stores an encrypted site token at `/etc/nginx/secrets/site_token`.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **ci.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/var/www/ci.cluster.local`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; index `/var/www/ci.cluster.local/index.html`

- **status.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/var/www/status.cluster.local`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; index `/var/www/status.cluster.local/index.html`

- **test.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/var/www/test.cluster.local`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; index `/var/www/test.cluster.local/index.html`

**Security configuration**:

- Fail2ban is enabled, installed, and started.
- UFW is enabled with default-deny incoming policy and allows SSH, HTTP, and HTTPS.
- Root SSH login is disabled.
- SSH password authentication is disabled.

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

No provider files are used by the execution tree. The `resources/lineinfile.rb` custom resource is not invoked by the listed recipe execution flow and is excluded.

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

No static file under `files/default/*` or `files/*` is present in the supplied directory listing. The recipes reference `cookbook_file` resources for site `index.html` files, but those source files are not included in the analyzed inventory.

**Data bags:**
```text
data_bags/nginx_secrets/site.json
data_bags/nginx_sites/ci.cluster.local.json
data_bags/nginx_sites/status.cluster.local.json
data_bags/nginx_sites/test.cluster.local.json
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The migration must preserve this logical order: security and firewall, Nginx installation and global configuration, SSL preparation, then per-site configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Applies UFW commands in order:
     1. `ufw --force default deny`
     2. `ufw allow ssh`
     3. `ufw allow http`
     4. `ufw allow https`
     5. `ufw --force enable`
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`; no Chef notification triggers it.
   - When `security.ssh.disable_root` is true, sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - When `security.ssh.password_auth` is false, sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Declares `service[sshd]` with action `nothing`; the Chef flow does not explicitly restart or reload SSH.
   - Ansible implementation should use package, service, template, UFW, line-in-file, and carefully tested SSH handlers as appropriate.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/etc/nginx/secrets` with mode `0700`.
   - Reads encrypted data bag `nginx_secrets/site`, including fields `id` and `token`.
   - Writes the token to `/etc/nginx/secrets/site_token` with mode `0600`.
   - Creates the following site roots with mode `0755` and deploys their index files with mode `0644`:
     - `ci.cluster.local`: `/var/www/ci.cluster.local` and `/var/www/ci.cluster.local/index.html`
     - `status.cluster.local`: `/var/www/status.cluster.local` and `/var/www/status.cluster.local/index.html`
     - `test.cluster.local`: `/var/www/test.cluster.local` and `/var/www/test.cluster.local/index.html`
   - The site loop runs exactly three iterations: `ci.cluster.local`, `status.cluster.local`, and `test.cluster.local`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with mode `0755` and group `root`.
   - Creates `/etc/ssl/private` with mode `0710` and group `ssl-cert`.
   - Uses role variables preserving:
     - Certificate path: `/etc/ssl/certs`
     - Private key path: `/etc/ssl/private`
   - Generates one self-signed certificate and private key for each site:
     - `ci.cluster.local`: certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
     - `test.cluster.local`: certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
   - Each certificate uses RSA 2048-bit, `-nodes`, validity of 365 days, and subject `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site name>/emailAddress=admin@example.com`.
   - Each private key is mode `0640`, owned by `root:ssl-cert`.
   - Certificate creation must be idempotent and must not regenerate existing certificates and keys on every run.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled`, both with mode `0755`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for each site:
     - `ci.cluster.local`: destination `/etc/nginx/sites-available/ci.cluster.local`, root `/var/www/ci.cluster.local`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: destination `/etc/nginx/sites-available/status.cluster.local`, root `/var/www/status.cluster.local`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
     - `test.cluster.local`: destination `/etc/nginx/sites-available/test.cluster.local`, root `/var/www/test.cluster.local`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
   - All three sites have `ssl_enabled: true`.
   - Creates symlinks:
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
   - Deletes `/etc/nginx/sites-enabled/default`.

**Attributes** (`cookbooks/nginx-multisite/attributes/default.rb`):

- `default['nginx']['ssl']['certificate_path'] = '/etc/ssl/certs'`
- `default['nginx']['ssl']['private_key_path'] = '/etc/ssl/private'`
- `default['security']['fail2ban']['enabled'] = true`
- `default['security']['ufw']['enabled'] = true`
- `default['security']['ssh']['disable_root'] = true`
- `default['security']['ssh']['password_auth'] = false`

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`.

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `sshd`: declared with action `nothing`; not explicitly started or restarted by the Chef flow.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The Ansible role must account for package, service, and firewall differences between Ubuntu and CentOS. The source flow explicitly uses UFW, so the target must provide UFW or define an equivalent firewall implementation.

## Credentials

**Detection Summary**: 1 data-bag credential detected across 1 encrypted data bag and 1 consuming recipe. TLS keys and certificates are additionally generated locally.

**Source**:

- **Provider**: Internal Chef encrypted data bag
- **URL**: None detected
- **Path**: `nginx_secrets/site`
- **Encryption status**: Encrypted
- **Data bag keys identified**: `id`, `token`

### Nginx site token

- **Variable**: `site_secret['token']`
- **Source file(s)**:
  - `data_bags/nginx_secrets/site.json`
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Encrypted Chef data bag
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **Target file mode**: `0600`
- **Target directory mode**: `/etc/nginx/secrets` with mode `0700`
- **Migration storage**: Ansible Vault or an approved external secret manager
- **Migration requirements**: Do not expose the token in task output; use `no_log: true` when writing it.

### TLS private keys

- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated on the managed host
- **Usage context**: Nginx TLS private keys
- **Paths**:
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
  - `/etc/ssl/private/test.cluster.local.key`
- **Permissions**: `0640`
- **Owner/group**: `root:ssl-cert`

### TLS certificates

- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated on the managed host
- **Usage context**: Nginx HTTPS server certificates
- **Validity**: 365 days
- **Key type**: RSA 2048-bit
- **Certificate paths**:
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
  - `/etc/ssl/certs/test.cluster.local.crt`

No HashiCorp Vault, CyberArk, AWS Secrets Manager, Chef Vault, environment-variable secret references, hardcoded passwords, API keys, or database credentials were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/default` — must be absent
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/ssl/private/test.cluster.local.key`
- `/var/www/ci.cluster.local/index.html`
- `/var/www/status.cluster.local/index.html`
- `/var/www/test.cluster.local/index.html`

**Service endpoints to check**: TCP `80`, TCP `443`, SSH normally on TCP `22`; no Unix sockets specified.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render

**Total template render operations**: 7.

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Firewall validation
ufw status verbose
ufw status numbered

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config

# Kernel security configuration
ls -l /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# Nginx configuration
nginx -t
nginx -T | grep -E 'ci\.cluster\.local|status\.cluster\.local|test\.cluster\.local'
ls -l /etc/nginx/nginx.conf /etc/nginx/conf.d/security.conf

# Secret permissions; do not print token contents
stat -c '%a %U %G %n' /etc/nginx/secrets
stat -c '%a %U %G %n' /etc/nginx/secrets/site_token

# Ports and processes
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN
pgrep -a nginx

# Logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u sshd --no-pager -n 100
journalctl -u nginx --no-pager | grep -E 'error|emerg|crit|alert'
```

Expected security values:

```text
PermitRootLogin no
PasswordAuthentication no
```

Expected firewall behavior:

- Default incoming policy is deny.
- SSH, HTTP, and HTTPS are allowed.
- UFW is active.

### `ci.cluster.local`

```bash
test -d /var/www/ci.cluster.local
test -f /var/www/ci.cluster.local/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/ci.cluster.local

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%a %U %G %n' /etc/ssl/private/ci.cluster.local.key

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
```

Expected:

- `server_name ci.cluster.local`
- Root `/var/www/ci.cluster.local`
- Certificate `/etc/ssl/certs/ci.cluster.local.crt`
- Key `/etc/ssl/private/ci.cluster.local.key`
- Certificate subject contains `CN = ci.cluster.local`
- Private key is `root:ssl-cert` with mode `640`
- HTTP and HTTPS requests reach the correct virtual host.

### `status.cluster.local`

```bash
test -d /var/www/status.cluster.local
test -f /var/www/status.cluster.local/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/status.cluster.local

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%a %U %G %n' /etc/ssl/private/status.cluster.local.key

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
```

Expected:

- `server_name status.cluster.local`
- Root `/var/www/status.cluster.local`
- Certificate `/etc/ssl/certs/status.cluster.local.crt`
- Key `/etc/ssl/private/status.cluster.local.key`
- Certificate subject contains `CN = status.cluster.local`
- Private key is `root:ssl-cert` with mode `640`
- HTTP and HTTPS requests reach the correct virtual host.

### `test.cluster.local`

```bash
test -d /var/www/test.cluster.local
test -f /var/www/test.cluster.local/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
grep -E 'server_name|root|ssl_certificate|ssl_certificate_key' \
  /etc/nginx/sites-available/test.cluster.local

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%a %U %G %n' /etc/ssl/private/test.cluster.local.key

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
```

Expected:

- `server_name test.cluster.local`
- Root `/var/www/test.cluster.local`
- Certificate `/etc/ssl/certs/test.cluster.local.crt`
- Key `/etc/ssl/private/test.cluster.local.key`
- Certificate subject contains `CN = test.cluster.local`
- Private key is `root:ssl-cert` with mode `640`
- HTTP and HTTPS requests reach the correct virtual host.

### Shared site and default-site checks

```bash
test ! -e /etc/nginx/sites-enabled/default
stat -c '%a %U %G %n' /etc/nginx/secrets
stat -c '%a %U %G %n' /etc/nginx/secrets/site_token
```

Expected:

```text
/etc/nginx/secrets       700
/etc/nginx/secrets/site_token 600
```

The three certificates must be valid for approximately 365 days from generation, and Nginx must listen on TCP ports `80` and `443`. DNS or `/etc/hosts` resolution must map all three hostnames to the target server before hostname-based endpoint testing.