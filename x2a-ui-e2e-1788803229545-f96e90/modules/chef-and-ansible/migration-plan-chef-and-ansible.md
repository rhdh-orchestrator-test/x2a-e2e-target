---
source-path: chef-and-ansible
---

Now I understand the structure. This is not a traditional Ansible role but rather a collection of Ansible playbooks with Chef InSpec testing. Let me analyze the content for modernization needs.

# Migration Plan: chef-and-ansible

**TLDR**: This is a collection of Ansible playbooks (not a traditional role) that demonstrates SSL/TLS security hardening for Apache web servers with Chef InSpec testing integration. The playbooks need significant modernization including FQCN adoption, loop syntax updates, proper file permissions, idempotency improvements, and handler corrections.

## Service Type and Configuration

**Service Type**: Web Server Security / SSL/TLS Configuration

**Key Operations**:
- Apache2 web server installation and configuration
- SSL/TLS certificate generation (self-signed)
- Virtual host configuration for HTTPS
- SSL protocol hardening (POODLE vulnerability fix)
- Static website deployment
- SSH daemon management

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
tests/ssh_profile.rb
tests/website_https_verify.rb
```

## Module Explanation

The collection performs operations across two main playbooks:

1. **website_https.yml** (`website_https.yml`):
   - **Package Management**: Updates apt cache and installs Apache2 with specific version pinning
   - **SSL Certificate Setup**: Creates certificate directory, generates private key, CSR, and self-signed certificate
   - **Virtual Host Configuration**: Deploys HTTPS virtual host configuration and static website content
   - **Service Configuration**: Enables SSL module and activates virtual host
   - Ansible module mapping: `apt` → `ansible.builtin.apt`, `file` → `ansible.builtin.file`, `copy` → `ansible.builtin.copy`, `command` → `ansible.builtin.command`

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - **SSL Hardening**: Fixes SSL protocol configuration to disable vulnerable protocols and enable only TLSv1.2
   - **Service Management**: Restarts Apache2 and SSH services after configuration changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

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
| `apt: update_cache=true` | `ansible.builtin.apt: update_cache: true` | website_https.yml | Parameter syntax |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Octal quoting |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Octal quoting |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Octal quoting |
| `become: yes` | `become: true` | Both files | Boolean syntax |
| Missing `changed_when` | Add `changed_when: false` | website_https.yml | Idempotency for command tasks |
| Handler name mismatch | Fix handler names | poodle_fix.yml | Handler "Restart apache2" called but "Restart apache" defined |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"

**Role dependencies**: None
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No Jinja2 templates present - configuration content is embedded in playbook variables.

## Argument Specification

Since these are playbooks rather than roles, argument specifications would be converted to playbook-level variable documentation:

**Variables to document:**
- `conftext`: string, Apache virtual host configuration content
- `webtext`: string, HTML content for the test website

## Checks for the Migration

**Files to verify**: 
- Modernized website_https.yml
- Modernized poodle_fix.yml
- collections/requirements.yml (new)

**Services to check**: 
- apache2 service status and SSL configuration
- sshd service status

**Templates to validate**: 
- None (embedded configuration content)

## Pre-flight checks:
```bash
# Verify Apache2 is running with SSL enabled
sudo systemctl status apache2
sudo apache2ctl -M | grep ssl

# Test HTTPS connectivity
curl -k https://localhost/

# Verify SSL protocol configuration
openssl s_client -connect localhost:443 -tls1_2

# Check certificate validity
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify SSH service
sudo systemctl status sshd
```

**Critical Issues to Address:**
1. **Handler Name Mismatch**: In `poodle_fix.yml`, the notify calls "Restart apache2" but handler is named "Restart apache"
2. **Missing Idempotency**: Command tasks need `changed_when` conditions
3. **Module Migration**: OpenSSL modules moved to community.crypto collection with some parameter changes
4. **File Permissions**: All file mode parameters need quoting for octal values
5. **Collection Dependencies**: Need to add community.crypto collection requirement