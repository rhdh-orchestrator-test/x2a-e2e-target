---
source-path: chef-and-ansible/website_https.yml
---

I can see this is a single playbook file, not a traditional Ansible role structure. Let me analyze this playbook for modernization. Based on my analysis, I can see this is actually a playbook that needs to be converted into a proper Ansible role structure.

# Migration Plan: apache-https-website

**TLDR**: This is a single playbook that configures Apache with HTTPS support, creates a simple "Hello World" website with SSL certificates, and manages virtual hosts. The main modernization needs include converting from playbook to role structure, updating module syntax to use FQCNs, fixing file permissions syntax, improving idempotency with proper change detection, and adding proper error handling.

## Service Type and Configuration

**Service Type**: Web Server

**Key Operations**:
- Install Apache2 web server with specific version
- Install SSL/TLS support packages (curl, openssl, python3-openssl)
- Generate self-signed SSL certificates (private key, CSR, certificate)
- Configure HTTPS virtual host for a "Hello World" website
- Deploy static HTML content
- Manage Apache site activation/deactivation
- Enable SSL module
- Restart services when configuration changes

## File Structure

**Current Structure** (single playbook):
```
website_https.yml
```

**Target Role Structure**:
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

1. **Package Management** (`website_https.yml`):
   - Updates apt cache using legacy syntax
   - Installs Apache2 with pinned version
   - Installs SSL-related packages
   - Legacy patterns: short module names, unquoted mode values

2. **SSL Certificate Generation** (`website_https.yml`):
   - Creates certificate directory with incorrect permissions
   - Generates private key, CSR, and self-signed certificate
   - Legacy patterns: unquoted file modes, missing FQCN

3. **Web Server Configuration** (`website_https.yml`):
   - Deploys virtual host configuration using inline content
   - Creates document root directory
   - Deploys HTML content using inline variables
   - Legacy patterns: inline content instead of templates, unquoted modes

4. **Apache Site Management** (`website_https.yml`):
   - Disables default site and enables custom site using command module
   - Enables SSL module
   - Legacy patterns: command module without changed_when, inconsistent handler naming

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN required |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN required |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN required |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN required |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | Collection migration |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | Collection migration |
| `openssl_certificate:` | `community.crypto.x509_certificate:` | website_https.yml | Module renamed in collection |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quote octal values |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quote octal values |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quote octal values |
| `update_cache=true` | `update_cache: true` | website_https.yml | YAML syntax |
| `force: yes` | `force: true` | website_https.yml | Boolean modernization |
| `become: yes` | `become: true` | website_https.yml | Boolean modernization |
| Inline content | Template files | website_https.yml | Use templates for maintainability |
| `command` without `changed_when` | Add `changed_when` logic | website_https.yml | Improve idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

**New templates to create:**
- **helloworld.conf.j2**: Apache virtual host configuration (convert from inline `conftext` variable)
- **index.html.j2**: HTML content (convert from inline `webtext` variable)

**Variables to template:**
- `apache_document_root`: "/var/www/helloworld"
- `apache_ssl_cert_path`: "/etc/apache2/certs/apache.crt"
- `apache_ssl_key_path`: "/etc/apache2/certs/apache.key"
- `site_title`: "Test Site"
- `site_heading`: "Hello, world!"
- `site_content`: "The site is up and running"

## Argument Specification

**Variables for meta/argument_specs.yml:**
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache package version
- `apache_document_root`: string, default "/var/www/helloworld", Document root path
- `apache_site_name`: string, default "helloworld", Site configuration name
- `ssl_cert_dir`: string, default "/etc/apache2/certs", SSL certificate directory
- `ssl_common_name`: string, default "{{ ansible_fqdn }}", SSL certificate common name
- `site_title`: string, default "Test Site", HTML page title
- `site_heading`: string, default "Hello, world!", Main heading text
- `site_content`: string, default "The site is up and running", Page content

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

**Templates to validate**: 
- helloworld.conf.j2 (Apache syntax validation)
- index.html.j2 (HTML validation)

## Pre-flight checks:
```bash
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify site accessibility
curl -k https://localhost/

# Check Apache service status
systemctl status apache2

# Verify enabled sites
a2ensite -l

# Check SSL module status
apache2ctl -M | grep ssl
```

**Critical modernization notes:**
1. Convert from playbook to proper role structure
2. The `openssl_certificate` module has been renamed to `x509_certificate` in the community.crypto collection
3. Add proper `changed_when` conditions to command tasks for idempotency
4. Replace inline content with proper Jinja2 templates
5. Add validation tasks to ensure SSL certificates are properly generated
6. Consider using `apache2_module` instead of `command: a2enmod` for better idempotency
7. The handler "Restart sshd" seems unrelated to Apache configuration and should be reviewed