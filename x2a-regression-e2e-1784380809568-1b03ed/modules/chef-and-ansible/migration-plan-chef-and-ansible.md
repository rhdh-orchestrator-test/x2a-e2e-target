---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for the chef-and-ansible module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The module configures an Apache web server with HTTPS support and includes security hardening. Key modernization needs include FQCN module names, boolean syntax updates, and proper loop structures.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Applies security hardening for SSL/TLS protocols (POODLE vulnerability fix)
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
(No dedicated meta file)

**Templates:**
(No dedicated template files, content is defined as variables in playbooks)

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
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, use of ansible.builtin.command with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns: short module names, no mode specified for file operations
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
- community.crypto: '>=1.0.0'
- ansible.posix: '>=1.0.0'

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this module. The templates are defined as variables within the playbooks:

- **website_https.yml**: Contains inline templates for Apache configuration and HTML content that should be moved to separate template files with proper Jinja2 syntax.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- conftext: string, Apache virtual host configuration template
- webtext: string, HTML content for the website
- apache_version: string, default: '2.4.41-4ubuntu3.10', Apache version to install
- ssl_protocols: string, default: '-all +TLSv1.2', SSL protocols to enable/disable

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (new file to include task files)
- tasks/install_apache.yml (extracted from website_https.yml)
- tasks/configure_ssl.yml (extracted from website_https.yml)
- tasks/configure_website.yml (extracted from website_https.yml)
- tasks/security_hardening.yml (extracted from poodle_fix.yml)
- handlers/main.yml (consolidated handlers)
- templates/virtualhost.conf.j2 (extracted from conftext variable)
- templates/index.html.j2 (extracted from webtext variable)
- defaults/main.yml (for variables)
- meta/main.yml (new file for role metadata)
- meta/argument_specs.yml (new file for argument specifications)

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2
- templates/index.html.j2

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify SSL configuration
apache2ctl -M | grep ssl
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify website accessibility
curl -k https://localhost/

# Verify SSL/TLS protocols
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail
```

## Migration Strategy

This is not a traditional Ansible role but rather a set of playbooks with Chef InSpec tests. The migration strategy should:

1. Convert the playbooks into a proper Ansible role structure
2. Extract inline templates into separate template files
3. Modernize module syntax with FQCN
4. Add proper idempotency checks
5. Standardize variable names and handler references
6. Maintain the Chef InSpec tests for compliance validation
7. Create proper documentation for the role

The resulting role will maintain the same functionality while following modern Ansible best practices.