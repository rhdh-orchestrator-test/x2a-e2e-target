---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS and security hardening. Migration needs include converting to a proper Ansible role structure with FQCN module names, modern loop syntax, and proper variable organization.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server
- Sets up HTTPS with self-signed certificates
- Deploys a simple "Hello World" website
- Implements security hardening (POODLE vulnerability fix)
- Uses Chef InSpec for compliance testing

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
(Handlers are embedded in the playbooks)

**Variable Files:**
(Variables are embedded in the playbooks)

**Meta:**
(No meta file exists)

**Templates:**
(No dedicated template files, content is embedded in variables)

**Static Files:**
index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs additional packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command module without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command module with changed_when

2. **poodle_fix.yml**:
   - Modifies Apache SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns: short module names, no mode for file operations
   - Modern equivalent: FQCN module names, proper file permissions

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
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| Missing file modes | Add explicit modes | poodle_fix.yml | For file operations |
| Embedded templates | Move to template files | website_https.yml | For conftext and webtext |
| Embedded variables | Move to defaults/main.yml | website_https.yml | For variable organization |
| Embedded handlers | Move to handlers/main.yml | website_https.yml, poodle_fix.yml | For handler organization |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None specified
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **apache_vhost.j2**: Create from embedded conftext variable, use proper Jinja2 syntax
- **index.html.j2**: Create from embedded webtext variable, fix HTML syntax errors

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- apache_version: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- ssl_cert_dir: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- vhost_name: string, default: "helloworld", description: "Name of the virtual host"
- document_root: string, default: "/var/www/helloworld", description: "Document root for the website"
- ssl_protocols: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- tasks/install.yml
- tasks/configure.yml
- tasks/secure.yml
- handlers/main.yml
- defaults/main.yml
- templates/apache_vhost.j2
- templates/index.html.j2
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/apache_vhost.j2
- templates/index.html.j2

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify HTTPS configuration
curl -k https://localhost/

# Verify SSL protocols (should only have TLSv1.2 enabled)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```