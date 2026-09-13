---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a standalone Ansible playbook, not a role. However, the user has requested to analyze it for migration to a modern Ansible role. I'll create a migration plan that converts this playbook into a proper Ansible role structure with modern best practices.

# Migration Plan: poodle_fix

**TLDR**: This is currently a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted into a proper Ansible role structure and modernized with current best practices including FQCN usage, proper error handling, and role organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets `/etc/apache2/mods-available/ssl.conf` configuration file

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
None required

**Static Files:**
None required

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, missing file permissions validation
   - **Step 3**: Modern equivalent: `ansible.builtin.replace` with proper validation and backup
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services when configuration changes
   - **Step 2**: Legacy patterns found: Handler name mismatch (`Restart apache` vs `Restart apache2` in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and proper service management
   - Ansible module mapping: Already uses FQCN `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | Fix notify/handler name alignment |
| Missing backup parameter | `backup: true` | tasks/main.yml | Safety improvement |
| Missing validation | Add validation task | tasks/main.yml | Verify Apache config syntax |
| Playbook structure | Role structure | All files | Convert to proper role |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix (for advanced file operations if needed)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted when SSL config changes)
- sshd (restarted when SSL config changes)

## Template Modernization

No templates are used in this role.

## Argument Specification

Variables for meta/argument_specs.yml:
- `poodle_fix_ssl_protocols`: string, default: "-all +TLSv1.2", SSL protocols to configure
- `poodle_fix_apache_ssl_conf`: string, default: "/etc/apache2/mods-available/ssl.conf", Path to Apache SSL configuration
- `poodle_fix_backup_config`: boolean, default: true, Whether to backup original config
- `poodle_fix_validate_config`: boolean, default: true, Whether to validate Apache config after changes

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should restart successfully after SSL config change)
- sshd (should restart successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Test Apache configuration syntax
apache2ctl configtest
# Verify SSL configuration file exists
test -f /etc/apache2/mods-available/ssl.conf
# Check current SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf
# Verify services are running
systemctl is-active apache2
systemctl is-active sshd
```

**Critical Issues Found:**
1. **Handler Name Mismatch**: The notify calls `Restart apache2` but handler is named `Restart apache` - this will cause the handler to never execute
2. **Missing FQCN**: The `replace` module needs to be `ansible.builtin.replace`
3. **Boolean Syntax**: `become: yes` should be `become: true`
4. **Missing Safety Features**: No backup of original configuration file
5. **No Validation**: No verification that Apache configuration is valid after changes
6. **Playbook vs Role**: Current structure is a playbook, needs conversion to proper role structure