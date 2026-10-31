---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook provisions an Nginx web server hosting three HTTPS-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs and starts Nginx and Fail2ban, configures UFW to deny inbound traffic by default while allowing SSH, HTTP, and HTTPS, applies kernel security settings, disables root SSH login and SSH password authentication, generates self-signed certificates, deploys static index pages, and enables the three Nginx site configurations. Certificate generation should be made idempotent in Ansible as an intentional migration improvement because the analyzed Chef execute resources do not show existence guards.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
  - Static content: `/opt/server/test/index.html`
  - SSL: Enabled

- **ci.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
  - Static content: `/opt/server/ci/index.html`
  - SSL: Enabled

- **status.cluster.local**: HTTPS-enabled Nginx virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`, HTTPS `443`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
  - Static content: `/opt/server/status/index.html`
  - SSL: Enabled

The `security` attribute namespace contains the following configured areas. These values are asserted by the migration plan but were not independently verified because an attributes analysis was not supplied:

- `fail2ban.enabled`: `true`
- `ufw.enabled`: `true`
- `ssh.disable_root`: `true`
- `ssh.password_auth`: `false`

Expected network access:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH: UFW `ssh` application rule; the exact port is determined by the system SSH configuration

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

No static file path under `files/` is listed in the supplied analysis. The `cookbook_file` resources deploy site index files from dynamically formed source paths based on the site folder; those source files are not included in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `security.rb`.
   - Includes `nginx.rb`.
   - Includes `ssl.rb`.
   - Includes `sites.rb`.
   - Execution order is `security`, `nginx`, `ssl`, then `sites`.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs `fail2ban` and `ufw`.
   - Enables and starts the `fail2ban` service.
   - Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
   - Sets the UFW default inbound policy to deny with `ufw --force default deny`.
   - Allows the UFW `ssh` application rule with `ufw allow ssh`.
   - Allows HTTP with `ufw allow http`.
   - Allows HTTPS with `ufw allow https`.
   - Enables UFW with `ufw --force enable`.
   - Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
   - Defines a sysctl reload command:
     ```bash
     sysctl -p /etc/sysctl.d/99-security.conf
     ```
   - The sysctl reload action is `nothing` unless notified.
   - Disables root SSH login when `security.ssh.disable_root` is `true`:
     ```bash
     sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
     ```
   - Disables SSH password authentication when `security.ssh.password_auth` is `false`:
     ```bash
     sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
     ```
   - Defines the `ssh` service as a notification target with action `nothing`; the Ansible implementation should reload or restart SSH only after SSH configuration changes.
   - Resources: one package resource, two service resources (`fail2ban` and `ssh`), two templates, and eight execute resources.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
   - Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
   - Enables and starts the `nginx` service.
   - Creates `/opt/server/test` and deploys `/opt/server/test/index.html` with mode `0644`.
   - Creates `/opt/server/ci` and deploys `/opt/server/ci/index.html` with mode `0644`.
   - Creates `/opt/server/status` and deploys `/opt/server/status/index.html` with mode `0644`.
   - The three cookbook file source paths are dynamically formed from the corresponding site folder and `index.html`.
   - Resource counts: one package, two templates, one service, three directories, and three cookbook files.
   - The analyzed execution tree starts Nginx before the per-site document roots and index files are deployed and does not show an explicit reload after static files are created.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs `openssl` and `ca-certificates`.
   - Creates the `ssl-cert` group.
   - Creates `/etc/ssl/certs` with mode `0755`.
   - Creates `/etc/ssl/private` with mode `0710`.
   - Generates a self-signed certificate and private key for `test.cluster.local`:
     - Key: `/etc/ssl/private/test.cluster.local.key`
     - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
     - Resource: `generate-ssl-cert-test.cluster.local`
   - Generates a self-signed certificate and private key for `ci.cluster.local`:
     - Key: `/etc/ssl/private/ci.cluster.local.key`
     - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
     - Resource: `generate-ssl-cert-ci.cluster.local`
   - Generates a self-signed certificate and private key for `status.cluster.local`:
     - Key: `/etc/ssl/private/status.cluster.local.key`
     - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
     - Resource: `generate-ssl-cert-status.cluster.local`
   - Each certificate command is equivalent to:
     ```bash
     openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout <site-private-key> \
       -out <site-certificate> \
       -subj "/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site-name>/emailAddress=admin@example.com"
     chmod 640 <site-private-key>
     chown root:ssl-cert <site-private-key>
     ```
   - Certificates are self-signed X.509 certificates valid for `365` days with RSA `2048` keys.
   - Private keys are generated without passphrases because `-nodes` is used.
   - Private keys have mode `0640` and ownership `root:ssl-cert`.
   - The Ansible implementation should use file existence or certificate inspection checks to avoid regenerating certificates on every run. This is an intentional idempotence correction because no guard is shown for the analyzed Chef execute resources.
   - Resource counts: one package resource installing two packages, one group, two directories, and three execute resources.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local` with mode `0644`.
   - Uses `server_name test.cluster.local`, document root `/opt/server/test`, SSL enabled, certificate `/etc/ssl/certs/test.cluster.local.crt`, and key `/etc/ssl/private/test.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/test.cluster.local` pointing to `/etc/nginx/sites-available/test.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local` with mode `0644`.
   - Uses `server_name ci.cluster.local`, document root `/opt/server/ci`, SSL enabled, certificate `/etc/ssl/certs/ci.cluster.local.crt`, and key `/etc/ssl/private/ci.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/ci.cluster.local` pointing to `/etc/nginx/sites-available/ci.cluster.local`.
   - Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` for `status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local` with mode `0644`.
   - Uses `server_name status.cluster.local`, document root `/opt/server/status`, SSL enabled, certificate `/etc/ssl/certs/status.cluster.local.crt`, and key `/etc/ssl/private/status.cluster.local.key`.
   - Creates `/etc/nginx/sites-enabled/status.cluster.local` pointing to `/etc/nginx/sites-available/status.cluster.local`.
   - Deletes `/etc/nginx/sites-enabled/default`.
   - Resource counts: three templates, three links, and one file deletion.
   - The Ansible implementation should validate the Nginx configuration and reload Nginx when site templates or links change.

## Dependencies

**External cookbook dependencies**: Dependency metadata was not supplied. No external cookbook dependencies were identified in the supplied execution tree.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started.
- `nginx`: enabled and started.
- `ssh`: notification target for SSH configuration changes.
- `ufw`: enabled using `ufw --force enable`.
- `sysctl`: reloaded using `/etc/sysctl.d/99-security.conf`.

## Credentials

**Detection Summary**: No application passwords, API tokens, data bags, encrypted data bags, Chef Vault items, CyberArk references, Conjur variables, or environment-variable secrets were detected. Three locally generated TLS private keys are sensitive files but are not retrieved from a secret-management system.

**Source**:

- **Provider**: None detected; TLS material is generated locally with OpenSSL.
- **URL**: None detected.
- **Path**:
  - `/etc/ssl/certs`
  - `/etc/ssl/private`

### TLS Private Keys

- **Variable(s)**:
  - `key_file`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; not stored in a data bag, vault, or external secret manager.
- **Usage context**: Used by the three Nginx virtual hosts as private TLS keys. Keys are generated with `openssl req -x509 -nodes -days 365 -newkey rsa:2048`, then assigned mode `0640` and ownership `root:ssl-cert`.

### Self-Signed TLS Certificates

- **Variable(s)**:
  - `cert_file`
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated certificate files.
- **Usage context**: Referenced by the Nginx site configurations. Each certificate uses its site hostname as the common name and is valid for `365` days.

The OpenSSL subject includes the non-secret identifier `admin@example.com`. No password is supplied because the private keys are generated with `-nodes`.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/sysctl.d/99-security.conf`
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
- Confirm `/etc/nginx/sites-enabled/default` is absent.

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH: the port configured by the host SSH service and allowed by UFW

