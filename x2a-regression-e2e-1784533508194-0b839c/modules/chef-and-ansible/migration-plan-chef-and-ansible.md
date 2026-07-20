---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The module sets up an Apache web server with HTTPS and includes InSpec tests to verify compliance. The main modernization needs are FQCN module names, boolean syntax, and loop structure updates.

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
(Handlers are defined within the playbooks)

**Variable Files:**
(Variables are defined within the playbooks)

**Meta:**
(No meta directory/file present)

**Templates:**
(No templates directory/files present)

**Static Files:**
index.html

**Test Files:**
tests/ssh_profile.rb
tests/website_https_verify.rb

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache web server and required packages
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web directory and deploys "Hello World" website
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command module without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns: short module names, no mode for file operations
   - Modern equivalent: FQCN module names, add mode for file operations

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
| Missing `mode` | Add `mode` parameter | poodle_fix.yml | For file operations |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | "Restart apache2" vs "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None specified
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No .j2 templates are present in this module.

## Argument Specification

Since this is not a traditional Ansible role but rather a set of playbooks, argument specifications would be created if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `vhost_name`: string, default: "helloworld", description: "Name of the virtual host"
- `document_root`: string, default: "/var/www/helloworld", description: "Document root for the website"

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

# Verify the website is accessible via HTTPS
curl -k https://localhost/

# Verify SSL configuration (should only have TLSv1.2 enabled)
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests to verify compliance
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

## Migration Notes

This is not a traditional Ansible role but rather a set of playbooks with Chef InSpec tests. To properly modernize this into an Ansible role structure:

1. Create a standard role directory structure:
   - roles/apache_https/tasks/
   - roles/apache_https/handlers/
   - roles/apache_https/defaults/
   - roles/apache_https/meta/

2. Move the tasks from the playbooks into appropriate task files

3. Extract handlers into a separate handlers/main.yml file

4. Extract variables into defaults/main.yml

5. Create meta/main.yml with role metadata

6. Consider converting Chef InSpec tests to Ansible Molecule tests for a fully Ansible-native testing approach

7. Add collection dependencies in meta/requirements.yml