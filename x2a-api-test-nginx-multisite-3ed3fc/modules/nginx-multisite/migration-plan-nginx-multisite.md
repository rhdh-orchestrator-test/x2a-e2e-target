---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures Nginx with three HTTPS virtual hosts—`test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs Nginx, OpenSSL, Fail2ban, and UFW; applies firewall, SSH, sysctl, and Fail2ban hardening; creates site document roots and index files; generates self-signed certificates and private keys; renders and enables one Nginx configuration per site; and removes the default Nginx site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **`test.cluster.local`**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTPS port `443`; HTTP port `80`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`

- **`ci.cluster.local`**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTPS port `443`; HTTP port `80`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`

- **`status.cluster.local`**: Nginx HTTPS virtual host
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTPS port `443`; HTTP port `80`
  - Key Config: SSL enabled; certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`

**Security services and controls**:

- **`fail2ban`**: Installed, configured with `/etc/fail2ban/jail.local`, enabled, and started.
- **`ufw`**: Installed with a default deny policy; SSH, HTTP, and HTTPS are allowed; firewall is enabled.
- **`ssh`**: `/etc/ssh/sshd_config` is modified to disable root login and password authentication. The service is declared with action `nothing`; no restart is shown.
- **Sysctl security**: Rendered to `/etc/sysctl.d/99-security.conf`; the Chef execution tree defines a reload command with action `nothing` and does not show a notification.

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

No provider files or custom resources are used by the execution tree.

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

The cookbook uses `cookbook_file` resources for site index files, but the supplied file inventory does not identify concrete static file paths under `files/default/`. Do not invent source paths; preserve the dynamic `site_folder/index.html` source behavior during migration.

## Module Explanation

The cookbook performs operations in this order:

1. `cookbooks/nginx-multisite/recipes/default.rb`
2. `cookbooks/nginx-multisite/recipes/security.rb`
3. `cookbooks/nginx-multisite/recipes/nginx.rb`
4. `cookbooks/nginx-multisite/recipes/ssl.rb`
5. `cookbooks/nginx-multisite/recipes/sites.rb`

The Ansible role should preserve this order with task-file imports.

### 1. Default recipe (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- Equivalent task order:
  ```yaml
  - import_tasks: security.yml
  - import_tasks: nginx.yml
  - import_tasks: ssl.yml
  - import_tasks: sites.yml
  ```

### 2. Security configuration (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs `fail2ban` and `ufw`.
- Enables and starts the `fail2ban` service.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Executes UFW commands in this order:
  1. `ufw --force default deny`
  2. `ufw allow ssh`
  3. `ufw allow http`
  4. `ufw allow https`
  5. `ufw --force enable`
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Defines `sysctl -p /etc/sysctl.d/99-security.conf` as `execute[reload_sysctl]` with action `nothing`; no notification is shown.
- Because `security.ssh.disable_root` is `true`, replaces the SSH root-login setting with:
  ```bash
  sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
  ```
- Because `security.ssh.password_auth` is `false`, replaces the SSH password-authentication setting with:
  ```bash
  sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
  ```
- Defines `service[ssh]` with action `nothing`; no SSH restart is shown.

### 3. Nginx installation and site content (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Enables and starts the `nginx` service.
- Creates document roots and deploys index files with directory mode `0755` and index-file mode `0644`.

**Expanded iterations:**

- **`test.cluster.local`**
  - Creates `/opt/server/test`.
  - Deploys `/opt/server/test/index.html`.
  - Derives the cookbook source dynamically from `site_folder/index.html`.

- **`ci.cluster.local`**
  - Creates `/opt/server/ci`.
  - Deploys `/opt/server/ci/index.html`.
  - Derives the cookbook source dynamically from `site_folder/index.html`.

- **`status.cluster.local`**
  - Creates `/opt/server/status`.
  - Deploys `/opt/server/status/index.html`.
  - Derives the cookbook source dynamically from `site_folder/index.html`.

The Ansible implementation must loop over the explicitly defined `nginx_sites` dictionary while retaining each site name and document root. The Nginx service starts after the Nginx configuration templates are rendered.

