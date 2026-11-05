---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies nginx, SSH, firewall, and kernel security settings; generates self-signed certificates; creates site document roots and index files; configures HTTP-to-HTTPS redirects; and enables the three virtual hosts. The cookbook targets Ubuntu `>= 18.04` and CentOS `>= 7.0`. The three dynamic cookbook files must be located or supplied before migration.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The `node['nginx']['sites']` collection contains exactly three sites. All sites have SSL enabled.

- **test.cluster.local**: Test web site
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Logs:
    - `/var/log/nginx/test.cluster.local_access.log`
    - `/var/log/nginx/test.cluster.local_error.log`
  - SSL enabled: `true`

- **ci.cluster.local**: Continuous-integration web site
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Logs:
    - `/var/log/nginx/ci.cluster.local_access.log`
    - `/var/log/nginx/ci.cluster.local_error.log`
  - SSL enabled: `true`

- **status.cluster.local**: Status web site
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Logs:
    - `/var/log/nginx/status.cluster.local_access.log`
    - `/var/log/nginx/status.cluster.local_error.log`
  - SSL enabled: `true`

Security configuration:

- fail2ban: enabled
- UFW: enabled with default incoming policy `deny`
- SSH root login: disabled
- SSH password authentication: disabled

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

No provider files are shown in the execution tree. The supplied structural analysis mentions `resources/lineinfile.rb`, but it is not used by any resource in the execution tree and is excluded.

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

No static files are listed in the supplied cookbook directory listing. The recipes use three dynamic `cookbook_file` resources whose source files are not present in the supplied file list:

```text
test/index.html
ci/index.html
status/index.html
```

These files must be identified or supplied before completing the Ansible migration.

## Module Explanation

The cookbook performs operations in this order:

1. `security`
2. `nginx`
3. `ssl`
4. `sites`

### 1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)

The entry recipe includes the operational recipes in this order:

1. `nginx-multisite::security`
2. `nginx-multisite::nginx`
3. `nginx-multisite::ssl`
4. `nginx-multisite::sites`

Ansible must preserve this dependency order: security configuration, nginx installation and configuration, certificate generation, then virtual-host deployment.

- Resource: `include_recipe` (4)

### 2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs packages:
  - `fail2ban`
  - `ufw`
- Enables and starts `fail2ban`.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` once to `/etc/fail2ban/jail.local` with mode `0644`.
- Restarts fail2ban after changes to `/etc/fail2ban/jail.local`.
- Configures UFW:
  - Default incoming policy: deny
  - Allows SSH on `22/tcp`
  - Allows HTTP on `80/tcp`
  - Allows HTTPS on `443/tcp`
  - Enables UFW
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` once to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Reloads the sysctl configuration after changes.
- Disables SSH root login in `/etc/ssh/sshd_config`.
- Disables SSH password authentication in `/etc/ssh/sshd_config`.
- Restarts SSH only when the SSH hardening configuration changes.

The fail2ban configuration includes SSH protection and nginx protections for HTTP authentication failures, request limits, and bot searches. The documented settings are ban time `3600`, find time `600`, and maximum retries `3`, with log paths under `/var/log/auth.log` and `/var/log/nginx/`.

The documented kernel security settings include reverse-path filtering, redirect and source-route protection, martian packet logging, ICMP protections, IPv6 disabling, TCP SYN cookies, and TCP backlog and retry settings.

Use `community.general.ufw`, `ansible.posix.sysctl`, and templated SSH configuration in Ansible.

- Resources:
  - `package`: 1 resource containing `fail2ban` and `ufw`
  - `service`: 2 (`fail2ban`, `ssh`)
  - `template`: 2
  - `execute`: 8
    - `ufw_default_deny`
    - `ufw_allow_ssh`
    - `ufw_allow_http`
    - `ufw_allow_https`
    - `ufw_enable`
    - `reload_sysctl`
    - Disable root login
    - Disable password authentication

### 3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs package `nginx`.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` once to `/etc/nginx/nginx.conf` with mode `0644`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` once to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Enables and starts the `nginx` service.
- Reloads nginx after changes to the main configuration, security configuration, document sites, certificates, virtual-host templates, or virtual-host links.
- Creates the three document roots and deploys one index file for each site.

The documented nginx configuration includes worker user `www-data`, automatic worker processes, PID file `/run/nginx.pid`, worker connections `768`, standard send and TCP settings, keepalive timeout `65`, gzip, and includes for modules, `conf.d`, and `sites-enabled`.

The documented nginx security configuration includes `server_tokens off`, login and API rate-limit zones, a `1k` maximum client body size, short client and send timeouts, TLS 1.2 and TLS 1.3, a shared TLS session cache, a `10m` TLS session timeout, explicit ECDHE/DHE ciphers, and preferred server ciphers.

