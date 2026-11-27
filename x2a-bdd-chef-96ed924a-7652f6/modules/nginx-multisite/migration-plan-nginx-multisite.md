---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with host security, fail2ban, UFW, SSH hardening, kernel network hardening, optional SSL certificates, and data-bag-defined virtual hosts. The entry recipe executes `security`, `nginx`, `ssl`, and `sites` in that order. The supplied analysis does not include the names or complete attributes of the `nginx_sites` data-bag items, so the runtime site inventory must be obtained before migration. The SSL-generation condition and certificate reload notification also require verification against the original Chef source because the validation notes identify contradictions in the analyzed execution tree.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**: Main web server and virtual-host service
  - Location/Path: `/etc/nginx/nginx.conf`, `/etc/nginx/sites-available`, `/etc/nginx/sites-enabled`
  - Port/Socket: TCP `80`; TCP `443` when SSL-enabled site configuration is active
  - Key Config: User `nginx`, worker processes `auto`, worker connections `768`, gzip enabled, and includes for `/etc/nginx/conf.d/*.conf` and `/etc/nginx/sites-enabled/*`
  - Service state: Enabled and started

- **fail2ban**: Intrusion prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: Monitors SSH and nginx logs; SSH port `22`, HTTP port `80`, HTTPS port `443`
  - Key Config: Service enabled and started; jails include `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch`

- **ufw**: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, TCP `80`, and TCP `443`
  - Key Config: Incoming traffic denied by default; firewall enabled

- **sshd**: SSH service
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config: `PermitRootLogin no` when `security.ssh.disable_root` is true; `PasswordAuthentication no` when `security.ssh.password_auth` is false; restart occurs only after a changed SSH configuration

- **nginx site inventory**: Runtime virtual-host instances loaded from the `nginx_sites` data bag
  - Location/Path: `/etc/nginx/sites-available/<site_name>`, `/etc/nginx/sites-enabled/<site_name>`, and each site’s `document_root`
  - Port/Socket: TCP `80`; TCP `443` for sites whose verified `ssl_enabled` value requires HTTPS
  - Key Config: Each item must provide `id`, `document_root`, and `ssl_enabled`
  - Exact instance names: Not present in the supplied analysis; obtain and enumerate the complete data-bag inventory before implementation

Expected runtime site variables:

```yaml
nginx_sites:
  # Populate from the Chef nginx_sites data bag.
  # Required fields:
  # - id
  # - document_root
  # - ssl_enabled
```

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

No provider files are used by the execution tree.

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

The execution tree references dynamic `cookbook_file` resources for runtime site `index.html` files, but no static source paths were provided.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the dependency order: host security, nginx, SSL material, then virtual-host configuration.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs packages `fail2ban` and `ufw`.
   - Enables and starts the **fail2ban** service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures the named fail2ban jails:
     - `sshd`
     - `nginx-http-auth`
     - `nginx-limit-req`
     - `nginx-botsearch`
   - Applies UFW rules:
     - Default incoming policy: deny
     - TCP `22`: allowed
     - TCP `80`: allowed
     - TCP `443`: allowed
     - Firewall: enabled
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Reloads `/etc/sysctl.d/99-security.conf` with `sysctl -p` when the sysctl file changes.
   - Applies SSH hardening conditionally:
     - `PermitRootLogin no` when `node['security']['ssh']['disable_root']` is true.
     - `PasswordAuthentication no` when `node['security']['ssh']['password_auth'] == false`.
   - Restarts `sshd` only after a changed SSH configuration.
   - Default attribute values enable both SSH hardening settings.
   - Security iteration items are explicitly `fail2ban`, `ufw`, and `ssh`.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the **nginx** service.
   - Reloads nginx after changed nginx configuration files, subject to verification of the original notification behavior.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Loads the encrypted Chef data-bag item `nginx_secrets/site`.
   - Writes its `token` field to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, mode `0600`, and sensitive handling.
   - Reads runtime site items from the `nginx_sites` data bag.
   - The supplied analysis does not provide the exact runtime site names, so no dynamic site resources can be expanded by name.
   - For every named site supplied during migration, the verified task list must create:
     - The site document root with owner `nginx`, group `nginx`, mode `0755`.
     - `<document_root>/index.html` with owner `nginx`, group `nginx`, mode `0644`.
     - The static source path derived from the portion of the site name before the first dot: `<site_folder>/index.html`.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, mode `0710`.
   - Reads the `nginx_sites` data bag and evaluates each site’s `ssl_enabled` value.
   - The validation notes identify a contradiction between the analyzed condition and the plan’s statement that certificates are generated when `ssl_enabled` is true. The original Chef condition must be confirmed before implementation; the migration must preserve the verified source condition exactly.
   - For each verified SSL-enabled site, the intended artifact paths are:
     - Certificate: `/etc/ssl/certs/<site_name>.crt`
     - Private key: `/etc/ssl/private/<site_name>.key`
   - Intended certificate properties:
     - Self-signed
     - RSA 2048-bit key
     - Valid for 365 days
     - Subject containing the site name
     - Email address `admin@example.com`
   - Intended private-key properties:
     - Owner `root`
     - Group `ssl-cert`
     - Mode `0640`
   - The source analysis does not conclusively verify whether certificate-generation resources reload nginx after creation; this notification must be confirmed before documenting or implementing it.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, mode `0755`.
   - The directory iteration is explicitly:
     - `/etc/nginx/sites-available`
     - `/etc/nginx/sites-enabled`
   - Reads runtime items from the `nginx_sites` data bag.
   - The supplied analysis does not provide exact site names; obtain the inventory before creating the site task list.
   - For every verified site name, renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
   - The site template receives:
     - `server_name`
     - `document_root`
     - `ssl_enabled`
     - `cert_file`
     - `key_file`
   - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to `/etc/nginx/sites-available/<site_name>`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Site-template behavior, headers, TLS directives, and logging must be verified against the source templates before being treated as confirmed implementation details.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

