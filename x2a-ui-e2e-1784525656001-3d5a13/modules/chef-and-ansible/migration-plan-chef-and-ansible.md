---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS support and SSL security hardening. The migration needs focus on modernizing Ansible syntax, using FQCN, proper boolean values, and loop structures.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with SSL/TLS Security Hardening

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Deploys a simple "Hello World" website
- Hardens SSL/TLS configuration (disables SSLv3, enables TLSv1.2)
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
(Handlers are embedded within the playbooks)

**Variable Files:**
(Variables are defined inline in the playbooks)

**Meta:**
(No dedicated meta file)

**Templates:**
(No dedicated template files, content is defined inline)

**Static Files:**
index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache web server with specific version
   - Installs curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web directory and deploys "Hello World" website
   - Disables default virtual host and enables the new one
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, use of ansible.builtin.command with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable SSLv3 and enable TLSv1.2
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
| Inconsistent handler names | Standardize handler names | website_https.yml, poodle_fix.yml | "Restart apache" vs "Restart apache2" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this module. The templates are defined inline as variables in the playbooks.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- conftext: string, default is the VirtualHost configuration, description: "Apache virtual host configuration for HTTPS"
- webtext: string, default is the HTML content, description: "HTML content for the Hello World website"

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
- Inline templates in website_https.yml

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify HTTPS is configured
curl -k https://localhost/

# Verify SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```