---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll analyze the content and prepare a migration plan:

# Migration Plan: poodle_fix

**TLDR**: This is a simple Ansible playbook (not a role) that mitigates the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The playbook needs to be converted to a proper role structure with modernized syntax including FQCN module names, quoted regex patterns, and proper handler naming.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
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
- tasks/main.yml (to be created)

**Handler Files:**
- handlers/main.yml (to be created)

**Variable Files:**
- defaults/main.yml (to be created)

**Meta:**
- meta/main.yml (to be created)

**Templates:**
None

**Static Files:**
None

## Module Explanation

The role performs operations in this order:

1. **Security Hardening** (`tasks/main.yml`):
   - Updates Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
   - Legacy pattern: Uses short-form module name `replace` without FQCN
   - Legacy pattern: Uses unquoted regex pattern
   - Modern equivalent: Use `ansible.builtin.replace` with quoted regex pattern
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

2. **Service Handlers** (`handlers/main.yml`):
   - Restarts Apache and SSH services after configuration changes
   - Legacy pattern: Handler name mismatch (defined as "Restart apache" but notified as "Restart apache2")
   - Modern equivalent: Ensure handler names match notification names exactly
   - Ansible module mapping: Already using FQCN `ansible.builtin.service`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Unquoted regex pattern | Quoted regex pattern `regexp: '^SSLProtocol.*$'` | poodle_fix.yml | Quoting regex patterns is recommended |
| Handler name mismatch | Match handler name with notification name | poodle_fix.yml | Handler defined as "Restart apache" but notified as "Restart apache2" |
| Standalone playbook | Proper role structure | poodle_fix.yml | Convert to role with tasks/main.yml and handlers/main.yml |

## Dependencies

**Collection dependencies** (for requirements.yml):
- None (uses only builtin modules)

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates to modernize.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the original playbook, but could add:
  - `ssl_protocols`: string, default: '-all +TLSv1.2', description: 'SSL protocols to enable/disable'
  - `apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- defaults/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Verify SSL configuration file exists: `ls -la /etc/apache2/mods-available/ssl.conf`
- Test Apache configuration after changes: `apache2ctl configtest`
- Verify SSL settings: `openssl s_client -connect localhost:443 -tls1_2`
- Verify SSL settings reject older protocols: `openssl s_client -connect localhost:443 -ssl3` (should fail)