Site iterations:

- **test.cluster.local**
  - Creates `/opt/server/test`
  - Owner/group: `www-data:www-data`
  - Mode: `0755`
  - Deploys source `test/index.html` to `/opt/server/test/index.html`
  - Index owner/group: `www-data:www-data`
  - Index mode: `0644`

- **ci.cluster.local**
  - Creates `/opt/server/ci`
  - Owner/group: `www-data:www-data`
  - Mode: `0755`
  - Deploys source `ci/index.html` to `/opt/server/ci/index.html`
  - Index owner/group: `www-data:www-data`
  - Index mode: `0644`

- **status.cluster.local**
  - Creates `/opt/server/status`
  - Owner/group: `www-data:www-data`
  - Mode: `0755`
  - Deploys source `status/index.html` to `/opt/server/status/index.html`
  - Index owner/group: `www-data:www-data`
  - Index mode: `0644`

- Resources:
  - `package`: 1
  - `template`: 2
  - `service`: 1
  - `directory`: 3
  - `cookbook_file`: 3

### 4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs packages:
  - `openssl`
  - `ca-certificates`
- Creates group `ssl-cert`.
- Creates `/etc/ssl/certs` with owner `root:root` and mode `0755`.
- Creates `/etc/ssl/private` with owner `root:ssl-cert` and mode `0710`.
- Generates one self-signed certificate and private key for each SSL-enabled site.
- Skips certificate generation when both the certificate and key already exist.
- Reloads nginx after certificate generation.

Certificate iterations:

- **test.cluster.local**
  - Execution resource: `generate-ssl-cert-test.cluster.local`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - RSA key size: `2048`
  - Validity: `365` days
  - Unencrypted private key
  - Subject: `/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=test.cluster.local/emailAddress=admin@example.com`
  - Key owner/group: `root:ssl-cert`
  - Key mode: `0640`

- **ci.cluster.local**
  - Execution resource: `generate-ssl-cert-ci.cluster.local`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - RSA key size: `2048`
  - Validity: `365` days
  - Unencrypted private key
  - Common Name: `ci.cluster.local`
  - Email address: `admin@example.com`
  - Key owner/group: `root:ssl-cert`
  - Key mode: `0640`

- **status.cluster.local**
  - Execution resource: `generate-ssl-cert-status.cluster.local`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - RSA key size: `2048`
  - Validity: `365` days
  - Unencrypted private key
  - Common Name: `status.cluster.local`
  - Email address: `admin@example.com`
  - Key owner/group: `root:ssl-cert`
  - Key mode: `0640`

No provider path is supplied for the custom execution resources. Implement them with guarded `ansible.builtin.command` or `ansible.builtin.shell` tasks, or an appropriate certificate-generation module, while preserving filenames, subjects, permissions, and ownership.

- Resources:
  - `package`: 1 resource containing `openssl` and `ca-certificates`
  - `group`: 1
  - `directory`: 2
  - Custom execution resources: 3

### 5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

The site collection executes exactly three times using `cookbooks/nginx-multisite/templates/default/site.conf.erb`.

- **test.cluster.local**
  - Renders to `/etc/nginx/sites-available/test.cluster.local`
  - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to the available-site file
  - `server_name`: `test.cluster.local`
  - `document_root`: `/opt/server/test`
  - `ssl_enabled`: `true`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Key: `/etc/ssl/private/test.cluster.local.key`

- **ci.cluster.local**
  - Renders to `/etc/nginx/sites-available/ci.cluster.local`
  - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to the available-site file
  - `server_name`: `ci.cluster.local`
  - `document_root`: `/opt/server/ci`
  - `ssl_enabled`: `true`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Key: `/etc/ssl/private/ci.cluster.local.key`

- **status.cluster.local**
  - Renders to `/etc/nginx/sites-available/status.cluster.local`
  - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to the available-site file
  - `server_name`: `status.cluster.local`
  - `document_root`: `/opt/server/status`
  - `ssl_enabled`: `true`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Key: `/etc/ssl/private/status.cluster.local.key`

Deletes `/etc/nginx/sites-enabled/default`.

Each site configuration includes:

- HTTP listener on port `80`
- HTTP-to-HTTPS redirect
- HTTPS listener on port `443`
- HTTP/2
- TLS 1.2 and TLS 1.3
- HSTS with `max-age=31536000` and `includeSubDomains`
- Site-specific document root and certificate paths
- Security headers
- Gzip compression
- `try_files $uri $uri/ =404`
- Blocking of `.htaccess`, `.git`, and `.svn`
- Per-site access and error logs

- Resources:
  - `template`: 3
  - `link`: 3
  - `file`: 1

## Dependencies

