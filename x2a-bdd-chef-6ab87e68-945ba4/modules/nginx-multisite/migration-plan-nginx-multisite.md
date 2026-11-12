---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: This cookbook configures nginx with three SSL-enabled virtual sites: `test.cluster.local`, `ci.cluster.local`, and `status.cluster.local`. It installs nginx, fail2ban, UFW, OpenSSL, and CA certificates; applies nginx, kernel, firewall, and SSH hardening; generates local self-signed certificates; deploys static site content; configures HTTP-to-HTTPS redirects; and enables the fail2ban, UFW, nginx, and SSH service behaviors. The Ansible migration must preserve the Chef recipe order, conditional execution, delayed handlers, ownership, permissions, paths, and all three site definitions.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

- **test.cluster.local**: SSL-enabled nginx virtual host serving static test content
  - Location/Path: `/opt/server/test`
  - Port/Socket: HTTP `80`; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/test.cluster.local.crt`; key `/etc/ssl/private/test.cluster.local.key`; site configuration `/etc/nginx/sites-available/test.cluster.local`; enabled link `/etc/nginx/sites-enabled/test.cluster.local`; content `/opt/server/test/index.html`

- **ci.cluster.local**: SSL-enabled nginx virtual host serving static CI content
  - Location/Path: `/opt/server/ci`
  - Port/Socket: HTTP `80`; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/ci.cluster.local.crt`; key `/etc/ssl/private/ci.cluster.local.key`; site configuration `/etc/nginx/sites-available/ci.cluster.local`; enabled link `/etc/nginx/sites-enabled/ci.cluster.local`; content `/opt/server/ci/index.html`

- **status.cluster.local**: SSL-enabled nginx virtual host serving static status content
  - Location/Path: `/opt/server/status`
  - Port/Socket: HTTP `80`; HTTPS `443` with HTTP/2
  - Key Config: Certificate `/etc/ssl/certs/status.cluster.local.crt`; key `/etc/ssl/private/status.cluster.local.key`; site configuration `/etc/nginx/sites-available/status.cluster.local`; enabled link `/etc/nginx/sites-enabled/status.cluster.local`; content `/opt/server/status/index.html`

Security configuration includes:

- `fail2ban`
- `ufw`
- `ssh`

Default attributes to preserve:

```yaml
nginx:
  sites:
    test.cluster.local:
      document_root: /opt/server/test
      ssl_enabled: true
    ci.cluster.local:
      document_root: /opt/server/ci
      ssl_enabled: true
    status.cluster.local:
      document_root: /opt/server/status
      ssl_enabled: true
  ssl:
    certificate_path: /etc/ssl/certs
    private_key_path: /etc/ssl/private

security:
  fail2ban:
    enabled: true
  ufw:
    enabled: true
  ssh:
    disable_root: true
    password_auth: false
```

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
├── resources/
├── templates/
│   └── default/
│       ├── fail2ban.jail.local.erb
│       ├── nginx.conf.erb
│       ├── security.conf.erb
│       ├── site.conf.erb
│       └── sysctl-security.conf.erb
└── files/
    └── default/