**Chef version requirement**: Chef `>= 16.0`

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd`

**Firewall dependencies**:

- TCP `22`
- TCP `80`
- TCP `443`

The migration must verify UFW and package availability on CentOS targets because the cookbook installs UFW despite supporting CentOS metadata.

## Credentials

**Detection Summary**: 3 credential categories detected across 2 recipes and 3 output artifact types.

**Source**:
  - **Provider**: Chef encrypted data bag for the nginx site token; local OpenSSL generation for TLS material
  - **URL**: None
  - **Path**: `nginx_secrets/site`; generated TLS paths under `/etc/ssl/certs` and `/etc/ssl/private`

### nginx Site Token

- **Variable(s)**: `site_secret['token']`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Source provider**: Chef encrypted data bag
- **Data bag**: `nginx_secrets`
- **Data-bag item**: `site`
- **Output file**: `/etc/nginx/secrets/site_token`
- **Usage context**: Written as a local nginx secret file; the analyzed recipe does not show it being interpolated into nginx configuration.
- **File protection**: Owner `root`, group `root`, mode `0600`; resource marked sensitive
- **Migration storage**: Ansible Vault or an approved AAP credential/secret integration; do not store plaintext in ordinary inventory.

### TLS Private Keys

- **Variable(s)**: `key_file`; migration variable may be named `nginx_tls_private_key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL
- **Source provider**: Local OpenSSL generation
- **Usage context**: nginx HTTPS private keys
- **Output path**: `/etc/ssl/private/<site_name>.key`
- **Properties**: RSA 2048-bit key; owner `root`; group `ssl-cert`; mode `0640`
- **Migration handling**: Protect generated keys, suppress sensitive command output, and do not expose key contents in logs.

### TLS Certificates

- **Variable(s)**: `cert_file`; migration variable may be named `nginx_tls_certificate`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated self-signed certificate
- **Source provider**: Local OpenSSL generation
- **Usage context**: nginx HTTPS virtual hosts
- **Output path**: `/etc/ssl/certs/<site_name>.crt`
- **Properties**: Self-signed, RSA 2048-bit key, validity of 365 days, subject containing the site name
- **Migration handling**: Confirm the source condition controlling generation before implementation.

No HashiCorp Vault, CyberArk, AWS Secrets Manager, Conjur, environment-variable secret references, database credentials, API tokens, or hardcoded passwords were detected.

## Checks for the Migration

**Files to verify**:

