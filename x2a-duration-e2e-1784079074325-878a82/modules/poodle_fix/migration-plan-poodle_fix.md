---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies security fixes for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Updates Apache SSL configuration to mitigate POODLE vulnerability
- Disables vulnerable SSL protocols and enables only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Updates Apache SSL configuration to mitigate the POODLE vulnerability by replacing the SSLProtocol line to only allow TLSv1.2
   - Legacy patterns found: non-FQCN module name (`replace`), missing mode parameter for file operations
   - Modern equivalent: Use `ansible.builtin.replace` with proper parameters
   - Ansible module mapping: `replace` → `ansible.builtin.replace`
   - Handler naming inconsistency: Notification uses "Restart apache2" but handler is defined as "Restart apache"

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Missing `mode` parameter | Add `mode: '0644'` | poodle_fix.yml | File permissions for idempotency |
| Handler name mismatch | Consistent handler naming | poodle_fix.yml | "Restart apache2" notification vs "Restart apache" handler |

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
- poodle_fix.yml

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Check SSL configuration file exists: `ls -la /etc/apache2/mods-available/ssl.conf`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Test SSL configuration: `openssl s_client -connect localhost:443 -tls1_2`
- Verify POODLE vulnerability is mitigated: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Modernized Role Structure

Since this is a single playbook file rather than a full role structure, the modernization would involve:

1. Converting it to a proper role structure with:
   - tasks/main.yml
   - handlers/main.yml
   - meta/main.yml

2. Or updating the existing playbook with modern syntax:

```yaml
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
      notify:
        - Restart apache2
        - Restart sshd
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