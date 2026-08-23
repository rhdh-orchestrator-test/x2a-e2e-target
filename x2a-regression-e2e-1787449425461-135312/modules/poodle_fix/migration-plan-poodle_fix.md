---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and create a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and to fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
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

1. **main.yml** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable protocols
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Legacy pattern: Short module name `replace:` without FQCN
   - Modern equivalent: `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| `yes` | `true` | tasks/main.yml | Boolean syntax |
| Handler name inconsistency | Consistent handler names | handlers/main.yml | Handler name in notify ("Restart apache2") doesn't match handler name ("Restart apache") |
| Missing `mode:` parameter | Add `mode:` parameter | tasks/main.yml | File permissions should be explicitly set |
| Missing argument specs | Add argument specs | meta/argument_specs.yml | Role validation |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: '*'

**Role dependencies**: None identified
**External packages**: None directly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates identified in the current structure.

## Argument Specification

For meta/argument_specs.yml:
- No variables identified in the current playbook, but could add:
  - `ssl_protocol`: string, default: '-all +TLSv1.2', description: 'SSL protocols to enable/disable'
  - `apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- meta/argument_specs.yml
- defaults/main.yml
- README.md

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS configuration
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Check for POODLE vulnerability
openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" if SSLv3 is disabled
```