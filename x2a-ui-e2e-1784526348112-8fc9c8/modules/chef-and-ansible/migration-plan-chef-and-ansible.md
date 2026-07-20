---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module:

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of playbooks demonstrating how to use Chef InSpec for compliance testing with Ansible. The module contains playbooks for setting up a secure HTTPS website and fixing SSL vulnerabilities, along with InSpec tests for verification. Modernization needs include FQCN updates, boolean syntax standardization, and proper loop structures.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a "Hello World" virtual host
- Hardens SSL configuration to prevent POODLE vulnerability
- Includes Chef InSpec tests for compliance verification

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
(Handlers are defined within the playbooks)

**Variable Files:**
(Variables are defined within the playbooks)

**Meta:**
(No meta directory present)

**Templates:**
(No templates directory present)

**Static Files:**
index.html

**Test Files:**
tests/ssh_profile.rb
tests/website_https_verify.rb

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures a virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, command modules with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns: short module names
   - Modern equivalent: FQCN module names

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
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| Missing `mode` in some file operations | Add `mode` parameter | website_https.yml | File permissions |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None specified

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

This module doesn't use traditional Jinja2 templates (.j2 files). Instead, it uses inline templates in variables:

- **website_https.yml**: 
  - `conftext` variable contains Apache virtual host configuration
  - `webtext` variable contains HTML content
  - Both should be properly indented in the YAML file

## Argument Specification

Since this is not a traditional Ansible role but rather a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `virtual_host_name`: string, default: "helloworld", description: "Name of the virtual host"
- `document_root`: string, default: "/var/www/helloworld", description: "Document root for the website"
- `cert_directory`: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml
- tests/website_https_verify.rb
- tests/ssh_profile.rb

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- Inline templates in website_https.yml (conftext and webtext variables)

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify SSL is enabled
apache2ctl -M | grep ssl

# Verify website is accessible via HTTPS
curl -k https://localhost/

# Verify SSL configuration (no POODLE vulnerability)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```