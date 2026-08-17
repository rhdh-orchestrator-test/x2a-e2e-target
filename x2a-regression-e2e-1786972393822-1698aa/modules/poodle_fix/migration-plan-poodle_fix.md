---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook that addresses the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted from a standalone playbook to a proper Ansible role structure with fully qualified collection names (FQCN) and modern syntax.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The source is a standalone playbook, not a role. We need to create a proper role structure.**

For the new role structure:
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
None in original playbook

**Static Files:**
None in original playbook

## Module Explanation

The role performs operations in this order:

1. **SSL Configuration** (`tasks/main.yml`):
   - Updates Apache SSL configuration to mitigate POODLE vulnerability by restricting protocols to TLSv1.2
   - Legacy pattern: Uses short module name `replace` without FQCN
   - Modern equivalent: Use `ansible.builtin.replace` with FQCN
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (notify uses "Restart apache2" but handler is named "Restart apache")
   - Modern equivalent: Consistent handler naming and FQCN usage
   - Ansible module mapping: Already using FQCN for `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler naming | poodle_fix.yml | Handler "Restart apache" vs notify "Restart apache2" |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role with tasks/main.yml, handlers/main.yml, etc. |
| No argument specs | Add meta/argument_specs.yml | N/A | Add role validation |
| No role metadata | Add meta/main.yml | N/A | Add proper role metadata |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: core

**Role dependencies**: None
**External packages**: None explicitly installed (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates in the original playbook.

## Argument Specification

For meta/argument_specs.yml:
- `apache_config_path`: 
  - type: str
  - default: "/etc/apache2/mods-available/ssl.conf"
  - description: "Path to Apache SSL configuration file"
- `ssl_protocol_string`: 
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

# Test for POODLE vulnerability
openssl s_client -connect localhost:443 -ssl3
# Should fail with "wrong version number" if properly configured
```