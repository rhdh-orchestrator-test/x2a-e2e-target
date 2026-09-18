---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is currently a playbook, not a role. The analysis summary shows 0 files because this is a single playbook file rather than a role structure. Let me provide a migration plan to convert this playbook into a modern Ansible role.

# Migration Plan: poodle_fix

**TLDR**: This is currently a playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook into a proper Ansible role structure and modernized to follow current best practices including FQCN usage, proper handler naming, and role organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Restarts Apache2 and SSH services after configuration changes

## File Structure

**Current Structure**: Single playbook file
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
None

**Static Files:**
None

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, handler name mismatch
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper handler references
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers**:
   - **Handler Issue**: Handler names don't match notification names ("Restart apache" vs "Restart apache2")
   - **Modern equivalent**: Consistent handler naming and FQCN usage

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" in both |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded paths | Parameterized variables | tasks/main.yml | Make configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by external role/playbook)
**Services managed**: 
- apache2 (restarted)
- sshd (restarted)

## Template Modernization

No templates present in current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml
- handlers/main.yml  
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**: 
- apache2 service status
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Verify SSH daemon is running
systemctl status sshd

# Check SSL configuration file exists
test -f /etc/apache2/mods-available/ssl.conf

# Verify SSL protocol configuration after role execution
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Test SSL configuration
apache2ctl configtest

# Verify services are running after restart
systemctl is-active apache2
systemctl is-active sshd
```

**Key Migration Notes**:
1. **Structure Conversion**: Convert from playbook to role structure
2. **Handler Fix**: Correct handler name mismatch ("Restart apache" → "Restart apache2")
3. **FQCN**: Add fully qualified collection names for all modules
4. **Parameterization**: Make hardcoded paths and configurations variable
5. **Boolean Modernization**: Convert `become: yes` to `become: true`
6. **Role Metadata**: Add proper meta/main.yml and argument specifications
7. **Error Handling**: Consider adding validation tasks to check if Apache SSL module is enabled
8. **Idempotency**: The replace module is already idempotent, but consider adding validation