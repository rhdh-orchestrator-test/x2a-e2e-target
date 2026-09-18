---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `chef-and-ansible/poodle_fix.yml` is actually a standalone Ansible playbook, not a role. However, the user has requested to analyze it for migration to a modern Ansible role. I'll create a migration plan that converts this playbook into a proper Ansible role structure with modern best practices.

# Migration Plan: poodle-fix-demo

**TLDR**: This is currently a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted into a proper Ansible role structure and modernized with current best practices including FQCN usage, proper file organization, and enhanced error handling.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets `/etc/apache2/mods-available/ssl.conf` configuration file

## File Structure

**Current Structure** (Playbook):
```
poodle_fix.yml
```

**Target Role Structure**:
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

1. **SSL Protocol Fix Task** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, missing file permissions validation
   - **Step 3**: Modern equivalent: `ansible.builtin.replace` with proper validation and backup
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (`poodle_fix.yml` handlers):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: Handler name mismatch (`Restart apache` vs `Restart apache2` in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and proper service management
   - Ansible module mapping: Already using `ansible.builtin.service` (modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | Fix notify/handler name alignment |
| Missing backup parameter | `backup: true` | tasks/main.yml | Safety improvement |
| Missing validation | Add validation tasks | tasks/main.yml | Verify Apache config syntax |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing error handling | Add block/rescue | tasks/main.yml | Proper error handling |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix: ">=1.0.0" (for enhanced file operations if needed)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted after configuration change)
- sshd (restarted after configuration change)

## Template Modernization

No templates are used in this role.

## Argument Specification

Variables for meta/argument_specs.yml:
- **ssl_protocols**: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: SSL protocols to enable in Apache configuration
- **apache_ssl_conf_path**:
  - type: path
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: Path to Apache SSL configuration file
- **backup_config**:
  - type: bool
  - default: true
  - description: Whether to backup configuration files before modification
- **validate_apache_config**:
  - type: bool
  - default: true
  - description: Whether to validate Apache configuration after changes

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (configuration and restart capability)
- sshd (restart capability)

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Test Apache configuration syntax
apache2ctl configtest
# Verify SSL configuration file exists
test -f /etc/apache2/mods-available/ssl.conf
# Check if Apache service is manageable
systemctl status apache2
# Verify SSH service is manageable  
systemctl status sshd
# Test SSL protocol configuration after applying changes
openssl s_client -connect localhost:443 -tls1_2 < /dev/null
```

**Critical Migration Notes**:
1. **Handler Name Fix**: The current playbook has a mismatch between the notify name (`Restart apache2`) and handler name (`Restart apache`). This must be corrected.
2. **Structure Conversion**: This is currently a playbook that needs to be converted to a proper role structure with separate task, handler, and variable files.
3. **Safety Improvements**: Add backup functionality and Apache configuration validation to prevent service disruption.
4. **Variable Parameterization**: Make SSL protocols and file paths configurable through role variables.
5. **Error Handling**: Add proper error handling with block/rescue structure for critical configuration changes.