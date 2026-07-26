---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS support and SSL security hardening. The migration needs focus on modernizing syntax, using FQCN, proper boolean values, and improving idempotency.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with SSL/TLS Security Configuration

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Deploys a simple "Hello World" website
- Hardens SSL/TLS configuration to prevent POODLE vulnerability
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
(Variables are defined within the playbooks)

**Meta:**
(No dedicated meta file)

**Templates:**
(No dedicated template files, content is embedded in variables)

**Static Files:**
index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs supporting packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates self-signed SSL certificates
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" website
   - Disables default site and enables the new virtual host with SSL
   - Legacy patterns: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, handlers with FQCN

2. **poodle_fix.yml**:
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 to mitigate POODLE vulnerability
   - Legacy patterns: short module names, no mode for file operations
   - Modern equivalent: FQCN module names, proper handlers

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
| Missing `mode:` | Add `mode:` parameter | website_https.yml | File permissions |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this module. The templates are embedded as variables in the playbooks:

- **website_https.yml**: The `conftext` and `webtext` variables contain template content that should be moved to separate template files with proper Jinja2 syntax.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, Apache virtual host configuration template
- `webtext`: string, HTML content for the website

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (new file to include task files)
- tasks/website_https.yml (migrated from website_https.yml)
- tasks/poodle_fix.yml (migrated from poodle_fix.yml)
- handlers/main.yml (new file for consolidated handlers)
- templates/virtualhost.conf.j2 (new file from conftext variable)
- templates/index.html.j2 (new file from webtext variable)
- defaults/main.yml (new file for variables)
- meta/main.yml (new file for role metadata)
- meta/argument_specs.yml (new file for variable specifications)

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2
- templates/index.html.j2

## Pre-flight checks:
```
# Verify Apache configuration
apache2ctl configtest

# Verify SSL configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify website is accessible
curl -k https://localhost/

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```