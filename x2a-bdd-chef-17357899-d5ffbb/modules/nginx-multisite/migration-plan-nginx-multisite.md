---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an Nginx multisite web server with Fail2ban, UFW, SSH and kernel hardening, global Nginx configuration, per-site document roots, optional self-signed TLS certificates, and virtual hosts. The execution order is `security`, `nginx`, `ssl`, and `sites`. Security collection items are named `fail2ban`, `ufw`, and `ssh`. Site names and configuration values are loaded dynamically from the `nginx_sites` data bag, but no actual site item names or values were supplied; those values must be obtained from Chef data before the Ansible inventory and site tasks can be completed. Credential, attribute, template-content, platform, and certificate-guard details require verification against the cookbook source because they are not fully represented in the supplied structured analysis.

## Service Type and Instances

**Service Type**: Web Server

**Supported platforms**: Ubuntu `>= 18.04` and CentOS `>= 7.0` are stated by the original plan but require verification against cookbook metadata.

**Configured Instances**:

- **fail2ban**: Intrusion-prevention service
  - Package: `fail2ban`
  - Configuration: `/etc/fail2ban/jail.local`
  - Service: `fail2ban`
  - Status: Enabled and started
  - Configuration-change action: Delayed service restart

- **ufw**: Host firewall
  - Package: `ufw`
  - Default incoming policy: Deny
  - Allowed services: SSH, HTTP, HTTPS
  - Enable command: `ufw --force enable`

- **ssh**: SSH service hardening
  - Configuration: `/etc/ssh/sshd_config`
  - Required settings:
    - `PermitRootLogin no`
    - `PasswordAuthentication no`
  - Service: `sshd`
  - Configuration-change action: Delayed service restart

- **nginx**: Web server
  - Package: `nginx`
  - Main configuration: `/etc/nginx/nginx.conf`
  - Security configuration: `/etc/nginx/conf.d/security.conf`
  - Service: `nginx`
  - HTTP endpoint: TCP `80`
  - HTTPS endpoint: TCP `443` when SSL-enabled sites are configured

- **nginx_sites data bag sites**: Dynamic virtual-host instances
  - Source: Chef data bag `nginx_sites`
  - Exact item names: Not supplied
  - Required fields for every item:
    - `id`
    - `document_root`
    - `ssl_enabled`
  - Required migration action: Retrieve the actual data bag items and create one explicit Ansible site definition per item.
  - Site-specific instances cannot be named or expanded until the data bag contents are provided.

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
│   └── lineinfile.rb                     # Mentioned by the original plan but not present in the executed recipe tree; verify before migration
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

No provider is used by the supplied execution tree.

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

