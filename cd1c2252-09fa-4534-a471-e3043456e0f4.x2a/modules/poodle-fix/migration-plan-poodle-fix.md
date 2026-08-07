---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on this file:

# Migration Plan: poodle_fix

**TLDR**: This playbook addresses the POODLE vulnerability by updating SSL configurations in Apache to disable vulnerable SSL protocols and enable only TLSv1.2. The modernization needs include converting the playbook to a proper role structure, using FQCN for modules, and ensuring proper handler naming consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 protocol
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. The migration will create a proper role structure.**

Current file:
```
chef-and-ansible/poodle_fix.yml
```

Proposed role structure:
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
defaults/main.yml (to be created, if needed)

**Meta:**
meta/main.yml (to be created)

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart services
   - Modern equivalent: Use `ansible.builtin.replace` with proper mode parameter

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Handler name inconsistency: "Restart apache" vs notification "Restart apache2"
   - Modern equivalent: Ensure handler names match notification names exactly

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Missing `mode:` parameter | Add `mode: preserve` | poodle_fix.yml | File permissions |
| Handler name mismatch | Ensure handler name matches notification name | poodle_fix.yml | "Restart apache" vs "Restart apache2" |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None required for this role

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are used in this role, but could add:
  - `ssl_config_path`: Path to SSL configuration file (default: '/etc/apache2/mods-available/ssl.conf')
  - `ssl_protocol_string`: Protocol string to use (default: '-all +TLSv1.2')

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
- Verify SSL configuration file exists: `ls -la /etc/apache2/mods-available/ssl.conf`
- Check current SSL protocol settings: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- After applying role, verify SSL settings: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Test SSL connection with: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no SSLv3 support (POODLE mitigation): `openssl s_client -connect localhost:443 -ssl3` (should fail)