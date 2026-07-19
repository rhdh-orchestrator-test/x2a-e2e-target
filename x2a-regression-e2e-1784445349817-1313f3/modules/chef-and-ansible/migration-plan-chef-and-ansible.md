---
source-path: chef-and-ansible
---

Based on my analysis, I'll now create a migration plan for this project.

# Migration Plan: chef-and-ansible

**TLDR**: This project demonstrates using Chef InSpec for compliance testing with Ansible playbooks that configure a secure Apache web server with HTTPS. The migration needs to focus on modernizing Ansible syntax in the playbooks, including FQCN module names, proper boolean values, and loop structures while maintaining the integration with Chef InSpec for compliance testing.

## Service Type and Configuration

**Service Type**: Web Server (Apache) with Security Hardening

**Key Operations**:
- Installs and configures Apache web server
- Sets up HTTPS with self-signed certificates
- Configures SSL/TLS security settings (disables SSLv3, enables TLSv1.2)
- Deploys a simple "Hello World" website
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
- website_https.yml
- poodle_fix.yml

**Handler Files:**
- Handlers are embedded in the playbooks (website_https.yml, poodle_fix.yml)

**Variable Files:**
- Variables are embedded in the playbooks

**Templates:**
- No separate template files (templates are embedded as variables in playbooks)

**Static Files:**
- index.html

**Test Files:**
- tests/website_https_verify.rb
- tests/ssh_profile.rb

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
   - Includes handlers to restart Apache and SSH services

2. **poodle_fix.yml**:
   - Modifies Apache SSL configuration to disable SSLv3 and enable only TLSv1.2
   - Includes handlers to restart Apache and SSH services

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
| `become: yes` | `become: true` | website_https.yml, poodle_fix.yml | Boolean syntax |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | For command modules |
| Missing `mode` | Add `mode: '0644'` | Some file operations | File permissions |
| `name: apache2` | `name: apache2` | website_https.yml, poodle_fix.yml | Handler name inconsistency (apache vs apache2) |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"
- ansible.posix: ">=1.0.0"

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

No separate template files exist in this project. Templates are embedded as variables in the playbooks:

- **website_https.yml**: Contains `conftext` and `webtext` variables that should be moved to template files
  - Create `templates/virtualhost.conf.j2` for Apache configuration
  - Create `templates/index.html.j2` for the website content

## Argument Specification

Variables that should be in meta/argument_specs.yml:

- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `ssl_cert_path`: string, default: "/etc/apache2/certs", description: "Path to store SSL certificates"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `virtual_host_name`: string, default: "helloworld", description: "Name of the virtual host"
- `document_root`: string, default: "/var/www/helloworld", description: "Document root for the website"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- tasks/install.yml
- tasks/configure.yml
- tasks/ssl.yml
- handlers/main.yml
- templates/virtualhost.conf.j2
- templates/index.html.j2
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/virtualhost.conf.j2
- templates/index.html.j2

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify SSL configuration
apache2ctl -M | grep ssl

# Test HTTPS connectivity
curl -k https://localhost/

# Verify SSL protocols
nmap --script ssl-enum-ciphers -p 443 localhost

# Run InSpec tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```