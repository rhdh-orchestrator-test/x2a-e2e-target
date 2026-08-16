---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of playbooks demonstrating how to use Chef InSpec for compliance testing alongside Ansible. The module configures an Apache web server with HTTPS support and includes InSpec tests for validation. Modernization needs include updating module syntax to FQCN, replacing deprecated loop syntax, and ensuring proper boolean formatting.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Compliance Testing

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Applies security hardening for SSL/TLS (disabling SSLv3, enabling TLSv1.2)
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
(No meta directory/file present)

**Templates:**
(No templates directory/files present)

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
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures a virtual host for HTTPS
   - Creates web directory and deploys a "Hello World" website
   - Disables default virtual host and enables the new one
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, command module with changed_when or use ansible.builtin.shell with creates/removes

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable SSLv3 and enable TLSv1.2 only
   - Restarts Apache and SSH services
   - Legacy patterns: short module names, no mode specified for file operations
   - Modern equivalent: FQCN module names, specify mode for file operations

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

**Role dependencies**: None specified
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No .j2 templates are present in this module.

## Argument Specification

Since this is not a traditional Ansible role but rather a set of playbooks, argument specifications would be created if converting to a proper role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_cert_path`: string, default: "/etc/apache2/certs", description: "Path to store SSL certificates"
- `virtual_host_name`: string, default: "helloworld", description: "Name of the virtual host"
- `document_root`: string, default: "/var/www/helloworld", description: "Document root for the website"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"

## Checks for the Migration

**Files to verify**:
- website_https.yml (modernized)
- poodle_fix.yml (modernized)
- tests/website_https_verify.rb
- tests/ssh_profile.rb

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify SSL is enabled
apache2ctl -M | grep ssl

# Verify website is accessible via HTTPS
curl -k https://localhost/ | grep "Hello, world!"

# Verify SSL configuration (no SSLv3, TLSv1.2 enabled)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```