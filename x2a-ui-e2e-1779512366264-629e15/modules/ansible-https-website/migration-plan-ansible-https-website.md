---
source-path: chef-and-ansible/website_https.yml
---

Now I'll create a detailed migration plan based on the file I've analyzed:

# Migration Plan: ansible-https-website

**TLDR**: This role sets up an Apache web server with HTTPS enabled using a self-signed certificate. It needs modernization to use FQCN module names, proper boolean syntax, quoted file modes, and improved command module usage with proper change detection.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server and SSL dependencies
- Generates self-signed SSL certificates
- Configures Apache virtual host for HTTPS
- Deploys a simple "Hello World" website
- Enables SSL module and the custom virtual host
- Disables the default virtual host

## File Structure

**Task Files:**
- chef-and-ansible/website_https.yml (playbook with embedded tasks)

**Handler Files:**
- Handlers are embedded in the website_https.yml playbook

**Variable Files:**
- Variables are embedded in the website_https.yml playbook

**Templates:**
- No separate template files (templates are embedded as variables in the playbook)

**Static Files:**
- No separate static files (content is embedded as variables in the playbook)

## Module Explanation

The role performs operations in this order:

1. **Package Installation** (`chef-and-ansible/website_https.yml`):
   - Updates apt cache
   - Installs Apache with a specific version
   - Installs curl, openssl, and PyOpenSSL packages
   - Legacy patterns: non-FQCN module names, non-standard boolean format
   - Modern equivalent: Use FQCN module names, standard boolean format

2. **SSL Certificate Generation** (`chef-and-ansible/website_https.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: non-FQCN module names, unquoted file modes
   - Modern equivalent: Use FQCN module names, quoted file modes

3. **Apache Configuration** (`chef-and-ansible/website_https.yml`):
   - Configures virtual host for HTTPS
   - Creates website directory
   - Deploys website content
   - Legacy patterns: non-FQCN module names, unquoted file modes
   - Modern equivalent: Use FQCN module names, quoted file modes

4. **Apache Module Management** (`chef-and-ansible/website_https.yml`):
   - Disables default virtual host
   - Enables custom virtual host
   - Enables SSL module
   - Legacy patterns: command module without changed_when, non-FQCN module names
   - Modern equivalent: Use FQCN module names, add changed_when or use specialized modules

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
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean syntax |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted file mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted file mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted file mode |
| `command: a2dissite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Add change detection |
| `command: a2ensite` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Add change detection |
| `command: a2enmod` | `ansible.builtin.command:` with `changed_when` | website_https.yml | Add change detection |
| Embedded templates | Separate template files | website_https.yml | Move to templates directory |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=1.0.0"

**Role dependencies**: None specified
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

The playbook uses embedded templates as variables. These should be moved to separate template files:

- **apache_vhost.conf.j2**: Move the `conftext` variable content to this file
- **index.html.j2**: Move the `webtext` variable content to this file

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, template for Apache virtual host configuration
- `webtext`: string, HTML content for the website

## Checks for the Migration

**Files to verify**:
- roles/ansible-https-website/tasks/main.yml
- roles/ansible-https-website/handlers/main.yml
- roles/ansible-https-website/defaults/main.yml
- roles/ansible-https-website/meta/main.yml
- roles/ansible-https-website/templates/apache_vhost.conf.j2
- roles/ansible-https-website/templates/index.html.j2

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- apache_vhost.conf.j2
- index.html.j2

## Pre-flight checks:
- `apache2ctl configtest` - Validate Apache configuration
- `openssl x509 -in /etc/apache2/certs/apache.crt -text -noout` - Validate SSL certificate
- `curl -k https://localhost` - Test HTTPS connection
- `systemctl status apache2` - Verify Apache service is running
- `systemctl status sshd` - Verify SSH service is running