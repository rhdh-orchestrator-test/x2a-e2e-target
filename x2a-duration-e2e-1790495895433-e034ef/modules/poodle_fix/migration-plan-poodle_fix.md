---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a standalone playbook, not an Ansible role. However, I can still provide a migration plan to modernize this into a proper Ansible role structure following current best practices.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2. The migration involves converting a standalone playbook into a proper role structure and modernizing deprecated syntax patterns.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Enforces TLS 1.2 only protocol in Apache configuration
- Manages Apache and SSH service restarts after configuration changes
- Addresses POODLE (Padding Oracle On Downgraded Legacy Encryption) vulnerability

## File Structure

**Current Structure** (Standalone Playbook):
```
poodle_fix.yml
```

**Target Role Structure** (To be created):
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
None

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Configuration Task** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: short module name, deprecated `dest` parameter, `become: yes`
   - **Step 3**: Modern equivalent: FQCN `ansible.builtin.replace`, `path` parameter, `become: true`
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Handler Inconsistency Issue**:
   - **Problem**: Task notifies "Restart apache2" but handler is named "Restart apache"
   - **Solution**: Align handler names with notification calls

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `dest=` parameter | `path:` | tasks/main.yml | Parameter name change |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Align names | handlers/main.yml | Fix notification target |
| Playbook structure | Role structure | All files | Convert to proper role |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system package manager)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_ssl_protocol`: string, default: "-all +TLSv1.2", description: "SSL protocol configuration for Apache"
- `apache_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `restart_services`: boolean, default: true, description: "Whether to restart services after configuration changes"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: 
None

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
```

**Critical Migration Notes**:
1. **Handler Name Fix**: The original playbook has a mismatch between the notification ("Restart apache2") and the actual handler name ("Restart apache"). This must be corrected.
2. **Role Structure**: Convert from standalone playbook to proper role structure with separate tasks, handlers, defaults, and meta files.
3. **Variable Parameterization**: Make the SSL protocol configuration and file paths configurable through role variables.
4. **Error Handling**: Add proper error handling and validation for the configuration changes.
5. **Idempotency**: The `replace` module is already idempotent, but consider adding validation tasks to verify the configuration is correct.