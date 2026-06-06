---
source-path: chef-and-ansible/website_https.yml
---

Now I'll analyze the content and prepare a migration plan for converting this playbook into a proper Ansible role.

# Migration Plan: apache-https-website

**TLDR**: This playbook sets up an Apache web server with HTTPS enabled using a self-signed certificate. It needs to be converted from a standalone playbook to a proper Ansible role with fully qualified collection names (FQCN), modern boolean syntax, quoted file modes, and proper command module usage with changed_when conditions.

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

**IMPORTANT: The source is a standalone playbook, not a role. The migration will create the following role structure:**

```
roles/apache-https-website/tasks/main.yml
roles/apache-https-website/handlers/main.yml
roles/apache-https-website/templates/helloworld.conf.j2
roles/apache-https-website/templates/index.html.j2
roles/apache-https-website/defaults/main.yml
roles/apache-https-website/meta/main.yml
```

**Task Files:**
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml

**Meta:**
meta/main.yml

**Templates:**
templates/helloworld.conf.j2
templates/index.html.j2

## Module Explanation

The role performs operations in this order:

1. **Package Installation** (`tasks/main.yml`):
   - Updates apt cache
   - Installs Apache web server with specific version
   - Installs dependencies (curl, openssl, python3-openssl)
   - Legacy patterns: short module names, unquoted boolean values
   - Modern equivalent: FQCN module names, quoted boolean values

2. **SSL Certificate Generation** (`tasks/main.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: short module names, unquoted file modes
   - Modern equivalent: FQCN module names, quoted file modes

3. **Website Configuration** (`tasks/main.yml`):
   - Creates virtual host configuration file
   - Creates website directory
   - Deploys website content
   - Legacy patterns: inline templates as variables, short module names
   - Modern equivalent: separate template files, FQCN module names

4. **Apache Configuration** (`tasks/main.yml`):
   - Disables default virtual host
   - Enables custom virtual host
   - Enables SSL module
   - Legacy patterns: command module without changed_when, short module names
   - Modern equivalent: command with changed_when or apache2_module/apache2_site modules

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
| `update_cache=true` | `update_cache: true` | tasks/main.yml | YAML syntax |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted file modes |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted file modes |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted file modes |
| `command: a2dissite` | `community.general.apache2_site: name=000-default state=absent` | tasks/main.yml | Module replacement |
| `command: a2ensite` | `community.general.apache2_site: name=helloworld state=present` | tasks/main.yml | Module replacement |
| `command: a2enmod` | `community.general.apache2_module: name=ssl state=present` | tasks/main.yml | Module replacement |
| Inline templates | Separate template files | tasks/main.yml | Template modernization |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.general: ">=3.0.0"
- community.crypto: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **helloworld.conf.j2**: Convert from inline variable `conftext` to template file with proper Jinja2 syntax
- **index.html.j2**: Convert from inline variable `webtext` to template file with proper Jinja2 syntax

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `website_domain`: string, default: "myhost", description: "Domain name for the website"
- `website_root`: string, default: "/var/www/helloworld", description: "Path to website root directory"
- `ssl_cert_dir`: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- `ssl_key_path`: string, default: "/etc/apache2/certs/apache.key", description: "Path to SSL private key"
- `ssl_csr_path`: string, default: "/etc/apache2/certs/apache.csr", description: "Path to SSL CSR"
- `ssl_cert_path`: string, default: "/etc/apache2/certs/apache.crt", description: "Path to SSL certificate"

## Checks for the Migration

**Files to verify**:
- roles/apache-https-website/tasks/main.yml
- roles/apache-https-website/handlers/main.yml
- roles/apache-https-website/templates/helloworld.conf.j2
- roles/apache-https-website/templates/index.html.j2
- roles/apache-https-website/defaults/main.yml
- roles/apache-https-website/meta/main.yml

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
- Test HTTPS connection: `curl -k https://localhost`