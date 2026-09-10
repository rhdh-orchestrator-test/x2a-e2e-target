---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, `poodle_fix.yml` is a standalone Ansible playbook, not a role. However, I can still provide a migration plan to modernize this playbook and potentially convert it into a proper role structure. Let me analyze the content for modernization needs.

# Migration Plan: poodle_fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLSv1.2 protocol. The main modernization needs include converting from a playbook to a role structure, fixing handler naming inconsistencies, adding proper file permissions, and implementing modern Ansible best practices.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Configures Apache SSL settings to disable vulnerable SSL protocols
- Replaces SSLProtocol configuration in Apache ssl.conf
- Restarts Apache and SSH services after configuration changes
- Addresses POODLE SSL vulnerability (CVE-2014-3566)

## File Structure

**Current Structure (Playbook):**
```
poodle_fix.yml
```

**Proposed Role Structure:**
```
tasks/main.yml
handlers/main.yml
defaults/main.yml
meta/main.yml
meta/argument_specs.yml
```

## Module Explanation

The playbook performs operations in this order:

1. **SSL Configuration Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Targets `/etc/apache2/mods-available/ssl.conf` file
   - **Step 3**: Replaces any existing SSLProtocol directive with secure TLSv1.2 only
   - **Legacy patterns found**: Missing FQCN, no file mode specification, handler naming inconsistency
   - **Modern equivalent**: Use `ansible.builtin.replace` with proper file permissions and consistent handler names
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Handler inconsistency**: Task notifies "Restart apache2" but handler is named "Restart apache"
   - **Missing validation**: No verification that services are actually running after restart

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache2" vs "Restart apache" |
| Missing file mode | Add `mode: '0644'` | tasks/main.yml | File permissions best practice |
| No backup option | Add `backup: true` | tasks/main.yml | Safety for config changes |
| Playbook structure | Role structure | All files | Convert to proper role |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix (for advanced file operations if needed)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the current playbook.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable in Apache"
- `apache_ssl_conf_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `backup_config`: boolean, default: true, description: "Whether to backup configuration files before modification"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (converted task)
- handlers/main.yml (fixed handler names)
- defaults/main.yml (new variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 service status and configuration
- sshd service status

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
systemctl is-active apache2
systemctl is-active sshd

# Test SSL configuration syntax
apache2ctl configtest

# Verify SSL protocols after change
openssl s_client -connect localhost:443 -tls1_2
```

**Critical Issues Found:**
1. **Handler naming inconsistency**: Task notifies "Restart apache2" but handler is named "Restart apache"
2. **Missing FQCN**: `replace` module needs `ansible.builtin.replace`
3. **No file permissions**: Configuration file modification lacks mode specification
4. **No backup**: Risky configuration changes without backup option
5. **Playbook vs Role**: Current structure is a playbook, should be converted to role for reusability
6. **Boolean syntax**: `become: yes` should be `become: true`

**Security Considerations:**
- This role addresses a critical SSL vulnerability (POODLE)
- Disabling older SSL protocols may break compatibility with very old clients
- Should include validation that TLSv1.2 is properly configured after changes