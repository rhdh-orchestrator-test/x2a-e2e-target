---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this Ansible content.

# Migration Plan: chef-and-ansible

**TLDR**: This repository contains Ansible playbooks for configuring a secure Apache web server with HTTPS support, along with Chef InSpec tests for validation. The main modernization needs include updating module syntax to FQCN format, converting boolean values to true/false, quoting octal modes, and improving idempotency for command modules.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server (version 2.4.41-4ubuntu3.10)
- Installs supporting packages (curl, openssl, python3-openssl)
- Configures SSL/TLS for HTTPS support
- Creates and deploys self-signed certificates
- Configures a virtual host for a "Hello World" website
- Hardens SSL/TLS configuration (disables SSLv3, enables TLSv1.2)
- Manages Apache and SSH services

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

**Playbook Files:**
- website_https.yml
- poodle_fix.yml

**Test Files:**
- tests/website_https_verify.rb
- tests/ssh_profile.rb

**Configuration Files:**
- kitchen.yml

**Documentation:**
- README.md
- index.html

## Module Explanation

The repository performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache web server and supporting packages
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web content directory and deploys "Hello World" page
   - Disables default site and enables custom virtual host
   - Enables SSL module in Apache
   - Restarts Apache and SSH services as needed

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Restarts Apache and SSH services

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `apt: update_cache=true` | `ansible.builtin.apt: update_cache=true` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quote octal modes |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quote octal modes |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quote octal modes |
| `command: a2dissite 000-default` | `ansible.builtin.command: a2dissite 000-default` with `changed_when` | website_https.yml | Add idempotency check |
| `command: a2ensite helloworld` | `ansible.builtin.command: a2ensite helloworld` with `changed_when` | website_https.yml | Add idempotency check |
| `command: a2enmod ssl` | `ansible.builtin.command: a2enmod ssl` with `changed_when` | website_https.yml | Add idempotency check |
| `update_cache=true` | `update_cache: true` | website_https.yml | Use YAML dictionary format |
| `name: Restart apache` | `name: Restart apache2` | website_https.yml | Inconsistent handler name |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**External packages**:
- apache2=2.4.41-4ubuntu3.10
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

No .j2 templates are present in this repository. The playbooks use inline templates via variables.

## Argument Specification

For a proper role conversion, these variables should be in meta/argument_specs.yml:

- `conftext`: string, default is the Apache virtual host configuration, description: "Apache virtual host configuration for HTTPS"
- `webtext`: string, default is the HTML content, description: "Content of the Hello World web page"

## Checks for the Migration

**Files to verify**:
- roles/apache_https/tasks/main.yml
- roles/apache_https/handlers/main.yml
- roles/apache_https/defaults/main.yml
- roles/apache_https/meta/main.yml
- roles/apache_https/meta/argument_specs.yml
- roles/ssl_hardening/tasks/main.yml
- roles/ssl_hardening/handlers/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- None (inline templates only)

## Pre-flight checks:
```
# Verify Apache is installed and running
systemctl status apache2

# Verify HTTPS is configured
curl -k https://localhost/

# Verify SSL/TLS configuration
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail

# Verify Apache configuration
apache2ctl -t

# Check virtual host configuration
ls -la /etc/apache2/sites-enabled/
```