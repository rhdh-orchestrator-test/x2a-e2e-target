---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks that configure an Apache web server with HTTPS support, along with Chef InSpec tests for compliance verification. The migration needs focus on modernizing the Ansible playbook syntax to use FQCN, proper boolean values, and structured loops.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with SSL/TLS Security Hardening

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Sets up a basic "Hello World" website
- Applies security hardening for SSL/TLS (disables SSLv3, enables TLSv1.2)
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
(No meta directory)

**Templates:**
(No templates directory, content is defined inline in variables)

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
   - Creates website directory and deploys "Hello World" content
   - Disables default virtual host and enables the new one
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command modules with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable SSLv3 and enable only TLSv1.2
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
| Inconsistent handler names | Standardize handler names | website_https.yml, poodle_fix.yml | "Restart apache" vs "Restart apache2" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No traditional templates (.j2 files) are used in this module. Instead, templates are defined as variables in the playbooks:

- **website_https.yml**: 
  - `conftext` variable contains Apache virtual host configuration
  - `webtext` variable contains HTML content
  - Both should be moved to separate template files for better maintainability

## Argument Specification

Since this is not a traditional Ansible role but a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `website_content`: string, default: HTML content, description: "Content of the website"
- `vhost_config`: string, default: Apache vhost config, description: "Apache virtual host configuration"

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml
- templates/vhost.conf.j2 (new)
- templates/index.html.j2 (new)
- defaults/main.yml (new)
- tasks/main.yml (new)
- handlers/main.yml (new)
- meta/main.yml (new)

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- New templates created from inline variables

## Pre-flight checks:
```bash
# Check Apache configuration
apache2ctl configtest

# Verify SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify website is accessible
curl -k https://localhost/

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

## Migration Strategy

This is not a traditional Ansible role but rather a set of playbooks with Chef InSpec tests. The migration strategy should be:

1. Convert the playbooks into a proper Ansible role structure
2. Modernize all module references to use FQCN
3. Fix boolean syntax and file permissions
4. Extract inline templates to separate template files
5. Create proper variable defaults
6. Add changed_when conditions to command modules
7. Standardize handler names
8. Keep the InSpec tests for compliance verification
9. Create proper documentation

The resulting role will maintain the same functionality but follow modern Ansible best practices.