---
source-path: chef-and-ansible
---

Now I understand the structure. This is not a traditional Ansible role, but rather a collection of Ansible playbooks with legacy patterns that need modernization. Let me provide the migration specification:

# Migration Plan: chef-and-ansible (Ansible Examples)

**TLDR**: This is a collection of legacy Ansible playbooks for Apache HTTPS configuration and SSL security hardening that need modernization to current best practices. The playbooks contain multiple legacy patterns including short module names, unquoted modes, command modules without idempotency controls, and deprecated parameter syntax.

## Service Type and Configuration

**Service Type**: Web Server (Apache2) with SSL/TLS Security Hardening

**Key Operations**:
- Install and configure Apache2 web server with specific version pinning
- Generate self-signed SSL certificates using OpenSSL
- Configure HTTPS virtual host with SSL termination
- Deploy static HTML content
- Implement SSL/TLS security hardening (POODLE vulnerability fix)
- Manage Apache modules (SSL activation)
- Service management for Apache2 and SSH

## File Structure

**Playbook Files:**
```
website_https.yml
poodle_fix.yml
```

**Test Infrastructure:**
```
kitchen.yml
tests/website_https_verify.rb
tests/ssh_profile.rb
```

**Documentation:**
```
README.md
index.html
```

## Module Explanation

The collection performs operations across two main playbooks:

1. **website_https.yml** (`website_https.yml`):
   - **Package Management**: Updates apt cache and installs Apache2 with version pinning, plus SSL-related packages
   - **Certificate Generation**: Creates SSL certificate directory and generates self-signed certificates using OpenSSL modules
   - **Web Configuration**: Deploys virtual host configuration and static HTML content
   - **Apache Management**: Manages site activation/deactivation and SSL module enablement
   - Legacy patterns: Short module names, unquoted modes, command modules without idempotency
   - Modern equivalent: FQCN modules, quoted modes, proper idempotency controls

2. **poodle_fix.yml** (`poodle_fix.yml`):
   - **Security Hardening**: Fixes SSL protocol configuration to disable vulnerable protocols
   - **Service Management**: Restarts Apache2 and SSH services after configuration changes
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
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octals |
| `mode: 0755` | `mode: '0755'` | website_https.yml | Quoted octals |
| `mode: 0644` | `mode: '0644'` | website_https.yml | Quoted octals |
| `become: yes` | `become: true` | Both files | Boolean syntax |
| `update_cache=true` | `update_cache: true` | website_https.yml | Parameter syntax |
| `force: yes` | `force: true` | website_https.yml | Boolean syntax |
| `command: a2dissite` | Add `changed_when` | website_https.yml | Idempotency |
| `command: a2ensite` | Add `changed_when` | website_https.yml | Idempotency |
| `command: a2enmod` | Add `changed_when` | website_https.yml | Idempotency |
| `openssl_*` modules | `community.crypto.*` | website_https.yml | Collection migration |
| Handler name mismatch | Fix "Restart apache2" vs "Restart apache" | poodle_fix.yml | Handler consistency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- `community.crypto: ">=2.0.0"` (for OpenSSL certificate management)
- `ansible.posix: ">=1.0.0"` (for enhanced file operations)

**Role dependencies**: None (standalone playbooks)
**External packages**: 
- apache2=2.4.41-4ubuntu3.10 (version pinned)
- curl
- openssl  
- python3-openssl

**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No Jinja2 templates present. Variables are defined inline using YAML multiline strings (`conftext` and `webtext` variables).

## Argument Specification

Variables that should be parameterized in a modernized role:
- `apache_version`: string, default "2.4.41-4ubuntu3.10", Apache version to install
- `cert_path`: string, default "/etc/apache2/certs", SSL certificate directory
- `web_root`: string, default "/var/www/helloworld", Document root path
- `ssl_protocols`: string, default "-all +TLSv1.2", SSL protocol configuration
- `site_name`: string, default "helloworld", Virtual host name
- `common_name`: string, default "myhost", SSL certificate common name

## Checks for the Migration

**Files to verify**: 
- Modernized playbooks with FQCN modules
- collections/requirements.yml with crypto collection
- Updated handler names for consistency
- Idempotency controls on command tasks

**Services to check**: 
- apache2 service status and SSL configuration
- sshd service functionality
- SSL certificate validity and protocols

**Templates to validate**: 
- Virtual host configuration syntax
- SSL certificate generation parameters

## Pre-flight checks:
```bash
# Verify Apache2 installation and SSL module
sudo apache2ctl -M | grep ssl
sudo apache2ctl configtest

# Check SSL certificate validity
openssl x509 -in /etc/apache2/certs/apache.crt -text -noout

# Verify SSL protocols (should only show TLSv1.2)
sudo apache2ctl -D DUMP_MODULES | grep ssl
nmap --script ssl-enum-ciphers -p 443 localhost

# Test HTTPS connectivity
curl -k https://localhost/
curl -I -k https://localhost/

# Verify SSH service is running
systemctl status sshd
```

**Critical Migration Notes:**
1. The `openssl_*` modules require the `community.crypto` collection
2. Command tasks need `changed_when` conditions for proper idempotency
3. Handler names must be consistent between notify and handler definitions
4. Version pinning on Apache2 package should be made configurable
5. Consider using `ansible.builtin.uri` module to verify HTTPS functionality instead of relying on external tests