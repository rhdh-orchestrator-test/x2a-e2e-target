---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can create a migration plan to convert this into a proper modern Ansible role. Let me provide the detailed migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, updating module syntax to use FQCN, fixing handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enforces TLS 1.2 only protocol usage
- Manages Apache and SSH service restarts after configuration changes

## File Structure

**Current Structure (Playbook):**
```
poodle_fix.yml
```

**Target Role Structure:**
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
```

**Task Files:**
tasks/main.yml

**Handler Files:**
handlers/main.yml

**Variable Files:**
defaults/main.yml

**Meta:**
meta/main.yml
meta/argument_specs.yml

**Templates:**
None

**Static Files:**
None

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, handler naming inconsistency
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent handler naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by the role)
**Services managed**: 
- apache2 (restarted after SSL configuration change)
- sshd (restarted as part of security hardening)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task with FQCN)
- handlers/main.yml (consistent handler names)
- defaults/main.yml (configurable variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (input validation)

**Services to check**: 
- apache2 (SSL configuration applied and service restarted)
- sshd (service restarted as part of security hardening)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
sudo grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache service status
sudo systemctl status apache2

# Verify SSH service status  
sudo systemctl status sshd

# Test SSL configuration with openssl
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"

# Verify POODLE vulnerability is fixed
nmap --script ssl-poodle localhost -p 443
```

**Critical Migration Notes**:
1. **Handler Naming Issue**: The current playbook has a mismatch between the notify target ("Restart apache2") and the actual handler name ("Restart apache"). This needs to be fixed for idempotency.
2. **Security Context**: This role addresses CVE-2014-3566 (POODLE attack) by disabling SSL 3.0 and enforcing TLS 1.2.
3. **Service Dependencies**: Both Apache and SSH services are restarted, indicating this might be part of a broader security hardening playbook.
4. **Configuration Path**: The role assumes Debian/Ubuntu Apache structure (`/etc/apache2/mods-available/ssl.conf`). Consider adding OS-specific variable support for broader compatibility.