---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this project.

# Migration Plan: chef-and-ansible

**TLDR**: This project demonstrates using Chef InSpec for compliance testing alongside Ansible playbooks that configure a secure Apache web server with HTTPS. The migration needs to focus on modernizing the Ansible playbooks by implementing FQCN module names, proper boolean syntax, and structured loop patterns while maintaining the integration with Chef InSpec for compliance testing.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server
- Sets up HTTPS with self-signed certificates
- Configures SSL/TLS security settings (disables SSLv3, enables TLSv1.2)
- Creates a simple "Hello World" website
- Implements security hardening for SSH and Apache

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
(Handlers are included within the playbook files)

**Variable Files:**
(Variables are defined inline within the playbooks)

**Meta:**
(No dedicated meta file)

**Templates:**
(No dedicated template files, content is defined inline)

**Static Files:**
index.html

## Module Explanation

The role performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache web server with specific version
   - Installs supporting packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates web directory and deploys "Hello World" website
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted booleans, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted booleans, command modules with changed_when
   - Ansible module mapping: apt → ansible.builtin.apt, file → ansible.builtin.file, etc.

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable SSLv3 and enable TLSv1.2
   - Restarts Apache and SSH services
   - Legacy patterns: short module names, no changed_when for command modules
   - Modern equivalent: FQCN module names, proper changed_when conditions
   - Ansible module mapping: replace → ansible.builtin.replace

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
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| `command: a2dissite 000-default` | `ansible.builtin.command: a2dissite 000-default`<br>`changed_when: false` | website_https.yml | Idempotency |
| `command: a2ensite helloworld` | `ansible.builtin.command: a2ensite helloworld`<br>`changed_when: false` | website_https.yml | Idempotency |
| `command: a2enmod ssl` | `ansible.builtin.command: a2enmod ssl`<br>`changed_when: false` | website_https.yml | Idempotency |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal modes |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal modes |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal modes |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this project. The templates are defined inline as variables in the playbooks.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- conftext: string, default is the VirtualHost configuration, description: "Apache virtual host configuration for HTTPS"
- webtext: string, default is the HTML content, description: "HTML content for the Hello World website"

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml
- kitchen.yml (for integration with InSpec)
- tests/website_https_verify.rb
- tests/ssh_profile.rb

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- Inline templates in website_https.yml

## Pre-flight checks:
```bash
# Verify Apache is running with SSL
systemctl status apache2
apache2ctl -M | grep ssl

# Verify HTTPS is working
curl -k https://localhost/ | grep "Hello, world!"

# Verify SSL/TLS configuration
openssl s_client -connect localhost:443 -ssl3 || echo "SSLv3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```