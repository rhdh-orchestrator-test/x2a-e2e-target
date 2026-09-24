---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is a collection of Ansible playbooks demonstrating web server security hardening and HTTPS configuration with InSpec compliance testing. The playbooks need modernization for FQCN usage, proper file permissions, idempotency improvements, and better error handling. The main focus is Apache2 SSL/TLS configuration and SSH security hardening.

## Service Type and Configuration

**Service Type**: Web Server Security / Compliance Automation

**Key Operations**:
- Install and configure Apache2 web server with HTTPS support
- Generate self-signed SSL certificates using OpenSSL
- Deploy a simple "Hello World" website with SSL/TLS encryption
- Harden SSL configuration to disable vulnerable protocols (SSL3, enable TLS1.2)
- Configure Apache virtual hosts for HTTPS
- SSH security hardening (disable root login)
- Compliance testing with Chef InSpec integration

## File Structure

**Playbook Files:**
```
poodle_fix.yml
website_https.yml
```

**Test Kitchen Configuration:**
```
kitchen.yml
```

**InSpec Test Files:**
```
tests/website_https_verify.rb
tests/ssh_profile.rb
```

**Documentation:**
```
README.md
index.html
```

## Module Explanation

The collection performs operations in this order:

1. **website_https.yml** (`website_https.yml`):
   - **Package Management**: Updates apt cache and installs Apache2, curl, openssl, python3-openssl
   - **SSL Certificate Generation**: Creates certificate directory, generates private key, CSR, and self-signed certificate
   - **Web Content Deployment**: Creates virtual host configuration and deploys HTML content
   - **Apache Configuration**: Enables SSL module and configures virtual hosts
   - Legacy patterns: Short module names, unquoted file modes, command modules without changed_when
   - Modern equivalent: FQCN modules, quoted modes, idempotent alternatives

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - **SSL Hardening**: Fixes SSL protocol configuration in Apache to disable vulnerable protocols
   - **Service Management**: Restarts Apache2 and SSH services
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
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quote octal modes |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quote octal modes |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quote octal modes |
| `command: a2dissite` | Add `changed_when: false` | website_https.yml | Idempotency |
| `command: a2ensite` | Add `changed_when: false` | website_https.yml | Idempotency |
| `command: a2enmod` | Add `changed_when: false` | website_https.yml | Idempotency |
| `become: yes` | `become: true` | Both files | Boolean modernization |
| Handler name mismatch | Fix "Restart apache2" → "Restart apache" | poodle_fix.yml | Handler consistency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No Jinja2 templates present - content is defined as YAML variables and deployed via copy module.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, Apache virtual host configuration content
- `webtext`: string, HTML content for the website
- Target host configuration variables for SSL certificate generation

## Checks for the Migration

**Files to verify**: 
- Modernized playbooks with FQCN modules
- Collection requirements.yml file
- Updated handler names and task idempotency

**Services to check**: 
- apache2 service status and SSL configuration
- sshd service configuration
- Port 443 HTTPS listener

**Templates to validate**: 
- None (content deployed via variables)

## Pre-flight checks:
```bash
# Verify Apache2 is running with SSL
sudo systemctl status apache2
sudo netstat -tlnp | grep :443

# Test HTTPS connectivity
curl -k https://localhost/

# Verify SSL protocols
openssl s_client -connect localhost:443 -tls1_2

# Check SSH configuration
sudo sshd -T | grep permitrootlogin

# Run InSpec compliance tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

**Critical Migration Notes:**
1. The `openssl_certificate` module has been replaced with `x509_certificate` in the community.crypto collection
2. All command tasks need `changed_when` conditions for proper idempotency
3. Handler name mismatch in poodle_fix.yml needs correction
4. File modes must be quoted to prevent octal interpretation issues
5. Consider using `apache2_module` instead of command-based `a2enmod`/`a2dissite` for better idempotency