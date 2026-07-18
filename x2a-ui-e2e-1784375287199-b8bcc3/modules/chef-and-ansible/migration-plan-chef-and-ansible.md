---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for the chef-and-ansible project.

# Migration Plan: chef-and-ansible

**TLDR**: This project demonstrates using Chef InSpec for compliance testing with Ansible playbooks that configure a secure Apache web server with HTTPS. The migration needs to focus on modernizing the Ansible playbooks by implementing FQCN module names, proper boolean syntax, and structured loop patterns while preserving the integration with Chef InSpec for compliance testing.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Implements security hardening for SSL/TLS (disabling SSLv3, enabling TLSv1.2)
- Integrates with Chef InSpec for compliance testing

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
(No dedicated template files, content is defined inline in variables)

**Static Files:**
index.html

## Module Explanation

The role performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs supporting packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web content directory and deploys "Hello World" website
   - Disables default virtual host and enables the new one
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, idempotent command handling
   - Ansible module mapping: apt → ansible.builtin.apt, file → ansible.builtin.file, etc.

2. **poodle_fix.yml**:
   - Updates Apache SSL configuration to disable SSLv3 and enable only TLSv1.2
   - Restarts Apache and SSH services
   - Legacy patterns: short module names, no changed_when for command modules
   - Modern equivalent: FQCN module names, idempotent command handling
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
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml, poodle_fix.yml | For command modules |
| Missing `mode` | Add `mode: '0644'` | Some file operations | File permissions |
| Inline variables | Move to vars files | website_https.yml | Structural improvement |
| Handlers in playbooks | Move to separate handler files | website_https.yml, poodle_fix.yml | Structural improvement |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this project. The templates are defined as inline variables in the playbooks.

For the inline templates in website_https.yml:
- **conftext variable**: No modernization needed for the Apache virtual host configuration
- **webtext variable**: Fix HTML syntax error in the head tag (`</head>` is missing the closing slash)

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- conftext: string, Apache virtual host configuration template
- webtext: string, HTML content for the website
- apache_version: string, default: "2.4.41-4ubuntu3.10", Apache version to install

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (new)
- tasks/apache_install.yml (new)
- tasks/apache_configure.yml (new)
- tasks/ssl_configure.yml (new)
- handlers/main.yml (new)
- defaults/main.yml (new)
- templates/virtualhost.conf.j2 (new)
- templates/index.html.j2 (new)
- meta/main.yml (new)
- meta/argument_specs.yml (new)

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2 (new)
- templates/index.html.j2 (new)

## Pre-flight checks:
```bash
# Verify Apache installation
systemctl status apache2

# Verify SSL configuration
apache2ctl -M | grep ssl

# Verify HTTPS is working
curl -k https://localhost/

# Verify SSL/TLS protocols
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```