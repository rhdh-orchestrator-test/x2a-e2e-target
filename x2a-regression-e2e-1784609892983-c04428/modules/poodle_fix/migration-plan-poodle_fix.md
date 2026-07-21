---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure communications
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a playbook, not a role structure. For migration to a proper role structure, we need to create the following files:**

```
tasks/main.yml
handlers/main.yml
meta/main.yml
README.md
```

**Task Files:**
tasks/main.yml (to be created from playbook tasks)

**Handler Files:**
handlers/main.yml (to be created from playbook handlers)

**Variable Files:**
defaults/main.yml (to be created, not in original)

**Meta:**
meta/main.yml (to be created, not in original)

**Templates:**
None in original

**Static Files:**
None in original

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Fix** (`tasks/main.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability
   - Legacy pattern: Uses short-form module name `replace:`
   - Modern equivalent: Use FQCN `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name inconsistency between notification ("Restart apache2") and handler definition ("Restart apache")
   - Modern equivalent: Consistent handler naming
   - Ansible module mapping: Already using FQCN `ansible.builtin.service:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name inconsistency | Consistent handler naming | handlers/main.yml | Handler "Restart apache" should match notification "Restart apache2" |
| Playbook structure | Role structure | All files | Convert from playbook to proper role structure |
| Missing `mode:` parameter | Add `mode:` parameter | tasks/main.yml | For file operations (though not directly applicable in replace module) |
| Missing role metadata | Create meta/main.yml | meta/main.yml | Add proper role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core collection

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize in the original playbook.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the original playbook, but for a proper role, we should add:
  - `apache_ssl_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
  - `ssl_protocol_setting`: string, default: '-all +TLSv1.2', description: 'SSL protocol configuration string'

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- defaults/main.yml
- README.md

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Check SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Verify TLS version with: `nmap --script ssl-enum-ciphers -p 443 localhost`