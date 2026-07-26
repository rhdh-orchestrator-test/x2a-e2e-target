---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for FQCN module names, handler naming consistency, and proper file structure to convert from a playbook to a proper Ansible role.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The current implementation is a standalone playbook, not a proper role structure. The migration will create the following role structure:**

```
tasks/main.yml
handlers/main.yml
meta/main.yml
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

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability by restricting protocols to TLSv1.2
   - Legacy pattern: Uses short-form module name `replace:`
   - Modern equivalent: Use FQCN `ansible.builtin.replace:`
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch between task notification and handler definition
   - Modern equivalent: Ensure handler names match exactly between notifications and definitions
   - Ansible module mapping: Already using FQCN `ansible.builtin.service:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | tasks/main.yml | FQCN |
| Handler name mismatch (`Restart apache2` vs `Restart apache`) | Use consistent handler names | tasks/main.yml, handlers/main.yml | Ensure notification names match handler names exactly |
| Playbook structure | Role structure | All files | Convert from standalone playbook to proper role structure |
| Missing `mode:` parameter | Add `mode:` parameter for file operations | tasks/main.yml | Best practice for file operations |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

```yaml
argument_specs:
  main:
    short_description: Mitigates POODLE vulnerability in Apache SSL configuration
    description:
      - Updates Apache SSL configuration to disable vulnerable protocols
      - Enables only TLSv1.2 to mitigate POODLE vulnerability
    options:
      apache_ssl_conf_path:
        type: str
        default: /etc/apache2/mods-available/ssl.conf
        description: Path to Apache SSL configuration file
      ssl_protocol_setting:
        type: str
        default: '-all +TLSv1.2'
        description: SSL protocol configuration string
```

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
```
# Verify Apache configuration syntax
apache2ctl configtest

# Check SSL/TLS protocols enabled in Apache
nmap --script ssl-enum-ciphers -p 443 localhost

# Verify SSH configuration
sshd -t

# Check SSH protocol versions
ssh -vv localhost
```