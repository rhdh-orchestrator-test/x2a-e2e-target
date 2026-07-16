---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and to fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables all SSL protocols except TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol directive
   - Uses the `replace` module to modify `/etc/apache2/mods-available/ssl.conf`
   - Sets `SSLProtocol -all +TLSv1.2` to disable all SSL protocols except TLSv1.2
   - Notifies handlers to restart Apache and SSH services after configuration changes
   - Legacy patterns found: non-FQCN module name (`replace`), missing mode parameter for file operations
   - Modern equivalent: Use `ansible.builtin.replace` with proper parameters

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name mismatch | Consistent handler names | poodle_fix.yml | Handler "Restart apache2" is notified but defined as "Restart apache" |
| Missing file mode | Add `mode:` parameter | poodle_fix.yml | File operations should specify mode for security |
| Missing `validate:` | Add validation | poodle_fix.yml | Apache config should be validated before restart |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

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
- Verify SSH configuration syntax: `sshd -t`
- Test SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Modernized Playbook

```yaml
---
- hosts: myhost
  remote_user: root
  become: true
  tasks:
    - name: Fix SSL in Apache
      ansible.builtin.replace:
        path: /etc/apache2/mods-available/ssl.conf
        regexp: '^SSLProtocol.*$'
        replace: 'SSLProtocol -all +TLSv1.2'
        mode: '0644'
        validate: 'apache2ctl -t %s'
      notify:
        - Restart apache
        - Restart sshd
  handlers:
    - name: Restart apache
      ansible.builtin.service:
        name: apache2
        state: restarted

    - name: Restart sshd
      ansible.builtin.service:
        name: sshd
        state: restarted
```

Note: This migration plan addresses a simple playbook rather than a full role structure. The modernization focuses on syntax updates and best practices for the existing playbook. For a more comprehensive solution, this could be converted to a proper role structure with separate task, handler, and variable files.