### 4. SSL package installation and certificate generation (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs `openssl` and `ca-certificates`.
- Creates group `ssl-cert`.
- Creates `/etc/ssl/certs` with mode `0755`.
- Creates `/etc/ssl/private` with mode `0710`.
- Generates 2048-bit RSA, 365-day, self-signed certificates for all three SSL-enabled sites.

**Expanded iterations:**

- **`test.cluster.local`**
  - Key: `/etc/ssl/private/test.cluster.local.key`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`

- **`ci.cluster.local`**
  - Key: `/etc/ssl/private/ci.cluster.local.key`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`

- **`status.cluster.local`**
  - Key: `/etc/ssl/private/status.cluster.local.key`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`

Each certificate uses this subject pattern:

```text
/C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN=<site_name>/emailAddress=admin@example.com
```

Each private key is owned by `root:ssl-cert` with mode `0640`.

An idempotent Ansible implementation should use `creates` or certificate-aware modules while preserving the output paths, subject names, RSA size, and certificate lifetime.

### 5. Nginx virtual-host sites (`cookbooks/nginx-multisite/recipes/sites.rb`)

The recipe renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` and creates an enabled-site link for each configured site.

**Expanded iterations:**

- **`test.cluster.local`**
  - Renders to `/etc/nginx/sites-available/test.cluster.local`.
  - Variables: `server_name=test.cluster.local`, `document_root=/opt/server/test`, `ssl_enabled=True`, `cert_file=/etc/ssl/certs/test.cluster.local.crt`, and `key_file=/etc/ssl/private/test.cluster.local.key`.
  - Links `/etc/nginx/sites-enabled/test.cluster.local` to `/etc/nginx/sites-available/test.cluster.local`.

- **`ci.cluster.local`**
  - Renders to `/etc/nginx/sites-available/ci.cluster.local`.
  - Variables: `server_name=ci.cluster.local`, `document_root=/opt/server/ci`, `ssl_enabled=True`, `cert_file=/etc/ssl/certs/ci.cluster.local.crt`, and `key_file=/etc/ssl/private/ci.cluster.local.key`.
  - Links `/etc/nginx/sites-enabled/ci.cluster.local` to `/etc/nginx/sites-available/ci.cluster.local`.

- **`status.cluster.local`**
  - Renders to `/etc/nginx/sites-available/status.cluster.local`.
  - Variables: `server_name=status.cluster.local`, `document_root=/opt/server/status`, `ssl_enabled=True`, `cert_file=/etc/ssl/certs/status.cluster.local.crt`, and `key_file=/etc/ssl/private/status.cluster.local.key`.
  - Links `/etc/nginx/sites-enabled/status.cluster.local` to `/etc/nginx/sites-available/status.cluster.local`.

After these iterations, removes `/etc/nginx/sites-enabled/default`. The Chef execution tree does not explicitly show an Nginx reload notification.

## Dependencies

**External cookbook dependencies**: None shown.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started
- `nginx`: enabled and started
- `ssh`: declared with action `nothing`; no restart shown

**Security and networking dependencies**:

- UFW default incoming policy: deny
- SSH allowed
- HTTP allowed
- HTTPS allowed
- SSH root login disabled
- SSH password authentication disabled
- `ssl-cert` group exists before private-key generation

## Credentials

**Detection Summary**: 0 external credentials detected across 0 files. Two types of locally generated TLS material are created across `cookbooks/nginx-multisite/recipes/ssl.rb`, `cookbooks/nginx-multisite/recipes/sites.rb`, and `cookbooks/nginx-multisite/attributes/default.rb`.

**Source**:
  - **Provider**: None detected
  - **URL**: None detected
  - **Path**: No secret path or data bag detected

### TLS private keys

- **Variable(s)**: `node['nginx']['ssl']['private_key_path']` and site names `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/attributes/default.rb`
- **Current storage**: Locally generated files
- **Usage context**: Nginx HTTPS private keys
- **Generated paths**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Permissions and ownership**: Mode `0640`, owner `root`, group `ssl-cert`

