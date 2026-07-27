---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 to mitigate the POODLE vulnerability
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
tasks/main.yml (to be created)

**Handler Files:**
handlers/main.yml (to be created)

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

1. **SSL Configuration Fix** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers with inconsistent naming
   - Modern equivalent: Use `ansible.builtin.replace` with proper handler names

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - One handler uses FQCN (`ansible.builtin.service`) while the other doesn't
   - Modern equivalent: Use consistent FQCN for all service handlers

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name inconsistency | Consistent handler names | tasks/main.yml, handlers/main.yml | Handler "Restart apache2" in notify vs "Restart apache" in handler definition |
| `service:` | `ansible.builtin.service:` | handlers/main.yml | FQCN for second handler |
| `become: yes` | `become: true` | Role level | Boolean syntax |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None identified, only built-in modules are used

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current structure.

## Argument Specification

For meta/argument_specs.yml:
- No variables identified in the current playbook that need specification

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- README.md

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check Apache SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration: `apache2ctl configtest`
- Test TLS version support: `nmap --script ssl-enum-ciphers -p 443 localhost`