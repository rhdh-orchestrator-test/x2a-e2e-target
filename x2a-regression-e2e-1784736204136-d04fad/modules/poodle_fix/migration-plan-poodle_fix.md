---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables all SSL protocols except TLSv1.2
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
defaults/main.yml (to be created)

**Meta:**
meta/main.yml (to be created)

**Templates:**
None identified

**Static Files:**
None identified

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Update** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers with inconsistent naming
   - Modern equivalent: Use `ansible.builtin.replace` with proper handler names

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name inconsistency | Match handler names exactly | poodle_fix.yml | Handler "Restart apache2" notified but defined as "Restart apache" |
| Playbook structure | Role structure | poodle_fix.yml | Convert playbook to proper role structure |
| Missing documentation | Add README.md with role purpose | N/A | Document the role's purpose and parameters |
| Missing meta information | Add meta/main.yml | N/A | Add proper metadata for the role |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None identified, only uses built-in modules

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current structure.

## Argument Specification

For meta/argument_specs.yml:
- No variables currently defined in the playbook
- Consider adding:
  - `ssl_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
  - `ssl_protocol_string`: string, default: '-all +TLSv1.2', description: 'SSL protocol configuration string'

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
- Verify SSL module is enabled in Apache: `apache2ctl -M | grep ssl`
- Check SSL configuration syntax: `apache2ctl configtest`
- Test SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no older protocols are enabled: `openssl s_client -connect localhost:443 -ssl3` (should fail)