---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies nginx and host-security settings; conditionally hardens SSH based on security attributes; generates 2048-bit self-signed certificates; creates site document roots and placeholder content; configures HTTP-to-HTTPS redirects; and enables nginx, fail2ban, and UFW.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

The `node['nginx']['sites']` collection contains exactly three sites. The execution tree confirms `ssl_enabled: true` for all three sites.

- **test.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: TCP `80` redirected to TCP `443`
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source `test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: TCP `80` redirected to TCP `443`
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source `ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: SSL-enabled nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: TCP `80` redirected to TCP `443`
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source `status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

### Security Attribute Groups

The supplied analysis confirms the presence of the `fail2ban`, `ufw`, and `ssh` attribute groups. The following values are reported by the cookbook plan but require verification against the attributes analysis:

- **fail2ban**
  - `enabled: true`
- **ufw**
  - `enabled: true`
- **ssh**
  - `disable_root: true`
  - `password_auth: false`

Package installation, fail2ban, UFW, and sysctl configuration execute unconditionally in the current recipe flow. SSH hardening is conditional:

- Root-login hardening runs when `node['security']['ssh']['disable_root']` is true.
- Password-authentication hardening runs when `node['security']['ssh']['password_auth'] == false`.

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

No provider files are used by the execution tree. The structural analysis mentions `resources/lineinfile.rb`, but it is not executed or referenced by the supplied recipe tree and is not included in the migration.

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

No static files are listed in the supplied cookbook directory listing. The nginx recipe references these three cookbook-file sources, which the Ansible role must provide or source:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - Preserves the sequence: host security, nginx installation, SSL generation, and virtual-host deployment.

2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts `fail2ban`.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Configures fail2ban defaults: ban time `3600`, find time `600`, retry count `3`, and backend `auto`.
   - Enables the SSH jail on `/var/log/auth.log`.
   - Enables nginx HTTP authentication and request-limit jails on `/var/log/nginx/*error.log`.
   - Enables the nginx bot-search jail on `/var/log/nginx/*access.log`.
   - Configures UFW with default deny, allows SSH on TCP `22`, HTTP on TCP `80`, HTTPS on TCP `443`, and enables the firewall.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Applies reverse-path filtering, redirect and source-route restrictions, martian logging, ICMP and broadcast restrictions, IPv6 disabling, SYN-cookie protection, and TCP backlog/retry settings.
   - Runs `sysctl -p /etc/sysctl.d/99-security.conf` as a delayed action.
   - Conditionally changes `PermitRootLogin` to `no` when `node['security']['ssh']['disable_root']` is true.
   - Conditionally changes `PasswordAuthentication` to `no` when `node['security']['ssh']['password_auth'] == false`.
   - Restarts `sshd` only when either conditional SSH configuration command changes the file.
   - Resources: `package` (1), `service[fail2ban]` (1), `template` (2), `execute` (8), and `service[sshd]` (1).
   - The eight execute resources are five UFW commands, one sysctl reload, one root-login hardening command, and one password-authentication hardening command.

3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Configures worker user `nginx`, automatic worker processes, PID `/run/nginx.pid`, `768` worker connections, standard access and error logs, gzip, `/etc/nginx/conf.d/*.conf`, and `/etc/nginx/sites-enabled/*`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Configures hidden nginx version headers, `login` and `api` rate-limit zones, a `1k` maximum request body, buffer restrictions, ten-second client and send timeouts, TLS 1.2 and TLS 1.3, a shared SSL session cache, a ten-minute SSL session timeout, ECDHE/DHE ciphers, and preferred server ciphers.
   - Enables and starts nginx.
   - Creates the following document roots with owner `nginx`, group `nginx`, mode `0755`, and recursive creation:
     - `test.cluster.local`: `/opt/server/test`; deploys `test/index.html` to `/opt/server/test/index.html` with owner `nginx`, group `nginx`, mode `0644`.
     - `ci.cluster.local`: `/opt/server/ci`; deploys `ci/index.html` to `/opt/server/ci/index.html` with owner `nginx`, group `nginx`, mode `0644`.
     - `status.cluster.local`: `/opt/server/status`; deploys `status/index.html` to `/opt/server/status/index.html` with owner `nginx`, group `nginx`, mode `0644`.
   - Resources: `package` (1), `template` (2), `service` (1), `directory` (3), and `cookbook_file` (3).

4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with owner `root`, group `root`, mode `0755`.
   - Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, mode `0710`.
   - Generates certificates for the following three enabled sites:
     - `test.cluster.local`: `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`.
     - `ci.cluster.local`: `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`.
     - `status.cluster.local`: `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`.
   - Generates 2048-bit RSA self-signed certificates valid for `365` days with subject country `US`, state `Example`, locality `Example`, organization `Example Org`, organizational unit `IT`, the site-specific common name, and email `admin@example.com`.
   - Skips certificate generation when both the certificate and key already exist.
   - Sets private keys to mode `0640`, owner `root`, and group `ssl-cert`.
   - Sends a delayed nginx reload notification after generating a certificate.
   - Resources: `package` (1), `group` (1), `directory` (2), and `execute` (3).

5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
   - The validated execution tree reports three directory resources in the site loop, one associated with each named site. The exact per-site directory paths are not present in the supplied structured analysis and must be verified during implementation; the two nginx configuration directories above remain required.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for:
     - `test.cluster.local`: `/etc/nginx/sites-available/test.cluster.local`, linked to `/etc/nginx/sites-enabled/test.cluster.local`, root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
     - `ci.cluster.local`: `/etc/nginx/sites-available/ci.cluster.local`, linked to `/etc/nginx/sites-enabled/ci.cluster.local`, root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
     - `status.cluster.local`: `/etc/nginx/sites-available/status.cluster.local`, linked to `/etc/nginx/sites-enabled/status.cluster.local`, root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Configures HTTP port `80` redirects to `https://$server_name$request_uri`.
   - Configures HTTPS port `443` with HTTP/2, site-specific document roots, index files `index.html`, `index.htm`, and `index.php`, TLS 1.2 and TLS 1.3, one-year HSTS with subdomain inclusion, security headers, gzip, `try_files`, `.htaccess` denial, `.git` and `.svn` denial, and site-specific access and error logs.
   - Creates the three site-enabled symlinks.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Sends delayed nginx reload notifications for template, symlink, and default-site deletion changes.
   - Resources: `directory` (3, including the validated three-resource site loop), `template` (3), `link` (3), and `file` (1).

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**Supported platforms**: Ubuntu `>= 18.04`; CentOS `>= 7.0`.

**System package dependencies**: `fail2ban`, `ufw`, `nginx`, `openssl`, `ca-certificates`.

**Service dependencies**: `fail2ban` enabled and started; nginx enabled and started; `sshd` restarted when conditional SSH hardening changes configuration; UFW enabled through `ufw --force enable`.

**Network ports**: TCP `22` for SSH; TCP `80` for HTTP; TCP `443` for HTTPS.

## Credentials

**Detection Summary**: No passwords, API tokens, data bags, encrypted data bags, Chef Vault items, CyberArk references, Conjur variables, or environment-variable secrets were detected. Three locally generated TLS private keys and three locally generated TLS certificates are sensitive cryptographic files but are not retrieved from a secret-management provider.

**Source**:
  - **Provider**: None detected
  - **URL**: None
  - **Path**: None

### Self-signed TLS private keys

- **Variable(s)**: `key_file`; `/etc/ssl/private/test.cluster.local.key`; `/etc/ssl/private/ci.cluster.local.key`; `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated by `openssl req`; not stored in a data bag or vault
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts
- **Permissions**: Mode `0640`, owner `root`, group `ssl-cert`

### Self-signed TLS certificates

- **Variable(s)**: `cert_file`; `/etc/ssl/certs/test.cluster.local.crt`; `/etc/ssl/certs/ci.cluster.local.crt`; `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`; `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: Public certificate files referenced by nginx HTTPS server blocks
- **Certificate lifetime**: `365` days

### Certificate subject email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the OpenSSL command
- **Usage context**: Subject email field of each generated self-signed certificate
- **Secret status**: Not a credential or authentication secret

## Checks for the Migration

**Files to verify**:

- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default` — should be absent
- `/opt/server/test`
- `/opt/server/test/index.html`
- `/opt/server/ci`
- `/opt/server/ci/index.html`
- `/opt/server/status`
- `/opt/server/status/index.html`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/ssl/certs`
- `/etc/ssl/private`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`
- `/var/log/auth.log`

**Service endpoints to check**: `test.cluster.local` on TCP `80` and `443`; `ci.cluster.local` on TCP `80` and `443`; `status.cluster.local` on TCP `80` and `443`. Nginx listens on shared ports `80` and `443`, with virtual-host selection based on the requested hostname.

**Templates rendered**:

- `fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render
- `site.conf.erb` total: 3 renders

## Pre-flight checks

### Package and service status

```bash
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active sshd
ufw status verbose
```

Expected state: nginx and fail2ban are enabled and active; UFW is active; SSH remains available on TCP `22`.

### Nginx configuration validation

```bash
nginx -t

grep -E 'user|worker_processes|worker_connections|access_log|error_log|gzip|sites-enabled|conf.d' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

test ! -e /etc/nginx/sites-enabled/default
```

Expected result:

```text
syntax is ok
test is successful
```

### Site: `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

readlink -f /etc/nginx/sites-enabled/test.cluster.local

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

curl -k -s --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%a %U %G' /etc/ssl/private/test.cluster.local.key
```

Expected results: HTTP returns `301`; HTTPS returns `200`; the certificate subject contains `CN = test.cluster.local`; certificate validity is approximately `365` days; the key has mode `0640` and group `ssl-cert`.

### Site: `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

readlink -f /etc/nginx/sites-enabled/ci.cluster.local

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

curl -k -s --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%a %U %G' /etc/ssl/private/ci.cluster.local.key
```

Expected results: HTTP returns `301`; HTTPS returns `200`; the certificate subject contains `CN = ci.cluster.local`; certificate validity is approximately `365` days; the key has mode `0640` and group `ssl-cert`.

### Site: `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

readlink -f /etc/nginx/sites-enabled/status.cluster.local

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

curl -k -s --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/ | head

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates

stat -c '%a %U %G' /etc/ssl/private/status.cluster.local.key
```

Expected results: HTTP returns `301`; HTTPS returns `200`; the certificate subject contains `CN = status.cluster.local`; certificate validity is approximately `365` days; the key has mode `0640` and group `ssl-cert`.

### TLS and HTTP security behavior

```bash
for host in test.cluster.local ci.cluster.local status.cluster.local; do
  curl -s -D - -o /dev/null -H "Host: ${host}" http://127.0.0.1/
  curl -k -s -D - -o /dev/null \
    --resolve "${host}:443:127.0.0.1" \
    "https://${host}/"
done
```

Verify that HTTP responses return redirects to the corresponding HTTPS hostname and HTTPS responses include:

- `Strict-Transport-Security`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection`
- `Referrer-Policy`
- `Content-Security-Policy`

### Listening ports

```bash
ss -tlnp | grep -E ':(80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN
```

Expected result: nginx listens on TCP `80` and TCP `443`.

### Firewall validation

```bash
ufw status numbered
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
```

Expected result: default policy is deny; SSH, HTTP, and HTTPS are allowed; firewall status is active.

### fail2ban validation

```bash
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
```

Verify that the four jails are enabled and that ban times and retry counts match `/etc/fail2ban/jail.local`.

### SSH hardening validation

```bash
grep -E '^PermitRootLogin|^PasswordAuthentication' /etc/ssh/sshd_config
systemctl is-active sshd
```

When the reported SSH attributes are verified, expected configuration is:

```text
PermitRootLogin no
PasswordAuthentication no
```

The SSH service must remain active after any configuration change.

### Kernel security validation

```bash
sysctl net.ipv4.conf.default.rp_filter
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv6.conf.all.disable_ipv6
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv4.tcp_max_syn_backlog
```

Expected values include:

```text
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.disable_ipv6 = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
```

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

Verify that nginx has no configuration or certificate errors and that requests to `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` appear in their corresponding site logs.