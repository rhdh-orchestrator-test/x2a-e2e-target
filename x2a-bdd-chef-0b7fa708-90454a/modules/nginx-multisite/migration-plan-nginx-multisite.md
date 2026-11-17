---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Migrate the `nginx-multisite` Chef cookbook to an Ansible role while preserving its recipe execution order, package resources, Nginx configuration, security configuration, SSL handling, and dynamically generated site configuration. The supplied execution analysis confirms the five recipes, referenced templates, package/resource names, absence of providers, and dynamic `nginx_sites` iteration. It does not provide the actual site data bag items, template contents, attribute contents, metadata, or complete resource properties; those items must be verified before implementation.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:

No exact site instance names are available in the supplied analysis. Site definitions are loaded dynamically from the `nginx_sites` Chef data bag. The data bag must be exported before migration, and every item must become an explicitly named Ansible site variable.

Each exported site entry must provide:

- **Site name**: `site['id']`
- **Document root**: `site['document_root']`
- **SSL enabled**: `site['ssl_enabled']`
- **Certificate path**: `/etc/ssl/certs/<site_name>.crt`
- **Private key path**: `/etc/ssl/private/<site_name>.key`
- **Nginx configuration**: `/etc/nginx/sites-available/<site_name>`
- **Enabled-site link**: `/etc/nginx/sites-enabled/<site_name>`

The supplied analysis identifies these network endpoints:

- HTTP: TCP port `80`
- HTTPS: TCP port `443`
- SSH administration: TCP port `22`

The exact HTTP, HTTPS, and certificate behavior must be confirmed from `site.conf.erb` and the exported site definitions before migration.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

### Recipes

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

### Providers

```text
```

No provider files are used by the supplied execution tree.

### Templates

