---
source-path: chef-and-ansible/website_https.yml
---

Now I'll create a detailed migration plan based on the website_https.yml file:

# Migration Plan: apache-https-website

**TLDR**: This role configures an Apache web server with HTTPS support using a self-signed certificate. It needs modernization from a playbook format to a proper Ansible role structure with fully qualified collection names (FQCN), proper boolean syntax, quoted file modes, and improved idempotency for command modules.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server and SSL dependencies
- Generates self-signed SSL certificates
- Configures a virtual host for HTTPS
- Creates a simple "Hello World" website
- Enables SSL module and the custom virtual host
- Disables the default virtual host

## File Structure

**IMPORTANT: The source is a standalone playbook (website_https.yml), not a role. We need to create a proper role structure.**

For the new role structure:
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
templates/virtualhost.conf.j2
templates/index.html.j2
```

## Module Explanation

The role performs operations in this order:

1. **Package Installation** (to be placed in `tasks/main.yml`):
   - Updates apt cache
   - Installs Apache with a specific version
   - Installs dependencies (curl, openssl, PyOpenSSL)
   - Legacy patterns: short module names, unquoted boolean, no FQCN
   - Modern equivalent: Use FQCN, proper boolean syntax, package module with lists

2. **SSL Certificate Generation** (to be placed in `tasks/main.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: short module names, unquoted file modes
   - Modern equivalent: Use FQCN, quoted file modes

3. **Website Configuration** (to be placed in `tasks/main.yml`):
   - Creates virtual host configuration
   - Creates website directory
   - Deploys website content
   - Legacy patterns: short module names, unquoted file modes, inline templates
   - Modern equivalent: Use FQCN, quoted file modes, separate template files

4. **Apache Configuration** (to be placed in `tasks/main.yml`):
   - Disables default site
   - Enables custom site
   - Enables SSL module
   - Legacy patterns: non-idempotent command modules, no changed_when
   - Modern equivalent: Use apache2_module and apache2_site modules for idempotency

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | tasks/main.yml | FQCN |
| `file:` | `ansible.builtin.file:` | tasks/main.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | tasks/main.yml | FQCN |
| `command:` | `ansible.builtin.command:` | tasks/main.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | tasks/main.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | tasks/main.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | tasks/main.yml | FQCN |
| `update_cache=true` | `update_cache: true` | tasks/main.yml | Boolean syntax |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted file modes |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted file modes |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted file modes |
| `command: a2dissite` | `community.general.apache2_site:` | tasks/main.yml | Idempotent module |
| `command: a2ensite` | `community.general.apache2_site:` | tasks/main.yml | Idempotent module |
| `command: a2enmod` | `community.general.apache2_module:` | tasks/main.yml | Idempotent module |
| Inline templates | External template files | tasks/main.yml | Move to template files |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.general: ">=3.0.0"
- community.crypto: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **virtualhost.conf.j2**: Create from inline `conftext` variable, use proper Jinja2 syntax
- **index.html.j2**: Create from inline `webtext` variable, fix HTML syntax error in the title tag

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache version to install
- `website_name`: string, default "helloworld", Name of the website
- `website_root`: string, default "/var/www/helloworld", Document root path
- `ssl_cert_path`: string, default "/etc/apache2/certs", Path for SSL certificates
- `ssl_common_name`: string, default "myhost", Common name for SSL certificate

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- templates/virtualhost.conf.j2
- templates/index.html.j2

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2
- templates/index.html.j2

## Pre-flight checks:
- Verify Apache installation: `systemctl status apache2`
- Verify SSL module: `apache2ctl -M | grep ssl`
- Verify virtual host: `apache2ctl -S`
- Verify SSL certificate: `openssl x509 -in /etc/apache2/certs/apache.crt -text -noout`
- Test HTTPS connection: `curl -k https://localhost/`