---
source-path: chef-and-ansible/website_https.yml
---

Now I'll analyze the content and create a migration plan for converting this playbook into a proper Ansible role:

# Migration Plan: apache-https-website

**TLDR**: This playbook sets up an Apache web server with HTTPS enabled using a self-signed certificate. It needs to be converted from a standalone playbook into a proper Ansible role with fully qualified collection names (FQCN), modern boolean syntax, quoted file modes, and proper command module usage with changed_when conditions.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server and SSL dependencies
- Generates self-signed SSL certificates
- Configures a virtual host for HTTPS
- Deploys a simple "Hello World" website
- Enables SSL module and the custom virtual host
- Disables the default virtual host

## File Structure

**Current Structure (Playbook):**
```
chef-and-ansible/website_https.yml
```

**Proposed Role Structure:**
```
roles/apache-https-website/tasks/main.yml
roles/apache-https-website/handlers/main.yml
roles/apache-https-website/defaults/main.yml
roles/apache-https-website/meta/main.yml
roles/apache-https-website/templates/helloworld.conf.j2
roles/apache-https-website/templates/index.html.j2
roles/apache-https-website/meta/argument_specs.yml
```

## Module Explanation

The role performs operations in this order:

1. **Package Installation** (`tasks/main.yml`):
   - Updates apt cache
   - Installs Apache with a specific version
   - Installs dependencies (curl, openssl, PyOpenSSL)
   - Legacy patterns: short module names, unquoted boolean values
   - Modern equivalent: FQCN module names, quoted boolean values

2. **SSL Certificate Generation** (`tasks/main.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: short module names, unquoted file modes
   - Modern equivalent: FQCN module names, quoted file modes

3. **Website Configuration** (`tasks/main.yml`):
   - Configures Apache virtual host for HTTPS
   - Creates website directory
   - Deploys website content
   - Legacy patterns: inline templates as variables, short module names
   - Modern equivalent: External template files, FQCN module names

4. **Apache Configuration** (`tasks/main.yml`):
   - Disables default site
   - Enables custom site
   - Enables SSL module
   - Legacy patterns: command module without changed_when, short module names
   - Modern equivalent: FQCN command module with changed_when conditions

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | tasks/main.yml | FQCN |
| `file:` | `ansible.builtin.file:` | tasks/main.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | tasks/main.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | tasks/main.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | tasks/main.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | tasks/main.yml | FQCN |
| `command:` | `ansible.builtin.command:` | tasks/main.yml | FQCN |
| `update_cache=true` | `update_cache: true` | tasks/main.yml | Modern boolean syntax |
| `force: yes` | `force: true` | tasks/main.yml | Modern boolean syntax |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted file modes |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted file modes |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted file modes |
| `command: a2dissite` without `changed_when` | Add `changed_when` condition | tasks/main.yml | Idempotency |
| `command: a2ensite` without `changed_when` | Add `changed_when` condition | tasks/main.yml | Idempotency |
| `command: a2enmod` without `changed_when` | Add `changed_when` condition | tasks/main.yml | Idempotency |
| Inline templates in vars | External template files | tasks/main.yml | Structural improvement |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **helloworld.conf.j2**: Convert from inline variable to template file with proper Jinja2 syntax
- **index.html.j2**: Convert from inline variable to template file with proper HTML structure (fix missing opening tag for head)

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `website_domain`: string, default: "myhost", description: "Domain name for the website and SSL certificate"
- `ssl_cert_dir`: string, default: "/etc/apache2/certs", description: "Directory to store SSL certificates"
- `website_root`: string, default: "/var/www/helloworld", description: "Document root for the website"
- `website_title`: string, default: "Test Site", description: "Title for the website"
- `website_heading`: string, default: "Hello, world!", description: "Main heading for the website"
- `website_content`: string, default: "The site is up and running", description: "Content for the website"

## Checks for the Migration

**Files to verify**:
- roles/apache-https-website/tasks/main.yml
- roles/apache-https-website/handlers/main.yml
- roles/apache-https-website/defaults/main.yml
- roles/apache-https-website/meta/main.yml
- roles/apache-https-website/templates/helloworld.conf.j2
- roles/apache-https-website/templates/index.html.j2
- roles/apache-https-website/meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- helloworld.conf.j2
- index.html.j2

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSL module is enabled: `apache2ctl -M | grep ssl`
- Verify virtual host is enabled: `apache2ctl -S | grep helloworld`
- Verify SSL certificate exists: `ls -la /etc/apache2/certs/apache.crt`
- Verify website is accessible: `curl -k https://localhost`
- Verify SSL is working: `openssl s_client -connect localhost:443`