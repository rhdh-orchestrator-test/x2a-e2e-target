---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, OpenSSL, CA certificates, Fail2ban, and UFW; configures Nginx, TLS certificates, site document roots, HTTP-to-HTTPS virtual hosts, firewall rules, kernel security settings, and SSH hardening. The supplied execution analysis confirms the recipe order, resources, site iterations, file paths, and credential-handling structure. Detailed attribute values, template contents, and Chef notification relationships require verification against the cookbook source before migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

All three configured sites have SSL enabled.

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - HTTP behavior: Listens on port `80` and redirects to HTTPS
  - HTTPS behavior: Listens on port `443` with HTTP/2
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - SSL: Enabled
  - Static content source: `test/index.html`
  - Access log: `/var/log/nginx/test.cluster.local_access.log`
  - Error log: `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - HTTP behavior: Listens on port `80` and redirects to HTTPS
  - HTTPS behavior: Listens on port `443` with HTTP/2
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - SSL: Enabled
  - Static content source: `ci/index.html`
  - Access log: `/var/log/nginx/ci.cluster.local_access.log`
  - Error log: `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - HTTP behavior: Listens on port `80` and redirects to HTTPS
  - HTTPS behavior: Listens on port `443` with HTTP/2
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - SSL: Enabled
  - Static content source: `status/index.html`
  - Access log: `/var/log/nginx/status.cluster.local_access.log`
  - Error log: `/var/log/nginx/status.cluster.local_error.log`

- **fail2ban**: Nginx and SSH intrusion-prevention service
  - Package: `fail2ban`
  - Service: Enabled and started
  - Configuration: `/etc/fail2ban/jail.local`

- **ufw**: Host firewall
  - Package: `ufw`
  - Default policy: Deny incoming traffic
  - Allowed services: SSH, HTTP, and HTTPS
  - Firewall state: Enabled

- **ssh**: SSH service hardened by the cookbook
  - Root login: Disabled
  - Password authentication: Disabled
  - Configuration file: `/etc/ssh/sshd_config`

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
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
```

**Providers**: None. No custom resource provider is used by the executed recipe flow.

No static file paths were listed in the supplied cookbook directory listing. The `nginx.rb` recipe references cookbook files named `test/index.html`, `ci/index.html`, and `status/index.html`; these payload files must be supplied in the Ansible project if required.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role must import task files in the same order: security, Nginx, SSL, and virtual sites.

2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures the `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` jails. Detailed template values require verification against the template source.
   - Sets UFW default incoming policy to deny.
   - Allows SSH on port `22`, HTTP on port `80`, and HTTPS on port `443`.
   - Enables UFW.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - The template is intended to configure reverse-path filtering, redirect and source-route rejection, martian logging, ICMP controls, IPv6 disablement, SYN cookies, and TCP retry/backlog settings. Exact values require verification against the template source.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Declares the SSH service for restart when hardening settings change.
   - Resources: `package` 1, `service` 2, `template` 2, and `execute` 8.

3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test`, owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/test/index.html` from `test/index.html`, owned by `www-data:www-data`, mode `0644`.
   - Creates `/opt/server/ci`, owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/ci/index.html` from `ci/index.html`, owned by `www-data:www-data`, mode `0644`.
   - Creates `/opt/server/status`, owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/status/index.html` from `status/index.html`, owned by `www-data:www-data`, mode `0644`.
   - Iterations: the document-root and static-file loop runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Resources: `package` 1, `template` 2, `service` 1, `directory` 3, and `cookbook_file` 3.
   - Exact Nginx configuration directives and reload notifications require verification against the two Nginx templates and recipe source.

4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` owned by `root:root`, mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert`, mode `0710`.
   - Generates a self-signed RSA certificate and private key for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
   - Generates a self-signed RSA certificate and private key for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=ci.cluster.local/emailAddress=admin@example.com`
   - Generates a self-signed RSA certificate and private key for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=status.cluster.local/emailAddress=admin@example.com`
   - Certificate generation uses RSA `2048`, validity of `365` days, key mode `0640`, owner `root`, and group `ssl-cert`.
   - Iterations: the SSL loop runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`; all three have SSL enabled.
   - Resources: `package` 1, `group` 1, `directory` 2, and `execute` 3.

