---
source-path: chef-and-ansible/website_https.yml
---

I can see that `website_https.yml` is a single playbook file, not an Ansible role structure. However, the user is asking to analyze the module 'apache-https-website' for migration to Ansible. This appears to be a playbook that needs to be converted into a proper Ansible role structure. Let me analyze the content and create a migration plan.

# Migration Plan: apache-https-website

**TLDR**: This is a single playbook file that configures an Apache web server with HTTPS support using self-signed certificates and deploys a simple "Hello World" website. The migration involves converting this playbook into a proper Ansible role structure with modern syntax, FQCN modules, proper file organization, and improved idempotency.

## Service Type and Configuration

**Service Type**: Web Server (Apache HTTPS)

**Key Operations**:
- Install Apache2 web server with specific version
- Install SSL/TLS dependencies (curl, openssl, python3-openssl)
- Generate self-signed SSL certificates (private key, CSR, certificate)
- Configure HTTPS virtual host for a "Hello World" website
- Deploy static HTML content
- Enable SSL module and configure site activation
- Manage Apache service restart through handlers

## File Structure

**Current Structure:**
```
website_https.yml (single playbook file)
```

**Target Role Structure:**
```
tasks/main.yml
handlers/main.yml
templates/helloworld.conf.j2
templates/index.html.j2
defaults/main.yml
vars/main.yml
meta/main.yml
meta/argument_specs.yml
files/
```

## Module Explanation

The playbook performs operations in this order:

1. **Package Management** (`website_https.yml` lines 20-32):
   - Updates apt cache using legacy syntax
   - Installs Apache2 with pinned version
   - Installs SSL dependencies (curl, openssl, python3-openssl)
   - Legacy patterns: `apt: update_cache=true`, missing FQCN

2. **SSL Certificate Generation** (`website_https.yml` lines 34-54):
   - Creates certificate directory with legacy file module syntax
   - Generates private key, CSR, and self-signed certificate
   - Legacy patterns: unquoted mode values, missing FQCN for crypto modules

3. **Apache Configuration** (`website_https.yml` lines 56-78):
   - Deploys virtual host configuration using inline content
   - Creates document root directory
   - Deploys HTML content using inline variables
   - Legacy patterns: `copy:` with inline content, unquoted modes

4. **Site Activation** (`website_https.yml` lines 80-92):
   - Disables default site and enables custom site using command module
   - Enables SSL module
   - Legacy patterns: `command:` without `changed_when`, missing idempotency

5. **Service Management** (`website_https.yml` lines 94-104):
   - Handlers for restarting sshd and apache2
   - Mixed legacy and modern syntax (some handlers already use FQCN)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt: update_cache=true` | `ansible.builtin.apt: update_cache: true` | tasks/main.yml | FQCN + YAML syntax |
| `apt:` | `ansible.builtin.apt:` | tasks/main.yml | FQCN |
| `file:` | `ansible.builtin.file:` | tasks/main.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | tasks/main.yml | FQCN |
| `command:` | `ansible.builtin.command:` | tasks/main.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | tasks/main.yml | Collection migration |
| `openssl_csr:` | `community.crypto.openssl_csr:` | tasks/main.yml | Collection migration |
| `openssl_certificate:` | `community.crypto.x509_certificate:` | tasks/main.yml | Module name change + collection |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted octal values |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted octal values |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted octal values |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Inline content vars | Template files | tasks/main.yml | Better maintainability |
| `command:` without `changed_when` | Add `changed_when` logic | tasks/main.yml | Idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **helloworld.conf.j2**: Convert inline `conftext` variable to proper Jinja2 template with configurable parameters
- **index.html.j2**: Convert inline `webtext` variable to template with customizable title and content

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", Apache package version
- `site_name`: string, default: "helloworld", Virtual host name
- `document_root`: string, default: "/var/www/helloworld", Web root directory
- `ssl_cert_path`: string, default: "/etc/apache2/certs", SSL certificate directory
- `common_name`: string, default: "{{ ansible_fqdn }}", SSL certificate common name
- `site_title`: string, default: "Test Site", HTML page title
- `site_content`: string, default: "Hello, world!", Main page content

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

**Critical Migration Notes:**
1. The `openssl_certificate` module has been replaced with `x509_certificate` in community.crypto collection
2. All command tasks need `changed_when` conditions for proper idempotency
3. The sshd restart handler seems unrelated to Apache configuration and should be reviewed
4. Consider using `ansible.builtin.apache2_module` instead of `command: a2enmod`
5. Consider using `ansible.builtin.apache2_site` instead of `command: a2ensite/a2dissite`
6. Template files will improve maintainability over inline content variables
7. Add proper error handling and validation for SSL certificate generation