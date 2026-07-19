---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this Ansible content.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of playbooks demonstrating how to use Chef InSpec for compliance testing with Ansible. The main playbook sets up an Apache web server with HTTPS, while a secondary playbook fixes SSL/TLS configuration for security compliance. The migration needs focus on modernizing module syntax to FQCN, updating loop structures, and improving idempotency.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server
- Configures SSL/TLS for HTTPS
- Creates self-signed certificates
- Deploys a simple "Hello World" website
- Configures virtual hosts
- Implements security hardening (POODLE vulnerability fix)

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
Handlers are embedded in the playbooks (website_https.yml, poodle_fix.yml)

**Variable Files:**
Variables are defined inline in the playbooks

**Meta:**
No dedicated meta file (not a traditional role structure)

**Templates:**
No dedicated template files (content is defined inline in variables)

**Static Files:**
No static files

## Module Explanation

The role performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache and dependencies
   - Creates directories for SSL certificates
   - Generates self-signed SSL certificates
   - Configures a virtual host for HTTPS
   - Creates and deploys a simple "Hello World" website
   - Activates the virtual host and SSL module
   - Ansible module mapping: short names → FQCN (apt → ansible.builtin.apt, etc.)

2. **poodle_fix.yml**:
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security compliance
   - Ansible module mapping: replace → ansible.builtin.replace

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
| `command: a2dissite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| `command: a2ensite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| `command: a2enmod` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Idempotency |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None (not a traditional role)
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist. The templates are defined as variables in the playbooks.

## Argument Specification

Since this is not a traditional role, there's no need for meta/argument_specs.yml. However, if converting to a proper role, these variables should be documented:
- conftext: string, default as shown, description: "Apache virtual host configuration"
- webtext: string, default as shown, description: "HTML content for the website"

## Checks for the Migration

**Files to verify**: 
- website_https.yml
- poodle_fix.yml

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None (inline variables)

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify HTTPS is configured
curl -k https://localhost/

# Verify SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail

# Verify Apache configuration
apache2ctl -t
```