5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Links `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.
   - Uses document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Links `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Uses document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Links `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.
   - Uses document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Iterations: the site loop runs for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - The intended virtual-host behavior is HTTP on port `80`, HTTP-to-HTTPS redirection, and HTTPS with HTTP/2 on port `443`. Exact TLS directives, security headers, HSTS, CSP, compression, and access/error-log configuration require verification against `site.conf.erb`.
   - Resources: `template` 3, `link` 3, and `file` 1.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**System package dependencies**:
- `nginx`
- `openssl`
- `ca-certificates`
- `fail2ban`
- `ufw`

**Service dependencies**:
- `nginx`: Enabled and started; configuration and certificate changes require configuration validation and reload behavior.
- `fail2ban`: Enabled and started; configuration changes require service restart behavior.
- `ssh`: Restarted when SSH hardening settings change.

## Credentials

**Detection Summary**: No external application credentials, passwords, API keys, data bags, Chef Vault references, or secret-manager integrations were detected across the supplied cookbook files.

**Source**:
- **Provider**: None detected
- **URL**: None
- **Path**: None

### Self-signed TLS private keys

- **Variable(s)**: `key_file`, `/etc/ssl/private/test.cluster.local.key`, `/etc/ssl/private/ci.cluster.local.key`, `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated files; not stored in a data bag, Chef Vault, environment variable, or external secret manager.
- **Usage context**: TLS private keys used by Nginx for HTTPS termination.
- **Permissions**: Owner `root`, group `ssl-cert`, mode `0640`.

### TLS certificates

- **Variable(s)**: `cert_file`, `/etc/ssl/certs/test.cluster.local.crt`, `/etc/ssl/certs/ci.cluster.local.crt`, `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated self-signed certificates.
- **Usage context**: TLS certificates used by Nginx for HTTPS virtual hosts.

### Certificate subject email

- **Variable/value**: `admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command.
- **Usage context**: Email address embedded in the subject of each self-signed certificate.

## Checks for the Migration

**Files to verify**:
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
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

**Service endpoints to check**:
- `test.cluster.local`: ports `80` and `443`
- `ci.cluster.local`: ports `80` and `443`
- `status.cluster.local`: ports `80` and `443`
- SSH firewall access: port `22`

**Templates rendered**:
- `fail2ban.jail.local.erb`: 1 render to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: 1 render to `/etc/nginx/nginx.conf`
- `security.conf.erb`: 1 render to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: 1 render to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: 3 renders:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Confirm installed packages
dpkg -l nginx openssl ca-certificates fail2ban ufw

# Nginx service
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t

# Fail2ban service
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# SSH service and configuration
systemctl status ssh || systemctl status sshd
sshd -t
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# Confirm Nginx configuration files
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test ! -e /etc/nginx/sites-enabled/default

# Confirm enabled virtual-host links
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

# Firewall checks
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'
ufw status verbose | grep 'Default: deny'

# Kernel security configuration
test -f /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
```

### Site: `test.cluster.local`

```bash
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
ls -l /etc/ssl/certs/test.cluster.local.crt
ls -l /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

curl -I --resolve test.cluster.local:80:127.0.0.1 \
  http://test.cluster.local/

curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

curl -k -s -D - --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | grep -E \
  'HTTP/|Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Content-Security-Policy'
```

### Site: `ci.cluster.local`

```bash
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/ssl/certs/ci.cluster.local.crt
ls -l /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

curl -I --resolve ci.cluster.local:80:127.0.0.1 \
  http://ci.cluster.local/

curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

curl -k -s -D - --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ | grep -E \
  'HTTP/|Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Content-Security-Policy'
```

### Site: `status.cluster.local`

```bash
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
ls -l /etc/ssl/certs/status.cluster.local.crt
ls -l /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

curl -I --resolve status.cluster.local:80:127.0.0.1 \
  http://status.cluster.local/

curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

curl -k -s -D - --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ | grep -E \
  'HTTP/|Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|Content-Security-Policy'
```