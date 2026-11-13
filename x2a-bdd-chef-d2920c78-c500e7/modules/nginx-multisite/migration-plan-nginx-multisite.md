---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx for three HTTPS virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. The execution order is security configuration, nginx installation and base configuration, SSL package installation and certificate generation, and site configuration. It also configures Fail2ban, UFW, SSH hardening, security-related sysctl settings, self-signed RSA certificates, static site content, HTTP-to-HTTPS redirects, security headers, and nginx site symlinks. The Ansible migration must preserve the three exact site names, paths, ports, certificate properties, and recipe execution order.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS nginx virtual site serving static content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` for redirect; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; source file `test/index.html`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; HTTP redirects to HTTPS

- **ci.cluster.local**: HTTPS nginx virtual site serving static content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` for redirect; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; source file `ci/index.html`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; HTTP redirects to HTTPS

- **status.cluster.local**: HTTPS nginx virtual site serving static content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` for redirect; HTTPS `443`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; source file `status/index.html`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; HTTP redirects to HTTPS

**Security services and settings**:

- **fail2ban**: Enabled; service `fail2ban`; configuration `/etc/fail2ban/jail.local`
- **ufw**: Enabled; default incoming policy `deny`; allows SSH, HTTP, and HTTPS
- **ssh**: Root login disabled; password authentication disabled

The supplied execution tree confirms the three-site collection and the security configuration flow. Attribute values and detailed template directives should be verified against the source files before implementation because they are not fully represented in the structured analysis.

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

No provider files are included in the supplied directory listing or execution tree.

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

No static files under `files/` are included in the supplied directory listing. The recipes reference these cookbook files, which must be supplied as migration inputs:

```text
test/index.html
ci/index.html
status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.
   - The Ansible role must preserve this order: security, nginx installation, SSL generation, and site configuration.
   - Resources: four `include_recipe` operations.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
   - Configures the reported Fail2ban defaults: ban time `3600`, find time `600`, maximum retries `3`, and backend `auto`.
   - Configures the reported SSH, nginx HTTP authentication, nginx request-rate, and nginx bot-search jails.
   - Configures UFW with default deny policy and allows SSH, HTTP, and HTTPS.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
   - Applies the sysctl file with `sysctl -p /etc/sysctl.d/99-security.conf` when the file changes.
   - Applies SSH hardening when enabled:
     - Sets `PermitRootLogin no`.
     - Sets `PasswordAuthentication no`.
     - Notifies a delayed `sshd` restart when either setting changes.
   - Declares `service[sshd]` as a notification target with action `nothing`; this recipe does not directly enable or start `sshd`.
   - Reported resources in execution order:
     - One package resource installing `fail2ban` and `ufw`.
     - `service[fail2ban]`.
     - Template resource for `/etc/fail2ban/jail.local`.
     - UFW default-deny command.
     - UFW SSH allow command.
     - UFW HTTP allow command.
     - UFW HTTPS allow command.
     - UFW enable command.
     - Template resource for `/etc/sysctl.d/99-security.conf`.
     - Initially disabled sysctl reload command.
     - Conditional root-login hardening command.
     - Conditional password-authentication hardening command.
     - `service[sshd]` with action `nothing`.
   - The detailed jail directives, sysctl values, ownership, modes, and conditional attribute values require verification against the source templates and attributes file.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
   - Enables and starts the `nginx` service.
   - Creates the document roots and deploys static index files for all three sites:
     - **test.cluster.local**
       - Creates `/opt/server/test`.
       - Deploys `test/index.html` to `/opt/server/test/index.html`.
     - **ci.cluster.local**
       - Creates `/opt/server/ci`.
       - Deploys `ci/index.html` to `/opt/server/ci/index.html`.
     - **status.cluster.local**
       - Creates `/opt/server/status`.
       - Deploys `status/index.html` to `/opt/server/status/index.html`.
   - The source directory is derived from the first DNS label: `test`, `ci`, and `status`.
   - The site loop runs exactly three times for `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`.
   - Reported resources in execution order:
     - `package[nginx]`.
     - Template resource for `/etc/nginx/nginx.conf`.
     - Template resource for `/etc/nginx/conf.d/security.conf`.
     - `service[nginx]`.
     - Three document-root directory resources.
     - Three static-file resources.
   - Changes to the nginx configuration templates notify a delayed nginx reload.
   - The reported base configuration includes worker, logging, gzip, module-include, and site-include settings. These detailed template directives and file ownership or mode values require verification against `nginx.conf.erb`, `security.conf.erb`, and the recipe source.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs`.
   - Creates `/etc/ssl/private`.
   - Generates self-signed certificates for exactly three sites:
     - **test.cluster.local**
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Key: `/etc/ssl/private/test.cluster.local.key`
       - Common Name: `test.cluster.local`
       - RSA key size: `2048`
       - Validity: `365` days
     - **ci.cluster.local**
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Key: `/etc/ssl/private/ci.cluster.local.key`
       - Common Name: `ci.cluster.local`
       - RSA key size: `2048`
       - Validity: `365` days
     - **status.cluster.local**
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Key: `/etc/ssl/private/status.cluster.local.key`
       - Common Name: `status.cluster.local`
       - RSA key size: `2048`
       - Validity: `365` days
   - Uses an OpenSSL self-signed certificate command with `-x509`, `-nodes`, `-days 365`, `-newkey rsa:2048`, and a site-specific subject.
   - Skips certificate generation when both the certificate and key already exist.
   - Applies the reported private-key permissions and ownership: mode `0640`, owner `root`, group `ssl-cert`.
   - Each certificate-generation command notifies a delayed nginx reload.
   - Reported resources in execution order:
     - One package resource installing `openssl` and `ca-certificates`.
     - `group[ssl-cert]`.
     - Certificate directory resource.
     - Private-key directory resource.
     - Certificate-generation command for `test.cluster.local`.
     - Certificate-generation command for `ci.cluster.local`.
     - Certificate-generation command for `status.cluster.local`.
   - Certificate-generation and key-permission details should be verified against `cookbooks/nginx-multisite/recipes/ssl.rb`.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates `/etc/nginx/sites-available`.
   - Creates `/etc/nginx/sites-enabled`.
   - Renders and enables the site configuration exactly three times:
     - **test.cluster.local**
       - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
       - Destination: `/etc/nginx/sites-available/test.cluster.local`
       - Link: `/etc/nginx/sites-enabled/test.cluster.local`
       - Document root: `/opt/server/test`
       - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
       - Key: `/etc/ssl/private/test.cluster.local.key`
       - SSL enabled: `true`
     - **ci.cluster.local**
       - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
       - Destination: `/etc/nginx/sites-available/ci.cluster.local`
       - Link: `/etc/nginx/sites-enabled/ci.cluster.local`
       - Document root: `/opt/server/ci`
       - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
       - Key: `/etc/ssl/private/ci.cluster.local.key`
       - SSL enabled: `true`
     - **status.cluster.local**
       - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
       - Destination: `/etc/nginx/sites-available/status.cluster.local`
       - Link: `/etc/nginx/sites-enabled/status.cluster.local`
       - Document root: `/opt/server/status`
       - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
       - Key: `/etc/ssl/private/status.cluster.local.key`
       - SSL enabled: `true`
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Changes to site templates, links, or default-site removal notify a delayed nginx reload.
   - The reported site-template behavior is:
     - HTTP listener on port `80`.
     - Redirect from HTTP to HTTPS.
     - HTTPS listener on port `443`.
     - HTTP/2 enabled.
     - TLS versions `TLSv1.2` and `TLSv1.3`.
     - HSTS and security headers.
     - Gzip compression.
     - `try_files $uri $uri/ =404`.
     - Denial of `.htaccess`, `.git`, and `.svn` paths.
     - Site-specific access and error logs.
   - Reported resources in execution order:
     - Two directory resources.
     - Three site template resources.
     - Three link resources.
     - File removal resource for `/etc/nginx/sites-enabled/default`.
   - Detailed headers, cipher lists, log directives, and template behavior require verification against `cookbooks/nginx-multisite/templates/default/site.conf.erb`.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `sshd`: restarted only when SSH hardening changes
- `ufw`: enabled through firewall configuration commands

**Operating-system support declared by metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The UFW commands and `/var/log/auth.log` path align most directly with Debian/Ubuntu systems. The Ansible role must either preserve this platform behavior or make an explicit platform decision before applying UFW and Fail2ban configuration on CentOS.

## Credentials

**Detection Summary**: No external credentials or secret-storage integrations detected. Three locally generated TLS private keys and three locally generated self-signed certificates are created by the SSL recipe.

**Source**:
  - **Provider**: None detected
  - **URL**: Not applicable
  - **Path**: Not applicable

### Self-signed TLS private keys

- **Variable(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL; not stored in a data bag, vault, external provider, or environment variable.
- **Usage context**: TLS private keys used by nginx for HTTPS termination.
- **Reported permissions**: Mode `0640`, owned by `root:ssl-cert`.

### Self-signed TLS certificates

- **Variable(s)**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Generated locally by OpenSSL.
- **Usage context**: Public certificates referenced by nginx HTTPS virtual hosts.
- **Reported properties**: RSA `2048`-bit self-signed certificates valid for `365` days.
- **Certificate subject metadata**: The reported subject includes `admin@example.com` and example organization fields. These are certificate metadata, not application credentials.

The supplied validation confirms the absence of external credential-provider references only to the extent represented by the analyzed files. A complete migration scan should include all recipes, templates, and `cookbooks/nginx-multisite/attributes/default.rb`.

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
- `/etc/nginx/sites-enabled/default` must not exist
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`