```

No provider file is used by the execution tree. A `resources/lineinfile.rb` custom resource was mentioned in structural analysis but is not present in the supplied execution tree and is not used by an executed resource.

No static files under `files/default/` or `files/` were supplied. The migration must provide equivalent source content for:

```text
test/index.html
ci/index.html
status/index.html
```

The deployed destinations and ownership must remain unchanged.

## Module Explanation

The cookbook performs operations in this order:

1. `security`
2. `nginx`
3. `ssl`
4. `sites`

### 1. Default entry recipe (`cookbooks/nginx-multisite/recipes/default.rb`)

- Includes `nginx-multisite::security`.
- Includes `nginx-multisite::nginx`.
- Includes `nginx-multisite::ssl`.
- Includes `nginx-multisite::sites`.
- The Ansible imports or includes must retain this exact order.

### 2. Security recipe (`cookbooks/nginx-multisite/recipes/security.rb`)

- Installs `fail2ban` and `ufw`.
- Enables and starts `fail2ban`.
- Deploys `cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb` to `/etc/fail2ban/jail.local` with mode `0644`.
- Preserves the configured SSH, nginx HTTP-authentication, nginx request-limit, and nginx bot-search jails.
- Restarts fail2ban through a delayed handler only when the jail configuration changes.
- Sets the UFW default incoming policy to deny.
- Allows TCP ports `22`, `80`, and `443`.
- Enables UFW non-interactively after the allow rules are present.
- Deploys `cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb` to `/etc/sysctl.d/99-security.conf` with mode `0644`.
- Applies the configured reverse-path filtering, redirect suppression, source-route suppression, martian logging, ICMP restrictions, IPv6 disablement, and TCP SYN protection settings.
- Runs `sysctl -p /etc/sysctl.d/99-security.conf` through a delayed handler only when the sysctl template changes.
- Sets `PermitRootLogin no` in `/etc/ssh/sshd_config` because `disable_root` is `true`.
- Sets `PasswordAuthentication no` because `password_auth` is `false`.
- Restarts SSH through a delayed handler only when either SSH setting changes.
- Resource counts: `package` 2 names, `service` 2, `template` 2, `execute` 8.

### 3. nginx installation and base configuration (`cookbooks/nginx-multisite/recipes/nginx.rb`)

- Installs the `nginx` package.
- Deploys `cookbooks/nginx-multisite/templates/default/nginx.conf.erb` to `/etc/nginx/nginx.conf` with mode `0644`.
- Preserves the nginx user, automatic worker processes, PID path, worker connections, log paths, gzip, and included `conf.d` and `sites-enabled` paths.
- Deploys `cookbooks/nginx-multisite/templates/default/security.conf.erb` to `/etc/nginx/conf.d/security.conf` with mode `0644`.
- Preserves nginx server-token hiding, request-rate zones, request-size limits, timeout values, TLS session settings, TLS protocols, configured cipher list, and preferred server ciphers.
- Enables and starts nginx.
- Uses a delayed reload handler for changes to nginx configuration, certificates, virtual hosts, links, and removal of the default site.
- Creates document roots and static files for exactly these three iterations:
  - `test.cluster.local`: `/opt/server/test`, source `test/index.html`, destination `/opt/server/test/index.html`
  - `ci.cluster.local`: `/opt/server/ci`, source `ci/index.html`, destination `/opt/server/ci/index.html`
  - `status.cluster.local`: `/opt/server/status`, source `status/index.html`, destination `/opt/server/status/index.html`
- Creates each document root recursively with owner `nginx`, group `nginx`, and mode `0755`.
- Deploys each index file with owner `nginx`, group `nginx`, and mode `0644`.
- Resource counts: `package` 1, `template` 2, `service` 1, document-root directory iterations 3, static-file iterations 3.

### 4. SSL package and certificate generation (`cookbooks/nginx-multisite/recipes/ssl.rb`)

- Installs `openssl` and `ca-certificates`.
- Creates the `ssl-cert` group.
- Creates `/etc/ssl/certs` with owner `root`, group `root`, and mode `0755`.
- Creates `/etc/ssl/private` with owner `root`, group `ssl-cert`, and mode `0710`.
- Generates certificates for exactly these three iterations:
  - `test.cluster.local`: `/etc/ssl/certs/test.cluster.local.crt` and `/etc/ssl/private/test.cluster.local.key`
  - `ci.cluster.local`: `/etc/ssl/certs/ci.cluster.local.crt` and `/etc/ssl/private/ci.cluster.local.key`
  - `status.cluster.local`: `/etc/ssl/certs/status.cluster.local.crt` and `/etc/ssl/private/status.cluster.local.key`
- Generates RSA `2048` certificates valid for `365` days.
- Uses subjects with country `US`, state and locality `Example`, organization `Example Org`, organizational unit `IT`, the site-specific common name, and email `admin@example.com`.
- Skips generation when both the certificate and key already exist.
- Sets each private key to owner `root`, group `ssl-cert`, and mode `0640`.
- Triggers a delayed nginx reload when a certificate or key is generated.
- Resource counts: `package` 2 names, `group` 1, `directory` 2, certificate-generation `execute` iterations 3.

### 5. Site directories, virtual hosts, links, and default-site removal (`cookbooks/nginx-multisite/recipes/sites.rb`)

- Creates `/etc/nginx/sites-available` with owner `root`, group `root`, and mode `0755`.
- Creates `/etc/nginx/sites-enabled` with owner `root`, group `root`, and mode `0755`.
- The structured analysis reports three directory-resource iterations associated with the site collection; the migration must preserve the analyzed iteration behavior while ensuring the two required nginx site directories exist before templates and links are created.
- Deploys `cookbooks/nginx-multisite/templates/default/site.conf.erb` three times:
  - `test.cluster.local`: document root `/opt/server/test`, certificate `/etc/ssl/certs/test.cluster.local.crt`, key `/etc/ssl/private/test.cluster.local.key`
  - `ci.cluster.local`: document root `/opt/server/ci`, certificate `/etc/ssl/certs/ci.cluster.local.crt`, key `/etc/ssl/private/ci.cluster.local.key`
  - `status.cluster.local`: document root `/opt/server/status`, certificate `/etc/ssl/certs/status.cluster.local.crt`, key `/etc/ssl/private/status.cluster.local.key`
- Writes the three templates with mode `0644`.
- Creates these enabled-site links:
  - `/etc/nginx/sites-enabled/test.cluster.local` → `/etc/nginx/sites-available/test.cluster.local`
  - `/etc/nginx/sites-enabled/ci.cluster.local` → `/etc/nginx/sites-available/ci.cluster.local`
  - `/etc/nginx/sites-enabled/status.cluster.local` → `/etc/nginx/sites-available/status.cluster.local`
- Removes `/etc/nginx/sites-enabled/default` when present.
- Preserves HTTP port `80`, HTTP-to-HTTPS redirects, HTTPS port `443`, HTTP/2, HSTS, security headers, gzip, `try_files`, missing-file `404` responses, sensitive-path blocking, and site-specific access and error logs.
- Resource counts: `directory` 3 analyzed iterations, `template` 3, `link` 3, `file` 1.

## Dependencies

**External cookbook dependencies**: None listed.

**System package dependencies**:

- `nginx`
- `fail2ban`
- `ufw`
- `openssl`
- `ca-certificates`

**Service dependencies**:

- `fail2ban`: enabled and started; restarted when `/etc/fail2ban/jail.local` changes
- `nginx`: enabled and started; reloaded after configuration, certificate, virtual-host, link, or default-site changes
- `sshd`: restarted when SSH hardening settings change

**Firewall rules**:

- `22/tcp` for SSH
- `80/tcp` for HTTP
- `443/tcp` for HTTPS

## Credentials

**Detection Summary**: No application credentials, passwords, API tokens, data bags, vault lookups, or secret-manager integrations were detected. Three locally generated TLS private keys and one non-secret certificate subject email were identified.

**Source**:

- **Provider**: None detected
- **URL**: None
- **Path**: None

### Generated TLS private keys

- **Variable(s)/Path(s)**:
  - `/etc/ssl/private/test.cluster.local.key`
  - `/etc/ssl/private/ci.cluster.local.key`
  - `/etc/ssl/private/status.cluster.local.key`
- **Source file(s)**:
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Locally generated files; not stored in a data bag, vault, environment variable, or secret manager
- **Usage context**: TLS private keys for the three nginx HTTPS virtual hosts
- **Permissions**: Owner `root`, group `ssl-cert`, mode `0640`; parent directory mode `0710`

### Self-signed certificate subject email

- **Variable(s)**: `admin@example.com`
- **Source file(s)**: `cookbooks/nginx-multisite/recipes/ssl.rb`
- **Current storage**: Hardcoded certificate subject metadata
- **Usage context**: Subject email in each generated self-signed certificate
- **Credential status**: Not a password, token, or authentication secret

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, `node['vault']`, `node['secrets']`, or environment-variable secret references were detected.

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
- `/etc/nginx/sites-enabled/default`
- `/etc/ssl/certs/test.cluster.local.crt`
- `/etc/ssl/certs/ci.cluster.local.crt`
- `/etc/ssl/certs/status.cluster.local.crt`
- `/etc/ssl/private/test.cluster.local.key`
- `/etc/ssl/private/ci.cluster.local.key`
- `/etc/ssl/private/status.cluster.local.key`
- `/opt/server/test/index.html`
- `/opt/server/ci/index.html`
- `/opt/server/status/index.html`
- `/etc/fail2ban/jail.local`
- `/etc/sysctl.d/99-security.conf`
- `/etc/ssh/sshd_config`
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`
- `/var/log/nginx/test.cluster.local_access.log`
- `/var/log/nginx/test.cluster.local_error.log`
- `/var/log/nginx/ci.cluster.local_access.log`
- `/var/log/nginx/ci.cluster.local_error.log`
- `/var/log/nginx/status.cluster.local_access.log`
- `/var/log/nginx/status.cluster.local_error.log`