```text
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/nginx/sites-enabled/default
/etc/ssl/certs
/etc/ssl/private
<document_root>/index.html
/etc/nginx/sites-available/<site_name>
/etc/nginx/sites-enabled/<site_name>
/etc/ssl/certs/<site_name>.crt
/etc/ssl/private/<site_name>.key
/var/log/nginx/<site_name>_access.log
/var/log/nginx/<site_name>_error.log
```

Replace `<site_name>` and `<document_root>` with every actual item from the verified `nginx_sites` inventory.

**Service endpoints to check**:

- `sshd`: TCP `22`
- `nginx` HTTP: TCP `80`
- `nginx` HTTPS: TCP `443` when a verified SSL-enabled site requires it

**Unix sockets and IPC**: None configured.

**Templates rendered**:

- `fail2ban.jail.local.erb`: once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: once for each item in the verified `nginx_sites` inventory; exact count is unavailable from the supplied analysis

## Pre-flight checks:

```bash
# Confirm supported operating system and package availability
cat /etc/os-release
command -v nginx
command -v openssl
command -v ufw
command -v fail2ban-client

# Verify the complete runtime site inventory before creating dynamic tasks
# Confirm every item has:
#   - id
#   - document_root
#   - ssl_enabled

# fail2ban instance
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# UFW instance
ufw status verbose
ufw status | grep -E '22/tcp'
ufw status | grep -E '80/tcp'
ufw status | grep -E '443/tcp'

# sshd instance
systemctl status sshd
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config
sshd -t
ss -tlnp | grep -E ':22\b'

# Kernel security configuration
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6
cat /etc/sysctl.d/99-security.conf

# nginx instance
nginx -t
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
ss -tlnp | grep -E ':(80|443)\b'

# nginx configuration
grep -E '^(user|worker_processes|pid)' /etc/nginx/nginx.conf
grep -E 'worker_connections|access_log|error_log|gzip|sites-enabled' /etc/nginx/nginx.conf
grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols' /etc/nginx/conf.d/security.conf

# nginx secret
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token
test -s /etc/nginx/secrets/site_token

# SSL directories
stat -c '%U:%G %a %n' /etc/ssl/certs
stat -c '%U:%G %a %n' /etc/ssl/private
getent group ssl-cert

# Site directories and links; replace placeholders with every verified site
test -f "/etc/nginx/sites-available/<site_name>"
test -L "/etc/nginx/sites-enabled/<site_name>"
readlink -f "/etc/nginx/sites-enabled/<site_name>"
test -f "<document_root>/index.html"
stat -c '%U:%G %a %n' "<document_root>"
stat -c '%U:%G %a %n' "<document_root>/index.html"
test ! -e /etc/nginx/sites-enabled/default

# HTTP checks for every verified HTTP site
curl -I -H "Host: <site_name>" http://127.0.0.1/
curl -s -H "Host: <site_name>" http://127.0.0.1/ | head

# SSL checks for every verified SSL site
test -f "/etc/ssl/certs/<site_name>.crt"
test -f "/etc/ssl/private/<site_name>.key"
openssl x509 -in "/etc/ssl/certs/<site_name>.crt" -noout -subject -dates
stat -c '%U:%G %a %n' "/etc/ssl/private/<site_name>.key"
curl -I -H "Host: <site_name>" http://127.0.0.1/
curl -k -I --resolve "<site_name>:443:127.0.0.1" "https://<site_name>/"

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
journalctl -u fail2ban --no-pager -n 50
journalctl -u nginx --no-pager -n 50
journalctl -u sshd --no-pager -n 50
tail -n 50 "/var/log/nginx/<site_name>_access.log"
tail -n 50 "/var/log/nginx/<site_name>_error.log"
```

Expected baseline results:

- `fail2ban`, `nginx`, and `sshd` are active.
- UFW is active with default incoming policy deny.
- TCP `22`, `80`, and `443` are allowed according to the verified deployment.
- `sshd -t` succeeds.
- `nginx -t` reports `syntax is ok` and `test is successful`.
- `/etc/nginx/secrets/site_token` is owned by `root:root` with mode `600`.
- `/etc/ssl/certs` is `root:root` with mode `755`.
- `/etc/ssl/private` is `root:ssl-cert` with mode `710`.
- Each verified site has the correct configuration file, symlink, document root, and index file.
- `/etc/nginx/sites-enabled/default` does not exist.
- SSL certificate and key checks are performed only according to the verified original `ssl_enabled` condition.