The `nginx.rb` recipe references dynamic `cookbook_file` sources such as `<site_folder>/index.html`, but no static files are present in the supplied directory listing. These files must be located and migrated separately if they exist in the complete cookbook source.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Ansible execution order must remain security, Nginx, SSL, then virtual hosts.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures the Fail2ban jails shown by the original plan:
     - SSH on `ssh`, using `/var/log/auth.log`.
     - Nginx HTTP authentication on `http,https`.
     - Nginx request limiting on `http,https`.
     - Nginx bot search on `http,https`.
   - Applies UFW rules:
     - Default incoming policy `deny`.
     - Allow SSH on TCP `22`.
     - Allow HTTP on TCP `80`.
     - Allow HTTPS on TCP `443`.
     - Enable the firewall.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Configures reverse-path filtering, redirect protection, source-route disabling, martian logging, ICMP protections, IPv6 disabling, and TCP SYN protections. Exact template values require source verification.
   - Reloads the sysctl configuration with:
     ```bash
     sysctl -p /etc/sysctl.d/99-security.conf
     ```
   - Sets `PermitRootLogin no` in `/etc/ssh/sshd_config`.
   - Sets `PasswordAuthentication no` in `/etc/ssh/sshd_config`.
   - Delays an `sshd` restart when SSH settings change.
   - Uses package, service, template, UFW execute, sysctl execute, and SSH-hardening resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Delays an Nginx reload when the global or security configuration changes.
   - Creates `/etc/nginx/secrets` with owner `root`, group `root`, and mode `0700`.
   - Writes a site token to `/etc/nginx/secrets/site_token` with owner `root`, group `root`, and mode `0600`.
   - The original plan states that the token is loaded from `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`; this encrypted-data-bag call and field require verification against the source.
   - Loads site items from the `nginx_sites` data bag.
   - For every site item whose exact data is obtained:
     - Sets `site_name` to `site['id']`.
     - Creates `config['document_root']` with owner `nginx`, group `nginx`, and mode `0755`.
     - Calculates `site_folder` as the first component of the site name.
     - Deploys `<document_root>/index.html` from `<site_folder>/index.html` with owner `nginx`, group `nginx`, and mode `0644`.
   - The dynamic site list cannot be expanded until actual `nginx_sites` item names and values are supplied.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
   - Loads SSL-enabled items from the `nginx_sites` data bag.
   - For each explicitly identified site with `ssl_enabled: true`, creates:
     - `/etc/ssl/certs/<site_name>.crt`
     - `/etc/ssl/private/<site_name>.key`
   - The original plan specifies self-signed OpenSSL certificates using RSA 2048-bit keys, 365-day validity, and subject CN equal to the site name.
   - The original plan states that generation is skipped when both files already exist. The supplied analysis confirms only the `ssl_enabled` condition; certificate existence guards must be verified in `cookbooks/nginx-multisite/recipes/ssl.rb`.
   - Sets private keys to owner `root`, group `ssl-cert`, and mode `0640`.
   - Delays an Nginx reload when a certificate is created or changed.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
   - Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - Loads site items from the `nginx_sites` data bag.
   - For every explicitly identified site:
     - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>`.
     - Supplies the site name, document root, SSL flag, certificate path, and private-key path.
     - Creates `/etc/nginx/sites-enabled/<site_name>` as a symlink to the available-site configuration.
     - Delays an Nginx reload when the template or link changes.
   - Deletes `/etc/nginx/sites-enabled/default` and delays an Nginx reload if the file is removed.
   - SSL-enabled sites are expected to redirect HTTP to HTTPS and listen on HTTPS with the configured certificate and key.
   - Non-SSL sites are expected to serve HTTP without certificate generation.
   - The exact rendered template behavior and security directives require verification against `site.conf.erb`.
   - No actual site instances can be listed until the `nginx_sites` data bag is inspected.

## Dependencies

**External cookbook dependencies**: None are listed in the supplied metadata; verify against cookbook metadata.

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

**Chef data dependencies**:

- `nginx_sites` data bag:
  - Required fields: `id`, `document_root`, `ssl_enabled`
  - Exact item names: Not supplied
- `nginx_secrets` encrypted data bag:
  - Item: `site`
  - Field: `token`
  - Presence and exact loading code require source verification

## Credentials

**Detection Summary**: One reported encrypted site token and generated TLS private keys were identified in the original plan. The encrypted data-bag loading details require verification against the cookbook source.

**Source**:

- **Provider**: Reported Chef encrypted data bag; source confirmation required
- **Data bag**: `nginx_secrets`
- **Item**: `site`
- **Secret field**: `token`
- **URL**: None detected

### Nginx site token

- **Variable**: Reported as `site_secret['token']`; verify exact variable name
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Reported Chef encrypted data bag
- **Data bag path**: `nginx_secrets/site`
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **File ownership**: `root:root`
- **File mode**: `0600`
- **Ansible storage**: Ansible Vault or an approved external secret manager
- **Handling**: Use `no_log: true` and never expose the token in task output

### TLS private keys

- **Variables**: `key_file`, `node['nginx']['ssl']['private_key_path']`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally by OpenSSL
- **Usage context**: `/etc/ssl/private/<site_name>.key`
- **File ownership**: `root:ssl-cert`
- **File mode**: `0640`
- **Handling**: Treat keys as sensitive and suppress command output

### Site data bag configuration

- **Variables**: `site`, `site_name`, `config['document_root']`, `config['ssl_enabled']`
- **Source files**:
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Chef `nginx_sites` data bag
- **Usage context**: Determines site names, document roots, TLS enablement, and virtual-host variables
- **Sensitive status**: No password or token field is explicitly shown; review values before placing them in source-controlled Ansible variables

No HashiCorp Vault, CyberArk, Conjur, AWS Secrets Manager, environment-variable secret, database connection string, or hardcoded password was detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available/<site_name>` for each retrieved `nginx_sites` item
- `/etc/nginx/sites-enabled/<site_name>` for each retrieved `nginx_sites` item
- `/etc/nginx/sites-enabled/default` must be absent
- `/etc/ssl/certs/<site_name>.crt` for each SSL-enabled retrieved site
- `/etc/ssl/private/<site_name>.key` for each SSL-enabled retrieved site
- `<document_root>/index.html` for each retrieved site

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443`
- Unix sockets: None configured by this cookbook

**Logs to verify**:

- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/<site_name>_access.log`
- `/var/log/nginx/<site_name>_error.log`
- `/var/log/auth.log`

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: once
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: once
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: once
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: once
- `site.conf.erb` → `/etc/nginx/sites-available/<site_name>`: once per retrieved `nginx_sites` item

