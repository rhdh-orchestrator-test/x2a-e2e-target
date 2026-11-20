---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook installs and configures nginx as a multi-site web server, creates document roots and virtual-host links from the `nginx_sites` Chef data bag, optionally generates self-signed TLS certificates, and applies host security hardening with fail2ban, UFW, sysctl, and SSH settings. Execution order is `security` → `nginx` → `ssl` → `sites`. The cookbook contains one encrypted secret, the `token` field from `nginx_secrets/site`. The supplied source does not include the names or values of the `nginx_sites` data bag items, so the site inventory must be obtained before the Ansible role is implemented.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **nginx**
  - Purpose: Multi-site HTTP and HTTPS web server
  - Location/Path: `/etc/nginx`
  - Port/Socket: TCP `80` and TCP `443`; no Unix socket specified
  - Key Config:
    - Main configuration: `/etc/nginx/nginx.conf`
    - Security configuration: `/etc/nginx/conf.d/security.conf`
    - Available sites: `/etc/nginx/sites-available`
    - Enabled sites: `/etc/nginx/sites-enabled`
    - Secret directory: `/etc/nginx/secrets`
    - Service is enabled and started
    - Template changes trigger a delayed nginx reload

- **fail2ban**
  - Purpose: Host intrusion-prevention service
  - Location/Path: `/etc/fail2ban/jail.local`
  - Port/Socket: None
  - Key Config:
    - Package: `fail2ban`
    - Service: `fail2ban`
    - Enabled and started
    - Template changes trigger a delayed service restart

- **ufw**
  - Purpose: Host firewall
  - Location/Path: UFW system configuration
  - Port/Socket: Allows TCP `22`, `80`, and `443`
  - Key Config:
    - Default incoming policy: deny
    - Firewall state: enabled
    - Rules: SSH, HTTP, and HTTPS

- **sshd**
  - Purpose: Secure shell access
  - Location/Path: `/etc/ssh/sshd_config`
  - Port/Socket: TCP `22`
  - Key Config:
    - `PermitRootLogin no`
    - `PasswordAuthentication no`
    - Service is restarted only when SSH configuration changes

- **nginx site inventory**
  - Purpose: Site-specific document roots, virtual hosts, enabled links, and optional TLS
  - Location/Path: Defined by the `nginx_sites` data bag
  - Port/Socket: HTTP `80`; HTTPS `443` when `ssl_enabled` is true
  - Key Config:
    - Required fields: `id`, `document_root`, and `ssl_enabled`
    - Site names and values are not present in the supplied source
    - The complete data bag inventory must be obtained and represented explicitly in Ansible variables before migration

## File Structure

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb

Providers:
No provider files are used by the executed recipes.

Templates:
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb

Attributes:
cookbooks/nginx-multisite/attributes/default.rb

Files:
No static files are listed in the supplied directory listing.
```

The structural analysis mentions `resources/lineinfile.rb`, but it is not invoked by the execution tree and is excluded from this migration plan. The `nginx.rb` recipe references dynamic `cookbook_file` sources named `<site_folder>/index.html`, but those static source files were not provided.

## Module Explanation

The cookbook performs operations in this order:

### 1. `default` (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- Uses four `include_recipe` resources.
- The Ansible implementation must preserve this order:
  1. Host security
  2. nginx installation and base configuration
  3. TLS dependencies and certificate generation
  4. Site configuration and enablement

### 2. `security` (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs the `fail2ban` and `ufw` packages.
- Enables and starts `fail2ban`.
- Renders `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Delayed-restarts `fail2ban` when the jail template changes.
- Configures UFW in this order:
  1. Sets the default policy to deny.
  2. Allows SSH on `22/tcp`.
  3. Allows HTTP on `80/tcp`.
  4. Allows HTTPS on `443/tcp`.
  5. Enables UFW.
