---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a standalone Ansible playbook, not a role. However, I can provide a migration plan to convert this playbook into a modern Ansible role structure. Let me analyze the content and provide the migration specification.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2. The migration involves converting a standalone playbook into a proper role structure and modernizing the syntax to follow current Ansible best practices.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Enforces TLS 1.2 only protocol in Apache configuration
- Manages Apache and SSH service restarts after configuration changes
- Targets POODLE vulnerability mitigation (CVE-2014-3566)

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
None

**Static Files:**
None

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: short module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: FQCN module name, consistent handler naming, proper file permissions
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers section):
   - **Step 1**: Restarts Apache and SSH services after configuration changes
   - **Step 2**: Legacy patterns: inconsistent handler names ("Restart apache" vs "Restart apache2")
   - **Step 3**: Modern equivalent: consistent naming, FQCN for service module
   - Ansible module mapping: `service` → `ansible.builtin.service` (already modernized in handlers)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Missing file mode | `mode: '0644'` | tasks/main.yml | File permission best practice |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing changed_when | Add idempotency check | tasks/main.yml | Improve task reliability |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix (for advanced file operations if needed)

**Role dependencies**: None
**External packages**: apache2 (managed by system, not installed by role)
**Services managed**: 
- apache2 (restarted after configuration)
- sshd (restarted after configuration)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default "/etc/apache2/mods-available/ssl.conf", description "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default "SSLProtocol -all +TLSv1.2", description "SSL protocol configuration string"
- `apache_service_name`: string, default "apache2", description "Name of Apache service"
- `restart_ssh`: boolean, default true, description "Whether to restart SSH service after changes"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (SSL configuration applied)
- sshd (service restart capability)

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
# Check current SSL configuration
grep -i sslprotocol /etc/apache2/mods-available/ssl.conf
# Verify Apache configuration syntax
apache2ctl configtest
# Check service status
systemctl status apache2
systemctl status sshd
# Test SSL configuration after applying role
openssl s_client -connect localhost:443 -tls1_2
```

**Key Migration Notes:**
1. **Security Focus**: This role addresses a critical security vulnerability (POODLE)
2. **Handler Consistency**: Fix the handler name mismatch between task notification and handler definition
3. **Idempotency**: Add proper changed_when conditions to improve task reliability
4. **Variable Flexibility**: Make file paths and service names configurable for different distributions
5. **Validation**: Add argument specs to ensure proper variable types and values
6. **Testing**: Include molecule tests to verify SSL configuration is properly applied

**Critical Security Consideration**: The role should validate that the SSL configuration change doesn't break existing HTTPS connections before applying the restart handlers.