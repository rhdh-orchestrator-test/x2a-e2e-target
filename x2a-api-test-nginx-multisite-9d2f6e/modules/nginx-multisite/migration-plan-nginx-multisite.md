---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; generates locally self-signed RSA 2048-bit certificates; deploys static site content; applies nginx, kernel, firewall, fail2ban, and SSH hardening; disables root SSH login and SSH password authentication; and allows SSH, HTTP, and HTTPS traffic. Detailed attribute and template values require verification against `attributes/default.rb` and the ERB templates because those contents were not included in the available structured analysis.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; content `/opt/server/test/index.html`

- **ci.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; content `/opt/server/ci/index.html`

- **status.cluster.local**: Static HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; content `/opt/server/status/index.html`

**Security configuration**:

- **fail2ban**: Enabled service using `/etc/fail2ban/jail.local`
- **ufw**: Enabled firewall with default deny policy and rules for TCP ports `22`, `80`, and `443`
- **ssh**: Root login disabled and password authentication disabled; SSH restarts only when the corresponding configuration changes

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

No provider file is used by the execution tree. The `lineinfile` custom resource mentioned by structural analysis is not part of the executed recipe flow.

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

The recipes deploy `index.html` through `cookbook_file` with dynamic sources `test/index.html`, `ci/index.html`, and `status/index.html`. No static file paths were present in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. `nginx-multisite::security` (`cookbooks/nginx-multisite/recipes/security.rb`)
2. `nginx-multisite::nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)
3. `nginx-multisite::ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)
4. `nginx-multisite::sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

The execution order must be preserved in Ansible.

1. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Applies guarded UFW commands for default deny, SSH port `22`, HTTP port `80`, HTTPS port `443`, and firewall enablement.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Configures SSH root-login and password-authentication hardening through guarded commands.
   - Declares the `ssh` service with action `nothing`; delayed notifications restart it after SSH configuration changes.
   - Delayed notifications restart fail2ban after jail configuration changes and reload sysctl after kernel configuration changes.
   - The execution tree contains package, service, template, and execute resources. Detailed template values require manual verification against the supplied ERB file.

2. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Changes to global nginx templates trigger delayed nginx reloads.
   - Creates `/opt/server/test`, owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/test/index.html` from `test/index.html`, mode `0644`.
   - Creates `/opt/server/ci`, owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/ci/index.html` from `ci/index.html`, mode `0644`.
   - Creates `/opt/server/status`, owned by `www-data:www-data`, mode `0755`, and deploys `/opt/server/status/index.html` from `status/index.html`, mode `0644`.
   - The execution tree contains one package, two templates, one service, three directories, and three `cookbook_file` resources.
   - Detailed worker, TLS, rate-limit, buffer, gzip, and security settings require manual template verification.

3. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates group `ssl-cert`.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` owned by `root:ssl-cert` with mode `0710`.
   - Generates a self-signed RSA 2048-bit certificate and unencrypted private key for **test.cluster.local**:
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Key: `/etc/ssl/private/test.cluster.local.key`
   - Generates a self-signed RSA 2048-bit certificate and unencrypted private key for **ci.cluster.local**:
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Key: `/etc/ssl/private/ci.cluster.local.key`
   - Generates a self-signed RSA 2048-bit certificate and unencrypted private key for **status.cluster.local**:
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Key: `/etc/ssl/private/status.cluster.local.key`
   - Certificate generation is guarded so it is skipped when both certificate and key already exist.
   - Generated keys are assigned owner `root`, group `ssl-cert`, and mode `0640`.
   - Certificate generation triggers delayed nginx reloads.
   - The execution tree contains one package resource, one group resource, two directory resources, and three certificate-generation commands.

4. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **test.cluster.local** to `/etc/nginx/sites-available/test.cluster.local`, mode `0644`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to the test site configuration.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **ci.cluster.local** to `/etc/nginx/sites-available/ci.cluster.local`, mode `0644`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to the CI site configuration.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for **status.cluster.local** to `/etc/nginx/sites-available/status.cluster.local`, mode `0644`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to the status site configuration.
   - Template and link changes trigger delayed nginx reloads.
   - Removes `/etc/nginx/sites-enabled/default` and reloads nginx when it is removed.
   - Each site receives `server_name`, `document_root`, `ssl_enabled`, `cert_file`, and `key_file` values.
   - The execution tree contains three templates, three links, and one file resource.
   - The supplied plan expects HTTP-to-HTTPS redirects and HTTPS listeners on ports `80` and `443`; detailed headers, HSTS, CSP, gzip, `try_files`, and TLS settings require manual verification against `site.conf.erb`.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata; verify against cookbook metadata before migration.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `ssh`

**Supported platforms**: The supplied plan lists Ubuntu `>= 18.04` and CentOS `>= 7.0`; verify these claims against cookbook metadata before migration.

**Firewall access**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`

## Credentials

**Detection Summary**: No application credentials or external secret-provider integrations were detected. Three locally generated TLS private keys and three locally generated TLS certificates are created by the cookbook.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed TLS private keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated key files; not stored in a data bag, Chef Vault, CyberArk, HashiCorp Vault, AWS Secrets Manager, or environment variable.
- **Usage context**: Nginx HTTPS private keys for the three virtual hosts.
- **Protection**: `/etc/ssl/private` mode `0710`; keys owned by `root:ssl-cert` with mode `0640`.

### Self-signed TLS certificates

- **Variable(s)**: `cert_file`; `/etc/ssl/certs/test.cluster.local.crt`; `/etc/ssl/certs/ci.cluster.local.crt`; `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated certificate files.
- **Usage context**: Nginx HTTPS certificate files.
- **Certificate attributes**: The plan specifies self-signed RSA 2048-bit certificates valid for `365` days, with common names matching the site hostnames. Verify these values against `recipes/ssl.rb` and the attributes file.

No passwords, tokens, connection strings, encrypted data bags, Chef Vault calls, CyberArk calls, Conjur variables, or secret-related node attributes were detected.

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
- `/etc/nginx/sites-enabled/default` should be absent
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
- `/var/log/auth.log`

**Service endpoints to check**:

- SSH: TCP `22`
- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`

**Unix sockets**: None configured by this cookbook.

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: 1 render to `/etc/fail2ban/jail.local`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: 1 render to `/etc/nginx/nginx.conf`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: 1 render to `/etc/nginx/conf.d/security.conf`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: 1 render to `/etc/sysctl.d/99-security.conf`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: 3 renders:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Package checks
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
  rpm -q nginx fail2ban ufw openssl ca-certificates

# Service checks
systemctl is-active nginx
systemctl is-active fail2ban
systemctl is-active ssh

# Configuration checks
nginx -t
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

# Firewall checks
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
ss -tlnp | grep -E ':(22|80|443) '

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U %G' /etc/ssl/private/test.cluster.local.key

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U %G' /etc/ssl/private/ci.cluster.local.key

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U %G' /etc/ssl/private/status.cluster.local.key

# Virtual-host and listener checks
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
nginx -T | grep -E 'listen 80|listen 443'
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Fail2ban checks
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# SSH checks
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
systemctl is-active ssh

# Kernel security checks
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.default.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.accept_source_route
sysctl net.ipv4.conf.all.log_martians
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.icmp_echo_ignore_broadcasts
sysctl net.ipv6.conf.all.disable_ipv6

# Confirm no default site remains
test ! -e /etc/nginx/sites-enabled/default
```