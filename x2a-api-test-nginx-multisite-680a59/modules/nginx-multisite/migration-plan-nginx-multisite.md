---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx and Fail2ban, configures UFW and kernel security settings, disables root SSH login and SSH password authentication, generates self-signed certificates, deploys per-site Nginx configurations and document roots, enables the sites, and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS Nginx virtual site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTPS TCP port `443`; HTTP behavior must be confirmed from the rendered site template
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **ci.cluster.local**: HTTPS Nginx virtual site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTPS TCP port `443`; HTTP behavior must be confirmed from the rendered site template
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **status.cluster.local**: HTTPS Nginx virtual site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTPS TCP port `443`; HTTP behavior must be confirmed from the rendered site template
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

- **fail2ban**: Intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: None
  - Key Config: Package installed; service enabled and started

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: SSH, HTTP TCP port `80`, and HTTPS TCP port `443` allowed
  - Key Config: Default incoming policy denied; firewall enabled non-interactively

- **ssh**: SSH service hardening
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: Configured SSH service port
  - Key Config: `PermitRootLogin no`; `PasswordAuthentication no`; service resource has action `nothing`

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

**Recipes:**
- `cookbooks/nginx-multisite/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/security.rb`
- `cookbooks/nginx-multisite/recipes/nginx.rb`
- `cookbooks/nginx-multisite/recipes/ssl.rb`
- `cookbooks/nginx-multisite/recipes/sites.rb`

**Providers:** None. No provider files or custom resources are used.

**Templates:**
- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`

**Attributes:**
- `cookbooks/nginx-multisite/attributes/default.rb`

**Files:** No static files under `files/default/*` or `files/*` are listed. The per-site `index.html` files are `cookbook_file` resources whose source paths are dynamically constructed from the site folder.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role must preserve this execution order.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Sets the UFW default incoming policy to deny.
   - Allows SSH, HTTP, and HTTPS before enabling UFW.
   - Enables UFW non-interactively.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Defines `execute[reload_sysctl]` with command `sysctl -p /etc/sysctl.d/99-security.conf` and action `nothing`.
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` when `security.ssh.disable_root` is `true`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config` when `security.ssh.password_auth` is `false`.
   - Defines `service[ssh]` with action `nothing`; no explicit SSH restart or reload is shown.
   - Contains 8 `execute` resources:
     - `ufw_default_deny`
     - `ufw_allow_ssh`
     - `ufw_allow_http`
     - `ufw_allow_https`
     - `ufw_enable`
     - `reload_sysctl`
     - `disable root login`
     - `disable password auth`
   - Template modes and other file metadata should be verified against the source recipe before migration; the supplied execution tree does not independently confirm them.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Iterates over `nginx.sites` with these exact entries:
     - `test.cluster.local`: creates `/opt/server/test` and deploys `/opt/server/test/index.html`.
     - `ci.cluster.local`: creates `/opt/server/ci` and deploys `/opt/server/ci/index.html`.
     - `status.cluster.local`: creates `/opt/server/status` and deploys `/opt/server/status/index.html`.
   - Each index file uses the dynamically constructed cookbook-file source `#{site_folder}/index.html`.
   - Template modes and other file metadata should be verified against the source recipe before migration.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates the certificate directory `/etc/ssl/certs`.
   - Creates the private-key directory `/etc/ssl/private`.
   - Iterates over exactly three SSL-enabled sites:
     - `test.cluster.local`: generates `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`.
     - `ci.cluster.local`: generates `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`.
     - `status.cluster.local`: generates `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`.
   - Certificate generation uses RSA 2048-bit keys, self-signed certificates, 365-day validity, no private-key passphrase, and the subject organization values specified by the recipe.
   - The supplied recipe commands apply private-key mode `0640` and ownership `root:ssl-cert`; these settings must be verified against the source recipe during migration because the execution-tree analysis does not independently confirm all file metadata.
   - The certificate-generation conditional guard is evaluated three times and does not skip any site.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterates over `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
     - `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`, using `/opt/server/test`, `/etc/ssl/certs/test.cluster.local.crt`, and `/etc/ssl/private/test.cluster.local.key`.
     - `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`, using `/opt/server/ci`, `/etc/ssl/certs/ci.cluster.local.crt`, and `/etc/ssl/private/ci.cluster.local.key`.
     - `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`, using `/opt/server/status`, `/etc/ssl/certs/status.cluster.local.crt`, and `/etc/ssl/private/status.cluster.local.key`.
   - Creates enabled-site links:
     - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
     - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
     - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
   - Deletes `/etc/nginx/sites-enabled/default`.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

**System package dependencies**:
- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:
- `nginx`: enabled and started
- `fail2ban`: enabled and started
- `ssh`: resource declared with action `nothing`; no explicit restart or start is shown

**Firewall dependencies**:
- SSH application profile
- HTTP/TCP port `80`
- HTTPS/TCP port `443`

## Credentials

**Detection Summary**: No externally supplied application credentials, passwords, API tokens, data bags, vault references, or secret-manager integrations were identified in the supplied analysis. The TLS private keys and certificates are generated locally by the cookbook. The absence of hardcoded credentials in the attributes file should be confirmed with a source-file credential scan.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### TLS Private Keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated files
- **Usage context**: TLS private keys for the three Nginx virtual sites
- **Generation**: RSA 2048-bit keys without passphrases; the recipe commands specify mode `0640` and owner/group `root:ssl-cert`, subject to source verification

### TLS Certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: TLS certificates referenced by the Nginx site configurations
- **Validity**: 365 days
- **Subject email**: `admin@example.com`

No provider, URL, external secret path, or secret-manager integration was detected.

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
- `/etc/nginx/sites-enabled/default` must be absent
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`

**Service endpoints to check**:
- `test.cluster.local`: HTTPS TCP port `443`
- `ci.cluster.local`: HTTPS TCP port `443`
- `status.cluster.local`: HTTPS TCP port `443`
- HTTP TCP port `80`
- Configured SSH service port

The exact HTTP and HTTPS listener behavior must be confirmed from the rendered `site.conf.erb` output.

**Templates rendered**:
- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks:

```bash
# Verify services
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

# Validate configurations
nginx -t
sshd -t
fail2ban-client -t

# Verify UFW policy and rules
ufw status verbose
ufw status | grep -E 'ssh|22'
ufw status | grep -E 'http|80'
ufw status | grep -E 'https|443'

# Verify SSH hardening
grep -E '^[[:space:]]*PermitRootLogin[[:space:]]+no' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication[[:space:]]+no' /etc/ssh/sshd_config

# Verify Fail2ban
test -f /etc/fail2ban/jail.local
fail2ban-client ping
fail2ban-client status

# Verify Nginx listeners
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Verify base configuration
test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test ! -e /etc/nginx/sites-enabled/default

# Verify kernel security configuration
test -f /etc/sysctl.d/99-security.conf
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
```

### Site: `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
```

Expected result: an HTTP response from the `test.cluster.local` virtual host, normally `200 OK` or the configured Nginx response.

### Site: `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
```

Expected result: an HTTP response from the `ci.cluster.local` virtual host, normally `200 OK` or the configured Nginx response.

### Site: `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
```

Expected result: an HTTP response from the `status.cluster.local` virtual host, normally `200 OK` or the configured Nginx response.

### Logs

```bash
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u ssh --no-pager -n 100
```

Any Nginx reload handler should run `nginx -t` before reloading the service.