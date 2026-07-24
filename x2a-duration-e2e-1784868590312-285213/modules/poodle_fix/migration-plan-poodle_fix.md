---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler names, and structured organization into a standard Ansible role format.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The current implementation is a standalone playbook, not a properly structured role. The migration will convert this to a proper role structure.**

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

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration Fix** (`tasks/main.yml`):
   - Updates the Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace` without FQCN
   - Modern equivalent: Use `ansible.builtin.replace` with proper parameter formatting
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch between task notification and handler definition
   - Modern equivalent: Ensure handler names match exactly between notifications and definitions
   - Ansible module mapping: `ansible.builtin.service` is already using FQCN

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Match handler names exactly | poodle_fix.yml | Task notifies "Restart apache2" but handler is named "Restart apache" |
| Playbook format | Role structure | poodle_fix.yml | Convert standalone playbook to proper role structure |
| No argument specs | Add argument specs | N/A | Create meta/argument_specs.yml for role validation |
| No role metadata | Add role metadata | N/A | Create meta/main.yml with role information |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin modules are used

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- `apache_ssl_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_setting`: 
  - type: str
  - default: "-all +TLSv1.2"
  - description: "SSL protocol configuration string for Apache"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- meta/argument_specs.yml
- defaults/main.yml

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

# Check SSH protocols
nmap --script ssh2-enum-algos -p 22 localhost
```