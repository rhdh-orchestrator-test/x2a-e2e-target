---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for the Ansible playbooks found in this repository.

# Migration Plan: chef-and-ansible Ansible Playbooks

**TLDR**: This repository contains Ansible playbooks for configuring a secure HTTPS website on Apache with self-signed certificates and SSL/TLS hardening. Key modernization needs include using FQCN for modules, proper boolean syntax, quoted file modes, and loop modernization.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Deploys a simple "Hello World" website
- Hardens SSL/TLS configuration (disables SSLv3, enables TLSv1.2)
- Manages Apache and SSH services

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

**Task Files:**
website_https.yml
poodle_fix.yml

**Handler Files:**
(Handlers are included within the playbook files)

**Variable Files:**
(Variables are defined inline in the playbooks)

**Meta:**
(No separate meta files)

**Templates:**
(No separate template files, content is defined inline in variables)

**Static Files:**
index.html

## Module Explanation

The role performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache, curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates self-signed SSL certificates
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host with SSL
   - Legacy patterns include short module names, unquoted booleans, and command modules without changed_when
   - Modern equivalent requires FQCN, proper boolean syntax, and idempotency checks

2. **poodle_fix.yml**:
   - Hardens SSL configuration by disabling SSLv3 and enabling only TLSv1.2
   - Uses replace module to modify Apache SSL configuration
   - Legacy patterns include short module names and handlers without FQCN
   - Modern equivalent requires FQCN and proper handler naming

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
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted file mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted file mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted file mode |
| Handler name inconsistency (`apache2` vs `apache`) | Use consistent handler names | website_https.yml, poodle_fix.yml | Consistency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.9.0"
- ansible.posix: ">=1.3.0"

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

No separate template files exist, but inline templates in variables should be modernized:

- **conftext and webtext variables in website_https.yml**: No modernization needed as they use proper YAML multiline syntax with `|` character.

## Argument Specification

For a proper role conversion, these variables should be in meta/argument_specs.yml:

- `conftext`: string, default as shown in playbook, "Apache virtual host configuration"
- `webtext`: string, default as shown in playbook, "Website HTML content"

## Checks for the Migration

**Files to verify**:
- roles/apache_https/tasks/main.yml
- roles/apache_https/tasks/ssl_hardening.yml
- roles/apache_https/handlers/main.yml
- roles/apache_https/defaults/main.yml
- roles/apache_https/meta/main.yml
- roles/apache_https/meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- No separate template files to validate

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify SSL is enabled
apache2ctl -M | grep ssl

# Check SSL configuration
openssl s_client -connect localhost:443 -tls1_2

# Verify website is accessible
curl -k https://localhost/

# Check that SSLv3 is disabled
openssl s_client -connect localhost:443 -ssl3
```