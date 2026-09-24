---
source-path: chef-and-ansible/poodle_fix.yml
---

Based on my analysis, I can see that `poodle_fix.yml` is actually a playbook file, not a role. However, I'll analyze it for modernization needs and provide a migration plan to convert it into a proper modern Ansible role structure.

# Migration Plan: poodle-fix-demo

**TLDR**: This is currently a single playbook file that fixes the POODLE SSL vulnerability in Apache by updating SSL protocol configuration. It needs to be converted from a playbook into a proper role structure and modernized with current Ansible best practices including FQCN usage, proper handler naming consistency, and role-based organization.

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
meta/main.yml
meta/argument_specs.yml
defaults/main.yml
README.md
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
   - **Step 1**: Uses `replace` module to update Apache SSL configuration
   - **Step 2**: Legacy patterns found: non-FQCN module name, inconsistent handler naming
   - **Step 3**: Modern equivalent: Use `ansible.builtin.replace` with proper FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Management** (handlers):
   - **Step 1**: Restarts Apache2 and SSH services after configuration changes
   - **Step 2**: Legacy patterns found: Handler name mismatch ("Restart apache" vs "Restart apache2" in notify)
   - **Step 3**: Modern equivalent: Consistent handler naming and FQCN usage
   - Ansible module mapping: `service` → `ansible.builtin.service` (already modern in handlers)

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN required |
| `become: yes` | `become: true` | tasks/main.yml | Boolean modernization |
| Handler name mismatch | Consistent naming | handlers/main.yml | "Restart apache" → "Restart apache2" |
| Playbook structure | Role structure | All files | Convert to proper role layout |
| Hardcoded paths | Parameterized variables | tasks/main.yml | Make SSL config path configurable |

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
- `ssl_protocols`: string, default: "-all +TLSv1.2", description: "SSL protocols to enable/disable"
- `restart_services`: boolean, default: true, description: "Whether to restart services after configuration changes"

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml (SSL configuration task)
- handlers/main.yml (service restart handlers)
- defaults/main.yml (default variables)
- meta/main.yml (role metadata)
- meta/argument_specs.yml (variable validation)

**Services to check**: 
- apache2 (should be running and using TLSv1.2 only)
- sshd (should restart successfully)

**Templates to validate**: None

## Pre-flight checks:
```bash
# Verify Apache SSL configuration
sudo apache2ctl configtest

# Check SSL protocols enabled
openssl s_client -connect localhost:443 -tls1_2 < /dev/null

# Verify services are running
systemctl status apache2
systemctl status sshd

# Test POODLE vulnerability fix
nmap --script ssl-poodle -p 443 localhost
```

**Critical Migration Notes:**
1. **Handler Name Consistency**: The current playbook has a mismatch where the task notifies "Restart apache2" but the handler is named "Restart apache". This must be fixed.
2. **Role Structure**: Convert from playbook to proper role structure with separate task and handler files.
3. **Variable Parameterization**: Make hardcoded paths and values configurable through role variables.
4. **FQCN Compliance**: Update all module references to use fully qualified collection names.
5. **Boolean Modernization**: Convert `become: yes` to `become: true`.
6. **Security Validation**: Add validation tasks to ensure the POODLE fix is properly applied.