```text
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

### Attributes

```text
cookbooks/nginx-multisite/attributes/default.rb
```

### Files

```text
```

No static `files/default/*` or `files/*` files are listed in the supplied cookbook structure. Dynamic site content referenced by `cookbook_file` is not present in the supplied directory listing.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Includes `nginx-multisite::security`.
   - Includes `nginx-multisite::nginx`.
   - Includes `nginx-multisite::ssl`.
   - Includes `nginx-multisite::sites`.

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs the `fail2ban` and `ufw` packages.
   - Declares the `fail2ban` service.
   - References `fail2ban.jail.local.erb`.
   - References `sysctl-security.conf.erb`.
   - Configures UFW resources and SSH hardening resources according to the recipe.
   - Exact file modes, ownership, notification behavior, and attribute conditionals require verification from the recipe and template contents.

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs the `nginx` package.
   - References `nginx.conf.erb`.
   - References `security.conf.erb`.
   - Declares the Nginx service.
   - Creates the Nginx secrets directory and site directories identified by the recipe.
   - Loads and iterates over the `nginx_sites` data bag.
   - Creates dynamic site document roots and dynamic `index.html` files.
   - The claimed encrypted data bag source for `/etc/nginx/secrets/site_token` is not explicitly evidenced by the supplied structured analysis and must be verified.

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs the `openssl` and `ca-certificates` packages.
   - Creates the `ssl-cert` group.
   - Creates certificate and private-key directories.
   - Iterates over SSL-enabled entries from the `nginx_sites` data bag.
   - Generates or manages site certificates and private keys according to the recipe.
   - Exact certificate-generation commands, idempotence conditions, ownership, modes, and notifications require verification.

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates the Nginx `sites-available` and `sites-enabled` directories.
   - Iterates over the named `nginx_sites` data bag entries.
   - Renders `site.conf.erb` for every exported site item.
   - Creates the corresponding enabled-site link.
   - Removes the default enabled site when present.
   - Exact symlink targets, template variables, modes, and notification behavior require verification.

### Dynamic site iterations

The supplied execution tree confirms dynamic iteration over `nginx_sites`, but does not provide item names. No site loop can be expanded with actual names until the data bag is exported.

Required migration inputs:

```yaml
nginx_sites:
  - id: "<verified-site-id>"
    document_root: "<verified-document-root>"
    ssl_enabled: "<verified-boolean>"
```

The final Ansible plan must replace these placeholders with one explicitly named entry per exported data bag item.

## Dependencies

**External cookbook dependencies**: Not verifiable because `metadata.rb` was not included in the supplied analysis.

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

**Data dependencies**:

- Standard Chef data bag: `nginx_sites`
- Claimed encrypted data bag: `nginx_secrets`, item `site`; usage is not explicitly evidenced by the supplied structured analysis and must be verified.

**Platform dependencies**: Platform support claims are not verifiable because `metadata.rb` was not included in the supplied analysis.

## Credentials

**Detection Summary**: 0 credentials verified by the supplied structured analysis. One site-token secret and locally generated TLS material are claimed by the original plan but require source verification.

### Nginx site token

- **Variable**: Claimed as `site_secret['token']`; not verified by the supplied structured analysis.
- **Source file**: Claimed as `cookbooks/nginx-multisite/recipes/nginx.rb`.
- **Current storage**: Claimed Chef encrypted data bag.
- **Data bag**: Claimed `nginx_secrets`, item `site`.
- **Usage context**: Claimed destination `/etc/nginx/secrets/site_token`.
- **Migration handling**: Verify the data bag load and token field. If confirmed, store the value in Ansible Vault or an approved external secret provider and deploy it with root ownership and mode `0600`.

### Nginx site definitions

- **Variables**: `site['id']`, `site['document_root']`, `site['ssl_enabled']`
- **Source files**:
  - `cookbooks/nginx-multisite/recipes/nginx.rb`
  - `cookbooks/nginx-multisite/recipes/ssl.rb`
  - `cookbooks/nginx-multisite/recipes/sites.rb`
- **Current storage**: Standard `nginx_sites` Chef data bag
- **Usage context**:
  - Site names
  - Document roots
  - SSL selection
  - Virtual-host variables
  - Dynamic static-content paths
- **Sensitive status**: Not classified as a secret by the supplied analysis.
- **Migration handling**: Export and explicitly enumerate every data bag item in controlled Ansible variables.

### TLS private keys and certificates

The original plan claims that TLS keys and certificates are generated locally from site names. The supplied structured analysis does not verify the generation commands, paths, permissions, or validity period. Confirm these details in `ssl.rb` before migrating them to Ansible crypto modules or an approved certificate-management process.

## Checks for the Migration

**Files to verify**:

```text
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
cookbooks/nginx-multisite/attributes/default.rb
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

Runtime paths identified by the original plan and requiring verification:

```text
/etc/nginx/nginx.conf
/etc/nginx/conf.d/security.conf
/etc/fail2ban/jail.local
/etc/sysctl.d/99-security.conf
/etc/nginx/secrets
/etc/nginx/secrets/site_token
/etc/nginx/sites-available
/etc/nginx/sites-enabled
/etc/ssl/certs
/etc/ssl/private
```

Per-site runtime paths cannot be listed by exact name until the `nginx_sites` data bag is exported.

**Service endpoints to check**:

- TCP port `22`
- TCP port `80`
- TCP port `443`
- Nginx PID path, if confirmed by `nginx.conf`
- No Unix socket is identified by the supplied analysis

**Templates rendered**:

- `fail2ban.jail.local.erb`: expected once; destination must be verified.
- `nginx.conf.erb`: expected once; destination must be verified.
- `security.conf.erb`: expected once; destination must be verified.
- `sysctl-security.conf.erb`: expected once; destination must be verified.
- `site.conf.erb`: once per explicitly exported `nginx_sites` item; exact count is unavailable.
- Dynamic site `index.html` content: once per explicitly exported site item; source files are not present in the supplied directory listing.

## Pre-flight checks

Run the following after the Ansible role completes and after all site names and template properties have been verified:

```bash
systemctl status fail2ban
systemctl is-enabled fail2ban
systemctl is-active fail2ban

systemctl status nginx
systemctl is-enabled nginx
systemctl is-active nginx

systemctl status sshd

ufw status verbose
ufw status | grep -E '22/tcp|80/tcp|443/tcp'

nginx -t
ss -tlnp | grep -E ':(22|80|443)\b'

test -f /etc/nginx/nginx.conf
test -f /etc/nginx/conf.d/security.conf
test -f /etc/fail2ban/jail.local
test -f /etc/sysctl.d/99-security.conf
test -d /etc/nginx/sites-available
test -d /etc/nginx/sites-enabled
test -d /etc/ssl/certs
test -d /etc/ssl/private
```

Verify the following before declaring the migration complete:

- All five recipes execute in the order `security`, `nginx`, `ssl`, `sites`.
- All packages named in the recipes are installed.
- All five referenced templates are rendered at their verified destinations.
- Every `nginx_sites` data bag item is represented by an explicitly named Ansible site entry.
- Every named site has its verified document root and Nginx configuration.
- Every SSL-enabled site has its verified certificate and private-key paths.
- Every enabled-site link resolves to its corresponding available-site configuration.
- Nginx configuration validation succeeds.
- Fail2ban, Nginx, and SSH services have the expected states.
- UFW rules and SSH hardening match the verified recipe and attribute behavior.
- Secret handling matches the verified Chef data bag implementation, if the claimed token source is confirmed.