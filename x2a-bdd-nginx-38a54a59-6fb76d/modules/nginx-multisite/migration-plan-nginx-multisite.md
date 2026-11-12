---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures an nginx web server for three HTTPS-enabled sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. The migration must preserve the execution order of security hardening, nginx installation and base configuration, self-signed certificate generation, and virtual-host deployment. It installs `fail2ban`, `ufw`, `nginx`, `openssl`, and `ca-certificates`; configures firewall and SSH hardening; creates site document roots and static index files; generates certificates; and enables nginx sites on ports 80 and 443.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: HTTPS-enabled nginx virtual host serving static content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; private key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; source `test/index.html`; access log `/var/log/nginx/test.cluster.local_access.log`; error log `/var/log/nginx/test.cluster.local_error.log`

- **ci.cluster.local**: HTTPS-enabled nginx virtual host serving static content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; private key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; source `ci/index.html`; access log `/var/log/nginx/ci.cluster.local_access.log`; error log `/var/log/nginx/ci.cluster.local_error.log`

- **status.cluster.local**: HTTPS-enabled nginx virtual host serving static content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80` redirects to HTTPS; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; private key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; source `status/index.html`; access log `/var/log/nginx/status.cluster.local_access.log`; error log `/var/log/nginx/status.cluster.local_error.log`

Security settings are represented by attributes rather than a recipe loop:

- `security.fail2ban.enabled = true`
- `security.ufw.enabled = true`
- `security.ssh.disable_root = true`
- `security.ssh.password_auth = false`

The analyzed recipes execute the fail2ban, UFW, and SSH operations unconditionally where present. The migration should not add conditional skips that are absent from the Chef behavior.

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
├── providers/
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
```

No provider files are used by the execution tree.

No static files are present in the supplied cookbook directory listing. The `nginx.rb` recipe references the following cookbook file sources, which must be supplied separately in the Ansible migration if the static pages are required:

- `test/index.html`
- `ci/index.html`
- `status/index.html`

## Module Explanation

The cookbook performs operations in this order:

1. `security`
2. `nginx`
3. `ssl`
4. `sites`

### 1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- Uses four `include_recipe` resources.
- The Ansible implementation must import task files in this same order.

### 2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts `fail2ban`.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local`.
- Applies the UFW default-deny policy.
- Allows SSH on `22/tcp`.
- Allows HTTP on `80/tcp`.
- Allows HTTPS on `443/tcp`.
- Enables UFW.
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf`.
- Defines delayed `sysctl -p /etc/sysctl.d/99-security.conf` execution.
- Disables SSH root login because `security.ssh.disable_root` is `true`.
- Disables SSH password authentication because `security.ssh.password_auth` is `false`.
- Defines `sshd` for delayed restart notifications.

**Resources**:

- Package: 1 resource installing `fail2ban` and `ufw`
- Service: 2 resources, `fail2ban` and `sshd`
- Template: 2 resources
- Execute: 8 resources:
  - `ufw_default_deny`
  - `ufw_allow_ssh`
  - `ufw_allow_http`
  - `ufw_allow_https`
  - `ufw_enable`
  - `reload_sysctl`
  - `disable root login`
  - `disable password auth`
- Total: 13 resources

**Iterations**: No `.each` loop is confirmed for this recipe. The fail2ban, UFW, and SSH operations are represented as individual resources.

The exact template contents, modes, ownership, notification metadata, fail2ban jail definitions, sysctl values, and complete attribute values require verification against the source files before implementation.

### 3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf`.
- Enables and starts nginx.
- Creates the document root and deploys the static index file for `test.cluster.local`:
  - Directory: `/opt/server/test`
  - File: `/opt/server/test/index.html`
  - Source: `test/index.html`
- Creates the document root and deploys the static index file for `ci.cluster.local`:
  - Directory: `/opt/server/ci`
  - File: `/opt/server/ci/index.html`
  - Source: `ci/index.html`
- Creates the document root and deploys the static index file for `status.cluster.local`:
  - Directory: `/opt/server/status`
  - File: `/opt/server/status/index.html`
  - Source: `status/index.html`

**Iterations**: The site-content loop runs three times:

1. `test.cluster.local`: `/opt/server/test`, source `test/index.html`
2. `ci.cluster.local`: `/opt/server/ci`, source `ci/index.html`
3. `status.cluster.local`: `/opt/server/status`, source `status/index.html`

**Resources**:

- Package: 1
- Template: 2
- Service: 1
- Directory: 3
- Cookbook file: 3
- Total: 10 resources

Changes to the nginx global or security configuration trigger delayed nginx reloads. The document-root and static-file resources do not define nginx notifications.

