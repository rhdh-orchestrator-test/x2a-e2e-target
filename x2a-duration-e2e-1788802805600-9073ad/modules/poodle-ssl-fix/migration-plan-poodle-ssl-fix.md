---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can provide a migration plan to convert this into a modern Ansible role. Let me provide the detailed migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The main modernization needs include converting from a playbook to a proper role structure, using FQCN for modules, fixing handler naming inconsistencies, and adding proper argument specifications.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enforces TLS 1.2 only protocol usage
- Manages Apache and SSH service restarts after configuration changes

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
None

**Static Files:**
None

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, handler naming inconsistency
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Fix handler names | handlers/main.yml | "Restart apache" vs "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role |
| Missing argument specs | Add meta/argument_specs.yml | meta/ | Role validation |
| Hardcoded paths | Parameterize paths | defaults/main.yml | Make configurable |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by the role)
**Services managed**: 
- apache2 (restarted after configuration change)
- sshd (restarted after configuration change)

## Template Modernization

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `restart_apache`: boolean, default: true, description: "Whether to restart Apache after configuration change"
- `restart_sshd`: boolean, default: true, description: "Whether to restart SSH daemon after configuration change"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted from playbook tasks)
- handlers/main.yml (extracted handlers with corrected names)
- defaults/main.yml (parameterized variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument validation)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: 
None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify Apache service status
systemctl status apache2

# Verify SSH service status
systemctl status sshd

# Test SSL configuration with openssl
echo | openssl s_client -connect localhost:443 -tls1_2 2>/dev/null | grep "Protocol"
```

## Critical Issues Found

1. **Handler Name Mismatch**: The task notifies "Restart apache2" but the handler is named "Restart apache" - this will cause the handler to never execute
2. **Hardcoded Paths**: The Apache configuration path is hardcoded and not parameterized
3. **Missing Error Handling**: No validation that the SSL configuration file exists before modification
4. **No Idempotency Check**: The replace operation will always report changed even if no change was made
5. **Security Consideration**: The current regex pattern may not catch all SSL protocol variations

## Additional Modernization Recommendations

1. **Add Validation**: Check if Apache SSL module is enabled before configuration
2. **Backup Strategy**: Create backup of original configuration before modification
3. **Platform Support**: Add support for different Linux distributions (CentOS/RHEL paths differ)
4. **SSL Testing**: Add tasks to verify SSL configuration is working correctly
5. **Molecule Testing**: Add molecule tests for the role validation