**External cookbook dependencies**: None shown in `metadata.rb`.

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

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: restarted only when SSH hardening changes
- UFW: enabled with default deny, allowing TCP ports `22`, `80`, and `443`

**Runtime network ports**:

- TCP `22`: SSH
- TCP `80`: nginx HTTP
- TCP `443`: nginx HTTPS

## Credentials

**Detection Summary**: No external credentials or secret-management integrations detected. Three locally generated TLS key materials are used across six files.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-Signed TLS Material

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/certs/status.cluster.local.crt`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated certificate and key files; not stored in a data bag, vault, environment variable, or external secret manager
- **Usage context**: nginx TLS certificates and private keys
- **Security details**: Private keys are unencrypted, mode `0640`, and owned by `root:ssl-cert`

The certificate subject contains the literal email address `admin@example.com`; this is not an authentication credential.

No data bags, Chef Vault items, CyberArk, Conjur, Vault attributes, database credentials, API keys, passwords, or secret environment variables were detected.

## Checks for the Migration

**Files to verify**:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
/etc/nginx/sites-enabled/test.cluster.local
/etc/nginx/sites-enabled/ci.cluster.local
/etc/nginx/sites-enabled/status.cluster.local
/etc/nginx/sites-enabled/default
/opt/server/test
/opt/server/test/index.html
/opt/server/ci
/opt/server/ci/index.html
/opt/server/status
/opt/server/status/index.html
/etc/ssl/certs/test.cluster.local.crt
/etc/ssl/private/test.cluster.local.key
/etc/ssl/certs/ci.cluster.local.crt
/etc/ssl/private/ci.cluster.local.key
/etc/ssl/certs/status.cluster.local.crt
/etc/ssl/private/status.cluster.local.key
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/ssh/sshd_config
```

The default site must be absent. The three dynamic source files must be supplied or otherwise identified before migration.

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: TCP `22`
- nginx PID file: `/run/nginx.pid`

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `sysctl-security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks:

```bash
# Service status
systemctl is-enabled --quiet nginx && systemctl is-active --quiet nginx
systemctl is-enabled --quiet fail2ban && systemctl is-active --quiet fail2ban
systemctl is-active --quiet ssh
ufw status verbose

# Package verification
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
  rpm -q nginx fail2ban ufw openssl ca-certificates

# nginx configuration
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
ss -tlnp | grep -E ':(22|80|443)\b'

# test.cluster.local
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key

# ci.cluster.local
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key

# status.cluster.local
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key

# Virtual-host links
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local
test ! -e /etc/nginx/sites-enabled/default

# Document roots and permissions
stat -c '%U:%G %a %n' /opt/server/test /opt/server/test/index.html
stat -c '%U:%G %a %n' /opt/server/ci /opt/server/ci/index.html
stat -c '%U:%G %a %n' /opt/server/status /opt/server/status/index.html

# Firewall
ufw status numbered
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

# fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
grep -E 'bantime|findtime|maxretry|logpath|port' /etc/fail2ban/jail.local

# SSH hardening
grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config

# Kernel security
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog

# Logs
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log
journalctl -u nginx --since "10 minutes ago"
journalctl -u fail2ban --since "10 minutes ago"
journalctl -u ssh --since "10 minutes ago"
tail -n 50 /var/log/auth.log
```

Expected results:

- nginx and fail2ban are enabled and active.
- SSH is active.
- UFW is active with default incoming policy `deny`.
- TCP ports `22`, `80`, and `443` are allowed and listening.
- Each HTTP virtual host returns a `301` redirect to its HTTPS URL.
- Each HTTPS virtual host returns HTTP `200` and serves its corresponding index file.
- Each private key is owned by `root:ssl-cert` with mode `640`.
- Document roots are owned by `www-data:www-data` with mode `755`.
- Index files are owned by `www-data:www-data` with mode `644`.
- The three enabled-site links resolve to their corresponding files in `sites-available`.
- `/etc/nginx/sites-enabled/default` does not exist.
- SSH configuration contains:
  - `PermitRootLogin no`
  - `PasswordAuthentication no`
- The fail2ban jails `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch` are enabled.
- Sysctl values include:
  - `net.ipv4.conf.default.rp_filter = 1`
  - `net.ipv4.conf.all.rp_filter = 1`
  - `net.ipv4.conf.all.accept_redirects = 0`
  - `net.ipv6.conf.all.disable_ipv6 = 1`
  - `net.ipv4.tcp_syncookies = 1`
  - `net.ipv4.tcp_max_syn_backlog = 2048`

The Ansible implementation must preserve notification behavior: nginx reloads after changed nginx configuration, certificate generation, site templates, or site links; fail2ban restarts after `jail.local` changes; SSH restarts after SSH hardening changes; and sysctl values reload after `/etc/sysctl.d/99-security.conf` changes.