The exact nginx template directives require verification against `nginx.conf.erb` and `security.conf.erb` before migration. The supplied analysis confirms that both templates are rendered but does not independently verify their complete contents.

### 4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs `openssl` and `ca-certificates`.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs`.
- Creates `/etc/ssl/private`.
- Generates a self-signed certificate and private key for `test.cluster.local`:
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Key: `/etc/ssl/private/test.cluster.local.key`
  - Subject CN: `test.cluster.local`
- Generates a self-signed certificate and private key for `ci.cluster.local`:
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Key: `/etc/ssl/private/ci.cluster.local.key`
  - Subject CN: `ci.cluster.local`
- Generates a self-signed certificate and private key for `status.cluster.local`:
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Key: `/etc/ssl/private/status.cluster.local.key`
  - Subject CN: `status.cluster.local`

**Iterations**: The SSL loop evaluates three items:

1. `test.cluster.local`: `ssl_enabled = true`
2. `ci.cluster.local`: `ssl_enabled = true`
3. `status.cluster.local`: `ssl_enabled = true`

No configured site is skipped.

**Resources**:

- Package: 1 resource installing `openssl` and `ca-certificates`
- Group: 1
- Directory: 2
- Execute: 3
- Total: 7 resources

The generated keys are stored under `/etc/ssl/private` and are set to mode `640` with ownership `root:ssl-cert`. Certificate generation is skipped when both the certificate and key already exist. Certificate creation triggers delayed nginx reloads.

The supplied plan describes 365-day RSA 2048 self-signed certificates with no passphrase and the subject email `admin@example.com`; these command details require verification against `cookbooks/nginx-multisite/recipes/ssl.rb` before being treated as source-confirmed migration requirements.

### 5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Creates the nginx site directory resources represented by the analyzed three-item directory loop.
- Renders one virtual-host configuration for `test.cluster.local`:
  - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Destination: `/etc/nginx/sites-available/test.cluster.local`
  - Server name: `test.cluster.local`
  - Document root: `/opt/server/test`
  - Certificate: `/etc/ssl/certs/test.cluster.local.crt`
  - Private key: `/etc/ssl/private/test.cluster.local.key`
- Creates the enabled-site link:
  - Link: `/etc/nginx/sites-enabled/test.cluster.local`
  - Target: `/etc/nginx/sites-available/test.cluster.local`
- Renders one virtual-host configuration for `ci.cluster.local`:
  - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Destination: `/etc/nginx/sites-available/ci.cluster.local`
  - Server name: `ci.cluster.local`
  - Document root: `/opt/server/ci`
  - Certificate: `/etc/ssl/certs/ci.cluster.local.crt`
  - Private key: `/etc/ssl/private/ci.cluster.local.key`
- Creates the enabled-site link:
  - Link: `/etc/nginx/sites-enabled/ci.cluster.local`
  - Target: `/etc/nginx/sites-available/ci.cluster.local`
- Renders one virtual-host configuration for `status.cluster.local`:
  - Template: `cookbooks/nginx-multisite/templates/default/site.conf.erb`
  - Destination: `/etc/nginx/sites-available/status.cluster.local`
  - Server name: `status.cluster.local`
  - Document root: `/opt/server/status`
  - Certificate: `/etc/ssl/certs/status.cluster.local.crt`
  - Private key: `/etc/ssl/private/status.cluster.local.key`
- Creates the enabled-site link:
  - Link: `/etc/nginx/sites-enabled/status.cluster.local`
  - Target: `/etc/nginx/sites-available/status.cluster.local`
- Deletes `/etc/nginx/sites-enabled/default`.

**Iterations**:

- Directory loop: 3 iterations, represented in the structured analysis as `directory[path]` resources. The exact three paths must be confirmed from `cookbooks/nginx-multisite/recipes/sites.rb`; the available analysis explicitly identifies `/etc/nginx/sites-available` and `/etc/nginx/sites-enabled`, but does not provide the third path.
- Site configuration loop:
  1. `test.cluster.local`
  2. `ci.cluster.local`
  3. `status.cluster.local`

**Resources**:

- Directory: 3
- Template: 3
- Link: 3
- File deletion: 1
- Total: 10 resources

The supplied analysis identifies SSL-enabled virtual hosts with HTTP-to-HTTPS redirection, HTTPS on port 443, HTTP/2, site-specific certificates and keys, static document roots, and site-specific logs. The complete headers, TLS directives, gzip behavior, routing rules, and denied paths require verification against `cookbooks/nginx-multisite/templates/default/site.conf.erb`.

## Dependencies

**External cookbook dependencies**: None specified in the supplied metadata.

**System package dependencies**:

