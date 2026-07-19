---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module:

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of example playbooks demonstrating how to use Chef InSpec for compliance testing alongside Ansible. The module contains playbooks for configuring a secure HTTPS website and fixing SSL vulnerabilities, along with InSpec tests for verification. Modernization needs include FQCN updates, boolean syntax standardization, and loop structure improvements.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Hardens SSL configuration to prevent POODLE vulnerability
- Includes InSpec tests for compliance verification

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
(No meta directory/file present)

**Templates:**
(No templates directory/files present)

**Static Files:**
index.html
tests/ssh_profile.rb
tests/website_https_verify.rb

## Module Explanation

The module performs operations in this order:

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
   - Modern equivalent: FQCN module names, quoted boolean values, command with changed_when or ansible.builtin.shell with creates/removes

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
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| Missing `changed_when` | Add `changed_when` condition | website_https.yml | For command modules |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| Missing file modes | Add `mode: '0644'` | Multiple files | File permissions |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: '>=1.0.0'
- ansible.posix: '>=1.0.0'

**Role dependencies**: None specified
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No .j2 templates are present in this module. The playbooks use inline templates via vars.

## Argument Specification

Since this is not a traditional role but a set of example playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `website_root`: string, default: "/var/www/helloworld", description: "Document root for the website"
- `ssl_cert_path`: string, default: "/etc/apache2/certs", description: "Path to store SSL certificates"
- `website_content`: string, default: (HTML content), description: "Content of the website"
- `vhost_config`: string, default: (VirtualHost config), description: "Apache VirtualHost configuration"

## Checks for the Migration

**Files to verify**:
- website_https.yml (modernized)
- poodle_fix.yml (modernized)
- collections/requirements.yml (new)

**Services to check**:
- apache2
- sshd

**Templates to validate**: None (inline templates in vars)

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify SSL configuration
apache2ctl -M | grep ssl

# Test HTTPS connectivity
curl -k https://localhost/

# Verify SSL protocols (should only have TLSv1.2 enabled)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
```