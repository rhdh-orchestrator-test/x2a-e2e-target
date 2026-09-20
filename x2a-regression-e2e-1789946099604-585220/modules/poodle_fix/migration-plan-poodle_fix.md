---
source-path: chef-and-ansible/poodle_fix.yml
---

I can see that `poodle_fix.yml` is actually a playbook file, not an Ansible role. However, the user has requested to analyze it for migration to a modern Ansible role. Let me examine the content more carefully and create a migration plan to convert this playbook into a proper Ansible role structure.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The migration involves converting a standalone playbook into a proper Ansible role structure with modern syntax, FQCN usage, and proper role organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enforces TLS 1.2 only protocol usage
- Manages Apache and SSH service restarts
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

1. **Main Tasks** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Replaces SSLProtocol directive to enforce TLS 1.2 only
   - **Step 3**: Notifies handlers to restart services
   - **Legacy patterns found**: Non-FQCN module usage, handler name mismatch
   - **Modern equivalent**: FQCN modules, consistent handler naming, proper role structure
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent handler naming | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Hardcoded paths | Parameterized variables | tasks/main.yml | Make configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `manage_apache_service`: boolean, default: true, description: "Whether to manage Apache service restarts"
- `manage_sshd_service`: boolean, default: true, description: "Whether to manage SSH service restarts"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (main task logic)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Check current SSL configuration
grep -n "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify SSH service is running
systemctl status sshd

# Test Apache configuration syntax after changes
apache2ctl configtest

# Verify TLS configuration with SSL testing tools
openssl s_client -connect localhost:443 -tls1_2
```

**Key Migration Notes:**
1. **Handler Name Consistency**: The original playbook has a mismatch between the notify target ("Restart apache2") and the actual handler name ("Restart apache"). This needs to be corrected.
2. **Role Structure**: Convert from a standalone playbook to a proper role structure with separate task and handler files.
3. **Parameterization**: Make file paths and configuration values configurable through variables.
4. **FQCN Usage**: Update all module references to use fully qualified collection names.
5. **Boolean Modernization**: Convert `yes`/`no` to `true`/`false` for boolean values.
6. **Security Focus**: This role specifically addresses the POODLE vulnerability (CVE-2014-3566) by disabling SSL 3.0 and enforcing TLS 1.2.