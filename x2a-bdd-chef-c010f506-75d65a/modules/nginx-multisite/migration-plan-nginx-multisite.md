---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, Fail2ban, UFW, OpenSSL, and CA certificates; applies SSH, kernel, firewall, and Fail2ban security settings; creates self-signed certificates; deploys static site content; configures nginx virtual hosts; and enables HTTP-to-HTTPS redirects. The Ansible implementation must preserve the recipe order, site names, paths, ports, resource guards, file ownership and permissions, and service notification behavior. Template directives, guards, modes, and notification timing require source-level verification where they are not confirmed by the supplied structural analysis.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **`test.cluster.local`**: SSL-enabled static nginx site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **`ci.cluster.local`**: SSL-enabled static nginx site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **`status.cluster.local`**: SSL-enabled static nginx site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

- **`fail2ban`**: Host intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Protects SSH and nginx traffic; no dedicated listening socket configured by this cookbook
  - Key Config: Package installed and service enabled and started. Exact jail directives and notification behavior require source-level verification.

- **`ufw`**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config: Default incoming policy is deny and the firewall is enabled. Exact command guards require source-level verification.

- **`ssh`**: SSH hardening configuration
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no` and `PasswordAuthentication no` are configured when the corresponding security settings are enabled.

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
└── templates/
    └── default/
        ├── fail2ban.jail.local.erb
        ├── nginx.conf.erb
        ├── security.conf.erb
        ├── site.conf.erb
        └── sysctl-security.conf.erb
```

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

No provider file is used by the execution tree.

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

The recipes reference static cookbook files through `cookbook_file`: `test/index.html`, `ci/index.html`, and `status/index.html`. These files are not present in the supplied directory listing. The Ansible role must provide equivalent static content at the corresponding document roots.

The structural analysis mentions `cookbooks/nginx-multisite/resources/lineinfile.rb`, but it is not part of the supplied execution tree and is not executed by these recipes. It is excluded from the migration flow unless source-level analysis confirms that it is required.

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security`, `nginx`, `ssl`, and `sites` in that order.
   - The Ansible role should import task files in the same order:
     ```yaml
     - import_tasks: security.yml
     - import_tasks: nginx.yml
     - import_tasks: ssl.yml
     - import_tasks: sites.yml
     ```
   - SSL certificate generation must occur before virtual host configuration is applied.

2. **`security`** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Configures and enables the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures UFW with a deny-by-default policy and allows TCP ports `22`, `80`, and `443`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Applies the configured kernel security settings and reloads sysctl when the configuration changes.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts `sshd` only when the SSH configuration changes.
   - Resource summary: one package resource installing two packages, one Fail2ban template, one Fail2ban service, five UFW execute resources, one sysctl template, one sysctl reload execute resource, two conditional SSH execute resources, and one `sshd` service resource.
   - Exact template directives, file modes, guards, and delayed notification timing require source-level verification.

3. **`nginx`** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` for `test.cluster.local`, owned by `nginx:nginx` with mode `0755`.
   - Deploys `/opt/server/test/index.html` from `test/index.html`, owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/ci` for `ci.cluster.local`, owned by `nginx:nginx` with mode `0755`.
   - Deploys `/opt/server/ci/index.html` from `ci/index.html`, owned by `nginx:nginx` with mode `0644`.
   - Creates `/opt/server/status` for `status.cluster.local`, owned by `nginx:nginx` with mode `0755`.
   - Deploys `/opt/server/status/index.html` from `status/index.html`, owned by `nginx:nginx` with mode `0644`.
   - Iterations: the document-root and static-file operations run for **`test.cluster.local`**, **`ci.cluster.local`**, and **`status.cluster.local`**.
   - Resource summary confirmed by structural analysis: `package[nginx]`, two templates, `service[nginx]`, three directory resources, and three `cookbook_file` resources.
   - No `group[nginx]` resource or reference is confirmed by the supplied analysis. The nginx user and group must be treated as package or operating-system prerequisites unless source-level analysis proves otherwise.
   - Exact nginx directives, file modes, and reload notification behavior require source-level verification.

4. **`ssl`** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private`.
   - Evaluates SSL generation for **`test.cluster.local`**, **`ci.cluster.local`**, and **`status.cluster.local`**.
   - Generates the following certificate and key pair for `test.cluster.local`:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Common name: `test.cluster.local`
   - Generates the following certificate and key pair for `ci.cluster.local`:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Common name: `ci.cluster.local`
   - Generates the following certificate and key pair for `status.cluster.local`:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Common name: `status.cluster.local`
   - The reported certificate-generation command uses RSA `2048`, `365` days, self-signed X.509 certificates, and the subject email `admin@example.com`. These command details require source-level verification.
   - Certificate generation is guarded by the existence of both the certificate and key.
   - Generated private keys are intended to be owned by `root:ssl-cert` with mode `0640`.
   - Iterations: certificate generation runs for **`test.cluster.local`**, **`ci.cluster.local`**, and **`status.cluster.local`**.
   - Resource summary: one package resource installing two packages, one group, two directories, and three certificate-generation execute resources.
   - The configured SSL directory attributes and exact notification behavior require verification against `cookbooks/nginx-multisite/attributes/default.rb` and `recipes/ssl.rb`.

