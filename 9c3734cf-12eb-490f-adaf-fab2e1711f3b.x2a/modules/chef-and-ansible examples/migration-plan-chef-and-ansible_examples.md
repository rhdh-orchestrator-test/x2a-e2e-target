---
source-path: chef-and-ansible
---

# Migration Plan: chef-and-ansible

**TLDR**: This is a collection of Ansible playbooks demonstrating web server security hardening and HTTPS configuration with Chef InSpec compliance testing. The playbooks need modernization for FQCN usage, proper file permissions, idempotency improvements, and structural updates to follow current Ansible best practices.

## Service Type and Configuration

**Service Type**: Web Server Security / Compliance Automation

**Key Operations**:
- Apache2 web server installation and configuration
- SSL/TLS certificate generation and management
- HTTPS virtual host setup with self-signed certificates
- SSL protocol hardening (disabling SSLv3, enforcing TLSv1.2)
- Web content deployment
- SSH security configuration validation
- Compliance testing with Chef InSpec integration

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
   - Package management: Updates apt cache and installs Apache2 with specific version
   - SSL infrastructure: Creates certificate directory, generates private key, CSR, and self-signed certificate
   - Web configuration: Deploys virtual host configuration and web content
   - Service management: Enables SSL module and activates virtual host
   - Legacy patterns: Short module names, unquoted file modes, command modules without changed_when

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - SSL hardening: Updates Apache SSL configuration to disable vulnerable protocols
   - Service restart: Triggers Apache and SSH service restarts
   - Legacy patterns: Short module names, handler name mismatch

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml, poodle_fix.yml | FQCN |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `openssl_privatekey:` | `community.crypto.openssl_privatekey:` | website_https.yml | Collection migration |
| `openssl_csr:` | `community.crypto.openssl_csr:` | website_https.yml | Collection migration |
| `openssl_certificate:` | `community.crypto.x509_certificate:` | website_https.yml | Module renamed + collection |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quote octal modes |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quote octal modes |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quote octal modes |
| `become: yes` | `become: true` | Both files | Boolean modernization |
| Missing `changed_when` | Add `changed_when: false` | website_https.yml, poodle_fix.yml | Command idempotency |
| Handler name mismatch | Fix handler names | poodle_fix.yml | "Restart apache2" vs "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No Jinja2 templates present in this collection. Variables are used inline with `content:` parameter.

## Argument Specification

Variables that should be defined in argument specs:
- `conftext`: string, required, Apache virtual host configuration
- `webtext`: string, required, HTML content for the website

## Checks for the Migration

**Files to verify**: 
- Modernized playbooks with FQCN usage
- Updated collection requirements.yml
- Fixed handler name references
- Proper file mode quoting

**Services to check**: 
- apache2 service status and SSL configuration
- sshd service configuration
- Port 443 HTTPS connectivity

**Templates to validate**: 
- No templates to validate (inline content used)

## Pre-flight checks:
```bash
# Verify Apache2 is running with SSL
systemctl status apache2
apache2ctl -M | grep ssl

# Test HTTPS connectivity
curl -k https://localhost/

# Verify SSL protocols
nmap --script ssl-enum-ciphers -p 443 localhost

# Check certificate validity
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify SSH configuration
sshd -t
```

**Critical Migration Notes:**
1. The `openssl_certificate` module has been replaced with `x509_certificate` in the community.crypto collection
2. Handler name mismatch in poodle_fix.yml needs correction ("Restart apache2" notify vs "Restart apache" handler)
3. All command tasks need `changed_when` conditions for proper idempotency
4. File modes must be quoted to prevent octal interpretation issues
5. Consider converting playbooks to roles for better reusability and structure