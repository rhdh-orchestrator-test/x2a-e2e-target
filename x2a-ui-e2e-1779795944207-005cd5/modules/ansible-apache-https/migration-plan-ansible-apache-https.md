---
source-path: chef-and-ansible/website_https.yml
---

Now I'll create a detailed migration plan based on the file I've analyzed:

# Migration Plan: ansible-apache-https

**TLDR**: This role configures an Apache web server with HTTPS support using a self-signed certificate. Key modernization needs include updating module syntax to FQCN format, fixing boolean representations, quoting octal modes, adding idempotency to command modules, and structuring the playbook as a proper Ansible role.

## Service Type and Configuration

**Service Type**: Web Server (Apache with HTTPS)

**Key Operations**:
- Installs Apache web server and SSL dependencies
- Generates self-signed SSL certificates
- Configures a virtual host for HTTPS
- Deploys a simple "Hello World" website
- Enables SSL module in Apache
- Manages Apache service

## File Structure

**Task Files:**
- chef-and-ansible/website_https.yml (currently a standalone playbook, not a role)

**Handler Files:**
- Handlers are embedded in the playbook

**Variable Files:**
- Variables are embedded in the playbook

**Meta:**
- None (needs to be created)

**Templates:**
- None (using inline templates via variables)

**Static Files:**
- None (content is generated inline)

## Module Explanation

The role performs operations in this order:

1. **Package Installation** (`chef-and-ansible/website_https.yml`):
   - Updates apt cache
   - Installs Apache web server with specific version
   - Installs dependencies (curl, openssl, PyOpenSSL)
   - Legacy patterns: short module names, unquoted boolean values
   - Modern equivalent: Use FQCN module names, quoted boolean values

2. **SSL Certificate Generation** (`chef-and-ansible/website_https.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: short module names, unquoted file modes
   - Modern equivalent: Use FQCN module names, quoted file modes

3. **Apache Configuration** (`chef-and-ansible/website_https.yml`):
   - Creates virtual host configuration
   - Creates web content directory
   - Deploys website content
   - Legacy patterns: short module names, unquoted file modes
   - Modern equivalent: Use FQCN module names, quoted file modes

4. **Apache Site Management** (`chef-and-ansible/website_https.yml`):
   - Disables default site
   - Enables custom site
   - Enables SSL module
   - Legacy patterns: non-idempotent command modules, missing changed_when
   - Modern equivalent: Use FQCN module names, add changed_when or replace with idempotent modules

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal mode |
| `command: a2dissite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| `command: a2ensite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| `command: a2enmod` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| Inline templates | Separate template files | website_https.yml | Structure |
| Standalone playbook | Role structure | website_https.yml | Structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"

**Role dependencies**: None

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

The current playbook uses inline templates via variables. These should be moved to separate template files:

- **templates/helloworld.conf.j2**: Apache virtual host configuration
- **templates/index.html.j2**: Website content

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache version to install
- `website_domain`: string, default "myhost", Domain name for the website
- `website_root`: string, default "/var/www/helloworld", Website document root
- `ssl_cert_dir`: string, default "/etc/apache2/certs", Directory for SSL certificates
- `ssl_key_path`: string, default "/etc/apache2/certs/apache.key", Path to SSL key
- `ssl_csr_path`: string, default "/etc/apache2/certs/apache.csr", Path to SSL CSR
- `ssl_cert_path`: string, default "/etc/apache2/certs/apache.crt", Path to SSL certificate

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml
- templates/helloworld.conf.j2
- templates/index.html.j2

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/helloworld.conf.j2
- templates/index.html.j2

## Pre-flight checks:
- Verify Apache installation: `systemctl status apache2`
- Verify SSL module: `apache2ctl -M | grep ssl`
- Verify virtual host configuration: `apache2ctl -S`
- Verify SSL certificate: `openssl x509 -in /etc/apache2/certs/apache.crt -text -noout`
- Test HTTPS connection: `curl -k https://localhost`
- Validate Apache configuration: `apache2ctl configtest`