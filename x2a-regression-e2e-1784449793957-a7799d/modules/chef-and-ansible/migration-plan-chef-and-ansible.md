---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for the Ansible content in the "chef-and-ansible" directory.

# Migration Plan: chef-and-ansible

**TLDR**: This repository contains Ansible playbooks for configuring a secure HTTPS website with Apache2 and SSL/TLS security hardening. The main modernization needs include updating module syntax to FQCN, replacing deprecated loop structures, fixing boolean syntax, and ensuring proper parameter quoting.

## Service Type and Configuration

**Service Type**: Web Server (Apache2 with HTTPS)

**Key Operations**:
- Installs Apache2 web server
- Configures SSL/TLS for secure HTTPS
- Creates self-signed certificates
- Deploys a simple "Hello World" website
- Hardens SSL configuration to prevent POODLE vulnerability
- Manages Apache2 and SSH services

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

```
website_https.yml
poodle_fix.yml
kitchen.yml
README.md
index.html
tests/website_https_verify.rb
tests/ssh_profile.rb
```

**Playbook Files:**
website_https.yml
poodle_fix.yml

**Configuration Files:**
kitchen.yml

**Documentation:**
README.md

**Static Files:**
index.html

**Test Files:**
tests/website_https_verify.rb
tests/ssh_profile.rb

## Module Explanation

The repository performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache2 with specific version
   - Installs curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys HTML content
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command modules with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
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
| Handler name mismatch | Consistent handler names | website_https.yml, poodle_fix.yml | "Restart apache" vs "Restart apache2" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

No .j2 templates are present in the repository. The playbooks use inline templates via variables.

## Argument Specification

For a proper role conversion, the following variables should be documented in meta/argument_specs.yml:

- `conftext`: Apache virtual host configuration (string)
- `webtext`: HTML content for the website (string)

## Checks for the Migration

**Files to verify**:
- roles/apache_https/tasks/main.yml
- roles/apache_https/tasks/poodle_fix.yml
- roles/apache_https/handlers/main.yml
- roles/apache_https/defaults/main.yml
- roles/apache_https/meta/main.yml
- roles/apache_https/meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- No .j2 templates to validate

## Pre-flight checks:
```bash
# Check Apache configuration
apache2ctl configtest

# Verify SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2

# Check for POODLE vulnerability
openssl s_client -connect localhost:443 -ssl3 2>&1 | grep "Protocol"

# Verify website is accessible
curl -k https://localhost/ | grep "Hello, world!"

# Check Apache and SSH services
systemctl status apache2
systemctl status sshd
```