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
- Configure HTTPS virtual host for "Hello World" website
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

1. **Package Management** (`website_https.yml` lines 21-33):
   - Updates apt cache using legacy syntax
   - Installs Apache2 with pinned version
   - Installs SSL dependencies (curl, openssl, python3-openssl)
   - Legacy patterns: `apt: update_cache=true`, missing FQCN

2. **SSL Certificate Generation** (`website_https.yml` lines 35-56):
   - Creates certificate directory with legacy file module syntax
   - Generates private key, CSR, and self-signed certificate
   - Legacy patterns: unquoted file modes, missing FQCN for crypto modules

3. **Apache Configuration** (`website_https.yml` lines 58-85):
   - Deploys virtual host configuration using inline content
   - Creates document root directory
   - Deploys HTML content using inline variables
   - Legacy patterns: `copy:` with inline content, unquoted modes

4. **Service Management** (`website_https.yml` lines 87-96):
   - Disables default site and enables custom site using command module
   - Enables SSL module
   - Legacy patterns: `command:` without `changed_when`, missing idempotency

5. **Handlers** (`website_https.yml` lines 98-108):
   - Restarts SSH and Apache services
   - Mixed legacy/modern syntax (some handlers use FQCN, some don't)

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
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted octal modes |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted octal modes |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted octal modes |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Inline `content:` | Template files | tasks/main.yml | Extract to templates |
| `command:` without `changed_when` | Add `changed_when` logic | tasks/main.yml | Idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **helloworld.conf.j2**: Extract Apache virtual host configuration from inline variable `conftext`
  - Make DocumentRoot configurable
  - Make SSL certificate paths configurable
  - Add proper Jinja2 variable syntax

- **index.html.j2**: Extract HTML content from inline variable `webtext`
  - Make title and content configurable
  - Fix malformed HTML (`/head>` should be `</head>`)

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache package version
- `site_name`: string, default "helloworld", Site name for configuration
- `document_root`: string, default "/var/www/helloworld", Web document root
- `ssl_cert_path`: string, default "/etc/apache2/certs/apache.crt", SSL certificate path
- `ssl_key_path`: string, default "/etc/apache2/certs/apache.key", SSL private key path
- `ssl_csr_path`: string, default "/etc/apache2/certs/apache.csr", SSL CSR path
- `cert_common_name`: string, default "{{ ansible_facts['fqdn'] }}", Certificate common name
- `site_title`: string, default "Test Site", HTML page title
- `site_content`: string, default "Hello, world!", Main page content

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- templates/helloworld.conf.j2
- templates/index.html.j2
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml
- collections/requirements.yml

**Services to check**:
- apache2 (running and enabled)
- SSL certificate validity

**Templates to validate**:
- Apache virtual host configuration syntax
- HTML content validity

## Pre-flight checks:
```bash
# Verify Apache is running with SSL
systemctl status apache2
apache2ctl -S
openssl s_client -connect localhost:443 -servername {{ cert_common_name }}

# Check site accessibility
curl -k https://localhost/
curl -k https://{{ cert_common_name }}/

# Verify SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Check Apache modules
apache2ctl -M | grep ssl
a2ensite -l
```

**Critical Migration Notes**:
1. The `openssl_certificate` module has been replaced with `x509_certificate` in community.crypto collection
2. Command tasks need `changed_when` conditions for proper idempotency
3. HTML template has malformed tag (`/head>` should be `</head>`)
4. SSL certificate generation should use `ansible_facts['fqdn']` instead of hardcoded hostname
5. Apache version pinning should be made configurable
6. File modes must be quoted to prevent octal interpretation issues