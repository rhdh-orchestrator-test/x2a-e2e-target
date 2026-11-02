---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Migrate the `nginx-multisite` Chef cookbook to Ansible while preserving its validated execution order: security packages and hardening, nginx installation and global configuration, SSL package and certificate setup, and three named virtual hosts. The configured sites are `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`, with document roots under `/opt/server`, HTTP and HTTPS endpoints on ports 80 and 443, locally generated TLS keys and certificates, and site-specific nginx configuration. Template directives, metadata, attribute contents, certificate guards, and notification relationships should be verified against the source cookbook before implementation because they were not present in the supplied structured analysis.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The analyzed `nginx.sites` collection contains exactly three sites. Each site is configured with `ssl_enabled: true`.

- **test.cluster.local**: Static nginx virtual host for the test environment
  - Location/Path: `/opt/server/test`
  - HTTP endpoint: port `80`; intended to redirect to HTTPS
  - HTTPS endpoint: port `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Static content source: `test/index.html`
  - Static content destination: `/opt/server/test/index.html`

- **ci.cluster.local**: Static nginx virtual host for continuous integration
  - Location/Path: `/opt/server/ci`
  - HTTP endpoint: port `80`; intended to redirect to HTTPS
  - HTTPS endpoint: port `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Static content source: `ci/index.html`
  - Static content destination: `/opt/server/ci/index.html`

- **status.cluster.local**: Static nginx virtual host for service status
  - Location/Path: `/opt/server/status`
  - HTTP endpoint: port `80`; intended to redirect to HTTPS
  - HTTPS endpoint: port `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Static content source: `status/index.html`
  - Static content destination: `/opt/server/status/index.html`

### Security Collection

The analyzed `security` collection contains three named areas:

- **fail2ban**
  - Enabled by default: `true`
  - Installs and starts the `fail2ban` service.
- **ufw**
  - Enabled by default: `true`
  - Installs UFW and configures firewall behavior.
- **ssh**
  - `disable_root: true`
  - `password_auth: false`
  - Controls root-login and password-authentication hardening.

The recipes do not iterate over this collection. They use these values as conditional configuration controls.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
recipes/default.rb
recipes/security.rb
recipes/nginx.rb
recipes/ssl.rb
recipes/sites.rb
```

**Providers:**
```text
```

No custom-resource provider is used by the execution tree.

**Templates:**
```text
templates/default/fail2ban.jail.local.erb
templates/default/nginx.conf.erb
templates/default/security.conf.erb
templates/default/site.conf.erb
templates/default/sysctl-security.conf.erb
```

**Attributes:**
```text
attributes/default.rb
```

**Files:**
```text
```

The recipes reference these static files through `cookbook_file`, but no static files are included in the supplied directory listing:

```text
test/index.html
ci/index.html
status/index.html
```

The Ansible migration must provide or otherwise source the corresponding static content.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - The Ansible role should preserve this logical order: security, nginx, SSL, then virtual hosts.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures UFW default-deny behavior and allows SSH, HTTP, and HTTPS.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Applies sysctl settings through a reload handler or command.
   - Conditionally enforces `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Conditionally enforces `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Restarts the distribution-appropriate SSH service when SSH configuration changes.
   - The supplied execution analysis confirms the security collection areas and resource ordering. Exact template directives and handler notification relationships require verification from the source templates and recipe.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates the three site document roots:
     - `/opt/server/test` for `test.cluster.local`
     - `/opt/server/ci` for `ci.cluster.local`
     - `/opt/server/status` for `status.cluster.local`
   - Deploys the three static index files:
     - `test/index.html` to `/opt/server/test/index.html`
     - `ci/index.html` to `/opt/server/ci/index.html`
     - `status/index.html` to `/opt/server/status/index.html`
   - The site iteration runs exactly three times, for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - The supplied execution analysis confirms the package, template, service, directory, and static-file resource ordering. Exact nginx directives in the templates require verification.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root:root` and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root:ssl-cert` and mode `0710`.
   - Processes the SSL configuration for these three named sites:
     - `test.cluster.local`
     - `ci.cluster.local`
     - `status.cluster.local`
   - Generates or manages:
     - `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`
     - `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`
     - `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`
   - The analyzed configuration marks SSL as enabled for all three sites.
   - The supplied execution analysis confirms the certificate-generation commands and the three site iterations, but does not verify certificate guards, certificate subjects, key permissions, or nginx notification relationships. These details must be checked against `cookbooks/nginx-multisite/recipes/ssl.rb` before implementation.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` once for each named site.
   - Creates one `sites-enabled` symlink for each rendered site.
   - Iterations:
     - `test.cluster.local`
       - Render destination: `/etc/nginx/sites-available/test.cluster.local`
       - Symlink: `/etc/nginx/sites-enabled/test.cluster.local`
       - Document root: `/opt/server/test`
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Private key: `/etc/ssl/private/test.cluster.local.key`
     - `ci.cluster.local`
       - Render destination: `/etc/nginx/sites-available/ci.cluster.local`
       - Symlink: `/etc/nginx/sites-enabled/ci.cluster.local`
       - Document root: `/opt/server/ci`
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Private key: `/etc/ssl/private/ci.cluster.local.key`
     - `status.cluster.local`
       - Render destination: `/etc/nginx/sites-available/status.cluster.local`
       - Symlink: `/etc/nginx/sites-enabled/status.cluster.local`
       - Document root: `/opt/server/status`
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Private key: `/etc/ssl/private/status.cluster.local.key`
   - Removes `/etc/nginx/sites-enabled/default`.
   - The supplied execution analysis confirms the three site iterations and resource order. The detailed virtual-host directives reported in the original plan require verification against `cookbooks/nginx-multisite/templates/default/site.conf.erb`.

## Dependencies

**External cookbook dependencies**: None verified in the supplied execution analysis. Confirm against cookbook metadata before implementation.

**System package dependencies**:
- `nginx`
- `openssl`
- `ca-certificates`
- `fail2ban`
- `ufw`

**Service dependencies**:
- `nginx`
- `fail2ban`
- SSH service: `ssh` on Ubuntu or commonly `sshd` on CentOS

**Firewall access configured**:
- SSH: port `22/tcp`
- HTTP: port `80/tcp`
- HTTPS: port `443/tcp`

The original plan reports Ubuntu `>= 18.04` and CentOS `>= 7.0` support, but the supplied structured analysis does not include metadata. Platform support must therefore be confirmed against the cookbook metadata.

## Credentials

**Detection Summary**: Three locally generated TLS private keys were identified across the SSL and site configuration resources. No externally sourced application credentials, database passwords, API tokens, data bags, vault references, or secret-provider references were detected.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed TLS private keys

- **Variable(s)**: `key_file`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Locally generated filesystem key files
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts
- **Key paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Reported permissions**: Mode `0640`, owner `root`, group `ssl-cert`; verify against the source recipe because this was not included in the structured analysis.

### Certificate subject email

- **Variable(s)**: Literal `admin@example.com`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded, non-secret certificate metadata
- **Usage context**: Subject email address in the generated self-signed certificates
- **Validation status**: Reported in the original plan but not confirmed by the supplied structured analysis.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, `node['vault']`, `node['secrets']`, environment-variable secret references, embedded database credentials, or hardcoded API tokens were identified.

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
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`

