---
source-path: chef-and-ansible/website_https.yml
---

Now I'll analyze the content and provide a migration plan:

# Migration Plan: website_https

**TLDR**: This is a playbook (not a role) that sets up an Apache web server with HTTPS using a self-signed certificate. Key modernization needs include converting from playbook to role structure, using FQCN for modules, proper quoting for modes, and replacing command modules with appropriate modules for idempotency.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server and SSL dependencies (curl, openssl, python3-openssl)
- Creates SSL certificates directory and generates self-signed certificates
- Configures a virtual host for HTTPS
- Creates a simple "Hello World" website
- Enables SSL module and the custom virtual host
- Disables the default virtual host

## File Structure

**IMPORTANT: This is currently a playbook, not a role. The migration will convert it to a role structure.**

Current structure:
```
website_https.yml
```

Proposed role structure:
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
templates/helloworld_vhost.conf.j2
templates/index.html.j2
meta/main.yml
```

## Module Explanation

The playbook performs operations in this order:

1. **Package Installation** (`tasks/main.yml`):
   - Updates apt cache
   - Installs Apache with specific version
   - Installs dependencies (curl, openssl, PyOpenSSL)
   - Legacy patterns: short module names, unquoted boolean values
   - Modern equivalent: FQCN module names, quoted boolean values

2. **SSL Certificate Setup** (`tasks/main.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: short module names, unquoted file modes
   - Modern equivalent: FQCN module names, quoted file modes

3. **Website Configuration** (`tasks/main.yml`):
   - Configures virtual host using inline content
   - Creates website directory
   - Deploys website content
   - Legacy patterns: short module names, unquoted file modes, inline templates
   - Modern equivalent: FQCN module names, quoted file modes, separate template files

4. **Apache Configuration** (`tasks/main.yml`):
   - Disables default site using command module
   - Enables custom site using command module
   - Enables SSL module using command module
   - Legacy patterns: non-idempotent command modules, missing changed_when
   - Modern equivalent: apache2_module and apache2_site modules for idempotency

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
| `command: a2dissite` | `community.apache.apache2_site:` | website_https.yml | Module replacement for idempotency |
| `command: a2ensite` | `community.apache.apache2_site:` | website_https.yml | Module replacement for idempotency |
| `command: a2enmod` | `community.apache.apache2_module:` | website_https.yml | Module replacement for idempotency |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal modes |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal modes |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal modes |
| `update_cache=true` | `update_cache: true` | website_https.yml | YAML syntax |
| Inline templates | Separate template files | website_https.yml | Move to templates directory |
| Playbook structure | Role structure | website_https.yml | Convert to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- community.apache: ">=1.0.0"

**Role dependencies**: None (to be defined in meta/main.yml)
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **helloworld_vhost.conf.j2**: Create from inline `conftext` variable, use proper Jinja2 variable syntax
- **index.html.j2**: Create from inline `webtext` variable, fix HTML syntax error (`</head>` tag is incorrect)

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- apache_version: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- server_name: string, default: "myhost", description: "Server name for SSL certificate"
- website_root: string, default: "/var/www/helloworld", description: "Document root for the website"
- ssl_cert_dir: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- ssl_key_path: string, default: "/etc/apache2/certs/apache.key", description: "Path to SSL private key"
- ssl_csr_path: string, default: "/etc/apache2/certs/apache.csr", description: "Path to SSL CSR"
- ssl_cert_path: string, default: "/etc/apache2/certs/apache.crt", description: "Path to SSL certificate"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- templates/helloworld_vhost.conf.j2
- templates/index.html.j2
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/helloworld_vhost.conf.j2
- templates/index.html.j2

## Pre-flight checks:
- Verify Apache configuration: `apache2ctl configtest`
- Check SSL certificate: `openssl x509 -in /etc/apache2/certs/apache.crt -text -noout`
- Verify SSL module is enabled: `apache2ctl -M | grep ssl`
- Test HTTPS connection: `curl -k https://localhost/`
- Check virtual host is enabled: `ls -la /etc/apache2/sites-enabled/`