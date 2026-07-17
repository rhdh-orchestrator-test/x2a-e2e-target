---
source-path: chef-and-ansible
---

Based on my analysis, I'll now provide a migration plan for this module.

# Migration Plan: chef-and-ansible

**TLDR**: This is not a traditional Ansible role but rather a set of Ansible playbooks with Chef InSpec tests for compliance automation. The module configures an Apache web server with HTTPS support and includes security hardening. The main modernization needs include FQCN module names, boolean syntax updates, and proper loop structures.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs Apache web server
- Configures HTTPS with self-signed certificates
- Deploys a simple "Hello World" website
- Implements security hardening (disables SSLv3, enables TLSv1.2)
- Uses Chef InSpec for compliance testing

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
(No meta directory)

**Templates:**
(No templates directory, content is defined inline)

**Static Files:**
index.html

## Module Explanation

The module performs operations in this order:

1. **website_https.yml**:
   - Updates apt cache
   - Installs Apache web server and dependencies (curl, openssl, PyOpenSSL)
   - Creates directory for SSL certificates
   - Generates SSL key, CSR, and self-signed certificate
   - Configures Apache virtual host for HTTPS
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the new virtual host
   - Enables SSL module in Apache
   - Ansible module mapping: short names → FQCN (apt → ansible.builtin.apt, file → ansible.builtin.file, etc.)

2. **poodle_fix.yml**:
   - Updates SSL configuration to disable vulnerable protocols and enable TLSv1.2
   - Restarts Apache and SSH services
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
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| Missing file modes | Add explicit modes | website_https.yml, poodle_fix.yml | For file operations |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No traditional Jinja2 templates are used in this module. Content is defined inline using YAML multiline strings.

## Argument Specification

Since this is not a traditional Ansible role but rather a set of playbooks, argument specifications would be defined if converting to a role:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", Apache version to install
- `website_root`: string, default: "/var/www/helloworld", Website root directory
- `ssl_cert_path`: string, default: "/etc/apache2/certs", Path for SSL certificates
- `website_content`: string, default: HTML content, Website content to deploy
- `vhost_config`: string, default: VirtualHost configuration, Apache virtual host configuration

## Checks for the Migration

**Files to verify**:
- website_https.yml
- poodle_fix.yml
- tests/website_https_verify.rb
- tests/ssh_profile.rb

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- Inline templates in website_https.yml (conftext and webtext variables)

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify HTTPS configuration
curl -k https://localhost/

# Verify SSL protocols
openssl s_client -connect localhost:443 -ssl3 || echo "SSLv3 disabled (good)"
openssl s_client -connect localhost:443 -tls1_2

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```