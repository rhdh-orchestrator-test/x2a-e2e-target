---
source-path: chef-and-ansible
---

Now I understand the structure. This is not a traditional Ansible role but rather a collection of Ansible playbooks with Chef InSpec tests. Let me analyze the content for modernization needs.

# Migration Plan: chef-and-ansible

**TLDR**: This is a collection of Ansible playbooks (not a traditional role) that demonstrates SSL/TLS security hardening for Apache web servers, including POODLE vulnerability fixes and HTTPS website deployment. The playbooks need significant modernization including FQCN adoption, loop modernization, proper file permissions, idempotency improvements, and structural reorganization into a proper Ansible role format.

## Service Type and Configuration

**Service Type**: Web Server Security / SSL/TLS Hardening

**Key Operations**:
- Apache2 web server installation and configuration
- SSL/TLS certificate generation (self-signed)
- POODLE vulnerability mitigation (SSL protocol hardening)
- HTTPS virtual host configuration
- Static website deployment
- SSH daemon management alongside Apache

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
   - **SSL Infrastructure**: Creates certificate directory, generates private key, CSR, and self-signed certificate
   - **Web Configuration**: Deploys virtual host configuration and static HTML content
   - **Service Management**: Enables SSL module, activates/deactivates sites
   - Legacy patterns: Short module names, unquoted file modes, command modules without changed_when
   - Modern equivalent: FQCN modules, quoted modes, proper idempotency checks

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - **Security Hardening**: Fixes POODLE vulnerability by updating SSL protocol configuration
   - **Service Restart**: Restarts both Apache and SSH services
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
| `update_cache=true` | `update_cache: true` | website_https.yml | YAML syntax |
| Missing `changed_when` | Add `changed_when: false` | website_https.yml, poodle_fix.yml | Idempotency |
| Handler name mismatch | Fix "Restart apache2" → "Restart apache" | poodle_fix.yml | Handler consistency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- community.crypto: ">=2.0.0"
- ansible.posix: ">=1.0.0"

**Role dependencies**: None (standalone playbooks)
**External packages**: apache2, curl, openssl, python3-openssl
**Services managed**: apache2, sshd

## Template Modernization

No Jinja2 templates present. The playbooks use inline YAML multiline strings for configuration content.

## Argument Specification

Variables that should be parameterized in a modern role structure:
- `apache_version`: string, default: "2.4.41-4ubuntu3.10", description: "Specific Apache version to install"
- `cert_path`: string, default: "/etc/apache2/certs", description: "Directory for SSL certificates"
- `web_root`: string, default: "/var/www/helloworld", description: "Document root for website"
- `site_name`: string, default: "helloworld", description: "Virtual host site name"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols configuration"

## Checks for the Migration

**Files to create in modern role structure**:
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml
- templates/virtualhost.conf.j2
- templates/index.html.j2
- collections/requirements.yml
- execution-environment.yml

**Services to check**: apache2, sshd
**Templates to validate**: New templates for virtual host and HTML content

## Pre-flight checks:
```bash
# Verify Apache is installed and running
systemctl status apache2

# Check SSL certificate validity
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify HTTPS site accessibility
curl -k https://localhost/

# Check SSL protocol configuration
grep SSLProtocol /etc/apache2/mods-available/ssl.conf

# Verify virtual host is enabled
apache2ctl -S

# Test SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost
```

**Critical Migration Notes**:
1. **Structure Transformation**: Convert from standalone playbooks to proper Ansible role structure
2. **Collection Dependencies**: The `openssl_*` modules have moved to `community.crypto` collection with some parameter changes
3. **Module Deprecation**: `openssl_certificate` is now `x509_certificate` in community.crypto
4. **Idempotency**: All `command` tasks need `changed_when` conditions
5. **Handler Consistency**: Fix handler name mismatch between notification and definition
6. **Security**: Consider using Let's Encrypt instead of self-signed certificates for production
7. **Version Pinning**: The specific Apache version may need updating for current Ubuntu releases