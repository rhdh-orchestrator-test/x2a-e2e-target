---
source-path: chef-and-ansible/website_https.yml
---

I can see this is a playbook file rather than a traditional Ansible role structure. Let me analyze this Apache HTTPS setup playbook for modernization. Based on my analysis, I can now provide the migration specification.

# Migration Plan: apache-https-setup

**TLDR**: This playbook configures Apache with HTTPS support by installing Apache2, generating self-signed SSL certificates, creating a virtual host configuration, and deploying a simple "Hello World" website. Key modernization needs include FQCN adoption, proper file permissions quoting, command task idempotency, and restructuring from playbook to proper role format.

## Service Type and Configuration

**Service Type**: Web Server

**Key Operations**:
- Install Apache2 web server with specific version pinning
- Install SSL/TLS dependencies (curl, openssl, python3-openssl)
- Generate self-signed SSL certificates (private key, CSR, certificate)
- Configure HTTPS virtual host for a test website
- Deploy static HTML content
- Enable SSL module and configure site activation
- Manage Apache2 service lifecycle

## File Structure

**Current Structure (Playbook):**
```
website_https.yml
```

**Target Structure (Role):**
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
   - Installs Apache2 with version pinning
   - Installs SSL dependencies
   - Ansible module mapping: `apt:` → `ansible.builtin.apt:`

2. **SSL Certificate Generation** (`website_https.yml`):
   - Creates certificate directory with unquoted mode
   - Generates private key, CSR, and self-signed certificate
   - Ansible module mapping: `openssl_*` → `community.crypto.openssl_*`

3. **Web Configuration** (`website_https.yml`):
   - Deploys virtual host configuration using inline content
   - Creates web directory and deploys HTML content
   - Ansible module mapping: `copy:`, `file:` → `ansible.builtin.copy:`, `ansible.builtin.file:`

4. **Service Configuration** (`website_https.yml`):
   - Disables default site and enables custom site using command tasks
   - Enables SSL module
   - Ansible module mapping: `command:` → `ansible.builtin.command:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | Collection migration |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | Collection migration |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | website_https.yml | Collection migration |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Octal quoting |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Octal quoting |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| `become: yes` | `become: true` | website_https.yml | Boolean syntax |
| Command tasks without `changed_when` | Add `changed_when` conditions | website_https.yml | Idempotency |
| Inline content variables | Template files | website_https.yml | Template modernization |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

**New templates to create:**
- **helloworld.conf.j2**: Extract `conftext` variable into proper Jinja2 template with configurable parameters
- **index.html.j2**: Extract `webtext` variable into proper HTML template with configurable content

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache package version
- `site_name`: string, default "helloworld", Virtual host name
- `document_root`: string, default "/var/www/helloworld", Web root directory
- `ssl_cert_path`: string, default "/etc/apache2/certs/apache.crt", SSL certificate path
- `ssl_key_path`: string, default "/etc/apache2/certs/apache.key", SSL private key path
- `ssl_common_name`: string, default "myhost", SSL certificate common name
- `site_title`: string, default "Test Site", HTML page title
- `site_content`: string, default "Hello, world!", Main page content

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml
- handlers/main.yml
- templates/helloworld.conf.j2
- templates/index.html.j2
- defaults/main.yml
- meta/argument_specs.yml

**Services to check**: 
- apache2 (running and enabled)
- SSL certificate validity

**Templates to validate**: 
- Virtual host configuration syntax
- HTML template rendering

## Pre-flight checks:
```bash
# Verify Apache is running with SSL
systemctl status apache2
apache2ctl -t
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
curl -k https://localhost
a2enmod ssl
a2ensite helloworld
```

**Critical modernization notes:**
1. **Structure**: Convert from playbook to proper role structure
2. **Idempotency**: Add `changed_when: false` to command tasks or replace with appropriate modules
3. **Security**: Consider using proper CA-signed certificates in production
4. **Handlers**: The current handler for "Restart sshd" seems incorrect for SSL module activation - should only restart apache2
5. **Version pinning**: Make Apache version configurable rather than hardcoded
6. **Template extraction**: Move inline content to proper template files for maintainability