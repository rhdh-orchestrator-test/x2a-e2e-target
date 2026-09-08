---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not an Ansible role. However, the user has requested to analyze it for migration to a modern Ansible role. I'll create a migration plan that converts this playbook into a proper Ansible role structure with modern best practices.

# Migration Plan: poodle_fix

**TLDR**: This is currently a simple playbook that fixes SSL configuration in Apache to address the POODLE vulnerability by enforcing TLSv1.2. It needs to be converted from a playbook to a proper Ansible role structure and modernized with current best practices including FQCN usage, proper file organization, and argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes SSL protocol configuration in Apache to mitigate POODLE vulnerability
- Replaces SSLProtocol directive to enforce TLSv1.2 only
- Manages Apache2 and SSH service restarts
- Targets SSL configuration file `/etc/apache2/mods-available/ssl.conf`

## File Structure

**Current Structure** (Playbook):
```
poodle_fix.yml
```

**Target Role Structure** (to be created):
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
None required

**Static Files:**
None required

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, old-style parameter formatting
   - **Step 3**: Modern equivalent: `ansible.builtin.replace` with proper parameter structure
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services when SSL config changes
   - **Step 2**: Handler name mismatch issue (notifies "Restart apache2" but handler named "Restart apache")
   - **Step 3**: Fix handler name consistency and use FQCN
   - Ansible module mapping: `service` → `ansible.builtin.service` (already modern in handlers)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `dest=` parameter style | `path:` parameter | tasks/main.yml | Parameter name modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Hardcoded paths | Configurable variables | tasks/main.yml | Make SSL config path configurable |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection, included by default)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in the current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration to enforce"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after SSL config change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after SSL config change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should restart after configuration change)
- sshd (should restart after configuration change)

**Templates to validate**: 
None required

## Pre-flight checks:
```bash
# Verify Apache SSL module is enabled
apache2ctl -M | grep ssl

# Check current SSL configuration
grep -n "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Test Apache configuration syntax
apache2ctl configtest

# Verify services are running after changes
systemctl status apache2
systemctl status sshd

# Test SSL configuration (after applying changes)
openssl s_client -connect localhost:443 -tls1_2
```

**Critical Issues to Address in Migration:**
1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Playbook to Role Conversion**: Complete restructuring from playbook format to role format
3. **Parameter Modernization**: The `dest=` parameter should be `path=` for the replace module
4. **FQCN Implementation**: Add fully qualified collection names for all modules
5. **Variable Configuration**: Make hardcoded paths and settings configurable through role variables
6. **Boolean Modernization**: Convert `become: yes` to `become: true`