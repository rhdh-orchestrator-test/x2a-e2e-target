---
source-path: chef-and-ansible/website_https.yml
---

Now I understand the structure and purpose of this file. Let me create a detailed migration plan based on this analysis.

# Migration Plan: apache-https-deployment

**TLDR**: This role configures an Apache web server with HTTPS support using a self-signed certificate. It needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, quoted file modes, and improved command module usage with proper change detection.

## Service Type and Configuration

**Service Type**: Web Server (Apache)

**Key Operations**:
- Installs Apache web server and SSL dependencies (curl, openssl, python3-openssl)
- Creates SSL certificates directory and generates self-signed certificates
- Configures a virtual host for HTTPS
- Creates a simple "Hello World" website
- Enables SSL module and the custom virtual host
- Disables the default virtual host
- Manages Apache and SSH services

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

```
website_https.yml
```

**Task Files:**
website_https.yml (contains inline tasks)

**Handler Files:**
website_https.yml (contains inline handlers)

**Variable Files:**
website_https.yml (contains inline vars)

**Templates:**
None (uses inline templates via vars)

**Static Files:**
None (content is generated from variables)

## Module Explanation

The role performs operations in this order:

1. **Main Tasks** (`website_https.yml`):
   - Updates apt cache and installs Apache with a specific version
   - Installs dependencies (curl, openssl, PyOpenSSL)
   - Creates a directory for SSL certificates
   - Generates SSL private key, CSR, and self-signed certificate
   - Configures a virtual host for HTTPS using inline template
   - Creates website directory and deploys "Hello World" content
   - Disables default site and enables the custom site and SSL module
   - Ansible module mapping: short names → fully qualified collection names (FQCN)

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
| `update_cache=true` | `update_cache: true` | website_https.yml | YAML syntax |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal mode |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octal mode |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octal mode |
| `command:` without `changed_when` | Add `changed_when` conditions | website_https.yml | Idempotency |
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| Playbook format | Role format | website_https.yml | Structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core
- community.crypto: >=2.0.0

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

The templates are defined inline as variables in the playbook:

- **conftext**: No modernization needed for the Apache virtual host configuration
- **webtext**: Fix HTML syntax error in the head tag (`</head>` is misspelled as `/head>`)

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, Apache virtual host configuration template
- `webtext`: string, HTML content for the website

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**:
- Apache virtual host configuration (now in templates/virtualhost.conf.j2)
- Website HTML content (now in templates/index.html.j2)

## Pre-flight checks:
```bash
# Verify Apache installation
systemctl status apache2

# Check SSL configuration
apache2ctl -M | grep ssl

# Verify virtual host configuration
apache2ctl -S

# Test SSL certificate
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Test website accessibility
curl -k https://localhost/
```