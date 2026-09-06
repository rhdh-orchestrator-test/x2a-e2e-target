---
source-path: chef-and-ansible/website_https.yml
---

I can see that `website_https.yml` is a single playbook file, not an Ansible role structure. However, the user is asking to analyze the module 'ansible-apache-https' for migration to Ansible. This appears to be a playbook that needs to be converted into a proper Ansible role structure. Let me analyze the content and create a migration plan.

# Migration Plan: ansible-apache-https

**TLDR**: This is a single playbook file that configures Apache with HTTPS support, creates SSL certificates, and deploys a simple "Hello World" website. The main modernization needs include converting from playbook to role structure, updating module syntax to use FQCNs, fixing file permissions syntax, improving idempotency with proper change detection, and replacing command modules with more appropriate alternatives.

## Service Type and Configuration

**Service Type**: Web Server (Apache HTTPS)

**Key Operations**:
- Install Apache2 web server with specific version
- Install SSL/TLS support packages (curl, openssl, python3-openssl)
- Generate self-signed SSL certificates (private key, CSR, certificate)
- Configure HTTPS virtual host for a "Hello World" website
- Deploy static HTML content
- Enable SSL module and configure site activation
- Manage Apache service restart through handlers

## File Structure

**Current Structure** (Single playbook):
```
website_https.yml
```

**Target Role Structure** (To be created):
```
tasks/main.yml
handlers/main.yml
templates/helloworld.conf.j2
templates/index.html.j2
defaults/main.yml
vars/main.yml
meta/main.yml
meta/argument_specs.yml
```

## Module Explanation

The playbook performs operations in this order:

1. **Package Management** (`website_https.yml` tasks 1-3):
   - Updates apt cache using legacy syntax
   - Installs specific Apache2 version
   - Installs SSL-related packages
   - Legacy patterns: `apt: update_cache=true`, missing FQCN
   - Modern equivalent: `ansible.builtin.apt:` with proper parameters

2. **SSL Certificate Generation** (`website_https.yml` tasks 4-7):
   - Creates certificate directory with unquoted mode
   - Generates private key, CSR, and self-signed certificate
   - Legacy patterns: `mode: 0640` (unquoted), missing FQCN for crypto modules
   - Modern equivalent: `community.crypto.*` modules with quoted modes

3. **Apache Configuration** (`website_https.yml` tasks 8-11):
   - Deploys virtual host configuration using inline content
   - Creates document root directory
   - Deploys HTML content using inline variables
   - Legacy patterns: inline content instead of templates, unquoted modes
   - Modern equivalent: Use templates with proper file permissions

4. **Service Configuration** (`website_https.yml` tasks 12-14):
   - Disables default site and enables custom site using command modules
   - Enables SSL module using command module
   - Legacy patterns: `command:` without `changed_when`, missing idempotency
   - Modern equivalent: `ansible.builtin.apache2_module` and proper change detection

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt: update_cache=true` | `ansible.builtin.apt: update_cache: true` | tasks/main.yml | FQCN + parameter syntax |
| `apt:` | `ansible.builtin.apt:` | tasks/main.yml | FQCN |
| `file:` | `ansible.builtin.file:` | tasks/main.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | tasks/main.yml | FQCN |
| `command:` | `ansible.builtin.command:` | tasks/main.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | tasks/main.yml | Collection migration |
| `openssl_csr:` | `community.crypto.openssl_csr:` | tasks/main.yml | Collection migration |
| `openssl_certificate:` | `community.crypto.x509_certificate:` | tasks/main.yml | Module name change + collection |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted octal permissions |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted octal permissions |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted octal permissions |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Inline content vars | Template files | tasks/main.yml | Use .j2 templates |
| `command: a2dissite` | `ansible.builtin.apache2_module:` | tasks/main.yml | Proper Apache module management |
| `command: a2ensite` | `ansible.builtin.apache2_module:` | tasks/main.yml | Proper Apache module management |
| `command: a2enmod` | `ansible.builtin.apache2_module:` | tasks/main.yml | Proper Apache module management |
| Missing `changed_when` | Add `changed_when` conditions | tasks/main.yml | Idempotency improvement |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

**Templates to create**:
- **helloworld.conf.j2**: Convert inline `conftext` variable to proper Jinja2 template with configurable parameters
- **index.html.j2**: Convert inline `webtext` variable to template with customizable content

**Variables to template**:
- Document root path: `/var/www/helloworld` → `{{ apache_document_root }}`
- SSL certificate paths → `{{ ssl_cert_path }}`, `{{ ssl_key_path }}`
- Site title and content → configurable variables

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", Apache package version
- `apache_document_root`: string, default: "/var/www/helloworld", Document root path
- `ssl_cert_dir`: string, default: "/etc/apache2/certs", SSL certificate directory
- `ssl_cert_path`: string, default: "/etc/apache2/certs/apache.crt", SSL certificate file
- `ssl_key_path`: string, default: "/etc/apache2/certs/apache.key", SSL private key file
- `ssl_csr_path`: string, default: "/etc/apache2/certs/apache.csr", SSL CSR file
- `site_name`: string, default: "helloworld", Apache site name
- `ssl_common_name`: string, default: "{{ ansible_facts['fqdn'] }}", SSL certificate common name
- `website_title`: string, default: "Test Site", HTML page title
- `website_content`: string, default: "Hello, world!", Main page content

## Checks for the Migration

**Files to verify**:
- tasks/main.yml (modernized task syntax)
- handlers/main.yml (service restart handlers)
- templates/helloworld.conf.j2 (Apache virtual host template)
- templates/index.html.j2 (HTML content template)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 service status and configuration
- SSL certificate validity
- Website accessibility on HTTPS

**Templates to validate**:
- helloworld.conf.j2 syntax validation
- index.html.j2 HTML validation

## Pre-flight checks:
```bash
# Verify Apache is running and configured
sudo systemctl status apache2
sudo apache2ctl configtest

# Check SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Test HTTPS connectivity
curl -k https://localhost/

# Verify site configuration
sudo apache2ctl -S

# Check enabled modules
sudo apache2ctl -M | grep ssl
```

**Critical Migration Notes**:
1. The `openssl_certificate` module has been replaced with `x509_certificate` in community.crypto collection
2. Command modules for Apache site/module management should be replaced with `apache2_module` where possible
3. All file permission modes must be quoted to prevent octal interpretation issues
4. The playbook structure needs complete conversion to role format with proper variable templating
5. Handler for "Restart sshd" appears unrelated to Apache configuration and should be reviewed for necessity