---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures Nginx as a multisite web server for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It enables HTTPS with locally generated 2048-bit, self-signed certificates, deploys site content and virtual hosts, configures Fail2ban and UFW, applies sysctl security settings, disables root SSH login, and disables SSH password authentication. Execution order is security hardening, Nginx installation and base configuration, SSL certificate generation, and site virtual-host configuration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: TCP `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: TCP `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: TCP `80` and `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

**Security configuration**:

- **fail2ban**: enabled; package installed and service enabled and started.
- **ufw**: enabled; default incoming policy denied; SSH, HTTP, and HTTPS allowed.
- **ssh**: root login disabled; password authentication disabled.

## File Structure

### Recipes

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

### Providers

```text
```

No provider files are used by the execution tree.

### Templates

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

### Attributes

```text
cookbooks/nginx-multisite/attributes/default.rb
```

### Files

No static files are listed in the supplied directory listing. The recipes deploy `index.html` through `cookbook_file`, but the source static files are not included in the supplied execution-tree file list.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - The migration must preserve this execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default incoming policy to deny.
   - Allows SSH, HTTP, and HTTPS through UFW.
   - Enables UFW non-interactively.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines `sysctl -p /etc/sysctl.d/99-security.conf` as an inactive command; it does not run by default because its action is `nothing` and no notification is shown.
   - Changes `/etc/ssh/sshd_config` to `PermitRootLogin no`.
   - Changes `/etc/ssh/sshd_config` to `PasswordAuthentication no`.
   - Declares the SSH service with action `nothing`; no SSH restart or reload is shown.
   - Execute resources: 8 total:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Iteration for **test.cluster.local**:
     - Creates `/opt/server/test` with mode `0755`.
     - Deploys the site-specific `index.html` to `/opt/server/test/index.html` with mode `0644`.
   - Iteration for **ci.cluster.local**:
     - Creates `/opt/server/ci` with mode `0755`.
     - Deploys the site-specific `index.html` to `/opt/server/ci/index.html` with mode `0644`.
   - Iteration for **status.cluster.local**:
     - Creates `/opt/server/status` with mode `0755`.
     - Deploys the site-specific `index.html` to `/opt/server/status/index.html` with mode `0644`.
   - No `www-data` group resource is included because it is not present in the supplied structured execution tree.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`, with the root owner and `ssl-cert` group.
   - Iteration for **test.cluster.local**:
     - Generates `/etc/ssl/private/test.cluster.local.key`.
     - Generates `/etc/ssl/certs/test.cluster.local.crt`.
     - Uses a 2048-bit RSA self-signed certificate valid for 365 days.
     - Uses common name `test.cluster.local`.
     - Sets the key to mode `0640` and ownership `root:ssl-cert`.
   - Iteration for **ci.cluster.local**:
     - Generates `/etc/ssl/private/ci.cluster.local.key`.
     - Generates `/etc/ssl/certs/ci.cluster.local.crt`.
     - Uses a 2048-bit RSA self-signed certificate valid for 365 days.
     - Uses common name `ci.cluster.local`.
     - Sets the key to mode `0640` and ownership `root:ssl-cert`.
   - Iteration for **status.cluster.local**:
     - Generates `/etc/ssl/private/status.cluster.local.key`.
     - Generates `/etc/ssl/certs/status.cluster.local.crt`.
     - Uses a 2048-bit RSA self-signed certificate valid for 365 days.
     - Uses common name `status.cluster.local`.
     - Sets the key to mode `0640` and ownership `root:ssl-cert`.
   - Each certificate subject uses:
     `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iteration for **test.cluster.local**:
     - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/test.cluster.local`.
     - Uses document root `/opt/server/test`.
     - Uses certificate `/etc/ssl/certs/test.cluster.local.crt`.
     - Uses private key `/etc/ssl/private/test.cluster.local.key`.
     - Creates `/etc/nginx/sites-enabled/test.cluster.local` as a link to the available configuration.
   - Iteration for **ci.cluster.local**:
     - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/ci.cluster.local`.
     - Uses document root `/opt/server/ci`.
     - Uses certificate `/etc/ssl/certs/ci.cluster.local.crt`.
     - Uses private key `/etc/ssl/private/ci.cluster.local.key`.
     - Creates `/etc/nginx/sites-enabled/ci.cluster.local` as a link to the available configuration.
   - Iteration for **status.cluster.local**:
     - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/status.cluster.local`.
     - Uses document root `/opt/server/status`.
     - Uses certificate `/etc/ssl/certs/status.cluster.local.crt`.
     - Uses private key `/etc/ssl/private/status.cluster.local.key`.
     - Creates `/etc/nginx/sites-enabled/status.cluster.local` as a link to the available configuration.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - No Nginx reload or restart is shown after site configuration changes. A controlled reload may be added only after validating the target behavior.

## Dependencies

**External cookbook dependencies**: Not specified.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no restart is shown

**Firewall allowances**:

- SSH
- HTTP
- HTTPS

## Credentials

**Detection Summary**: No externally sourced credentials or secret-storage mechanisms were detected. Three locally generated SSL private keys are sensitive files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed SSL private keys

- **Variable(s)**: `key_file`, derived from `node['nginx']['ssl']['private_key_path']` and the site name
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by the `openssl req` command
- **Usage context**: HTTPS private keys for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Files**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions**: Mode `0640`, owner/group `root:ssl-cert`

The certificate subject email `admin@example.com` is certificate metadata, not a password, token, or authentication secret. No data bags, vault items, environment-variable secrets, hardcoded passwords, API keys, or database credentials were detected.

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
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/nginx/sites-enabled/default` must be absent

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH: permitted by UFW; exact port is not specified

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
# Check installed packages
dpkg -l nginx fail2ban ufw openssl ca-certificates

# Check services
systemctl status nginx
systemctl status fail2ban
systemctl status ssh

# Validate Nginx configuration
nginx -t

# Check listening ports
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'

# Check firewall status and rules
ufw status verbose
ufw status numbered
ufw status | grep -E '80|http'
ufw status | grep -E '443|https'
ufw status | grep ssh

# Validate SSH settings
grep -E '^PermitRootLogin' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication' /etc/ssh/sshd_config
# Expected:
# PermitRootLogin no
# PasswordAuthentication no

# Check security configuration
cat /etc/sysctl.d/99-security.conf
cat /etc/fail2ban/jail.local
fail2ban-client status

# Test test.cluster.local
ls -ld /opt/server/test
ls -l /opt/server/test/index.html
ls -l /etc/nginx/sites-available/test.cluster.local
ls -l /etc/nginx/sites-enabled/test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G %n' /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/

# Test ci.cluster.local
ls -ld /opt/server/ci
ls -l /opt/server/ci/index.html
ls -l /etc/nginx/sites-available/ci.cluster.local
ls -l /etc/nginx/sites-enabled/ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G %n' /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/

# Test status.cluster.local
ls -ld /opt/server/status
ls -l /opt/server/status/index.html
ls -l /etc/nginx/sites-available/status.cluster.local
ls -l /etc/nginx/sites-enabled/status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -issuer -dates
stat -c '%a %U:%G %n' /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/

# Expected private-key permissions and ownership
# 640 root:ssl-cert

# Verify default site removal
test ! -e /etc/nginx/sites-enabled/default

# Verify certificate subjects
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject

# Expected common names:
# CN=test.cluster.local
# CN=ci.cluster.local
# CN=status.cluster.local

# Review service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u ssh --no-pager -n 100
```