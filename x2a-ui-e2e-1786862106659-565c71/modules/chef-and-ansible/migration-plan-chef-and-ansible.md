---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this project.

# Migration Plan: chef-and-ansible

**TLDR**: This project contains Ansible playbooks for configuring a secure Apache web server with HTTPS support, along with Chef InSpec tests for validation. The main modernization needs include updating module syntax to FQCN format, replacing deprecated loop syntax, and improving idempotency in command modules.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server
- Configures SSL/TLS for HTTPS
- Creates self-signed certificates
- Deploys a simple "Hello World" website
- Hardens SSL configuration to prevent POODLE vulnerability
- Includes Chef InSpec tests for validation

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

```
README.md
index.html
kitchen.yml
poodle_fix.yml
tests/ssh_profile.rb
tests/website_https_verify.rb
website_https.yml
```

**Task Files:**
website_https.yml
poodle_fix.yml

**Handler Files:**
Handlers are defined within the playbooks (website_https.yml, poodle_fix.yml)

**Variable Files:**
Variables are defined inline within the playbooks

**Meta:**
No dedicated meta file

**Templates:**
No dedicated template files (content is defined inline using variables)

**Static Files:**
No dedicated static files

## Module Explanation

The role performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs supporting packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Handlers restart Apache and SSH services when needed

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Handlers restart Apache and SSH services when needed

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
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `command:` without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal mode |
| `name: Restart apache` | `name: Restart apache2` | website_https.yml | Handler name inconsistency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this project. The templates are defined inline using variables:

- **website_https.yml**: 
  - `conftext` variable contains Apache virtual host configuration
  - `webtext` variable contains HTML content

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, Apache virtual host configuration template
- `webtext`: string, HTML content for the website

## Checks for the Migration

**Files to verify**: 
- website_https.yml
- poodle_fix.yml
- tests/website_https_verify.rb

**Services to check**: 
- apache2
- sshd

**Templates to validate**: 
- Inline templates in `conftext` and `webtext` variables

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify SSL is enabled
apache2ctl -M | grep ssl

# Verify HTTPS is working
curl -k https://localhost/

# Verify SSL configuration (no POODLE vulnerability)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
```

## Migration Notes

This project is not structured as a traditional Ansible role but rather as standalone playbooks with Chef InSpec tests. To properly migrate this to a modern Ansible role:

1. Create a standard Ansible role structure:
   - tasks/main.yml
   - handlers/main.yml
   - defaults/main.yml
   - meta/main.yml
   - templates/
   - tests/

2. Move the tasks from website_https.yml and poodle_fix.yml into tasks/main.yml

3. Extract the handlers into handlers/main.yml

4. Move the inline templates (`conftext` and `webtext`) to template files:
   - templates/virtualhost.conf.j2
   - templates/index.html.j2

5. Define variables in defaults/main.yml

6. Create meta/argument_specs.yml for variable validation

7. Update the InSpec tests to work with the new role structure

This migration will transform the standalone playbooks into a reusable, modern Ansible role that follows best practices.