---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module:

# Migration Plan: chef-and-ansible

**TLDR**: This is a demonstration module showing how to use Chef InSpec for compliance testing alongside Ansible. It contains playbooks for setting up a secure HTTPS website with Apache and fixing SSL POODLE vulnerability. The module needs modernization to use FQCN module names, proper boolean syntax, and structured loops.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Applies security hardening for SSL/TLS (POODLE vulnerability fix)
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
(Handlers are embedded in the playbooks)

**Variable Files:**
(Variables are embedded in the playbooks)

**Meta:**
(No dedicated meta file)

**Templates:**
(No dedicated template files, content is embedded in variables)

**Static Files:**
index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs supporting packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: non-FQCN module names, unquoted boolean values, command modules without changed_when

2. **poodle_fix.yml**:
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns: non-FQCN module names, no mode specified for file operations

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `command:` without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Missing `mode:` | Add `mode: '0644'` | poodle_fix.yml | File permissions |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this module. The templates are embedded as variables in the playbooks.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, Apache virtual host configuration template
- `webtext`: string, HTML content for the website

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
- Embedded templates in variables (conftext, webtext)

## Pre-flight checks:
```
# Verify Apache is running with SSL
systemctl status apache2
apache2ctl -M | grep ssl

# Verify website is accessible via HTTPS
curl -k https://localhost/

# Verify SSL configuration (no POODLE vulnerability)
nmap --script ssl-enum-ciphers -p 443 localhost
```

This module is not a traditional Ansible role but rather a demonstration of using Chef InSpec with Ansible for compliance testing. The migration plan focuses on modernizing the Ansible playbooks while preserving the Chef InSpec testing functionality.