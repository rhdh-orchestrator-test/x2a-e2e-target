---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle-fix

**TLDR**: This role implements a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and to fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate the POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: The provided file is a standalone playbook, not a structured Ansible role.**

poodle_fix.yml

## Module Explanation

The playbook performs operations in this order:

1. **poodle_fix.yml**:
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols and enable only TLSv1.2
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Notifies handlers to restart Apache and SSH services after configuration changes
   - Legacy patterns found: short module name `replace`, handler name mismatch
   - Modern equivalent: Use FQCN `ansible.builtin.replace`, fix handler name consistency

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name mismatch | Match handler name in notification | poodle_fix.yml | Handler "Restart apache2" notified but handler defined as "Restart apache" |
| Missing `changed_when` | Add condition for idempotency | poodle_fix.yml | Add `changed_when` to improve idempotency |
| Missing file mode | Add mode parameter | poodle_fix.yml | Consider adding `validate` parameter for Apache config |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this playbook.

## Argument Specification

For conversion to a proper role, the following variables should be in meta/argument_specs.yml:
- `poodle_fix_apache_config_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: 'Path to Apache SSL configuration file'
- `poodle_fix_ssl_protocol`: string, default: '-all +TLSv1.2', description: 'SSL protocol configuration string'

## Checks for the Migration

**Files to verify**: 
- tasks/main.yml
- handlers/main.yml
- meta/argument_specs.yml
- defaults/main.yml

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
```bash
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

## Conversion Notes

This file is a standalone playbook, not a structured Ansible role. To convert it to a proper role:

1. Create a standard role directory structure:
   ```
   poodle-fix/
   ├── defaults/
   │   └── main.yml
   ├── handlers/
   │   └── main.yml
   ├── meta/
   │   └── main.yml
   │   └── argument_specs.yml
   └── tasks/
       └── main.yml
   ```

2. Move the task to tasks/main.yml with proper FQCN
3. Move handlers to handlers/main.yml with consistent naming
4. Add variables to defaults/main.yml
5. Create proper meta/main.yml with role metadata
6. Add argument specifications to meta/argument_specs.yml