## Pre-flight checks

```bash
# fail2ban instance
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

# ufw instance
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# ssh instance
systemctl status sshd
systemctl is-active sshd
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config
sshd -t

# Kernel security configuration
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6

# nginx instance
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
nginx -T | grep -E 'server_name|listen 80|listen 443|ssl_certificate|root '

# Network endpoints
ss -tlnp | grep ':22 '
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '

# Secret and TLS permissions
stat -c '%U:%G %a %n' /etc/nginx/secrets/site_token
stat -c '%U:%G %a %n' /etc/ssl/private
# Run once for each retrieved SSL-enabled site:
stat -c '%U:%G %a %n' /etc/ssl/private/<site_name>.key

# Site checks must be generated as explicit blocks after the data bag is retrieved.
# SSL-enabled site:
curl -I -H 'Host: <site_name>' http://127.0.0.1/
curl -k -I --resolve <site_name>:443:127.0.0.1 https://<site_name>/
ls -l /etc/nginx/sites-available/<site_name>
ls -l /etc/nginx/sites-enabled/<site_name>
ls -l /etc/ssl/certs/<site_name>.crt
ls -l /etc/ssl/private/<site_name>.key
ls -l <document_root>/index.html
tail -n 20 /var/log/nginx/<site_name>_access.log
tail -n 20 /var/log/nginx/<site_name>_error.log

# Non-SSL site:
curl -I -H 'Host: <site_name>' http://127.0.0.1/
ls -l /etc/nginx/sites-available/<site_name>
ls -l /etc/nginx/sites-enabled/<site_name>
ls -l <document_root>/index.html
tail -n 20 /var/log/nginx/<site_name>_access.log
tail -n 20 /var/log/nginx/<site_name>_error.log

# Service logs
journalctl -u nginx --since "10 minutes ago"
journalctl -u fail2ban --since "10 minutes ago"
journalctl -u sshd --since "10 minutes ago"
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/auth.log
```

Expected results:

- `fail2ban` is enabled and active.
- UFW is active and allows TCP ports `22`, `80`, and `443`.
- `sshd` is active and reports `PermitRootLogin no` and `PasswordAuthentication no`.
- Kernel security settings are applied.
- `nginx` is enabled and active.
- `nginx -t` succeeds.
- Nginx listens on TCP port `80` and on TCP port `443` when an SSL-enabled site exists.
- Every retrieved site has an available configuration, enabled-site symlink, document-root index file, and site-specific logs.
- SSL-enabled sites have certificates and private keys with the required permissions.
- HTTP redirects to HTTPS for SSL-enabled sites.
- Non-SSL sites serve HTTP directly.