**Directories to verify**:

- `/opt/server/test`
- `/opt/server/ci`
- `/opt/server/status`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/ssl/certs`
- `/etc/ssl/private`

**Log files to verify**:

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

- HTTP TCP port `80`
- HTTPS TCP port `443`
- SSH TCP port `22`
- nginx PID file `/run/nginx.pid`
- No Unix socket is configured by this cookbook

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/test.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/ci.cluster.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → `/etc/nginx/sites-available/status.cluster.local`: 1 render

## Pre-flight checks

Run these checks after the Ansible migration.

### Package and service checks

```bash
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx

systemctl is-enabled fail2ban
systemctl is-active fail2ban

systemctl is-active sshd
```

Verify that nginx and Fail2ban are enabled and active, SSH is active, and all five packages are installed.

### Nginx configuration validation

```bash
nginx -t
nginx -T | grep -E \
'server_name (test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local)'

grep -E 'user nginx|worker_processes|worker_connections|access_log|error_log' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf
```

Expected result:

```text
syntax is ok
test is successful
```

### Instance-specific HTTP checks

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
```

Verify individually that:

- `test.cluster.local` returns HTTP status `301` and redirects to its HTTPS URL.
- `ci.cluster.local` returns HTTP status `301` and redirects to its HTTPS URL.
- `status.cluster.local` returns HTTP status `301` and redirects to its HTTPS URL.

