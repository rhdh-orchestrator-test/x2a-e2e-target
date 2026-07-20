---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This project demonstrates using Chef InSpec for compliance testing with Ansible playbooks. It contains Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities, along with InSpec tests for validation. The migration needs focus on modernizing Ansible syntax to use FQCN, proper boolean values, and structured loops.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server with HTTPS
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Implements security hardening for SSL/TLS protocols (POODLE vulnerability fix)
- Includes InSpec tests for compliance validation

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
(Variables are defined within the playbooks)

**Meta:**
(No dedicated meta file)

**Templates:**
(No dedicated template files, content is embedded in variables)

**Static Files:**
index.html

## Module Explanation

The role performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs supporting packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, command module with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security compliance
   - Legacy patterns: short module names, no mode for file operations
   - Modern equivalent: FQCN module names, proper file permissions

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Key-value syntax |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `command:` without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Missing `mode:` | Add `mode: '0644'` | website_https.yml, poodle_fix.yml | File permissions |
| `service:` | `ansible.builtin.service:` | website_https.yml, poodle_fix.yml | FQCN |
| Inconsistent handler name | Standardize handler names | website_https.yml, poodle_fix.yml | "Restart apache" vs "Restart apache2" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this project. The templates are embedded as variables in the playbooks.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, default is the VirtualHost configuration, description: "Apache VirtualHost configuration for HTTPS"
- `webtext`: string, default is the HTML content, description: "HTML content for the Hello World website"

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
- No dedicated template files to validate

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify HTTPS is configured: `curl -k https://localhost/`
- Verify SSL protocols: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Run InSpec tests: `inspec exec tests/website_https_verify.rb`
- Verify SSH hardening: `inspec exec tests/ssh_profile.rb`