---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. However, I can create a migration plan to convert this into a modern Ansible role for SSL security hardening. Let me provide the migration specification:

# Migration Plan: ssl-security-hardening

**TLDR**: This legacy playbook performs SSL/TLS security hardening by fixing the POODLE vulnerability in Apache SSL configuration. It needs to be converted from a standalone playbook into a modern Ansible role with proper structure, FQCN usage, handler naming consistency, and comprehensive SSL security hardening capabilities.

## Service Type and Configuration

**Service Type**: Security Hardening (SSL/TLS Configuration)

**Key Operations**:
- Fixes POODLE vulnerability by disabling SSLv3 and weak protocols
- Configures Apache SSL to use only TLSv1.2
- Manages Apache2 and SSH service restarts
- Targets SSL protocol configuration in Apache modules

## File Structure

**Current Structure** (Legacy Playbook):
```
poodle_fix.yml
```

**Target Role Structure** (Modern):
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
templates/ssl.conf.j2
vars/main.yml
```

**Task Files:**
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml
vars/main.yml

**Meta:**
meta/main.yml
meta/argument_specs.yml

**Templates:**
templates/ssl.conf.j2

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Hardening** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, basic regex replacement
   - **Step 3**: Modern equivalent: FQCN module usage, template-based configuration, comprehensive SSL hardening
   - Ansible module mapping: `replace` → `ansible.builtin.replace` (with template alternative)

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services
   - **Step 2**: Legacy patterns: Handler name mismatch (`Restart apache` vs `Restart apache2` in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming, proper service management
   - Ansible module mapping: Already uses FQCN `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | `Restart apache` → `Restart apache2` |
| Hardcoded paths | Variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` → `{{ ssl_config_path }}` |
| Inline regex | Template-based config | tasks/main.yml | Replace regex with template management |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Limited SSL hardening | Comprehensive hardening | tasks/main.yml | Add cipher suites, HSTS, etc. |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix: ">=1.0.0" (for enhanced file operations)

**Role dependencies**: None (standalone security hardening role)

**External packages**: 
- apache2 (assumed to be pre-installed)
- openssl (for SSL/TLS functionality)

**Services managed**: 
- apache2 (restarted after SSL configuration changes)
- sshd (restarted for SSH hardening if applicable)

## Template Modernization

**ssl.conf.j2**: New template to replace inline regex replacement
- Comprehensive SSL/TLS configuration
- Configurable protocol versions
- Cipher suite management
- Security headers configuration

## Argument Specification

Variables for meta/argument_specs.yml:

- **ssl_protocols**: list, default: ['+TLSv1.2', '+TLSv1.3'], description: "Allowed SSL/TLS protocols"
- **ssl_config_path**: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- **ssl_cipher_suite**: string, default: "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS", description: "SSL cipher suite configuration"
- **enable_hsts**: boolean, default: true, description: "Enable HTTP Strict Transport Security"
- **hsts_max_age**: integer, default: 31536000, description: "HSTS max-age in seconds"
- **apache_service_name**: string, default: "apache2", description: "Apache service name"
- **restart_services**: list, default: ["apache2"], description: "Services to restart after SSL configuration"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL hardening tasks)
- handlers/main.yml (service restart handlers)
- templates/ssl.conf.j2 (SSL configuration template)
- defaults/main.yml (default variables)
- meta/argument_specs.yml (role validation)
- vars/main.yml (role variables)
- meta/main.yml (role metadata)

**Services to check**: 
- apache2 (SSL configuration applied)
- sshd (if SSH hardening included)

**Templates to validate**: 
- ssl.conf.j2 (proper SSL/TLS configuration syntax)

## Pre-flight checks:
```bash
# Verify Apache SSL module is enabled
apache2ctl -M | grep ssl

# Test SSL configuration syntax
apache2ctl configtest

# Verify SSL protocols (after applying changes)
openssl s_client -connect localhost:443 -tls1_2

# Check for POODLE vulnerability mitigation
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify HSTS headers (if enabled)
curl -I https://localhost/ | grep -i strict-transport-security

# Test Apache service restart capability
systemctl status apache2
```

**Additional Security Validations**:
- SSL Labs test simulation for configuration strength
- Cipher suite validation against current security standards
- Protocol version verification (no SSLv2/SSLv3/TLSv1.0/TLSv1.1)
- Certificate chain validation
- Perfect Forward Secrecy verification