---
source-path: chef-and-ansible/website_https.yml
---

I can see that `website_https.yml` is a single playbook file, not an Ansible role structure. However, the user is asking me to analyze the module 'ansible-apache-ssl' for migration to Ansible. Let me examine the content more carefully to understand what needs to be modernized and converted into a proper Ansible role structure.

Based on my analysis, this is a single playbook file that needs to be converted into a modern Ansible role. Let me provide the migration specification:

# Migration Plan: ansible-apache-ssl

**TLDR**: This legacy playbook configures Apache with SSL/HTTPS support, creating self-signed certificates and deploying a simple "Hello World" website. It needs complete restructuring from a monolithic playbook into a modern Ansible role with proper FQCN usage, file organization, argument specifications, and modernized syntax patterns.

## Service Type and Configuration

**Service Type**: Web Server (Apache HTTP Server with SSL/TLS)

**Key Operations**:
- Install Apache2 web server with specific version pinning
- Install SSL/TLS dependencies (curl, openssl, python3-openssl)
- Generate self-signed SSL certificates (private key, CSR, certificate)
- Configure SSL-enabled virtual host for HTTPS
- Deploy static HTML content
- Manage Apache site activation/deactivation
- Enable SSL module in Apache
- Service management through handlers

## File Structure

**IMPORTANT: This is currently a single playbook file that needs to be restructured into a proper role.**

**Current Structure:**
```
website_https.yml (monolithic playbook - needs conversion)
```

**Target Role Structure:**
```
tasks/main.yml
handlers/main.yml
templates/virtualhost.conf.j2
templates/index.html.j2
defaults/main.yml
vars/main.yml
meta/main.yml
meta/argument_specs.yml
files/.gitkeep
```

## Module Explanation

The current playbook performs operations in this order:

1. **Package Management** (tasks section):
   - Updates apt cache using legacy `apt: update_cache=true` syntax
   - Installs Apache2 with version pinning using legacy parameter format
   - Installs SSL dependencies using modern list format
   - Legacy patterns: Short module names, unquoted parameters

2. **SSL Certificate Generation** (tasks section):
   - Creates certificate directory with unquoted octal mode
   - Generates private key using `openssl_privatekey` (needs FQCN)
   - Generates CSR using `openssl_csr` (needs FQCN)  
   - Generates self-signed certificate using `openssl_certificate` (needs FQCN)
   - Legacy patterns: Missing FQCN, unquoted file modes

3. **Web Content Deployment** (tasks section):
   - Configures virtual host using inline content variable
   - Creates web directory with proper permissions
   - Deploys HTML content using inline variable
   - Legacy patterns: Inline content should use templates

4. **Apache Configuration** (tasks section):
   - Deactivates default site using `command` module without `changed_when`
   - Activates custom site using `command` module without `changed_when`
   - Enables SSL module using `command` module without `changed_when`
   - Legacy patterns: Missing idempotency controls, should use `apache2_module`

5. **Service Management** (handlers section):
   - Restarts SSH service (mixed with modern FQCN)
   - Restarts Apache service (mixed with modern FQCN)
   - Legacy patterns: SSH restart seems unrelated to Apache SSL configuration

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
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | tasks/main.yml | Collection migration |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted octal modes |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted octal modes |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted octal modes |
| `command` without `changed_when` | Add `changed_when` conditions | tasks/main.yml | Idempotency |
| Inline `content:` variables | Template files | tasks/main.yml | Better maintainability |
| `a2ensite`/`a2dissite` commands | `community.general.apache2_module` | tasks/main.yml | Proper Apache management |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- community.general: ">=6.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd (questionable - should be removed)

## Template Modernization

**Target templates to create:**
- **virtualhost.conf.j2**: Convert inline `conftext` variable to proper Jinja2 template with configurable parameters
- **index.html.j2**: Convert inline `webtext` variable to template with customizable content

**Variables to template:**
- Document root path
- SSL certificate paths  
- Virtual host configuration
- Website content and title

## Argument Specification

**Variables for meta/argument_specs.yml:**
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", Apache version to install
- `site_name`: string, default: "helloworld", Name of the site/virtual host
- `document_root`: string, default: "/var/www/helloworld", Web document root
- `ssl_cert_path`: string, default: "/etc/apache2/certs/apache.crt", SSL certificate path
- `ssl_key_path`: string, default: "/etc/apache2/certs/apache.key", SSL private key path
- `ssl_csr_path`: string, default: "/etc/apache2/certs/apache.csr", SSL CSR path
- `common_name`: string, default: "{{ ansible_facts['fqdn'] }}", SSL certificate common name
- `website_title`: string, default: "Test Site", HTML page title
- `website_content`: string, default: "Hello, world!", Main website content
- `cert_directory_mode`: string, default: "'0750'", Certificate directory permissions
- `web_directory_mode`: string, default: "'0755'", Web directory permissions
- `cert_file_mode`: string, default: "'0640'", Certificate file permissions
- `html_file_mode`: string, default: "'0644'", HTML file permissions

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml
- handlers/main.yml  
- templates/virtualhost.conf.j2
- templates/index.html.j2
- defaults/main.yml
- vars/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**: 
- apache2 (running and enabled)
- SSL module loaded in Apache

**Templates to validate**: 
- virtualhost.conf.j2 (proper Jinja2 syntax, configurable paths)
- index.html.j2 (valid HTML structure)

## Pre-flight checks:
```bash
# Verify Apache is installed and running
systemctl status apache2

# Check SSL module is enabled  
apache2ctl -M | grep ssl

# Verify SSL certificates exist and are valid
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Test HTTPS connectivity
curl -k https://localhost/

# Verify virtual host configuration
apache2ctl -S

# Check site is enabled
a2ensite -q helloworld && echo "Site enabled" || echo "Site not enabled"
```

**Critical Migration Notes:**
1. Remove the SSH service restart handler - it's unrelated to Apache SSL configuration
2. Replace `command` module usage for Apache management with proper `community.general.apache2_module` 
3. Add proper `changed_when` conditions for any remaining command tasks
4. Convert inline content variables to proper Jinja2 templates
5. Add comprehensive error handling for SSL certificate generation
6. Consider adding certificate validation and renewal logic
7. The role should be idempotent and support check mode