### Instance-specific HTTPS checks

Because the certificates are self-signed, use `-k`.

```bash
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
```

Verify individually that:

- `test.cluster.local` returns HTTP status `200` from `/opt/server/test`, includes HSTS, `X-Frame-Options: DENY`, and `X-Content-Type-Options: nosniff`.
- `ci.cluster.local` returns HTTP status `200` from `/opt/server/ci`, includes HSTS, `X-Frame-Options: DENY`, and `X-Content-Type-Options: nosniff`.
- `status.cluster.local` returns HTTP status `200` from `/opt/server/status`, includes HSTS, `X-Frame-Options: DENY`, and `X-Content-Type-Options: nosniff`.

### Instance-specific content checks

```bash
test -f /opt/server/test/index.html
test -f /opt/server/ci/index.html
test -f /opt/server/status/index.html

curl -k --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

curl -k --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

curl -k --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/
```

Verify that:

- `test.cluster.local` serves `/opt/server/test/index.html`.
- `ci.cluster.local` serves `/opt/server/ci/index.html`.
- `status.cluster.local` serves `/opt/server/status/index.html`.

### Certificate checks

```bash
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt \
  -noout -subject -issuer -dates

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt \
  -noout -subject -issuer -dates

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt \
  -noout -subject -issuer -dates
```

