---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan for this Ansible role.

# Migration Plan: poodle_fix

**TLDR**: This role mitigates the POODLE vulnerability by updating SSL/TLS protocol configurations in Apache. It needs modernization from a playbook format to a proper role structure with fully qualified collection names (FQCN), proper handler naming, and structured organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The current implementation is a standalone playbook, not a proper role structure. The migration will create a proper role structure.**

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

1. **SSL Configuration Update** (`tasks/main.yml`):
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace:`
   - Modern equivalent: Use FQCN `ansible.builtin.replace:`
   - Notifies handlers to restart services after configuration changes
   - Ansible module mapping: `replace:` → `ansible.builtin.replace:`

2. **Service Restart Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (notifies "Restart apache2" but handler is "Restart apache")
   - Modern equivalent: Ensure handler names match exactly with notifications
   - Ansible module mapping: Already using FQCN `ansible.builtin.service:`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler "Restart apache" should match notification "Restart apache2" |
| Playbook format | Role structure | poodle_fix.yml | Convert from playbook to proper role structure |
| Missing `mode:` | Add `mode:` parameter | tasks/main.yml | For file operations (though not present in current code) |
| Missing role metadata | Create meta/main.yml | N/A | Add proper role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are present in the current implementation.

## Argument Specification

For meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol configuration string"

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

# Check SSL/TLS protocol settings
openssl s_client -connect localhost:443 -tls1_2

# Verify SSH configuration
sshd -t

# Check if services are running
systemctl status apache2
systemctl status sshd
```