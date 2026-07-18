---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS and implement security fixes. The migration needs to focus on converting these standalone playbooks into a proper Ansible role structure with modern syntax.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Compliance Testing

**Key Operations**:
- Installs and configures Apache web server with HTTPS support
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Implements security fixes for SSL/TLS (POODLE vulnerability)
- Uses Chef InSpec for compliance testing

## File Structure

**IMPORTANT: The current structure is not a proper Ansible role but rather standalone playbooks and tests.**

```
README.md
index.html
kitchen.yml
poodle_fix.yml
tests/ssh_profile.rb
tests/website_https_verify.rb
website_https.yml
```

**Current Structure (Not a Role):**
- Playbooks: website_https.yml, poodle_fix.yml
- Tests: tests/website_https_verify.rb, tests/ssh_profile.rb
- Configuration: kitchen.yml
- Documentation: README.md
- Sample content: index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache web server and dependencies
   - Creates SSL certificates directory
   - Generates SSL key, CSR, and self-signed certificate
   - Configures a virtual host for HTTPS
   - Creates a "Hello World" website
   - Enables SSL module and the virtual host
   - Legacy patterns found: short module names, unquoted booleans, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command modules with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns found: short module names, inconsistent handler names
   - Modern equivalent: FQCN module names, consistent handler names

3. **Tests**:
   - Chef InSpec tests for HTTPS functionality and SSH security compliance
   - These will need to be converted to Ansible-native testing methods

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
| Command without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |
| Inconsistent handler names | Consistent handler names | website_https.yml, poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Standalone playbooks | Role structure | All files | Project structure |
| Chef InSpec tests | Ansible Molecule tests | tests/* | Testing framework |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: '>=1.0.0'
- ansible.posix: '>=1.0.0'

**Role dependencies**: None specified in current files
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **No traditional .j2 templates exist in the current structure**
- The inline templates in the playbooks (conftext, webtext) should be moved to proper template files

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `vhost_name`: string, default: "helloworld", description: "Name of the virtual host"
- `document_root`: string, default: "/var/www/helloworld", description: "Document root for the website"
- `ssl_cert_dir`: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"

## Checks for the Migration

**Files to verify in the new role structure**:
- tasks/main.yml
- tasks/install.yml
- tasks/configure.yml
- tasks/secure.yml
- handlers/main.yml
- templates/vhost.conf.j2
- templates/index.html.j2
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml
- molecule/default/converge.yml
- molecule/default/verify.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/vhost.conf.j2 (converted from inline conftext)
- templates/index.html.j2 (converted from inline webtext)

## Pre-flight checks:
```
# Check Apache installation
systemctl status apache2

# Verify SSL configuration
apache2ctl -M | grep ssl

# Test HTTPS connectivity
curl -k https://localhost/

# Verify SSL protocols (should only allow TLSv1.2)
nmap --script ssl-enum-ciphers -p 443 localhost

# Check virtual host configuration
apache2ctl -S

# Validate configuration files
apache2ctl configtest
```