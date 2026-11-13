---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and configures Nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies SSH and kernel security hardening; creates self-signed certificates; deploys one static page per site; renders and enables three Nginx site configurations; and enables the Nginx, Fail2ban, and UFW services. The Ansible implementation must preserve the recipe execution order, idempotent firewall and SSH changes, certificate-generation checks, file permissions, and service reload notifications.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled Nginx virtual host serving a static site
  - Location/Path: `/opt/server/test`
  - Static file: `/opt/server/test/index.html`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - SSL enabled: `true`
  - Ownership: Document root and static file `nginx:nginx`; private key `root:ssl-cert`
  - Modes: Document root `0755`, static file `0644`, private key `0640`

- **ci.cluster.local**: SSL-enabled Nginx virtual host serving a static site
  - Location/Path: `/opt/server/ci`
  - Static file: `/opt/server/ci/index.html`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - SSL enabled: `true`
  - Ownership: Document root and static file `nginx:nginx`; private key `root:ssl-cert`
  - Modes: Document root `0755`, static file `0644`, private key `0640`

- **status.cluster.local**: SSL-enabled Nginx virtual host serving a static site
  - Location/Path: `/opt/server/status`
  - Static file: `/opt/server/status/index.html`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - SSL enabled: `true`
  - Ownership: Document root and static file `nginx:nginx`; private key `root:ssl-cert`
  - Modes: Document root `0755`, static file `0644`, private key `0640`

**Security configuration**:

- **fail2ban**
  - Package: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Service enabled and started

- **ufw**
  - Package: `ufw`
  - Default incoming policy: deny
  - Allowed ports: `22/tcp`, `80/tcp`, `443/tcp`
  - Firewall enabled

- **ssh**
  - Root login disabled
  - Password authentication disabled
  - `sshd` restarted only when the corresponding configuration changes

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

No custom-resource provider is used by the execution tree.

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

The execution-tree listing does not include the source static files used by `cookbook_file`. The Ansible migration must provide source content for:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role must import task files in this same order.

2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Restarts `fail2ban` when `/etc/fail2ban/jail.local` changes.
   - Sets the UFW default incoming policy to deny.
   - Allows SSH on `22/tcp`.
   - Allows HTTP on `80/tcp`.
   - Allows HTTPS on `443/tcp`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` only when the sysctl template changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` when `node['security']['ssh']['disable_root']` is `true`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` when `node['security']['ssh']['password_auth']` is `false`.
   - Restarts `sshd` only when either SSH setting changes.
   - Declares `sshd` as a notification target with action `nothing`.
   - Resources: one package resource containing two packages, two services, two templates, and eight execute resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`

3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Reloads Nginx when either main configuration template changes.
   - Creates document roots and deploys static files for the following three sites:
     - `test.cluster.local`: creates `/opt/server/test` as `nginx:nginx`, mode `0755`, and deploys `test/index.html` to `/opt/server/test/index.html` as `nginx:nginx`, mode `0644`.
     - `ci.cluster.local`: creates `/opt/server/ci` as `nginx:nginx`, mode `0755`, and deploys `ci/index.html` to `/opt/server/ci/index.html` as `nginx:nginx`, mode `0644`.
     - `status.cluster.local`: creates `/opt/server/status` as `nginx:nginx`, mode `0755`, and deploys `status/index.html` to `/opt/server/status/index.html` as `nginx:nginx`, mode `0644`.
   - The site source names are derived from `site_name.split('.').first`: `test`, `ci`, and `status`.
   - Resources: one package, two templates, one service, three directories, and three `cookbook_file` resources.

4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` as `root:root`, mode `0755`.
   - Creates `/etc/ssl/private` as `root:ssl-cert`, mode `0710`.
   - Generates self-signed RSA certificates and unencrypted 2048-bit private keys for:
     - `test.cluster.local`: certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`, common name `test.cluster.local`.
     - `ci.cluster.local`: certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`, common name `ci.cluster.local`.
     - `status.cluster.local`: certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`, common name `status.cluster.local`.
   - Each certificate is valid for 365 days and uses subject email `admin@example.com`.
   - Certificate generation is skipped when both the certificate and key already exist.
   - Sets private-key ownership to `root:ssl-cert` and mode `0640`.
   - Reloads Nginx after certificate or key generation.
   - All three sites have `ssl_enabled: true`; no site is skipped.
   - Ansible should use an idempotent certificate implementation such as `community.crypto.openssl_privatekey` and `community.crypto.x509_certificate`.
   - Resources: one package resource containing two packages, one group, two directories, and three certificate-generation execute resources.

