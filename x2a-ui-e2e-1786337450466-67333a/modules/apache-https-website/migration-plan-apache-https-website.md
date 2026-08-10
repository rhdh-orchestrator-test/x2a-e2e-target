---
source-path: chef-and-ansible/website_https.yml
---

Now I'll create a detailed migration plan based on the analysis:

# Migration Plan: apache-https-website

**TLDR**: This role configures an Apache web server with HTTPS support using a self-signed certificate. It needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, quoted file modes, and improved command module usage with proper change detection.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server and SSL dependencies
- Generates self-signed SSL certificates
- Configures a virtual host for HTTPS
- Creates a simple "Hello World" website
- Enables SSL module and the custom virtual host
- Disables the default virtual host

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
templates/helloworld.conf.j2
templates/index.html.j2
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
   - Legacy patterns: short module names (`apt`), unquoted boolean (`update_cache=true`)
   - Modern equivalent: FQCN (`ansible.builtin.apt`), proper boolean syntax (`update_cache: true`)

2. **SSL Certificate Setup** (`tasks/main.yml`):
   - Creates directory for certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Legacy patterns: short module names (`file`, `openssl_privatekey`, `openssl_csr`, `openssl_certificate`), unquoted file mode
   - Modern equivalent: FQCN (`ansible.builtin.file`, `community.crypto.openssl_privatekey`, `community.crypto.openssl_csr`, `community.crypto.openssl_certificate`), quoted file mode (`'0640'`)

3. **Apache Configuration** (`tasks/main.yml`):
   - Creates virtual host configuration using inline template
   - Creates website directory
   - Deploys website content using inline template
   - Legacy patterns: short module names (`copy`, `file`), unquoted file modes, inline templates
   - Modern equivalent: FQCN (`ansible.builtin.copy`, `ansible.builtin.file`), quoted file modes, separate template files

4. **Apache Module Management** (`tasks/main.yml`):
   - Disables default virtual host
   - Enables custom virtual host
   - Enables SSL module
   - Legacy patterns: using `command` module without change detection, missing handlers
   - Modern equivalent: `ansible.builtin.command` with `changed_when`, or better alternatives like `community.general.apache2_module` and `community.general.apache2_site`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | tasks/main.yml | FQCN |
| `file:` | `ansible.builtin.file:` | tasks/main.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | tasks/main.yml | FQCN |
| `command:` | `ansible.builtin.command:` | tasks/main.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | tasks/main.yml | FQCN |
| `openssl_csr:` | `community.crypto.openssl_csr:` | tasks/main.yml | FQCN |
| `openssl_certificate:` | `community.crypto.openssl_certificate:` | tasks/main.yml | FQCN |
| `update_cache=true` | `update_cache: true` | tasks/main.yml | Boolean syntax |
| `mode: 0640` | `mode: '0640'` | tasks/main.yml | Quoted file mode |
| `mode: 0755` | `mode: '0755'` | tasks/main.yml | Quoted file mode |
| `mode: 0644` | `mode: '0644'` | tasks/main.yml | Quoted file mode |
| `command: a2dissite` | `community.general.apache2_site: name=000-default state=absent` | tasks/main.yml | Module replacement |
| `command: a2ensite` | `community.general.apache2_site: name=helloworld state=present` | tasks/main.yml | Module replacement |
| `command: a2enmod` | `community.general.apache2_module: name=ssl state=present` | tasks/main.yml | Module replacement |
| Inline templates | External template files | tasks/main.yml | Move to template files |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.general: ">=3.0.0"
- community.crypto: ">=2.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

- **helloworld.conf.j2**: Create from inline `conftext` variable, ensure proper indentation and Jinja2 syntax
- **index.html.j2**: Create from inline `webtext` variable, fix HTML syntax error (`</head>` tag is incorrect)

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Version of Apache to install"
- `website_root`: string, default: "/var/www/helloworld", description: "Directory path for website files"
- `ssl_cert_dir`: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- `site_title`: string, default: "Test Site", description: "Website title"
- `site_heading`: string, default: "Hello, world!", description: "Main heading for the website"
- `site_message`: string, default: "The site is up and running", description: "Message displayed on the website"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- templates/helloworld.conf.j2
- templates/index.html.j2

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- templates/helloworld.conf.j2
- templates/index.html.j2

## Pre-flight checks:
```
# Verify Apache installation
systemctl status apache2

# Verify SSL module is enabled
apache2ctl -M | grep ssl

# Verify virtual host configuration
apache2ctl -S

# Verify SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Test HTTPS connection
curl -k https://localhost/

# Verify port 443 is listening
ss -tlnp | grep :443
```