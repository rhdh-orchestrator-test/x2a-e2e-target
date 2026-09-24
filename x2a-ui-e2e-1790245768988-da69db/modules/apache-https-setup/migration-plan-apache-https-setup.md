---
source-path: chef-and-ansible/website_https.yml
---

I can see this is a playbook file, not a traditional Ansible role structure. Let me analyze the content and provide a migration plan to convert this playbook into a modern Ansible role.

# Migration Plan: apache-https-setup

**TLDR**: This legacy playbook configures Apache with HTTPS support, creates a self-signed SSL certificate, and deploys a simple "Hello World" website. Key modernization needs include converting from playbook to role structure, adding FQCN module names, fixing file permissions syntax, improving idempotency with proper change detection, and replacing command modules with more appropriate alternatives.

## Service Type and Configuration

**Service Type**: Web Server

**Key Operations**:
- Install Apache2 web server with specific version
- Install SSL/TLS support packages (curl, openssl, python3-openssl)
- Generate self-signed SSL certificates (private key, CSR, certificate)
- Configure HTTPS virtual host for a test website
- Deploy static HTML content
- Enable SSL module and configure site activation
- Manage Apache service restart through handlers

## File Structure

**Task Files:**
```
tasks/main.yml
```

**Handler Files:**
```
handlers/main.yml
```

**Variable Files:**
```
defaults/main.yml
vars/main.yml
```

**Meta:**
```
meta/main.yml
meta/argument_specs.yml
```

**Templates:**
```
templates/virtualhost.conf.j2
templates/index.html.j2
```

**Static Files:**
```
files/.gitkeep
```

## Module Explanation

The role performs operations in this order:

1. **Package Management** (`tasks/main.yml`):
   - Updates apt cache and installs Apache2 with specific version
   - Installs SSL-related packages (curl, openssl, python3-openssl)
   - Legacy patterns: Short module names, unquoted mode values
   - Modern equivalent: FQCN modules, quoted file permissions

2. **SSL Certificate Generation** (`tasks/main.yml`):
   - Creates certificate directory with proper permissions
   - Generates private key, CSR, and self-signed certificate
   - Legacy patterns: Unquoted mode values, missing FQCN
   - Modern equivalent: community.crypto collection modules with FQCN

3. **Web Content Deployment** (`tasks/main.yml`):
   - Configures virtual host using inline content variable
   - Creates web directory and deploys HTML content
   - Legacy patterns: Inline content in playbook, unquoted modes
   - Modern equivalent: Template files, quoted permissions

4. **Apache Configuration** (`tasks/main.yml`):
   - Disables default site and enables custom site
   - Activates SSL module
   - Legacy patterns: command modules without changed_when, inconsistent handler naming
   - Modern equivalent: apache2_module for SSL, proper idempotency checks

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | tasks/main.yml | FQCN |
| `file:` | `ansible.builtin.file:` | tasks/main.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | tasks/main.yml | FQCN |
| `command:` | `ansible.builtin.command:` | tasks/main.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | tasks/main.yml | Collection migration |
| `openssl_csr:` | `community.crypto.openssl_csr:` | tasks/main.yml | Collection migration |
| `openssl_certificate:` | `community.crypto.x509_certificate:` | tasks/main.yml | Module renamed |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted octal values |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted octal values |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted octal values |
| `update_cache=true` | `update_cache: true` | tasks/main.yml | YAML syntax |
| `command: a2enmod ssl` | `community.general.apache2_module:` | tasks/main.yml | Proper module |
| `command: a2ensite` | `community.general.apache2_site:` | tasks/main.yml | Proper module |
| `command: a2dissite` | `community.general.apache2_site:` | tasks/main.yml | Proper module |
| Inline content vars | Template files | tasks/main.yml | Better maintainability |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- community.general: ">=5.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd (incorrectly triggered)

## Template Modernization

- **virtualhost.conf.j2**: Convert inline `conftext` variable to proper Jinja2 template with configurable parameters
- **index.html.j2**: Convert inline `webtext` variable to template with customizable content

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache package version
- `site_name`: string, default "helloworld", Virtual host site name
- `document_root`: string, default "/var/www/helloworld", Web document root
- `ssl_cert_path`: string, default "/etc/apache2/certs", SSL certificate directory
- `common_name`: string, default "{{ ansible_fqdn }}", SSL certificate common name
- `site_title`: string, default "Test Site", HTML page title
- `site_content`: string, default "Hello, world!", Main page content

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml
- templates/virtualhost.conf.j2
- templates/index.html.j2

**Services to check**: apache2 (remove incorrect sshd handler)
**Templates to validate**: virtualhost.conf.j2, index.html.j2

## Pre-flight checks:
```bash
# Verify Apache is running and configured
systemctl status apache2
apache2ctl configtest

# Check SSL certificate validity
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify HTTPS site accessibility
curl -k https://localhost/

# Check enabled sites and modules
a2ensite -l
a2enmod -l | grep ssl
```

**Critical Issues to Address:**
1. **Handler Error**: "Restart sshd" handler is incorrectly triggered by SSL module activation - should only restart apache2
2. **Idempotency**: Command modules need `changed_when` conditions
3. **Security**: Self-signed certificates should have configurable validity period
4. **Module Migration**: `openssl_certificate` → `community.crypto.x509_certificate` with parameter changes
5. **Structure**: Convert from playbook to proper role structure with separate files for better maintainability