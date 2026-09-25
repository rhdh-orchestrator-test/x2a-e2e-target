---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is a demonstration project showing Ansible playbooks for Apache HTTPS configuration and SSL security hardening (POODLE vulnerability fix), designed to work with Chef InSpec for compliance testing. Key modernization needs include FQCN adoption, loop modernization, proper file permissions, idempotency improvements, and converting playbooks to a proper role structure.

## Service Type and Configuration

**Service Type**: Web Server / Security Hardening

**Key Operations**:
- Install and configure Apache2 web server with HTTPS support
- Generate self-signed SSL certificates using OpenSSL
- Deploy a simple "Hello World" website
- Configure SSL virtual host with TLS 1.2 enforcement
- Fix POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
- Enable Apache SSL module and configure virtual hosts
- Manage Apache and SSH service restarts

## File Structure

**Playbook Files:**
```
website_https.yml
poodle_fix.yml
```

**Test Files:**
```
tests/website_https_verify.rb
tests/ssh_profile.rb
```

**Configuration Files:**
```
kitchen.yml
README.md
index.html
```

## Module Explanation

The project contains two main playbooks that perform operations in this order:

1. **website_https.yml** (`website_https.yml`):
   - **Package Management**: Updates apt cache and installs Apache2 with specific version, plus curl, openssl, and python3-openssl
   - **SSL Certificate Generation**: Creates certificate directory, generates private key, CSR, and self-signed certificate
   - **Website Deployment**: Configures virtual host, creates web directory, deploys HTML content
   - **Apache Configuration**: Disables default site, enables custom site, enables SSL module
   - Legacy patterns: Short module names, unquoted file modes, command tasks without changed_when
   - Modern equivalent: FQCN modules, quoted modes, idempotency controls

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - **SSL Security Hardening**: Fixes POODLE vulnerability by replacing SSL protocol configuration in Apache
   - Legacy patterns: Short module names, handler name mismatch
   - Modern equivalent: FQCN modules, consistent handler naming

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | Collection migration |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | Collection migration |
| `openssl_certificate:` | `community.crypto.x509_certificate:` | website_https.yml | Module replacement + parameter drift |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octals |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octals |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octals |
| `become: yes` | `become: true` | Both files | Boolean modernization |
| Missing `changed_when` | Add `changed_when` conditions | website_https.yml | Idempotency for command tasks |
| Handler name mismatch | Fix handler names | poodle_fix.yml | "Restart apache2" vs "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No Jinja2 templates present - content is defined in YAML variables using literal block scalars.

**Variables to convert to templates:**
- **conftext variable**: Should become `templates/helloworld.conf.j2`
- **webtext variable**: Should become `templates/index.html.j2`

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Apache2 package version to install"
- `cert_path`: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- `web_root`: string, default: "/var/www/helloworld", description: "Document root for the website"
- `site_name`: string, default: "helloworld", description: "Name of the Apache virtual host"
- `common_name`: string, default: "myhost", description: "Common name for SSL certificate"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbooks)
- handlers/main.yml (consolidated handlers)
- templates/helloworld.conf.j2 (from conftext variable)
- templates/index.html.j2 (from webtext variable)
- defaults/main.yml (role variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: apache2, sshd
**Templates to validate**: helloworld.conf.j2, index.html.j2

## Pre-flight checks:
```bash
# Verify Apache is running and configured
systemctl status apache2
curl -k https://localhost/
openssl s_client -connect localhost:443 -tls1_2

# Verify SSL configuration
apache2ctl -S
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify POODLE fix
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify InSpec tests pass
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

**Critical Migration Notes:**
1. **Module Parameter Drift**: `openssl_certificate` module has been replaced with `community.crypto.x509_certificate` with different parameter names
2. **Handler Consistency**: Fix handler name mismatch between "Restart apache2" (notify) and "Restart apache" (handler)
3. **Idempotency**: Add `changed_when: false` or appropriate conditions to `a2dissite`, `a2ensite`, and `a2enmod` commands
4. **Role Structure**: Convert from standalone playbooks to proper role structure with tasks, handlers, templates, and defaults
5. **Variable Templating**: Move inline content variables to proper Jinja2 templates for better maintainability