**Templates rendered**:

- `fail2ban.jail.local.erb`: rendered once to `/etc/fail2ban/jail.local`
- `nginx.conf.erb`: rendered once to `/etc/nginx/nginx.conf`
- `security.conf.erb`: rendered once to `/etc/nginx/conf.d/security.conf`
- `sysctl-security.conf.erb`: rendered once to `/etc/sysctl.d/99-security.conf`
- `site.conf.erb`: rendered three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

### Security services and firewall

```bash
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

ufw status verbose
ufw status numbered
ufw default
ufw show added
```

Confirm that the default inbound policy is deny, SSH is allowed, HTTP is allowed, HTTPS is allowed, and UFW is active.

### SSH hardening

```bash
grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config
sshd -t
systemctl status ssh
```

Confirm:

- `PermitRootLogin no`
- `PasswordAuthentication no`
- `sshd -t` exits successfully.
- The SSH service remains active after configuration changes.
- The configured SSH port remains allowed by UFW.

### Kernel security configuration

```bash
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
sysctl --system
```

Confirm that effective kernel values match the settings rendered by `sysctl-security.conf.erb`.

### Nginx service and configuration

```bash
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
nginx -T
```

Confirm that Nginx is enabled and active, `nginx -t` succeeds, and the configuration includes all three enabled site files.

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
stat -c '%A %U:%G' /etc/ssl/private/test.cluster.local.key

curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
```

Confirm the document root, index file, virtual-host configuration, symlink, certificate, and private key exist. The symlink must resolve to `/etc/nginx/sites-available/test.cluster.local`; the certificate subject must contain `CN=test.cluster.local`; and the key must be owned by `root:ssl-cert` with mode equivalent to `0640`.

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
stat -c '%A %U:%G' /etc/ssl/private/ci.cluster.local.key

curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
```

Confirm the document root, index file, virtual-host configuration, symlink, certificate, and private key exist. The symlink must resolve to `/etc/nginx/sites-available/ci.cluster.local`; the certificate subject must contain `CN=ci.cluster.local`; and the key must be owned by `root:ssl-cert` with mode equivalent to `0640`.

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
stat -c '%A %U:%G' /etc/ssl/private/status.cluster.local.key

curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
```

Confirm the document root, index file, virtual-host configuration, symlink, certificate, and private key exist. The symlink must resolve to `/etc/nginx/sites-available/status.cluster.local`; the certificate subject must contain `CN=status.cluster.local`; and the key must be owned by `root:ssl-cert` with mode equivalent to `0640`.

### HTTP and HTTPS listeners

```bash
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
```

Confirm that Nginx listens on TCP ports `80` and `443`.

DNS or `/etc/hosts` must resolve all three hostnames to the target server before running the virtual-host checks.

### Default site removal

```bash
test ! -e /etc/nginx/sites-enabled/default
```

Confirm that the default Nginx site does not exist.

### Logs

```bash
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
journalctl -u ssh --no-pager -n 50
```

Check for configuration errors, certificate-generation failures, Fail2ban startup failures, and SSH reload failures.