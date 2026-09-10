---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook, not a role. However, the user has requested to analyze it for migration to a modern Ansible role. I'll create a migration plan to convert this playbook into a proper Ansible role structure with modern best practices.

# Migration Plan: poodle_fix

**TLDR**: This is currently a playbook that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook to a proper Ansible role structure and modernized with current best practices including FQCN usage, proper file organization, and argument specifications.

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

**Target Role Structure** (to be created):
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
None required

## Module Explanation

The current playbook performs operations in this order:

1. **SSL Protocol Fix** (`poodle_fix.yml`):
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns: Handler name mismatch ("Restart apache" vs "Restart apache2" in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and FQCN usage
   - Ansible module mapping: `service` → `ansible.builtin.service` (already modernized in handlers)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| No argument specs | Add argument_specs.yml | meta/ | Role validation |
| No defaults | Add defaults/main.yml | defaults/ | Variable management |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin (core collection)

**Role dependencies**: None
**External packages**: apache2 (assumed to be pre-installed)
**Services managed**: 
- apache2 (restarted after SSL config change)
- sshd (restarted after SSL config change)

## Template Modernization

No templates are used in this role.

## Argument Specification

Variables that should be in meta/argument_specs.yml:
- `ssl_config_path`: string, default: "/etc/apache2/mods-available/ssl.conf", description: "Path to Apache SSL configuration file"
- `ssl_protocol_config`: string, default: "SSLProtocol -all +TLSv1.2", description: "SSL protocol configuration string"
- `manage_apache_service`: boolean, default: true, description: "Whether to manage Apache service restarts"
- `manage_ssh_service`: boolean, default: true, description: "Whether to manage SSH service restarts"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (argument specifications)

**Services to check**: 
- apache2 (should restart successfully after SSL config change)
- sshd (should restart successfully)

**Templates to validate**: 
None required

## Pre-flight checks:
```bash
# Verify Apache SSL module is enabled
apache2ctl -M | grep ssl

# Test Apache configuration syntax
apache2ctl configtest

# Verify SSL configuration file exists
test -f /etc/apache2/mods-available/ssl.conf

# Check current SSL protocol configuration
grep "SSLProtocol" /etc/apache2/mods-available/ssl.conf

# Verify services are running after role execution
systemctl status apache2
systemctl status sshd

# Test SSL configuration (after role execution)
openssl s_client -connect localhost:443 -tls1_2 < /dev/null
```

**Key Migration Notes**:
1. This conversion transforms a simple playbook into a reusable, parameterized role
2. The handler name inconsistency must be fixed ("Restart apache" → "Restart apache2")
3. All modules need FQCN prefixes for modern Ansible compatibility
4. Boolean values should use `true`/`false` instead of `yes`/`no`
5. The role should be made configurable through variables for different Apache installations
6. Consider adding idempotency checks and validation tasks