---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The module sets up an Apache web server with HTTPS and includes InSpec tests to verify compliance. The modernization needs focus on updating module syntax to FQCN, converting boolean values, and improving idempotency.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Compliance Testing

**Key Operations**:
- Installs and configures Apache web server with HTTPS
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Applies security hardening for SSL/TLS (POODLE vulnerability fix)
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

**Playbook Files:**
website_https.yml
poodle_fix.yml

**Test Files:**
tests/website_https_verify.rb
tests/ssh_profile.rb

**Configuration Files:**
kitchen.yml

**Documentation:**
README.md

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
   - Creates web directory and deploys "Hello World" website
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command modules without changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security compliance
   - Legacy patterns: short module names, missing changed_when for command modules

3. **Tests**:
   - Chef InSpec tests verify HTTPS functionality and security compliance
   - Tests check for port 443 listening, website availability, and disabled SSL3 protocol
   - SSH security profile tests for root login restrictions

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
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules (a2dissite, a2ensite, a2enmod) |
| Missing `mode` | Add `mode` parameter | website_https.yml | For file operations |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | "Restart apache2" vs "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: '>=1.9.0'
- ansible.posix: '>=1.3.0'

**Role dependencies**: None specified
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No traditional Jinja2 templates are used in this module. The playbooks use inline templates via variables (`conftext` and `webtext`).

## Argument Specification

Since this is not a traditional Ansible role but rather a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: '2.4.41-4ubuntu3.10', description: 'Version of Apache to install'
- `ssl_protocols`: string, default: '-all +TLSv1.2', description: 'SSL protocols to enable/disable'
- `virtual_host_name`: string, default: 'helloworld', description: 'Name of the virtual host'
- `document_root`: string, default: '/var/www/helloworld', description: 'Document root for the website'
- `ssl_cert_path`: string, default: '/etc/apache2/certs', description: 'Path to store SSL certificates'

## Checks for the Migration

**Files to verify**:
- website_https.yml (modernized)
- poodle_fix.yml (modernized)
- meta/main.yml (new)
- defaults/main.yml (new)
- tasks/main.yml (new)
- tasks/install.yml (new)
- tasks/configure.yml (new)
- tasks/secure.yml (new)
- handlers/main.yml (new)
- tests/website_https_verify.rb (unchanged)
- tests/ssh_profile.rb (unchanged)

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2 (new, extracted from inline template)
- templates/index.html.j2 (new, extracted from inline template)

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify HTTPS is configured: `curl -k https://localhost/`
- Verify SSL protocols: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Run InSpec tests: `inspec exec tests/website_https_verify.rb`
- Verify SSH security: `inspec exec tests/ssh_profile.rb`