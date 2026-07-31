---
source-path: chef-and-ansible
---

Based on the files I've examined, I can now create a migration plan for converting the Apache HTTPS website playbook into a proper Ansible role following modern best practices.

# Migration Plan: apache-https-website

**TLDR**: This role configures an Apache web server with HTTPS support using a self-signed certificate. Key modernization needs include FQCN module names, proper boolean syntax, quoted file modes, and converting the playbook structure into a proper role structure with separate task files.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server and SSL dependencies
- Generates self-signed SSL certificates
- Configures a virtual host for HTTPS
- Creates a simple "Hello World" website
- Enables SSL module and the custom virtual host
- Applies security hardening by restricting SSL protocols (POODLE fix)

## File Structure

**Current Structure (Playbook):**
```
website_https.yml
poodle_fix.yml
```

**Proposed Role Structure:**
```
tasks/main.yml
tasks/install.yml
tasks/ssl_certificates.yml
tasks/configure.yml
tasks/security.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
templates/virtualhost.conf.j2
templates/index.html.j2
meta/argument_specs.yml
```

## Module Explanation

The role performs operations in this order:

1. **Install packages** (`tasks/install.yml`):
   - Updates apt cache
   - Installs Apache web server with specific version
   - Installs dependencies (curl, openssl, PyOpenSSL)
   - Legacy patterns: short module names, unquoted boolean values, non-loop package installation
   - Modern equivalent: FQCN module names, proper boolean syntax, loop for package installation

2. **SSL Certificate Generation** (`tasks/ssl_certificates.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: short module names, unquoted file modes
   - Modern equivalent: FQCN module names, quoted file modes

3. **Web Server Configuration** (`tasks/configure.yml`):
   - Configures virtual host with SSL settings
   - Creates web directory
   - Deploys website content
   - Disables default site and enables custom site
   - Enables SSL module
   - Legacy patterns: short module names, command module without changed_when, inline templates
   - Modern equivalent: FQCN module names, changed_when conditions, separate template files

4. **Security Hardening** (`tasks/security.yml`):
   - Fixes POODLE vulnerability by restricting SSL protocols
   - Legacy patterns: short module names
   - Modern equivalent: FQCN module names

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
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted file mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted file mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted file mode |
| `command: a2dissite` without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |
| `command: a2ensite` without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |
| `command: a2enmod` without `changed_when` | Add `changed_when` condition | website_https.yml | Idempotency |
| Inline templates in vars | Separate template files | website_https.yml | Structure |
| Playbook structure | Role structure | website_https.yml, poodle_fix.yml | Structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **virtualhost.conf.j2**: Convert inline `conftext` variable to template file with proper indentation and variable references
- **index.html.j2**: Convert inline `webtext` variable to template file, fix HTML syntax error in head tag

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache version to install
- `website_domain`: string, default "myhost", Domain name for the website
- `website_root`: string, default "/var/www/helloworld", Website document root
- `ssl_cert_dir`: string, default "/etc/apache2/certs", Directory for SSL certificates
- `ssl_protocols`: string, default "-all +TLSv1.2", SSL protocols to enable/disable

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- tasks/install.yml
- tasks/ssl_certificates.yml
- tasks/configure.yml
- tasks/security.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- templates/virtualhost.conf.j2
- templates/index.html.j2
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

# Verify SSL module is enabled
apache2ctl -M | grep ssl

# Verify virtual host configuration
apache2ctl -t

# Verify SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Test HTTPS connection
curl -k https://localhost

# Verify SSL protocols (POODLE fix)
nmap --script ssl-enum-ciphers -p 443 localhost
```