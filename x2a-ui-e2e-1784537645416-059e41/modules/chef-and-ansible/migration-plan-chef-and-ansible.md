---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module:

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of playbooks demonstrating how to use Chef InSpec for compliance testing alongside Ansible. The module contains playbooks for setting up a secure HTTPS website and fixing SSL vulnerabilities, along with InSpec tests for verification. The migration needs focus on modernizing Ansible syntax in the playbooks.

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
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Activates SSL module in Apache
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
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `command: a2dissite` without `changed_when` | Add `changed_when: false` or check for actual changes | website_https.yml | Idempotency |
| `command: a2ensite` without `changed_when` | Add `changed_when: false` or check for actual changes | website_https.yml | Idempotency |
| `command: a2enmod` without `changed_when` | Add `changed_when: false` or check for actual changes | website_https.yml | Idempotency |
| Missing `mode` for some file operations | Add appropriate `mode` parameter | website_https.yml | File permissions |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this module. The templates are embedded as variables in the playbooks.

## Argument Specification

Since this is not a traditional role but a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `website_root`: string, default: "/var/www/helloworld", description: "Document root for the website"
- `ssl_cert_dir`: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"

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
- Embedded templates in website_https.yml (conftext and webtext variables)

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify SSL configuration
apache2ctl -M | grep ssl
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify website accessibility
curl -k https://localhost/ | grep "Hello, world"

# Verify SSL security (requires OpenSSL)
openssl s_client -connect localhost:443 -ssl3 || echo "SSLv3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2 | grep "Protocol"

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```