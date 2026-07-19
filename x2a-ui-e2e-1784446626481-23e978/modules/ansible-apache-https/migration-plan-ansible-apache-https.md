---
source-path: chef-and-ansible
---

Based on the files I've examined, I'll now create a migration plan for converting the Apache HTTPS configuration from the playbook format to a proper Ansible role structure.

# Migration Plan: ansible-apache-https

**TLDR**: This migration converts an Apache HTTPS configuration playbook into a modern Ansible role. The playbook installs and configures Apache with SSL/TLS support, creates a self-signed certificate, and deploys a simple website. Key modernization needs include FQCN conversion, loop modernization, proper directory structure, and argument specifications.

## Service Type and Configuration

**Service Type**: Web Server (Apache with HTTPS)

**Key Operations**:
- Installs Apache web server (version 2.4.41-4ubuntu3.10)
- Installs supporting packages (curl, openssl, python3-openssl)
- Generates self-signed SSL certificates
- Configures Apache virtual host for HTTPS
- Deploys a simple "Hello World" website
- Enables SSL module and disables default site
- Hardens SSL configuration to prevent POODLE vulnerability

## File Structure

**IMPORTANT: The original structure is a flat playbook, not a proper role. The migration will create the following role structure:**

```
tasks/main.yml
tasks/install.yml
tasks/ssl_certificates.yml
tasks/website.yml
tasks/security.yml
handlers/main.yml
templates/helloworld.conf.j2
templates/index.html.j2
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
```

**Task Files:**
tasks/main.yml
tasks/install.yml
tasks/ssl_certificates.yml
tasks/website.yml
tasks/security.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml

**Meta:**
meta/main.yml
meta/argument_specs.yml

**Templates:**
templates/helloworld.conf.j2
templates/index.html.j2

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **main.yml** (`tasks/main.yml`):
   - Includes other task files in logical order
   - Legacy pattern: Flat playbook structure
   - Modern equivalent: Modular task files with includes
   - Ansible module mapping: N/A (structural change)

2. **install.yml** (`tasks/install.yml`):
   - Updates apt cache
   - Installs Apache and supporting packages
   - Legacy patterns: Short module names, unquoted boolean values, non-loop package installation
   - Modern equivalent: FQCN module names, quoted boolean values, loop for package installation
   - Ansible module mapping: `apt:` → `ansible.builtin.apt:`

3. **ssl_certificates.yml** (`tasks/ssl_certificates.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: Short module names, unquoted file modes
   - Modern equivalent: FQCN module names, quoted file modes
   - Ansible module mapping: 
     - `file:` → `ansible.builtin.file:`
     - `openssl_privatekey:` → `community.crypto.openssl_privatekey:`
     - `openssl_csr:` → `community.crypto.openssl_csr:`
     - `openssl_certificate:` → `community.crypto.openssl_certificate:`

4. **website.yml** (`tasks/website.yml`):
   - Configures Apache virtual host
   - Creates website directory
   - Deploys website content
   - Legacy patterns: Short module names, unquoted file modes, hardcoded content
   - Modern equivalent: FQCN module names, quoted file modes, templates
   - Ansible module mapping: 
     - `copy:` → `ansible.builtin.copy:` or `ansible.builtin.template:`
     - `file:` → `ansible.builtin.file:`

5. **security.yml** (`tasks/security.yml`):
   - Disables default site
   - Enables the custom site
   - Enables SSL module
   - Hardens SSL configuration (POODLE fix)
   - Legacy patterns: Short module names, command modules without changed_when, unquoted regexp
   - Modern equivalent: FQCN module names, proper changed_when conditions, quoted regexp
   - Ansible module mapping: 
     - `command:` → `ansible.builtin.command:`
     - `replace:` → `ansible.builtin.replace:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` or `ansible.builtin.template:` | website_https.yml | FQCN, use template for dynamic content |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal modes |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal modes |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal modes |
| Hardcoded content in vars | Template files | website_https.yml | Move to templates directory |
| Command modules without changed_when | Add `changed_when` conditions | website_https.yml | Idempotency improvement |
| Flat playbook structure | Role directory structure | All files | Structural modernization |
| Unquoted regexp | Quoted regexp | poodle_fix.yml | String handling |
| Individual package installation | Loop-based installation | website_https.yml | Already using pkg list for some packages |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.9.0"

**Role dependencies**: None

**External packages**:
- apache2 (version 2.4.41-4ubuntu3.10)
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

- **helloworld.conf.j2**: Convert from hardcoded content in vars to template file
  - Replace `{{ conftext }}` with proper template syntax
  - Use variables for paths and domain names

- **index.html.j2**: Convert from hardcoded content in vars to template file
  - Replace `{{ webtext }}` with proper template syntax
  - Fix HTML syntax error (missing opening bracket in head tag)

## Argument Specification

Variables that should be in meta/argument_specs.yml:

- `apache_version`: 
  - type: string
  - default: "2.4.41-4ubuntu3.10"
  - description: "Version of Apache to install"

- `apache_vhost_name`: 
  - type: string
  - default: "helloworld"
  - description: "Name of the Apache virtual host"

- `apache_document_root`: 
  - type: string
  - default: "/var/www/helloworld"
  - description: "Document root for the website"

- `apache_ssl_cert_dir`: 
  - type: string
  - default: "/etc/apache2/certs"
  - description: "Directory for SSL certificates"

- `apache_ssl_protocols`: 
  - type: string
  - default: "-all +TLSv1.2"
  - description: "SSL protocols to enable/disable"

- `apache_server_name`: 
  - type: string
  - default: "myhost"
  - description: "Server name for the Apache virtual host and SSL certificate"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- tasks/install.yml
- tasks/ssl_certificates.yml
- tasks/website.yml
- tasks/security.yml
- handlers/main.yml
- templates/helloworld.conf.j2
- templates/index.html.j2
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/helloworld.conf.j2
- templates/index.html.j2

## Pre-flight checks:
- Verify Apache installation: `systemctl status apache2`
- Verify SSL configuration: `apache2ctl -M | grep ssl`
- Verify virtual host configuration: `apache2ctl -S`
- Verify SSL certificate: `openssl x509 -in /etc/apache2/certs/apache.crt -text -noout`
- Verify HTTPS connectivity: `curl -k https://localhost/`
- Verify SSL protocols: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify website content: `curl -k https://localhost/ | grep "Hello, world!"`