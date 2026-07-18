---
source-path: chef-and-ansible
---

Based on my analysis of the files in the chef-and-ansible directory, I'll now provide a detailed migration plan:

# Migration Plan: chef-and-ansible-playbooks

**TLDR**: This project contains Ansible playbooks for configuring a secure HTTPS website with Apache2 on Ubuntu, along with SSL/TLS security hardening. The primary modernization needs include FQCN module naming, boolean syntax updates, loop modernization, and proper quoting of file modes.

## Service Type and Configuration

**Service Type**: Web Server (Apache2)

**Key Operations**:
- Installs and configures Apache2 web server
- Sets up HTTPS with self-signed certificates
- Configures SSL/TLS security settings (disables SSLv3, enables TLSv1.2)
- Creates a simple "Hello World" website
- Manages Apache2 virtual hosts
- Includes InSpec tests for compliance verification

## File Structure

**Playbook Files**:
website_https.yml
poodle_fix.yml

**Configuration Files**:
kitchen.yml

**Test Files**:
tests/website_https_verify.rb
tests/ssh_profile.rb

**Static Files**:
index.html
README.md

## Module Explanation

The role performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache and installs Apache2 with specific version
   - Installs curl, openssl, and PyOpenSSL
   - Creates directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys HTML content
   - Disables default site and enables custom site
   - Activates SSL module in Apache
   - Legacy patterns: short module names, unquoted boolean values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, command module with changed_when

2. **poodle_fix.yml**:
   - Updates SSL configuration in Apache to disable vulnerable protocols
   - Enables only TLSv1.2 for security
   - Legacy patterns: short module names, unquoted file paths
   - Modern equivalent: FQCN module names, properly quoted paths

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
| `command: a2ensite helloworld` | `ansible.builtin.command: a2ensite helloworld`<br>`changed_when: "command_result.rc == 0"` | website_https.yml | Idempotency |
| `command: a2enmod ssl` | `ansible.builtin.command: a2enmod ssl`<br>`changed_when: "command_result.rc == 0"` | website_https.yml | Idempotency |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted file modes |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted file modes |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted file modes |
| `dest=` | `dest:` | poodle_fix.yml | YAML syntax |
| `regexp=` | `regexp:` | poodle_fix.yml | YAML syntax |
| `replace=` | `replace:` | poodle_fix.yml | YAML syntax |
| `name: Restart apache2` | `name: Restart apache` | poodle_fix.yml | Handler name consistency |

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

No Jinja2 templates (.j2 files) were found in the project. The playbooks use inline templates via variables:
- `conftext` in website_https.yml
- `webtext` in website_https.yml

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, Apache virtual host configuration template
- `webtext`: string, HTML content for the website

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml
- kitchen.yml

**Services to check**:
- apache2 (running, listening on port 443)
- sshd (running)

**Templates to validate**: None (inline templates only)

## Pre-flight checks:
```bash
# Verify Apache is running with SSL
systemctl status apache2
curl -k https://localhost/

# Verify SSL configuration
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -ssl3 # Should fail

# Verify website content
curl -k https://localhost/ | grep "Hello, world!"

# Verify Apache configuration
apache2ctl configtest
```