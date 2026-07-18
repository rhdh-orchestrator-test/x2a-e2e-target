---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS and SSL security hardening. Migration needs include FQCN module names, boolean syntax updates, and proper loop structure.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Sets up a "Hello World" virtual host
- Hardens SSL/TLS configuration (disables SSLv3, enables TLSv1.2)
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
(No meta directory)

**Templates:**
(No templates directory, content is defined inline in variables)

**Static Files:**
index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates self-signed SSL certificates
   - Configures a virtual host for HTTPS
   - Creates web content directory and deploys "Hello World" website
   - Disables default virtual host and enables the new one
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, command modules with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable vulnerable protocols and enable TLSv1.2
   - Legacy patterns: short module names, no mode for file operations
   - Modern equivalent: FQCN module names, add mode for file operations

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
| Command without changed_when | Add `changed_when` condition | website_https.yml | Idempotency |
| Missing mode in file operations | Add `mode: '0644'` | poodle_fix.yml | File permissions |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None (this is a playbook, not a role)
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No .j2 templates are used in this module. Content is defined inline in variables.

## Argument Specification

Since this is not a traditional Ansible role but rather a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_protocol`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `virtual_host_name`: string, default: "helloworld", description: "Name of the virtual host"
- `document_root`: string, default: "/var/www/helloworld", description: "Document root for the website"

## Checks for the Migration

**Files to verify**:
- website_https.yml (modernized)
- poodle_fix.yml (modernized)

**Services to check**:
- apache2
- sshd

**Templates to validate**: None (inline content)

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify SSL is enabled
apache2ctl -M | grep ssl

# Verify HTTPS is working
curl -k https://localhost/ | grep "Hello, world!"

# Verify SSL protocols (should show TLSv1.2 enabled, SSLv3 disabled)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests to verify compliance
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```