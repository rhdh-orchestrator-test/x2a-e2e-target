---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of example playbooks demonstrating how to use Chef InSpec for compliance testing alongside Ansible. The module contains playbooks for configuring a secure HTTPS website and fixing SSL vulnerabilities, along with InSpec tests for verification. The migration needs focus on modernizing Ansible syntax in the playbooks.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Compliance Testing

**Key Operations**:
- Installs and configures Apache web server with HTTPS
- Generates self-signed SSL certificates
- Configures a virtual host for a "Hello World" website
- Implements security fixes for SSL/TLS (POODLE vulnerability)
- Includes Chef InSpec tests for compliance verification

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
   - Installs additional packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host with SSL
   - Legacy patterns found: short module names, unquoted booleans, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command modules with changed_when

2. **poodle_fix.yml**:
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns found: short module names, inconsistent handler names
   - Modern equivalent: FQCN module names, consistent handler names

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
| `force: yes` | `force: true` | website_https.yml | Boolean modernization |
| `command: a2dissite 000-default` | `ansible.builtin.command: a2dissite 000-default`<br>`changed_when: false` | website_https.yml | Add changed_when for idempotency |
| `command: a2ensite helloworld` | `ansible.builtin.command: a2ensite helloworld`<br>`changed_when: false` | website_https.yml | Add changed_when for idempotency |
| `command: a2enmod ssl` | `ansible.builtin.command: a2enmod ssl`<br>`changed_when: false` | website_https.yml | Add changed_when for idempotency |
| `Restart apache` vs `Restart apache2` | Use consistent handler name: `Restart apache` | website_https.yml, poodle_fix.yml | Handler name consistency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"

**Role dependencies**: None explicitly defined

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

No dedicated template files exist in this module. The templates are embedded as variables in the playbooks.

## Argument Specification

Since this is not a traditional role but a set of example playbooks, argument specifications would be created if converting to a proper role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_cert_path`: string, default: "/etc/apache2/certs", description: "Path to store SSL certificates"
- `website_content`: string, default: HTML content, description: "Content for the Hello World website"
- `vhost_config`: string, default: VirtualHost configuration, description: "Apache VirtualHost configuration"

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None (embedded in playbooks)

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify HTTPS is configured
curl -k https://localhost/

# Verify SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

## Additional Notes

This module is not a traditional Ansible role but rather a demonstration of using Chef InSpec for compliance testing alongside Ansible playbooks. To properly migrate this to a modern Ansible structure, it would be advisable to:

1. Convert the playbooks into a proper role structure with tasks/, handlers/, defaults/, etc.
2. Move the embedded templates to the templates/ directory
3. Create proper variable files in defaults/ and vars/
4. Create meta/main.yml with proper role metadata
5. Keep the InSpec tests in a tests/ directory but consider adding Ansible-native tests as well

The primary focus of this module is demonstrating the integration between Ansible for configuration management and Chef InSpec for compliance testing, which is a valid approach even in modern Ansible environments.