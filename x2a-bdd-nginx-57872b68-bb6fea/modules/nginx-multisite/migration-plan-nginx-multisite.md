---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server with three SSL-enabled virtual hosts: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies firewall, SSH, sysctl, nginx, and fail2ban security configuration; generates locally signed certificates; creates static document roots and index files; and enables HTTP-to-HTTPS nginx sites on ports 80 and 443. Template contents, attribute defaults, command guards, notifications, and some exact configuration values require verification against the source files because they are not fully represented in the supplied execution analysis.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled nginx virtual host serving static content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; HTTPS uses HTTP/2, TLS certificates, and static-file serving
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`

- **ci.cluster.local**: SSL-enabled nginx virtual host serving static content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; HTTPS uses HTTP/2, TLS certificates, and static-file serving
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`

- **status.cluster.local**: SSL-enabled nginx virtual host serving static content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Key Config: HTTP redirects to HTTPS; HTTPS uses HTTP/2, TLS certificates, and static-file serving
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`

**Security components**:

- **fail2ban**: Enabled; installs and starts the `fail2ban` service and renders `/etc/fail2ban/jail.local`.
- **ufw**: Enabled; installs UFW, denies incoming traffic by default, and allows SSH, HTTP, and HTTPS.
- **ssh**: The analyzed recipe contains conditional resources for disabling root login and password authentication. The cookbook does not independently enable or start `sshd`; it only uses it as a delayed restart target when SSH configuration changes.

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

The recipes invoke `cookbook_file` for three static `index.html` files, but the supplied file inventory does not list their source files. Verify their presence in the source repository before mapping them to Ansible. Do not invent source-file paths.

## Module Explanation

The cookbook performs operations in this order:

1. `default`
2. `security`
3. `nginx`
4. `ssl`
5. `sites`

### 1. Default entry recipe

**Recipe**: `cookbooks/nginx-multisite/recipes/default.rb`

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- Preserves the execution order required by the package, service, certificate, and site configuration dependencies.

**Resources**: `include_recipe` (4)

### 2. Security configuration

**Recipe**: `cookbooks/nginx-multisite/recipes/security.rb`

#### Package installation

Installs:

- `fail2ban`
- `ufw`

**Resources**: `package` (1)

#### fail2ban

- Enables and starts `service[fail2ban]`.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
- The analyzed plan specifies file mode `0644` and a delayed fail2ban restart when the template changes; verify these notification and mode details against the source recipe.
- The plan identifies the following intended jail configuration, which requires direct template verification:
  - Default bantime: `3600`
  - Default findtime: `600`
  - Default maxretry: `3`
  - Backend: `auto`
  - Jails: `sshd`, `nginx-http-auth`, `nginx-limit-req`, and `nginx-botsearch`
  - Log paths including `/var/log/auth.log`, `/var/log/nginx/*error.log`, and `/var/log/nginx/*access.log`

**Resources**: `service` (1), `template` (1)

#### UFW configuration

The recipe analyzes five UFW command resources:

1. `ufw --force default deny`
2. `ufw allow ssh`
3. `ufw allow http`
4. `ufw allow https`
5. `ufw --force enable`

The original plan describes guards that avoid repeating commands when the relevant UFW state or rule already exists. Confirm those guards against the recipe. The Ansible migration should use idempotent UFW modules where available.

**Resources**: `execute` (5)

#### Kernel security settings

- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
- The plan specifies mode `0644`; verify the mode and template contents against the source.
- The intended settings include IPv4 reverse-path filtering, disabled IPv4 and IPv6 redirect acceptance, disabled source routing, martian packet logging, ICMP protections, IPv6 disabling, TCP SYN cookies, and TCP backlog and SYN retry settings.
- The analyzed plan identifies a `reload_sysctl` execute resource with action `nothing`, invoked by a delayed template notification:
  ```bash
  sysctl -p /etc/sysctl.d/99-security.conf
  ```
- Confirm the notification timing and exact sysctl directives against the source.

**Resources**: `template` (1), `execute` (1)

#### SSH hardening

The supplied plan identifies these configured conditions, which must be verified in `cookbooks/nginx-multisite/attributes/default.rb`:

- `node['security']['ssh']['disable_root']` is `true`
- `node['security']['ssh']['password_auth']` is `false`

When enabled, the recipe conditionally applies:

- `PermitRootLogin no` to `/etc/ssh/sshd_config`
- `PasswordAuthentication no` to `/etc/ssh/sshd_config`

The plan identifies two guarded `sed` commands and delayed `sshd` restart notifications. Verify the exact guards, commands, and notification behavior against the source. `service[sshd]` has action `nothing`; this cookbook does not independently start or enable SSH.

**Resources**: `execute` (2 conditional resources), `service` (1)

**Security recipe resource summary**:

- `package`: 1
- `service`: 2
- `template`: 2
- `execute`: 8 total, consisting of 5 UFW commands, 1 sysctl reload command, 1 root-login command, and 1 password-authentication command

### 3. nginx installation and document roots

**Recipe**: `cookbooks/nginx-multisite/recipes/nginx.rb`

#### nginx package and base configuration

- Installs `nginx`.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
- Enables and starts the nginx service.
- The plan identifies delayed nginx reloads for configuration changes; verify notification behavior against the source.

The intended base configuration includes:

- Worker user: `nginx`
- Worker processes: `auto`
- PID file: `/run/nginx.pid`
- Worker connections: `768`
- Access log: `/var/log/nginx/access.log`
- Error log: `/var/log/nginx/error.log`
- Gzip enabled
- Includes `/etc/nginx/conf.d/*.conf`
- Includes `/etc/nginx/sites-enabled/*`

The intended security configuration includes:

- `server_tokens off`
- Rate-limit zones `login` at `10r/m` and `api` at `30r/m`
- Small client buffer limits
- `client_max_body_size 1k`
- Ten-second client and send timeouts
- TLS 1.2 and TLS 1.3
- SSL session cache and timeout
- An explicit ECDHE/DHE cipher list

These directive values require direct verification against the templates.

**Resources**: `package` (1), `template` (2), `service` (1)

#### Site document roots and index files

The site loop contains exactly three iterations:

1. **test.cluster.local**
   - Creates `/opt/server/test`.
   - Intended owner and group: `nginx:nginx`.
   - Intended mode: `0755`.
   - Creates `/opt/server/test/index.html` using a `cookbook_file`.
   - Intended source derivation: `test/index.html`.
   - Intended file owner and group: `nginx:nginx`.
   - Intended file mode: `0644`.

2. **ci.cluster.local**
   - Creates `/opt/server/ci`.
   - Intended owner and group: `nginx:nginx`.
   - Intended mode: `0755`.
   - Creates `/opt/server/ci/index.html` using a `cookbook_file`.
   - Intended source derivation: `ci/index.html`.
   - Intended file owner and group: `nginx:nginx`.
   - Intended file mode: `0644`.

3. **status.cluster.local**
   - Creates `/opt/server/status`.
   - Intended owner and group: `nginx:nginx`.
   - Intended mode: `0755`.
   - Creates `/opt/server/status/index.html` using a `cookbook_file`.
   - Intended source derivation: `status/index.html`.
   - Intended file owner and group: `nginx:nginx`.
   - Intended file mode: `0644`.

The three destination paths are inferred from the recipe loop. The corresponding cookbook source files and their contents are not present in the supplied file inventory and require repository verification.

**Resources inside the site loop**: `directory` (3), `cookbook_file` (3)

### 4. SSL packages, directories, and certificates

**Recipe**: `cookbooks/nginx-multisite/recipes/ssl.rb`

#### SSL packages

Installs:

- `openssl`
- `ca-certificates`

**Resources**: `package` (1)

#### SSL group and directories

- Creates group `ssl-cert`.
- Creates `/etc/ssl/certs` with intended owner `root:root` and mode `0755`.
- Creates `/etc/ssl/private` with intended owner `root:ssl-cert` and mode `0710`.

Verify ownership and modes against the source recipe.

**Resources**: `group` (1), `directory` (2)

#### Self-signed certificate generation

The SSL loop has three configured SSL-enabled iterations:

1. **test.cluster.local**
   - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
   - Key: `/etc/ssl/private/test.cluster.local.key`
   - Intended certificate subject CN: `test.cluster.local`
   - Intended key: RSA, 2048 bits, without a passphrase
   - Intended validity: 365 days
   - Intended subject email: `admin@example.com`
   - Intended key permissions: mode `0640`, owner `root`, group `ssl-cert`

2. **ci.cluster.local**
   - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
   - Key: `/etc/ssl/private/ci.cluster.local.key`
   - Intended certificate subject CN: `ci.cluster.local`
   - Intended key: RSA, 2048 bits, without a passphrase
   - Intended validity: 365 days
   - Intended subject email: `admin@example.com`
   - Intended key permissions: mode `0640`, owner `root`, group `ssl-cert`

3. **status.cluster.local**
   - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
   - Key: `/etc/ssl/private/status.cluster.local.key`
   - Intended certificate subject CN: `status.cluster.local`
   - Intended key: RSA, 2048 bits, without a passphrase
   - Intended validity: 365 days
   - Intended subject email: `admin@example.com`
   - Intended key permissions: mode `0640`, owner `root`, group `ssl-cert`

The plan states that generation is skipped when both certificate and key exist and that newly generated files trigger a delayed nginx reload. Verify the exact OpenSSL commands, guards, permissions, and notifications against the source recipe.

**Resources**: `execute` (3)

### 5. nginx site directories, virtual hosts, and links

**Recipe**: `cookbooks/nginx-multisite/recipes/sites.rb`

#### Site configuration directories

The original plan identifies these two configuration directories:

- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`

Both are intended to have owner `root:root` and mode `0755`. A conflicting structured analysis reportedly identified three site-related directory resources instead. Confirm the actual `directory` resources directly in `cookbooks/nginx-multisite/recipes/sites.rb` before final implementation.

**Resources reported in the original plan**: `directory` (2)

#### Virtual host templates and enabled-site links

The site template loop contains exactly three iterations:

1. **test.cluster.local**
   - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
   - Destination: `/etc/nginx/sites-available/test.cluster.local`
   - Link: `/etc/nginx/sites-enabled/test.cluster.local`
   - Document root: `/opt/server/test`
   - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
   - Private key: `/etc/ssl/private/test.cluster.local.key`
   - Intended mode: `0644`

2. **ci.cluster.local**
   - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
   - Destination: `/etc/nginx/sites-available/ci.cluster.local`
   - Link: `/etc/nginx/sites-enabled/ci.cluster.local`
   - Document root: `/opt/server/ci`
   - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
   - Private key: `/etc/ssl/private/ci.cluster.local.key`
   - Intended mode: `0644`

3. **status.cluster.local**
   - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
   - Destination: `/etc/nginx/sites-available/status.cluster.local`
   - Link: `/etc/nginx/sites-enabled/status.cluster.local`
   - Document root: `/opt/server/status`
   - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
   - Private key: `/etc/ssl/private/status.cluster.local.key`
   - Intended mode: `0644`

The plan identifies the following intended site-template behavior, which requires direct template verification:

- Port 80 listener
- HTTP-to-HTTPS redirect
- Port 443 SSL listener with HTTP/2
- TLS 1.2 and TLS 1.3
- HSTS and security headers
- Gzip compression
- Static-file serving with `try_files`
- Denial of `.htaccess`, `.git`, and `.svn` paths
- Per-site access and error logs

The recipe also deletes `/etc/nginx/sites-enabled/default`. Verify the specified reload notifications and template mode against the source.

**Resources**: `template` (3), `link` (3), `file` (1)

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata or execution data.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `nginx`: Enabled and started by the cookbook; reloaded when applicable nginx configuration, site, link, or certificate resources change.
- `fail2ban`: Enabled and started by the cookbook; restarted when its jail configuration changes.
- `sshd`: Must already be running or managed externally. This cookbook only references it as a delayed restart target for SSH configuration changes.

## Credentials

**Detection Summary**: No credentials or secret resources were detected in the supplied execution analysis. Template and attribute contents were not included, so complete secret detection requires direct source verification.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

No credential resources were identified for data bags, encrypted data bags, Chef Vault, Conjur, CyberArk, Vault attributes, or secret-related environment variables in the supplied analysis. The locally generated SSL private keys are sensitive generated artifacts, but they are not imported credentials. The fixed value `admin@example.com`, if present in the certificate subject, is an identity value rather than an authentication secret.

### Generated SSL Private Keys

- **Variable(s)**: None
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Generated locally on the target host under `/etc/ssl/private`
- **Usage context**: Used by the nginx HTTPS virtual hosts
- **Instances**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`

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
- `/etc/nginx/sites-enabled/default` should be absent
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`

The three static `index.html` destinations are inferred from the recipe loop. Verify that their cookbook source files exist before migration.

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`

**Unix sockets**: None configured by this cookbook.

**Network interfaces**: No specific bind address is configured in the supplied plan; verify that nginx listens on the intended interfaces.

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 render
- `nginx.conf.erb`: 1 render
- `security.conf.erb`: 1 render
- `sysctl-security.conf.erb`: 1 render
- `site.conf.erb`: 3 renders:
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks

### Service status

```bash
systemctl status nginx
systemctl status fail2ban
systemctl status sshd
```

Expected results:

- `nginx` is enabled and active.
- `fail2ban` is enabled and active.
- `sshd` is active if managed externally; this cookbook does not enable or start it.

### Package verification

```bash
dpkg -l nginx fail2ban ufw openssl ca-certificates
```

On RPM-based systems:

```bash
rpm -q nginx fail2ban ufw openssl ca-certificates
```

### nginx configuration validation

```bash
nginx -t
nginx -T | grep -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local'
```

```bash
grep -E 'worker_processes|worker_connections|access_log|error_log|gzip|sites-enabled' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf
```

### Site: `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

curl -k -I --resolve test.cluster.local:80:127.0.0.1 \
  http://test.cluster.local/

curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -dates
```

Verify that HTTP redirects to HTTPS, HTTPS serves the expected static content when the index file exists, the certificate subject contains `CN=test.cluster.local`, and the private key has mode `0640` with group `ssl-cert`.

### Site: `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

curl -k -I --resolve ci.cluster.local:80:127.0.0.1 \
  http://ci.cluster.local/

curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -dates
```

Verify that HTTP redirects to HTTPS, HTTPS serves the expected static content when the index file exists, the certificate subject contains `CN=ci.cluster.local`, and the private key has mode `0640` with group `ssl-cert`.

### Site: `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

curl -k -I --resolve status.cluster.local:80:127.0.0.1 \
  http://status.cluster.local/

curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -dates
```

Verify that HTTP redirects to HTTPS, HTTPS serves the expected static content when the index file exists, the certificate subject contains `CN=status.cluster.local`, and the private key has mode `0640` with group `ssl-cert`.

### Port and listener checks

```bash
ss -tlnp | grep -E ':(80|443)\b'
netstat -tulpn | grep -E ':(80|443)\b'
```

Verify that nginx listens on TCP ports `80` and `443`.

### TLS checks

```bash
openssl s_client -connect 127.0.0.1:443 \
  -servername test.cluster.local </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates

openssl s_client -connect 127.0.0.1:443 \
  -servername ci.cluster.local </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates

openssl s_client -connect 127.0.0.1:443 \
  -servername status.cluster.local </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates
```

Verify the certificate selected for each hostname and confirm that the deployed configuration supports TLS 1.2 or TLS 1.3 and rejects older protocols.

### Firewall checks

```bash
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'
```

Verify that UFW is active, the default incoming policy is deny, and ports `22/tcp`, `80/tcp`, and `443/tcp` are allowed.

### SSH hardening checks

```bash
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config
sshd -t
```

Verify the settings only if the corresponding attributes are enabled in the source cookbook. Confirm that `sshd -t` reports no configuration errors. Ensure SSH remains managed and running externally.

### Kernel security checks

```bash
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
sysctl net.ipv6.conf.all.disable_ipv6
```

Compare the values with the verified contents of `/etc/sysctl.d/99-security.conf`.

### fail2ban checks

```bash
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
```

Verify the jail names and enabled state against the source template before treating these as required checks.

### Logs

```bash
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log
tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log
tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log

journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

No nginx configuration errors should appear after deployment. Verify the per-site log paths against the rendered `site.conf.erb` template.