Verify individually:

- `test.cluster.local` has subject CN `test.cluster.local`.
- `ci.cluster.local` has subject CN `ci.cluster.local`.
- `status.cluster.local` has subject CN `status.cluster.local`.
- Each certificate is self-signed, uses an RSA `2048`-bit key, and is valid for approximately `365` days.

Verify private-key ownership and permissions:

```bash
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected result for each key:

```text
root:ssl-cert 640
```

### Nginx listener checks

```bash
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN
```

Verify that nginx listens on TCP ports `80` and `443`.

### Site link checks

```bash
readlink -f /etc/nginx/sites-enabled/test.cluster.local
readlink -f /etc/nginx/sites-enabled/ci.cluster.local
readlink -f /etc/nginx/sites-enabled/status.cluster.local

test ! -e /etc/nginx/sites-enabled/default
```

Expected links:

```text
/etc/nginx/sites-available/test.cluster.local
/etc/nginx/sites-available/ci.cluster.local
/etc/nginx/sites-available/status.cluster.local
```

The default enabled site must not exist.

### Firewall checks

```bash
ufw status verbose
ufw status numbered
```

Verify:

- UFW status is `active`.
- Default incoming policy is `deny`.
- SSH is allowed on `22/tcp`.
- HTTP is allowed on `80/tcp`.
- HTTPS is allowed on `443/tcp`.

### Fail2ban checks

```bash
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch

grep -E 'bantime|findtime|maxretry|backend' \
  /etc/fail2ban/jail.local
```

Verify that the expected jails are present:

- `sshd`
- `nginx-http-auth`
- `nginx-limit-req`
- `nginx-botsearch`

### SSH hardening checks

```bash
grep -E '^PermitRootLogin no$' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication no$' /etc/ssh/sshd_config

sshd -t
systemctl is-active sshd
```

Expected results:

```text
PermitRootLogin no
PasswordAuthentication no
```

`sshd -t` must succeed and `sshd` must be active.

### Sysctl checks

```bash
sysctl -p /etc/sysctl.d/99-security.conf

sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.all.accept_redirects
sysctl net.ipv6.conf.all.accept_redirects
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_source_route
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv4.tcp_syncookies
sysctl net.ipv6.conf.all.disable_ipv6
```

Verify the configured values, including:

- `rp_filter = 1`
- `accept_redirects = 0`
- `send_redirects = 0`
- `accept_source_route = 0`
- `icmp_echo_ignore_all = 1`
- `tcp_syncookies = 1`
- IPv6 disabled according to the deployed sysctl configuration

### Log checks

```bash
tail -n 50 /var/log/nginx/access.log
tail -n 50 /var/log/nginx/error.log

tail -n 50 /var/log/nginx/test.cluster.local_access.log
tail -n 50 /var/log/nginx/test.cluster.local_error.log

tail -n 50 /var/log/nginx/ci.cluster.local_access.log
tail -n 50 /var/log/nginx/ci.cluster.local_error.log

tail -n 50 /var/log/nginx/status.cluster.local_access.log
tail -n 50 /var/log/nginx/status.cluster.local_error.log

journalctl -u nginx --since '10 minutes ago'
journalctl -u fail2ban --since '10 minutes ago'
```

Verify that requests to `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local` appear in their respective access logs and that nginx reports no configuration or certificate errors.