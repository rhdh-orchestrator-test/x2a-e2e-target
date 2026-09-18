---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a traditional Ansible role structure. However, I can create a migration plan to convert this into a proper modern Ansible role. Let me provide the migration specification:

# Migration Plan: poodle-ssl-fix

**TLDR**: This is a security hardening playbook that fixes the POODLE SSL vulnerability by configuring Apache to use only TLS 1.2 protocol. The migration involves converting a standalone playbook into a proper role structure with modern Ansible syntax, FQCN usage, and proper role organization.

## Service Type and Configuration

**Service Type**: Security Hardening / Web Server Configuration

**Key Operations**:
- Fixes POODLE SSL vulnerability in Apache web server
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enforces TLS 1.2 only protocol usage
- Manages Apache and SSH service restarts
- Targets `/etc/apache2/mods-available/ssl.conf` configuration file

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

1. **SSL Protocol Configuration** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to modify Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, mixed handler naming
   - **Step 3**: Modern equivalent: `ansible.builtin.replace` with consistent handler names
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers section):
   - **Step 1**: Restarts Apache and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: inconsistent handler naming (`Restart apache` vs `Restart apache2` in notify)
   - **Step 3**: Modern equivalent: consistent handler naming and FQCN usage
   - Ansible module mapping: Already using `ansible.builtin.service` (partially modern)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | `Restart apache` → `Restart apache2` |
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

No templates present in the current implementation.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `apache_ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `manage_apache_service`: boolean, default: true, description: "Whether to manage Apache service restarts"
- `manage_ssh_service`: boolean, default: true, description: "Whether to manage SSH service restarts"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should restart after SSL config change)
- sshd (should restart after SSL config change)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache is installed and SSL module is available
apache2ctl -M | grep ssl
systemctl is-active apache2

# Verify SSH service is running
systemctl is-active sshd

# Check current SSL configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Test Apache configuration syntax
apache2ctl configtest

# Verify TLS 1.2 is working after migration
openssl s_client -connect localhost:443 -tls1_2 -servername localhost
```

**Additional Migration Notes:**
1. The original playbook has a handler naming inconsistency (`Restart apache` in handler definition vs `Restart apache2` in notify)
2. The role should be made more flexible by parameterizing the Apache configuration path and SSL protocol settings
3. Consider adding validation tasks to ensure Apache SSL module is enabled before attempting configuration
4. Add proper error handling for cases where Apache is not installed or SSL module is not available
5. The role should include platform-specific variables for different Linux distributions (Debian/Ubuntu vs RHEL/CentOS paths)