---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a standalone Ansible playbook, not a role. However, I can provide a migration plan to convert this playbook into a modern Ansible role structure. Let me analyze the content and provide the migration specification.

# Migration Plan: poodle_fix

**TLDR**: This is currently a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook to a proper role structure and modernized with current Ansible best practices including FQCN usage, proper handler naming consistency, and role-based organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets SSL configuration in `/etc/apache2/mods-available/ssl.conf`

## File Structure

**Current Structure** (Playbook):
```
poodle_fix.yml
```

**Target Role Structure**:
```
tasks/main.yml
handlers/main.yml
meta/main.yml
defaults/main.yml
```

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update SSL protocol configuration in Apache
   - **Step 2**: Legacy patterns found: non-FQCN module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns: Handler name mismatch (`Restart apache2` vs `Restart apache`)
   - **Step 3**: Modern equivalent: Consistent handler naming and FQCN usage

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | Fix `Restart apache2` vs `Restart apache` |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded paths | Variables | tasks/main.yml | Make paths configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system)
**Services managed**: 
- apache2 (restarted after SSL config change)
- sshd (restarted after SSL config change)

## Template Modernization

No templates present in current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `manage_apache_service`: boolean, default: true, description: "Whether to manage Apache service restart"
- `manage_ssh_service`: boolean, default: true, description: "Whether to manage SSH service restart"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata and argument specs)

**Services to check**: 
- apache2 (should restart after configuration change)
- sshd (should restart after configuration change)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL module is enabled
apache2ctl -M | grep ssl

# Check current SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Test Apache configuration syntax
apache2ctl configtest

# Verify services are running after restart
systemctl status apache2
systemctl status sshd

# Test SSL configuration with openssl
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"
```

## Critical Migration Notes

1. **Handler Name Consistency**: The current playbook has a mismatch between the notify target (`Restart apache2`) and the actual handler name (`Restart apache`). This needs to be fixed.

2. **Role Structure**: Convert from standalone playbook to proper role structure with separate tasks, handlers, defaults, and meta files.

3. **Variable Configuration**: Make hardcoded paths and configurations variable to improve reusability.

4. **Security Validation**: Add tasks to validate that the SSL configuration change was successful and that only secure protocols are enabled.

5. **Idempotency**: The current `replace` task is idempotent, but consider adding validation tasks to ensure the configuration is correct.