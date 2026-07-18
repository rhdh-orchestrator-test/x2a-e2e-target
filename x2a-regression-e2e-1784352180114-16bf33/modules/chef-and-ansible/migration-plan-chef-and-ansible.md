---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for the Ansible content in this repository.

# Migration Plan: chef-and-ansible

**TLDR**: This repository contains Ansible playbooks for configuring an Apache web server with HTTPS support and SSL security hardening. The main modernization needs include updating module syntax to FQCN format, replacing deprecated loop syntax, and ensuring proper boolean formatting.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server
- Configures SSL/TLS for secure HTTPS connections
- Creates self-signed certificates
- Deploys a simple "Hello World" website
- Hardens SSL configuration to prevent POODLE vulnerability
- Manages Apache virtual hosts

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
website_https.yml
poodle_fix.yml

**Configuration Files:**
kitchen.yml

**Documentation:**
README.md

**Test Files:**
tests/website_https_verify.rb
tests/ssh_profile.rb

**Static Files:**
index.html

## Module Explanation

The repository performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs supporting packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web directory and deploys "Hello World" website
   - Disables default site and enables custom site
   - Enables SSL module in Apache
   - Includes handlers for restarting Apache and SSH services

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Includes handlers for restarting Apache and SSH services

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
| Unquoted file mode `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal mode |
| Unquoted file mode `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal mode |
| Unquoted file mode `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal mode |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| `command: a2dissite 000-default` | Add `changed_when: false` or appropriate condition | website_https.yml | Idempotency |
| `command: a2ensite helloworld` | Add `changed_when: false` or appropriate condition | website_https.yml | Idempotency |
| `command: a2enmod ssl` | Add `changed_when: false` or appropriate condition | website_https.yml | Idempotency |
| `name: Restart apache` | Consistent handler name | website_https.yml, poodle_fix.yml | Handler name mismatch (apache vs apache2) |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

No .j2 templates are present in the repository. The playbooks use inline templates via variables (`conftext` and `webtext`).

## Argument Specification

For a proper role conversion, the following variables should be documented in meta/argument_specs.yml:

- `conftext`: string, default is the Apache virtual host configuration
  - Description: Apache virtual host configuration for HTTPS
- `webtext`: string, default is the HTML content
  - Description: Content of the Hello World website

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (new file to create)
- handlers/main.yml (new file to create)
- defaults/main.yml (new file to create)
- meta/main.yml (new file to create)
- meta/argument_specs.yml (new file to create)

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- None (inline templates used)

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify HTTPS is enabled: `curl -k https://localhost/`
- Verify SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify SSL protocols: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify Apache virtual host: `apache2ctl -S`
- Verify certificate: `openssl x509 -in /etc/apache2/certs/apache.crt -text -noout`