---
source-path: chef-and-ansible
---

Now that I have a good understanding of the content, I'll create a migration plan:

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of playbooks demonstrating how to use Chef InSpec for compliance testing alongside Ansible. The module contains playbooks for configuring a secure HTTPS website with Apache and fixing SSL vulnerabilities, along with InSpec tests for validation. The migration needs focus on modernizing Ansible syntax in the playbooks.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Compliance Testing

**Key Operations**:
- Installs and configures Apache web server with HTTPS
- Creates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Hardens SSL configuration to prevent POODLE vulnerability
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
(Handlers are embedded within the playbooks)

**Variable Files:**
(Variables are embedded within the playbooks)

**Meta:**
(No meta directory)

**Templates:**
(No templates directory, content is embedded in variables)

**Static Files:**
index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command module without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command module with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
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
| `update_cache=true` | `update_cache: true` | website_https.yml | YAML syntax |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| Missing `mode` | Add `mode` parameter | poodle_fix.yml | For file operations |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | "Restart apache2" vs "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None (this is not a traditional role)
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No traditional .j2 templates exist in this module. The templates are embedded as variables in the playbooks.

## Argument Specification

Since this is not a traditional Ansible role but rather a set of playbooks, argument specifications are not applicable. However, if converting to a role, these variables should be documented:
- conftext: Apache virtual host configuration
- webtext: HTML content for the website

## Checks for the Migration

**Files to verify**: 
- website_https.yml
- poodle_fix.yml

**Services to check**: 
- apache2
- sshd

**Templates to validate**: 
- Embedded templates in variables (conftext, webtext)

## Pre-flight checks:
```
# Verify Apache configuration
apache2ctl configtest

# Verify SSL configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify website is accessible
curl -k https://localhost/

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```