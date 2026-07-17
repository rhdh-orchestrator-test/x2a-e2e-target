---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The module configures an Apache web server with HTTPS support and includes security hardening. Key modernization needs include FQCN module names, boolean syntax updates, and proper loop structures.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Applies security hardening (POODLE vulnerability fix)
- Includes Chef InSpec tests for compliance validation

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
   - Installs additional packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command module without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command module with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to mitigate POODLE vulnerability
   - Restarts Apache and SSH services
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
| Missing `mode` | Add `mode: '0644'` | poodle_fix.yml | For file operations |
| `pkg:` list format | Use `name:` with list | website_https.yml | Modern syntax |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None (this is a playbook, not a role)
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No traditional .j2 templates exist in this module. The templates are defined inline as variables in the playbooks.

## Argument Specification

Since this is not a traditional role but a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_cert_path`: string, default: "/etc/apache2/certs", description: "Path to store SSL certificates"
- `vhost_name`: string, default: "helloworld", description: "Name of the virtual host"
- `document_root`: string, default: "/var/www/helloworld", description: "Document root for the website"

## Checks for the Migration

**Files to verify**:
- website_https.yml (modernized)
- poodle_fix.yml (modernized)
- tests/website_https_verify.rb
- tests/ssh_profile.rb

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- Inline templates in website_https.yml for Apache configuration and website content

## Pre-flight checks:
```
# Check Apache configuration
apache2ctl configtest

# Verify SSL is enabled
apache2ctl -M | grep ssl

# Test HTTPS connectivity
curl -k https://localhost/

# Verify SSL protocols (POODLE fix)
nmap --script ssl-enum-ciphers -p 443 localhost
```