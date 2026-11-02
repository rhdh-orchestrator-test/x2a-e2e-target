---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures Nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It creates site document roots and index files, generates self-signed certificates, configures HTTP-to-HTTPS redirects and Nginx security settings, removes the default site, and enables Fail2ban, UFW, SSH hardening, and kernel network-security settings. The stated attribute values and detailed template settings should be verified against the cookbook files because the supplied structured analysis did not include complete attribute or template-content analysis.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`; index file `/opt/server/test/index.html`

- **ci.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`; index file `/opt/server/ci/index.html`

- **status.cluster.local**: SSL-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`; index file `/opt/server/status/index.html`

**Security services**:

- **fail2ban**: Enabled and started; package `fail2ban`; configuration `/etc/fail2ban/jail.local`
- **ufw**: Enabled with default deny policy; allows SSH, HTTP, and HTTPS; package `ufw`
- **ssh**: Root login and password authentication disabled in `/etc/ssh/sshd_config`; service notification target `ssh`

**SSL directories**:

- Certificates: `/etc/ssl/certs`
- Private keys: `/etc/ssl/private`

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

No provider files or custom resources are used by the execution tree.

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

No static files under `files/default/*` or `files/*` are listed. The recipes reference these `cookbook_file` sources, which must be supplied separately during migration:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - Preserves the execution sequence for the Ansible role: security setup, Nginx installation, SSL setup, then virtual-host deployment.
   - Resources used: four `include_recipe` declarations.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Applies UFW default-deny policy and allows TCP ports `22`, `80`, and `443`, then enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Reloads `/etc/sysctl.d/99-security.conf` with `sysctl -p` when the sysctl template changes.
   - Hardens `/etc/ssh/sshd_config` by setting `PermitRootLogin no`.
   - Hardens `/etc/ssh/sshd_config` by setting `PasswordAuthentication no`.
   - Restarts `ssh` only when SSH hardening changes.
   - Resources: one package resource, two service resources, two templates, and eight execute resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`
   - Detailed Fail2ban and sysctl settings require verification against the rendered templates.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` owned by `www-data:www-data` with mode `0755`.
   - Deploys `test/index.html` to `/opt/server/test/index.html` owned by `www-data:www-data` with mode `0644`.
   - Creates `/opt/server/ci` owned by `www-data:www-data` with mode `0755`.
   - Deploys `ci/index.html` to `/opt/server/ci/index.html` owned by `www-data:www-data` with mode `0644`.
   - Creates `/opt/server/status` owned by `www-data:www-data` with mode `0755`.
   - Deploys `status/index.html` to `/opt/server/status/index.html` owned by `www-data:www-data` with mode `0644`.
   - Iteration expansion:
     - `test.cluster.local` maps to directory `test`.
     - `ci.cluster.local` maps to directory `ci`.
     - `status.cluster.local` maps to directory `status`.
   - Resources: one package, two templates, one service, three directories, and three `cookbook_file` resources.
   - Detailed Nginx base and security settings require verification against the rendered templates.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`, owned by `root:root`.
   - Creates `/etc/ssl/private` with mode `0710`, owned by `root:ssl-cert`.
   - Generates a self-signed 2048-bit RSA certificate and unencrypted private key for `test.cluster.local` when either file is absent:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Private key: `/etc/ssl/private/test.cluster.local.key`
   - Generates a self-signed 2048-bit RSA certificate and unencrypted private key for `ci.cluster.local` when either file is absent:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Private key: `/etc/ssl/private/ci.cluster.local.key`
   - Generates a self-signed 2048-bit RSA certificate and unencrypted private key for `status.cluster.local` when either file is absent:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Private key: `/etc/ssl/private/status.cluster.local.key`
   - Uses 365-day validity, common names matching the hostnames, and the subject email `admin@example.com`.
   - Sets each private key to mode `0640` and ownership `root:ssl-cert`.
   - Notifies a delayed Nginx reload after certificate generation.
   - Iteration expansion:
     - `test.cluster.local`
     - `ci.cluster.local`
     - `status.cluster.local`
   - Resources: one package resource, one group, two directories, and three certificate-generation execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Notifies a delayed Nginx reload when site templates, enabled links, or default-site removal changes.
   - Site variables:
     - `test.cluster.local`: root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local`: root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`: root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
   - Resources: three templates, three links, and one file deletion.
   - The supplied plan describes HTTP-to-HTTPS redirects, HTTP/2, TLS versions, HSTS, security headers, compression, `try_files`, restricted paths, and per-site logs; these details require verification against `site.conf.erb`.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**System package dependencies**: `nginx`, `fail2ban`, `ufw`, `openssl`, `ca-certificates`

**Service dependencies**: `nginx`, `fail2ban`, `ssh`

## Credentials

**Detection Summary**: No externally supplied credentials were identified in the supplied plan. Complete credential verification requires scanning all cookbook files, including `cookbooks/nginx-multisite/recipes/ssl.rb`, for secret providers, environment-variable secrets, hardcoded passwords, and vault integrations.

**Source**:
  - **Provider**: None detected for externally supplied secrets
  - **URL**: None
  - **Path**: None

### Generated TLS Private Keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by the OpenSSL command
- **Usage context**: Nginx HTTPS private keys
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`

### Certificate Subject Email

- **Variable/value**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL subject string
- **Usage context**: Subject email field of each self-signed certificate
- **Security classification**: Not an authentication credential

### Certificate References

- **Variable(s)**: `node['nginx']['ssl']['certificate_path']`, `node['nginx']['ssl']['private_key_path']`, `cert_file`, `key_file`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/attributes/default.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Certificates in `/etc/ssl/certs`; private keys in `/etc/ssl/private`
- **Usage context**: Nginx TLS configuration
- **Verification status**: Attribute definitions and values require confirmation from `attributes/default.rb`.

## Checks for the Migration

**Files to verify**:

- `cookbooks/nginx-multisite/attributes/default.rb`
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
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`
- `/var/log/auth.log`

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80` redirects with `301`; HTTPS `443` serves `/opt/server/test/index.html`
- `ci.cluster.local`: HTTP `80` redirects with `301`; HTTPS `443` serves `/opt/server/ci/index.html`
- `status.cluster.local`: HTTP `80` redirects with `301`; HTTPS `443` serves `/opt/server/status/index.html`
- SSH: TCP `22`; UFW allows access, root login is disabled, and password authentication is disabled

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

**Total template render operations**: `7`

## Pre-flight checks

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
  rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl status nginx
systemctl status fail2ban
systemctl status ssh
systemctl is-enabled nginx
systemctl is-active nginx

# Configuration validation
nginx -t
sshd -t

# Fail2ban validation
fail2ban-client status
fail2ban-client status sshd

# UFW validation
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# SSH hardening validation
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config

# Kernel security validation
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
cat /etc/sysctl.d/99-security.conf

# Listening ports and processes
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
ps aux | grep '[n]ginx'
ufw status numbered | grep -E '22|80|443'
```

### `test.cluster.local` checks

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject | grep 'CN = test.cluster.local'
stat -c '%a %U %G' /etc/ssl/private/test.cluster.local.key

stat -c '%a %U %G' /opt/server/test
stat -c '%a %U %G' /opt/server/test/index.html
readlink -f /etc/nginx/sites-enabled/test.cluster.local
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
```

Expected values: HTTP status `301`; HTTPS serves the test index; key mode and ownership `640 root ssl-cert`; document-root directory `755 www-data www-data`; index file `644 www-data www-data`; enabled link targets `/etc/nginx/sites-available/test.cluster.local`.

### `ci.cluster.local` checks

```bash
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
curl -k --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject | grep 'CN = ci.cluster.local'
stat -c '%a %U %G' /etc/ssl/private/ci.cluster.local.key

stat -c '%a %U %G' /opt/server/ci
stat -c '%a %U %G' /opt/server/ci/index.html
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
```

Expected values: HTTP status `301`; HTTPS serves the CI index; key mode and ownership `640 root ssl-cert`; document-root directory `755 www-data www-data`; index file `644 www-data www-data`; enabled link targets `/etc/nginx/sites-available/ci.cluster.local`.

### `status.cluster.local` checks

```bash
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
curl -k --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject | grep 'CN = status.cluster.local'
stat -c '%a %U %G' /etc/ssl/private/status.cluster.local.key

stat -c '%a %U %G' /opt/server/status
stat -c '%a %U %G' /opt/server/status/index.html
readlink -f /etc/nginx/sites-enabled/status.cluster.local
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
```

Expected values: HTTP status `301`; HTTPS serves the status index; key mode and ownership `640 root ssl-cert`; document-root directory `755 www-data www-data`; index file `644 www-data www-data`; enabled link targets `/etc/nginx/sites-available/status.cluster.local`.

### Reload and notification checks

Verify the following notification behavior:

- `/etc/nginx/nginx.conf` → Nginx reload
- `/etc/nginx/conf.d/security.conf` → Nginx reload
- `/etc/nginx/sites-available/test.cluster.local` → Nginx reload
- `/etc/nginx/sites-available/ci.cluster.local` → Nginx reload
- `/etc/nginx/sites-available/status.cluster.local` → Nginx reload
- Site-enabled link changes → Nginx reload
- Generated certificates or private keys → Nginx reload
- `/etc/fail2ban/jail.local` → Fail2ban restart
- `/etc/sysctl.d/99-security.conf` → `sysctl -p /etc/sysctl.d/99-security.conf`
- SSH hardening changes → SSH restart

### Additional checks

```bash
# Default site removal
test ! -e /etc/nginx/sites-enabled/default

# Global logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log

# Fail2ban and SSH logs
journalctl -u fail2ban --no-pager -n 50
tail -n 50 /var/log/auth.log
```