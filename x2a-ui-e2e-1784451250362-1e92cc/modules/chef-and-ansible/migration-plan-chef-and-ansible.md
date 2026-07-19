---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for the chef-and-ansible module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The migration needs focus on modernizing the Ansible playbooks to use FQCN, proper boolean syntax, and structured loops while preserving the Chef InSpec testing framework integration.

## Service Type and Configuration

**Service Type**: Web Server (Apache HTTPS)

**Key Operations**:
- Installs and configures Apache web server with HTTPS
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Implements SSL security hardening (POODLE fix)
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
(Variables are embedded within the playbooks)

**Meta:**
(No dedicated meta file)

**Templates:**
(No dedicated template files, content is embedded as variables)

**Static Files:**
index.html

**Test Files:**
tests/ssh_profile.rb
tests/website_https_verify.rb
kitchen.yml

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs dependencies (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command modules with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security compliance
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
- ansible.posix: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this module. The templates are embedded as variables in the playbooks.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- conftext: string, default is the VirtualHost configuration, description: "Apache virtual host configuration"
- webtext: string, default is the HTML content, description: "Website HTML content"

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml
- tests/website_https_verify.rb
- tests/ssh_profile.rb
- kitchen.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- Embedded templates in website_https.yml (conftext and webtext variables)

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify HTTPS is configured correctly
curl -k https://localhost/

# Verify SSL protocols
openssl s_client -connect localhost:443 -ssl3 || echo "SSLv3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2 && echo "TLSv1.2 enabled (good)"

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

## Additional Notes

This is not a traditional Ansible role but rather a set of playbooks with Chef InSpec tests. To properly modernize this into an Ansible role structure:

1. Create a standard Ansible role structure:
   - Create tasks/main.yml and move tasks from website_https.yml
   - Create handlers/main.yml for the handlers
   - Create defaults/main.yml for the variables
   - Create templates/ directory and move embedded templates to files
   - Create meta/main.yml with proper role metadata

2. Preserve the Chef InSpec testing integration by:
   - Keeping the tests/ directory with InSpec tests
   - Updating kitchen.yml to point to the new role structure

3. Consider splitting the functionality:
   - One role for Apache HTTPS setup
   - One role for security hardening (POODLE fix)

This will maintain the compliance automation capabilities while providing a more maintainable Ansible structure.