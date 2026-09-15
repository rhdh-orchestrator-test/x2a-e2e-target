---
source-path: chef-and-ansible/website_https.yml
---

I can see this is a playbook file rather than a traditional Ansible role structure. Let me analyze this Apache HTTPS website playbook for modernization. Based on my analysis, this is a single playbook file that needs to be converted into a proper Ansible role structure.

# Migration Plan: apache-https-website

**TLDR**: This playbook configures an Apache web server with HTTPS support using self-signed certificates and deploys a simple "Hello World" website. Key modernization needs include converting from playbook to role structure, updating module syntax to use FQCNs, fixing file permissions syntax, improving idempotency with proper change detection, and adding proper error handling.

## Service Type and Configuration

**Service Type**: Web Server (Apache HTTPS)

**Key Operations**:
- Install Apache2 web server with specific version
- Install SSL/TLS dependencies (curl, openssl, python3-openssl)
- Generate self-signed SSL certificates (private key, CSR, certificate)
- Configure HTTPS virtual host for custom website
- Deploy static HTML content
- Enable SSL module and configure site activation
- Manage Apache service lifecycle

## File Structure

**Current Structure** (single playbook):
```
website_https.yml
```

**Target Role Structure** (to be created):
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
   - Updates apt cache using legacy `apt: update_cache=true` syntax
   - Installs specific Apache2 version with legacy parameter format
   - Installs SSL dependencies using modern list format
   - Legacy patterns: Short module names, inline parameters
   - Modern equivalent: FQCN modules with proper YAML structure

2. **SSL Certificate Generation** (`website_https.yml` tasks 4-7):
   - Creates certificate directory with unquoted octal mode
   - Generates private key, CSR, and self-signed certificate
   - Uses community.crypto collection modules (already modern)
   - Legacy patterns: Unquoted file modes
   - Modern equivalent: Quoted octal modes

3. **Website Configuration** (`website_https.yml` tasks 8-10):
   - Deploys virtual host configuration using inline content
   - Creates document root directory
   - Deploys HTML content using inline variables
   - Legacy patterns: Inline content instead of templates
   - Modern equivalent: Jinja2 templates with proper variable structure

4. **Service Configuration** (`website_https.yml` tasks 11-13):
   - Disables default site and enables custom site using command module
   - Enables SSL module using command module
   - Missing `changed_when` conditions for idempotency
   - Legacy patterns: Command modules without change detection
   - Modern equivalent: Apache modules with proper change detection

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | tasks/main.yml | FQCN |
| `file:` | `ansible.builtin.file:` | tasks/main.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | tasks/main.yml | FQCN |
| `command:` | `ansible.builtin.command:` | tasks/main.yml | FQCN |
| `apt: update_cache=true` | `ansible.builtin.apt: update_cache: true` | tasks/main.yml | YAML syntax |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted octals |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted octals |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted octals |
| Inline `content:` | Template files | tasks/main.yml | Template modernization |
| `command:` without `changed_when` | Add `changed_when` conditions | tasks/main.yml | Idempotency |
| Playbook structure | Role structure | All files | Project structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

**Templates to create:**
- **helloworld.conf.j2**: Convert inline `conftext` variable to proper Jinja2 template with configurable parameters
- **index.html.j2**: Convert inline `webtext` variable to template with configurable title and content

**Variables to template:**
- SSL certificate paths (make configurable)
- Document root path
- Virtual host configuration
- Website content and title

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache package version
- `site_name`: string, default "helloworld", Site identifier
- `document_root`: string, default "/var/www/helloworld", Website document root
- `ssl_cert_path`: string, default "/etc/apache2/certs", SSL certificate directory
- `common_name`: string, default "{{ ansible_fqdn }}", SSL certificate common name
- `website_title`: string, default "Test Site", HTML page title
- `website_content`: string, default "Hello, world!", Main page content
- `ssl_key_size`: integer, default 2048, Private key size
- `cert_valid_days`: integer, default 365, Certificate validity period

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- templates/helloworld.conf.j2
- templates/index.html.j2
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2 (running and enabled)
- SSL certificate validity
- Virtual host configuration

**Templates to validate**:
- Apache virtual host configuration syntax
- HTML content rendering

## Pre-flight checks:
```bash
# Verify Apache is running with SSL
systemctl status apache2
apache2ctl -S

# Check SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify site accessibility
curl -k https://localhost
curl -I -k https://localhost

# Check Apache modules
apache2ctl -M | grep ssl

# Verify virtual host configuration
apache2ctl -t
```

**Critical Modernization Notes:**
1. **Handler Issue**: The current playbook has a handler "Restart sshd" that's triggered by SSL module activation - this appears to be an error and should only restart Apache
2. **Idempotency**: Command modules need `changed_when` conditions to prevent unnecessary changes
3. **Security**: Consider using Let's Encrypt instead of self-signed certificates for production
4. **Flexibility**: Convert hardcoded values to variables for reusability
5. **Error Handling**: Add block/rescue/always for certificate generation tasks
6. **Package Pinning**: Consider making Apache version configurable rather than hardcoded