---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS support and implement security fixes. The migration needs focus on modernizing Ansible syntax, using FQCN, proper boolean values, and structured loops.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Compliance Testing

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Implements security fixes for SSL/TLS (POODLE vulnerability)
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
   - Installs additional packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures a virtual host for HTTPS
   - Creates a "Hello World" website
   - Deactivates default virtual host and activates the new one
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, command module with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable vulnerable protocols
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
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| Missing `mode` | Add `mode: '0644'` | poodle_fix.yml | For file operations |
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None specified
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No .j2 templates are present in this module.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- conftext: string, default is the VirtualHost configuration, description: "Apache virtual host configuration"
- webtext: string, default is the HTML content, description: "Content for the Hello World website"

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml
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

# Verify HTTPS is enabled
curl -k https://localhost/

# Verify SSL configuration (should only allow TLSv1.2)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests to verify compliance
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

## Additional Notes

This is not a traditional Ansible role but rather a set of playbooks with Chef InSpec tests. To properly migrate this to a modern Ansible role structure, you would need to:

1. Create a proper role directory structure:
   - tasks/main.yml (combining the tasks from both playbooks)
   - handlers/main.yml (extracting handlers from playbooks)
   - defaults/main.yml (for variables)
   - meta/main.yml (for role metadata)
   - tests/ (keeping the InSpec tests)

2. Update all syntax to modern Ansible standards as outlined in the modernization mapping.

3. Consider using ansible-test for testing instead of or alongside Chef InSpec.

4. Create a proper collection structure if this is to be distributed as a collection.