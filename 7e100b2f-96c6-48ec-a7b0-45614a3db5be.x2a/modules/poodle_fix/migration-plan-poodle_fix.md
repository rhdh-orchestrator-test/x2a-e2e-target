---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization primarily for syntax updates, including fully qualified collection names (FQCN) for the replace module and handler notification consistency.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure connections
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Targets hosts in the "myhost" group with root privileges
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols and enable only TLSv1.2
   - Notifies handlers to restart Apache and SSH services after configuration changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler "Restart apache2" is notified but defined as "Restart apache" |
| Unquoted file path | Quoted file path | poodle_fix.yml | `dest=/etc/apache2/mods-available/ssl.conf` should use quotes |
| Missing mode parameter | Add `mode:` parameter | poodle_fix.yml | File permissions should be explicitly set |
| `yes` boolean | `true` boolean | poodle_fix.yml | `become: yes` → `become: true` |

## Dependencies

**Collection dependencies** (for requirements.yml):
- No external collections required, only ansible.builtin

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

No variables are defined in this role that would require argument specifications.

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized playbook)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify SSH configuration: `sshd -t`
- Test SSL/TLS security: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Recommended Modern Role Structure

Since this is a simple playbook rather than a full role, it should be converted to a proper role structure:

```
roles/
  poodle_fix/
    tasks/
      main.yml
    handlers/
      main.yml
    meta/
      main.yml
    README.md
```

The playbook logic should be moved to these files with proper FQCN and modern syntax.