- The original commands are guarded by checks for `Default: deny`, `22/tcp`, `80/tcp`, `443/tcp`, and `Status: active`.
- The Ansible implementation should use idempotent `community.general.ufw` tasks.
- Renders `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Notifies `sysctl -p /etc/sysctl.d/99-security.conf` with a delayed action when the sysctl template changes.
- The sysctl reload action is otherwise disabled.
- When `security_ssh_disable_root` is true, changes `/etc/ssh/sshd_config` to:
  - `PermitRootLogin no`
- When `security_ssh_password_auth` is false, changes `/etc/ssh/sshd_config` to:
  - `PasswordAuthentication no`
- Delayed-restarts `sshd` when either SSH setting changes.
- Declares `service[sshd]` with action `nothing`.
- Resource totals:
  - One package declaration installing two packages
  - Two service declarations: `fail2ban` and `sshd`
  - Two templates
  - Eight execute resources:
    - `ufw_default_deny`
    - `ufw_allow_ssh`
    - `ufw_allow_http`
    - `ufw_allow_https`
    - `ufw_enable`
    - `reload_sysctl`
    - `disable root login`
    - `disable password auth`

### 3. `nginx` (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package without a pinned version.
- Renders `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Renders `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Delayed-reloads nginx when either nginx template changes.
- Enables and starts the `nginx` service.
- Supports nginx restart, reload, and status actions.
- Creates `/etc/nginx/secrets` with:
  - Owner: `root`
  - Group: `root`
  - Mode: `0700`
- Loads `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`.
- Writes the data bag `token` field to `/etc/nginx/secrets/site_token` with:
  - Owner: `root`
  - Group: `root`
  - Mode: `0600`
  - Sensitive logging enabled
- Reads the complete `nginx_sites` data bag.
- For every data bag item represented in the migration inventory:
  - Sets `site_name` from `site['id']`.
  - Creates `config['document_root']` recursively.
  - Assigns owner and group `nginx`.
  - Assigns directory mode `0755`.
  - Derives `site_folder` from the first component of `site_name` split at `.`.
  - Deploys `<document_root>/index.html` from `<site_folder>/index.html`.
  - Assigns the index file to owner and group `nginx` with mode `0644`.
- The supplied source does not provide the data bag item names, document roots, or SSL values. The Ansible implementation must replace this unresolved inventory with named site variables before deployment.
- Resource totals:
  - One package
  - Two templates
  - One service
  - One fixed directory plus one document-root directory per site
  - One secret file
  - One cookbook file per site

### 4. `ssl` (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs `openssl` and `ca-certificates` without pinned versions.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` with:
  - Owner: `root`
  - Group: `root`
  - Mode: `0755`
- Creates `/etc/ssl/private` with:
  - Owner: `root`
  - Group: `ssl-cert`
  - Mode: `0710`
- Reads the `nginx_sites` data bag.
- Processes only sites whose `ssl_enabled` value is true.
- Uses the derived variable `key_file` for the private-key path:
  - `/etc/ssl/private/<site_name>.key`
- Uses the certificate path:
  - `/etc/ssl/certs/<site_name>.crt`
- Generates a self-signed certificate with:
  - RSA 2048-bit key
  - Validity of 365 days
  - Subject common name equal to `<site_name>`
  - Subject values `C=US`, `ST=Example`, `L=Example`, `O=Example Org`, `OU=IT`, and `emailAddress=admin@example.com`
- The validation notes identify an apparent source-analysis discrepancy containing a duplicate `/L=Example` component. The migration should verify the full source and intentionally either preserve that duplicate or normalize it to the single locality component documented above.
- Sets generated private keys to:
  - Owner: `root`
  - Group: `ssl-cert`
  - Mode: `0640`
- Skips certificate generation when both certificate and private-key files already exist.
- Delayed-reloads nginx after certificate generation.
- Creates one certificate-generation execute resource per named SSL-enabled site, using the resource name `generate-ssl-cert-<site_name>`.
- The supplied source does not identify SSL-enabled site names. The Ansible inventory must explicitly enumerate them before implementation.

### 5. `sites` (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Creates `/etc/nginx/sites-available` with owner `root:root` and mode `0755`.
- Creates `/etc/nginx/sites-enabled` with owner `root:root` and mode `0755`.
- Reads the named site inventory derived from the `nginx_sites` data bag.
- Renders `cookbooks/nginx-multisite/templates/default/site.conf.erb` to `/etc/nginx/sites-available/<site_name>` with mode `0644`.
- Supplies these template variables:
  - `server_name`: `<site_name>`
  - `document_root`: configured document root
  - `ssl_enabled`: configured SSL setting
  - `cert_file`: `/etc/ssl/certs/<site_name>.crt`
  - `key_file`: `/etc/ssl/private/<site_name>.key`