**Service endpoints to check**:

- SSH: TCP `22`
- `test.cluster.local`: TCP `80` and TCP `443`
- `ci.cluster.local`: TCP `80` and TCP `443`
- `status.cluster.local`: TCP `80` and TCP `443`

**Unix sockets**: None configured by this cookbook.

**Network interfaces**: No specific bind address is configured in the analyzed plan; verify that nginx uses the intended wildcard bindings.

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
  - Rendered once to `/etc/fail2ban/jail.local`.
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
  - Rendered once to `/etc/nginx/nginx.conf`.
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`
  - Rendered once to `/etc/nginx/conf.d/security.conf`.
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`
  - Rendered once to `/etc/sysctl.d/99-security.conf`.
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Rendered three times:
    - `/etc/nginx/sites-available/test.cluster.local`
    - `/etc/nginx/sites-available/ci.cluster.local`
    - `/etc/nginx/sites-available/status.cluster.local`

The supplied structured analysis confirms the template paths and rendering counts. It does not include template contents, so directives such as HTTP-to-HTTPS redirects, HTTP/2, HSTS, CSP, cipher lists, rate limits, Fail2ban jails, and exact sysctl values must be verified before migration sign-off.

## Pre-flight checks

```bash
# Package status
dpkg -l nginx openssl ca-certificates fail2ban ufw 2>/dev/null || \
  rpm -q nginx openssl ca-certificates fail2ban ufw

# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh 2>/dev/null || systemctl status sshd

# Nginx configuration validation
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'

# Firewall status
ufw status verbose
ufw status numbered

# SSH configuration validation
sshd -t
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# Sysctl configuration presence
test -f /etc/sysctl.d/99-security.conf
sysctl net.ipv4.conf.all.rp_filter

# Listener checks
ss -tlnp | grep ':22 '
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
```

### `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

readlink -f /etc/nginx/sites-enabled/test.cluster.local
grep -E 'server_name|root|listen|ssl_certificate|ssl_certificate_key|access_log|error_log' \
  /etc/nginx/sites-available/test.cluster.local

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%A %U:%G %n' /etc/ssl/private/test.cluster.local.key

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/
```

Verify the document root is `/opt/server/test`, the certificate and key paths are site-specific, HTTP redirects to HTTPS, and HTTPS returns the expected site content.

### `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

readlink -f /etc/nginx/sites-enabled/ci.cluster.local
grep -E 'server_name|root|listen|ssl_certificate|ssl_certificate_key|access_log|error_log' \
  /etc/nginx/sites-available/ci.cluster.local

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%A %U:%G %n' /etc/ssl/private/ci.cluster.local.key

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/
```

Verify the document root is `/opt/server/ci`, the certificate and key paths are site-specific, HTTP redirects to HTTPS, and HTTPS returns the expected site content.

### `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

readlink -f /etc/nginx/sites-enabled/status.cluster.local
grep -E 'server_name|root|listen|ssl_certificate|ssl_certificate_key|access_log|error_log' \
  /etc/nginx/sites-available/status.cluster.local

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%A %U:%G %n' /etc/ssl/private/status.cluster.local.key

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
```

Verify the document root is `/opt/server/status`, the certificate and key paths are site-specific, HTTP redirects to HTTPS, and HTTPS returns the expected site content.

### Shared virtual-host and security checks

```bash
# The packaged default site should be removed
test ! -e /etc/nginx/sites-enabled/default

# Verify expected site names and listeners
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local|listen'

# Verify nginx and security configuration files exist
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf

# Verify all three site-specific log pairs
test -f /var/log/nginx/test.cluster.local_access.log
test -f /var/log/nginx/test.cluster.local_error.log
test -f /var/log/nginx/ci.cluster.local_access.log
test -f /var/log/nginx/ci.cluster.local_error.log
test -f /var/log/nginx/status.cluster.local_access.log
test -f /var/log/nginx/status.cluster.local_error.log
```

Confirm UFW is active with default incoming policy deny and allows ports 22, 80, and 443. Confirm the SSH service name and handlers are correct for the target distribution.