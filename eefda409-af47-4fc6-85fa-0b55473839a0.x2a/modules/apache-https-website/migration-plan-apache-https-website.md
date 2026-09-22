---
source-path: chef-and-ansible/website_https.yml
---

I can see this is a single playbook file, not a traditional Ansible role structure. Let me analyze the content and provide a migration plan to convert this playbook into a modern Ansible role.

# Migration Plan: apache-https-website

**TLDR**: This is a single playbook that sets up an Apache web server with HTTPS/SSL support, including self-signed certificates and a simple "Hello World" website. The migration involves converting it from a playbook to a proper role structure and modernizing deprecated syntax, module names, and adding proper error handling and idempotency.

## Service Type and Configuration

**Service Type**: Web Server (Apache HTTPS)

**Key Operations**:
- Install Apache2 web server with specific version
- Install SSL/TLS dependencies (curl, openssl, python3-openssl)
- Generate self-signed SSL certificates (private key, CSR, certificate)
- Configure HTTPS virtual host for "Hello World" site
- Deploy static HTML content
- Enable SSL module and configure site activation
- Manage Apache service lifecycle

## File Structure

**Current Structure:**
```
website_https.yml
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
```

## Module Explanation

The playbook performs operations in this order:

1. **Package Management** (`tasks/main.yml`):
   - Updates apt cache using legacy `apt: update_cache=true` syntax
   - Installs Apache2 with pinned version using legacy parameter format
   - Installs SSL dependencies using modern `pkg:` list format
   - Modern equivalent: Use FQCN `ansible.builtin.apt` with proper parameter structure

2. **SSL Certificate Setup** (`tasks/main.yml`):
   - Creates certificate directory with unquoted octal mode `0640`
   - Generates private key, CSR, and self-signed certificate using community.crypto modules
   - Modern equivalent: Quote octal modes, use FQCN for community.crypto modules

3. **Apache Configuration** (`tasks/main.yml`):
   - Deploys virtual host configuration using inline content variable
   - Creates web directory with proper permissions
   - Deploys HTML content using inline variable
   - Modern equivalent: Use templates instead of inline content, add proper file ownership

4. **Site Management** (`tasks/main.yml`):
   - Uses bare `command` modules without `changed_when` for idempotency
   - Activates/deactivates sites and SSL module
   - Modern equivalent: Add `changed_when` conditions or use `apache2_module`/`apache2_site` modules

5. **Service Management** (`handlers/main.yml`):
   - Handlers use mixed FQCN (correct) and notify incorrect service (sshd instead of ssh)
   - Modern equivalent: Fix handler names and ensure proper service management

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt: update_cache=true` | `ansible.builtin.apt: update_cache: true` | tasks/main.yml | FQCN + parameter structure |
| `apt: name: apache2=2.4.41-4ubuntu3.10` | `ansible.builtin.apt: name: apache2=2.4.41-4ubuntu3.10` | tasks/main.yml | FQCN |
| `file: mode: 0640` | `ansible.builtin.file: mode: '0640'` | tasks/main.yml | Quote octal modes |
| `copy: mode: 0644` | `ansible.builtin.copy: mode: '0644'` | tasks/main.yml | Quote octal modes |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | tasks/main.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | tasks/main.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | tasks/main.yml | FQCN |
| `command:` without `changed_when` | Add `changed_when` conditions | tasks/main.yml | Idempotency |
| Inline content variables | Template files | tasks/main.yml | Better maintainability |
| `notify: Restart sshd` | `notify: Restart ssh` | tasks/main.yml | Correct service name |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, ssh

## Template Modernization

- **helloworld.conf.j2**: Convert inline `conftext` variable to proper Jinja2 template with configurable parameters
- **index.html.j2**: Convert inline `webtext` variable to template with customizable title and content

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache version to install
- `site_name`: string, default "helloworld", Name of the site
- `document_root`: string, default "/var/www/helloworld", Document root path
- `ssl_cert_path`: string, default "/etc/apache2/certs", SSL certificate directory
- `common_name`: string, default "myhost", SSL certificate common name
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

**Services to check**: apache2, ssh
**Templates to validate**: helloworld.conf.j2, index.html.j2

## Pre-flight checks:
```bash
# Verify Apache is running and configured
systemctl status apache2
apache2ctl configtest

# Check SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify site accessibility
curl -k https://localhost
curl -I -k https://localhost

# Check enabled sites and modules
a2ensite -l
a2enmod -l | grep ssl
```

**Critical Migration Notes:**
1. The original playbook has a handler notification error (`Restart sshd` should be `Restart ssh`)
2. All `command` tasks need `changed_when` conditions for proper idempotency
3. Octal file modes must be quoted in modern Ansible
4. Consider using `apache2_module` and `apache2_site` modules instead of `command` for better idempotency
5. SSL certificate generation should include proper validation and renewal logic
6. The role should support different operating systems beyond Ubuntu/Debian