- Delayed-reloads nginx when a site template changes.
- Creates `/etc/nginx/sites-enabled/<site_name>` as a link to `/etc/nginx/sites-available/<site_name>`.
- Delayed-reloads nginx when an enabled-site link changes.
- Deletes `/etc/nginx/sites-enabled/default` and delayed-reloads nginx after deletion.
- Resource totals:
  - Two directories
  - One site template per named site
  - One enabled-site link per named site
  - One default-site file deletion

## Attributes

`cookbooks/nginx-multisite/attributes/default.rb` defines:

| Chef Attribute | Value | Ansible Variable |
|---|---:|---|
| `node['nginx']['ssl']['certificate_path']` | `/etc/ssl/certs` | `nginx_ssl_certificate_path` |
| `node['nginx']['ssl']['private_key_path']` | `/etc/ssl/private` | `nginx_ssl_private_key_path` |
| `node['security']['fail2ban']['enabled']` | `true` | `security_fail2ban_enabled` |
| `node['security']['ufw']['enabled']` | `true` | `security_ufw_enabled` |
| `node['security']['ssh']['disable_root']` | `true` | `security_ssh_disable_root` |
| `node['security']['ssh']['password_auth']` | `false` | `security_ssh_password_auth` |

The cookbook does not define site instances in the attributes file. Site instances originate in the `nginx_sites` data bag.

## Dependencies

**External cookbook dependencies**: None declared in the supplied `metadata.rb`.

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

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Platform consideration**: The recipes explicitly create Debian-style nginx site directories. These directories may not be created by the nginx package on Fedora or CentOS.

## Credentials

**Detection Summary**: 2 sensitive credential categories detected in 2 recipe files; one category is an encrypted data bag secret and one category is locally generated TLS private keys.

**Source**:

- **Provider**: Chef encrypted data bag
- **Data bag**: `nginx_secrets`
- **Item**: `site`
- **Field**: `token`
- **Source file**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **URL**: Not applicable
- **Path**: `/etc/nginx/secrets/site_token`

### nginx Site Token

- **Variable(s)**: `token` field from `Chef::EncryptedDataBagItem.load('nginx_secrets', 'site')`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/nginx.rb`
- **Current storage**: Chef encrypted data bag
- **Usage context**: Written to `/etc/nginx/secrets/site_token`
- **File ownership**: `root:root`
- **File mode**: `0600`
- **Logging protection**: Chef file resource uses sensitive logging
- **Migration storage**: Ansible Vault or an AAP credential/secret-management integration
- **Migration requirement**: Do not store the plaintext token in the role repository or log its value

The exact Ruby local variable name is not confirmed by the supplied execution tree. The authoritative identity is the `token` field loaded from `nginx_secrets/site`.

### TLS Private Keys

- **Variable(s)**: `key_file` / `tls_private_key`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Locally generated self-signed private key
- **Usage context**: nginx TLS private key
- **Resolved path**: `/etc/ssl/private/<site_name>.key`
- **File ownership**: `root:ssl-cert`
- **File mode**: `0640`
- **Migration requirement**: Preserve restrictive permissions and do not log private-key content

TLS certificates and their subject values are not credentials. No HashiCorp Vault, CyberArk, AWS Secrets Manager, environment-variable secret references, hardcoded passwords, API keys, or database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/etc/nginx/nginx.conf`
- `/etc/nginx/conf.d/security.conf`
- `/etc/nginx/secrets/site_token`
- `/etc/nginx/sites-available`
- `/etc/nginx/sites-enabled`
- One `/etc/nginx/sites-available/<site_name>` file for every named site
- One `/etc/nginx/sites-enabled/<site_name>` link for every named site
- One `<document_root>/index.html` file for every named site
- One `/etc/ssl/certs/<site_name>.crt` file for every SSL-enabled site
- One `/etc/ssl/private/<site_name>.key` file for every SSL-enabled site

**Service endpoints to check**:

- SSH: TCP `22`
- HTTP: TCP `80`
- HTTPS: TCP `443` when enabled by the rendered site configuration
- Unix sockets: None specified

