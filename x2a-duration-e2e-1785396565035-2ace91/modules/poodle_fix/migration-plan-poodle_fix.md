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
   - Updates Apache SSL configuration to mitigate POODLE vulnerability by replacing the SSLProtocol line
   - Uses the `replace` module without FQCN
   - Notifies handlers to restart Apache and SSH services
   - Has handler name inconsistency: notifies "Restart apache2" but handler is named "Restart apache"
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `yes` | `true` | poodle_fix.yml | Boolean modernization |
| Handler name inconsistency | Match handler names exactly | poodle_fix.yml | Handler "Restart apache2" notified but handler named "Restart apache" |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in this playbook that require argument specification

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
- Validate Apache configuration: `apache2ctl configtest`
- Check SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Test TLS version support: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Modernized Version

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