- `fail2ban`
- `ufw`
- `nginx`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`
- `nginx`
- `sshd`, restarted when SSH hardening changes

**Network access configured**:

- SSH: `22/tcp`
- HTTP: `80/tcp`
- HTTPS: `443/tcp`

**Supported platforms**: Platform claims require verification against the cookbook metadata and attributes before migration. The original plan identifies Ubuntu `>= 18.04` and CentOS `>= 7.0`, but these values are not confirmed by the supplied structured analysis.

## Credentials

**Detection Summary**: No externally supplied application credentials, passwords, tokens, data bags, vault integrations, or external secret-manager references were detected. Three locally generated private keys and the hardcoded certificate subject email require secure handling.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### Self-signed certificate private keys

- **Variable(s)**:
  - `key_file`
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/templates/default/site.conf.erb`
- **Current storage**: Generated locally on the managed host; not retrieved from a vault or data bag
- **Usage context**: TLS private keys for the HTTPS virtual hosts
- **Permissions**: The plan identifies mode `640` and ownership `root:ssl-cert`; verify these values against the source recipe

### Certificate subject email

- **Variable/value**: `admin@example.com`
- **Source file**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded in the certificate-generation command
- **Usage context**: Subject email field of the generated self-signed certificates
- **Migration handling**: Store as an ordinary non-secret certificate subject value unless source verification shows otherwise

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, Conjur, CyberArk, secret attributes, or environment-variable secrets were detected.

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
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/status.cluster.local.key`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/opt/server/test`
- `/opt/server/ci`
- `/opt/server/status`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- `/etc/ssl/certs`
- `/etc/ssl/private`

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH firewall allowance: `22/tcp`

**Templates rendered**:

- `fail2ban.jail.local.erb`: once
- `nginx.conf.erb`: once
- `security.conf.erb`: once
- `sysctl-security.conf.erb`: once
- `site.conf.erb`: three times:
  - `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-available/status.cluster.local`

## Pre-flight checks

```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status sshd

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active sshd

# Firewall rules
ufw status verbose
ufw status | grep '22/tcp'
ufw status | grep '80/tcp'
ufw status | grep '443/tcp'

# SSH hardening
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config

# Kernel settings
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.icmp_echo_ignore_all
sysctl net.ipv6.conf.all.disable_ipv6

# Nginx validation
nginx -t
nginx -T | grep -E 'test.cluster.local|ci.cluster.local|status.cluster.local'
test ! -e /etc/nginx/sites-enabled/default

# Listening ports
ss -tlnp | grep ':22 '
ss -tlnp | grep ':80 '
ss -tlnp | grep ':443 '
```

Expected SSH configuration:

```text
PermitRootLogin no
PasswordAuthentication no
```

### `test.cluster.local`

```bash
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/
curl -k -s --resolve test.cluster.local:443:127.0.0.1 https://test.cluster.local/ | head

test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key

openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/test.cluster.local.key
```

Expected behavior:

- HTTP redirects to `https://test.cluster.local/...`.
- HTTPS returns a successful response when the index file exists.
- The certificate subject contains `CN=test.cluster.local`.

### `ci.cluster.local`

```bash
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/
curl -k -s --resolve ci.cluster.local:443:127.0.0.1 https://ci.cluster.local/ | head

test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key

openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/ci.cluster.local.key
```

Expected behavior:

- HTTP redirects to `https://ci.cluster.local/...`.
- HTTPS returns a successful response when the index file exists.
- The certificate subject contains `CN=ci.cluster.local`.

### `status.cluster.local`

```bash
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/
curl -k -s --resolve status.cluster.local:443:127.0.0.1 https://status.cluster.local/ | head

test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key

openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -subject -dates
stat -c '%U:%G %a %n' /etc/ssl/private/status.cluster.local.key
```

Expected behavior:

- HTTP redirects to `https://status.cluster.local/...`.
- HTTPS returns a successful response when the index file exists.
- The certificate subject contains `CN=status.cluster.local`.

### TLS and security-header checks

```bash
curl -k -s -D - \
  --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/ \
  -o /dev/null | grep -E 'HTTP/|strict-transport-security|x-frame-options|x-content-type-options|content-security-policy'

openssl s_client \
  -connect 127.0.0.1:443 \
  -servername test.cluster.local </dev/null 2>/dev/null \
  | grep -E 'Protocol|Cipher|subject='

openssl s_client \
  -connect 127.0.0.1:443 \
  -servername ci.cluster.local </dev/null 2>/dev/null \
  | grep -E 'Protocol|Cipher|subject='

openssl s_client \
  -connect 127.0.0.1:443 \
  -servername status.cluster.local </dev/null 2>/dev/null \
  | grep -E 'Protocol|Cipher|subject='
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
```