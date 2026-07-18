---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module:

# Migration Plan: chef-and-ansible

**TLDR**: This is a demonstration module showing how to use Chef InSpec for compliance testing with Ansible. It contains playbooks for setting up a secure HTTPS website and fixing SSL vulnerabilities. The modernization needs focus on updating module syntax to FQCN, replacing deprecated loop structures, and ensuring proper parameter quoting.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with SSL/TLS Security Hardening

**Key Operations**:
- Installs and configures Apache web server
- Sets up HTTPS with self-signed certificates
- Configures a virtual host for a "Hello World" website
- Implements SSL/TLS security hardening (POODLE vulnerability fix)
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
(No dedicated meta file)

**Templates:**
(No dedicated template files, content is defined inline in variables)

**Static Files:**
index.html

## Module Explanation

The role performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs supporting packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host with SSL
   - Legacy patterns: short module names, unquoted mode values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted mode values, command with changed_when or ansible.builtin.shell with creates/removes

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns: short module names, handlers without FQCN
   - Modern equivalent: FQCN module names, handlers with FQCN

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
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal mode |
| `command: a2dissite 000-default` | `ansible.builtin.command: a2dissite 000-default`<br>`changed_when: false` | website_https.yml | Add changed_when for idempotency |
| `command: a2ensite helloworld` | `ansible.builtin.command: a2ensite helloworld`<br>`changed_when: false` | website_https.yml | Add changed_when for idempotency |
| `command: a2enmod ssl` | `ansible.builtin.command: a2enmod ssl`<br>`changed_when: false` | website_https.yml | Add changed_when for idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this module. The templates are defined inline as variables in the playbooks.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- conftext: string, default is the VirtualHost configuration, description: "Apache virtual host configuration for HTTPS"
- webtext: string, default is the HTML content, description: "HTML content for the Hello World website"

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml
- tests/ssh_profile.rb
- tests/website_https_verify.rb

**Services to check**:
- apache2
- sshd

**Templates to validate**: None (inline variables)

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify HTTPS is enabled: `curl -k https://localhost/`
- Verify SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE fix: `openssl s_client -connect localhost:443 -ssl3` (should fail)
- Run InSpec tests: `inspec exec tests/website_https_verify.rb`
- Run SSH compliance test: `inspec exec tests/ssh_profile.rb`