**Service endpoints to check**:

- `test.cluster.local`: HTTP `80`, HTTPS `443`
- `ci.cluster.local`: HTTP `80`, HTTPS `443`
- `status.cluster.local`: HTTP `80`, HTTPS `443`
- SSH: TCP `22`

**Unix sockets**: None configured.

**Network interfaces**: No specific bind address; nginx uses the default listeners on ports `80` and `443`.

**Templates rendered**:

- `fail2ban.jail.local.erb`: 1 time
- `nginx.conf.erb`: 1 time
- `security.conf.erb`: 1 time
- `sysctl-security.conf.erb`: 1 time
- `site.conf.erb`: 3 times
  - `test.cluster.local`
  - `ci.cluster.local`
  - `status.cluster.local`

## Pre-flight checks

```bash
# Package and service status
dpkg -l nginx fail2ban ufw openssl ca-certificates 2>/dev/null || \
rpm -q nginx fail2ban ufw openssl ca-certificates

systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-enabled fail2ban
systemctl is-active fail2ban
systemctl is-active sshd || systemctl is-active ssh

# Configuration validation
nginx -t
sshd -t
ufw status verbose
sysctl -p /etc/sysctl.d/99-security.conf

grep -E 'worker_processes|worker_connections|access_log|error_log|gzip on|sites-enabled' \
  /etc/nginx/nginx.conf

grep -E 'server_tokens|limit_req_zone|client_max_body_size|ssl_protocols|ssl_ciphers' \
  /etc/nginx/conf.d/security.conf

# Shared directories and configuration files
test -d /etc/nginx/sites-available
test -d /etc/nginx/sites-enabled
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf
test -f /etc/ssh/sshd_config
test ! -e /etc/nginx/sites-enabled/default

# test.cluster.local
test -d /opt/server/test
test -f /opt/server/test/index.html
test -f /etc/nginx/sites-available/test.cluster.local
test -L /etc/nginx/sites-enabled/test.cluster.local
test -f /etc/ssl/certs/test.cluster.local.crt
test -f /etc/ssl/private/test.cluster.local.key
curl -I -H 'Host: test.cluster.local' http://127.0.0.1/
curl -k -I --resolve test.cluster.local:443:127.0.0.1 \
  https://test.cluster.local/

# ci.cluster.local
test -d /opt/server/ci
test -f /opt/server/ci/index.html
test -f /etc/nginx/sites-available/ci.cluster.local
test -L /etc/nginx/sites-enabled/ci.cluster.local
test -f /etc/ssl/certs/ci.cluster.local.crt
test -f /etc/ssl/private/ci.cluster.local.key
curl -I -H 'Host: ci.cluster.local' http://127.0.0.1/
curl -k -I --resolve ci.cluster.local:443:127.0.0.1 \
  https://ci.cluster.local/

# status.cluster.local
test -d /opt/server/status
test -f /opt/server/status/index.html
test -f /etc/nginx/sites-available/status.cluster.local
test -L /etc/nginx/sites-enabled/status.cluster.local
test -f /etc/ssl/certs/status.cluster.local.crt
test -f /etc/ssl/private/status.cluster.local.key
curl -I -H 'Host: status.cluster.local' http://127.0.0.1/
curl -k -I --resolve status.cluster.local:443:127.0.0.1 \
  https://status.cluster.local/

# Certificate and key permissions
stat -c '%U:%G %a %n' \
  /etc/ssl/private/test.cluster.local.key \
  /etc/ssl/private/ci.cluster.local.key \
  /etc/ssl/private/status.cluster.local.key

# Firewall rules
ufw status | grep -E '22/tcp|80/tcp|443/tcp'
```