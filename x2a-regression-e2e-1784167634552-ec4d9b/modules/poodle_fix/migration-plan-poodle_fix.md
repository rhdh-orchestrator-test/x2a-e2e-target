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
- Enables only TLSv1.2 protocol
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Connects to target hosts as root with privilege escalation
   - Updates the Apache SSL configuration file to disable vulnerable SSL protocols and enable only TLSv1.2
   - Notifies handlers to restart Apache and SSH services after configuration changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| Handler name mismatch | Fix handler name consistency | poodle_fix.yml | Handler name in notify ("Restart apache2") doesn't match actual handler name ("Restart apache") |
| Unquoted file path | `dest: '/etc/apache2/mods-available/ssl.conf'` | poodle_fix.yml | Quote file paths |
| Inline parameters | Multi-line parameter format | poodle_fix.yml | Convert inline parameters to multi-line format for better readability |

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
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Verify SSL module is enabled in Apache: `apache2ctl -M | grep ssl`
- Check SSL configuration after applying: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Test SSL connection with: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no SSLv3 support (POODLE vulnerability): `openssl s_client -connect localhost:443 -ssl3` (should fail)

## Modernized Playbook

```yaml
---
- hosts: myhost
  remote_user: root
  become: true
  tasks:
    - name: Fix SSL in Apache
      ansible.builtin.replace:
        dest: '/etc/apache2/mods-available/ssl.conf'
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