---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is a collection of Ansible playbooks demonstrating web server security hardening and HTTPS configuration with InSpec compliance testing. The playbooks need modernization for FQCN usage, proper file permissions, idempotency improvements, and better error handling.

## Service Type and Configuration

**Service Type**: Web Server Security / Compliance Automation

**Key Operations**:
- Apache2 web server installation and configuration
- SSL/TLS certificate generation and management
- HTTPS virtual host setup with self-signed certificates
- SSL protocol hardening (disabling SSLv3, enforcing TLSv1.2)
- Web content deployment
- SSH security configuration validation
- Compliance testing with InSpec

## File Structure

**Playbook Files:**
```
poodle_fix.yml
website_https.yml
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

The playbooks perform operations in this order:

1. **website_https.yml** (`website_https.yml`):
   - **Package Management**: Updates apt cache and installs Apache2 with specific version, plus SSL dependencies
   - **Certificate Management**: Creates certificate directory, generates private key, CSR, and self-signed certificate
   - **Web Configuration**: Deploys virtual host configuration and web content
   - **Service Configuration**: Enables SSL module and activates the new site
   - Legacy patterns: Short module names, unquoted file modes, command modules without changed_when
   - Modern equivalent: FQCN modules, quoted modes, proper idempotency checks

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - **SSL Hardening**: Fixes SSL protocol configuration in Apache to disable vulnerable protocols
   - **Service Management**: Restarts Apache and SSH services after configuration changes
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
| `openssl_certificate:` | `community.crypto.x509_certificate:` | website_https.yml | Module replacement + parameter changes |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octals |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octals |
| `command: a2dissite` | `ansible.builtin.command: a2dissite` + `changed_when` | website_https.yml | Idempotency |
| `command: a2ensite` | `ansible.builtin.command: a2ensite` + `changed_when` | website_https.yml | Idempotency |
| `command: a2enmod` | `ansible.builtin.command: a2enmod` + `changed_when` | website_https.yml | Idempotency |
| Handler name mismatch | Consistent naming | poodle_fix.yml | Handler references |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No Jinja2 templates present in this collection. All content is defined as inline variables.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `conftext`: string, required, Apache virtual host configuration
- `webtext`: string, required, HTML content for the website
- Target host configuration variables for certificate generation

## Checks for the Migration

**Files to verify**: 
- Modernized playbooks with FQCN modules
- Collection requirements.yml file
- Updated handler references
- Proper idempotency checks on command tasks

**Services to check**: 
- apache2 service status and configuration
- SSL certificate validity
- HTTPS connectivity on port 443

**Templates to validate**: 
- None (no Jinja2 templates present)

## Pre-flight checks:
```bash
# Verify Apache is running with SSL
systemctl status apache2
netstat -tlnp | grep :443

# Test HTTPS connectivity
curl -k https://localhost/

# Verify SSL protocols
openssl s_client -connect localhost:443 -ssl3 2>&1 | grep -i "protocol"
openssl s_client -connect localhost:443 -tls1_2 2>&1 | grep -i "protocol"

# Run InSpec compliance tests
inspec exec tests/website_https_verify.rb
inspec exec tests/ssh_profile.rb
```

**Critical Modernization Notes:**
1. The `openssl_certificate` module has been replaced with `x509_certificate` in community.crypto collection with different parameters
2. All command tasks need `changed_when` conditions for proper idempotency
3. Handler name in poodle_fix.yml ("Restart apache2") doesn't match handler definition ("Restart apache")
4. File modes need to be quoted to prevent YAML interpretation as integers
5. Consider using `apache2_module` from community.general collection instead of `a2enmod` command for better idempotency