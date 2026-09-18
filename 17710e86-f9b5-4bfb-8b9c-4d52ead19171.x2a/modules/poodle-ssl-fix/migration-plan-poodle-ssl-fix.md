---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role. However, I'll analyze it as if it were to be converted into a modern Ansible role structure. Let me provide the migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. The main modernization needs include converting from playbook to role structure, fixing FQCN usage, correcting handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Configures Apache to use only TLSv1.2 protocol
- Restarts Apache and SSH services after configuration changes
- Addresses POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability

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

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, handler naming inconsistency
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache and SSH services
   - **Step 2**: Legacy patterns found: Handler name mismatch ("Restart apache" vs "Restart apache2" in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and proper FQCN usage

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Hardcoded paths | Variables | tasks/main.yml | `/etc/apache2/mods-available/ssl.conf` → variable |
| Hardcoded protocols | Variables | tasks/main.yml | `TLSv1.2` → configurable variable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (included by default)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2
- sshd

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**: 
- apache2 (running and enabled)
- sshd (running and enabled)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Check current SSL configuration
grep SSLProtocol /etc/apache2/mods-available/ssl.conf
# Verify Apache configuration syntax
apache2ctl configtest
# Check service status
systemctl status apache2
systemctl status sshd
# Test SSL configuration after changes
openssl s_client -connect localhost:443 -tls1_2
```

**Critical Issues Found:**
1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Missing FQCN**: The `replace` module should be `ansible.builtin.replace`
3. **Boolean Syntax**: `become: yes` should be `become: true`
4. **Hardcoded Values**: Configuration paths and SSL protocols should be variables for flexibility
5. **Missing Role Structure**: Current playbook needs conversion to proper role structure with argument specifications

**Security Considerations:**
- This role addresses the POODLE vulnerability (CVE-2014-3566)
- Disabling older SSL/TLS protocols may affect compatibility with legacy clients
- Consider adding validation to ensure TLS configuration doesn't break existing connections