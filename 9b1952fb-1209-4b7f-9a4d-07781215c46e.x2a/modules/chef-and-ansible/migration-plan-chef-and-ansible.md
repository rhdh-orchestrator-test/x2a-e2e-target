---
source-path: chef-and-ansible
---

Based on my analysis, I can see that this is not a traditional Ansible role structure, but rather a collection of Ansible playbooks with Chef InSpec tests for compliance verification. Let me provide the migration plan:

# Migration Plan: chef-and-ansible

**TLDR**: This is a collection of standalone Ansible playbooks (not a role) that demonstrates web server security hardening and HTTPS configuration with Chef InSpec compliance testing. The main modernization needs include FQCN adoption, loop modernization, proper file permissions, idempotency improvements, and restructuring into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Web Server Security / SSL/TLS Hardening

**Key Operations**:
- Install and configure Apache2 web server with HTTPS
- Generate self-signed SSL certificates using OpenSSL
- Deploy a simple "Hello World" website
- Configure SSL/TLS security (disable SSLv3, enable TLSv1.2)
- Fix POODLE vulnerability by updating SSL protocols
- Manage Apache virtual hosts and SSL modules
- Compliance testing with Chef InSpec

## File Structure

**Playbook Files:**
```
website_https.yml
poodle_fix.yml
```

**Configuration Files:**
```
kitchen.yml
README.md
index.html
```

**Test Files:**
```
tests/website_https_verify.rb
tests/ssh_profile.rb
```

## Module Explanation

The collection performs operations through two main playbooks:

1. **website_https.yml** (`website_https.yml`):
   - **Package Management**: Updates apt cache and installs Apache2, curl, openssl, python3-openssl
   - **Certificate Generation**: Creates SSL certificate directory, generates private key, CSR, and self-signed certificate
   - **Web Configuration**: Deploys virtual host configuration and website content using inline variables
   - **Service Configuration**: Enables SSL module, activates virtual host, deactivates default site
   - Legacy patterns: Short module names, unquoted file modes, command modules without changed_when
   - Modern equivalent: FQCN modules, quoted modes, idempotent alternatives

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - **Security Hardening**: Fixes POODLE vulnerability by updating SSL protocol configuration
   - **Handler Issues**: Handler name mismatch ("Restart apache2" vs "Restart apache")
   - Legacy patterns: Short module names, handler name inconsistency
   - Modern equivalent: FQCN modules, consistent handler naming

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN + idempotency |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octals |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octals |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octals |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | Collection migration |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | Collection migration |
| `openssl_certificate:` | `community.crypto.x509_certificate:` | website_https.yml | Module replacement |
| `command: a2dissite` | `ansible.builtin.command:` + `changed_when` | website_https.yml | Idempotency |
| `command: a2ensite` | `ansible.builtin.command:` + `changed_when` | website_https.yml | Idempotency |
| `command: a2enmod` | `ansible.builtin.command:` + `changed_when` | website_https.yml | Idempotency |
| Handler name mismatch | Consistent naming | poodle_fix.yml | "Restart apache2" → "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None (standalone playbooks)
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No Jinja2 templates present. Inline variables used in playbooks should be moved to separate variable files in a role structure.

## Argument Specification

Variables that should be in meta/argument_specs.yml for role conversion:
- `conftext`: string, Apache virtual host configuration template
- `webtext`: string, HTML content for the website
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache package version
- `cert_path`: string, default "/etc/apache2/certs", SSL certificate directory
- `web_root`: string, default "/var/www/helloworld", Website document root
- `common_name`: string, default "myhost", SSL certificate common name

## Checks for the Migration

**Files to verify**: 
- Role structure: tasks/main.yml, handlers/main.yml, defaults/main.yml, meta/main.yml, meta/argument_specs.yml
- Collections requirements.yml
- Execution environment files: execution-environment.yml, bindep.txt

**Services to check**: apache2, sshd
**Templates to validate**: None (convert inline vars to templates)

## Pre-flight checks:
```bash
# Verify Apache is running with SSL
systemctl status apache2
netstat -tlnp | grep :443

# Test HTTPS connectivity
curl -k https://localhost/
openssl s_client -connect localhost:443 -servername localhost

# Verify SSL protocols
nmap --script ssl-enum-ciphers -p 443 localhost

# Check certificate validity
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify virtual host configuration
apache2ctl -S
```

## Role Structure Conversion

**Critical Note**: This collection needs to be converted from standalone playbooks to a proper Ansible role structure:

1. **Create role directory structure**:
   ```
   roles/apache_https_hardening/
   ├── tasks/main.yml
   ├── handlers/main.yml  
   ├── defaults/main.yml
   ├── vars/main.yml
   ├── templates/
   ├── meta/main.yml
   └── meta/argument_specs.yml
   ```

2. **Split playbook tasks** into logical task files:
   - `tasks/packages.yml` - Package installation
   - `tasks/certificates.yml` - SSL certificate generation
   - `tasks/configuration.yml` - Apache configuration
   - `tasks/security.yml` - POODLE fix and security hardening

3. **Convert inline variables** to templates:
   - `templates/virtualhost.conf.j2` - Apache virtual host configuration
   - `templates/index.html.j2` - Website content

4. **Handler consolidation**: Fix handler name mismatches and ensure all handlers are properly defined

5. **Add idempotency**: Use `changed_when` conditions for all command/shell tasks

This migration transforms a collection of demonstration playbooks into a production-ready, reusable Ansible role following current best practices.