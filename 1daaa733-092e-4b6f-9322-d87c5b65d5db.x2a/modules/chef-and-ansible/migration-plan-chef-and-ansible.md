---
source-path: chef-and-ansible
---

Now I have a complete understanding of this Ansible project. Let me provide the migration plan:

# Migration Plan: chef-and-ansible

**TLDR**: This is a demonstration project showing Ansible playbooks for Apache HTTPS configuration and SSL security hardening (POODLE vulnerability fix), designed to work with Chef InSpec for compliance testing. The main modernization needs include FQCN adoption, loop modernization, proper file permissions, idempotency improvements, and converting playbooks into a proper Ansible role structure.

## Service Type and Configuration

**Service Type**: Web Server (Apache2 with SSL/TLS Security Hardening)

**Key Operations**:
- Install and configure Apache2 web server with specific version pinning
- Generate self-signed SSL certificates using OpenSSL
- Configure HTTPS virtual host for a "Hello World" website
- Implement SSL security hardening (disable SSL 3.0, enable TLS 1.2 only)
- Fix POODLE vulnerability by updating SSL protocol configuration
- Manage Apache modules (SSL activation)
- Deploy static web content

## File Structure

**Playbook Files:**
```
website_https.yml
poodle_fix.yml
```

**Static Files:**
```
index.html
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
```

## Module Explanation

The project contains two main playbooks that perform operations in this order:

1. **website_https.yml** (`website_https.yml`):
   - **Package Management**: Updates apt cache and installs Apache2 with version pinning, plus SSL-related packages
   - **Certificate Generation**: Creates SSL certificate directory and generates self-signed certificates
   - **Web Configuration**: Configures Apache virtual host for HTTPS and deploys static content
   - **Service Management**: Activates SSL module and virtual host configuration
   - Legacy patterns: Short module names, unquoted file modes, command modules without idempotency checks
   - Modern equivalent: FQCN modules, quoted file modes, proper changed_when conditions

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - **Security Hardening**: Fixes POODLE vulnerability by updating SSL protocol configuration in Apache
   - **Service Restart**: Restarts Apache and SSH services after configuration changes
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
| `openssl_certificate:` | `community.crypto.x509_certificate:` | website_https.yml | Module renamed + collection |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octals |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octals |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octals |
| `command: a2dissite` | Add `changed_when` | website_https.yml | Idempotency |
| `command: a2ensite` | Add `changed_when` | website_https.yml | Idempotency |
| `command: a2enmod` | Add `changed_when` | website_https.yml | Idempotency |
| Handler name mismatch | Fix handler names | poodle_fix.yml | "Restart apache2" vs "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No Jinja2 templates present in this project. The configuration content is embedded as YAML variables using literal block scalars.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, Apache virtual host configuration content
- `webtext`: string, HTML content for the website
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache package version to install
- `cert_path`: string, default "/etc/apache2/certs", SSL certificate directory
- `web_root`: string, default "/var/www/helloworld", Document root directory
- `site_name`: string, default "helloworld", Virtual host name

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (consolidated from website_https.yml)
- tasks/ssl_hardening.yml (from poodle_fix.yml)
- handlers/main.yml (consolidated handlers)
- defaults/main.yml (extracted variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)
- files/index.html (static content)
- collections/requirements.yml (collection dependencies)

**Services to check**: apache2, sshd
**Templates to validate**: None (using copy with content)

## Pre-flight checks:
```bash
# Verify Apache is running with SSL
systemctl status apache2
ss -tlnp | grep :443

# Test HTTPS connectivity
curl -k https://localhost/
openssl s_client -connect localhost:443 -tls1_2

# Verify SSL protocols (should only show TLS 1.2)
nmap --script ssl-enum-ciphers -p 443 localhost

# Check Apache configuration
apache2ctl configtest
apache2ctl -S

# Verify certificate files
ls -la /etc/apache2/certs/
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout
```

**Additional Migration Notes:**
1. The project should be restructured from standalone playbooks into a proper Ansible role
2. The `openssl_certificate` module has been replaced with `x509_certificate` in the community.crypto collection
3. Command tasks need `changed_when` conditions to prevent unnecessary "changed" status
4. Handler names need to be consistent between tasks and handler definitions
5. Consider using `ansible.builtin.apache2_module` instead of command-based `a2enmod`/`a2dismod`
6. The Chef InSpec tests should be preserved as they provide valuable compliance validation