5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` as `root:root`, mode `0755`.
   - Creates `/etc/nginx/sites-enabled` as `root:root`, mode `0755`.
   - The validated execution analysis reports three directory-resource iterations in the site-directory loop. The migration must preserve the execution-tree behavior and verify the third directory resource/path from the Chef source before implementation; the two explicitly identified paths are `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for:
     - `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`, with document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`, and mode `0644`.
     - `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`, with document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`, and mode `0644`.
     - `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`, with document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`, and mode `0644`.
   - Creates these enabled-site symlinks:
     - `/etc/nginx/sites-enabled/test.cluster.local` -> `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` -> `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` -> `/etc/nginx/sites-available/status.cluster.local`
   - Removes `/etc/nginx/sites-enabled/default`.
   - Reloads Nginx when a site template, symlink, or default-site deletion changes.
   - Resources: two explicitly identified directory resources, three site templates, three links, and one deleted file, plus the validated third directory-loop resource requiring source-level path verification.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:
- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: restarted only after SSH hardening changes
- `ufw`: enabled through the UFW command line

**Network dependencies**:
- SSH: `22/tcp`
- HTTP: `80/tcp`
- HTTPS: `443/tcp`

## Credentials

**Detection Summary**: 0 application credentials detected across the supplied cookbook files. No data bags, vault references, API tokens, database passwords, or environment-variable secrets were found.

**Source**:
- **Provider**: None detected
- **URL**: Not applicable
- **Path**: Not applicable

### Self-signed certificate subject email

- **Variable(s)**: No variable; literal value `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate-generation parameter
- **Usage context**: X.509 subject email address for all three self-signed certificates; this is not an application credential

### Certificate and private-key paths

- **Variable(s)**:
  - `node['nginx']['ssl']['certificate_path']`
  - `node['nginx']['ssl']['private_key_path']`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Non-secret attributes containing filesystem paths
- **Usage context**: Locations of Nginx TLS certificates and private keys

Generated private keys are sensitive files. Preserve:

```text
owner: root
group: ssl-cert
mode: 0640
```

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
- `/etc/nginx/sites-enabled/default` must be absent
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`

**Directories to verify**:
- `/opt/server/test`
- `/opt/server/ci`
- `/opt/server/status`
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- The third site-directory resource reported by the validated `sites.rb` execution analysis

**Service endpoints to check**:
- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: `22/tcp`

**Templates rendered**:
- `fail2ban.jail.local.erb`: 1 rendering
- `nginx.conf.erb`: 1 rendering
- `security.conf.erb`: 1 rendering
- `sysctl-security.conf.erb`: 1 rendering
- `site.conf.erb`: 3 renderings:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks

```bash
# Package availability
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx --no-pager
systemctl status fail2ban --no-pager
systemctl status sshd --no-pager
ufw status verbose

# Configuration validation
nginx -t
sshd -t
sysctl -p /etc/sysctl.d/99-security.conf

# Firewall validation
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# Listening sockets
ss -tlnp | grep ':22 '
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
```

### `test.cluster.local`

```bash
test -d /opt/server/test
stat -c '%U:%G %a %n' /opt/server/test /opt/server/test/index.html
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
readlink -f /etc/nginx/sites-enabled/test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
```

Expected values:
- Document root: `nginx:nginx 755`
- Static file: `nginx:nginx 644`
- Private key: `root:ssl-cert 640`
- Symlink target: `/etc/nginx/sites-available/test.cluster.local`
- Certificate common name: `test.cluster.local`

### `ci.cluster.local`

```bash
test -d /opt/server/ci
stat -c '%U:%G %a %n' /opt/server/ci /opt/server/ci/index.html
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
```

Expected values:
- Document root: `nginx:nginx 755`
- Static file: `nginx:nginx 644`
- Private key: `root:ssl-cert 640`
- Symlink target: `/etc/nginx/sites-available/ci.cluster.local`
- Certificate common name: `ci.cluster.local`

### `status.cluster.local`

```bash
test -d /opt/server/status
stat -c '%U:%G %a %n' /opt/server/status /opt/server/status/index.html
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
readlink -f /etc/nginx/sites-enabled/status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
```

Expected values:
- Document root: `nginx:nginx 755`
- Static file: `nginx:nginx 644`
- Private key: `root:ssl-cert 640`
- Symlink target: `/etc/nginx/sites-available/status.cluster.local`
- Certificate common name: `status.cluster.local`

### Nginx site and default-site checks

```bash
test ! -e /etc/nginx/sites-enabled/default

readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

nginx -t
```

Expected symlink targets:

```text
/etc/nginx/sites-enabled/test.cluster.local
  -> /etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
  -> /etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
  -> /etc/nginx/sites-available/status.cluster.local
```

### Security and service checks

```bash
ufw status verbose
grep '22/tcp' /etc/ufw/user.rules
grep '80/tcp' /etc/ufw/user.rules
grep '443/tcp' /etc/ufw/user.rules

grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

fail2ban-client status
cat /etc/fail2ban/jail.local
journalctl -u fail2ban --no-pager -n 50

cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u sshd --no-pager -n 100
```

Expected results:
- UFW status is `active`.
- Default incoming policy is `deny`.
- `22/tcp`, `80/tcp`, and `443/tcp` are allowed.
- `PermitRootLogin no` is present.
- `PasswordAuthentication no` is present.
- `sshd -t` exits successfully.
- Fail2ban is active and `/etc/fail2ban/jail.local` exists.
- Nginx reloads complete successfully after Nginx configuration, security configuration, certificate generation, site template, site symlink, and default-site removal changes.