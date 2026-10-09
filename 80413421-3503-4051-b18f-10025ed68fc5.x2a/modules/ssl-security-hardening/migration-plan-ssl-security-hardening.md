---
source-path: chef-and-ansible/poodle_fix.yml
---

I can see that `poodle_fix.yml` is actually a playbook file, not a role structure. Let me analyze this file for modernization needs. Based on the analysis, this appears to be a standalone playbook rather than a role, but I can still provide a migration plan to modernize it into a proper role structure.

# Migration Plan: SSL Security Hardening (POODLE Fix)

**TLDR**: This is a standalone playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2. It needs to be converted from a playbook to a proper role structure and modernized with FQCN, proper handler naming, and role-based organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Configures SSL protocol to use only TLSv1.2 by modifying `/etc/apache2/mods-available/ssl.conf`
- Restarts Apache2 and SSH services after configuration changes
- Targets systems with Apache2 web server installed

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

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, playbook structure instead of role
   - **Step 3**: Modern equivalent: Convert to role with `ansible.builtin.replace` and proper task organization
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers**:
   - **Handler inconsistency**: Notifies "Restart apache2" but handler is named "Restart apache"
   - **Mixed FQCN usage**: Handlers already use FQCN but tasks don't
   - **Service management**: Properly restarts both Apache2 and SSH services

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| Playbook structure | Role structure | All files | Convert to proper role |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Hardcoded paths | Parameterized paths | tasks/main.yml | Make SSL config path configurable |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Missing argument specs | Add argument_specs.yml | meta/argument_specs.yml | Role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core modules)

**Role dependencies**: None
**External packages**: Apache2 web server (assumed pre-installed)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after SSL configuration"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook)
- handlers/main.yml (extracted handlers)
- defaults/main.yml (new variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 (should restart successfully)
- sshd (should restart successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache2 is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Check SSL configuration syntax
apache2ctl configtest

# Verify SSH service is running
systemctl status sshd

# Test SSL configuration after applying role
openssl s_client -connect localhost:443 -tls1_2

# Verify POODLE vulnerability is fixed
nmap --script ssl-poodle localhost
```

**Critical Migration Notes:**
1. **Handler Name Fix**: The current playbook has a mismatch between the notify name ("Restart apache2") and the actual handler name ("Restart apache"). This must be corrected.
2. **Role Structure**: Convert from standalone playbook to proper role structure with separate task and handler files.
3. **Parameterization**: Make hardcoded paths and configurations into variables for better reusability.
4. **FQCN Consistency**: Tasks use short module names while handlers already use FQCN - standardize on FQCN throughout.
5. **Boolean Modernization**: Convert `become: yes` to `become: true`.
6. **Security Validation**: Add checks to ensure the SSL configuration change actually fixes the POODLE vulnerability.