---
source-path: chef-and-ansible/poodle_fix.yml
---

I can see that `poodle_fix.yml` is a standalone playbook file, not an Ansible role. However, the user has requested to analyze it as a module for migration to Ansible. Let me examine the content more carefully and provide a migration plan to convert this playbook into a proper Ansible role structure.

# Migration Plan: poodle_fix

**TLDR**: This is a standalone playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook to a proper Ansible role structure with modernized syntax, FQCN usage, and proper role organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Updates SSL protocol configuration to disable vulnerable protocols
- Enables only TLSv1.2 protocol
- Manages Apache2 and SSH service restarts
- Targets SSL configuration in `/etc/apache2/mods-available/ssl.conf`

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

The playbook performs operations in this order:

1. **SSL Protocol Fix Task** (`tasks/main.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, old-style parameter formatting
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper parameter structure
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (`handlers/main.yml`):
   - **Step 1**: Restarts Apache2 and SSH services when SSL config changes
   - **Step 2**: Handler name mismatch issue (notifies "Restart apache2" but handler is "Restart apache")
   - **Step 3**: Fix handler name consistency and ensure both handlers are properly defined
   - Ansible module mapping: `ansible.builtin.service` (already modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| `dest=` parameter style | `path:` parameter | tasks/main.yml | Parameter modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | Fix notification target |
| Playbook structure | Role structure | All files | Convert to proper role |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Inline parameters | YAML dictionary format | tasks/main.yml | Parameter structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (managed by system)
**Services managed**: 
- apache2 (web server)
- sshd (SSH daemon)

## Template Modernization

No templates present in the current playbook.

## Argument Specification

Variables for meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `manage_apache_service`: boolean, default: true, description: "Whether to manage Apache service restarts"
- `manage_ssh_service`: boolean, default: true, description: "Whether to manage SSH service restarts"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml
- handlers/main.yml
- defaults/main.yml
- meta/main.yml
- meta/argument_specs.yml

**Services to check**: 
- apache2 (should restart after SSL config change)
- sshd (should restart after SSL config change)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
systemctl status apache2
apache2ctl -M | grep ssl

# Check current SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify SSH service is running
systemctl status sshd

# Test Apache configuration syntax after changes
apache2ctl configtest

# Verify SSL protocols are properly configured
openssl s_client -connect localhost:443 -tls1_2 < /dev/null
```

**Critical Issues Found:**
1. **Handler Name Mismatch**: Task notifies "Restart apache2" but handler is named "Restart apache"
2. **Non-FQCN Module**: `replace` should be `ansible.builtin.replace`
3. **Parameter Style**: Old-style `dest=` should be modern YAML `path:`
4. **Boolean Values**: `become: yes` should be `become: true`
5. **Playbook vs Role**: Current structure is a playbook, needs conversion to role format
6. **Missing Variables**: Hard-coded paths and values should be parameterized

**Modernization Priority:**
1. Fix handler name consistency (critical for functionality)
2. Convert to proper role structure
3. Apply FQCN and syntax modernization
4. Add argument specifications and defaults
5. Parameterize configuration values