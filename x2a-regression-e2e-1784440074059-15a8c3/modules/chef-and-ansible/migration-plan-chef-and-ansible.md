---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The playbooks configure an Apache web server with HTTPS support and SSL security hardening. Migration needs include FQCN module naming, boolean syntax modernization, and proper loop structures.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs Apache web server (version 2.4.41-4ubuntu3.10)
- Installs supporting packages (curl, openssl, python3-openssl)
- Configures SSL/TLS for HTTPS support with self-signed certificates
- Creates and configures a virtual host for a "Hello World" website
- Hardens SSL configuration to prevent POODLE vulnerability
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
   - Updates apt cache and installs Apache web server and dependencies
   - Creates SSL certificates directory and generates self-signed certificates
   - Configures a virtual host for HTTPS
   - Creates website content and directory structure
   - Activates the virtual host and SSL module
   - Legacy patterns found: short module names, unquoted boolean values, command modules without changed_when
   - Modern equivalent: FQCN module names, quoted boolean values, command modules with changed_when

2. **poodle_fix.yml**:
   - Hardens SSL configuration to prevent POODLE vulnerability by restricting to TLSv1.2
   - Legacy patterns found: short module names, unquoted file paths
   - Modern equivalent: FQCN module names, proper variable quoting

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
| `command: a2ensite helloworld` | `ansible.builtin.command: a2ensite helloworld`<br>`changed_when: false` | website_https.yml | Idempotency |
| `command: a2enmod ssl` | `ansible.builtin.command: a2enmod ssl`<br>`changed_when: false` | website_https.yml | Idempotency |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal modes |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal modes |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal modes |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.9.0"
- ansible.posix: ">=1.3.0"

**Role dependencies**: None explicitly defined
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No dedicated template files exist in this module. The templates are embedded as variables in the playbooks.

## Argument Specification

For a proper role conversion, the following variables should be in meta/argument_specs.yml:

- `conftext`: string, default is the VirtualHost configuration, description: "Apache virtual host configuration"
- `webtext`: string, default is the HTML content, description: "Website HTML content"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (new file to be created)
- handlers/main.yml (new file to be created)
- defaults/main.yml (new file to be created)
- templates/virtualhost.conf.j2 (new file to be created)
- templates/index.html.j2 (new file to be created)
- meta/main.yml (new file to be created)
- meta/argument_specs.yml (new file to be created)

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2 (to be created from conftext variable)
- templates/index.html.j2 (to be created from webtext variable)

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSL is enabled: `apache2ctl -M | grep ssl`
- Verify website is accessible: `curl -k https://localhost/`
- Verify SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE mitigation: `openssl s_client -connect localhost:443 -ssl3 || echo "SSLv3 disabled (good)"`