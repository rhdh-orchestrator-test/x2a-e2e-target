---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The module configures an Apache web server with HTTPS support and includes security hardening. The migration needs to focus on converting these standalone playbooks into a proper Ansible role structure with modern syntax.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server
- Sets up HTTPS with self-signed certificates
- Configures a virtual host for a "Hello World" website
- Implements security hardening (POODLE vulnerability fix)
- Uses Chef InSpec for compliance testing

## File Structure

**IMPORTANT: The current structure is not a proper Ansible role but a collection of playbooks and tests.**

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
None (using standalone playbooks instead of role tasks)

**Handler Files:**
None (handlers defined within playbooks)

**Variable Files:**
None (variables defined within playbooks)

**Meta:**
None

**Templates:**
None (using inline content variables instead)

**Static Files:**
index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml** (`website_https.yml`):
   - Sets up an Apache web server with HTTPS support
   - Installs Apache and required packages
   - Creates self-signed SSL certificates
   - Configures a virtual host for a "Hello World" website
   - Legacy patterns include short module names, unquoted booleans, and command modules without changed_when
   - Modern equivalent would use FQCN module names, quoted booleans, and proper idempotency checks

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - Applies security hardening by fixing the POODLE vulnerability
   - Updates SSL configuration to disable vulnerable protocols
   - Legacy patterns include short module names and inconsistent handler naming
   - Modern equivalent would use FQCN module names and consistent handler naming

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
| `command:` without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |
| Inconsistent handler names | Standardize handler names | website_https.yml, poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Inline templates | Move to template files | website_https.yml | For `conftext` and `webtext` |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **apache_vhost.j2**: Create from inline `conftext` variable in website_https.yml
- **index.html.j2**: Create from inline `webtext` variable in website_https.yml

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache version to install
- `website_root`: string, default "/var/www/helloworld", Document root for the website
- `ssl_cert_path`: string, default "/etc/apache2/certs", Path for SSL certificates
- `ssl_protocols`: string, default "-all +TLSv1.2", SSL protocols to enable/disable

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- tasks/install.yml
- tasks/configure.yml
- tasks/secure.yml
- handlers/main.yml
- templates/apache_vhost.j2
- templates/index.html.j2
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/apache_vhost.j2
- templates/index.html.j2

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify HTTPS configuration
curl -k https://localhost/

# Verify SSL protocols (POODLE fix)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```