**Templates rendered**:

- `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` → `/etc/fail2ban/jail.local`: 1 render
- `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` → `/etc/nginx/nginx.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/security.conf.erb` → `/etc/nginx/conf.d/security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` → `/etc/sysctl.d/99-security.conf`: 1 render
- `cookbooks/nginx-multisite/templates/default/site.conf.erb` → one `/etc/nginx/sites-available/<site_name>` path per named `nginx_sites` item

The exact site render count cannot be calculated from the supplied source because the data bag item names and values were not included. Deployment must not proceed until the site inventory is obtained and substituted for the unresolved site placeholders.

## Pre-flight checks

```bash
# Validate installed packages
dpkg-query -W fail2ban ufw nginx openssl ca-certificates 2>/dev/null || \
rpm -q fail2ban ufw nginx openssl ca-certificates

# Service status checks
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx

systemctl status sshd
systemctl is-active sshd

# UFW policy and rules
ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
ufw status | grep 'Default: deny'

# SSH hardening
grep -E '^PermitRootLogin ' /etc/ssh/sshd_config
grep -E '^PasswordAuthentication ' /etc/ssh/sshd_config
sshd -t

# Sysctl validation
cat /etc/sysctl.d/99-security.conf
sysctl -p /etc/sysctl.d/99-security.conf

# nginx configuration validation
nginx -t
nginx -T

# Fixed nginx paths
ls -l /etc/nginx/nginx.conf
ls -l /etc/nginx/conf.d/security.conf
ls -ld /etc/nginx/secrets
ls -l /etc/nginx/secrets/site_token
ls -ld /etc/nginx/sites-available
ls -ld /etc/nginx/sites-enabled

# Secret permissions
stat -c '%U:%G %a %n' \
  /etc/nginx/secrets \
  /etc/nginx/secrets/site_token

# Required listening ports
ss -tlnp | grep -E ':(22|80|443)\b'
lsof -iTCP:80 -sTCP:LISTEN
lsof -iTCP:443 -sTCP:LISTEN

# Service logs
journalctl -u nginx --no-pager -n 100
journalctl -u fail2ban --no-pager -n 100
journalctl -u sshd --no-pager -n 100

# Fail2ban validation
fail2ban-client status

# Site inventory and link validation
find /etc/nginx/sites-available -maxdepth 1 -type f -ls
find /etc/nginx/sites-enabled -maxdepth 1 -type l -ls
find /etc/ssl/certs -maxdepth 1 -name '*.crt' -ls
find /etc/ssl/private -maxdepth 1 -name '*.key' -ls

# The default nginx site must be absent
test ! -e /etc/nginx/sites-enabled/default
```

After the complete `nginx_sites` inventory is obtained, create an individually named validation block for every exact site name containing:

```bash
test -d "<document_root>"
test -f "<document_root>/index.html"

test -f "/etc/nginx/sites-available/<site_name>"
test -L "/etc/nginx/sites-enabled/<site_name>"
readlink "/etc/nginx/sites-enabled/<site_name>"

grep -nE 'server_name|root|listen|ssl_certificate|ssl_certificate_key' \
  "/etc/nginx/sites-available/<site_name>"

curl -I -H "Host: <site_name>" http://127.0.0.1/
```

The link target must be:

```text
/etc/nginx/sites-available/<site_name>
```

For every named site whose `ssl_enabled` value is true, also run:

```bash
test -f "/etc/ssl/certs/<site_name>.crt"
test -f "/etc/ssl/private/<site_name>.key"

openssl x509 \
  -in "/etc/ssl/certs/<site_name>.crt" \
  -noout -subject -issuer -dates

stat -c '%U:%G %a %n' "/etc/ssl/private/<site_name>.key"

curl -k -I -H "Host: <site_name>" https://127.0.0.1/
```

Expected TLS private-key ownership and permissions:

```text
root:ssl-cert 640
```

The certificate subject must contain:

```text
CN=<site_name>
```

For publicly resolvable site names, additionally validate:

```bash
curl -I "http://<site_name>/"
curl -k -I "https://<site_name>/"
```

The final migration validation must replace `<site_name>` and `<document_root>` with the exact values obtained from the `nginx_sites` data bag.