### TLS certificates

- **Variable(s)**: `node['nginx']['ssl']['certificate_path']` and site names `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
  - `cookbooks/nginx-multisite/attributes/default.rb`
- **Current storage**: Locally generated self-signed certificate files
- **Usage context**: Nginx HTTPS certificates
- **Generated paths**:
  - `/etc/ssl/certs/test.cluster.local.crt`
  - `/etc/ssl/certs/ci.cluster.local.crt`
  - `/etc/ssl/certs/status.cluster.local.crt`

The certificate subject contains the non-secret email address `admin@example.com`. No password, token, external certificate provider, or secret-manager integration is used.

## Checks for the Migration

**Files to verify**:

- `cookbooks/nginx-multisite/recipes/default.rb`
- `cookbooks/nginx-multisite/recipes/security.rb`
- `cookbooks/nginx-multisite/recipes/nginx.rb`
- `cookbooks/nginx-multisite/recipes/ssl.rb`
- `cookbooks/nginx-multisite/recipes/sites.rb`
- `cookbooks/nginx-multisite/attributes/default.rb`
- `/etc/fail2ban/jail.local`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/sites-available/test.cluster.local`
- `/etc/nginx/sites-available/ci.cluster.local`
- `/etc/nginx/sites-available/status.cluster.local`
- `/etc/nginx/sites-enabled/test.cluster.local`
- `/etc/nginx/sites-enabled/ci.cluster.local`
- `/etc/nginx/sites-enabled/status.cluster.local`
- `/etc/nginx/sites-enabled/default`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
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
- `/etc/ssl/certs`
- `/etc/ssl/private`

**Service endpoints to check**:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH: configured SSH port and the corresponding UFW rule
- Nginx hostnames: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb`: 3 renders
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks

### Security services, firewall, and SSH

```bash
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

ufw status verbose
ufw status numbered

grep -E '^[[:space:]]*PermitRootLogin' /etc/ssh/sshd_config
grep -E '^[[:space:]]*PasswordAuthentication' /etc/ssh/sshd_config

cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf
```

Expected SSH settings:

```text
PermitRootLogin no
PasswordAuthentication no
```

Expected UFW behavior:

- Default incoming policy is deny.
- SSH is allowed.
- HTTP is allowed.
- HTTPS is allowed.

### Nginx service and configuration

```bash
systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx
nginx -t
ss -tlnp | grep ':80'
ss -tlnp | grep ':443'
```

Expected `nginx -t` output indicates that syntax is OK and the test is successful. Nginx should listen on TCP ports `80` and `443`.

### Site configuration: `test.cluster.local`

```bash
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
```

Verify that the HTTPS request reaches the `test.cluster.local` virtual host, normally returns HTTP `200`, contains `CN=test.cluster.local`, and uses private-key ownership `root:ssl-cert` with mode `640`.

### Site configuration: `ci.cluster.local`

```bash
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
```

Verify that the HTTPS request reaches the `ci.cluster.local` virtual host, normally returns HTTP `200`, contains `CN=ci.cluster.local`, and uses private-key ownership `root:ssl-cert` with mode `640`.

### Site configuration: `status.cluster.local`

```bash
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Verify that the HTTPS request reaches the `status.cluster.local` virtual host, normally returns HTTP `200`, contains `CN=status.cluster.local`, and uses private-key ownership `root:ssl-cert` with mode `640`.

### Default Nginx site removal

```bash
test ! -e /etc/nginx/sites-enabled/default
```

### Nginx host and SSL configuration

```bash
grep -R -E 'test\.cluster\.local|ci\.cluster\.local|status\.cluster\.local' /etc/nginx/sites-available
grep -R -E '/etc/ssl/certs|/etc/ssl/private' /etc/nginx/sites-available
```

### Logs

```bash
journalctl -u nginx --no-pager -n 50
journalctl -u fail2ban --no-pager -n 50
```

Check for configuration errors, certificate-access failures, permission failures, and service-start failures.