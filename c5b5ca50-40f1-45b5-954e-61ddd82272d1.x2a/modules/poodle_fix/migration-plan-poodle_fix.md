---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL protocol settings in Apache. It needs modernization primarily for module syntax (FQCN), handler naming consistency, and proper file mode specifications.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Targets Apache's SSL configuration file to mitigate the POODLE vulnerability
   - Uses the `replace` module to modify SSL protocol settings, disabling all protocols except TLSv1.2
   - Notifies handlers to restart both Apache and SSH services after the change
   - Legacy patterns found: non-FQCN module names, handler name inconsistency
   - Modern equivalent: Use fully qualified collection names, consistent handler names
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name inconsistency (`Restart apache2` in notify vs `Restart apache` in handler) | Consistent handler names | poodle_fix.yml | Handler names should match exactly |
| Missing file mode in replace module | Add `mode: '0644'` | poodle_fix.yml | File permissions should be explicitly set |
| Missing `changed_when` for idempotency | Add appropriate `changed_when` condition | poodle_fix.yml | Improve idempotency |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates are used in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables are defined in this playbook that would require argument specifications

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized)
- meta/main.yml (to be created)
- meta/argument_specs.yml (to be created if variables are added)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS protocols: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test SSL vulnerability: `openssl s_client -connect localhost:443 -ssl3`

## Modernized Playbook Example

```yaml
---
- hosts: myhost
  remote_user: root
  become: true
  tasks:
    - name: Fix SSL in Apache
      ansible.builtin.replace:
        dest: /etc/apache2/mods-available/ssl.conf
        regexp: '^SSLProtocol.*$'
        replace: 'SSLProtocol -all +TLSv1.2'
        mode: '0644'
      notify:
        - Restart apache2
        - Restart sshd
      register: ssl_fix
      changed_when: ssl_fix.changed

  handlers:
    - name: Restart apache2
      ansible.builtin.service:
        name: apache2
        state: restarted

    - name: Restart sshd
      ansible.builtin.service:
        name: sshd
        state: restarted
```