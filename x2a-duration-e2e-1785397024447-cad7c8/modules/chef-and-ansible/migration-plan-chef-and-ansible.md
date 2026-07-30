---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS and SSL security hardening. Migration needs include FQCN module names, boolean syntax updates, and proper loop structures.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Deploys a simple "Hello World" website
- Hardens SSL configuration to prevent POODLE vulnerability
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
(Handlers are defined within the playbooks)

**Variable Files:**
(Variables are defined within the playbooks)

**Meta:**
(No meta directory present)

**Templates:**
(No templates directory present)

**Static Files:**
index.html

**Test Files:**
tests/ssh_profile.rb
tests/website_https_verify.rb

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates self-signed SSL certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" website
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, idempotent command handling

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
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| `command: a2dissite 000-default` | `ansible.builtin.command: a2dissite 000-default`<br>`changed_when: false` | website_https.yml | Idempotency |
| `command: a2ensite helloworld` | `ansible.builtin.command: a2ensite helloworld`<br>`changed_when: false` | website_https.yml | Idempotency |
| `command: a2enmod ssl` | `ansible.builtin.command: a2enmod ssl`<br>`changed_when: false` | website_https.yml | Idempotency |
| Missing file modes | Add `mode: '0644'` | poodle_fix.yml | File permissions |
| `name: Restart apache` | `name: Restart apache2` | website_https.yml, poodle_fix.yml | Handler name consistency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None (this is a playbook, not a role)

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

No .j2 templates are present in this module.

## Argument Specification

Since this is not a traditional Ansible role but rather a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", Apache version to install
- `website_root`: string, default: "/var/www/helloworld", Website root directory
- `ssl_cert_dir`: string, default: "/etc/apache2/certs", SSL certificate directory
- `ssl_protocols`: string, default: "-all +TLSv1.2", SSL protocols to enable/disable

## Checks for the Migration

**Files to verify**:
- website_https.yml (modernized)
- poodle_fix.yml (modernized)
- tests/website_https_verify.rb
- tests/ssh_profile.rb

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify SSL is enabled
apache2ctl -M | grep ssl

# Verify website is accessible via HTTPS
curl -k https://localhost/ | grep "Hello, world!"

# Verify SSL configuration (no POODLE vulnerability)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

## Migration Notes

This is not a traditional Ansible role but rather a set of playbooks with Chef InSpec tests. To properly modernize this into an Ansible role structure:

1. Create a standard role directory structure:
   - tasks/main.yml (from website_https.yml tasks)
   - tasks/poodle_fix.yml
   - handlers/main.yml (consolidate handlers)
   - defaults/main.yml (extract variables)
   - meta/main.yml (new file with role metadata)
   - files/index.html

2. Convert Chef InSpec tests to Ansible Molecule tests:
   - Create molecule/default/verify.yml with equivalent tests
   - Replace kitchen.yml with molecule.yml

3. Consider using ansible-lint to catch additional modernization opportunities

4. Add proper documentation in README.md explaining the role's purpose and variables