5. **`sites`** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available`.
   - Creates `/etc/nginx/sites-enabled`.
   - Contains an additional loop with three directory resources associated with the configured sites. The exact paths for these three resources are not confirmed by the supplied validation summary and must be obtained from the source before implementation.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
   - Template variables include `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Iterations: virtual-host templates and links run for **`test.cluster.local`**, **`ci.cluster.local`**, and **`status.cluster.local`**.
   - Each virtual host listens on HTTP `80`, redirects to HTTPS with status `301`, and listens on HTTPS `443` with SSL and HTTP/2.
   - The virtual hosts use document roots `/opt/server/test`, `/opt/server/ci`, and `/opt/server/status` respectively.
   - The virtual hosts use the corresponding certificate, private-key, access-log, and error-log paths listed in the Service Type and Instances section.
   - The reported virtual-host settings include TLS 1.2 and TLS 1.3, security headers, HSTS, gzip, `try_files $uri $uri/ =404`, and denial of `.htaccess`, `.git`, and `.svn` paths. These directives require source-level verification.
   - Resource summary: two explicitly identified site directories, three additional site-loop directory resources, three templates, three links, and one deleted file.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:
- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `nginx`
- `fail2ban`
- `sshd`

**Network dependencies**:
- TCP `22`: SSH
- TCP `80`: HTTP redirects
- TCP `443`: HTTPS virtual hosts

**Unix sockets**: None configured by the cookbook.

**Required operating-system identity**:
- The `nginx` user and group must exist for document-root and static-file ownership. The supplied analysis does not confirm that this cookbook creates the group.

## Credentials

**Detection Summary**: No credential-store integrations or retrieved credentials detected across the supplied execution flow.

**Source**:
- **Provider**: None detected
- **URL**: None
- **Path**: None

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, Conjur, CyberArk, or other secret-manager integration is present in the supplied execution tree.

### Locally generated TLS private keys

- **Variable(s)**: None retrieved from a credential store
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files under `/etc/ssl/private`
- **Usage context**: nginx HTTPS virtual hosts
- **Required protection**: `root:ssl-cert`, mode `0640`

The certificate subject email `admin@example.com` is certificate metadata, not an authentication secret.

## Checks for the Migration

**Files to verify**:
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` — must not exist
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
- `/opt/server/status/index.html`
- `/etc/ssl/certs`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
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
- `test.cluster.local`: HTTP TCP `80`; HTTPS TCP `443`
- `ci.cluster.local`: HTTP TCP `80`; HTTPS TCP `443`
- `status.cluster.local`: HTTP TCP `80`; HTTPS TCP `443`
- SSH: TCP `22`

**Templates rendered**:
- `fail2ban.jail.local.erb`: 1 render to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: 1 render to `/etc/nginx/nginx.conf`
- `security.conf.erb`: 1 render to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: 1 render to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: 3 renders:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

**Resource and behavior verification**:
- Confirm three additional directory resources in `recipes/sites.rb` and record their exact paths.
- Confirm SSL path attributes in `cookbooks/nginx-multisite/attributes/default.rb`.
- Confirm Fail2ban and UFW enabled defaults in `cookbooks/nginx-multisite/attributes/default.rb`.
- Confirm template directives, file modes, command guards, and delayed notification behavior from the recipe and template source.
- Confirm that the static source files are supplied by the Ansible role.

## Pre-flight checks

```bash
# Package status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

# nginx configuration validation
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'

# Network listeners
ss -tlnp | grep ':22 '
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# UFW status
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# Fail2ban status
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH validation
grep -E '^PermitRootLogin |^PasswordAuthentication ' /etc/ssh/sshd_config
sshd -t
systemctl is-active sshd

# Sysctl validation
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6

# nginx logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

### `test.cluster.local`

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -checkend 0
test -f /etc/ssl/private/test.cluster.local.key
stat -c '%U %G %a %n' /etc/ssl/private/test.cluster.local.key
grep -E 'root |ssl_certificate |ssl_certificate_key |listen ' \
  /etc/nginx/sites-available/test.cluster.local
test -f /opt/server/test/index.html

tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
```

Expected results:
- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200` for the static index page.
- The certificate subject contains `CN=test.cluster.local`.
- The certificate is not expired.
- The key is owned by `root:ssl-cert` with mode `640`.
- The document root is `/opt/server/test`.

### `ci.cluster.local`

```bash
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -checkend 0
test -f /etc/ssl/private/ci.cluster.local.key
stat -c '%U %G %a %n' /etc/ssl/private/ci.cluster.local.key
grep -E 'root |ssl_certificate |ssl_certificate_key |listen ' \
  /etc/nginx/sites-available/ci.cluster.local
test -f /opt/server/ci/index.html

tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
```

Expected results:
- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200` for the static index page.
- The certificate subject contains `CN=ci.cluster.local`.
- The certificate is not expired.
- The key is owned by `root:ssl-cert` with mode `640`.
- The document root is `/opt/server/ci`.

### `status.cluster.local`

```bash
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -checkend 0
test -f /etc/ssl/private/status.cluster.local.key
stat -c '%U %G %a %n' /etc/ssl/private/status.cluster.local.key
grep -E 'root |ssl_certificate |ssl_certificate_key |listen ' \
  /etc/nginx/sites-available/status.cluster.local
test -f /opt/server/status/index.html

tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
```

Expected results:
- HTTP returns `301` and redirects to HTTPS.
- HTTPS returns `200` for the static index page.
- The certificate subject contains `CN=status.cluster.local`.
- The certificate is not expired.
- The key is owned by `root:ssl-cert` with mode `640`.
- The document root is `/opt/server/status`.

### Certificate and ownership verification

```bash
stat -c '%U %G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

test ! -e /etc/nginx/sites-enabled/default
```

Expected results:
- All private keys are owned by `root:ssl-cert` with mode `640`.
- Each enabled-site link resolves to the corresponding site-available file.
- `/etc/nginx/sites-enabled/default` does not exist.