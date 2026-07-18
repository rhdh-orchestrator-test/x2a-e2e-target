---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for the chef-and-ansible module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS and SSL security hardening. The migration needs focus on modernizing Ansible syntax, using FQCN, proper boolean values, and updating deprecated patterns.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server
- Sets up HTTPS with self-signed certificates
- Configures a virtual host for a "Hello World" website
- Implements SSL/TLS security hardening (POODLE vulnerability fix)
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
(No meta directory/file)

**Templates:**
(No templates directory/files)

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
   - Creates web directory and deploys a "Hello World" website
   - Disables default site and enables the new virtual host
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, use of ansible.builtin.command with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns: short module names, no mode for file operations
   - Modern equivalent: FQCN module names, proper file permissions

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Key-value syntax |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml, poodle_fix.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| Missing handler name | Fix handler name | poodle_fix.yml | Handler "Restart apache2" referenced but defined as "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None (this is not structured as a traditional role)
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

## Conversion to Proper Ansible Role

To convert this to a proper Ansible role structure, the following would be needed:

1. Create standard role directory structure:
   - tasks/main.yml (from website_https.yml tasks)
   - tasks/poodle_fix.yml
   - handlers/main.yml (consolidate handlers)
   - defaults/main.yml (extract variables)
   - meta/main.yml (add role metadata)
   - tests/ (keep InSpec tests)

2. Extract variables from inline definitions to defaults/main.yml
3. Create proper documentation in README.md
4. Add meta/argument_specs.yml for variable validation

This would transform the current playbooks into a reusable Ansible role following modern best practices.