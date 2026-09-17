---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is currently a playbook, not a role. The analysis summary shows 0 files because this is a single playbook file rather than a role structure. Let me provide a migration plan to convert this playbook into a modern Ansible role.

# Migration Plan: poodle_fix

**TLDR**: This is currently a playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook into a proper Ansible role structure with modern syntax and best practices.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Restarts Apache and SSH services after configuration changes

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

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Current**: Uses `replace` module with legacy syntax (no FQCN)
   - **Legacy patterns**: Short module name, `become: yes` at play level, handler name mismatch
   - **Modern equivalent**: Use FQCN `ansible.builtin.replace`, proper handler naming
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Restart Handlers**:
   - **Current**: Mixed handler naming (one handler named "Restart apache" but notified as "Restart apache2")
   - **Legacy patterns**: Handler name mismatch will cause failures
   - **Modern equivalent**: Consistent handler naming, proper FQCN usage

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` (play level) | `become: true` (role level) | tasks/main.yml | Boolean modernization + role-level privilege |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hard-coded paths | Parameterized variables | defaults/main.yml | Configuration flexibility |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix (for advanced file operations if needed)

**Role dependencies**: None
**External packages**: apache2 (managed by the target system)
**Services managed**: 
- apache2 (restarted after SSL configuration change)
- sshd (restarted after configuration change)

## Template Modernization

No templates in current implementation. Consider adding:
- **ssl.conf.j2**: Template for SSL configuration with parameterized protocols

## Argument Specification

Variables for meta/argument_specs.yml:
- `poodle_fix_ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable"
- `poodle_fix_apache_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `poodle_fix_restart_services`: list, default: ["apache2", "sshd"], description: "Services to restart after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 service status and SSL configuration
- sshd service status

**Templates to validate**: 
- None currently, but consider ssl.conf.j2 template for future flexibility

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Check current SSL configuration
grep -i "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify SSH service is running
systemctl status sshd

# Test SSL configuration after role execution
openssl s_client -connect localhost:443 -tls1_2
```

**Critical Issues to Address in Migration**:

1. **Handler Name Mismatch**: The current playbook notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute.

2. **Playbook to Role Conversion**: This needs to be restructured from a single playbook file into a proper role directory structure.

3. **Hard-coded Configuration**: The Apache configuration path and SSL protocols should be parameterized for flexibility across different systems.

4. **Missing Error Handling**: No validation that the SSL configuration file exists before attempting to modify it.

5. **Security Consideration**: The role should validate that TLSv1.2 is actually supported on the target system before applying the configuration.