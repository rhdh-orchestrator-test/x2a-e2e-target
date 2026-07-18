---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this Ansible content.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a collection of standalone playbooks that configure Apache with HTTPS and SSL security fixes. The primary modernization needs include using FQCN module names, proper boolean syntax, quoted file modes, and structured loops instead of deprecated patterns.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server with specific version
- Configures SSL/TLS for secure HTTPS connections
- Generates self-signed certificates
- Creates and configures a virtual host
- Deploys a simple "Hello World" website
- Applies security fixes for SSL/TLS (POODLE vulnerability)

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
None (this is not a traditional Ansible role with tasks directory)

**Handler Files:**
None (handlers are defined within the playbooks)

**Variable Files:**
None (variables are defined within the playbooks)

**Meta:**
None

**Templates:**
None (content is defined inline using variables)

**Static Files:**
index.html

## Module Explanation

The repository contains standalone playbooks rather than a traditional Ansible role structure:

1. **website_https.yml**:
   - Sets up Apache with HTTPS support
   - Installs necessary packages (apache2, curl, openssl, python3-openssl)
   - Creates SSL certificates directory
   - Generates self-signed SSL certificates
   - Configures a virtual host for HTTPS
   - Deploys a simple "Hello World" website
   - Legacy patterns found: non-FQCN module names, unquoted boolean values, unquoted file modes
   - Modern equivalent: Use FQCN module names, quoted file modes, proper boolean syntax

2. **poodle_fix.yml**:
   - Applies security fix for POODLE vulnerability in SSL
   - Updates SSL configuration to disable vulnerable protocols
   - Legacy patterns found: non-FQCN module names
   - Modern equivalent: Use FQCN module names

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
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted file mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted file mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted file mode |
| `command:` without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No traditional templates (.j2 files) are used in this repository. Content is defined inline using variables in the playbooks.

## Argument Specification

Since this is not a traditional Ansible role, there's no need for meta/argument_specs.yml. However, if converting to a role, these variables should be documented:
- conftext: string, default as shown in website_https.yml, Apache virtual host configuration
- webtext: string, default as shown in website_https.yml, HTML content for the website

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None (inline content)

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify SSL configuration
apache2ctl -M | grep ssl

# Verify virtual host configuration
apache2ctl -S

# Test HTTPS connection
curl -k https://localhost

# Verify SSL/TLS protocols (POODLE fix)
nmap --script ssl-enum-ciphers -p 443 localhost
```

## Migration Recommendations

1. Convert the standalone playbooks into a proper Ansible role structure:
   - Create tasks/main.yml
   - Move handlers to handlers/main.yml
   - Move variables to defaults/main.yml
   - Create templates for Apache configuration and website content

2. Add proper idempotency checks for command modules:
   - Add `changed_when` conditions to a2dissite, a2ensite, and a2enmod commands

3. Consider using more idiomatic Ansible modules:
   - Replace `command: a2ensite` with `community.general.apache2_module`
   - Replace `command: a2enmod` with `community.general.apache2_module`

4. Add proper documentation in README.md about role usage and variables