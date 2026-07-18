---
source-path: chef-and-ansible
---

Now I'll provide a detailed migration plan based on my analysis:

# Migration Plan: chef-and-ansible

**TLDR**: This project demonstrates using Chef InSpec for compliance testing alongside Ansible playbooks that configure a secure HTTPS website. The migration needs to focus on converting the existing playbooks into a proper Ansible role structure with modern syntax, while preserving the InSpec testing capabilities.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with SSL/TLS Security Hardening

**Key Operations**:
- Installs Apache web server
- Configures SSL/TLS with self-signed certificates
- Creates a "Hello World" virtual host
- Hardens SSL configuration to prevent POODLE vulnerability
- Includes InSpec tests for compliance validation

## File Structure

**IMPORTANT: The repository is not currently structured as an Ansible role. It contains standalone playbooks and tests.**

Current structure:
```
README.md
index.html
kitchen.yml
poodle_fix.yml
tests/ssh_profile.rb
tests/website_https_verify.rb
website_https.yml
```

Proposed role structure:
```
tasks/main.yml
tasks/ssl_hardening.yml
handlers/main.yml
defaults/main.yml
templates/helloworld.conf.j2
templates/index.html.j2
meta/main.yml
meta/argument_specs.yml
tests/inspec/website_https_verify.rb
tests/inspec/ssh_profile.rb
molecule/default/converge.yml
molecule/default/verify.yml
```

**Task Files:**
- tasks/main.yml
- tasks/ssl_hardening.yml

**Handler Files:**
- handlers/main.yml

**Variable Files:**
- defaults/main.yml

**Meta:**
- meta/main.yml
- meta/argument_specs.yml

**Templates:**
- templates/helloworld.conf.j2
- templates/index.html.j2

**Static Files:**
- None (content will be moved to templates)

## Module Explanation

The role performs operations in this order:

1. **Main tasks** (`tasks/main.yml`):
   - Updates apt cache
   - Installs Apache and required packages (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures virtual host for HTTPS
   - Creates web directory and deploys "Hello World" website
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Legacy patterns: short module names, unquoted mode values, command module without changed_when
   - Modern equivalent: FQCN module names, quoted mode values, handlers for service restarts

2. **SSL Hardening** (`tasks/ssl_hardening.yml`):
   - Updates SSL configuration to disable vulnerable protocols
   - Enables only TLSv1.2
   - Legacy patterns: short module names, no changed_when for commands
   - Modern equivalent: FQCN module names, proper handlers

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | FQCN, module moved to collection |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | FQCN, module moved to collection |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | FQCN, module moved to collection |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN, missing changed_when |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quote octal permissions |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quote octal permissions |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quote octal permissions |
| Inline templates | Move to template files | website_https.yml | Move `conftext` and `webtext` to template files |
| `command: a2dissite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Add changed_when condition |
| `command: a2ensite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Add changed_when condition |
| `command: a2enmod` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Add changed_when condition |
| `update_cache=true` | `update_cache: true` | website_https.yml | Use YAML syntax instead of key=value |
| Playbook vars | Move to defaults/main.yml | website_https.yml | Role variable structure |
| Test Kitchen | Molecule | kitchen.yml | Modern Ansible testing framework |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"

**Role dependencies**: None

**External packages**:
- apache2
- curl
- openssl
- python3-openssl

**Services managed**:
- apache2
- sshd

## Template Modernization

- **helloworld.conf.j2**: Create from inline `conftext` variable, use proper Jinja2 syntax with variable references
- **index.html.j2**: Create from inline `webtext` variable, fix HTML syntax errors (missing < in </head> tag)

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `website_root`: string, default: "/var/www/helloworld", description: "Directory path for website files"
- `ssl_cert_dir`: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `website_title`: string, default: "Test Site", description: "Title for the website"
- `website_heading`: string, default: "Hello, world!", description: "Main heading for the website"
- `website_content`: string, default: "The site is up and running", description: "Content for the website"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- tasks/ssl_hardening.yml
- handlers/main.yml
- defaults/main.yml
- templates/helloworld.conf.j2
- templates/index.html.j2
- meta/main.yml
- meta/argument_specs.yml
- molecule/default/converge.yml
- molecule/default/verify.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/helloworld.conf.j2
- templates/index.html.j2

## Pre-flight checks:
- Verify Apache is running: `systemctl status apache2`
- Verify SSL is enabled: `apache2ctl -M | grep ssl`
- Test HTTPS connection: `curl -k https://localhost/`
- Verify SSL protocols: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Run InSpec tests: `inspec exec tests/inspec/website_https_verify.rb`
- Verify SSH hardening: `inspec exec tests/inspec/ssh_profile.rb`